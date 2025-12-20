"""Task definitions and mappings for the agent API."""

from __future__ import annotations

from typing import Callable, Dict, Type
from pydantic import BaseModel

from backend.consulting_services.strategy.forecasting import run_forecast
from backend.consulting_services.hr.legacy_human_resources import retention_insights
from backend.consulting_services.inventory.tracking import calculate_inventory_variance
from backend.consulting_services.kpi.kpi_utils import (
    calculate_kpi_summary,
    calculate_labor_cost_analysis,
    calculate_prime_cost_analysis,
    calculate_sales_performance_analysis
)
from backend.consulting_services.kpi.legacy_labor import calculate_labor_cost
from backend.consulting_services.inventory.liquor import calculate_liquor_variance
from backend.consulting_services.menu.legacy_product_mix import generate_pmix_report


class TaskDefinition:
    """Definition for an agent task."""
    
    def __init__(
        self,
        runner: Callable,
        schema: Type[BaseModel],
        requires_entitlement: bool = False,
        description: str = ""
    ):
        self.runner = runner
        self.schema = schema
        self.requires_entitlement = requires_entitlement
        self.description = description


# Pydantic schemas for task validation
class ForecastSchema(BaseModel):
    sales_data: list


class HRRetentionSchema(BaseModel):
    turnover_rate: float
    industry_avg: float = 70.0


class InventoryVarianceSchema(BaseModel):
    expected_usage: float
    actual_usage: float


class LaborCostSchema(BaseModel):
    total_sales: float
    labor_hours: float
    hourly_rate: float


class LiquorVarianceSchema(BaseModel):
    expected_oz: float
    actual_oz: float


class KPISummarySchema(BaseModel):
    total_sales: float
    labor_cost: float
    food_cost: float
    hours_worked: float


class ProductMixSchema(BaseModel):
    items: list


class LaborCostAnalysisSchema(BaseModel):
    total_sales: float
    labor_cost: float
    hours_worked: float
    target_labor_percent: float = 30.0


class PrimeCostAnalysisSchema(BaseModel):
    total_sales: float
    labor_cost: float
    food_cost: float
    target_prime_percent: float = 60.0


class SalesPerformanceAnalysisSchema(BaseModel):
    total_sales: float
    labor_cost: float
    food_cost: float
    hours_worked: float
    previous_sales: float = None


# Task definitions mapping
TASK_DEFINITIONS: Dict[str, TaskDefinition] = {
    "forecast": TaskDefinition(
        runner=lambda data: run_forecast(data.sales_data),
        schema=ForecastSchema,
        requires_entitlement=False,
        description="Generate sales forecast from historical data"
    ),
    "hr_retention": TaskDefinition(
        runner=lambda data: retention_insights(data.turnover_rate, data.industry_avg),
        schema=HRRetentionSchema,
        requires_entitlement=False,
        description="Analyze HR retention metrics"
    ),
    "inventory_variance": TaskDefinition(
        runner=lambda data: calculate_inventory_variance(data.expected_usage, data.actual_usage),
        schema=InventoryVarianceSchema,
        requires_entitlement=False,
        description="Calculate inventory variance analysis"
    ),
    "labor_cost": TaskDefinition(
        runner=lambda data: calculate_labor_cost(data.total_sales, data.labor_hours, data.hourly_rate),
        schema=LaborCostSchema,
        requires_entitlement=False,
        description="Calculate labor cost analysis"
    ),
    "liquor_variance": TaskDefinition(
        runner=lambda data: calculate_liquor_variance(data.expected_oz, data.actual_oz),
        schema=LiquorVarianceSchema,
        requires_entitlement=False,
        description="Calculate liquor variance analysis"
    ),
    "kpi_summary": TaskDefinition(
        runner=lambda data: calculate_kpi_summary(
            total_sales=data.total_sales,
            labor_cost=data.labor_cost,
            food_cost=data.food_cost,
            hours_worked=data.hours_worked,
        ),
        schema=KPISummarySchema,
        requires_entitlement=True,
        description="Generate comprehensive KPI summary"
    ),
    "pmix_report": TaskDefinition(
        runner=lambda data: generate_pmix_report(data.items),
        schema=ProductMixSchema,
        requires_entitlement=False,
        description="Generate product mix analysis report"
    ),
    "labor_cost_analysis": TaskDefinition(
        runner=lambda data: calculate_labor_cost_analysis(
            total_sales=data.total_sales,
            labor_cost=data.labor_cost,
            hours_worked=data.hours_worked,
            target_labor_percent=data.target_labor_percent
        ),
        schema=LaborCostAnalysisSchema,
        requires_entitlement=True,
        description="Advanced labor cost analysis with targets"
    ),
    "prime_cost_analysis": TaskDefinition(
        runner=lambda data: calculate_prime_cost_analysis(
            total_sales=data.total_sales,
            labor_cost=data.labor_cost,
            food_cost=data.food_cost,
            target_prime_percent=data.target_prime_percent
        ),
        schema=PrimeCostAnalysisSchema,
        requires_entitlement=True,
        description="Prime cost analysis with target percentages"
    ),
    "sales_performance_analysis": TaskDefinition(
        runner=lambda data: calculate_sales_performance_analysis(
            total_sales=data.total_sales,
            labor_cost=data.labor_cost,
            food_cost=data.food_cost,
            hours_worked=data.hours_worked,
            previous_sales=data.previous_sales
        ),
        schema=SalesPerformanceAnalysisSchema,
        requires_entitlement=True,
        description="Comprehensive sales performance analysis"
    ),
}
