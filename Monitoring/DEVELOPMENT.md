# Development & Extension Guide

Guide for extending and customizing the Monitoring Module.

## Adding Custom Detection Rules

The detection logic is in `app/services/monitoring_service.py` in the `_detect_anomalies()` method.

### Example: Add a Custom Rule for Response Time

```python
# In _detect_anomalies() method

def _detect_anomalies(self, request: MonitoringDataRequest) -> Tuple[StatusEnum, str]:
    data = request.data
    source = request.source_module
    
    # ... existing rules ...
    
    # NEW RULE: Check response time degradation
    if "response_time_ms" in data:
        response_time = data["response_time_ms"]
        
        # Check if response time is too high
        if response_time > 3000:  # 3 seconds
            return StatusEnum.CRITICAL, f"Response time critical: {response_time}ms"
        elif response_time > 1500:  # 1.5 seconds
            return StatusEnum.WARNING, f"Response time elevated: {response_time}ms"
    
    return StatusEnum.NORMAL, "All checks passed"
```

### Example: Add ML Model Performance Rule

```python
def _detect_anomalies(self, request: MonitoringDataRequest) -> Tuple[StatusEnum, str]:
    data = request.data
    
    # ... existing rules ...
    
    # NEW: Check F1 score for classification models
    if "f1_score" in data:
        f1 = data["f1_score"]
        
        if f1 < 0.60:
            return StatusEnum.CRITICAL, f"Model performance critical: F1={f1:.3f}"
        elif f1 < 0.75:
            return StatusEnum.WARNING, f"Model performance degraded: F1={f1:.3f}"
    
    # Check precision and recall
    if "precision" in data and "recall" in data:
        precision = data["precision"]
        recall = data["recall"]
        
        if precision < 0.70 or recall < 0.70:
            return StatusEnum.WARNING, f"Precision: {precision:.2f}, Recall: {recall:.2f}"
    
    return StatusEnum.NORMAL, ""
```

---

## Adding New API Endpoints

Add new endpoints in `app/routers/monitoring.py`:

### Example: Get Statistics

```python
from fastapi import APIRouter
from app.services.monitoring_service import monitoring_service

@router.get(
    "/stats",
    summary="Get monitoring statistics",
    description="Returns statistical summary of monitoring data"
)
async def get_statistics():
    """
    Get statistics about the monitoring data.
    """
    logs = list(monitoring_service.logs)
    
    if not logs:
        return {"message": "No logs available"}
    
    statuses = {}
    for log in logs:
        status = log.detected_status.value
        statuses[status] = statuses.get(status, 0) + 1
    
    return {
        "total_logs": len(logs),
        "status_distribution": statuses,
        "critical_percentage": (statuses.get("critical", 0) / len(logs)) * 100 if logs else 0,
        "warning_percentage": (statuses.get("warning", 0) / len(logs)) * 100 if logs else 0
    }
```

### Example: Export Logs as CSV

```python
from fastapi.responses import StreamingResponse
import csv
import io

@router.get("/logs/export")
async def export_logs_csv():
    """Export all logs as CSV file"""
    
    logs = list(monitoring_service.logs)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "log_id", "timestamp", "source_module", "event_type",
        "detected_status", "reason"
    ])
    
    # Write data
    for log in logs:
        writer.writerow([
            log.log_id,
            log.timestamp.isoformat(),
            log.source_module,
            log.event_type,
            log.detected_status.value,
            log.reason
        ])
    
    # Convert to bytes
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=monitoring_logs.csv"}
    )
```

---

## Integrating with Database

Replace in-memory storage with PostgreSQL:

### Step 1: Install SQLAlchemy

```bash
pip install sqlalchemy psycopg2-binary
```

### Step 2: Create Database Models

```python
# app/models/database.py
from sqlalchemy import Column, String, DateTime, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.models.schemas import StatusEnum

Base = declarative_base()

class MonitoringLogDB(Base):
    __tablename__ = "monitoring_logs"
    
    log_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source_module = Column(String, index=True)
    event_type = Column(String)
    input_data_snapshot = Column(JSON)
    detected_status = Column(Enum(StatusEnum))
    reason = Column(String)
    llm_analysis = Column(String, nullable=True)
    llm_suggestions = Column(JSON, nullable=True)
```

### Step 3: Update Monitoring Service

```python
# app/services/monitoring_service.py
from sqlalchemy.orm import Session
from app.models.database import MonitoringLogDB

class MonitoringService:
    def __init__(self, db: Session):
        self.db = db
    
    async def store_log(self, log: MonitoringLog):
        """Store log in database instead of memory"""
        db_log = MonitoringLogDB(
            log_id=log.log_id,
            timestamp=log.timestamp,
            source_module=log.source_module,
            event_type=log.event_type,
            input_data_snapshot=log.input_data_snapshot,
            detected_status=log.detected_status,
            reason=log.reason,
            llm_analysis=log.llm_analysis,
            llm_suggestions=log.llm_suggestions
        )
        self.db.add(db_log)
        self.db.commit()
    
    def get_recent_logs(self, limit: int = 50):
        """Fetch from database"""
        return self.db.query(MonitoringLogDB)\
            .order_by(MonitoringLogDB.timestamp.desc())\
            .limit(limit)\
            .all()
```

---

## Adding Authentication

Protect your endpoints with API key authentication:

### Step 1: Create Auth Middleware

```python
# app/middleware/auth.py
from fastapi import HTTPException, Header
from app.config import API_KEY

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### Step 2: Add to Endpoints

```python
from app.middleware.auth import verify_api_key

@router.post("/data", dependencies=[Depends(verify_api_key)])
async def submit_monitoring_data(request: MonitoringDataRequest):
    """Only accessible with valid API key"""
    # ... endpoint logic
```

---

## Adding Webhooks for Alerts

Send alerts to external services when critical events occur:

### Step 1: Create Webhook Service

```python
# app/services/webhook_service.py
import httpx
from app.models.schemas import MonitoringLog
from app.config import WEBHOOK_URL

class WebhookService:
    def __init__(self):
        self.webhook_url = WEBHOOK_URL
    
    async def notify_critical_event(self, log: MonitoringLog):
        """Send webhook notification for critical events"""
        if not self.webhook_url:
            return
        
        async with httpx.AsyncClient() as client:
            await client.post(
                self.webhook_url,
                json={
                    "event_type": "critical_alert",
                    "log_id": log.log_id,
                    "source": log.source_module,
                    "reason": log.reason,
                    "timestamp": log.timestamp.isoformat()
                }
            )
```

### Step 2: Call in Monitoring Service

```python
# In _update_system_status()
if detected_status == StatusEnum.CRITICAL:
    await webhook_service.notify_critical_event(log)
```

### Step 3: Configure in .env

```env
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

---

## Adding Prometheus Metrics

Export metrics for monitoring the monitoring service:

### Step 1: Install Prometheus Client

```bash
pip install prometheus-client
```

### Step 2: Create Metrics

```python
# app/utils/metrics.py
from prometheus_client import Counter, Gauge, Histogram

# Counters
data_processed_counter = Counter(
    'monitoring_data_processed_total',
    'Total data points processed',
    ['source_module', 'status']
)

# Gauges
current_status_gauge = Gauge(
    'monitoring_system_status',
    'Current system status (0=normal, 1=warning, 2=critical)'
)

# Histograms
processing_time_histogram = Histogram(
    'monitoring_processing_seconds',
    'Time taken to process monitoring data'
)
```

### Step 3: Add Metrics Endpoint

```python
# In app/main.py
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

---

## Testing Custom Rules

Create tests for your new rules:

```python
# test_custom_rules.py
import pytest
from app.services.monitoring_service import MonitoringService
from app.models.schemas import MonitoringDataRequest, StatusEnum

@pytest.mark.asyncio
async def test_response_time_critical():
    """Test response time critical threshold"""
    service = MonitoringService()
    
    request = MonitoringDataRequest(
        source_module="api",
        event_type="response",
        data={"response_time_ms": 5000}
    )
    
    status, reason = service._detect_anomalies(request)
    
    assert status == StatusEnum.CRITICAL
    assert "response time" in reason.lower()

@pytest.mark.asyncio
async def test_response_time_warning():
    """Test response time warning threshold"""
    service = MonitoringService()
    
    request = MonitoringDataRequest(
        source_module="api",
        event_type="response",
        data={"response_time_ms": 2000}
    )
    
    status, reason = service._detect_anomalies(request)
    
    assert status == StatusEnum.WARNING
```

---

## Performance Optimization

### Caching Recent Status

```python
from functools import lru_cache
from datetime import datetime, timedelta

class MonitoringService:
    def __init__(self):
        self.last_status_update = None
        self.cached_status = None
    
    def get_system_health(self, use_cache=True):
        """Get health with optional caching"""
        now = datetime.utcnow()
        
        # Use cache if recent
        if use_cache and self.cached_status and \
           (now - self.last_status_update) < timedelta(seconds=5):
            return self.cached_status
        
        # Calculate fresh status
        health = self._calculate_health()
        self.cached_status = health
        self.last_status_update = now
        return health
```

### Async Processing

```python
import asyncio

async def process_batch(self, requests: List[MonitoringDataRequest]):
    """Process multiple requests concurrently"""
    tasks = [self.process_data(req) for req in requests]
    return await asyncio.gather(*tasks)
```

---

## Monitoring Your Monitoring

Add self-monitoring to detect issues:

```python
class MonitoringService:
    async def self_check(self):
        """Check the monitoring service itself"""
        
        # Check response times
        if self.total_processed == 0:
            return "No data processed yet"
        
        # Check log storage efficiency
        log_memory = len(self.logs) * 1024  # Approximate
        
        if log_memory > 100_000_000:  # 100MB
            logger.warning("Log storage exceeding 100MB")
        
        # Check error rate
        error_rate = self.critical_count / self.total_processed
        if error_rate > 0.2:  # >20%
            logger.warning("High critical event rate")
```

---

## Production Checklist

- [ ] Enable database persistence
- [ ] Add authentication/API keys
- [ ] Set up webhooks for alerts
- [ ] Export Prometheus metrics
- [ ] Configure log rotation
- [ ] Set up alerting rules
- [ ] Test failover/recovery
- [ ] Document custom rules
- [ ] Set up monitoring for the monitor
- [ ] Load testing done
- [ ] Security review completed

---

## Getting Help

1. Check logs: `logs/monitoring.log`
2. Enable debug mode: `DEBUG_MODE=true` in .env
3. Visit docs: http://localhost:8000/docs
4. Read API_EXAMPLES.md for request/response examples
5. Check test_api.py for usage patterns

Happy extending! 🚀
