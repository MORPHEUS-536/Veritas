# Quick Start Guide

Get the Monitoring Module running in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

```bash
# Copy the example env file
copy .env.example .env

# Edit .env if needed (all defaults are set)
```

## Step 3: Create Logs Directory

```bash
mkdir logs
```

## Step 4: Start the Server

```bash
# Option A: Using Python module
python -m app.main

# Option B: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 5: Test the API

In a new terminal:

```bash
# Run the test suite
python test_api.py

# Or use curl to test a single endpoint
curl -X POST http://localhost:8000/monitor/data \
  -H "Content-Type: application/json" \
  -d '{
    "source_module": "inference",
    "event_type": "prediction_result",
    "data": {"prediction_score": 0.95, "latency_ms": 250}
  }'
```

## Step 6: View Interactive Documentation

Open your browser and go to:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Optional: Enable LLM Monitoring

To enable intelligent LLM analysis:

1. **Get an API key:**
   - OpenAI: https://platform.openai.com/api-keys
   - Claude: https://console.anthropic.com/
   - Gemini: https://ai.google.dev/

2. **Update .env:**
   ```env
   ENABLE_LLM_MONITORING=true
   LLM_PROVIDER=openai  # or claude, gemini
   LLM_API_KEY=your-key-here
   ```

3. **Restart the server and test:**
   ```bash
   python test_api.py
   ```

---

## Troubleshooting

**Port already in use?**
```bash
# Change port in .env
API_PORT=8001

# Or kill process using the port
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

**Module not found?**
```bash
# Make sure you're in the correct directory
cd c:\Monitoring

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**LLM API errors?**
- Check your API key is valid
- Check your LLM provider has active credits
- Check `logs/monitoring.log` for details

**Can't connect to server?**
- Make sure server is running on the correct port
- Check firewall settings
- Verify API_HOST and API_PORT in .env

---

## Next Steps

1. Read **README.md** for full documentation
2. Check **API_EXAMPLES.md** for detailed API examples
3. Integrate with your other modules (inference, preprocessing, etc.)
4. Customize the monitoring rules in `app/services/monitoring_service.py`

---

## Project Structure

```
monitoring/
├── app/
│   ├── main.py           ← FastAPI app
│   ├── config.py         ← Configuration
│   ├── models/schemas.py ← Data models
│   ├── services/
│   │   ├── monitoring_service.py  ← Core logic
│   │   └── llm_service.py         ← LLM integration
│   ├── routers/monitoring.py     ← API endpoints
│   └── utils/logger.py           ← Logging
├── .env.example          ← Configuration template
├── requirements.txt      ← Dependencies
├── README.md            ← Full docs
├── API_EXAMPLES.md      ← API examples
├── test_api.py          ← Test suite
└── QUICKSTART.md        ← This file
```

---

**That's it! Your monitoring module is ready to use.** 🎉

For complete documentation, see **README.md** and **API_EXAMPLES.md**.
