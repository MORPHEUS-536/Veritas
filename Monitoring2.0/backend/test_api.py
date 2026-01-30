"""
Sample Test Script for Monitoring System
Demonstrates API usage and testing scenarios.

IMPORTANT: Before running this script:
1. Make sure the server is running (python main.py in another terminal)
2. Have your Groq API key ready from https://console.groq.com
3. Add the API key to the .env file (GROQ_API_KEY=your_key_here)
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000/api/v1/monitoring"


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_response(response):
    """Pretty print API response."""
    try:
        data = response.json()
        print(json.dumps(data, indent=2, default=str))
    except:
        print(response.text)


def test_submit_event(name, source, event_type, data):
    """Test submitting an event."""
    print(f"Submitting event: {name}")
    response = requests.post(
        f"{BASE_URL}/events",
        json={
            "source": source,
            "event_type": event_type,
            "data": data,
            "metadata": {"test_id": name}
        }
    )
    print(f"Status: {response.status_code}")
    print_response(response)
    return response.json() if response.status_code == 201 else None


def test_health_status():
    """Test getting health status."""
    print("Getting system health status...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print_response(response)


def test_get_logs():
    """Test getting logs."""
    print("Getting monitoring logs...")
    response = requests.get(f"{BASE_URL}/logs?limit=5")
    print(f"Status: {response.status_code}")
    print_response(response)


def test_query_logs(status=None, source=None):
    """Test querying logs with filters."""
    print(f"Querying logs (status={status}, source={source})...")
    response = requests.post(
        f"{BASE_URL}/logs/query",
        json={
            "limit": 10,
            "offset": 0,
            "status": status,
            "source": source
        }
    )
    print(f"Status: {response.status_code}")
    print_response(response)


def test_llm_analysis():
    """Test LLM analysis."""
    print("Triggering LLM analysis...")
    response = requests.post(
        f"{BASE_URL}/analysis/llm",
        json={
            "lookback_minutes": 10,
            "focus_areas": ["response_time", "error_rate"]
        }
    )
    print(f"Status: {response.status_code}")
    print_response(response)


def test_statistics():
    """Test getting statistics."""
    print("Getting statistics...")
    response = requests.get(f"{BASE_URL}/stats")
    print(f"Status: {response.status_code}")
    print_response(response)


def test_re_evaluate():
    """Test re-evaluation."""
    print("Triggering re-evaluation...")
    response = requests.post(f"{BASE_URL}/analysis/re-evaluate?lookback_minutes=30")
    print(f"Status: {response.status_code}")
    print_response(response)


def run_test_suite():
    """Run complete test suite."""
    print_section("MONITORING SYSTEM - API TEST SUITE")
    print("Testing Monitoring System endpoints...\n")
    
    # Test 1: Root endpoint
    print_section("TEST 1: Root Endpoint")
    response = requests.get(BASE_URL + "/")
    print_response(response)
    
    # Test 2: Submit normal event
    print_section("TEST 2: Submit Normal Event")
    test_submit_event(
        "normal_response",
        "api_service",
        "api_response",
        {
            "response_time": 150,
            "status_code": 200,
            "items_returned": 100,
            "output": "success"
        }
    )
    
    # Test 3: Submit warning event (high response time)
    print_section("TEST 3: Submit Warning Event (High Response Time)")
    test_submit_event(
        "slow_response",
        "api_service",
        "api_response",
        {
            "response_time": 8000,  # Exceeds threshold
            "status_code": 200,
            "items_returned": 50,
            "output": "success"
        }
    )
    
    # Test 4: Submit critical event (multiple issues)
    print_section("TEST 4: Submit Critical Event (Multiple Issues)")
    test_submit_event(
        "critical_event",
        "database_service",
        "query_response",
        {
            "response_time": 10000,  # Exceeds threshold
            "error_rate": 25,  # Exceeds threshold
            "cpu_usage": 95,  # Exceeds threshold
            "status": "error"
        }
    )
    
    # Test 5: Submit event with silent failure pattern
    print_section("TEST 5: Silent Failure Detection")
    test_submit_event(
        "silent_failure",
        "processing_service",
        "data_processing",
        {
            "status": "success",
            "processed": True,
            "result": None,  # Silent failure pattern
            "items_processed": 0
        }
    )
    
    # Test 6: Get health status
    print_section("TEST 6: Get Health Status")
    test_health_status()
    
    # Test 7: Get all logs
    print_section("TEST 7: Get Monitoring Logs")
    test_get_logs()
    
    # Test 8: Query logs by status
    print_section("TEST 8: Query Logs - WARNING Status")
    test_query_logs(status="WARNING")
    
    # Test 9: Query logs by source
    print_section("TEST 9: Query Logs - Specific Source")
    test_query_logs(source="api_service")
    
    # Test 10: Get statistics
    print_section("TEST 10: Get Statistics")
    test_statistics()
    
    # Test 11: Re-evaluate
    print_section("TEST 11: Re-evaluate Recent Logs")
    test_re_evaluate()
    
    # Test 12: LLM Analysis (if enabled)
    print_section("TEST 12: Trigger LLM Analysis")
    test_llm_analysis()
    
    print_section("TEST SUITE COMPLETE")
    print("All tests executed. Check responses above for results.\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  MONITORING SYSTEM - TEST SCRIPT")
    print("=" * 60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Time: {datetime.now().isoformat()}\n")
    
    try:
        # Test connectivity
        print("Testing connectivity...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ Connected to Monitoring System\n")
        else:
            print("✗ Connection failed\n")
            exit(1)
        
        # Run test suite
        run_test_suite()
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to Monitoring System")
        print(f"  Make sure the server is running at {BASE_URL}")
        print("\n  Run the server with:")
        print("    python main.py")
        exit(1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        exit(1)
