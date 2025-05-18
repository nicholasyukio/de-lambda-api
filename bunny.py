import os
import requests
from datetime import datetime, timedelta

is_local = os.path.exists('.env')

# Load environment variables from .env
if is_local:
    from dotenv import load_dotenv
    load_dotenv()

bunny_api_key = os.getenv("BUNNY_API_KEY")
library_id = str(os.getenv("BUNNY_LIBRARY_ID"))

def get_video_info(video_id):
    url = f"https://video.bunnycdn.com/library/{library_id}/videos/{video_id}"
    headers = {
        "accept": "application/json",
        "AccessKey": bunny_api_key
    }
    response = requests.get(url, headers=headers)
    #print(response.text)
    if response.status_code == 200:
        json_response = response.json()
        views = json_response["views"]
        length = json_response["length"]
        title = json_response["title"]
        thumbnail_url = f"https://vz-6f64f7fb-752.b-cdn.net/{video_id}/{json_response['thumbnailFileName']}"
        averageWatchTime = json_response["averageWatchTime"]
        totalWatchTime = json_response["totalWatchTime"]
        return {"views": views, "length": length, "title": title, "thumbnail_url": thumbnail_url, "averageWatchTime": averageWatchTime, "totalWatchTime": totalWatchTime}
    else:
        return -1, -1, -1, -1