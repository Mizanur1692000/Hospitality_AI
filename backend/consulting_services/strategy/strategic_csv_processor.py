"""
Strategic Planning CSV Processors
Handles business goals and sales forecasting CSV uploads.
"""
from typing import Any, Dict
import pandas as pd

from backend.consulting_services.kpi.kpi_utils import format_business_report
from backend.consulting_services.strategy.analysis_functions import (
    calculate_sales_forecasting_analysis,
    calculate_growth_strategy_analysis,
    calculate_operational_excellence_analysis,
)


def _clean_numeric(value) -> float:
    if value is None:
        return 0.0
    try:
        if isinstance(value, float) and pd.isna(value):
            return 0.0
    except Exception:
        pass
    if isinstance(value, str):
        s = value.strip().replace("$", "").replace("%", "").replace(",", "")
        if s == "" or s.lower() == "nan":
            return 0.0
        try:
            return float(s)
        except ValueError:
            return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _mean_or_default(series, default_value: float) -> float:
    if series is None:
        return default_value
    try:
        cleaned = series.apply(_clean_numeric)
        mean_value = cleaned.mean()
        if pd.isna(mean_value):
            return default_value
        return float(mean_value)
    except Exception:
        return default_value


def process_business_goals_csv_data(csv_file) -> Dict[str, Any]:
    """Process business goals CSV into a strategic planning report."""
    try:
        df = pd.read_csv(csv_file)
        actual_cols = [c.strip() for c in df.columns]
        df.columns = actual_cols

        required = ["revenue_target", "budget_total"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            return {
                "status": "error",
                "message": f"Missing required columns: {', '.join(missing)}",
                "your_columns": actual_cols,
                "help": "CSV must include: revenue_target, budget_total. Optional: marketing_spend, target_roi, timeline_months, acquisition_cost, conversion_rate"
            }

        # Use first row as summary inputs
        row = df.iloc[0]
        revenue_target = _clean_numeric(row.get("revenue_target"))
        budget_total = _clean_numeric(row.get("budget_total"))
        marketing_spend = _clean_numeric(row.get("marketing_spend"))
        target_roi = _clean_numeric(row.get("target_roi")) or 20.0
        timeline_months = int(_clean_numeric(row.get("timeline_months")) or 12)
        acquisition_cost = _clean_numeric(row.get("acquisition_cost"))
        conversion_rate = _clean_numeric(row.get("conversion_rate"))

        total_spend = budget_total + marketing_spend
        projected_net = revenue_target - total_spend
        roi_achieved = (projected_net / total_spend * 100) if total_spend > 0 else 0.0

        performance = {
            "rating": "Good" if roi_achieved >= target_roi else "Needs Improvement",
            "color": "green" if roi_achieved >= target_roi else "orange"
        }

        metrics = {
            "Revenue Target": revenue_target,
            "Budget Total": budget_total,
            "Marketing Spend": marketing_spend,
            "Target ROI": target_roi,
            "Timeline (Months)": timeline_months,
            "Projected Net": projected_net,
            "ROI Achieved": roi_achieved
        }
        if acquisition_cost:
            metrics["Acquisition Cost"] = acquisition_cost
        if conversion_rate:
            metrics["Conversion Rate"] = conversion_rate

        recommendations = []
        if roi_achieved < target_roi:
            recommendations.append("Increase revenue target or reduce total spend to hit ROI goal")
        if marketing_spend > 0 and total_spend > 0 and (marketing_spend / total_spend) > 0.5:
            recommendations.append("Rebalance spend so marketing is not more than 50% of total budget")
        if revenue_target < total_spend:
            recommendations.append("Revenue target is below total spend; revisit pricing or volume assumptions")
        if not recommendations:
            recommendations.append("Goals look balanced. Track monthly progress and adjust budgets quarterly")

        additional_data = {
            "Total Spend": total_spend,
            "Timeline": f"{timeline_months} months"
        }

        report = format_business_report(
            analysis_type="Business Goals Analysis",
            metrics=metrics,
            performance=performance,
            recommendations=recommendations,
            benchmarks=None,
            additional_data=additional_data
        )

        return {
            "status": "success",
            "analysis_type": report.get("analysis_type"),
            "business_report": report.get("business_report"),
            "business_report_html": report.get("business_report_html"),
            "metrics": metrics,
            "recommendations": recommendations
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "traceback": traceback.format_exc() if hasattr(traceback, "format_exc") else None
        }


def process_sales_forecasting_csv_data(csv_file) -> Dict[str, Any]:
    """Process sales forecasting CSV into a strategic planning report."""
    try:
        df = pd.read_csv(csv_file)
        actual_cols = [c.strip() for c in df.columns]
        df.columns = actual_cols

        required = ["historical_sales", "current_sales", "growth_rate", "seasonal_factor"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            return {
                "status": "error",
                "message": f"Missing required columns: {', '.join(missing)}",
                "your_columns": actual_cols,
                "help": "CSV must include: historical_sales, current_sales, growth_rate, seasonal_factor. Optional: forecast_periods, trend_strength, market_growth, confidence_level"
            }

        row = df.iloc[0]
        historical_sales = _clean_numeric(row.get("historical_sales"))
        current_sales = _clean_numeric(row.get("current_sales"))
        growth_rate = _clean_numeric(row.get("growth_rate"))
        seasonal_factor = _clean_numeric(row.get("seasonal_factor")) or 1.0
        forecast_periods = _clean_numeric(row.get("forecast_periods") or row.get("forecast_period")) or 12.0
        trend_strength = _clean_numeric(row.get("trend_strength")) or 0.5
        market_growth = _clean_numeric(row.get("market_growth")) or 5.0
        confidence_level = _clean_numeric(row.get("confidence_level")) or 85.0

        report = calculate_sales_forecasting_analysis(
            historical_sales=historical_sales,
            current_sales=current_sales,
            growth_rate=growth_rate,
            seasonal_factor=seasonal_factor,
            forecast_periods=forecast_periods,
            trend_strength=trend_strength,
            market_growth=market_growth,
            confidence_level=confidence_level
        )

        return {
            "status": "success",
            "analysis_type": "Sales Forecasting Analysis",
            "business_report": report.get("business_report"),
            "business_report_html": report.get("business_report_html"),
            "metrics": report.get("metrics"),
            "recommendations": report.get("recommendations"),
            "performance": report.get("performance")
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "traceback": traceback.format_exc() if hasattr(traceback, "format_exc") else None
        }


def process_growth_strategy_csv_data(csv_file) -> Dict[str, Any]:
    """Process growth strategy CSV into a strategic planning report."""
    try:
        df = pd.read_csv(csv_file)
        actual_cols = [c.strip() for c in df.columns]
        df.columns = actual_cols

        required_any = [
            "market_size",
            "market_share",
            "competition_level",
            "investment_budget",
            "growth_potential",
            "market_penetration",
            "target_roi",
            "roi_target",
        ]
        if not any(col in df.columns for col in required_any):
            return {
                "status": "error",
                "message": "Missing required columns: at least one growth strategy metric is required",
                "your_columns": actual_cols,
                "help": "CSV must include at least one of: market_size, market_share, competition_level, investment_budget, growth_potential, market_penetration, target_roi"
            }

        market_size = _mean_or_default(df.get("market_size"), 0.0)
        market_share = _mean_or_default(df.get("market_share"), 0.0)
        competition_level = _mean_or_default(df.get("competition_level"), 0.0)
        investment_budget = _mean_or_default(df.get("investment_budget"), 0.0)
        growth_potential = _mean_or_default(df.get("growth_potential"), 15.0)
        market_penetration = _mean_or_default(df.get("market_penetration"), 5.0)
        roi_target = _mean_or_default(df.get("roi_target"), 0.0)
        if roi_target == 0.0:
            roi_target = _mean_or_default(df.get("target_roi"), 20.0)
        competitive_advantage = _mean_or_default(df.get("competitive_advantage"), 7.0)

        report = calculate_growth_strategy_analysis(
            market_size=market_size,
            market_share=market_share,
            competition_level=competition_level,
            investment_budget=investment_budget,
            growth_potential=growth_potential,
            competitive_advantage=competitive_advantage,
            market_penetration=market_penetration,
            roi_target=roi_target
        )

        return {
            "status": "success",
            "analysis_type": "Growth Strategy Analysis",
            "business_report": report.get("business_report"),
            "business_report_html": report.get("business_report_html"),
            "metrics": report.get("metrics"),
            "recommendations": report.get("recommendations"),
            "performance": report.get("performance")
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "traceback": traceback.format_exc() if hasattr(traceback, "format_exc") else None
        }


def process_operational_excellence_csv_data(csv_file) -> Dict[str, Any]:
    """Process operational excellence CSV into a strategic planning report."""
    try:
        df = pd.read_csv(csv_file)
        actual_cols = [c.strip() for c in df.columns]
        df.columns = actual_cols

        required_any = [
            "efficiency_score",
            "process_time",
            "quality_rating",
            "customer_satisfaction",
            "cost_per_unit",
            "waste_percentage",
            "productivity_score",
            "industry_benchmark",
        ]
        if not any(col in df.columns for col in required_any):
            return {
                "status": "error",
                "message": "Missing required columns: at least one operational excellence metric is required",
                "your_columns": actual_cols,
                "help": "CSV must include at least one of: efficiency_score, process_time, quality_rating, customer_satisfaction, cost_per_unit, waste_percentage"
            }

        efficiency_score = _mean_or_default(df.get("efficiency_score"), 0.0)
        process_time = _mean_or_default(df.get("process_time"), 0.0)
        quality_rating = _mean_or_default(df.get("quality_rating"), 0.0)
        customer_satisfaction = _mean_or_default(df.get("customer_satisfaction"), 0.0)
        cost_per_unit = _mean_or_default(df.get("cost_per_unit"), 0.0)
        waste_percentage = _mean_or_default(df.get("waste_percentage"), 0.0)
        employee_productivity = _mean_or_default(df.get("employee_productivity"), 0.0)
        if employee_productivity == 0.0:
            employee_productivity = _mean_or_default(df.get("productivity_score"), 8.0)
        benchmark_score = _mean_or_default(df.get("benchmark_score"), 0.0)
        if benchmark_score == 0.0:
            benchmark_score = _mean_or_default(df.get("industry_benchmark"), 85.0)

        report = calculate_operational_excellence_analysis(
            efficiency_score=efficiency_score,
            process_time=process_time,
            quality_rating=quality_rating,
            customer_satisfaction=customer_satisfaction,
            cost_per_unit=cost_per_unit,
            waste_percentage=waste_percentage,
            employee_productivity=employee_productivity,
            benchmark_score=benchmark_score
        )

        return {
            "status": "success",
            "analysis_type": "Operational Excellence Analysis",
            "business_report": report.get("business_report"),
            "business_report_html": report.get("business_report_html"),
            "metrics": report.get("metrics"),
            "recommendations": report.get("recommendations"),
            "performance": report.get("performance")
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"CSV processing error: {str(e)}",
            "traceback": traceback.format_exc() if hasattr(traceback, "format_exc") else None
        }
