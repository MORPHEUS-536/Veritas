"""
Simple test file demonstrating the Monitoring Module API.
Run this after starting the FastAPI server.
"""

import httpx
import asyncio
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


async def print_response(title: str, response: httpx.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, default=str))
    except:
        print(response.text)


async def test_monitoring_api():
    """Test the Monitoring Module API"""
    
    async with httpx.AsyncClient() as client:
        # 1. Health Check
        print("\n\n" + "█" * 60)
        print("█ TEST 1: HEALTH CHECK")
        print("█" * 60)
        
        response = await client.get(f"{BASE_URL}/monitor/health")
        await print_response("GET /monitor/health", response)
        
        
        # 2. Submit Normal Data
        print("\n\n" + "█" * 60)
        print("█ TEST 2: SUBMIT NORMAL DATA")
        print("█" * 60)
        
        normal_data = {
            "source_module": "inference",
            "event_type": "prediction_result",
            "data": {
                "prediction_score": 0.95,
                "latency_ms": 250,
                "model_version": "v2.1"
            }
        }
        print("\nRequest:")
        print(json.dumps(normal_data, indent=2))
        
        response = await client.post(
            f"{BASE_URL}/monitor/data",
            json=normal_data
        )
        await print_response("POST /monitor/data (Normal)", response)
        
        
        # 3. Submit Warning Data
        print("\n\n" + "█" * 60)
        print("█ TEST 3: SUBMIT WARNING DATA")
        print("█" * 60)
        
        warning_data = {
            "source_module": "preprocessing",
            "event_type": "data_validation",
            "data": {
                "error_rate": 0.08,
                "records_processed": 1024
            }
        }
        print("\nRequest:")
        print(json.dumps(warning_data, indent=2))
        
        response = await client.post(
            f"{BASE_URL}/monitor/data",
            json=warning_data
        )
        await print_response("POST /monitor/data (Warning)", response)
        
        
        # 4. Submit Critical Data
        print("\n\n" + "█" * 60)
        print("█ TEST 4: SUBMIT CRITICAL DATA")
        print("█" * 60)
        
        critical_data = {
            "source_module": "database",
            "event_type": "query_execution",
            "data": {
                "latency_ms": 6500,
                "status": "success"
            }
        }
        print("\nRequest:")
        print(json.dumps(critical_data, indent=2))
        
        response = await client.post(
            f"{BASE_URL}/monitor/data",
            json=critical_data
        )
        await print_response("POST /monitor/data (Critical)", response)
        
        
        # 5. Submit More Data for Patterns
        print("\n\n" + "█" * 60)
        print("█ TEST 5: SUBMIT MULTIPLE DATA POINTS")
        print("█" * 60)
        
        for i in range(5):
            data = {
                "source_module": "inference",
                "event_type": "prediction_result",
                "data": {
                    "prediction_score": 0.85 + (i * 0.02),
                    "latency_ms": 200 + (i * 50)
                }
            }
            response = await client.post(f"{BASE_URL}/monitor/data", json=data)
            print(f"  Submission {i+1}: {response.status_code} - {response.json()['detected_status']}")
        
        
        # 6. Get System Status
        print("\n\n" + "█" * 60)
        print("█ TEST 6: GET SYSTEM STATUS")
        print("█" * 60)
        
        response = await client.get(f"{BASE_URL}/monitor/status")
        await print_response("GET /monitor/status", response)
        
        
        # 7. Get Recent Logs
        print("\n\n" + "█" * 60)
        print("█ TEST 7: GET RECENT LOGS")
        print("█" * 60)
        
        response = await client.get(f"{BASE_URL}/monitor/logs?limit=5")
        await print_response("GET /monitor/logs?limit=5", response)
        
        
        # 8. Get Warning Logs Only
        print("\n\n" + "█" * 60)
        print("█ TEST 8: GET WARNING LOGS")
        print("█" * 60)
        
        response = await client.get(f"{BASE_URL}/monitor/logs?status=warning&limit=10")
        await print_response("GET /monitor/logs?status=warning", response)
        
        
        # 9. Get Logs by Source
        print("\n\n" + "█" * 60)
        print("█ TEST 9: GET LOGS BY SOURCE")
        print("█" * 60)
        
        response = await client.get(f"{BASE_URL}/monitor/logs?source=inference&limit=5")
        await print_response("GET /monitor/logs?source=inference", response)
        
        
        # 10. Trigger LLM Analysis (if enabled)
        print("\n\n" + "█" * 60)
        print("█ TEST 10: TRIGGER LLM ANALYSIS")
        print("█ (Requires ENABLE_LLM_MONITORING=true in .env)")
        print("█" * 60)
        
        analysis_request = {
            "num_recent_logs": 10,
            "focus_area": "latency"
        }
        print("\nRequest:")
        print(json.dumps(analysis_request, indent=2))
        
        response = await client.post(
            f"{BASE_URL}/monitor/analyze",
            json=analysis_request
        )
        await print_response("POST /monitor/analyze", response)
        
        
        # Final Status
        print("\n\n" + "█" * 60)
        print("█ FINAL: SYSTEM STATUS")
        print("█" * 60)
        
        response = await client.get(f"{BASE_URL}/monitor/status")
        await print_response("GET /monitor/status (Final)", response)
        
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Check logs at: logs/monitoring.log")
        print("2. Visit interactive docs at: http://localhost:8000/docs")
        print("3. Read API_EXAMPLES.md for more detailed examples")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n" + "▓" * 60)
    print("▓ MONITORING MODULE - API TEST SUITE")
    print("▓" * 60)
    print("\nMake sure the FastAPI server is running:")
    print("  python -m app.main")
    print("  or")
    print("  uvicorn app.main:app --reload")
    print("\n" + "▓" * 60 + "\n")
    
    try:
        asyncio.run(test_monitoring_api())
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nMake sure the server is running on http://localhost:8000")
        print("Run: python -m app.main")
