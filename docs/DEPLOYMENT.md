# Deployment Guide

This guide covers various deployment options for the YouTube Summarizer application.

## 🚀 Deployment Options

### 1. Local Development

For development and testing purposes.

```bash
# Set environment
export FLASK_ENV=development

# Run with Flask development server
python run.py

# Or with auto-reload
flask run --reload
```

**Pros:**
- Easy setup
- Auto-reload on changes
- Debug mode enabled

**Cons:**
- Not suitable for production
- Single-threaded
- No load balancing

---

### 2. Production with Gunicorn

Recommended for production deployments.

#### Basic Setup

```bash
# Install production dependencies
pip install -r requirements/production.txt

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

#### Advanced Configuration

```bash
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 60
keepalive = 5
preload_app = True
```

```bash
# Run with config file
gunicorn -c gunicorn.conf.py run:app
```

**Pros:**
- Production-ready
- Multi-worker support
- Good performance
- Configurable

**Cons:**
- Requires additional setup
- No built-in load balancing

---

### 3. Docker Deployment

Containerized deployment for consistency across environments.

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "run:app"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
    volumes:
      - ./cache:/app/cache
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

#### Build and Run

```bash
# Build image
docker build -t youtube-summarizer .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e YOUTUBE_API_KEY=your-api-key \
  youtube-summarizer

# Or with Docker Compose
docker-compose up -d
```

**Pros:**
- Consistent environment
- Easy scaling
- Isolated dependencies
- Portable

**Cons:**
- Additional complexity
- Resource overhead
- Requires Docker knowledge

---

### 4. Cloud Platform Deployments

#### Heroku

```bash
# Install Heroku CLI
# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set YOUTUBE_API_KEY=your-api-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main
```

**Procfile:**
```
web: gunicorn run:app
```

#### Vercel

The project includes `vercel.json` for Vercel deployment:

```json
{
  "builds": [
    {
      "src": "app/routes.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/routes.py"
    }
  ]
}
```

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

#### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Google Cloud Platform

```yaml
# app.yaml for App Engine
runtime: python311

env_variables:
  SECRET_KEY: "your-secret-key"
  YOUTUBE_API_KEY: "your-api-key"
  FLASK_ENV: "production"

automatic_scaling:
  min_instances: 1
  max_instances: 10
```

```bash
# Deploy to App Engine
gcloud app deploy
```

---

### 5. VPS/Server Deployment

For deployment on virtual private servers or dedicated servers.

#### Nginx + Gunicorn Setup

1. **Install dependencies:**
```bash
sudo apt update
sudo apt install python3 python3-pip nginx supervisor
```

2. **Setup application:**
```bash
# Clone repository
git clone https://github.com/your-username/Youtube_Summary_Project.git
cd Youtube_Summary_Project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/production.txt
```

3. **Configure Nginx:**
```nginx
# /etc/nginx/sites-available/youtube-summarizer
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/Youtube_Summary_Project/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

4. **Configure Supervisor:**
```ini
# /etc/supervisor/conf.d/youtube-summarizer.conf
[program:youtube-summarizer]
command=/path/to/Youtube_Summary_Project/venv/bin/gunicorn -c gunicorn.conf.py run:app
directory=/path/to/Youtube_Summary_Project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/youtube-summarizer.log
```

5. **Enable and start services:**
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/youtube-summarizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Start Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start youtube-summarizer
```

---

## 🔧 Environment Configuration

### Environment Variables

Set these environment variables for production:

```bash
# Required
export SECRET_KEY="your-very-secure-secret-key"
export FLASK_ENV="production"

# Optional but recommended
export YOUTUBE_API_KEY="your-youtube-api-key"

# Cache configuration
export CACHE_ENABLED="true"
export CACHE_DIR="/tmp/youtube_summarizer_cache"

# Performance tuning
export WEB_CONCURRENCY="4"
export MAX_TRANSCRIPT_LENGTH="50000"

# Security
export WTF_CSRF_ENABLED="true"
export CORS_ORIGINS="https://your-domain.com"
```

### Configuration Files

Create environment-specific configuration:

```python
# config/production.py
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    # ... other settings
```

---

## 📊 Monitoring and Logging

### Application Monitoring

1. **Health Checks:**
```python
# Add to routes.py
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
```

2. **Metrics Collection:**
```python
# Using Prometheus
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)
```

### Logging Configuration

```python
# Production logging setup
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/youtube_summarizer.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

---

## 🔒 Security Considerations

### SSL/HTTPS

1. **Let's Encrypt (Free):**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

2. **Nginx SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
}
```

### Security Headers

```python
# Using Flask-Talisman
from flask_talisman import Talisman

Talisman(app, force_https=True)
```

### Rate Limiting

```python
# Using Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/summarize', methods=['POST'])
@limiter.limit("10 per minute")
def summarize():
    # ... route logic
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use:**
```bash
# Find process using port
sudo lsof -i :8000
# Kill process
sudo kill -9 PID
```

2. **Permission denied:**
```bash
# Fix file permissions
sudo chown -R www-data:www-data /path/to/app
sudo chmod -R 755 /path/to/app
```

3. **Memory issues:**
```bash
# Monitor memory usage
htop
# Adjust worker count
gunicorn -w 2 run:app  # Reduce workers
```

4. **SSL certificate issues:**
```bash
# Renew Let's Encrypt certificate
sudo certbot renew
sudo systemctl reload nginx
```

### Performance Optimization

1. **Enable caching:**
```python
CACHE_ENABLED = True
CACHE_DURATION_HOURS = 24
```

2. **Use CDN for static files:**
```nginx
location /static {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

3. **Database optimization (if using):**
```python
# Connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': -1,
    'pool_pre_ping': True
}
```

---

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer Setup:**
```nginx
upstream app_servers {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://app_servers;
    }
}
```

2. **Multiple App Instances:**
```bash
# Run multiple instances
gunicorn -w 4 -b 127.0.0.1:8000 run:app &
gunicorn -w 4 -b 127.0.0.1:8001 run:app &
gunicorn -w 4 -b 127.0.0.1:8002 run:app &
```

### Vertical Scaling

1. **Increase worker count:**
```bash
# Calculate workers: (2 x CPU cores) + 1
gunicorn -w 9 run:app  # For 4-core server
```

2. **Optimize memory usage:**
```python
# Use smaller models for better performance
SUMMARIZATION_MODEL = "t5-small"
```

This deployment guide provides comprehensive options for deploying the YouTube Summarizer application across different environments and platforms.
