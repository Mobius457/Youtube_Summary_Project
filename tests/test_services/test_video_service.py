# tests/test_services/test_video_service.py

import pytest
from app.services.video_service import VideoService
from tests.conftest import VALID_YOUTUBE_URLS, INVALID_URLS


class TestVideoService:
    """Test cases for VideoService class."""
    
    def test_validate_youtube_url_valid_urls(self):
        """Test URL validation with valid YouTube URLs."""
        for url in VALID_YOUTUBE_URLS:
            assert VideoService.validate_youtube_url(url), f"URL should be valid: {url}"
    
    def test_validate_youtube_url_invalid_urls(self):
        """Test URL validation with invalid URLs."""
        for url in INVALID_URLS:
            assert not VideoService.validate_youtube_url(url), f"URL should be invalid: {url}"
    
    def test_extract_video_id_standard_url(self):
        """Test video ID extraction from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = VideoService.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test video ID extraction from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = VideoService.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test video ID extraction from embed YouTube URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = VideoService.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_parameters(self):
        """Test video ID extraction from URL with parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        video_id = VideoService.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test video ID extraction from invalid URL."""
        url = "https://www.example.com"
        video_id = VideoService.extract_video_id(url)
        assert video_id is None
    
    def test_clean_transcript_basic(self):
        """Test basic transcript cleaning."""
        transcript = "  This is a test   transcript with   extra spaces.  "
        cleaned = VideoService.clean_transcript(transcript)
        assert cleaned == "This is a test transcript with extra spaces."
    
    def test_clean_transcript_with_artifacts(self):
        """Test transcript cleaning with common artifacts."""
        transcript = "This is a test [Music] transcript (inaudible) with artifacts."
        cleaned = VideoService.clean_transcript(transcript)
        assert "[Music]" not in cleaned
        assert "(inaudible)" not in cleaned
        assert "This is a test transcript with artifacts." in cleaned
    
    def test_clean_transcript_empty(self):
        """Test transcript cleaning with empty input."""
        assert VideoService.clean_transcript("") == ""
        assert VideoService.clean_transcript(None) == ""
    
    def test_format_video_duration_minutes_only(self):
        """Test duration formatting for minutes only."""
        duration = VideoService.format_video_duration(330)  # 5:30
        assert duration == "5:30"
    
    def test_format_video_duration_with_hours(self):
        """Test duration formatting with hours."""
        duration = VideoService.format_video_duration(5025)  # 1:23:45
        assert duration == "1:23:45"
    
    def test_format_video_duration_seconds_only(self):
        """Test duration formatting for seconds only."""
        duration = VideoService.format_video_duration(45)  # 0:45
        assert duration == "0:45"
