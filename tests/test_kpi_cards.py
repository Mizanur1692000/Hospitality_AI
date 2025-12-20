"""
Tests for KPI Business Insight Cards
Validates the new task functions work correctly.
"""

from agent_core.tasks.kpi_labor_cost import run as lc_run
from agent_core.tasks.kpi_prime_cost import run as pc_run
from agent_core.tasks.kpi_sales_performance import run as sp_run


def test_labor_cost_success():
    """Test successful labor cost calculation."""
    payload, code = lc_run({"total_sales": 10000, "labor_cost": 2100})
    assert code == 200
    assert payload["status"] == "success"
    assert payload["data"]["labor_percent"] == 21.0
    assert payload["service"] == "kpi"
    assert payload["subtask"] == "labor_cost"
    assert len(payload["insights"]) > 0


def test_labor_cost_missing_fields():
    """Test labor cost with missing required fields."""
    payload, code = lc_run({"total_sales": 10000})
    assert code == 400
    assert payload["status"] == "error"
    assert "Missing required fields" in payload["error"]


def test_labor_cost_negative_values():
    """Test labor cost with negative values."""
    payload, code = lc_run({"total_sales": -1000, "labor_cost": 2100})
    assert code == 400
    assert payload["status"] == "error"
    assert "must be >= 0" in payload["error"]


def test_prime_cost_success():
    """Test successful prime cost calculation."""
    payload, code = pc_run({"total_sales": 10000, "labor_cost": 2100, "food_cost": 3300})
    assert code == 200
    assert payload["status"] == "success"
    assert payload["data"]["prime_cost"] == 5400
    assert payload["data"]["prime_percent"] == 54.0
    assert payload["service"] == "kpi"
    assert payload["subtask"] == "prime_cost"
    assert len(payload["insights"]) > 0


def test_prime_cost_missing_fields():
    """Test prime cost with missing required fields."""
    payload, code = pc_run({"total_sales": 10000, "labor_cost": 2100})
    assert code == 400
    assert payload["status"] == "error"
    assert "Missing required fields" in payload["error"]


def test_sales_performance_success():
    """Test successful sales performance calculation."""
    payload, code = sp_run({"total_sales": 12000, "hours_open": 48})
    assert code == 200
    assert payload["status"] == "success"
    assert payload["data"]["sales_per_hour"] == 250.0
    assert payload["service"] == "kpi"
    assert payload["subtask"] == "sales_performance"
    assert len(payload["insights"]) > 0


def test_sales_performance_zero_hours():
    """Test sales performance with zero hours."""
    payload, code = sp_run({"total_sales": 12000, "hours_open": 0})
    assert code == 400
    assert payload["status"] == "error"
    assert "must be > 0" in payload["error"]


def test_sales_performance_missing_fields():
    """Test sales performance with missing required fields."""
    payload, code = sp_run({"total_sales": 12000})
    assert code == 400
    assert payload["status"] == "error"
    assert "Missing required fields" in payload["error"]


if __name__ == "__main__":
    # Run tests manually
    test_labor_cost_success()
    test_prime_cost_success()
    test_sales_performance_success()
    print("All tests passed!")
