import json
import os
import boto3
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# 1. retrieves channel details for the SWAR PERFECT channel ID and loads them into a file
API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

channel = youtube.channels().list(
    part="contentDetails",
    id=os.getenv("YOUTUBE_CHANNEL_ID")
)

try:
    result = channel.execute()
except Exception as e:
    print(type(e))
    print(f"Error fetching channel details: {e}")
    result = {}

with open("channel_details.json", "w") as f:
    json.dump(result, f, indent=4)
    
# 2. retrieve the list of videos for the channel and load them into a file (use YouTube's UPLOADED playlist ID)
playlist_id = result.get("items", [])[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")

videos = youtube.playlistItems().list(
    part="snippet",
    playlistId=playlist_id,
    maxResults=50
)

try:
    video_result = videos.execute()
except Exception as e:
    print(type(e))
    print(f"Error fetching videos: {e}")
with open("videos_raw.json", "w") as f:
    json.dump(video_result, f, indent=4)
    
# 3. for each video, retrieve VideoID, title, description, thumbnail URL, and publish date, and load them into a file
videos = []
for item in video_result.get("items", []):
    video = {
        "video_id": item["snippet"]["resourceId"]["videoId"],
        "title": item["snippet"]["title"],
        "description": item["snippet"]["description"],
        "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
        "publish_date": item["snippet"]["publishedAt"]
    }
    videos.append(video)

# store the JSON file in the public folder of the website to access from the frontend 
FRONTEND_PUBLIC_FOLDER = os.path.join(os.path.dirname(__file__), "..", "swar-perfect-website", "public")
with open(os.path.join(FRONTEND_PUBLIC_FOLDER, "videos.json"), "w") as f:
    json.dump(videos, f, indent=4)