#!/usr/bin/env python
"""
Example usage of the FDE MVP API.
Demonstrates all key endpoints and functionality.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

def print_response(response):
    """Pretty print a response."""
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"Status Code: {response.status_code}\n")

def main():
    print_section("FDE MVP API Usage Examples")
    
    # 1. Health Check
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    
    # 2. Create Single Event
    print_section("2. Create Single Event")
    event_data = {
        "event_type": "transaction",
        "customer_id": "CUST_DEMO_001",
        "value": 1250.50,
        "status": "success",
        "metadata": {
            "source": "api_demo",
            "payment_method": "credit_card"
        }
    }
    response = requests.post(f"{BASE_URL}/events", json=event_data)
    print_response(response)
    
    # 3. Batch Event Ingestion
    print_section("3. Batch Event Ingestion")
    batch_events = [
        {
            "event_type": "login",
            "customer_id": "CUST_DEMO_001",
            "status": "success"
        },
        {
            "event_type": "transaction",
            "customer_id": "CUST_DEMO_001",
            "value": 450.00,
            "status": "success"
        },
        {
            "event_type": "error",
            "customer_id": "CUST_DEMO_002",
            "status": "failed"
        }
    ]
    response = requests.post(f"{BASE_URL}/ingest", json=batch_events)
    print_response(response)
    
    # 4. Get Events
    print_section("4. Get Events (Last 5)")
    response = requests.get(f"{BASE_URL}/events?limit=5")
    print_response(response)
    
    # 5. Get Customer Events
    print_section("5. Get Events for Customer CUST_DEMO_001")
    response = requests.get(f"{BASE_URL}/events?customer_id=CUST_DEMO_001")
    print_response(response)
    
    # 6. Risk Prediction
    print_section("6. Risk Prediction")
    risk_request = {
        "customer_id": "CUST_DEMO_001",
        "event_type": "transaction",
        "value": 5000.00,
        "metadata": {
            "urgent": True,
            "location": "foreign"
        }
    }
    response = requests.post(f"{BASE_URL}/predict", json=risk_request)
    print_response(response)
    
    # 7. Data Quality Reports
    print_section("7. Data Quality Reports")
    response = requests.get(f"{BASE_URL}/data-quality/reports?limit=3")
    print_response(response)
    
    # 8. RAG Copilot Query
    print_section("8. RAG Copilot Query")
    copilot_query = {
        "question": "What are the supported event types in the system?",
        "max_sources": 3
    }
    response = requests.post(f"{BASE_URL}/copilot", json=copilot_query)
    print_response(response)
    
    # 9. Another Copilot Query
    print_section("9. RAG Copilot - Risk Factors Query")
    copilot_query = {
        "question": "How is risk score calculated?",
        "max_sources": 3
    }
    response = requests.post(f"{BASE_URL}/copilot", json=copilot_query)
    print_response(response)
    
    print_section("Example Complete!")
    print("Visit http://localhost:8501 to see the dashboard")
    print("Visit http://localhost:8000/docs for interactive API docs")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API.")
        print("Make sure the API is running: docker-compose up -d")
        print("Or run locally: uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"\nError: {e}")
