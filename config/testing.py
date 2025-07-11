# config/testing.py

import os
import tempfile
from .base import BaseConfig


class TestingConfig(BaseConfig):
    """Testing configuration."""
    
    # Flask settings
    DEBUG = False
    TESTING = True
    
    # Testing-specific settings
    FLASK_ENV = 'testing'
    
    # Disable security features for testing
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'testing-secret-key'
    
    # Disable CORS for testing
    CORS_ENABLED = False
    
    # Logging settings for testing
    LOG_LEVEL = 'ERROR'  # Reduce noise during testing
    
    # Cache settings for testing
    CACHE_ENABLED = False  # Disable caching for consistent test results
    CACHE_DIR = tempfile.mkdtemp()  # Use temporary directory
    CACHE_DURATION_HOURS = 1
    
    # Testing model settings (use smallest/fastest models)
    SUMMARIZATION_MODEL = 't5-small'
    MAX_SUMMARY_LENGTH = 100
    MIN_SUMMARY_LENGTH = 20
    
    # Testing limits (smaller for faster tests)
    MAX_TRANSCRIPT_LENGTH = 5000
    MIN_TRANSCRIPT_LENGTH = 10
    RATE_LIMIT_ENABLED = False  # Disable rate limiting for tests
    
    # Feature flags for testing (enable all for comprehensive testing)
    ENABLE_KEYWORD_EXTRACTION = True
    ENABLE_ADVANCED_SUMMARIZATION = True
    ENABLE_CONTENT_TYPE_DETECTION = True
    
    # Performance settings for testing
    THREADING = False  # Disable threading for predictable tests
    PROCESSES = 1
    
    # Testing-specific paths
    STATIC_FOLDER = 'app/static'
    TEMPLATE_FOLDER = 'app/templates'
    
    @staticmethod
    def init_app(app):
        """Initialize application for testing."""
        BaseConfig.init_app(app)
        
        # Testing-specific initialization
        import logging
        
        # Suppress most logging during tests
        logging.getLogger().setLevel(logging.ERROR)
        
        # Disable Flask's request logging
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        
        # Create temporary cache directory
        cache_dir = TestingConfig.CACHE_DIR
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
    
    @classmethod
    def get_test_data_dir(cls):
        """Get directory for test data files."""
        return os.path.join(os.path.dirname(__file__), '..', 'tests', 'data')
    
    @classmethod
    def get_mock_config(cls):
        """Get configuration for mocking external services."""
        return {
            'mock_youtube_api': True,
            'mock_transformers': True,
            'mock_nltk': True,
            'mock_file_operations': True,
            'use_test_data': True
        }
    
    @classmethod
    def get_test_urls(cls):
        """Get test URLs for testing."""
        return {
            'valid_youtube_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'valid_youtu_be_url': 'https://youtu.be/dQw4w9WgXcQ',
            'valid_embed_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
            'invalid_url': 'https://www.example.com/not-youtube',
            'malformed_url': 'not-a-url-at-all'
        }
    
    @classmethod
    def get_test_data(cls):
        """Get test data for testing."""
        return {
            'sample_transcript': """
                Welcome to this tutorial video. Today we're going to learn about Python programming.
                First, let's talk about variables. Variables are used to store data in Python.
                You can create a variable by simply assigning a value to it.
                For example, you can write: name equals "John". This creates a string variable.
                Next, we'll discuss functions. Functions are reusable blocks of code.
                You define a function using the def keyword followed by the function name.
                Remember to practice these concepts to become proficient in Python programming.
            """.strip(),
            'sample_video_info': {
                'title': 'Python Programming Tutorial',
                'channel': 'Test Education Channel',
                'description': 'Learn Python programming basics in this comprehensive tutorial.',
                'video_id': 'test123',
                'duration': 600
            },
            'sample_summary': 'This video teaches Python programming basics including variables and functions.',
            'sample_keywords': ['python', 'programming', 'variables', 'functions', 'tutorial']
        }
    
    @classmethod
    def cleanup_test_environment(cls):
        """Clean up test environment after tests."""
        import shutil
        
        # Clean up temporary cache directory
        if os.path.exists(cls.CACHE_DIR):
            try:
                shutil.rmtree(cls.CACHE_DIR)
            except Exception:
                pass  # Ignore cleanup errors
