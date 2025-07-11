# app/services/video_service.py

import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, Tuple
from app.utils.summarizer import get_transcript, extract_video_info
from app.utils.transcript_fetcher import get_video_id


class VideoService:
    """Service for handling video-related operations."""
    
    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """
        Validate if the provided URL is a valid YouTube URL.
        
        Args:
            url (str): The URL to validate
            
        Returns:
            bool: True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
            
        youtube_patterns = [
            r'^https?://(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'^https?://(www\.)?youtu\.be/[\w-]+',
            r'^https?://(www\.)?youtube\.com/embed/[\w-]+',
            r'^https?://(www\.)?youtube\.com/v/[\w-]+',
        ]
        
        return any(re.match(pattern, url.strip()) for pattern in youtube_patterns)
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Optional[str]: Video ID if found, None otherwise
        """
        if not VideoService.validate_youtube_url(url):
            return None
            
        try:
            # Handle different YouTube URL formats
            if 'youtu.be/' in url:
                return url.split('youtu.be/')[-1].split('?')[0]
            elif 'youtube.com/watch' in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                return params.get('v', [None])[0]
            elif 'youtube.com/embed/' in url:
                return url.split('youtube.com/embed/')[-1].split('?')[0]
            elif 'youtube.com/v/' in url:
                return url.split('youtube.com/v/')[-1].split('?')[0]
        except Exception:
            pass
            
        return None
    
    @staticmethod
    def get_video_data(url: str) -> Tuple[str, Dict[str, str]]:
        """
        Get video transcript and metadata.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Tuple[str, Dict[str, str]]: Transcript and video info
            
        Raises:
            ValueError: If URL is invalid
            Exception: If transcript or video info cannot be retrieved
        """
        if not VideoService.validate_youtube_url(url):
            raise ValueError("Invalid YouTube URL provided")
        
        video_id = VideoService.extract_video_id(url)
        if not video_id:
            raise ValueError("Could not extract video ID from URL")
        
        try:
            # Get transcript using the existing utility
            transcript = get_transcript(url)
            if not transcript or len(transcript.strip()) == 0:
                raise Exception("No transcript available for this video")
            
            # Get video metadata
            video_info = extract_video_info(url)
            if not video_info:
                video_info = {
                    'title': 'Unknown Title',
                    'channel': 'Unknown Channel',
                    'description': ''
                }
            
            return transcript, video_info
            
        except Exception as e:
            if "No English captions found" in str(e):
                raise Exception("No English captions available for this video")
            elif "Could not find downloaded subtitle file" in str(e):
                raise Exception("Unable to download video captions")
            else:
                raise Exception(f"Error retrieving video data: {str(e)}")
    
    @staticmethod
    def get_video_info_only(url: str) -> Dict[str, str]:
        """
        Get only video metadata without transcript.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            Dict[str, str]: Video metadata
        """
        if not VideoService.validate_youtube_url(url):
            raise ValueError("Invalid YouTube URL provided")
        
        try:
            return extract_video_info(url)
        except Exception as e:
            return {
                'title': 'Unknown Title',
                'channel': 'Unknown Channel',
                'description': '',
                'error': str(e)
            }
    
    @staticmethod
    def format_video_duration(duration_seconds: int) -> str:
        """
        Format video duration from seconds to human-readable format.
        
        Args:
            duration_seconds (int): Duration in seconds
            
        Returns:
            str: Formatted duration (e.g., "5:30", "1:23:45")
        """
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    @staticmethod
    def clean_transcript(transcript: str) -> str:
        """
        Clean and normalize transcript text.
        
        Args:
            transcript (str): Raw transcript text
            
        Returns:
            str: Cleaned transcript
        """
        if not transcript:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        cleaned = re.sub(r'\s+', ' ', transcript.strip())
        
        # Remove common transcript artifacts
        cleaned = re.sub(r'\[.*?\]', '', cleaned)  # Remove [Music], [Applause], etc.
        cleaned = re.sub(r'\(.*?\)', '', cleaned)  # Remove (inaudible), etc.
        
        # Remove duplicate sentences (common in auto-generated captions)
        sentences = cleaned.split('.')
        unique_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in unique_sentences:
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences).strip()
