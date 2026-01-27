"""
KPI Labor Cost Analysis Task
Calculates labor cost percentage and provides comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.kpi_utils import calculate_labor_cost_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate labor cost percentage analysis with comprehensive business report.

    Args:
        params: Dictionary containing total_sales, labor_cost, and hours_worked
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "kpi", "labor_cost"

    try:
        # Validate required fields
        require(params, ["total_sales", "labor_cost", "hours_worked"])

        # Validate positive numbers
        validate_positive_numbers(params, ["total_sales", "labor_cost", "hours_worked"])

        # Extract and convert values
        total_sales = float(params["total_sales"])
        labor_cost = float(params["labor_cost"])
        hours_worked = float(params["hours_worked"])
        target_labor_percent = float(params.get("target_labor_percent", 30.0))
        
        # Extract optional parameters
        overtime_hours = float(params["overtime_hours"]) if params.get("overtime_hours") is not None else None
        covers = int(params["covers"]) if params.get("covers") is not None else None

        # Use comprehensive analysis function
        analysis_result = calculate_labor_cost_analysis(
            total_sales=total_sales,
            labor_cost=labor_cost,
            hours_worked=hours_worked,
            target_labor_percent=target_labor_percent,
            overtime_hours=overtime_hours,
            covers=covers
        )

        # Check if analysis was successful
        if analysis_result.get("status") == "error":
            return error_payload(service, subtask, analysis_result.get("message", "Analysis failed"))

        # Extract insights from the business report
        insights = analysis_result.get("recommendations", [])

        # Prepare response data
        data = {
            "labor_percent": analysis_result["key_metrics"]["labor_percent"],
            "total_sales": total_sales,
            "labor_cost": labor_cost,
            "hours_worked": hours_worked,
            "sales_per_labor_hour": analysis_result["key_metrics"]["sales_per_labor_hour"],
            "cost_per_labor_hour": analysis_result["key_metrics"]["cost_per_labor_hour"],
            "labor_efficiency": analysis_result["performance_rating"],
            "business_report_html": analysis_result["business_report_html"],
            "business_report": analysis_result["business_report"]
        }

        return success_payload(service, subtask, params, data, insights), 200

    except ValueError as e:
        return error_payload(service, subtask, str(e))
    except Exception as e:
        return error_payload(service, subtask, f"Internal error: {str(e)}", 500)
