# config/development.py

import os
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    # Flask settings
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    FLASK_ENV = 'development'
    
    # Relaxed security for development
    WTF_CSRF_ENABLED = False
    
    # Enable CORS for development (frontend/backend separation)
    CORS_ENABLED = True
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:5000']
    
    # Logging settings for development
    LOG_LEVEL = 'DEBUG'
    
    # Cache settings for development
    CACHE_ENABLED = True
    CACHE_DIR = 'dev_cache'
    CACHE_DURATION_HOURS = 1  # Shorter cache for development
    
    # Development model settings (faster models for quicker iteration)
    SUMMARIZATION_MODEL = 't5-small'  # Smaller model for faster development
    MAX_SUMMARY_LENGTH = 150
    MIN_SUMMARY_LENGTH = 30
    
    # Relaxed limits for development
    MAX_TRANSCRIPT_LENGTH = 10000  # Smaller for faster processing
    RATE_LIMIT_PER_MINUTE = 100  # Higher limit for development
    
    # Enable all features for development testing
    ENABLE_KEYWORD_EXTRACTION = True
    ENABLE_ADVANCED_SUMMARIZATION = True
    ENABLE_CONTENT_TYPE_DETECTION = True
    
    # Development-specific paths
    STATIC_FOLDER = 'app/static'
    TEMPLATE_FOLDER = 'app/templates'
    
    @staticmethod
    def init_app(app):
        """Initialize application for development."""
        BaseConfig.init_app(app)
        
        # Development-specific initialization
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        # Create cache directory if it doesn't exist
        cache_dir = DevelopmentConfig.CACHE_DIR
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        
        # Print configuration info for development
        print(f"Development mode enabled")
        print(f"Cache directory: {cache_dir}")
        print(f"Debug mode: {DevelopmentConfig.DEBUG}")
        print(f"Model: {DevelopmentConfig.SUMMARIZATION_MODEL}")
    
    @classmethod
    def get_database_url(cls):
        """Get database URL for development (if needed in future)."""
        return os.getenv('DEV_DATABASE_URL', 'sqlite:///dev_youtube_summarizer.db')
    
    @classmethod
    def get_redis_url(cls):
        """Get Redis URL for development caching (if needed in future)."""
        return os.getenv('DEV_REDIS_URL', 'redis://localhost:6379/0')
