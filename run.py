#!/usr/bin/env python3
"""
YouTube Summarizer Application Runner.

This script starts the Flask development server.
For production deployment, use a WSGI server like Gunicorn.
"""

import os
from app import app

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))

    print(f"Starting YouTube Summarizer on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")

    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )