# tests/test_models/test_video.py

import pytest
from datetime import datetime
from app.models.video import Video, VideoInfo


class TestVideoInfo:
    """Test cases for VideoInfo model."""
    
    def test_video_info_creation_basic(self):
        """Test basic VideoInfo creation."""
        info = VideoInfo(
            title="Test Video",
            channel="Test Channel",
            description="Test description"
        )
        
        assert info.title == "Test Video"
        assert info.channel == "Test Channel"
        assert info.description == "Test description"
    
    def test_video_info_creation_with_url(self):
        """Test VideoInfo creation with URL."""
        info = VideoInfo(
            title="Test Video",
            channel="Test Channel",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        
        assert info.video_id == "dQw4w9WgXcQ"
        assert info.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    def test_video_info_clean_text(self):
        """Test text cleaning in VideoInfo."""
        info = VideoInfo(
            title="  Test   Video  \n\r  ",
            channel="  Test\nChannel  ",
            description="Test\r\ndescription"
        )
        
        assert info.title == "Test Video"
        assert info.channel == "Test Channel"
        assert info.description == "Test description"
    
    def test_video_info_empty_values(self):
        """Test VideoInfo with empty values."""
        info = VideoInfo(title="", channel="")
        
        assert info.title == "Unknown Title"
        assert info.channel == "Unknown Channel"
        assert info.description == ""
    
    def test_video_info_to_dict(self):
        """Test VideoInfo to_dict conversion."""
        info = VideoInfo(
            title="Test Video",
            channel="Test Channel",
            description="Test description",
            video_id="test123"
        )
        
        result = info.to_dict()
        
        assert result['title'] == "Test Video"
        assert result['channel'] == "Test Channel"
        assert result['description'] == "Test description"
        assert result['video_id'] == "test123"
    
    def test_video_info_from_dict(self):
        """Test VideoInfo from_dict creation."""
        data = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'description': 'Test description',
            'video_id': 'test123'
        }
        
        info = VideoInfo.from_dict(data)
        
        assert info.title == "Test Video"
        assert info.channel == "Test Channel"
        assert info.description == "Test description"
        assert info.video_id == "test123"
    
    def test_extract_video_id_various_formats(self):
        """Test video ID extraction from various URL formats."""
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/v/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
            ("invalid_url", None),
            ("", None)
        ]
        
        for url, expected_id in test_cases:
            result = VideoInfo._extract_video_id(url)
            assert result == expected_id, f"Failed for URL: {url}"


class TestVideo:
    """Test cases for Video model."""
    
    def test_video_creation_basic(self, sample_video_info):
        """Test basic Video creation."""
        video = Video(
            info=sample_video_info,
            transcript="This is a test transcript."
        )
        
        assert video.info == sample_video_info
        assert video.transcript == "This is a test transcript."
        assert video.transcript_language == "en"
        assert video.transcript_source == "auto"
    
    def test_video_word_count(self, sample_video_info):
        """Test word count calculation."""
        video = Video(
            info=sample_video_info,
            transcript="This is a test transcript with multiple words."
        )
        
        assert video.word_count == 8
    
    def test_video_estimated_reading_time(self, sample_video_info):
        """Test estimated reading time calculation."""
        # Create transcript with 400 words (should be 2 minutes at 200 WPM)
        transcript = " ".join(["word"] * 400)
        video = Video(
            info=sample_video_info,
            transcript=transcript
        )
        
        assert video.estimated_reading_time == 2
    
    def test_video_is_valid_true(self, sample_video_info):
        """Test is_valid property returns True for valid video."""
        video = Video(
            info=sample_video_info,
            transcript="This is a sufficiently long transcript with enough content for meaningful summarization."
        )
        
        assert video.is_valid is True
    
    def test_video_is_valid_false_short_transcript(self, sample_video_info):
        """Test is_valid property returns False for short transcript."""
        video = Video(
            info=sample_video_info,
            transcript="Short"
        )
        
        assert video.is_valid is False
    
    def test_video_is_valid_false_unknown_title(self):
        """Test is_valid property returns False for unknown title."""
        info = VideoInfo(title="Unknown Title", channel="Test Channel")
        video = Video(
            info=info,
            transcript="This is a sufficiently long transcript with enough content."
        )
        
        assert video.is_valid is False
    
    def test_video_get_content_preview_short(self, sample_video_info):
        """Test content preview for short transcript."""
        transcript = "This is a short transcript."
        video = Video(info=sample_video_info, transcript=transcript)
        
        preview = video.get_content_preview(100)
        assert preview == transcript
    
    def test_video_get_content_preview_long(self, sample_video_info):
        """Test content preview for long transcript."""
        transcript = "This is a very long transcript. " * 20
        video = Video(info=sample_video_info, transcript=transcript)
        
        preview = video.get_content_preview(50)
        assert len(preview) <= 53  # 50 + "..."
        assert preview.endswith("...") or preview.endswith(".")
    
    def test_video_clean_transcript(self, sample_video_info):
        """Test transcript cleaning."""
        transcript = "This is [Music] a test (inaudible) transcript 00:01:30 with artifacts."
        video = Video(info=sample_video_info, transcript=transcript)
        
        assert "[Music]" not in video.transcript
        assert "(inaudible)" not in video.transcript
        assert "00:01:30" not in video.transcript
    
    def test_video_to_dict(self, sample_video_info):
        """Test Video to_dict conversion."""
        video = Video(
            info=sample_video_info,
            transcript="Test transcript"
        )
        
        result = video.to_dict()
        
        assert 'info' in result
        assert 'transcript' in result
        assert 'word_count' in result
        assert 'is_valid' in result
        assert result['transcript'] == "Test transcript"
    
    def test_video_from_dict(self):
        """Test Video from_dict creation."""
        data = {
            'info': {
                'title': 'Test Video',
                'channel': 'Test Channel',
                'description': 'Test description'
            },
            'transcript': 'Test transcript',
            'transcript_language': 'en',
            'transcript_source': 'manual'
        }
        
        video = Video.from_dict(data)
        
        assert video.info.title == "Test Video"
        assert video.transcript == "Test transcript"
        assert video.transcript_language == "en"
        assert video.transcript_source == "manual"
    
    def test_video_validate_success(self, sample_video_info):
        """Test successful video validation."""
        video = Video(
            info=sample_video_info,
            transcript="This is a sufficiently long transcript with enough content for validation."
        )
        
        errors = video.validate()
        assert len(errors) == 0
    
    def test_video_validate_errors(self):
        """Test video validation with errors."""
        info = VideoInfo(title="Unknown Title", channel="Unknown Channel")
        video = Video(
            info=info,
            transcript="Short"
        )
        
        errors = video.validate()
        assert len(errors) > 0
        assert any("title" in error.lower() for error in errors)
        assert any("channel" in error.lower() for error in errors)
        assert any("transcript" in error.lower() for error in errors)
    
    def test_video_invalid_info_type(self):
        """Test Video creation with invalid info type."""
        with pytest.raises(ValueError, match="info must be a VideoInfo instance"):
            Video(info="not_a_video_info", transcript="test")
