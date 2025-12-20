"""
Performance Optimization Task
Provides actionable recommendations for improvement with goal setting and progress tracking.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.dashboard_analysis import calculate_performance_optimization


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate performance optimization analysis with actionable recommendations.

    Args:
        params: Dictionary containing performance optimization metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "kpi_dashboard", "performance_optimization"

    try:
        # Validate required fields - at least one performance optimization metric required
        if not any(key in params for key in ["current_performance", "target_performance", "optimization_potential", "efficiency_score"]):
            return error_payload(service, subtask, "At least one performance optimization metric is required")

        # Extract and convert values with defaults
        current_performance = float(params.get("current_performance", 0.0))
        target_performance = float(params.get("target_performance", 0.0))
        optimization_potential = float(params.get("optimization_potential", 0.0))
        efficiency_score = float(params.get("efficiency_score", 0.0))

        # Optional parameters
        baseline_metrics = float(params.get("baseline_metrics", 0.0))
        improvement_rate = float(params.get("improvement_rate", 10.0))
        goal_timeframe = float(params.get("goal_timeframe", 90.0))
        progress_tracking = float(params.get("progress_tracking", 8.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "current_performance": current_performance,
                "target_performance": target_performance,
                "optimization_potential": optimization_potential,
                "efficiency_score": efficiency_score,
                "baseline_metrics": baseline_metrics,
                "improvement_rate": improvement_rate,
                "goal_timeframe": goal_timeframe,
                "progress_tracking": progress_tracking
            }, [
                "current_performance", "target_performance", "optimization_potential", "efficiency_score",
                "baseline_metrics", "improvement_rate", "goal_timeframe", "progress_tracking"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the performance optimization function
        result = calculate_performance_optimization(
            current_performance=current_performance,
            target_performance=target_performance,
            optimization_potential=optimization_potential,
            efficiency_score=efficiency_score,
            baseline_metrics=baseline_metrics,
            improvement_rate=improvement_rate,
            goal_timeframe=goal_timeframe,
            progress_tracking=progress_tracking
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Performance Optimization Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
