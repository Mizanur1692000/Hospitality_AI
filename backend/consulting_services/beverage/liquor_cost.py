"""
Beverage Liquor Cost Analysis Task
Analyzes liquor costs, variance, and cost per ounce with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.kpi_utils import calculate_liquor_cost_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate liquor cost analysis with comprehensive business report.

    Args:
        params: Dictionary containing liquor cost metrics and optional targets
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "beverage", "liquor_cost"

    try:
        # Validate required fields - at least one metric required
        if not any(key in params for key in ["expected_oz", "actual_oz", "liquor_cost", "total_sales"]):
            return error_payload(service, subtask, "At least one liquor cost metric is required")

        # Extract and convert values with defaults
        expected_oz = float(params.get("expected_oz", 0.0))
        actual_oz = float(params.get("actual_oz", 0.0))
        liquor_cost = float(params.get("liquor_cost", 0.0))
        total_sales = float(params.get("total_sales", 0.0))

        # Optional parameters
        bottle_cost = float(params.get("bottle_cost", 0.0))
        bottle_size_oz = float(params.get("bottle_size_oz", 25.0))  # Standard 750ml bottle
        target_cost_percentage = float(params.get("target_cost_percentage", 20.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "expected_oz": expected_oz,
                "actual_oz": actual_oz,
                "liquor_cost": liquor_cost,
                "total_sales": total_sales,
                "bottle_cost": bottle_cost,
                "bottle_size_oz": bottle_size_oz,
                "target_cost_percentage": target_cost_percentage
            }, [
                "expected_oz", "actual_oz", "liquor_cost", "total_sales",
                "bottle_cost", "bottle_size_oz", "target_cost_percentage"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_liquor_cost_analysis(
            expected_oz=expected_oz,
            actual_oz=actual_oz,
            liquor_cost=liquor_cost,
            total_sales=total_sales,
            bottle_cost=bottle_cost,
            bottle_size_oz=bottle_size_oz,
            target_cost_percentage=target_cost_percentage
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Liquor Cost Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
