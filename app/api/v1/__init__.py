# app/api/v1/__init__.py

"""
API v1 package for YouTube Summarizer.

Version 1 of the REST API providing video summarization endpoints.
"""

from flask import Blueprint

# Create v1 API blueprint
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/v1')

# Import and register endpoints
from . import endpoints

__all__ = ['api_v1_bp']
