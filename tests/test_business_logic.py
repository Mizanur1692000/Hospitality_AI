#!/usr/bin/env python3
"""
Comprehensive Business Logic Test Suite
Tests all critical KPI calculations and API endpoints
Run this before deploying to production!

Usage:
    python tests/test_business_logic.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from backend.consulting_services.kpi.kpi_utils import (
    calculate_kpi_summary,
    calculate_labor_cost_analysis,
    calculate_prime_cost_analysis,
    calculate_sales_performance_analysis
)
from django.test import RequestFactory
from apps.agent_core.views import agent_view
import json


class TestRunner:
    """Test runner with colored output"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def test(self, name, condition, details=""):
        """Run a single test"""
        if condition:
            print(f"  ✅ {name}")
            self.passed += 1
            self.tests.append((name, True, details))
        else:
            print(f"  ❌ {name}")
            if details:
                print(f"     → {details}")
            self.failed += 1
            self.tests.append((name, False, details))

    def section(self, title):
        """Print section header"""
        print(f"\n{'='*70}")
        print(f"{title}")
        print('='*70)

    def summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print("TEST SUMMARY")
        print('='*70)
        print(f"  Total Tests: {self.passed + self.failed}")
        print(f"  ✅ Passed: {self.passed}")
        print(f"  ❌ Failed: {self.failed}")

        if self.failed == 0:
            print(f"\n  🎉 ALL TESTS PASSED! Ready for production!")
        else:
            print(f"\n  ⚠️  {self.failed} test(s) failed - fix before deploying")
        print('='*70)

        return self.failed == 0


def test_kpi_calculations(runner):
    """Test core KPI calculation functions"""
    runner.section("1. KPI CALCULATION TESTS")

    # Test with valid data
    result = calculate_kpi_summary(
        total_sales=10000.0,
        labor_cost=2800.0,
        food_cost=3200.0,
        hours_worked=200.0
    )

    runner.test("KPI Summary returns success", result['status'] == 'success')
    runner.test("Labor % calculation correct", result['kpis']['labor_percent']['value'] == 28.0)
    runner.test("Food % calculation correct", result['kpis']['food_percent']['value'] == 32.0)
    runner.test("Prime Cost % calculation correct", result['kpis']['prime_percent']['value'] == 60.0)
    runner.test("Sales per Hour calculation correct", result['kpis']['sales_per_labor_hour']['value'] == 50.0)
    runner.test("Recommendations provided", len(result['recommendations']) > 0)
    runner.test("Industry benchmarks included", 'industry_benchmarks' in result)

    # Test error handling - negative values
    error_result = calculate_kpi_summary(
        total_sales=-10000.0,
        labor_cost=2800.0,
        food_cost=3200.0,
        hours_worked=200.0
    )
    runner.test("Negative sales rejected", error_result['status'] == 'error')

    # Test error handling - zero hours
    error_result = calculate_kpi_summary(
        total_sales=10000.0,
        labor_cost=2800.0,
        food_cost=3200.0,
        hours_worked=0.0
    )
    runner.test("Zero hours rejected", error_result['status'] == 'error')

    # Test error handling - zero sales
    error_result = calculate_kpi_summary(
        total_sales=0.0,
        labor_cost=2800.0,
        food_cost=3200.0,
        hours_worked=200.0
    )
    runner.test("Zero sales rejected", error_result['status'] == 'error')


def test_labor_cost_analysis(runner):
    """Test labor cost analysis"""
    runner.section("2. LABOR COST ANALYSIS TESTS")

    result = calculate_labor_cost_analysis(
        total_sales=10000.0,
        labor_cost=2800.0,
        hours_worked=200.0,
        target_labor_percent=30.0
    )

    runner.test("Labor analysis returns success", result['status'] == 'success')
    runner.test("Labor percent calculated", 'labor_percent' in result['key_metrics'])
    runner.test("Performance rating provided", result['performance_rating'] in ['Excellent', 'Good', 'Acceptable', 'Needs Improvement'])
    runner.test("Business report generated", len(result['business_report']) > 0)
    runner.test("Recommendations provided", len(result['recommendations']) > 0)


def test_prime_cost_analysis(runner):
    """Test prime cost analysis"""
    runner.section("3. PRIME COST ANALYSIS TESTS")

    result = calculate_prime_cost_analysis(
        total_sales=10000.0,
        labor_cost=2800.0,
        food_cost=3200.0,
        target_prime_percent=60.0
    )

    runner.test("Prime cost analysis returns success", result['status'] == 'success')
    runner.test("Prime cost calculated", 'prime_cost' in result['key_metrics'])
    runner.test("Prime cost equals labor + food", result['key_metrics']['prime_cost'] == 6000.0)
    runner.test("Performance rating provided", result['performance_rating'] in ['Excellent', 'Good', 'Acceptable', 'Needs Improvement'])
    runner.test("Business report generated", len(result['business_report']) > 0)


def test_sales_performance_analysis(runner):
    """Test sales performance analysis"""
    runner.section("4. SALES PERFORMANCE ANALYSIS TESTS")

    result = calculate_sales_performance_analysis(
        total_sales=10000.0,
        labor_cost=2800.0,
        food_cost=3200.0,
        hours_worked=200.0,
        previous_sales=9000.0
    )

    runner.test("Sales analysis returns success", result['status'] == 'success')
    runner.test("Sales per hour calculated", 'sales_per_labor_hour' in result['key_metrics'])
    runner.test("Growth metrics included", 'additional_insights' in result)
    runner.test("Performance rating provided", result['performance_rating'] in ['Excellent', 'Good', 'Acceptable', 'Needs Improvement'])


def test_api_endpoints(runner):
    """Test API endpoints"""
    runner.section("5. API ENDPOINT TESTS")

    factory = RequestFactory()

    # Test KPI summary endpoint with entitlement
    request_data = {
        'task': 'kpi_summary',
        'payload': {
            'total_sales': 10000.0,
            'labor_cost': 2800.0,
            'food_cost': 3200.0,
            'hours_worked': 200.0
        }
    }

    request = factory.post(
        '/api/agent/',
        data=json.dumps(request_data),
        content_type='application/json',
        HTTP_X_KPI_ANALYSIS_ENTITLED='true'
    )

    response = agent_view(request)
    runner.test("KPI endpoint returns 200", response.status_code == 200)

    response_data = json.loads(response.content)
    runner.test("KPI endpoint returns valid JSON", 'kpis' in response_data)

    # Test without entitlement (should fail)
    request = factory.post(
        '/api/agent/',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    response = agent_view(request)
    runner.test("KPI endpoint requires entitlement", response.status_code == 403)

    # Test validation (missing fields)
    request_data_invalid = {
        'task': 'kpi_summary',
        'payload': {
            'total_sales': 10000.0
            # Missing required fields
        }
    }

    request = factory.post(
        '/api/agent/',
        data=json.dumps(request_data_invalid),
        content_type='application/json',
        HTTP_X_KPI_ANALYSIS_ENTITLED='true'
    )

    response = agent_view(request)
    runner.test("API validates required fields", response.status_code == 400)

    # Test HR retention (non-entitlement endpoint)
    request_data = {
        'task': 'hr_retention',
        'payload': {
            'turnover_rate': 45.0,
            'industry_avg': 70.0
        }
    }

    request = factory.post(
        '/api/agent/',
        data=json.dumps(request_data),
        content_type='application/json'
    )

    response = agent_view(request)
    runner.test("Non-entitlement endpoint works", response.status_code == 200)


def test_edge_cases(runner):
    """Test edge cases and boundary conditions"""
    runner.section("6. EDGE CASE TESTS")

    # Very large numbers
    result = calculate_kpi_summary(
        total_sales=1000000.0,
        labor_cost=280000.0,
        food_cost=320000.0,
        hours_worked=2000.0
    )
    runner.test("Handles large numbers", result['status'] == 'success')

    # Very small numbers
    result = calculate_kpi_summary(
        total_sales=100.0,
        labor_cost=28.0,
        food_cost=32.0,
        hours_worked=2.0
    )
    runner.test("Handles small numbers", result['status'] == 'success')

    # Decimal precision
    result = calculate_kpi_summary(
        total_sales=10000.50,
        labor_cost=2800.33,
        food_cost=3200.17,
        hours_worked=200.5
    )
    runner.test("Handles decimal precision", result['status'] == 'success')
    runner.test("Calculations maintain precision", isinstance(result['kpis']['prime_percent']['value'], (int, float)))


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 HOSPITALITY AI - BUSINESS LOGIC TEST SUITE")
    print("="*70)
    print("Testing all critical calculations and API endpoints...")

    runner = TestRunner()

    # Run all test suites
    test_kpi_calculations(runner)
    test_labor_cost_analysis(runner)
    test_prime_cost_analysis(runner)
    test_sales_performance_analysis(runner)
    test_api_endpoints(runner)
    test_edge_cases(runner)

    # Print summary
    all_passed = runner.summary()

    # Return exit code
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
