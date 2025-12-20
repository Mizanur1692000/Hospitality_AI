"""
Growth Strategy Analysis Task
Analyzes market opportunities, competitive positioning, and investment planning with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from .analysis_functions import calculate_growth_strategy_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate growth strategy analysis with comprehensive business report.

    Args:
        params: Dictionary containing growth strategy metrics
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "strategic", "growth_strategy"

    try:
        # Validate required fields - at least one growth strategy metric required
        if not any(key in params for key in ["market_size", "market_share", "competition_level", "investment_budget"]):
            return error_payload(service, subtask, "At least one growth strategy metric is required")

        # Extract and convert values with defaults
        market_size = float(params.get("market_size", 0.0))
        market_share = float(params.get("market_share", 0.0))
        competition_level = float(params.get("competition_level", 0.0))
        investment_budget = float(params.get("investment_budget", 0.0))

        # Optional parameters
        growth_potential = float(params.get("growth_potential", 15.0))
        competitive_advantage = float(params.get("competitive_advantage", 7.0))
        market_penetration = float(params.get("market_penetration", 5.0))
        roi_target = float(params.get("roi_target", 20.0))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "market_size": market_size,
                "market_share": market_share,
                "competition_level": competition_level,
                "investment_budget": investment_budget,
                "growth_potential": growth_potential,
                "competitive_advantage": competitive_advantage,
                "market_penetration": market_penetration,
                "roi_target": roi_target
            }, [
                "market_size", "market_share", "competition_level", "investment_budget",
                "growth_potential", "competitive_advantage", "market_penetration", "roi_target"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_growth_strategy_analysis(
            market_size=market_size,
            market_share=market_share,
            competition_level=competition_level,
            investment_budget=investment_budget,
            growth_potential=growth_potential,
            competitive_advantage=competitive_advantage,
            market_penetration=market_penetration,
            roi_target=roi_target
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Growth Strategy Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
