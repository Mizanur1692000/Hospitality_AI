"""
KPI Food Cost Analysis Task
Calculates food cost percentage and provides comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.kpi_utils import calculate_food_cost_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate food cost percentage analysis with comprehensive business report.

    Args:
        params: Dictionary containing total_sales and food_cost
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "kpi", "food_cost"

    try:
        # Validate required fields
        require(params, ["total_sales", "food_cost"])

        # Validate positive numbers
        validate_positive_numbers(params, ["total_sales", "food_cost"])

        # Extract and convert values
        total_sales = float(params["total_sales"])
        food_cost = float(params["food_cost"])
        target_food_percent = float(params.get("target_food_percent", 30.0))
        
        # Extract optional parameters
        waste_cost = float(params["waste_cost"]) if params.get("waste_cost") is not None else None
        covers = int(params["covers"]) if params.get("covers") is not None else None
        beginning_inventory = float(params["beginning_inventory"]) if params.get("beginning_inventory") is not None else None
        ending_inventory = float(params["ending_inventory"]) if params.get("ending_inventory") is not None else None

        # Use comprehensive analysis function
        analysis_result = calculate_food_cost_analysis(
            total_sales=total_sales,
            food_cost=food_cost,
            target_food_percent=target_food_percent,
            waste_cost=waste_cost,
            covers=covers,
            beginning_inventory=beginning_inventory,
            ending_inventory=ending_inventory
        )

        # Check if analysis was successful
        if analysis_result.get("status") == "error":
            return error_payload(service, subtask, analysis_result.get("message", "Analysis failed"))

        # Extract insights from the business report
        insights = analysis_result.get("recommendations", [])

        # Prepare response data
        data = {
            "food_percent": analysis_result["key_metrics"]["food_percent"],
            "total_sales": total_sales,
            "food_cost": food_cost,
            "gross_profit": analysis_result["key_metrics"]["gross_profit"],
            "gross_profit_margin": analysis_result["key_metrics"]["gross_profit_margin"],
            "food_efficiency": analysis_result["performance_rating"],
            "business_report_html": analysis_result["business_report_html"],
            "business_report": analysis_result["business_report"]
        }

        return success_payload(service, subtask, params, data, insights), 200

    except ValueError as e:
        return error_payload(service, subtask, str(e))
    except Exception as e:
        return error_payload(service, subtask, f"Internal error: {str(e)}", 500)
