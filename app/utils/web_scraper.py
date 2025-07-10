import requests
from bs4 import BeautifulSoup

def scrape_video_description(video_url):
    """
    Scrapes the video description from a YouTube video page as a fallback.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(video_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # This selector reliably targets the meta tag containing the description
        description_tag = soup.find("meta", {"name": "description"})
        
        if description_tag and description_tag.get("content"):
            return description_tag.get("content")
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error during web scraping request: {e}")
        return None