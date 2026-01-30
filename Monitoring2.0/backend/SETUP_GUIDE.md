# Complete Setup & Run Guide - Monitoring System 2.0

## 📋 STEP-BY-STEP SETUP

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Get Groq API Key

1. Visit: **https://console.groq.com**
2. Sign up or log in
3. Create an API key (copy it)
4. Keep it safe for the next step

### Step 3: Configure .env File

Open the `.env` file in the `backend` folder and find this line:

```
GROQ_API_KEY=your_groq_api_key_here
```

Replace `your_groq_api_key_here` with your actual API key. For example:

```
GROQ_API_KEY=gsk_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Your .env file should look like:**
```env
DEBUG=False
HOST=0.0.0.0
PORT=8000

ENABLE_LLM_MONITORING=True
WARNING_THRESHOLD=0.7
CRITICAL_THRESHOLD=0.9

GROQ_API_KEY=gsk_xxxxxxxxxxxxx      ← YOUR KEY HERE
GROQ_MODEL=mixtral-8x7b-32768
GROQ_MAX_TOKENS=1024

LOG_LEVEL=INFO
LOG_FILE=logs/monitoring.log

MAX_LOG_ENTRIES=10000
```

### Step 4: Start the Server

In terminal 1 (from backend folder):
```bash
python main.py
```

You should see:
```
============================================================
  Starting Monitoring System Backend v1.0.0
============================================================

Configuration validated successfully
Database initialized
LLM Monitoring: ENABLED
Application running on 0.0.0.0:8000
```

### Step 5: Test in Another Terminal

In terminal 2 (from backend folder):
```bash
python test_api.py
```

This will run all test scenarios and show you the system in action!

### Step 6: View API Documentation

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔍 What Each Feature Does

### 1. Event Submission
Submit data/events for the system to monitor:
```bash
curl -X POST http://localhost:8000/api/v1/monitoring/events \
  -H "Content-Type: application/json" \
  -d '{
    "source": "my_service",
    "event_type": "response",
    "data": {
      "response_time": 250,
      "status_code": 200
    }
  }'
```

### 2. Health Status
Check overall system health:
```bash
curl http://localhost:8000/api/v1/monitoring/health
```

### 3. View Logs
See all monitoring events:
```bash
curl http://localhost:8000/api/v1/monitoring/logs?limit=10
```

### 4. LLM Analysis
Get intelligent insights (requires API key):
```bash
curl -X POST http://localhost:8000/api/v1/monitoring/analysis/llm \
  -H "Content-Type: application/json" \
  -d '{"lookback_minutes": 30}'
```

### 5. Statistics
View system statistics:
```bash
curl http://localhost:8000/api/v1/monitoring/stats
```

---

## ⚠️ Troubleshooting

### "ModuleNotFoundError" when running main.py
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"
Either:
1. Kill the existing process: `lsof -ti:8000 | xargs kill -9`
2. Or change port in `.env`: `PORT=8001`

### "GROQ_API_KEY not set" error
Check that:
1. `.env` file exists in backend folder
2. GROQ_API_KEY line has your actual key (not placeholder)
3. File is saved
4. Server was restarted after adding key

### "Cannot connect to Monitoring System" when running tests
Make sure:
1. Server is running (`python main.py` in another terminal)
2. It says "Application running on 0.0.0.0:8000"
3. Both terminals are in the backend folder

### LLM features not working
1. Check if ENABLE_LLM_MONITORING=True in .env
2. Verify GROQ_API_KEY is set correctly
3. Restart server: stop and run `python main.py` again

---

## 📊 What the Tests Show

When you run `python test_api.py`, it tests:

✅ **Event Submission** - Normal, Warning, and Critical events
✅ **Health Status** - System health classification
✅ **Log Retrieval** - Getting and filtering logs
✅ **LLM Analysis** - Intelligent pattern analysis
✅ **Statistics** - System statistics
✅ **Re-evaluation** - Manual log re-analysis

---

## 🎯 Quick Commands Reference

| Command | What it does |
|---------|-------------|
| `python main.py` | Start the server |
| `python test_api.py` | Run all tests |
| `pip install -r requirements.txt` | Install dependencies |
| Visit `/docs` | See interactive API docs |
| Visit `/health` | Quick health check |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (ADD YOUR API KEY HERE) |
| `main.py` | Start the server |
| `test_api.py` | Run tests |
| `requirements.txt` | Dependencies |
| `README.md` | Full documentation |
| `QUICKSTART.md` | Quick start guide |

---

## 🚀 You're All Set!

1. ✅ Dependencies installed
2. ✅ API key configured in .env
3. ✅ Server running
4. ✅ Tests passing
5. ✅ API docs available

**Start using the Monitoring System!**

Visit: **http://localhost:8000/docs**

---

**Need help?** Check QUICKSTART.md or README.md for more details.
