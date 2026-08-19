## YouTube ingestion Lambda

The Lambda in `python_scripts/fetch_and_store_videos.py` retrieves the complete uploads playlist, skips malformed video records, filters titles, and publishes:

- `videos.json`
- `filtered_videos.json`

### Required environment variables

- `YOUTUBE_API_KEY`: YouTube Data API key.
- `YOUTUBE_CHANNEL_ID`: channel to ingest.
- `S3_BUCKET_NAME`: bucket for the JSON objects.

### Optional environment variables

- `TITLE_KEYWORDS`: comma-separated normalized title phrases. Defaults to `swarperfect,karaoke`.
- `YOUTUBE_RETRY_ATTEMPTS`: retry count for transient YouTube errors. Defaults to `3`.
- `MINIMUM_VALID_VIDEOS`: minimum valid records required before publishing. Defaults to `1`.

The Lambda logs structured `event=...` records to CloudWatch Logs, including request IDs, page counts, skipped records, retry context, timing, and upload counts. CloudFront access logging is separate and does not receive Lambda logs automatically.

The function fails before publishing when configuration, YouTube retrieval, transformation, or validation fails. It writes the two existing S3 keys only after a complete valid catalog is prepared. Because the keys are written in two S3 operations, a failure between those operations can still leave the two objects from different runs; use versioned objects and a manifest if atomic publication becomes necessary.

Keep API keys out of source control and deployment artifacts. Store them in Lambda environment configuration or a managed secret, and restrict the key to the required API and application where possible.
