"""
Beverage Pricing Analysis Task
Analyzes drink pricing, margins, and profitability optimization with comprehensive business report.
"""

from backend.shared.utils.common import success_payload, error_payload, require, validate_positive_numbers
from backend.consulting_services.kpi.kpi_utils import calculate_pricing_analysis


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate pricing analysis with comprehensive business report.

    Args:
        params: Dictionary containing pricing metrics and optional targets
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "beverage", "pricing"

    try:
        # Validate required fields - at least one metric required
        if not any(key in params for key in ["drink_price", "cost_per_drink", "sales_volume", "competitor_price"]):
            return error_payload(service, subtask, "At least one pricing metric is required")

        # Extract and convert values with defaults
        drink_price = float(params.get("drink_price", 0.0))
        cost_per_drink = float(params.get("cost_per_drink", 0.0))
        sales_volume = float(params.get("sales_volume", 0.0))
        competitor_price = float(params.get("competitor_price", 0.0))

        # Optional parameters
        target_margin = float(params.get("target_margin", 75.0))
        market_position = params.get("market_position", "premium")
        elasticity_factor = float(params.get("elasticity_factor", 1.5))

        # Validate positive numbers
        try:
            validate_positive_numbers({
                "drink_price": drink_price,
                "cost_per_drink": cost_per_drink,
                "sales_volume": sales_volume,
                "competitor_price": competitor_price,
                "target_margin": target_margin,
                "elasticity_factor": elasticity_factor
            }, [
                "drink_price", "cost_per_drink", "sales_volume", "competitor_price",
                "target_margin", "elasticity_factor"
            ])
        except ValueError as e:
            return error_payload(service, subtask, str(e))

        # Call the comprehensive analysis function
        result = calculate_pricing_analysis(
            drink_price=drink_price,
            cost_per_drink=cost_per_drink,
            sales_volume=sales_volume,
            competitor_price=competitor_price,
            target_margin=target_margin,
            market_position=market_position,
            elasticity_factor=elasticity_factor
        )

        # Extract business reports from result
        business_report_html = result.get("business_report_html", "")
        business_report = result.get("business_report", "")

        return success_payload(
            service, subtask, params, {
                "analysis_type": "Beverage Pricing Analysis",
                "business_report_html": business_report_html,
                "business_report": business_report,
                "metrics": result.get("metrics", {}),
                "performance": result.get("performance", {}),
                "recommendations": result.get("recommendations", [])
            }, result.get("recommendations", [])
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Analysis failed: {str(e)}")
