"""
Beverage Inventory Management Task
Analyzes bar inventory, stock levels, and reorder optimization with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.kpi_utils import calculate_inventory_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate inventory analysis with comprehensive business report.

    Args:
        params: Dictionary containing inventory metrics and optional targets
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "beverage", "inventory"

    try:
        # Validate required fields - at least one metric required
        if not any(key in params for key in ["current_stock", "reorder_point", "monthly_usage", "inventory_value"]):
            return error_payload(service, subtask, "At least one inventory metric is required")

        # Extract and convert values with defaults
        current_stock = float(params.get("current_stock", 0.0))
        reorder_point = float(params.get("reorder_point", 0.0))
        monthly_usage = float(params.get("monthly_usage", 0.0))
        inventory_value = float(params.get("inventory_value", 0.0))

        # Optional parameters
        lead_time_days = float(params.get("lead_time_days", 7.0))
        safety_stock = float(params.get("safety_stock", 0.0))
        item_cost = float(params.get("item_cost", 0.0))
        target_turnover = float(params.get("target_turnover", 12.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "current_stock": current_stock,
                "reorder_point": reorder_point,
                "monthly_usage": monthly_usage,
                "inventory_value": inventory_value,
                "lead_time_days": lead_time_days,
                "safety_stock": safety_stock,
                "item_cost": item_cost,
                "target_turnover": target_turnover
            }, [
                "current_stock", "reorder_point", "monthly_usage", "inventory_value",
                "lead_time_days", "safety_stock", "item_cost", "target_turnover"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_inventory_analysis(
            current_stock=current_stock,
            reorder_point=reorder_point,
            monthly_usage=monthly_usage,
            inventory_value=inventory_value,
            lead_time_days=lead_time_days,
            safety_stock=safety_stock,
            item_cost=item_cost,
            target_turnover=target_turnover
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Bar Inventory Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
