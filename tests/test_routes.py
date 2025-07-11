# tests/test_routes.py

import pytest
import json
from unittest.mock import patch, Mock


class TestRoutes:
    """Test cases for application routes."""
    
    def test_index_route(self, client):
        """Test the index route returns the main page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'YouTube Video Summarizer' in response.data
    
    def test_index_route_alternative(self, client):
        """Test the alternative index route."""
        response = client.get('/index')
        assert response.status_code == 200
        assert b'YouTube Video Summarizer' in response.data
    
    @patch('app.routes.run_summarization')
    @patch('app.routes.get_transcript')
    @patch('app.routes.extract_video_info')
    def test_summarize_route_success(self, mock_extract_info, mock_get_transcript, 
                                   mock_run_summarization, client):
        """Test successful summarization request."""
        # Mock the functions
        mock_extract_info.return_value = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'description': 'Test description'
        }
        mock_get_transcript.return_value = "This is a test transcript."
        mock_run_summarization.return_value = ("Test summary", "test, keywords")
        
        # Make request
        response = client.post('/summarize', 
                             data=json.dumps({'url': 'https://www.youtube.com/watch?v=test123'}),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'summary' in data
        assert 'keywords' in data
        assert data['summary'] == 'Test summary'
        assert data['keywords'] == 'test, keywords'
    
    def test_summarize_route_missing_url(self, client):
        """Test summarization request with missing URL."""
        response = client.post('/summarize', 
                             data=json.dumps({}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'URL is required' in data['error']
    
    def test_summarize_route_empty_url(self, client):
        """Test summarization request with empty URL."""
        response = client.post('/summarize', 
                             data=json.dumps({'url': ''}),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.routes.extract_video_info')
    def test_summarize_route_extract_info_error(self, mock_extract_info, client):
        """Test summarization when video info extraction fails."""
        mock_extract_info.side_effect = Exception("Video not found")
        
        response = client.post('/summarize', 
                             data=json.dumps({'url': 'https://www.youtube.com/watch?v=test123'}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.routes.get_transcript')
    @patch('app.routes.extract_video_info')
    def test_summarize_route_transcript_error(self, mock_extract_info, mock_get_transcript, client):
        """Test summarization when transcript extraction fails."""
        mock_extract_info.return_value = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'description': 'Test description'
        }
        mock_get_transcript.side_effect = Exception("No captions available")
        
        response = client.post('/summarize', 
                             data=json.dumps({'url': 'https://www.youtube.com/watch?v=test123'}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    @patch('app.routes.run_summarization')
    @patch('app.routes.get_transcript')
    @patch('app.routes.extract_video_info')
    def test_summarize_route_summarization_error(self, mock_extract_info, mock_get_transcript, 
                                               mock_run_summarization, client):
        """Test summarization when summary generation fails."""
        mock_extract_info.return_value = {
            'title': 'Test Video',
            'channel': 'Test Channel',
            'description': 'Test description'
        }
        mock_get_transcript.return_value = "This is a test transcript."
        mock_run_summarization.side_effect = Exception("Summarization failed")
        
        response = client.post('/summarize', 
                             data=json.dumps({'url': 'https://www.youtube.com/watch?v=test123'}),
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_summarize_route_invalid_json(self, client):
        """Test summarization with invalid JSON data."""
        response = client.post('/summarize', 
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_summarize_route_wrong_method(self, client):
        """Test summarization endpoint with wrong HTTP method."""
        response = client.get('/summarize')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_nonexistent_route(self, client):
        """Test accessing a non-existent route."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
