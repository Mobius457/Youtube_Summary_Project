# config/production.py

import os
from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    FLASK_ENV = 'production'
    
    # Security settings for production
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in production
    
    # CORS settings for production
    CORS_ENABLED = True
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    # Logging settings for production
    LOG_LEVEL = 'WARNING'
    
    # Cache settings for production
    CACHE_ENABLED = True
    CACHE_DIR = os.getenv('CACHE_DIR', '/tmp/youtube_summarizer_cache')
    CACHE_DURATION_HOURS = 24
    
    # Production model settings
    SUMMARIZATION_MODEL = os.getenv('SUMMARIZATION_MODEL', 't5-base')
    MAX_SUMMARY_LENGTH = 200
    MIN_SUMMARY_LENGTH = 50
    
    # Production limits
    MAX_TRANSCRIPT_LENGTH = 50000
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_PER_MINUTE = 10
    
    # Feature flags for production
    ENABLE_KEYWORD_EXTRACTION = True
    ENABLE_ADVANCED_SUMMARIZATION = True
    ENABLE_CONTENT_TYPE_DETECTION = True
    
    # Performance settings for production
    THREADING = True
    PROCESSES = int(os.getenv('WEB_CONCURRENCY', '4'))
    
    # Production-specific paths
    STATIC_FOLDER = 'app/static'
    TEMPLATE_FOLDER = 'app/templates'
    
    @staticmethod
    def init_app(app):
        """Initialize application for production."""
        BaseConfig.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Set up file logging for production
        if not app.debug and not app.testing:
            # Create logs directory if it doesn't exist
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            # Set up rotating file handler
            file_handler = RotatingFileHandler(
                'logs/youtube_summarizer.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('YouTube Summarizer startup')
        
        # Validate production configuration
        errors = ProductionConfig.validate_production_config()
        if errors:
            for error in errors:
                app.logger.error(f"Configuration error: {error}")
            raise ValueError(f"Production configuration errors: {'; '.join(errors)}")
        
        # Create cache directory if it doesn't exist
        cache_dir = ProductionConfig.CACHE_DIR
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
    
    @classmethod
    def validate_production_config(cls):
        """Validate production-specific configuration."""
        errors = cls.validate_config()
        
        # Additional production-specific validations
        if not cls.SECRET_KEY:
            errors.append("SECRET_KEY environment variable must be set in production")
        
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            errors.append("SECRET_KEY must be changed from default value in production")
        
        if not cls.YOUTUBE_API_KEY:
            errors.append("YOUTUBE_API_KEY should be set for optimal performance in production")
        
        if cls.DEBUG:
            errors.append("DEBUG should be False in production")
        
        if not cls.CORS_ORIGINS:
            errors.append("CORS_ORIGINS should be configured for production")
        
        return errors
    
    @classmethod
    def get_database_url(cls):
        """Get database URL for production (if needed in future)."""
        return os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/youtube_summarizer')
    
    @classmethod
    def get_redis_url(cls):
        """Get Redis URL for production caching (if needed in future)."""
        return os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    @classmethod
    def get_sentry_dsn(cls):
        """Get Sentry DSN for error tracking (if needed in future)."""
        return os.getenv('SENTRY_DSN')
