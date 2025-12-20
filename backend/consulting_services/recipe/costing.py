"""
Recipe Costing Analysis Task
Analyzes ingredient costs, portion costs, and profit margins with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from .analysis_functions import calculate_recipe_costing_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate recipe costing analysis with comprehensive business report.

    Args:
        params: Dictionary containing recipe costing metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "recipe", "costing"

    try:
        # Validate required fields - at least one recipe costing metric required
        if not any(key in params for key in ["ingredient_cost", "portion_cost", "recipe_price", "total_cost"]):
            return error_payload(service, subtask, "At least one recipe costing metric is required")

        # Extract and convert values with defaults
        ingredient_cost = float(params.get("ingredient_cost", 0.0))
        portion_cost = float(params.get("portion_cost", 0.0))
        recipe_price = float(params.get("recipe_price", 0.0))
        total_cost = float(params.get("total_cost", 0.0))

        # Optional parameters
        portion_size = float(params.get("portion_size", 1.0))
        servings = float(params.get("servings", 1.0))
        target_margin = float(params.get("target_margin", 70.0))
        labor_cost = float(params.get("labor_cost", 0.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "ingredient_cost": ingredient_cost,
                "portion_cost": portion_cost,
                "recipe_price": recipe_price,
                "total_cost": total_cost,
                "portion_size": portion_size,
                "servings": servings,
                "target_margin": target_margin,
                "labor_cost": labor_cost
            }, [
                "ingredient_cost", "portion_cost", "recipe_price", "total_cost",
                "portion_size", "servings", "target_margin", "labor_cost"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_recipe_costing_analysis(
            ingredient_cost=ingredient_cost,
            portion_cost=portion_cost,
            recipe_price=recipe_price,
            total_cost=total_cost,
            portion_size=portion_size,
            servings=servings,
            target_margin=target_margin,
            labor_cost=labor_cost
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Recipe Costing Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
