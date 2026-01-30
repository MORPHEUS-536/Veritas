# Monitoring System Backend

A comprehensive FastAPI-based monitoring system for detecting failures, anomalies, and managing system health. Features both rule-based logic and optional LLM-assisted intelligent monitoring using the Groq API.

## 🚀 Features

### Core Monitoring
- **Continuous Event Monitoring**: Submit and analyze data/events in real-time
- **Rule-Based Detection**: 
  - Threshold violations (response time, CPU, memory, error rates)
  - Invalid or null output detection
  - Consistency checks across data fields
  - Silent failure detection
  - Anomaly detection using historical trend analysis
- **System Health Classification**: NORMAL, WARNING, or CRITICAL
- **Detailed Monitoring Logs**: Timestamp, source, input snapshot, status, reasoning, and suggestions

### LLM-Assisted Intelligence (Optional)
- **Groq API Integration**: Optional LLM-based analysis using Groq API
- **Human-Readable Insights**: Explains anomalies in simple language
- **Smart Severity Classification**: Augments rule-based logic
- **Actionable Recommendations**: Suggests corrective actions
- **Configurable**: Enable/disable via `ENABLE_LLM_MONITORING` flag

### System Management
- **Re-evaluation Mechanism**: Manual or automatic triggering
- **Fail-Safe Decision Logic**: 
  - CONTINUE (normal operation)
  - RETRY (retry operation)
  - REPROCESS (reprocess data)
  - ESCALATE (escalate to humans)
  - HALT (stop system)
- **Log Management**: Query, filter, and archive monitoring logs
- **Maintenance Tools**: Cleanup old logs, statistics, re-evaluation

## 📋 Prerequisites

- Python 3.9+
- pip or conda

## 🔧 Setup

### 1. Clone and Navigate
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# FastAPI Configuration
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Monitoring Configuration
ENABLE_LLM_MONITORING=True
WARNING_THRESHOLD=0.7
CRITICAL_THRESHOLD=0.9

# Groq API Configuration (Required if ENABLE_LLM_MONITORING=True)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
GROQ_MAX_TOKENS=1024

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/monitoring.log

# Data Retention
MAX_LOG_ENTRIES=10000
```

### 5. Run the Application
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at: `http://localhost:8000`

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Base URL
```
http://localhost:8000/api/v1/monitoring
```

### Key Endpoints

#### Submit Event for Monitoring
```bash
POST /api/v1/monitoring/events

{
  "source": "api_module",
  "event_type": "api_response",
  "data": {
    "response_time": 250,
    "status_code": 200,
    "output": "success"
  },
  "metadata": {
    "user_id": "123"
  }
}
```

#### Get System Health Status
```bash
GET /api/v1/monitoring/health
```

Response:
```json
{
  "current_status": "WARNING",
  "severity_score": 0.75,
  "last_update": "2025-01-30T10:30:00Z",
  "recent_issues": ["Response time exceeds threshold"],
  "total_events_processed": 150
}
```

#### Query Monitoring Logs
```bash
GET /api/v1/monitoring/logs?limit=50&status=WARNING&source=api_module
```

Or with POST for advanced filters:
```bash
POST /api/v1/monitoring/logs/query

{
  "limit": 50,
  "offset": 0,
  "status": "WARNING",
  "source": "api_module",
  "start_time": "2025-01-30T10:00:00Z"
}
```

#### Trigger LLM Analysis
```bash
POST /api/v1/monitoring/analysis/llm

{
  "lookback_minutes": 30,
  "focus_areas": ["response_times", "error_rates"]
}
```

Response:
```json
{
  "analysis": "System health shows mixed indicators...",
  "severity": "WARNING",
  "key_findings": [
    "Response times trending upward",
    "CPU usage exceeding threshold",
    "Error rate increased by 15%"
  ],
  "recommendations": [
    "Investigate resource utilization",
    "Review recent code deployments",
    "Implement circuit breaker patterns"
  ],
  "confidence": 0.82
}
```

#### Get Statistics
```bash
GET /api/v1/monitoring/stats
```

#### Re-evaluate Recent Logs
```bash
POST /api/v1/monitoring/analysis/re-evaluate?lookback_minutes=60
```

#### Cleanup Old Logs
```bash
POST /api/v1/monitoring/maintenance/cleanup?older_than_hours=48
```

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # FastAPI endpoints
│   ├── monitoring/
│   │   ├── __init__.py
│   │   └── engine.py           # Rule-based monitoring logic
│   ├── services/
│   │   ├── __init__.py
│   │   └── groq_service.py     # Groq LLM integration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic schemas
│   ├── utils/
│   │   ├── __init__.py
│   │   └── database.py         # In-memory database
│   ├── __init__.py
│   └── config.py               # Configuration management
├── logs/                        # Log files directory
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment file
└── README.md                    # This file
```

## 📊 Monitoring Rules

### Threshold Violations
Monitors common metrics:
- `response_time` > 5000ms
- `cpu_usage` > 90%
- `memory_usage` > 85%
- `error_rate` > 10%
- `latency` > 3000ms

### Consistency Checks
Validates logical consistency:
- Status 200 with error response → Inconsistent
- Status 500+ with success response → Inconsistent

### Silent Failure Detection
Detects failures that appear successful:
- Success status but null result
- Processed=True but no output
- Completed=True but items_processed=0

### Anomaly Detection
Uses statistical analysis:
- Z-score > 3 indicates outlier
- Historical trend comparison
- Pattern deviation detection

## 🤖 LLM Integration

### Getting a Groq API Key
1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Create an API key
4. Add to `.env`: `GROQ_API_KEY=your_key_here`

### LLM Features
- Analyzes recent monitoring logs
- Explains patterns and anomalies
- Provides severity classification
- Suggests corrective actions
- Provides confidence scores

### Disabling LLM
Set in `.env`:
```env
ENABLE_LLM_MONITORING=False
```

## 🔐 Security Considerations

- **API Key Management**: Use environment variables, never commit to git
- **CORS**: Currently set to allow all origins (restrict in production)
- **Error Messages**: Debug mode disabled in production
- **Logging**: Sensitive data should be masked in logs
- **Database**: In-memory storage (implement persistent storage for production)

## 🚦 Health Status Interpretation

### NORMAL (Severity 0.0 - 0.7)
- All metrics within acceptable ranges
- No detected anomalies
- System operating as expected

### WARNING (Severity 0.7 - 0.9)
- Some metrics approaching thresholds
- Minor anomalies detected
- System requires monitoring
- No immediate action needed

### CRITICAL (Severity 0.9 - 1.0)
- Multiple threshold violations
- Significant anomalies detected
- System may be unstable
- Immediate investigation required

## 📝 Example Workflows

### 1. Monitor API Responses
```python
# Submit event
POST /events
{
  "source": "api_service",
  "event_type": "response",
  "data": {
    "response_time": 2500,
    "status_code": 200,
    "items_returned": 50
  }
}

# Check health
GET /health

# Get detailed logs
GET /logs?source=api_service
```

### 2. Investigate Issues
```python
# Get warning/critical logs
GET /logs?status=WARNING&status=CRITICAL

# Trigger LLM analysis
POST /analysis/llm
{
  "lookback_minutes": 30,
  "focus_areas": ["response_times"]
}

# Re-evaluate recent period
POST /analysis/re-evaluate?lookback_minutes=60
```

### 3. Maintenance
```python
# Get statistics
GET /stats

# Cleanup old logs
POST /maintenance/cleanup?older_than_hours=48
```

## 🧪 Testing

Example test with curl:
```bash
# Submit test event
curl -X POST http://localhost:8000/api/v1/monitoring/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test_module",
    "event_type": "test_event",
    "data": {
      "response_time": 250,
      "status_code": 200
    }
  }'

# Check health
curl http://localhost:8000/api/v1/monitoring/health

# Get logs
curl http://localhost:8000/api/v1/monitoring/logs?limit=10
```

## 🔮 Future Enhancements

- Persistent storage (PostgreSQL, MongoDB)
- Advanced alerting system
- Webhooks for critical events
- Custom rule builder UI
- Performance metrics dashboard
- Multi-tenant support
- Rate limiting and throttling
- Advanced authentication/authorization

## 📄 License

Built for hackathon. Free to use and modify.

## 🙋 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review logs in `logs/monitoring.log`
3. Check `.env` configuration
4. Verify Groq API key if using LLM features

---

**Built with ❤️ for the hackathon**
