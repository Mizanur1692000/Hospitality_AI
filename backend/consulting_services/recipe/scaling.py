"""
Recipe Scaling Analysis Task
Analyzes batch size optimization, yield calculations, and consistency maintenance with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from .analysis_functions import calculate_recipe_scaling_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate recipe scaling analysis with comprehensive business report.

    Args:
        params: Dictionary containing recipe scaling metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "recipe", "scaling"

    try:
        # Validate required fields - at least one recipe scaling metric required
        if not any(key in params for key in ["current_batch", "target_batch", "yield_percentage", "consistency_score"]):
            return error_payload(service, subtask, "At least one recipe scaling metric is required")

        # Extract and convert values with defaults
        current_batch = float(params.get("current_batch", 0.0))
        target_batch = float(params.get("target_batch", 0.0))
        yield_percentage = float(params.get("yield_percentage", 0.0))
        consistency_score = float(params.get("consistency_score", 0.0))

        # Optional parameters
        base_recipe_cost = float(params.get("base_recipe_cost", 0.0))
        scaling_factor = float(params.get("scaling_factor", 1.0))
        quality_threshold = float(params.get("quality_threshold", 85.0))
        efficiency_score = float(params.get("efficiency_score", 8.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "current_batch": current_batch,
                "target_batch": target_batch,
                "yield_percentage": yield_percentage,
                "consistency_score": consistency_score,
                "base_recipe_cost": base_recipe_cost,
                "scaling_factor": scaling_factor,
                "quality_threshold": quality_threshold,
                "efficiency_score": efficiency_score
            }, [
                "current_batch", "target_batch", "yield_percentage", "consistency_score",
                "base_recipe_cost", "scaling_factor", "quality_threshold", "efficiency_score"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_recipe_scaling_analysis(
            current_batch=current_batch,
            target_batch=target_batch,
            yield_percentage=yield_percentage,
            consistency_score=consistency_score,
            base_recipe_cost=base_recipe_cost,
            scaling_factor=scaling_factor,
            quality_threshold=quality_threshold,
            efficiency_score=efficiency_score
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Recipe Scaling Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
