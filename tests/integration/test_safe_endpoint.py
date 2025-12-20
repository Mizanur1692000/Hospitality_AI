"""
Test script for the safe endpoint
Validates that the new architecture works without breaking existing functionality.
"""

import requests
import json


def test_safe_endpoint():
    """Test the safe endpoint with various scenarios."""
    base_url = "http://127.0.0.1:8000/api/agent/safe/"

    print("Testing Safe Agent Service Endpoint")
    print("=" * 50)

    # Test 1: Labor Cost Analysis
    print("\n1. Testing Labor Cost Analysis...")
    labor_data = {
        "service": "kpi",
        "subtask": "labor_cost",
        "params": {
            "total_sales": 10000,
            "labor_cost": 2100
        }
    }

    try:
        response = requests.post(base_url, json=labor_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Prime Cost Analysis
    print("\n2. Testing Prime Cost Analysis...")
    prime_data = {
        "service": "kpi",
        "subtask": "prime_cost",
        "params": {
            "total_sales": 10000,
            "labor_cost": 2100,
            "food_cost": 3300
        }
    }

    try:
        response = requests.post(base_url, json=prime_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Sales Performance Analysis
    print("\n3. Testing Sales Performance Analysis...")
    sales_data = {
        "service": "kpi",
        "subtask": "sales_performance",
        "params": {
            "total_sales": 12000,
            "hours_open": 48
        }
    }

    try:
        response = requests.post(base_url, json=sales_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 4: Invalid Task
    print("\n4. Testing Invalid Task...")
    invalid_data = {
        "service": "kpi",
        "subtask": "invalid_task",
        "params": {}
    }

    try:
        response = requests.post(base_url, json=invalid_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 5: Missing Required Fields
    print("\n5. Testing Missing Required Fields...")
    missing_data = {
        "service": "kpi",
        "subtask": "labor_cost",
        "params": {
            "total_sales": 10000
            # Missing labor_cost
        }
    }

    try:
        response = requests.post(base_url, json=missing_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("Safe endpoint testing completed!")


if __name__ == "__main__":
    test_safe_endpoint()
