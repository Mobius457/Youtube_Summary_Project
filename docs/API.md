# API Documentation

The YouTube Summarizer provides a RESTful API for programmatic access to video summarization functionality.

## Base URL

```
http://localhost:5000  # Development
https://your-domain.com  # Production
```

## Authentication

Currently, the API does not require authentication. Rate limiting may be applied based on configuration.

## Endpoints

### 1. Get Home Page

**GET** `/` or `/index`

Returns the main application page.

**Response:**
- **200 OK**: HTML page

---

### 2. Summarize Video

**POST** `/summarize`

Generates a summary for a YouTube video.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Parameters:**
- `url` (string, required): Valid YouTube URL

**Response:**

**Success (200 OK):**
```json
{
  "summary": "🎬 The video \"Video Title\" by Channel Name provides a comprehensive overview of the topic...",
  "keywords": "keyword1, keyword2, keyword3, keyword4, keyword5",
  "video_info": {
    "title": "Video Title",
    "channel": "Channel Name", 
    "description": "Video description text..."
  }
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "error": "URL is required."
}
```

**500 Internal Server Error:**
```json
{
  "error": "No English captions found."
}
```

---

## Request Examples

### cURL

```bash
# Basic summarization request
curl -X POST http://localhost:5000/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Python

```python
import requests

url = "http://localhost:5000/summarize"
data = {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

response = requests.post(url, json=data)
result = response.json()

if response.status_code == 200:
    print("Summary:", result["summary"])
    print("Keywords:", result["keywords"])
else:
    print("Error:", result["error"])
```

### JavaScript

```javascript
const summarizeVideo = async (videoUrl) => {
  try {
    const response = await fetch('/summarize', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: videoUrl })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Something went wrong');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error.message);
    throw error;
  }
};

// Usage
summarizeVideo('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
  .then(result => {
    console.log('Summary:', result.summary);
    console.log('Keywords:', result.keywords);
  })
  .catch(error => {
    console.error('Failed to summarize:', error);
  });
```

## Response Format

### Summary Response

The API returns a JSON object with the following structure:

```json
{
  "summary": "string",      // Enhanced summary with emojis and formatting
  "keywords": "string",     // Comma-separated keywords
  "video_info": {
    "title": "string",      // Video title
    "channel": "string",    // Channel name
    "description": "string" // Video description (may be truncated)
  }
}
```

### Error Response

Error responses follow this format:

```json
{
  "error": "string"  // Human-readable error message
}
```

## Supported URL Formats

The API accepts various YouTube URL formats:

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/v/VIDEO_ID`

URLs with additional parameters are also supported:
- `https://www.youtube.com/watch?v=VIDEO_ID&t=30s`
- `https://youtu.be/VIDEO_ID?t=30`

## Error Codes

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| 200 | Success | Request processed successfully |
| 400 | Bad Request | Missing or invalid URL |
| 404 | Not Found | Invalid endpoint |
| 405 | Method Not Allowed | Wrong HTTP method |
| 500 | Internal Server Error | Video processing error, no captions, etc. |

## Rate Limiting

Rate limiting may be applied based on configuration:

- Default: No rate limiting in development
- Production: Configurable via `RATE_LIMIT_PER_MINUTE`

When rate limited, the API returns:

```json
{
  "error": "Rate limit exceeded. Please try again later."
}
```

## Processing Time

Processing times vary based on:

- Video length
- Transcript complexity
- Server resources
- Model size

Typical processing times:
- Short videos (< 10 min): 5-15 seconds
- Medium videos (10-30 min): 15-45 seconds
- Long videos (> 30 min): 45+ seconds

## Limitations

### Video Requirements

- Must be publicly accessible
- Must have English captions (auto-generated or manual)
- Must be a valid YouTube video

### Content Limitations

- Maximum transcript length: 50,000 characters (configurable)
- Minimum transcript length: 50 characters (configurable)
- Very long videos may timeout or fail

### Technical Limitations

- No batch processing (one video at a time)
- No real-time streaming
- No video download (transcript only)

## Best Practices

### Error Handling

Always implement proper error handling:

```python
try:
    response = requests.post(url, json=data, timeout=60)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except ValueError as e:
    print(f"Invalid JSON response: {e}")
```

### Timeout Handling

Set appropriate timeouts for requests:

```python
# Allow up to 60 seconds for processing
response = requests.post(url, json=data, timeout=60)
```

### Retry Logic

Implement retry logic for transient failures:

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

## Future API Enhancements

Planned features for future versions:

- Batch processing endpoint
- Summary customization options
- Multiple output formats
- Webhook support
- API key authentication
- Advanced filtering options
