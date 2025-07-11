# app/__init__.py

"""
YouTube Summarizer Flask Application.

This module initializes the Flask application with all necessary
configurations, blueprints, and extensions.
"""

import os
import logging
from flask import Flask
from config import get_config


def create_app(config_name=None):
    """
    Application factory pattern.

    Args:
        config_name: Configuration environment name

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize configuration
    config_class.init_app(app)

    # Setup logging
    setup_logging(app)

    # Register blueprints
    register_blueprints(app)

    # Register error handlers
    register_error_handlers(app)

    return app


def setup_logging(app):
    """Setup application logging."""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # Setup file logging
        file_handler = logging.FileHandler('logs/youtube_summarizer.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('YouTube Summarizer startup')


def register_blueprints(app):
    """Register application blueprints."""
    # Register API blueprint
    from app.api import api_bp
    app.register_blueprint(api_bp)


def register_error_handlers(app):
    """Register global error handlers."""
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('error.html', error_code=404), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        app.logger.error(f'Server Error: {error}')
        return render_template('error.html', error_code=500), 500


# Create application instance
app = create_app()

# Import routes (this must be after app creation)
from app import routes