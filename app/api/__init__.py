# app/api/__init__.py

"""
API package for YouTube Summarizer.

This package contains versioned API endpoints for programmatic access
to the application's functionality.
"""

from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import version-specific blueprints
from .v1 import api_v1_bp

# Register version blueprints
api_bp.register_blueprint(api_v1_bp)

__all__ = ['api_bp']
