# agent_core/tests.py
import json

from django.test import Client, TestCase
from django.urls import reverse


class AgentCoreTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_agent_status(self):
        """Test agent status endpoint"""
        response = self.client.get(reverse("agent-status"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "Agent is running.")

    def test_kpi_summary(self):
        """Test KPI summary calculation"""
        url = reverse("kpi-summary")
        payload = {"total_sales": 45000, "labor_cost": 12500, "food_cost": 11000, "hours_worked": 980}
        response = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertAlmostEqual(data["labor_percent"], 27.78, places=2)
        self.assertAlmostEqual(data["food_percent"], 24.44, places=2)

    def test_pmix_report(self):
        """Test product mix analysis"""
        url = reverse("pmix-report")
        payload = {
            "items": [
                {"name": "Ribeye", "quantity_sold": 55, "price": 42, "cost": 17},
                {"name": "Lobster Roll", "quantity_sold": 40, "price": 32, "cost": 13},
            ]
        }
        response = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["pmix_report"]), 2)

    def test_liquor_variance(self):
        """Test liquor variance calculation"""
        url = reverse("liquor-variance")
        payload = {"expected_oz": 100, "actual_oz": 85}
        response = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["variance_oz"], -15.0)

    def test_unified_agent_endpoint(self):
        """Test the unified agent endpoint"""
        url = reverse("agent")
        payload = {
            "task": "kpi_summary",
            "data": {"total_sales": 50000, "labor_cost": 15000, "food_cost": 12000, "hours_worked": 1000},
        }
        response = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_agent_view_missing_hr_data(self):
        url = reverse("agent")
        payload = {"task": "hr_retention", "data": {}}
        response = self.client.post(url, json.dumps(payload), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("turnover_rate", data["message"])


class BusinessLogicTests(TestCase):
    """Test the core business logic functions"""

    def test_kpi_calculations(self):
        """Test KPI calculation accuracy"""
        from backend.consulting_services.kpi import calculate_kpi_summary

        result = calculate_kpi_summary(total_sales=100000, labor_cost=30000, food_cost=25000, hours_worked=2000)

        self.assertEqual(result["labor_percent"], 30.0)
        self.assertEqual(result["food_percent"], 25.0)
        self.assertEqual(result["prime_cost"], 55000)
        self.assertEqual(result["prime_percent"], 55.0)
        self.assertEqual(result["sales_per_labor_hour"], 50.0)

    def test_liquor_variance_calculation(self):
        """Test liquor variance calculation accuracy"""
        from backend.consulting_services.liquor import calculate_liquor_variance

        result = calculate_liquor_variance(expected_oz=200, actual_oz=180)

        self.assertEqual(result["variance_oz"], -20.0)
        self.assertEqual(result["variance_percent"], -10.0)

    def test_product_mix_analysis(self):
        """Test product mix analysis logic"""
        from backend.consulting_services.product_mix import generate_pmix_report

        items = [
            {"name": "High Profit Item", "quantity_sold": 100, "price": 50, "cost": 20},
            {"name": "Low Profit Item", "quantity_sold": 50, "price": 30, "cost": 25},
        ]

        result = generate_pmix_report(items)

        self.assertEqual(result["status"], "success")
        # High profit item should be first (sorted by total profit)
        self.assertEqual(result["pmix_report"][0]["name"], "High Profit Item")
        self.assertEqual(result["pmix_report"][0]["total_profit"], 3000.0)
