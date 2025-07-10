from googleapiclient.discovery import build

def get_video_details(video_id, api_key):
    if not api_key:
        print("Warning: YOUTUBE_API_KEY not found.")
        return None
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(part="snippet", id=video_id)
        response = request.execute()
        return response.get('items', [{}])[0].get('snippet')
    except Exception as e:
        print(f"Error fetching details from YouTube API: {e}")
        return None