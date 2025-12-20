"""
Sales Forecasting Analysis Task
Analyzes historical trends, seasonal patterns, and growth projections with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from .analysis_functions import calculate_sales_forecasting_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate sales forecasting analysis with comprehensive business report.

    Args:
        params: Dictionary containing sales forecasting metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "strategic", "sales_forecasting"

    try:
        # Validate required fields - at least one sales forecasting metric required
        if not any(key in params for key in ["historical_sales", "current_sales", "growth_rate", "seasonal_factor"]):
            return error_payload(service, subtask, "At least one sales forecasting metric is required")

        # Extract and convert values with defaults
        historical_sales = float(params.get("historical_sales", 0.0))
        current_sales = float(params.get("current_sales", 0.0))
        growth_rate = float(params.get("growth_rate", 0.0))
        seasonal_factor = float(params.get("seasonal_factor", 1.0))

        # Optional parameters
        forecast_periods = float(params.get("forecast_periods", 12.0))
        trend_strength = float(params.get("trend_strength", 0.5))
        market_growth = float(params.get("market_growth", 5.0))
        confidence_level = float(params.get("confidence_level", 85.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "historical_sales": historical_sales,
                "current_sales": current_sales,
                "growth_rate": growth_rate,
                "seasonal_factor": seasonal_factor,
                "forecast_periods": forecast_periods,
                "trend_strength": trend_strength,
                "market_growth": market_growth,
                "confidence_level": confidence_level
            }, [
                "historical_sales", "current_sales", "growth_rate", "seasonal_factor",
                "forecast_periods", "trend_strength", "market_growth", "confidence_level"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_sales_forecasting_analysis(
            historical_sales=historical_sales,
            current_sales=current_sales,
            growth_rate=growth_rate,
            seasonal_factor=seasonal_factor,
            forecast_periods=forecast_periods,
            trend_strength=trend_strength,
            market_growth=market_growth,
            confidence_level=confidence_level
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Sales Forecasting Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
