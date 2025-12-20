"""Pydantic schemas for KPI analysis services."""

from __future__ import annotations

from typing import List, Literal

from pydantic import BaseModel, Field, FieldValidationInfo, field_validator


class InputPrimeCost(BaseModel):
    """Validate the prime cost task payload.

    Examples:
        >>> InputPrimeCost(
        ...     labor_costs=18432.50,
        ...     food_costs=26341.70,
        ...     total_sales=83215.90,
        ... )
        InputPrimeCost(labor_costs=18432.5, food_costs=26341.7, total_sales=83215.9, industry_benchmark_pct=0.6)
    """

    labor_costs: float = Field(..., description="Total labor costs for the reporting window.")
    food_costs: float = Field(..., description="Total food costs for the reporting window.")
    total_sales: float = Field(..., description="Total net sales for the reporting window.")
    industry_benchmark_pct: float = Field(
        0.60,
        description="Benchmark ratio used for comparison.",
    )

    class Config:
        extra = "forbid"

    @field_validator("labor_costs", "food_costs")
    @classmethod
    def _validate_non_negative(cls, value: float, info: FieldValidationInfo) -> float:
        """Ensure that cost inputs are non-negative.

        Examples:
            >>> InputPrimeCost(labor_costs=0.0, food_costs=10.0, total_sales=100.0).labor_costs
            0.0
        """

        if value < 0:
            field_name = getattr(info, "field_name", "value")
            raise ValueError(f"{field_name} must be greater than or equal to zero.")
        return value

    @field_validator("total_sales")
    @classmethod
    def _validate_total_sales(cls, value: float) -> float:
        """Ensure sales are positive to avoid division by zero.

        Examples:
            >>> InputPrimeCost(labor_costs=0.0, food_costs=0.0, total_sales=100.0).total_sales
            100.0
        """

        if value <= 0:
            raise ValueError("total_sales must be greater than zero to compute percentages.")
        return value

    @field_validator("industry_benchmark_pct")
    @classmethod
    def _validate_benchmark(cls, value: float) -> float:
        """Validate that the benchmark ratio sits within the unit interval.

        Examples:
            >>> InputPrimeCost(
            ...     labor_costs=0.0,
            ...     food_costs=0.0,
            ...     total_sales=100.0,
            ...     industry_benchmark_pct=0.55,
            ... ).industry_benchmark_pct
            0.55
        """

        if not 0 <= value <= 1:
            raise ValueError("industry_benchmark_pct must be between 0 and 1 inclusive.")
        return value


class Metric(BaseModel):
    """Metric entry for the response payload.

    Examples:
        >>> Metric(name="Prime Cost %", value=0.55, unit="ratio")
        Metric(name='Prime Cost %', value=0.55, unit='ratio')
    """

    name: str
    value: float
    unit: str

    class Config:
        extra = "forbid"


class TableRow(BaseModel):
    """Tabular representation of component costs.

    Examples:
        >>> TableRow(component="Labor", amount=18432.5, pct_sales=0.22)
        TableRow(component='Labor', amount=18432.5, pct_sales=0.22)
    """

    component: str
    amount: float
    pct_sales: float

    class Config:
        extra = "forbid"


class Diagnostics(BaseModel):
    """Diagnostic metadata accompanying the KPI analysis response.

    Examples:
        >>> Diagnostics(benchmark=0.6, recommendations=["Monitor"], timing_ms=0)
        Diagnostics(benchmark=0.6, recommendations=['Monitor'], timing_ms=0)
    """

    benchmark: float
    recommendations: List[str]
    timing_ms: int

    class Config:
        extra = "forbid"


class OutputPrimeCost(BaseModel):
    """Canonical output schema for the prime cost KPI analysis task.

    Examples:
        >>> OutputPrimeCost(
        ...     status="ok",
        ...     summary="Prime cost is 55.0% of sales, below the 60.0% benchmark.",
        ...     metrics=[Metric(name="Prime Cost %", value=0.55, unit="ratio")],
        ...     table=[TableRow(component="Prime", amount=1000.0, pct_sales=0.55)],
        ...     diagnostics=Diagnostics(benchmark=0.6, recommendations=["Monitor"], timing_ms=0),
        ... )
        OutputPrimeCost(status='ok', summary='Prime cost is 55.0% of sales, below the 60.0% benchmark.', metrics=[Metric(name='Prime Cost %', value=0.55, unit='ratio')], table=[TableRow(component='Prime', amount=1000.0, pct_sales=0.55)], diagnostics=Diagnostics(benchmark=0.6, recommendations=['Monitor'], timing_ms=0))
    """

    status: Literal["ok", "error", "locked"]
    summary: str
    metrics: List[Metric]
    table: List[TableRow]
    diagnostics: Diagnostics

    class Config:
        extra = "forbid"
