# tests/conftest.py

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from app import app
from app.models.video import Video, VideoInfo
from app.models.summary import Summary, SummaryType


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def sample_video_info():
    """Create a sample VideoInfo object for testing."""
    return VideoInfo(
        title="Test Video Title",
        channel="Test Channel",
        description="This is a test video description",
        video_id="test123",
        url="https://www.youtube.com/watch?v=test123",
        duration=300,
        view_count=1000
    )


@pytest.fixture
def sample_video(sample_video_info):
    """Create a sample Video object for testing."""
    return Video(
        info=sample_video_info,
        transcript="This is a test transcript with some content for testing purposes. It contains multiple sentences to simulate real video content.",
        transcript_language="en",
        transcript_source="auto"
    )


@pytest.fixture
def sample_summary():
    """Create a sample Summary object for testing."""
    return Summary(
        content="This is a test summary of the video content.",
        keywords=["test", "video", "content"],
        summary_type=SummaryType.ENHANCED,
        key_points=["First key point", "Second key point"],
        content_type="educational"
    )


@pytest.fixture
def sample_transcript():
    """Provide a sample transcript for testing."""
    return """
    Welcome to this tutorial video. Today we're going to learn about Python programming.
    First, let's talk about variables. Variables are used to store data in Python.
    You can create a variable by simply assigning a value to it.
    For example, you can write: name equals "John". This creates a string variable.
    Next, we'll discuss functions. Functions are reusable blocks of code.
    You define a function using the def keyword followed by the function name.
    Remember to practice these concepts to become proficient in Python programming.
    """


@pytest.fixture
def mock_youtube_url():
    """Provide a mock YouTube URL for testing."""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def invalid_youtube_url():
    """Provide an invalid YouTube URL for testing."""
    return "https://www.example.com/not-youtube"


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_yt_dlp():
    """Mock yt-dlp functionality for testing."""
    with patch('app.utils.summarizer.yt_dlp.YoutubeDL') as mock_ydl:
        mock_instance = Mock()
        mock_ydl.return_value.__enter__.return_value = mock_instance
        
        # Mock extract_info response
        mock_instance.extract_info.return_value = {
            'title': 'Test Video Title',
            'uploader': 'Test Channel',
            'description': 'Test description',
            'subtitles': {'en': [{'url': 'test_url'}]},
            'automatic_captions': {'en': [{'url': 'test_url'}]}
        }
        
        yield mock_instance


@pytest.fixture
def mock_transformers():
    """Mock transformers pipeline for testing."""
    with patch('app.utils.summarizer.pipeline') as mock_pipeline:
        mock_summarizer = Mock()
        mock_summarizer.return_value = [{'summary_text': 'Test summary content'}]
        mock_pipeline.return_value = mock_summarizer
        yield mock_summarizer


@pytest.fixture
def mock_nltk():
    """Mock NLTK functionality for testing."""
    with patch('app.utils.summarizer.nltk') as mock_nltk:
        # Mock tokenization
        mock_nltk.sent_tokenize.return_value = [
            "This is the first sentence.",
            "This is the second sentence.",
            "This is the third sentence."
        ]
        
        mock_nltk.tokenize.word_tokenize.return_value = [
            "this", "is", "a", "test", "transcript", "with", "some", "words"
        ]
        
        # Mock stopwords
        mock_nltk.corpus.stopwords.words.return_value = ["is", "a", "the", "with", "some"]
        
        yield mock_nltk


@pytest.fixture(autouse=True)
def mock_file_operations():
    """Mock file operations to avoid actual file I/O during tests."""
    with patch('builtins.open'), \
         patch('os.listdir'), \
         patch('os.path.exists'), \
         patch('os.makedirs'), \
         patch('tempfile.TemporaryDirectory'):
        yield


@pytest.fixture
def sample_api_request():
    """Sample API request data for testing."""
    return {
        'url': 'https://www.youtube.com/watch?v=test123',
        'summary_type': 'enhanced',
        'include_keywords': True
    }


@pytest.fixture
def sample_api_response():
    """Sample API response data for testing."""
    return {
        'summary': 'This is a test summary of the video content.',
        'keywords': 'test, video, content, python, programming',
        'video_info': {
            'title': 'Test Video Title',
            'channel': 'Test Channel',
            'description': 'Test description'
        }
    }


# Test data constants
TEST_VIDEO_ID = "dQw4w9WgXcQ"
TEST_YOUTUBE_URL = f"https://www.youtube.com/watch?v={TEST_VIDEO_ID}"
TEST_YOUTU_BE_URL = f"https://youtu.be/{TEST_VIDEO_ID}"
TEST_EMBED_URL = f"https://www.youtube.com/embed/{TEST_VIDEO_ID}"

INVALID_URLS = [
    "not_a_url",
    "https://www.example.com",
    "https://vimeo.com/123456",
    "youtube.com/watch?v=invalid",  # Missing protocol
    "",
    None
]

VALID_YOUTUBE_URLS = [
    TEST_YOUTUBE_URL,
    TEST_YOUTU_BE_URL,
    TEST_EMBED_URL,
    "https://www.youtube.com/watch?v=test123&t=30s",
    "https://youtu.be/test123?t=30",
    "https://www.youtube.com/embed/test123?start=30"
]
