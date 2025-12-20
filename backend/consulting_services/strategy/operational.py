"""
Operational Excellence Analysis Task
Analyzes process optimization, efficiency metrics, and best practices with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from .analysis_functions import calculate_operational_excellence_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate operational excellence analysis with comprehensive business report.

    Args:
        params: Dictionary containing operational excellence metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "strategic", "operational_excellence"

    try:
        # Validate required fields - at least one operational excellence metric required
        if not any(key in params for key in ["efficiency_score", "process_time", "quality_rating", "customer_satisfaction"]):
            return error_payload(service, subtask, "At least one operational excellence metric is required")

        # Extract and convert values with defaults
        efficiency_score = float(params.get("efficiency_score", 0.0))
        process_time = float(params.get("process_time", 0.0))
        quality_rating = float(params.get("quality_rating", 0.0))
        customer_satisfaction = float(params.get("customer_satisfaction", 0.0))

        # Optional parameters
        cost_per_unit = float(params.get("cost_per_unit", 0.0))
        waste_percentage = float(params.get("waste_percentage", 0.0))
        employee_productivity = float(params.get("employee_productivity", 8.0))
        benchmark_score = float(params.get("benchmark_score", 85.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "efficiency_score": efficiency_score,
                "process_time": process_time,
                "quality_rating": quality_rating,
                "customer_satisfaction": customer_satisfaction,
                "cost_per_unit": cost_per_unit,
                "waste_percentage": waste_percentage,
                "employee_productivity": employee_productivity,
                "benchmark_score": benchmark_score
            }, [
                "efficiency_score", "process_time", "quality_rating", "customer_satisfaction",
                "cost_per_unit", "waste_percentage", "employee_productivity", "benchmark_score"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_operational_excellence_analysis(
            efficiency_score=efficiency_score,
            process_time=process_time,
            quality_rating=quality_rating,
            customer_satisfaction=customer_satisfaction,
            cost_per_unit=cost_per_unit,
            waste_percentage=waste_percentage,
            employee_productivity=employee_productivity,
            benchmark_score=benchmark_score
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Operational Excellence Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
