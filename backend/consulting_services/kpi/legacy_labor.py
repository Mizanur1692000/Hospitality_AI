"""
Labor Management Module
Handles staff scheduling, workforce planning, and labor optimization
"""

from backend.shared.utils.business_report import format_business_insight, format_comprehensive_analysis


def run():
    return {"tool": "Labor Management", "status": "OK — logic not implemented yet"}


def calculate_labor_cost(total_sales, labor_hours, hourly_rate):
    """
    Calculate labor cost analysis with input validation

    Args:
        total_sales (float): Total sales revenue
        labor_hours (float): Total labor hours worked
        hourly_rate (float): Hourly wage rate

    Returns:
        dict: Labor cost calculations or error response with both text and HTML reports
    """
    # Input validation
    inputs = {"total_sales": total_sales, "labor_hours": labor_hours, "hourly_rate": hourly_rate}

    # Check for None values
    for name, value in inputs.items():
        if value is None:
            return {"status": "error", "message": f"{name} cannot be null"}

    # Check for numeric types
    for name, value in inputs.items():
        if not isinstance(value, (int, float)):
            return {"status": "error", "message": f"{name} must be a number, got {type(value).__name__}"}

    # Check for negative values
    for name, value in inputs.items():
        if value < 0:
            return {"status": "error", "message": f"{name} cannot be negative"}

    # Check for zero values where division occurs
    if total_sales == 0:
        return {"status": "error", "message": "total_sales cannot be zero"}

    # Perform calculations
    total_labor_cost = labor_hours * hourly_rate
    labor_percent = (total_labor_cost / total_sales) * 100

    # Calculate productivity
    productivity = total_sales / labor_hours if labor_hours > 0 else 0

    # Generate formatted business report (now returns dict with text and html)
    report_result = format_comprehensive_analysis('labor', {
        'labor_costs': total_labor_cost,
        'total_sales': total_sales,
        'labor_hours': labor_hours
    })

    return {
        "status": "success",
        "total_sales": total_sales,
        "labor_hours": labor_hours,
        "hourly_rate": hourly_rate,
        "total_labor_cost": round(total_labor_cost, 2),
        "labor_percent": round(labor_percent, 2),
        "productivity": round(productivity, 2),
        "business_report": report_result.get("text", "") if isinstance(report_result, dict) else report_result,
        "business_report_html": report_result.get("html", "") if isinstance(report_result, dict) else ""
    }
