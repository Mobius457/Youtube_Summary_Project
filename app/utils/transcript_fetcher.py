from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    if not url:
        return None
    try:
        query = urlparse(url).query
        params = parse_qs(query)
        # Handles both standard and short YouTube URLs
        return params.get("v", [None])[0] or url.split('/')[-1]
    except:
        return None

def get_transcript(video_id):
    """Fetches the transcript for a given YouTube video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text
    except Exception as e:
        print(f"Could not retrieve transcript for video ID {video_id}: {e}")
        return None