import json
import os
import boto3
from googleapiclient.discovery import build

s3 = boto3.client("s3")


def get_channel_details(youtube, channel_id):
    try:
        channel = youtube.channels().list(
            part="contentDetails",
            id=channel_id,
        )
        return channel.execute()
    except Exception as e:
        print(f"Error fetching channel details: {e}")
        return {}


def get_playlist_videos(youtube, playlist_id):
    try:
        videos = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
        )
        return videos.execute()
    except Exception as e:
        print(f"Error fetching videos: {e}")
        return {"items": []}


def transform_videos(video_result):
    videos = []

    for item in video_result.get("items", []):
        snippet = item.get("snippet", {})

        videos.append(
            {
                "video_id": snippet.get("resourceId", {}).get("videoId"),
                "title": snippet.get("title"),
                "description": snippet.get("description"),
                "thumbnail_url": (
                    snippet.get("thumbnails", {})
                    .get("high", {})
                    .get("url")
                ),
                "publish_date": snippet.get("publishedAt"),
            }
        )

    return videos


def upload_to_s3(videos):
    json_data = json.dumps(videos, indent=4)

    bucket_name = os.getenv("S3_BUCKET_NAME")

    s3.put_object(
        Bucket=bucket_name,
        Key="videos.json",
        Body=json_data,
        ContentType="application/json",
    )


def lambda_handler(event, context):
    print("Starting Swar Perfect YouTube ingestion")

    api_key = os.getenv("YOUTUBE_API_KEY")
    channel_id = os.getenv("YOUTUBE_CHANNEL_ID")

    print("Connecting to YouTube API")

    youtube = build(
        "youtube",
        "v3",
        developerKey=api_key,
    )

    print("Connected to YouTube API, fetching channel details")

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

    print(f"Found uploads playlist: {playlist_id}")

    print("Retrieving uploaded videos")

    video_result = get_playlist_videos(
        youtube,
        playlist_id,
    )

    print(
        f"Retrieved {len(video_result.get('items', []))} videos"
    )

    print("Transforming video metadata")

    videos = transform_videos(video_result)

    print("Uploading videos.json to S3")

    upload_to_s3(videos)

    print(
        f"Uploaded {len(videos)} videos to S3"
    )

    return {
        "statusCode": 200,
        "videos_processed": len(videos),
        "bucket": os.getenv("S3_BUCKET_NAME"),
        "object": "videos.json",
    }