# config/base.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    """Base configuration class with common settings."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_APP = os.getenv('FLASK_APP', 'run.py')
    
    # YouTube API settings
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Cache settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_DIR = os.getenv('CACHE_DIR', 'cache')
    CACHE_DURATION_HOURS = int(os.getenv('CACHE_DURATION_HOURS', '24'))
    
    # Summarization settings
    DEFAULT_SUMMARY_TYPE = os.getenv('DEFAULT_SUMMARY_TYPE', 'enhanced')
    MAX_TRANSCRIPT_LENGTH = int(os.getenv('MAX_TRANSCRIPT_LENGTH', '50000'))
    MIN_TRANSCRIPT_LENGTH = int(os.getenv('MIN_TRANSCRIPT_LENGTH', '50'))
    
    # Model settings
    SUMMARIZATION_MODEL = os.getenv('SUMMARIZATION_MODEL', 't5-base')
    MAX_SUMMARY_LENGTH = int(os.getenv('MAX_SUMMARY_LENGTH', '200'))
    MIN_SUMMARY_LENGTH = int(os.getenv('MIN_SUMMARY_LENGTH', '50'))
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '10'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Security settings
    WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED', 'true').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = int(os.getenv('WTF_CSRF_TIME_LIMIT', '3600'))
    
    # CORS settings
    CORS_ENABLED = os.getenv('CORS_ENABLED', 'false').lower() == 'true'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Performance settings
    THREADING = os.getenv('THREADING', 'true').lower() == 'true'
    PROCESSES = int(os.getenv('PROCESSES', '1'))
    
    # Feature flags
    ENABLE_KEYWORD_EXTRACTION = os.getenv('ENABLE_KEYWORD_EXTRACTION', 'true').lower() == 'true'
    ENABLE_ADVANCED_SUMMARIZATION = os.getenv('ENABLE_ADVANCED_SUMMARIZATION', 'true').lower() == 'true'
    ENABLE_CONTENT_TYPE_DETECTION = os.getenv('ENABLE_CONTENT_TYPE_DETECTION', 'true').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """Initialize application with this configuration."""
        pass
    
    @classmethod
    def get_cache_config(cls):
        """Get cache-related configuration."""
        return {
            'enabled': cls.CACHE_ENABLED,
            'directory': cls.CACHE_DIR,
            'duration_hours': cls.CACHE_DURATION_HOURS
        }
    
    @classmethod
    def get_summarization_config(cls):
        """Get summarization-related configuration."""
        return {
            'model': cls.SUMMARIZATION_MODEL,
            'max_length': cls.MAX_SUMMARY_LENGTH,
            'min_length': cls.MIN_SUMMARY_LENGTH,
            'max_transcript_length': cls.MAX_TRANSCRIPT_LENGTH,
            'min_transcript_length': cls.MIN_TRANSCRIPT_LENGTH,
            'default_type': cls.DEFAULT_SUMMARY_TYPE
        }
    
    @classmethod
    def get_feature_flags(cls):
        """Get feature flag configuration."""
        return {
            'keyword_extraction': cls.ENABLE_KEYWORD_EXTRACTION,
            'advanced_summarization': cls.ENABLE_ADVANCED_SUMMARIZATION,
            'content_type_detection': cls.ENABLE_CONTENT_TYPE_DETECTION,
            'rate_limiting': cls.RATE_LIMIT_ENABLED,
            'caching': cls.CACHE_ENABLED,
            'cors': cls.CORS_ENABLED
        }
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings."""
        errors = []
        
        # Check required settings
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY must be set to a secure value in production")
        
        # Validate numeric settings
        if cls.MAX_TRANSCRIPT_LENGTH <= 0:
            errors.append("MAX_TRANSCRIPT_LENGTH must be positive")
        
        if cls.MIN_TRANSCRIPT_LENGTH <= 0:
            errors.append("MIN_TRANSCRIPT_LENGTH must be positive")
        
        if cls.MAX_TRANSCRIPT_LENGTH <= cls.MIN_TRANSCRIPT_LENGTH:
            errors.append("MAX_TRANSCRIPT_LENGTH must be greater than MIN_TRANSCRIPT_LENGTH")
        
        if cls.MAX_SUMMARY_LENGTH <= cls.MIN_SUMMARY_LENGTH:
            errors.append("MAX_SUMMARY_LENGTH must be greater than MIN_SUMMARY_LENGTH")
        
        if cls.CACHE_DURATION_HOURS <= 0:
            errors.append("CACHE_DURATION_HOURS must be positive")
        
        # Validate model settings
        valid_models = ['t5-base', 't5-small', 't5-large', 'facebook/bart-base', 'facebook/bart-large']
        if cls.SUMMARIZATION_MODEL not in valid_models:
            errors.append(f"SUMMARIZATION_MODEL must be one of: {', '.join(valid_models)}")
        
        # Validate summary types
        valid_types = ['basic', 'enhanced', 'professional', 'detailed']
        if cls.DEFAULT_SUMMARY_TYPE not in valid_types:
            errors.append(f"DEFAULT_SUMMARY_TYPE must be one of: {', '.join(valid_types)}")
        
        return errors
