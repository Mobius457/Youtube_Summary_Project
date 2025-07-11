# app/routes.py

from flask import render_template, request, jsonify, current_app
from datetime import datetime
import time

from app import app
from app.services.video_service import VideoService
from app.services.summary_service import SummaryService
from app.services.cache_service import CacheService
from app.models.summary import SummaryRequest, SummaryResponse, SummaryStatus, SummaryType
from app.models.video import Video, VideoInfo

# Initialize services
cache_service = CacheService()


@app.route('/')
@app.route('/index')
def index():
    """Main page route."""
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    """
    Main summarization endpoint.

    Handles video summarization requests from the web interface.
    """
    start_time = time.time()

    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400

        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required.'}), 400

        # Validate YouTube URL
        if not VideoService.validate_youtube_url(url):
            return jsonify({'error': 'Please provide a valid YouTube URL.'}), 400

        # Check cache first
        if current_app.config.get('CACHE_ENABLED', True):
            cached_result = cache_service.get_cached_summary(url)
            if cached_result:
                current_app.logger.info(f"Returning cached result for URL: {url}")
                return jsonify({
                    'summary': cached_result['summary'].content if hasattr(cached_result['summary'], 'content') else cached_result['summary'],
                    'keywords': cached_result['keywords'],
                    'video_info': cached_result['video_info'],
                    'cached': True
                })

        # Get video data using the service
        try:
            transcript, video_info = VideoService.get_video_data(url)
            current_app.logger.info(f"Retrieved video data for: {video_info.get('title', 'Unknown')}")
        except Exception as e:
            current_app.logger.error(f"Failed to get video data: {str(e)}")
            return jsonify({'error': str(e)}), 500

        # Generate summary using the service
        try:
            summary_text, keywords = SummaryService.generate_summary(transcript, video_info)
            current_app.logger.info(f"Generated summary for: {video_info.get('title', 'Unknown')}")
        except Exception as e:
            current_app.logger.error(f"Failed to generate summary: {str(e)}")
            return jsonify({'error': f'Failed to generate summary: {str(e)}'}), 500

        processing_time = time.time() - start_time

        # Cache the result
        if current_app.config.get('CACHE_ENABLED', True):
            try:
                cache_service.cache_summary(url, summary_text, keywords, video_info)
                current_app.logger.info(f"Cached summary for: {video_info.get('title', 'Unknown')}")
            except Exception as e:
                current_app.logger.warning(f"Failed to cache summary: {str(e)}")

        # Log successful processing
        current_app.logger.info(f"Successfully processed video in {processing_time:.2f}s")

        # Return the results as JSON
        return jsonify({
            'summary': summary_text,
            'keywords': keywords,
            'video_info': video_info,
            'processing_time': processing_time
        })

    except Exception as e:
        # Log the error
        current_app.logger.error(f"Unexpected error in summarize route: {str(e)}")

        # Return generic error message
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500


@app.route('/summary/<video_id>')
def view_summary(video_id):
    """
    Display a dedicated summary page for a video.

    Args:
        video_id: YouTube video ID
    """
    try:
        # Construct URL from video ID
        url = f"https://www.youtube.com/watch?v={video_id}"

        # Check if we have a cached summary
        if current_app.config.get('CACHE_ENABLED', True):
            cached_result = cache_service.get_cached_summary(url)
            if cached_result:
                return render_template('summary.html',
                                     summary=cached_result['summary'],
                                     keywords=cached_result['keywords'].split(', ') if isinstance(cached_result['keywords'], str) else cached_result['keywords'],
                                     video_info=cached_result['video_info'])

        # If no cached result, redirect to main page
        return render_template('error.html',
                             error_code=404,
                             error_message="Summary not found. Please generate a summary first.")

    except Exception as e:
        current_app.logger.error(f"Error displaying summary: {str(e)}")
        return render_template('error.html',
                             error_code=500,
                             error_message="An error occurred while loading the summary.")


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })


@app.route('/cache/stats')
def cache_stats():
    """Get cache statistics (admin endpoint)."""
    if not current_app.config.get('CACHE_ENABLED', True):
        return jsonify({'cache_enabled': False})

    try:
        stats = cache_service.get_cache_stats()
        return jsonify({
            'cache_enabled': True,
            'stats': stats
        })
    except Exception as e:
        current_app.logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({'error': 'Failed to get cache statistics'}), 500


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html',
                         error_code=404,
                         error_message="The page you're looking for doesn't exist."), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    current_app.logger.error(f"Internal server error: {str(error)}")
    return render_template('error.html',
                         error_code=500,
                         error_message="An internal server error occurred."), 500


@app.errorhandler(400)
def bad_request_error(error):
    """Handle 400 errors."""
    return render_template('error.html',
                         error_code=400,
                         error_message="Bad request. Please check your input."), 400


# Context processors
@app.context_processor
def inject_config():
    """Inject configuration into templates."""
    return {
        'config': current_app.config,
        'now': datetime.utcnow()
    }