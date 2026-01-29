# API Examples & Documentation

This document provides complete API request/response examples for the Monitoring Module.

---

## Table of Contents
1. [Submit Data for Monitoring](#1-submit-data-for-monitoring)
2. [Get System Health Status](#2-get-system-health-status)
3. [Get Monitoring Logs](#3-get-monitoring-logs)
4. [Trigger LLM Analysis](#4-trigger-llm-analysis)
5. [Health Check](#5-health-check)

---

## 1. Submit Data for Monitoring

**Endpoint:** `POST /monitor/data`

**Description:** Submit data/events from other modules to be monitored for anomalies, threshold violations, and suspicious patterns.

### Request

```bash
curl -X POST http://localhost:8000/monitor/data \
  -H "Content-Type: application/json" \
  -d '{
    "source_module": "inference",
    "event_type": "prediction_result",
    "data": {
      "prediction_score": 0.95,
      "latency_ms": 250,
      "model_version": "v2.1"
    },
    "metadata": {
      "user_id": "user_123",
      "request_id": "req_abc123"
    }
  }'
```

### Request Schema

```json
{
  "source_module": "string (required) - Name of module sending data",
  "event_type": "string (required) - Type of event",
  "data": "object (required) - Actual data to monitor",
  "metadata": "object (optional) - Additional metadata",
  "timestamp": "ISO 8601 datetime (optional) - Defaults to current time"
}
```

### Response (Success)

**Status Code:** 200 OK

```json
{
  "success": true,
  "message": "Data monitored successfully",
  "log_id": "log_20260129_103000_a1b2c3d4",
  "detected_status": "normal",
  "reason": "All metrics within acceptable range"
}
```

### Response (Warning)

```json
{
  "success": true,
  "message": "Data monitored successfully",
  "log_id": "log_20260129_103045_x8y9z0w1",
  "detected_status": "warning",
  "reason": "High latency detected: 2500ms"
}
```

### Response (Critical)

```json
{
  "success": true,
  "message": "Data monitored successfully",
  "log_id": "log_20260129_103100_p2q3r4s5",
  "detected_status": "critical",
  "reason": "Excessive latency detected: 6000ms"
}
```

### Example: Different Data Types

**Inference Pipeline Data:**
```json
{
  "source_module": "inference",
  "event_type": "prediction_result",
  "data": {
    "prediction_score": 0.87,
    "confidence": 0.92,
    "latency_ms": 300,
    "model_version": "v2.1"
  }
}
```

**Preprocessing Module Data:**
```json
{
  "source_module": "preprocessing",
  "event_type": "data_validation",
  "data": {
    "records_processed": 1024,
    "error_rate": 0.02,
    "duration_ms": 500,
    "status": "success"
  }
}
```

**Database Operation:**
```json
{
  "source_module": "database",
  "event_type": "query_execution",
  "data": {
    "latency_ms": 150,
    "rows_affected": 42,
    "status": "success"
  }
}
```

---

## 2. Get System Health Status

**Endpoint:** `GET /monitor/status`

**Description:** Get the current overall system health status with key metrics.

### Request

```bash
curl -X GET http://localhost:8000/monitor/status
```

### Response

**Status Code:** 200 OK

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

### Response (With Recent Critical Event)

```json
{
  "current_status": "critical",
  "total_logs_processed": 623,
  "warning_count": 8,
  "critical_count": 2,
  "last_update": "2026-01-29T10:40:15Z",
  "uptime_seconds": 5400.2,
  "last_critical_event": {
    "log_id": "log_20260129_104010_m7n8o9p0",
    "timestamp": "2026-01-29T10:40:10Z",
    "source_module": "inference",
    "event_type": "prediction_result",
    "input_data_snapshot": {
      "prediction_score": 0.45
    },
    "detected_status": "critical",
    "reason": "Low prediction confidence: 0.45",
    "llm_analysis": null,
    "llm_suggestions": null
  }
}
```

---

## 3. Get Monitoring Logs

**Endpoint:** `GET /monitor/logs`

**Description:** Retrieve recent monitoring logs with optional filtering by status or source.

### Request - Get Recent Logs

```bash
curl -X GET http://localhost:8000/monitor/logs?limit=10
```

### Request - Filter by Status

```bash
curl -X GET http://localhost:8000/monitor/logs?limit=20&status=warning
```

### Request - Filter by Source Module

```bash
curl -X GET http://localhost:8000/monitor/logs?limit=15&source=inference
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 50 | Number of logs to return (1-500) |
| status | string | none | Filter by status: normal, warning, or critical |
| source | string | none | Filter by source module name |

### Response

**Status Code:** 200 OK

```json
{
  "total_count": 512,
  "returned_count": 3,
  "logs": [
    {
      "log_id": "log_20260129_101500_a1b2c3d4",
      "timestamp": "2026-01-29T10:15:00Z",
      "source_module": "inference",
      "event_type": "prediction_result",
      "input_data_snapshot": {
        "prediction_score": 0.95,
        "latency_ms": 250
      },
      "detected_status": "normal",
      "reason": "All metrics within acceptable range",
      "llm_analysis": null,
      "llm_suggestions": null
    },
    {
      "log_id": "log_20260129_102000_e5f6g7h8",
      "timestamp": "2026-01-29T10:20:00Z",
      "source_module": "preprocessing",
      "event_type": "data_validation",
      "input_data_snapshot": {
        "error_rate": 0.08
      },
      "detected_status": "warning",
      "reason": "Elevated error rate: 8.0%",
      "llm_analysis": "The preprocessing module is experiencing slightly elevated error rates, likely due to data quality issues. Monitor for patterns.",
      "llm_suggestions": [
        "Review input data quality",
        "Check preprocessing rules",
        "Consider alerting data intake team"
      ]
    },
    {
      "log_id": "log_20260129_102500_i9j0k1l2",
      "timestamp": "2026-01-29T10:25:00Z",
      "source_module": "database",
      "event_type": "query_execution",
      "input_data_snapshot": {
        "latency_ms": 6500,
        "status": "success"
      },
      "detected_status": "critical",
      "reason": "Excessive latency detected: 6500ms",
      "llm_analysis": "Database queries are significantly slower than expected. This could impact overall system performance.",
      "llm_suggestions": [
        "Check database load",
        "Review active connections",
        "Consider query optimization",
        "Check for locks or deadlocks"
      ]
    }
  ]
}
```

---

## 4. Trigger LLM Analysis

**Endpoint:** `POST /monitor/analyze`

**Description:** Manually trigger intelligent LLM-based analysis on recent monitoring logs. Requires ENABLE_LLM_MONITORING=true in .env.

### Request

```bash
curl -X POST http://localhost:8000/monitor/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "num_recent_logs": 20,
    "focus_area": "latency"
  }'
```

### Request Schema

```json
{
  "num_recent_logs": "integer (1-100, default 10) - Number of recent logs to analyze",
  "focus_area": "string (optional) - Specific area to focus on"
}
```

### Response (Normal System)

**Status Code:** 200 OK

```json
{
  "system_state": "normal",
  "analysis": "The system is operating normally with consistent performance metrics. All monitored components are functioning within expected parameters.",
  "suggestions": [
    "Continue standard monitoring protocols",
    "Monitor inference latency trends",
    "Log performance metrics hourly"
  ],
  "confidence": 0.94,
  "analysis_timestamp": "2026-01-29T10:35:00Z"
}
```

### Response (Warning System)

```json
{
  "system_state": "warning",
  "analysis": "The system is experiencing some performance degradation. Recent logs show elevated latency in the database module and slightly reduced prediction confidence scores.",
  "suggestions": [
    "Investigate database performance",
    "Review model performance metrics",
    "Check system resource utilization",
    "Consider scaling if load is high"
  ],
  "confidence": 0.87,
  "analysis_timestamp": "2026-01-29T10:35:00Z"
}
```

### Response (Critical System)

```json
{
  "system_state": "critical",
  "analysis": "Multiple critical issues detected. Prediction confidence has dropped significantly, and latency exceeds acceptable thresholds. Immediate investigation required.",
  "suggestions": [
    "Scale up inference infrastructure",
    "Restart affected services",
    "Review model performance",
    "Check for resource exhaustion",
    "Initiate incident response protocol"
  ],
  "confidence": 0.91,
  "analysis_timestamp": "2026-01-29T10:35:00Z"
}
```

### Error Response - LLM Not Enabled

**Status Code:** 503 Service Unavailable

```json
{
  "detail": "LLM monitoring is not enabled. Set ENABLE_LLM_MONITORING=true in .env"
}
```

### Error Response - No Logs Available

**Status Code:** 400 Bad Request

```json
{
  "detail": "No logs available for analysis"
}
```

---

## 5. Health Check

**Endpoint:** `GET /monitor/health`

**Description:** Simple health check endpoint to verify the service is running.

### Request

```bash
curl -X GET http://localhost:8000/monitor/health
```

### Response

**Status Code:** 200 OK

```json
{
  "status": "healthy",
  "service": "monitoring",
  "timestamp": "2026-01-29T10:35:00Z",
  "llm_enabled": true
}
```

---

## Python Client Examples

### Using `requests` library

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Submit monitoring data
def submit_data():
    response = requests.post(
        f"{BASE_URL}/monitor/data",
        json={
            "source_module": "inference",
            "event_type": "prediction_result",
            "data": {
                "prediction_score": 0.95,
                "latency_ms": 250
            }
        }
    )
    print(json.dumps(response.json(), indent=2))

# 2. Get system status
def get_status():
    response = requests.get(f"{BASE_URL}/monitor/status")
    print(json.dumps(response.json(), indent=2))

# 3. Get logs with filter
def get_logs():
    response = requests.get(
        f"{BASE_URL}/monitor/logs",
        params={"limit": 10, "status": "warning"}
    )
    print(json.dumps(response.json(), indent=2))

# 4. Trigger LLM analysis
def analyze():
    response = requests.post(
        f"{BASE_URL}/monitor/analyze",
        json={
            "num_recent_logs": 20,
            "focus_area": "latency"
        }
    )
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    submit_data()
    get_status()
    get_logs()
    analyze()
```

### Using `httpx` with async/await

```python
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def main():
    async with httpx.AsyncClient() as client:
        # Submit data
        response = await client.post(
            f"{BASE_URL}/monitor/data",
            json={
                "source_module": "inference",
                "event_type": "prediction_result",
                "data": {"prediction_score": 0.95}
            }
        )
        print(json.dumps(response.json(), indent=2))
        
        # Get status
        response = await client.get(f"{BASE_URL}/monitor/status")
        print(json.dumps(response.json(), indent=2))

asyncio.run(main())
```

---

## Error Handling

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Data submitted and analyzed successfully |
| 400 | Bad Request | Invalid query parameters or malformed JSON |
| 500 | Server Error | Unexpected internal error |
| 503 | Service Unavailable | LLM provider not configured |

### Error Response Format

```json
{
  "detail": "Error description explaining what went wrong"
}
```

---

## Testing the Monitoring Module

### Shell Script for Testing

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "=== Monitoring Module Test Suite ==="

# Test 1: Health check
echo -e "\n1. Health Check"
curl -s "$BASE_URL/monitor/health" | jq .

# Test 2: Submit normal data
echo -e "\n2. Submit Normal Data"
curl -s -X POST "$BASE_URL/monitor/data" \
  -H "Content-Type: application/json" \
  -d '{
    "source_module": "inference",
    "event_type": "prediction_result",
    "data": {"prediction_score": 0.95, "latency_ms": 200}
  }' | jq .

# Test 3: Submit warning data
echo -e "\n3. Submit Warning Data"
curl -s -X POST "$BASE_URL/monitor/data" \
  -H "Content-Type: application/json" \
  -d '{
    "source_module": "inference",
    "event_type": "prediction_result",
    "data": {"prediction_score": 0.65}
  }' | jq .

# Test 4: Submit critical data
echo -e "\n4. Submit Critical Data"
curl -s -X POST "$BASE_URL/monitor/data" \
  -H "Content-Type: application/json" \
  -d '{
    "source_module": "inference",
    "event_type": "prediction_result",
    "data": {"latency_ms": 6500}
  }' | jq .

# Test 5: Get status
echo -e "\n5. Get System Status"
curl -s "$BASE_URL/monitor/status" | jq .

# Test 6: Get logs
echo -e "\n6. Get Recent Logs"
curl -s "$BASE_URL/monitor/logs?limit=5" | jq .

# Test 7: Get warning logs
echo -e "\n7. Get Warning Logs"
curl -s "$BASE_URL/monitor/logs?status=warning" | jq .

# Test 8: LLM Analysis (if enabled)
echo -e "\n8. Trigger LLM Analysis"
curl -s -X POST "$BASE_URL/monitor/analyze" \
  -H "Content-Type: application/json" \
  -d '{"num_recent_logs": 10}' | jq .

echo -e "\n=== Tests Complete ==="
```

Save as `test_monitoring.sh`, make executable, and run:
```bash
chmod +x test_monitoring.sh
./test_monitoring.sh
```

---

## Integration with Other Modules

The Monitoring module exposes clear, RESTful endpoints that any other module can call.

### Example: Inference Module Integration

```python
# In your inference module
import requests
from datetime import datetime

MONITOR_URL = "http://localhost:8000"

def log_prediction_result(prediction, confidence, latency_ms):
    """Send prediction result to monitoring module"""
    response = requests.post(
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
    
    if response.status_code == 200:
        result = response.json()
        if result["detected_status"] == "critical":
            # Handle critical alert
            trigger_incident_response()
        elif result["detected_status"] == "warning":
            # Log warning for investigation
            log_warning(result["reason"])
    
    return response.json()
```

---

## Tips & Best Practices

1. **Always include `source_module`** - This helps identify which module sent the data
2. **Use consistent `event_type` values** - Makes filtering and analysis more meaningful
3. **Include relevant metrics in data** - More context helps both rule-based and LLM analysis
4. **Monitor logs regularly** - Check `/monitor/logs` periodically for patterns
5. **Run LLM analysis periodically** - Get intelligent insights beyond rule-based detection
6. **Set up alerting** - Monitor `/monitor/status` and alert on status changes
7. **Clean up logs** - In production, consider persisting logs to a database
