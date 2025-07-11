# YouTube Video Summarizer

A powerful AI-driven web application that transforms YouTube videos into concise, insightful summaries using advanced natural language processing.

## 🌟 Features

- **AI-Powered Summarization**: Uses state-of-the-art transformer models (T5, BART) for intelligent content analysis
- **Multi-Format Support**: Works with YouTube.com, youtu.be, and embedded video URLs
- **Keyword Extraction**: Automatically identifies key topics and themes
- **Content Type Detection**: Recognizes different video types (tutorial, review, educational, etc.)
- **Professional Formatting**: Generates well-structured summaries with emojis and bullet points
- **Caching System**: Improves performance by caching processed summaries
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **RESTful API**: Clean API endpoints for integration with other applications

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Youtube_Summary_Project.git
   cd Youtube_Summary_Project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # For development
   pip install -r requirements/development.txt
   
   # For production
   pip install -r requirements/production.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# YouTube API (Optional but recommended)
YOUTUBE_API_KEY=your-youtube-api-key

# Summarization Settings
SUMMARIZATION_MODEL=t5-base
MAX_SUMMARY_LENGTH=200
DEFAULT_SUMMARY_TYPE=enhanced

# Cache Settings
CACHE_ENABLED=true
CACHE_DURATION_HOURS=24

# Feature Flags
ENABLE_KEYWORD_EXTRACTION=true
ENABLE_ADVANCED_SUMMARIZATION=true
```

### YouTube API Key (Optional)

While not required, setting up a YouTube API key improves performance and reliability:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add the key to your `.env` file

## 📖 Usage

### Web Interface

1. Open the application in your browser
2. Paste a YouTube URL in the input field
3. Click "Summarize" and wait for processing
4. View the generated summary, keywords, and key points

### API Usage

#### Summarize a Video

```bash
curl -X POST http://localhost:5000/summarize \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

Response:
```json
{
  "summary": "Enhanced summary of the video content...",
  "keywords": "keyword1, keyword2, keyword3",
  "video_info": {
    "title": "Video Title",
    "channel": "Channel Name",
    "description": "Video description..."
  }
}
```

## 🏗️ Architecture

### Project Structure

```
Youtube_Summary_Project/
├── app/
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   ├── utils/           # Utility functions
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   └── routes.py        # Flask routes
├── config/              # Configuration files
├── tests/               # Test suite
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── requirements/        # Dependencies
```

### Key Components

- **Models**: Data structures for videos, summaries, and requests
- **Services**: Business logic layer (VideoService, SummaryService)
- **Utils**: Core functionality (transcript fetching, summarization, keyword extraction)
- **Templates**: Jinja2 templates with responsive design
- **Static Assets**: CSS, JavaScript, and images

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_routes.py

# Run with verbose output
pytest -v
```

### Test Structure

- `tests/test_models/` - Model validation tests
- `tests/test_services/` - Business logic tests
- `tests/test_utils/` - Utility function tests
- `tests/test_routes.py` - API endpoint tests

## 🚀 Deployment

### Local Development

```bash
export FLASK_ENV=development
python run.py
```

### Production Deployment

#### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

#### Using Docker

```bash
# Build image
docker build -t youtube-summarizer .

# Run container
docker run -p 8000:8000 youtube-summarizer
```

#### Environment-Specific Configurations

- **Development**: `config/development.py`
- **Production**: `config/production.py`
- **Testing**: `config/testing.py`

## 🔍 Troubleshooting

### Common Issues

1. **"No English captions found"**
   - The video must have English captions (auto-generated or manual)
   - Try a different video with captions

2. **"Invalid YouTube URL"**
   - Ensure the URL is from YouTube (youtube.com or youtu.be)
   - Check that the video is public and accessible

3. **Slow processing**
   - Large videos take longer to process
   - Consider using a YouTube API key for better performance
   - Check your internet connection

4. **Memory issues**
   - Large transcripts may cause memory issues
   - Adjust `MAX_TRANSCRIPT_LENGTH` in configuration

### Performance Optimization

- Enable caching with `CACHE_ENABLED=true`
- Use a YouTube API key
- Consider using a smaller model for faster processing
- Implement Redis for distributed caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Hugging Face Transformers](https://huggingface.co/transformers/) for NLP models
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video processing
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [NLTK](https://www.nltk.org/) for natural language processing

## 📞 Support

- Create an issue for bug reports or feature requests
- Check the [documentation](docs/) for detailed information
- Review [troubleshooting guide](docs/TROUBLESHOOTING.md) for common issues
