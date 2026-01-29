# Monitoring Module - Hackathon Application

A robust, production-ready **Monitoring Module** for the hackathon application backend. Continuously monitors incoming data/events, detects anomalies, threshold violations, and suspicious patterns. Integrates LLM (OpenAI/Claude/Gemini) for intelligent analysis.

## 🎯 Features

### Core Monitoring
- ✅ **Continuous Data Monitoring** - Processes incoming events from all modules
- ✅ **Rule-Based Anomaly Detection** - Detects thresholds, invalid patterns, latency issues
- ✅ **Status Classification** - Classifies as Normal / Warning / Critical
- ✅ **Comprehensive Logging** - Maintains timestamped logs with full context
- ✅ **Pattern Analysis** - Detects statistical outliers and trend changes

### LLM Integration
- ✅ **Intelligent Analysis** - Uses LLM to classify system state and explain issues
- ✅ **Multi-Provider Support** - Works with OpenAI, Claude (Anthropic), or Google Gemini
- ✅ **Actionable Suggestions** - LLM recommends corrective actions
- ✅ **Optional & Safe** - Can be disabled via config; fails gracefully if API key missing

### REST API
- ✅ **4 Core Endpoints** - Submit data, get status, retrieve logs, trigger analysis
- ✅ **Comprehensive Documentation** - Full OpenAPI/Swagger docs at `/docs`
- ✅ **Error Handling** - Robust error responses with clear messages
- ✅ **Async/Await** - Uses FastAPI for high performance

### Developer Experience
- ✅ **Clean Code Structure** - Well-organized with separation of concerns
- ✅ **Inline Documentation** - Every function has clear docstrings and comments
- ✅ **Type Hints** - Full type annotations for better IDE support
- ✅ **Environment Config** - All settings via `.env` file
- ✅ **Logging** - Structured logging to file and console

---

## 📋 Architecture

```
monitoring_module/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration from environment
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models for request/response
│   ├── services/
│   │   ├── __init__.py
│   │   ├── monitoring_service.py    # Core monitoring logic
│   │   └── llm_service.py           # LLM integration service
│   ├── routers/
│   │   ├── __init__.py
│   │   └── monitoring.py       # API endpoints/routes
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # Logging configuration
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── API_EXAMPLES.md            # Complete API documentation
└── README.md                   # This file
```

### Key Design Decisions

1. **Stateful In-Memory Storage** - For hackathon speed; easily replaceable with database
2. **Async/FastAPI** - Better performance and non-blocking I/O
3. **Service Layer Pattern** - Clean separation between API and business logic
4. **Optional LLM** - Rule-based monitoring works standalone; LLM is enhancement
5. **Deque with MaxLen** - Efficient memory management for log storage

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Clone/Setup the workspace:**
   ```bash
   cd c:\Monitoring
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Using venv
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment configuration:**
   ```bash
   # Copy the example env file
   copy .env.example .env
   
   # Edit .env with your settings (see Configuration section below)
   ```

5. **Create logs directory:**
   ```bash
   mkdir logs
   ```

6. **Run the application:**
   ```bash
   # Using Python directly
   python -m app.main
   
   # Or using uvicorn
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the service:**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG_MODE=false

# Monitoring Configuration
MAX_LOGS_STORED=1000
MONITORING_CHECK_INTERVAL=60
ANOMALY_THRESHOLD_WARNING=0.7
ANOMALY_THRESHOLD_CRITICAL=0.9

# LLM Configuration (Optional)
ENABLE_LLM_MONITORING=false
LLM_PROVIDER=openai  # or claude, gemini
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-3.5-turbo
LLM_MAX_TOKENS=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/monitoring.log
```

### Getting LLM API Keys

**OpenAI:**
- Visit https://platform.openai.com/api-keys
- Create new secret key
- Add to `.env`: `LLM_API_KEY=sk-...`

**Claude (Anthropic):**
- Visit https://console.anthropic.com/
- Create API key in account settings
- Add to `.env`: `LLM_API_KEY=sk-ant-...`

**Google Gemini:**
- Visit https://ai.google.dev/
- Click "Get API key"
- Add to `.env`: `LLM_API_KEY=AIza...`

---

## 📡 API Reference

### 1. Submit Data for Monitoring

**POST** `/monitor/data`

Submit data/events to be monitored.

```bash
curl -X POST http://localhost:8000/monitor/data \
  -H "Content-Type: application/json" \
  -d '{
    "source_module": "inference",
    "event_type": "prediction_result",
    "data": {
      "prediction_score": 0.95,
      "latency_ms": 250
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Data monitored successfully",
  "log_id": "log_20260129_103000_a1b2c3d4",
  "detected_status": "normal",
  "reason": "All metrics within acceptable range"
}
```

---

### 2. Get System Health Status

**GET** `/monitor/status`

Get current system health and metrics.

```bash
curl http://localhost:8000/monitor/status
```

**Response:**
```json
{
  "current_status": "normal",
  "total_logs_processed": 512,
  "warning_count": 3,
  "critical_count": 0,
  "last_update": "2026-01-29T10:35:00Z",
  "uptime_seconds": 3600.5,
  "last_critical_event": null
}
```

---

### 3. Get Monitoring Logs

**GET** `/monitor/logs`

Retrieve recent logs with optional filtering.

```bash
# Get recent logs
curl http://localhost:8000/monitor/logs?limit=10

# Filter by status
curl http://localhost:8000/monitor/logs?status=warning

# Filter by source module
curl http://localhost:8000/monitor/logs?source=inference
```

**Response:**
```json
{
  "total_count": 512,
  "returned_count": 10,
  "logs": [
    {
      "log_id": "log_20260129_101500_a1b2c3d4",
      "timestamp": "2026-01-29T10:15:00Z",
      "source_module": "inference",
      "event_type": "prediction_result",
      "input_data_snapshot": { "prediction_score": 0.95 },
      "detected_status": "normal",
      "reason": "All metrics within acceptable range",
      "llm_analysis": null,
      "llm_suggestions": null
    }
  ]
}
```

---

### 4. Trigger LLM Analysis

**POST** `/monitor/analyze`

Manually trigger intelligent LLM analysis on recent logs.

```bash
curl -X POST http://localhost:8000/monitor/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "num_recent_logs": 20,
    "focus_area": "latency"
  }'
```

**Response:**
```json
{
  "system_state": "warning",
  "analysis": "System experiencing elevated latency. Recent logs show database query times above normal thresholds...",
  "suggestions": [
    "Investigate database performance",
    "Check system resource utilization",
    "Review active database connections"
  ],
  "confidence": 0.87,
  "analysis_timestamp": "2026-01-29T10:35:00Z"
}
```

---

### 5. Health Check

**GET** `/monitor/health`

Simple health check endpoint.

```bash
curl http://localhost:8000/monitor/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "monitoring",
  "timestamp": "2026-01-29T10:35:00Z",
  "llm_enabled": true
}
```

---

## 🧠 Monitoring Logic

### Rule-Based Detection

The monitoring service applies the following rules (in order):

1. **Null/Empty Data Check** → CRITICAL if empty
2. **Latency Check**
   - `> 5000ms` → CRITICAL
   - `> 2000ms` → WARNING
3. **Prediction Score Check**
   - Invalid (not 0-1) → CRITICAL
   - `< 0.9` (CRITICAL threshold) → CRITICAL
   - `< 0.7` (WARNING threshold) → WARNING
4. **Pattern Anomaly Detection** → WARNING if outlier (z-score > 3)
5. **Data Consistency Checks** → WARNING/CRITICAL for invalid values
6. **Error Rate Check**
   - `> 10%` → CRITICAL
   - `> 5%` → WARNING

### Status Update Logic

- CRITICAL events override all other statuses
- System downgrades from WARNING to NORMAL after 5 consecutive normal events
- Last critical event is always tracked

### LLM Analysis

When enabled, the LLM:
1. Receives formatted log summary with recent patterns
2. Classifies overall system state
3. Provides human-readable explanation
4. Suggests 3-5 actionable recommendations
5. Provides confidence score (0-1)

---

## 🔧 Development & Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Testing Endpoints with curl

See [API_EXAMPLES.md](API_EXAMPLES.md) for comprehensive examples.

Quick test script:
```bash
# Test 1: Submit normal data
curl -X POST http://localhost:8000/monitor/data \
  -H "Content-Type: application/json" \
  -d '{"source_module":"test","event_type":"test","data":{"prediction_score":0.95}}'

# Test 2: Check status
curl http://localhost:8000/monitor/status

# Test 3: Get logs
curl http://localhost:8000/monitor/logs?limit=5
```

### Logging

Logs are written to both console and file:
- **Console:** INFO and above
- **File:** `logs/monitoring.log` - DEBUG and above

Change log level in `.env`:
```env
LOG_LEVEL=DEBUG  # or INFO, WARNING, ERROR
```

---

## 🔌 Integration with Other Modules

### From Inference Module

```python
import requests

MONITOR_URL = "http://localhost:8000"

def inference_pipeline(data):
    # Your inference logic
    prediction = run_model(data)
    confidence = get_confidence(prediction)
    latency_ms = measure_latency()
    
    # Send to monitoring
    monitoring_response = requests.post(
        f"{MONITOR_URL}/monitor/data",
        json={
            "source_module": "inference",
            "event_type": "prediction_result",
            "data": {
                "prediction": prediction,
                "confidence": confidence,
                "latency_ms": latency_ms
            }
        }
    )
    
    # Check for critical issues
    if monitoring_response.json()["detected_status"] == "critical":
        # Handle critical alert
        trigger_fallback_mechanism()
    
    return prediction
```

### From Preprocessing Module

```python
def data_preprocessing(raw_data):
    processed_data = preprocess(raw_data)
    error_rate = calculate_error_rate()
    
    requests.post(
        f"{MONITOR_URL}/monitor/data",
        json={
            "source_module": "preprocessing",
            "event_type": "validation",
            "data": {
                "records_processed": len(processed_data),
                "error_rate": error_rate,
                "status": "success"
            }
        }
    )
    
    return processed_data
```

---

## 📊 Data Models

See [models/schemas.py](app/models/schemas.py) for complete Pydantic models:

- `MonitoringDataRequest` - Request to submit data
- `MonitoringLog` - Stored monitoring log entry
- `StatusEnum` - Status enumeration (normal/warning/critical)
- `LLMAnalysisResult` - LLM analysis output
- `SystemHealthStatus` - System health snapshot
- `MonitoringAnalysisRequest` - Request for LLM analysis

---

## 🛡️ Error Handling

### Common Errors

| Scenario | Status | Solution |
|----------|--------|----------|
| Missing required field | 400 | Check request schema in documentation |
| LLM not enabled | 503 | Set `ENABLE_LLM_MONITORING=true` and provide `LLM_API_KEY` |
| API key invalid | 503 | Verify API key is correct for your LLM provider |
| No logs available | 400 | Submit some monitoring data first |
| Internal error | 500 | Check logs at `logs/monitoring.log` |

### Graceful Degradation

- If LLM API fails → Rule-based detection still works
- If logs are full → Oldest logs are automatically discarded (FIFO)
- If environment variables missing → Service uses defaults or disables features

---

## 📈 Scalability & Production Notes

### Current Limitations
- Logs stored in memory (deque) - max 1000 by default
- Single instance (not distributed)
- No database persistence

### For Production
1. **Database Integration** - Replace deque with PostgreSQL/MongoDB
2. **Message Queue** - Use Kafka/RabbitMQ for high-volume events
3. **Caching** - Add Redis for status lookups
4. **Clustering** - Run multiple instances with load balancing
5. **Monitoring** - Instrument service with Prometheus/StatsD metrics
6. **Alerting** - Integrate with PagerDuty/Slack

### Example: PostgreSQL Integration

```python
# Replace deque with database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/monitoring"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# In monitoring_service.py
def store_log(log: MonitoringLog):
    db = SessionLocal()
    db.add(log)
    db.commit()
```

---

## 📝 Code Examples

### Python Client for Monitoring

```python
from httpx import Client
import json

class MonitoringClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = Client()
    
    def submit_data(self, source, event_type, data):
        """Submit monitoring data"""
        response = self.client.post(
            f"{self.base_url}/monitor/data",
            json={
                "source_module": source,
                "event_type": event_type,
                "data": data
            }
        )
        return response.json()
    
    def get_status(self):
        """Get system status"""
        return self.client.get(f"{self.base_url}/monitor/status").json()
    
    def get_logs(self, limit=50, status=None):
        """Get logs with optional filtering"""
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self.client.get(f"{self.base_url}/monitor/logs", params=params).json()
    
    def analyze(self, num_logs=10, focus_area=None):
        """Trigger LLM analysis"""
        data = {"num_recent_logs": num_logs}
        if focus_area:
            data["focus_area"] = focus_area
        return self.client.post(f"{self.base_url}/monitor/analyze", json=data).json()

# Usage
client = MonitoringClient()
client.submit_data("inference", "prediction", {"confidence": 0.95})
status = client.get_status()
print(status)
```

---

## 🤝 Contributing

1. Keep code clean and well-documented
2. Add type hints to all functions
3. Test new features with example requests
4. Update docstrings and comments
5. Follow the existing code structure

---

## 📄 License

Part of hackathon project - Use freely for educational purposes.

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Google Gemini Documentation](https://ai.google.dev/)

---

## ❓ FAQ

**Q: Can I use this with a database instead of in-memory storage?**
A: Yes! Replace the deque in MonitoringService with SQLAlchemy models.

**Q: Does LLM monitoring slow down the system?**
A: LLM calls are only made for WARNING/CRITICAL events, not for every request. You can also disable LLM monitoring.

**Q: What if my LLM API rate limit is exceeded?**
A: The service fails gracefully - rule-based monitoring continues working. Check logs for details.

**Q: Can I customize the detection rules?**
A: Yes! Edit `_detect_anomalies()` method in [services/monitoring_service.py](app/services/monitoring_service.py).

**Q: How do I clear old logs?**
A: Call `monitoring_service.clear_logs()` or restart the service.

---

**Happy Monitoring! 🎉**
