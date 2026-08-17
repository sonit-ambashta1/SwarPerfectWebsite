import json

try:
    with open("videos.json", "r") as f:
        videos = json.load(f)
except FileNotFoundError:
    videos = []

swarperfect_karaoke_videos = list(filter(lambda video: "swarperfect" in video["title"].lower() and "karaoke" in video["title"].lower(), videos))
with open("swarperfect_karaoke_videos.json", "w") as f:
    json.dump(swarperfect_karaoke_videos, f, indent=4)