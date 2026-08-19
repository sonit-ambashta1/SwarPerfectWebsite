import json
import logging
import os
import re
import time
import unicodedata

import boto3
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

s3 = boto3.client("s3")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_TITLE_KEYWORDS = ("swarperfect", "karaoke")
MAX_RESULTS_PER_PAGE = 50
DEFAULT_RETRY_ATTEMPTS = 3
TRANSIENT_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}


def _log(event, **fields):
    details = " ".join(
        f"{key}={str(value).replace(' ', '_')}"
        for key, value in fields.items()
        if value is not None
    )
    logger.info("event=%s%s", event, f" {details}" if details else "")


def _required_env(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def _retry_attempts():
    try:
        return max(1, int(os.getenv("YOUTUBE_RETRY_ATTEMPTS", DEFAULT_RETRY_ATTEMPTS)))
    except ValueError as error:
        raise RuntimeError("YOUTUBE_RETRY_ATTEMPTS must be an integer") from error


def _execute_with_retries(request, operation, attempts):
    for attempt in range(1, attempts + 1):
        try:
            return request.execute()
        except HttpError as error:
            status = getattr(error.resp, "status", None)
            retryable = status in TRANSIENT_HTTP_STATUS_CODES
            if not retryable or attempt == attempts:
                logger.exception(
                    "event=youtube_request_failed operation=%s attempt=%s status=%s",
                    operation,
                    attempt,
                    status,
                )
                raise

            delay = min(2 ** (attempt - 1), 8)
            _log(
                "youtube_request_retry",
                operation=operation,
                attempt=attempt,
                status=status,
                delay_seconds=delay,
            )
            time.sleep(delay)


def _normalize_title(value):
    if not isinstance(value, str):
        return ""

    normalized = unicodedata.normalize("NFKC", value).casefold()
    normalized = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", normalized)
    normalized = re.sub(r"[^\w]+", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def _title_keywords():
    configured = os.getenv("TITLE_KEYWORDS", "")
    values = configured.split(",") if configured else DEFAULT_TITLE_KEYWORDS
    keywords = tuple(
        normalized
        for normalized in (_normalize_title(value) for value in values)
        if normalized
    )
    if not keywords:
        raise RuntimeError("TITLE_KEYWORDS must contain at least one keyword")
    return keywords


def get_channel_details(youtube, channel_id):
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id,
    )
    return _execute_with_retries(request, "channel_details", _retry_attempts())


def get_playlist_videos(youtube, playlist_id):
    items = []
    page_token = None
    seen_page_tokens = set()
    page_number = 0

    while True:
        if page_token in seen_page_tokens:
            raise RuntimeError(f"YouTube returned a repeated page token: {page_token}")
        if page_token:
            seen_page_tokens.add(page_token)

        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": MAX_RESULTS_PER_PAGE,
        }
        if page_token:
            params["pageToken"] = page_token

        page_number += 1
        response = _execute_with_retries(
            youtube.playlistItems().list(**params),
            f"playlist_page_{page_number}",
            _retry_attempts(),
        )
        if not isinstance(response, dict):
            raise RuntimeError(f"Invalid response returned for playlist page {page_number}")

        page_items = response.get("items")
        if not isinstance(page_items, list):
            raise RuntimeError(f"Invalid items returned for playlist page {page_number}")

        items.extend(page_items)
        _log(
            "playlist_page_fetched",
            page=page_number,
            page_items=len(page_items),
            total_items=len(items),
        )

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            return {"items": items}
        page_token = next_page_token


def filter_videos(videos, keywords=None):
    keywords = keywords or _title_keywords()
    return [
        video
        for video in videos
        if any(
            f" {keyword} " in f" {_normalize_title(video.get('title'))} "
            for keyword in keywords
        )
    ]

def transform_videos(video_result):
    videos = []
    skipped = 0

    for item in video_result.get("items", []):
        snippet = item.get("snippet")
        if not isinstance(snippet, dict):
            skipped += 1
            continue

        resource_id = snippet.get("resourceId")
        video_id = resource_id.get("videoId") if isinstance(resource_id, dict) else None
        title = snippet.get("title")
        if not isinstance(video_id, str) or not video_id.strip() or not isinstance(title, str) or not title.strip():
            skipped += 1
            continue

        thumbnails = snippet.get("thumbnails")
        if not isinstance(thumbnails, dict):
            thumbnails = {}
        thumbnail_url = next(
            (
                thumbnails.get(size, {}).get("url")
                for size in ("maxres", "high", "medium", "default")
                if isinstance(thumbnails.get(size), dict) and thumbnails.get(size, {}).get("url")
            ),
            None,
        )

        videos.append(
            {
                "video_id": video_id,
                "title": title.strip(),
                "description": snippet.get("description", ""),
                "thumbnail_url": thumbnail_url,
                "publish_date": snippet.get("publishedAt"),
            }
        )

    _log("videos_transformed", valid=len(videos), skipped=skipped)
    return videos


def upload_to_s3(videos, name):
    bucket_name = _required_env("S3_BUCKET_NAME")

    s3.put_object(
        Bucket=bucket_name,
        Key=f"{name}.json",
        Body=json.dumps(videos, indent=2).encode("utf-8"),
        ContentType="application/json",
        CacheControl="max-age=300",
    )
    _log("s3_object_uploaded", key=f"{name}.json", count=len(videos))


def _minimum_valid_videos():
    try:
        return max(1, int(os.getenv("MINIMUM_VALID_VIDEOS", "1")))
    except ValueError as error:
        raise RuntimeError("MINIMUM_VALID_VIDEOS must be an integer") from error


def lambda_handler(event, context):
    started_at = time.monotonic()
    request_id = getattr(context, "aws_request_id", None)
    bucket_name = _required_env("S3_BUCKET_NAME")
    api_key = _required_env("YOUTUBE_API_KEY")
    channel_id = _required_env("YOUTUBE_CHANNEL_ID")
    keywords = _title_keywords()
    _log("ingestion_started", request_id=request_id, channel_id=channel_id, keywords=keywords)

    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key,
    )

    _log("youtube_client_created", request_id=request_id)

    channel_result = get_channel_details(
        youtube,
        channel_id,
    )

    items = channel_result.get("items", [])

    if not items:
        raise RuntimeError(
            "No channel information returned."
        )

    playlist_id = (
        items[0]
        .get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("uploads")
    )

    if not playlist_id:
        raise RuntimeError(
            "Uploads playlist ID not found."
        )

    _log("uploads_playlist_found", request_id=request_id, playlist_id=playlist_id)

    video_result = get_playlist_videos(
        youtube,
        playlist_id,
    )

    videos = transform_videos(video_result)

    minimum_videos = _minimum_valid_videos()
    if len(videos) < minimum_videos:
        raise RuntimeError(
            f"Only {len(videos)} valid videos found; minimum is {minimum_videos}"
        )

    filtered_videos = filter_videos(videos, keywords)
    _log(
        "videos_ready_to_publish",
        request_id=request_id,
        total=len(videos),
        filtered=len(filtered_videos),
    )

    upload_to_s3(videos, "videos")
    upload_to_s3(filtered_videos, "filtered_videos")

    duration_ms = round((time.monotonic() - started_at) * 1000)
    _log("ingestion_completed", request_id=request_id, total=len(videos), duration_ms=duration_ms)

    return {
        "statusCode": 200,
        "videos_processed": len(videos),
        "videos_filtered": len(filtered_videos),
        "bucket": bucket_name,
        "object": "videos.json",
    }