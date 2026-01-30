# Quick Start Guide - Monitoring System Backend

## 🚀 Get Started in 5 Minutes

### Step 1: Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure
```bash
# Copy example environment file
cp .env.example .env

# Optional: Configure .env (adjust settings as needed)
# For hackathon: defaults work fine
```

### Step 3: Run
```bash
# Start the server
python main.py
```

You'll see:
```
============================================================
  Starting Monitoring System Backend v1.0.0
============================================================

Logging configured at level INFO
Configuration validated successfully
Database initialized
LLM Monitoring: ENABLED
...
Application running on 0.0.0.0:8000
```

### Step 4: Access
Open your browser:
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📝 Quick Examples

### Submit Event (using curl)
```bash
curl -X POST http://localhost:8000/api/v1/monitoring/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "my_service",
    "event_type": "response",
    "data": {
      "response_time": 250,
      "status_code": 200,
      "output": "success"
    }
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

### Run Tests
```bash
# In another terminal (with venv activated)
python test_api.py
```

## 🔑 Using LLM Features

1. Get Groq API Key from https://console.groq.com
2. Add to `.env`:
   ```
   GROQ_API_KEY=your_key_here
   ```
3. Restart the server
4. LLM analysis is now available at:
   ```
   POST /api/v1/monitoring/analysis/llm
   ```

## 📚 Key Features

✅ Real-time event monitoring
✅ Rule-based anomaly detection
✅ LLM-assisted intelligent analysis
✅ REST API with full documentation
✅ Detailed monitoring logs
✅ System health classification
✅ Advanced log querying

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change PORT in .env
PORT=8001
python main.py
```

### Module Not Found Errors
```bash
# Make sure virtual environment is activated
# And requirements are installed
pip install -r requirements.txt
```

### LLM Analysis Not Working
```bash
# Check .env file:
# 1. ENABLE_LLM_MONITORING=True
# 2. GROQ_API_KEY is set correctly
# 3. Restart the server
```

### No Logs in Database
```bash
# Submit some events first:
# Use curl examples above or test_api.py
python test_api.py
```

## 📖 Documentation

- **Full README**: See `README.md`
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Test Script**: Run `python test_api.py`

## 🎯 Next Steps

1. **Explore APIs**: Visit http://localhost:8000/docs
2. **Submit Events**: Use examples above or test_api.py
3. **Query Logs**: Try different filters on `/logs` endpoint
4. **Analyze Data**: Trigger LLM analysis on `/analysis/llm`
5. **Check Health**: Monitor system status on `/health`

## 💡 Tips for Hackathon

- **Start Simple**: Focus on rule-based monitoring first
- **Test Thoroughly**: Use test_api.py to verify functionality
- **Show Features**: LLM analysis is impressive for judges
- **Document Code**: Comments and docstrings are your friends
- **Handle Errors**: Graceful error handling impresses

## 🚨 Common Workflows

### Monitor an API Service
```python
# 1. Submit response data
POST /events with response_time, status_code, etc.

# 2. Check health
GET /health

# 3. View logs
GET /logs?source=api_service
```

### Detect Anomalies
```python
# 1. Submit events from different sources
# 2. Let system learn patterns
# 3. Request LLM analysis
POST /analysis/llm

# 4. Review key_findings and recommendations
```

### Investigate Issues
```python
# 1. Get health status
GET /health

# 2. Query warning/critical logs
GET /logs?status=WARNING

# 3. Run LLM analysis for insights
POST /analysis/llm

# 4. Get recommendations
```

---

**Need help?** Check the full README.md or look at test_api.py for examples!
