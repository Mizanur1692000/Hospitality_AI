"""
Comprehensive Analysis Task
Analyzes multiple performance metrics with industry benchmarking and detailed reporting.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.dashboard_analysis import calculate_comprehensive_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate comprehensive analysis with detailed business report.

    Args:
        params: Dictionary containing comprehensive analysis metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "kpi_dashboard", "comprehensive_analysis"

    try:
        # Validate required fields - at least one comprehensive analysis metric required
        if not any(key in params for key in ["total_sales", "labor_cost", "food_cost", "prime_cost"]):
            return error_payload(service, subtask, "At least one comprehensive analysis metric is required")

        # Extract and convert values with defaults
        total_sales = float(params.get("total_sales", 0.0))
        labor_cost = float(params.get("labor_cost", 0.0))
        food_cost = float(params.get("food_cost", 0.0))
        prime_cost = float(params.get("prime_cost", 0.0))

        # Optional parameters
        hours_worked = float(params.get("hours_worked", 0.0))
        hourly_rate = float(params.get("hourly_rate", 0.0))
        previous_sales = float(params.get("previous_sales", 0.0))
        target_margin = float(params.get("target_margin", 70.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "total_sales": total_sales,
                "labor_cost": labor_cost,
                "food_cost": food_cost,
                "prime_cost": prime_cost,
                "hours_worked": hours_worked,
                "hourly_rate": hourly_rate,
                "previous_sales": previous_sales,
                "target_margin": target_margin
            }, [
                "total_sales", "labor_cost", "food_cost", "prime_cost",
                "hours_worked", "hourly_rate", "previous_sales", "target_margin"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_comprehensive_analysis(
            total_sales=total_sales,
            labor_cost=labor_cost,
            food_cost=food_cost,
            prime_cost=prime_cost,
            hours_worked=hours_worked,
            hourly_rate=hourly_rate,
            previous_sales=previous_sales,
            target_margin=target_margin
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Comprehensive Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
