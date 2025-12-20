"""
Test script specifically for Labor Cost Analysis
Demonstrates the exact API call the codex agent should use.
"""

import requests
import json


def test_labor_cost_analysis():
    """Test the Labor Cost Analysis endpoint with various scenarios."""
    base_url = "http://127.0.0.1:8000/api/agent/safe/"

    print("Testing Labor Cost Analysis Business Insight Card")
    print("=" * 60)

    # Test Case 1: Good Labor Efficiency
    print("\n1. Testing Good Labor Efficiency (21%)...")
    good_data = {
        "service": "kpi",
        "subtask": "labor_cost",
        "params": {
            "total_sales": 10000,
            "labor_cost": 2100
        }
    }

    try:
        response = requests.post(base_url, json=good_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Labor Cost %: {result['data']['labor_percent']}%")
            print(f"Efficiency: {result['data']['labor_efficiency']}")
            print(f"Insight: {result['insights'][0]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test Case 2: High Labor Cost (Above Target)
    print("\n2. Testing High Labor Cost (35%)...")
    high_data = {
        "service": "kpi",
        "subtask": "labor_cost",
        "params": {
            "total_sales": 10000,
            "labor_cost": 3500
        }
    }

    try:
        response = requests.post(base_url, json=high_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Labor Cost %: {result['data']['labor_percent']}%")
            print(f"Efficiency: {result['data']['labor_efficiency']}")
            print(f"Insight: {result['insights'][0]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test Case 3: Low Labor Cost (Below Target)
    print("\n3. Testing Low Labor Cost (15%)...")
    low_data = {
        "service": "kpi",
        "subtask": "labor_cost",
        "params": {
            "total_sales": 10000,
            "labor_cost": 1500
        }
    }

    try:
        response = requests.post(base_url, json=low_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Labor Cost %: {result['data']['labor_percent']}%")
            print(f"Efficiency: {result['data']['labor_efficiency']}")
            print(f"Insight: {result['insights'][0]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test Case 4: Error Handling - Missing Fields
    print("\n4. Testing Error Handling - Missing Fields...")
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
        if response.status_code == 400:
            result = response.json()
            print(f"Error: {result['error']}")
        else:
            print(f"Unexpected response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test Case 5: Error Handling - Negative Values
    print("\n5. Testing Error Handling - Negative Values...")
    negative_data = {
        "service": "kpi",
        "subtask": "labor_cost",
        "params": {
            "total_sales": -1000,
            "labor_cost": 2100
        }
    }

    try:
        response = requests.post(base_url, json=negative_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 400:
            result = response.json()
            print(f"Error: {result['error']}")
        else:
            print(f"Unexpected response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    print("\n" + "=" * 60)
    print("Labor Cost Analysis testing completed!")
    print("\nNext steps for Codex Agent:")
    print("1. Verify backend is working (Done)")
    print("2. Create frontend component")
    print("3. Add styling")
    print("4. Test complete user flow")


if __name__ == "__main__":
    test_labor_cost_analysis()
