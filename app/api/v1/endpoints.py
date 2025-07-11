# app/api/v1/endpoints.py

"""
API v1 endpoints for YouTube Summarizer.

This module contains all REST API endpoints for version 1.
"""

from flask import request, jsonify, current_app
from datetime import datetime
import time

from . import api_v1_bp
from app.services.video_service import VideoService
from app.services.summary_service import SummaryService
from app.services.cache_service import CacheService
from app.models.summary import SummaryRequest, SummaryResponse, SummaryStatus
from app.models.video import Video, VideoInfo


# Initialize services
cache_service = CacheService()


@api_v1_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'YouTube Summarizer API v1'
    })


@api_v1_bp.route('/info', methods=['GET'])
def api_info():
    """
    API information endpoint.
    
    Returns:
        JSON response with API information
    """
    return jsonify({
        'name': 'YouTube Summarizer API',
        'version': '1.0.0',
        'description': 'AI-powered YouTube video summarization service',
        'endpoints': {
            'health': '/api/v1/health',
            'info': '/api/v1/info',
            'summarize': '/api/v1/summarize',
            'video_info': '/api/v1/video/{video_id}',
            'cache_stats': '/api/v1/cache/stats'
        },
        'documentation': '/docs/api',
        'support': 'https://github.com/your-username/Youtube_Summary_Project'
    })


@api_v1_bp.route('/summarize', methods=['POST'])
def summarize_video():
    """
    Summarize a YouTube video.
    
    Request Body:
        {
            "url": "https://www.youtube.com/watch?v=VIDEO_ID",
            "summary_type": "enhanced",  # optional
            "max_length": 200,           # optional
            "include_keywords": true,    # optional
            "language": "en"             # optional
        }
    
    Returns:
        JSON response with summary data
    """
    start_time = time.time()
    
    try:
        # Validate request
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Create summary request object
        try:
            summary_request = SummaryRequest.from_dict(data)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Check cache first
        if current_app.config.get('CACHE_ENABLED', True):
            cached_result = cache_service.get_cached_summary(summary_request.url)
            if cached_result:
                processing_time = time.time() - start_time
                
                # Create response from cache
                response = SummaryResponse(
                    summary=cached_result['summary'],
                    video_info=cached_result['video_info'],
                    status=SummaryStatus.CACHED,
                    cached=True,
                    processing_stats={
                        'processing_time': processing_time,
                        'cached_at': cached_result['cached_at']
                    }
                )
                
                return jsonify(response.to_dict())
        
        # Get video data
        try:
            transcript, video_info = VideoService.get_video_data(summary_request.url)
        except Exception as e:
            error_response = SummaryResponse.create_error_response(
                str(e), 
                {'title': 'Unknown', 'channel': 'Unknown', 'description': ''}
            )
            return jsonify(error_response.to_dict()), 500
        
        # Generate summary
        try:
            summary_text, keywords = SummaryService.generate_summary(transcript, video_info)
        except Exception as e:
            error_response = SummaryResponse.create_error_response(
                f"Failed to generate summary: {str(e)}", 
                video_info
            )
            return jsonify(error_response.to_dict()), 500
        
        processing_time = time.time() - start_time
        
        # Create summary object
        from app.models.summary import Summary
        summary = Summary(
            content=summary_text,
            keywords=keywords.split(', ') if keywords else [],
            summary_type=summary_request.summary_type,
            processing_time=processing_time
        )
        
        # Create response
        response = SummaryResponse(
            summary=summary,
            video_info=video_info,
            status=SummaryStatus.COMPLETED,
            processing_stats={
                'processing_time': processing_time,
                'transcript_length': len(transcript),
                'summary_length': len(summary_text)
            }
        )
        
        # Cache the result
        if current_app.config.get('CACHE_ENABLED', True):
            cache_service.cache_summary(
                summary_request.url,
                summary_text,
                keywords,
                video_info
            )
        
        return jsonify(response.to_dict())
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in summarize_video: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@api_v1_bp.route('/video/<video_id>', methods=['GET'])
def get_video_info(video_id):
    """
    Get video information without summarization.
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        JSON response with video information
    """
    try:
        # Construct YouTube URL from video ID
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Validate URL
        if not VideoService.validate_youtube_url(url):
            return jsonify({'error': 'Invalid video ID'}), 400
        
        # Get video info
        video_info = VideoService.get_video_info_only(url)
        
        return jsonify({
            'video_id': video_id,
            'video_info': video_info,
            'url': url
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting video info: {str(e)}")
        return jsonify({'error': 'Failed to get video information'}), 500


@api_v1_bp.route('/cache/stats', methods=['GET'])
def get_cache_stats():
    """
    Get cache statistics.
    
    Returns:
        JSON response with cache statistics
    """
    try:
        if not current_app.config.get('CACHE_ENABLED', True):
            return jsonify({
                'cache_enabled': False,
                'message': 'Caching is disabled'
            })
        
        stats = cache_service.get_cache_stats()
        
        return jsonify({
            'cache_enabled': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting cache stats: {str(e)}")
        return jsonify({'error': 'Failed to get cache statistics'}), 500


@api_v1_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear cache (all entries or expired only).
    
    Request Body:
        {
            "clear_all": false  # optional, default false (clear expired only)
        }
    
    Returns:
        JSON response with operation result
    """
    try:
        if not current_app.config.get('CACHE_ENABLED', True):
            return jsonify({
                'cache_enabled': False,
                'message': 'Caching is disabled'
            }), 400
        
        data = request.get_json() or {}
        clear_all = data.get('clear_all', False)
        
        if clear_all:
            removed_count = cache_service.clear_all_cache()
            message = f"Cleared all cache entries ({removed_count} removed)"
        else:
            removed_count = cache_service.clear_expired_cache()
            message = f"Cleared expired cache entries ({removed_count} removed)"
        
        return jsonify({
            'success': True,
            'message': message,
            'removed_count': removed_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({'error': 'Failed to clear cache'}), 500


@api_v1_bp.route('/batch/summarize', methods=['POST'])
def batch_summarize():
    """
    Batch summarize multiple videos (future feature).
    
    Request Body:
        {
            "urls": ["url1", "url2", "url3"],
            "summary_type": "enhanced",  # optional
            "max_concurrent": 3          # optional
        }
    
    Returns:
        JSON response with batch operation status
    """
    return jsonify({
        'error': 'Batch summarization is not yet implemented',
        'message': 'This feature is planned for a future release',
        'status': 'not_implemented'
    }), 501


# Error handlers for API v1
@api_v1_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    return jsonify({
        'error': 'Bad Request',
        'message': 'The request was invalid or malformed',
        'status_code': 400
    }), 400


@api_v1_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found',
        'status_code': 404
    }), 404


@api_v1_bp.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 Method Not Allowed errors."""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The HTTP method is not allowed for this endpoint',
        'status_code': 405
    }), 405


@api_v1_bp.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error."""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500


# Rate limiting decorator (for future use)
def rate_limit(max_requests=10, per_minutes=1):
    """
    Rate limiting decorator (placeholder for future implementation).
    
    Args:
        max_requests: Maximum number of requests
        per_minutes: Time window in minutes
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            # TODO: Implement rate limiting logic
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
