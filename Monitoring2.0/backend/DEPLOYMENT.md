# Deployment Guide - Monitoring System Backend

## Pre-Deployment Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with valid settings
- [ ] Groq API key obtained (if using LLM features)
- [ ] Logs directory created and writable
- [ ] All tests passing

## Local Development

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings
```

### Running
```bash
# Development with auto-reload
python main.py

# Or with Uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing
```bash
# Run the test suite
python test_api.py

# The script will run through all major endpoints and scenarios
```

## Production Deployment

### Option 1: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  monitoring-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - HOST=0.0.0.0
      - PORT=8000
      - ENABLE_LLM_MONITORING=True
      - GROQ_API_KEY=${GROQ_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

Deploy with Docker:
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f monitoring-backend

# Stop
docker-compose down
```

### Option 2: Gunicorn + Uvicorn

Install Gunicorn:
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## Environment Configuration for Production

Production `.env`:
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000
ENABLE_LLM_MONITORING=True
GROQ_API_KEY=your_production_key_here
LOG_LEVEL=WARNING
LOG_FILE=/var/log/monitoring-system/monitoring.log
MAX_LOG_ENTRIES=50000
```

## Health Checks

```bash
# Verify application is running
curl http://localhost:8000/health

# Check API documentation
curl http://localhost:8000/docs

# Submit test event
curl -X POST http://localhost:8000/api/v1/monitoring/events \
  -H "Content-Type: application/json" \
  -d '{"source": "test", "event_type": "test", "data": {}}'
```

## Troubleshooting

**Port already in use**: Change PORT in .env
**Memory issues**: Reduce MAX_LOG_ENTRIES in .env
**LLM not working**: Verify GROQ_API_KEY is set correctly
**Permission denied on logs**: Run `chmod 755 logs/`

---

For complete deployment guide including Docker, Nginx, monitoring, and security hardening, see the full DEPLOYMENT.md documentation.
