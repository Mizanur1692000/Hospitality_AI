"""
KPI Sales Performance Analysis Task
Calculates sales performance with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.kpi_utils import calculate_sales_performance_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate sales performance analysis with comprehensive business report.

    Args:
        params: Dictionary containing total_sales, labor_cost, food_cost, and hours_worked
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "kpi", "sales_performance"

    try:
        # Validate required fields
        require(params, ["total_sales", "labor_cost", "food_cost", "hours_worked"])

        # Validate positive numbers
        validate_positive_numbers(params, ["total_sales", "labor_cost", "food_cost", "hours_worked"])

        # Extract and convert values
        total_sales = float(params["total_sales"])
        labor_cost = float(params["labor_cost"])
        food_cost = float(params["food_cost"])
        hours_worked = float(params["hours_worked"])
        previous_sales = float(params["previous_sales"]) if params.get("previous_sales") else None
        
        # Extract optional parameters
        covers = int(params["covers"]) if params.get("covers") is not None else None
        avg_check = float(params["avg_check"]) if params.get("avg_check") is not None else None

        # Validate hours_worked > 0
        if hours_worked <= 0:
            raise ValueError("hours_worked must be > 0")

        # Use comprehensive analysis function
        analysis_result = calculate_sales_performance_analysis(
            total_sales=total_sales,
            labor_cost=labor_cost,
            food_cost=food_cost,
            hours_worked=hours_worked,
            previous_sales=previous_sales,
            covers=covers,
            avg_check=avg_check
        )

        # Check if analysis was successful
        if analysis_result.get("status") == "error":
            return error_payload(service, subtask, analysis_result.get("message", "Analysis failed"))

        # Extract insights from the business report
        insights = analysis_result.get("recommendations", [])

        # Prepare response data
        data = {
            "sales_per_hour": analysis_result["key_metrics"]["sales_per_labor_hour"],
            "total_sales": total_sales,
            "labor_cost": labor_cost,
            "food_cost": food_cost,
            "hours_worked": hours_worked,
            "labor_percent": analysis_result["key_metrics"]["labor_percent"],
            "food_percent": analysis_result["key_metrics"]["food_percent"],
            "prime_percent": analysis_result["key_metrics"]["prime_percent"],
            "performance_rating": analysis_result["performance_rating"],
            "business_report_html": analysis_result["business_report_html"],
            "business_report": analysis_result["business_report"]
        }

        # Add growth data if available
        if previous_sales:
            growth_data = analysis_result.get("additional_insights", {}).get("growth_analysis", {})
            if growth_data:
                data.update({
                    "previous_sales": previous_sales,
                    "sales_growth_percent": growth_data.get("sales_growth_percent"),
                    "sales_growth_amount": growth_data.get("sales_growth_amount"),
                    "growth_trend": growth_data.get("growth_trend")
                })

        return success_payload(service, subtask, params, data, insights), 200

    except ValueError as e:
        return error_payload(service, subtask, str(e))
    except Exception as e:
        return error_payload(service, subtask, f"Internal error: {str(e)}", 500)
