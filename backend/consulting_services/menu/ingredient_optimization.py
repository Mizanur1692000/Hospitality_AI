"""
Ingredient Optimization Analysis Task
Analyzes supplier costs, waste reduction, and quality consistency with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from .analysis_functions import calculate_ingredient_optimization_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate ingredient optimization analysis with comprehensive business report.

    Args:
        params: Dictionary containing ingredient optimization metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "recipe", "ingredient_optimization"

    try:
        # Validate required fields - at least one ingredient optimization metric required
        if not any(key in params for key in ["current_cost", "supplier_cost", "waste_percentage", "quality_score"]):
            return error_payload(service, subtask, "At least one ingredient optimization metric is required")

        # Extract and convert values with defaults
        current_cost = float(params.get("current_cost", 0.0))
        supplier_cost = float(params.get("supplier_cost", 0.0))
        waste_percentage = float(params.get("waste_percentage", 0.0))
        quality_score = float(params.get("quality_score", 0.0))

        # Optional parameters
        usage_volume = float(params.get("usage_volume", 0.0))
        supplier_count = float(params.get("supplier_count", 1.0))
        consistency_score = float(params.get("consistency_score", 8.0))
        storage_cost = float(params.get("storage_cost", 0.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "current_cost": current_cost,
                "supplier_cost": supplier_cost,
                "waste_percentage": waste_percentage,
                "quality_score": quality_score,
                "usage_volume": usage_volume,
                "supplier_count": supplier_count,
                "consistency_score": consistency_score,
                "storage_cost": storage_cost
            }, [
                "current_cost", "supplier_cost", "waste_percentage", "quality_score",
                "usage_volume", "supplier_count", "consistency_score", "storage_cost"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_ingredient_optimization_analysis(
            current_cost=current_cost,
            supplier_cost=supplier_cost,
            waste_percentage=waste_percentage,
            quality_score=quality_score,
            usage_volume=usage_volume,
            supplier_count=supplier_count,
            consistency_score=consistency_score,
            storage_cost=storage_cost
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Ingredient Optimization Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
