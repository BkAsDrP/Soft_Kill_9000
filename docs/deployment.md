# SOFTKILL-9000 Deployment Guide

Complete guide for deploying SOFTKILL-9000 in production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Development Deployment](#development-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Security](#security)
- [Performance Tuning](#performance-tuning)

---

## Prerequisites

### System Requirements

**Minimum**:
- Python 3.9+
- 512MB RAM
- 100MB disk space
- Single CPU core

**Recommended**:
- Python 3.10+
- 2GB RAM
- 1GB disk space
- 2+ CPU cores

### Dependencies

```bash
# System dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv

# System dependencies (macOS)
brew install python@3.10

# System dependencies (RHEL/CentOS)
sudo yum install -y python3 python3-pip
```

---

## Development Deployment

### Local Setup

1. **Clone Repository**
```bash
git clone https://github.com/BkAsDrP/Softkill9000.git
cd Softkill9000
```

2. **Create Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
# Development installation
pip install -e ".[dev]"

# Verify installation
python -m softkill9000 --version
```

4. **Run Tests**
```bash
pytest
pytest --cov=softkill9000 --cov-report=html
```

5. **Run Development Server** (API)
```bash
uvicorn softkill9000.api.server:app --reload --host 127.0.0.1 --port 8000
```

### Development Tools

```bash
# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/softkill9000

# Sort imports
isort src/ tests/
```

---

## Production Deployment

### Standalone Application

1. **Install in Production Environment**
```bash
# Create production directory
mkdir -p /opt/softkill9000
cd /opt/softkill9000

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install softkill9000

# Or install from source
git clone https://github.com/BkAsDrP/Softkill9000.git
pip install -e ".[api]"
```

2. **Configuration**
```bash
# Create config directory
mkdir -p /etc/softkill9000

# Copy default config
cp configs/default_config.yaml /etc/softkill9000/production.yaml

# Edit configuration
nano /etc/softkill9000/production.yaml
```

3. **Run Application**
```bash
# CLI mode
python -m softkill9000 --config /etc/softkill9000/production.yaml

# API mode
softkill9000-api
```

### API Server with Gunicorn

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Create Gunicorn Config** (`gunicorn_config.py`)
```python
# gunicorn_config.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
timeout = 120
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/softkill9000/access.log"
errorlog = "/var/log/softkill9000/error.log"
loglevel = "info"

# Process naming
proc_name = "softkill9000-api"

# Security
limit_request_line = 4096
limit_request_fields = 100
```

3. **Start Gunicorn**
```bash
# Create log directory
sudo mkdir -p /var/log/softkill9000
sudo chown $USER:$USER /var/log/softkill9000

# Start server
gunicorn softkill9000.api.server:app -c gunicorn_config.py
```

### Systemd Service

Create `/etc/systemd/system/softkill9000.service`:

```ini
[Unit]
Description=SOFTKILL-9000 API Server
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/softkill9000
Environment="PATH=/opt/softkill9000/venv/bin"
ExecStart=/opt/softkill9000/venv/bin/gunicorn softkill9000.api.server:app -c /opt/softkill9000/gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable softkill9000
sudo systemctl start softkill9000
sudo systemctl status softkill9000
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/softkill9000`:

```nginx
upstream softkill9000_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.softkill9000.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.softkill9000.example.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.softkill9000.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.softkill9000.example.com/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Logging
    access_log /var/log/nginx/softkill9000-access.log;
    error_log /var/log/nginx/softkill9000-error.log;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20;

    location / {
        proxy_pass http://softkill9000_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /api/docs {
        proxy_pass http://softkill9000_api/api/docs;
    }

    location /health {
        proxy_pass http://softkill9000_api/health;
        access_log off;
    }
}
```

Enable and test:

```bash
sudo ln -s /etc/nginx/sites-available/softkill9000 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY pyproject.toml .
COPY README.md .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[api]"

# Copy application
COPY src/ src/
COPY configs/ configs/

# Create non-root user
RUN useradd -m -u 1000 softkill && \
    chown -R softkill:softkill /app
USER softkill

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "softkill9000.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  softkill9000-api:
    build: .
    container_name: softkill9000-api
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - WORKERS=4
    volumes:
      - ./configs:/app/configs:ro
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - softkill9000-network

  nginx:
    image: nginx:alpine
    container_name: softkill9000-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - softkill9000-api
    restart: unless-stopped
    networks:
      - softkill9000-network

networks:
  softkill9000-network:
    driver: bridge
```

### Build and Run

```bash
# Build image
docker build -t softkill9000:1.0.0 .

# Run container
docker run -d \
  --name softkill9000-api \
  -p 8000:8000 \
  -v $(pwd)/configs:/app/configs:ro \
  softkill9000:1.0.0

# Or use docker-compose
docker-compose up -d

# View logs
docker-compose logs -f softkill9000-api

# Stop
docker-compose down
```

---

## Cloud Deployment

### AWS Elastic Beanstalk

1. **Install EB CLI**
```bash
pip install awsebcli
```

2. **Initialize EB Application**
```bash
eb init -p python-3.10 softkill9000-app
```

3. **Create Environment**
```bash
eb create softkill9000-prod
```

4. **Deploy**
```bash
eb deploy
```

5. **Monitor**
```bash
eb logs
eb status
```

### AWS Lambda

Create `lambda_handler.py`:

```python
import json
from softkill9000 import MissionSimulator
from softkill9000.config import SimulationConfig, AgentConfig

def lambda_handler(event, context):
    """AWS Lambda handler for SOFTKILL-9000."""
    
    # Parse config from event
    config_data = event.get('config', {})
    
    # Create default config if not provided
    if not config_data.get('agents'):
        config_data['agents'] = [
            {'role': 'Longsight', 'species': "Vyr'khai"}
        ]
    
    # Create simulation
    config = SimulationConfig(**config_data)
    sim = MissionSimulator(config=config)
    
    # Run simulation
    sim.setup()
    results = sim.run()
    
    return {
        'statusCode': 200,
        'body': json.dumps(results),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
```

### Google Cloud Run

Create `Dockerfile` (as above) and deploy:

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/softkill9000

# Deploy
gcloud run deploy softkill9000 \
  --image gcr.io/PROJECT_ID/softkill9000 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# Create resource group
az group create --name softkill9000-rg --location eastus

# Create container
az container create \
  --resource-group softkill9000-rg \
  --name softkill9000-api \
  --image softkill9000:1.0.0 \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --dns-name-label softkill9000-api \
  --environment-variables LOG_LEVEL=INFO
```

---

## Monitoring & Maintenance

### Health Checks

Add health endpoint (in `api/server.py`):

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.now().isoformat()
    }
```

### Logging

Configure structured logging:

```python
import logging
from pythonjsonlogger import jsonlogger

# Create logger
logger = logging.getLogger()
handler = logging.StreamHandler()

# JSON formatter
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Metrics Collection

Use Prometheus for metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
simulation_counter = Counter('simulations_total', 'Total simulations run')
simulation_duration = Histogram('simulation_duration_seconds', 'Simulation duration')

# Add metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Log Rotation

Configure logrotate (`/etc/logrotate.d/softkill9000`):

```
/var/log/softkill9000/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload softkill9000
    endscript
}
```

---

## Security

### Environment Variables

Store sensitive data in environment variables:

```bash
# .env file (never commit!)
API_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
LOG_LEVEL=INFO
```

Load in application:

```python
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
```

### API Authentication

Add authentication middleware:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# Protect endpoints
@app.post("/api/simulations", dependencies=[Depends(verify_api_key)])
async def create_simulation(...):
    ...
```

### HTTPS/TLS

Use Let's Encrypt for SSL certificates:

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.softkill9000.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# firewalld (RHEL/CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## Performance Tuning

### Database Connection Pooling

If using a database:

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0
)
```

### Caching

Use Redis for caching:

```python
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379)

@lru_cache(maxsize=128)
def get_cached_results(simulation_id):
    # Check Redis first
    cached = redis_client.get(f"sim:{simulation_id}")
    if cached:
        return json.loads(cached)
    
    # Otherwise fetch and cache
    results = fetch_results(simulation_id)
    redis_client.setex(
        f"sim:{simulation_id}",
        3600,  # 1 hour TTL
        json.dumps(results)
    )
    return results
```

### Async Processing

Use Celery for background tasks:

```python
from celery import Celery

celery_app = Celery('softkill9000', broker='redis://localhost:6379/0')

@celery_app.task
def run_simulation_async(config_data):
    config = SimulationConfig(**config_data)
    sim = MissionSimulator(config=config)
    sim.setup()
    return sim.run()
```

### Resource Limits

Set resource limits in systemd service:

```ini
[Service]
MemoryLimit=2G
CPUQuota=200%
TasksMax=50
```

---

## Backup & Recovery

### Configuration Backup

```bash
#!/bin/bash
# backup_config.sh

BACKUP_DIR="/backup/softkill9000"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configs
tar -czf $BACKUP_DIR/configs_$DATE.tar.gz /etc/softkill9000/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/softkill9000/

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Database Backup

```bash
# PostgreSQL
pg_dump -U user database > backup_$(date +%Y%m%d).sql

# MongoDB
mongodump --db softkill9000 --out /backup/mongo_$(date +%Y%m%d)
```

---

**Last Updated**: November 12, 2025  
**Version**: 1.0.0  
**Maintained By**: MotionBlendAI Team
