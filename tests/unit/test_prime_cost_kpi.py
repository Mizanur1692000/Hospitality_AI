"""Tests for the prime cost KPI analysis task."""

from __future__ import annotations

import json
from typing import Dict

from django.test import SimpleTestCase
from pydantic import ValidationError

from agent_core.schemas.kpi_analysis import InputPrimeCost
from agent_core.tasks.kpi_analysis.prime_cost import (
    build_prime_cost_response,
    calc_prime_cost,
    compare_to_benchmark,
    compute_percent,
    generate_recommendations,
)


class PrimeCostLogicTests(SimpleTestCase):
    """Validate the pure functions supporting the prime cost workflow."""

    def test_compute_percent(self) -> None:
        """Percentages should calculate as numerator divided by denominator."""

        self.assertAlmostEqual(compute_percent(30.0, 120.0), 0.25)
        with self.assertRaises(ValueError):
            compute_percent(10.0, 0.0)

    def test_calc_prime_cost_happy_path(self) -> None:
        """Prime cost metrics should include both component ratios and totals."""

        result = calc_prime_cost(18432.50, 26341.70, 83215.90)
        self.assertAlmostEqual(result["labor_pct"], 0.2215, places=3)
        self.assertAlmostEqual(result["food_pct"], 0.3165, places=3)
        self.assertAlmostEqual(result["prime_pct"], 0.5380, places=3)
        self.assertEqual(result["prime_amount"], 18432.50 + 26341.70)

    def test_compare_to_benchmark(self) -> None:
        """Benchmark comparison should signal when prime cost beats the target."""

        comparison = compare_to_benchmark(0.55, 0.60)
        self.assertTrue(comparison["is_within"])
        self.assertLess(comparison["delta_pct"], 0)

    def test_generate_recommendations_includes_food_guidance(self) -> None:
        """Food guidance triggers when food percentage is slightly elevated."""

        metrics: Dict[str, float] = {
            "prime_pct": 0.55,
            "food_pct": 0.33,
            "labor_pct": 0.22,
        }
        recs = generate_recommendations(metrics, 0.60)
        self.assertIn("Prime cost within standards—monitor weekly.", recs)
        self.assertTrue(any("Food costs" in rec for rec in recs))

    def test_build_prime_cost_response_structure(self) -> None:
        """The business logic must hydrate the output schema."""

        payload = InputPrimeCost(
            labor_costs=18432.50,
            food_costs=26341.70,
            total_sales=83215.90,
        )
        response = build_prime_cost_response(payload)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(len(response["metrics"]), 3)
        self.assertEqual(response["table"][2]["component"], "Prime")
        self.assertIn("Prime cost is", response["summary"])

    def test_input_validation_rules(self) -> None:
        """Schema validators should guard against invalid numbers."""

        with self.assertRaises(ValidationError):
            InputPrimeCost(labor_costs=-1.0, food_costs=0.0, total_sales=100.0)
        with self.assertRaises(ValidationError):
            InputPrimeCost(labor_costs=0.0, food_costs=0.0, total_sales=0.0)
        with self.assertRaises(ValidationError):
            InputPrimeCost(labor_costs=0.0, food_costs=0.0, total_sales=100.0, industry_benchmark_pct=1.5)
        with self.assertRaises(ValidationError):
            InputPrimeCost(labor_costs=0.0, total_sales=100.0)  # type: ignore[arg-type]


class PrimeCostEndpointTests(SimpleTestCase):
    """Ensure the /api/agent/ endpoint contracts for prime cost."""

    endpoint = "/api/agent/"
    entitlement_header = {"HTTP_X_KPI_ANALYSIS_ENTITLED": "true"}

    def _post(self, body: dict, use_entitlement: bool = True):
        headers = self.entitlement_header if use_entitlement else {}
        return self.client.post(
            self.endpoint,
            data=json.dumps(body),
            content_type="application/json",
            **headers,
        )

    def test_requires_entitlement(self) -> None:
        """Calls without entitlement should be locked."""

        response = self._post({"task": "kpi_analysis.prime_cost", "payload": {"labor_costs": 1}}, use_entitlement=False)
        self.assertEqual(response.status_code, 403)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], "LOCKED")
        self.assertEqual(payload["status"], "locked")

    def test_happy_path_response(self) -> None:
        """Prime cost service returns metrics and table entries on success."""

        body = {
            "task": "kpi_analysis.prime_cost",
            "payload": {
                "labor_costs": 18432.50,
                "food_costs": 26341.70,
                "total_sales": 83215.90,
                "industry_benchmark_pct": 0.60,
            },
        }
        response = self._post(body)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload["status"], "ok")
        self.assertAlmostEqual(payload["metrics"][2]["value"], 0.5380, places=3)
        self.assertAlmostEqual(payload["table"][2]["pct_sales"], 0.5380, places=3)
        self.assertIn("benchmark", payload["diagnostics"])

    def test_invalid_total_sales(self) -> None:
        """Zero sales should trigger a friendly validation error."""

        body = {
            "task": "kpi_analysis.prime_cost",
            "payload": {
                "labor_costs": 100.0,
                "food_costs": 100.0,
                "total_sales": 0.0,
            },
        }
        response = self._post(body)
        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.content)
        self.assertEqual(payload["code"], "INVALID_INPUT")
        self.assertIn("total_sales", payload["details"])

    def test_negative_costs(self) -> None:
        """Negative costs are rejected."""

        body = {
            "task": "kpi_analysis.prime_cost",
            "payload": {
                "labor_costs": -10.0,
                "food_costs": 100.0,
                "total_sales": 1000.0,
            },
        }
        response = self._post(body)
        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.content)
        self.assertIn("labor_costs", payload["details"])

    def test_missing_fields(self) -> None:
        """Omitting required fields should surface schema errors."""

        body = {"task": "kpi_analysis.prime_cost", "payload": {"labor_costs": 100.0, "total_sales": 1000.0}}
        response = self._post(body)
        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.content)
        self.assertIn("food_costs", payload["details"])

    def test_benchmark_out_of_range(self) -> None:
        """Benchmark must remain within the unit interval."""

        body = {
            "task": "kpi_analysis.prime_cost",
            "payload": {
                "labor_costs": 100.0,
                "food_costs": 100.0,
                "total_sales": 1000.0,
                "industry_benchmark_pct": 1.5,
            },
        }
        response = self._post(body)
        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.content)
        self.assertIn("industry_benchmark_pct", payload["details"])
