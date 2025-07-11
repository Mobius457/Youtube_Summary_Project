# tests/test_utils/test_summarizer.py

import pytest
from unittest.mock import Mock, patch, mock_open
from app.utils.summarizer import (
    get_transcript, 
    extract_video_info, 
    run_summarization,
    parse_subtitle_content,
    extract_key_points,
    format_summary
)


class TestGetTranscript:
    """Test cases for get_transcript function."""
    
    def test_get_transcript_success(self, mock_yt_dlp):
        """Test successful transcript extraction."""
        # Mock file operations
        mock_subtitle_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
This is the first subtitle line.

00:00:05.000 --> 00:00:10.000
This is the second subtitle line.
"""
        
        with patch('os.listdir', return_value=['subtitle.en.vtt']), \
             patch('builtins.open', mock_open(read_data=mock_subtitle_content)):
            
            result = get_transcript("https://www.youtube.com/watch?v=test123")
            
            assert result is not None
            assert "first subtitle line" in result
            assert "second subtitle line" in result
    
    def test_get_transcript_no_captions(self, mock_yt_dlp):
        """Test transcript extraction when no captions are available."""
        mock_yt_dlp.extract_info.return_value = {
            'subtitles': {},
            'automatic_captions': {}
        }
        
        with pytest.raises(Exception, match="No English captions found"):
            get_transcript("https://www.youtube.com/watch?v=test123")
    
    def test_get_transcript_file_not_found(self, mock_yt_dlp):
        """Test transcript extraction when subtitle file is not found."""
        with patch('os.listdir', return_value=[]):
            with pytest.raises(Exception, match="Could not find downloaded subtitle file"):
                get_transcript("https://www.youtube.com/watch?v=test123")


class TestParseSubtitleContent:
    """Test cases for parse_subtitle_content function."""
    
    def test_parse_vtt_content(self):
        """Test parsing VTT subtitle content."""
        vtt_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
This is the first line.

00:00:05.000 --> 00:00:10.000
This is the second line.
"""
        result = parse_subtitle_content(vtt_content)
        expected = "This is the first line. This is the second line."
        assert result == expected
    
    def test_parse_srt_content(self):
        """Test parsing SRT subtitle content."""
        srt_content = """1
00:00:01,000 --> 00:00:05,000
This is the first line.

2
00:00:05,000 --> 00:00:10,000
This is the second line.
"""
        result = parse_subtitle_content(srt_content)
        expected = "This is the first line. This is the second line."
        assert result == expected
    
    def test_parse_content_with_html_tags(self):
        """Test parsing content with HTML tags."""
        content_with_tags = """1
00:00:01,000 --> 00:00:05,000
<i>This is italic text.</i>

2
00:00:05,000 --> 00:00:10,000
<b>This is bold text.</b>
"""
        result = parse_subtitle_content(content_with_tags)
        expected = "This is italic text. This is bold text."
        assert result == expected


class TestExtractVideoInfo:
    """Test cases for extract_video_info function."""
    
    def test_extract_video_info_success(self, mock_yt_dlp):
        """Test successful video info extraction."""
        result = extract_video_info("https://www.youtube.com/watch?v=test123")
        
        assert result['title'] == 'Test Video Title'
        assert result['channel'] == 'Test Channel'
        assert result['description'] == 'Test description'
    
    def test_extract_video_info_failure(self):
        """Test video info extraction failure."""
        with patch('app.utils.summarizer.yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl.side_effect = Exception("Network error")
            
            result = extract_video_info("https://www.youtube.com/watch?v=test123")
            
            assert result['title'] == 'Unknown Title'
            assert result['channel'] == 'Unknown Channel'
            assert result['description'] == ''


class TestRunSummarization:
    """Test cases for run_summarization function."""
    
    def test_run_summarization_success(self, sample_transcript, mock_transformers, mock_nltk):
        """Test successful summarization."""
        video_info = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'description': 'Test description'
        }
        
        with patch('app.utils.advanced_summarizer.create_professional_summary') as mock_create:
            mock_create.return_value = "Enhanced test summary"
            
            summary, keywords = run_summarization(sample_transcript, video_info)
            
            assert summary == "Enhanced test summary"
            assert isinstance(keywords, str)
            assert len(keywords) > 0
    
    def test_run_summarization_fallback(self, sample_transcript, mock_nltk):
        """Test summarization with fallback when enhanced fails."""
        video_info = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'description': 'Test description'
        }
        
        with patch('app.utils.advanced_summarizer.create_professional_summary') as mock_create, \
             patch('app.utils.summarizer.pipeline') as mock_pipeline:
            
            # Make enhanced summarization fail
            mock_create.side_effect = Exception("Enhanced summarization failed")
            
            # Mock fallback summarization
            mock_summarizer = Mock()
            mock_summarizer.return_value = [{'summary_text': 'Fallback summary'}]
            mock_pipeline.return_value = mock_summarizer
            
            summary, keywords = run_summarization(sample_transcript, video_info)
            
            assert summary == "Fallback summary"
            assert isinstance(keywords, str)
    
    def test_run_summarization_empty_transcript(self):
        """Test summarization with empty transcript."""
        video_info = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'description': 'Test description'
        }
        
        with pytest.raises(Exception):
            run_summarization("", video_info)
    
    def test_run_summarization_no_video_info(self, sample_transcript, mock_transformers, mock_nltk):
        """Test summarization without video info."""
        with patch('app.utils.advanced_summarizer.create_professional_summary') as mock_create:
            mock_create.return_value = "Test summary"
            
            summary, keywords = run_summarization(sample_transcript, None)
            
            assert summary == "Test summary"
            assert isinstance(keywords, str)


class TestExtractKeyPoints:
    """Test cases for extract_key_points function."""
    
    def test_extract_key_points_with_indicators(self, mock_nltk):
        """Test key point extraction with importance indicators."""
        transcript = """
        This is an important point about programming.
        Remember to always test your code.
        The key thing to understand is variables.
        You should never ignore error messages.
        """
        
        mock_nltk.sent_tokenize.return_value = [
            "This is an important point about programming.",
            "Remember to always test your code.",
            "The key thing to understand is variables.",
            "You should never ignore error messages."
        ]
        
        result = extract_key_points(transcript)
        
        assert isinstance(result, list)
        assert len(result) > 0
        # Should find sentences with importance indicators
        assert any("important" in point.lower() for point in result)
    
    def test_extract_key_points_empty_transcript(self, mock_nltk):
        """Test key point extraction with empty transcript."""
        mock_nltk.sent_tokenize.return_value = []
        
        result = extract_key_points("")
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestFormatSummary:
    """Test cases for format_summary function."""
    
    def test_format_summary_basic(self):
        """Test basic summary formatting."""
        video_info = {
            'title': 'Test Video',
            'channel': 'Test Channel'
        }
        summary = "This is a test summary."
        key_points = ["Point 1", "Point 2"]
        
        result = format_summary(video_info, summary, key_points)
        
        assert video_info['title'] in result
        assert video_info['channel'] in result
        assert summary in result
        assert "Point 1" in result
        assert "Point 2" in result
    
    def test_format_summary_empty_key_points(self):
        """Test summary formatting with empty key points."""
        video_info = {
            'title': 'Test Video',
            'channel': 'Test Channel'
        }
        summary = "This is a test summary."
        key_points = []
        
        result = format_summary(video_info, summary, key_points)
        
        assert video_info['title'] in result
        assert summary in result
        # Should handle empty key points gracefully
        assert isinstance(result, str)
        assert len(result) > 0
