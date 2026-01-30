# Quick Reference Card - Monitoring System

## 🚀 Get Started in 3 Commands

```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

Then visit: **http://localhost:8000/docs**

## 📚 Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point |
| `app/config.py` | Configuration management |
| `app/monitoring/engine.py` | Rule-based detection logic |
| `app/services/groq_service.py` | LLM integration |
| `app/api/routes.py` | API endpoints |
| `app/utils/database.py` | Log storage |
| `test_api.py` | Test suite |
| `.env.example` | Environment template |

## 🔗 API Quick Reference

### Submit Event
```bash
curl -X POST http://localhost:8000/api/v1/monitoring/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "api_service",
    "event_type": "response",
    "data": {"response_time": 250, "status_code": 200}
  }'
```

### Check Health
```bash
curl http://localhost:8000/api/v1/monitoring/health
```

### Get Logs
```bash
curl http://localhost:8000/api/v1/monitoring/logs?limit=10
```

### Analyze with LLM
```bash
curl -X POST http://localhost:8000/api/v1/monitoring/analysis/llm \
  -H "Content-Type: application/json" \
  -d '{"lookback_minutes": 30}'
```

### Get Statistics
```bash
curl http://localhost:8000/api/v1/monitoring/stats
```

## 📊 Core Concepts

### Health Status
- **NORMAL** (0.0-0.7): Operating normally
- **WARNING** (0.7-0.9): Requires monitoring
- **CRITICAL** (0.9-1.0): Immediate action needed

### Detection Rules
1. **Threshold Violations**: response_time, cpu_usage, memory_usage, error_rate, latency
2. **Invalid Output**: null values, error strings, empty structures
3. **Consistency Checks**: Status code vs response logic
4. **Silent Failure**: Success but null/no output
5. **Anomalies**: Z-score > 3 (statistical outliers)

### Fail-Safe Actions
- **CONTINUE**: Normal operation
- **RETRY**: Attempt again
- **REPROCESS**: Reprocess data
- **ESCALATE**: Alert operators
- **HALT**: Stop system

## 🔧 Configuration

### Key Environment Variables
```env
ENABLE_LLM_MONITORING=True          # Toggle LLM features
GROQ_API_KEY=your_key_here          # Required for LLM
WARNING_THRESHOLD=0.7               # Severity threshold
CRITICAL_THRESHOLD=0.9              # Critical threshold
MAX_LOG_ENTRIES=10000               # Log retention
LOG_FILE=logs/monitoring.log        # Log location
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/routes.py              (API endpoints)
│   ├── monitoring/engine.py        (Core logic)
│   ├── services/groq_service.py    (LLM service)
│   ├── models/schemas.py           (Data models)
│   ├── utils/database.py           (Storage)
│   └── config.py                   (Configuration)
├── main.py                         (Entry point)
├── test_api.py                     (Tests)
├── requirements.txt                (Dependencies)
└── README.md                       (Full docs)
```

## 🎯 Common Workflows

### Monitor API Service
```bash
# 1. Submit response
curl -X POST http://localhost:8000/api/v1/monitoring/events \
  -d '{...event_data...}'

# 2. Check health
curl http://localhost:8000/api/v1/monitoring/health

# 3. View logs
curl http://localhost:8000/api/v1/monitoring/logs?source=api_service
```

### Detect Anomalies
```bash
# Submit events → System learns patterns → Analyze
curl -X POST http://localhost:8000/api/v1/monitoring/analysis/llm \
  -d '{"lookback_minutes": 30, "focus_areas": ["response_times"]}'
```

### Investigate Issues
```bash
# Get warnings/critical logs
curl "http://localhost:8000/api/v1/monitoring/logs?status=WARNING"

# Get LLM insights
curl -X POST http://localhost:8000/api/v1/monitoring/analysis/llm \
  -d '{"lookback_minutes": 60}'
```

## 🧪 Testing

```bash
# Run complete test suite
python test_api.py

# Tests all major endpoints and scenarios
# Validates normal, warning, and critical events
# Checks log querying, health status, LLM analysis
```

## 📖 Documentation Files

| Document | Purpose |
|----------|---------|
| README.md | Complete feature documentation |
| QUICKSTART.md | 5-minute setup guide |
| ARCHITECTURE.md | System design & technical details |
| DEPLOYMENT.md | Production deployment guide |
| PROJECT_MANIFEST.md | File structure & statistics |

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change PORT in .env |
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| LLM not working | Set GROQ_API_KEY in .env |
| No logs found | Submit events first: `python test_api.py` |

## 📊 Endpoints at a Glance

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/v1/monitoring/events | Submit event |
| GET | /api/v1/monitoring/health | Current status |
| GET | /api/v1/monitoring/logs | Get logs |
| POST | /api/v1/monitoring/logs/query | Advanced query |
| POST | /api/v1/monitoring/analysis/llm | LLM analysis |
| POST | /api/v1/monitoring/analysis/re-evaluate | Re-evaluate |
| GET | /api/v1/monitoring/stats | Statistics |
| POST | /api/v1/monitoring/maintenance/cleanup | Cleanup |

## 🎓 Key Classes

- **MonitoringEngine**: Core rule-based detection
- **GroqLLMService**: LLM integration
- **MonitoringDatabase**: Log storage & querying
- **MonitoringLog**: Complete log entry
- **HealthStatusResponse**: Health status API response

## ⚙️ Performance Tips

- Reduce `MAX_LOG_ENTRIES` if memory constrained
- Use persistent database for production
- Run on multiple workers with Gunicorn
- Enable caching for frequently queried logs
- Archive old logs to external storage

## 🔒 Security

- Never commit `.env` file
- Use environment variables for API keys
- Restrict CORS to known domains in production
- Implement authentication for API access
- Log all access attempts
- Sanitize error messages

## 🚀 Deployment Quick Start

### Docker
```bash
docker-compose up -d
```

### Gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Systemd
```bash
sudo systemctl start monitoring-system
```

## 📞 Support

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Logs**: Check `logs/monitoring.log`
- **Test**: Run `python test_api.py`

---

**Version**: 1.0.0 | **Status**: Production Ready | **Last Updated**: 2025-01-30
