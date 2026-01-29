# Veritas Backend: Deployment & Setup Guide

## Quick Start (Development)

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Virtual environment tool (venv/conda)

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb veritas_db
createuser veritas_admin -P  # Set password when prompted

# Grant permissions
psql -U postgres -d veritas_db -c \
  "GRANT ALL PRIVILEGES ON DATABASE veritas_db TO veritas_admin;"

# Verify connection
psql -U veritas_admin -d veritas_db -c "SELECT version();"
```

### 2. Python Environment

```bash
cd Veritas/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements_db.txt
```

### 3. Environment Configuration

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://veritas_admin:your_password@localhost:5432/veritas_db

# Security
JWT_SECRET=your-256-bit-secret-key-min-32-chars-change-in-production
BCRYPT_ROUNDS=12

# App
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### 4. Initialize Database

```bash
# Run Python script to create tables
python -c "from database import init_db; init_db(); print('✓ Database initialized')"
```

### 5. Run Backend

```bash
# Development (with auto-reload)
uvicorn api_routes:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn api_routes:app --host 0.0.0.0 --port 8000 --workers 4
```

Check API: http://localhost:8000/docs

---

## Database Schema Application

### Option 1: Using Python (Recommended)

```python
from database import init_db, Base
from orm_models import *  # Import all models

# Create all tables
init_db()
```

### Option 2: Using SQL Script Directly

```bash
# Apply schema.sql directly
psql -U veritas_admin -d veritas_db -f backend/SCHEMA.sql
```

### Verify Schema

```bash
# Connect to database
psql -U veritas_admin -d veritas_db

# List tables
\dt

# Check users table structure
\d users

# Verify indexes
\di
```

---

## Production Deployment

### Prerequisites
- PostgreSQL 13+ (managed service recommended: AWS RDS, Google Cloud SQL, Azure)
- Redis 6+ (for token blacklist, session cache)
- Container runtime (Docker recommended)
- Orchestration (Kubernetes for scale)

### 1. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_db.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_db.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "api_routes:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose (Dev/Staging)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: veritas_db
    environment:
      POSTGRES_USER: veritas_admin
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: veritas_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./SCHEMA.sql:/docker-entrypoint-initdb.d/01-schema.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U veritas_admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: veritas_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: .
    container_name: veritas_backend
    environment:
      DATABASE_URL: postgresql://veritas_admin:dev_password@postgres:5432/veritas_db
      JWT_SECRET: dev-secret-key-min-32-characters-long-replace-in-prod
      BCRYPT_ROUNDS: 12
      DEBUG: "True"
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./:/app
    command: uvicorn api_routes:app --reload --host 0.0.0.0

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

### 3. Environment Variables (Production)

Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.):

```env
# Database (managed service)
DATABASE_URL=postgresql://admin:STRONG_PASSWORD@veritas-db.c.us-east-1.rds.amazonaws.com:5432/veritas_db

# Security
JWT_SECRET=<generate-with-secrets-manager>
BCRYPT_ROUNDS=12

# App
DEBUG=False
LOG_LEVEL=WARNING
ENVIRONMENT=production
ALLOWED_ORIGINS=https://veritas.example.com,https://teacher.veritas.example.com

# Monitoring
SENTRY_DSN=https://<key>@sentry.io/<project>
DATADOG_API_KEY=<datadog-api-key>

# Redis
REDIS_URL=redis://<password>@veritas-redis.cache.amazonaws.com:6379/0

# CORS
CORS_ORIGINS=["https://veritas.example.com"]
```

### 4. PostgreSQL Optimization (Production)

```sql
-- Connection pooling (via pgBouncer, not in DB)
-- Application side: pool_size=10, max_overflow=20

-- Autovacuum tuning for high-volume tables
ALTER TABLE monitoring_events SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_analyze_scale_factor = 0.005,
    autovacuum_vacuum_cost_delay = 10
);

-- Enable slow query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1s
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

SELECT pg_reload_conf();
```

### 5. Nginx Reverse Proxy

```nginx
upstream veritas_backend {
    server backend:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 443 ssl http2;
    server_name api.veritas.example.com;

    ssl_certificate /etc/letsencrypt/live/api.veritas.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.veritas.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://veritas_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /health {
        access_log off;
        proxy_pass http://veritas_backend;
    }
}

server {
    listen 80;
    server_name api.veritas.example.com;
    return 301 https://$server_name$request_uri;
}
```

### 6. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: veritas-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: veritas-backend
  template:
    metadata:
      labels:
        app: veritas-backend
    spec:
      containers:
      - name: backend
        image: veritas:backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: veritas-secrets
              key: database-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: veritas-secrets
              key: jwt-secret
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: veritas-secrets
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

---

## Testing

### Unit Tests

```bash
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v --cov=.
```

### Sample Test

```python
# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from api_routes import app
from database import SessionLocal

client = TestClient(app)

def test_register_student():
    response = client.post("/auth/register", json={
        "email": "student@test.com",
        "username": "student1",
        "password": "secure_password",
        "first_name": "John",
        "last_name": "Doe",
        "role": "student"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "student@test.com"

def test_login():
    # First register
    client.post("/auth/register", json={
        "email": "login_test@test.com",
        "username": "logintest",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "role": "student"
    })
    
    # Then login
    response = client.post("/auth/login", json={
        "email": "login_test@test.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

---

## Monitoring & Observability

### Application Metrics (with Prometheus)

```python
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('veritas_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('veritas_request_duration_seconds', 'Request duration')
db_pool_size = Gauge('veritas_db_pool_size', 'Database connection pool size')

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    with request_duration.time():
        return await call_next(request)
```

### Logging Configuration

```python
import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(filename)s:%(lineno)d: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": "veritas.log",
            "maxBytes": 10485760,
            "backupCount": 10
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Database Performance Monitoring

```sql
-- Slow query log
SELECT 
    query,
    calls,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%exam%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Backup & Disaster Recovery

### PostgreSQL Backup

```bash
# Full backup
pg_dump -U veritas_admin -h localhost veritas_db > veritas_db_backup.sql

# Compressed backup
pg_dump -U veritas_admin -h localhost -F c veritas_db > veritas_db_backup.dump

# Restore
psql -U veritas_admin -d veritas_db < veritas_db_backup.sql

# Restore from compressed
pg_restore -U veritas_admin -d veritas_db veritas_db_backup.dump
```

### Automated Backups

```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backups/veritas"
DB_NAME="veritas_db"
DB_USER="veritas_admin"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/veritas_$DATE.sql.gz

# Keep last 30 days
find $BACKUP_DIR -name "veritas_*.sql.gz" -mtime +30 -delete

# Upload to S3
aws s3 cp $BACKUP_DIR/veritas_$DATE.sql.gz s3://veritas-backups/

echo "Backup completed: veritas_$DATE.sql.gz"
```

Add to crontab:
```
0 2 * * * /scripts/backup.sh  # 2 AM daily
```

---

## Troubleshooting

### Issue: "Connection refused" to database

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
psql -U veritas_admin -d veritas_db -c "SELECT 1"

# Check firewall (if remote)
psql -U veritas_admin -h 1.2.3.4 -d veritas_db -c "SELECT 1"
```

### Issue: Slow monitoring event ingestion

```python
# Check connection pool status
from database import engine
pool = engine.pool

print(f"Pool size: {pool.size()}")
print(f"Checkedout connections: {pool.checkedout()}")

# Solution: Increase pool size
# pool_size=20, max_overflow=40
```

### Issue: Out of memory with materialized views

```sql
-- Drop and recreate without CONCURRENT
DROP MATERIALIZED VIEW exam_performance_summary;

-- Reduce frequency of refresh
-- Or partition to smaller views
```

---

## Checklist for Go-Live

- [ ] Database: PostgreSQL 13+ configured with backups
- [ ] Secrets: All environment variables in secure vault
- [ ] SSL/TLS: HTTPS configured, certificates valid
- [ ] Rate limiting: Implement to prevent abuse
- [ ] CORS: Configured for frontend domains only
- [ ] Monitoring: Prometheus, Sentry, or similar active
- [ ] Logging: Centralized logging configured
- [ ] Load testing: Min 100 concurrent users tested
- [ ] Security scan: Dependency check, SQL injection tests
- [ ] Disaster recovery: Backup/restore tested
- [ ] Documentation: API docs, runbooks updated
- [ ] On-call: Support contacts defined

---

## Support

For issues or questions:
- Check logs: `tail -f veritas.log`
- Database logs: `tail -f /var/log/postgresql/postgresql.log`
- API docs: http://localhost:8000/docs
