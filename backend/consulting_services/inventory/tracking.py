"""
Inventory Management Module
Handles stock tracking, ordering, and inventory optimization
"""

from backend.shared.utils.business_report import format_business_insight, format_comprehensive_analysis


def run():
    return {"tool": "Inventory Management", "status": "OK — logic not implemented yet"}


def calculate_inventory_variance(expected_usage, actual_usage):
    """
    Calculate inventory variance with input validation

    Args:
        expected_usage (float): Expected inventory usage
        actual_usage (float): Actual inventory usage

    Returns:
        dict: Variance calculations or error response
    """
    # Input validation
    if expected_usage is None:
        return {"status": "error", "message": "expected_usage cannot be null"}
    if actual_usage is None:
        return {"status": "error", "message": "actual_usage cannot be null"}

    # Check for numeric types
    if not isinstance(expected_usage, (int, float)):
        return {"status": "error", "message": f"expected_usage must be a number, got {type(expected_usage).__name__}"}
    if not isinstance(actual_usage, (int, float)):
        return {"status": "error", "message": f"actual_usage must be a number, got {type(actual_usage).__name__}"}

    # Check for negative values
    if expected_usage < 0:
        return {"status": "error", "message": "expected_usage cannot be negative"}
    if actual_usage < 0:
        return {"status": "error", "message": "actual_usage cannot be negative"}

    # Check for zero expected_usage (division by zero)
    if expected_usage == 0:
        return {"status": "error", "message": "expected_usage cannot be zero"}

    # Perform calculations
    variance = actual_usage - expected_usage
    variance_percent = (variance / expected_usage) * 100

    # Generate business report
    report = format_business_insight(
        title="Inventory Variance Analysis",
        calculation="Variance = Actual Usage - Expected Usage\nVariance % = (Variance / Expected Usage) × 100",
        example=f"Variance = {actual_usage:.2f} - {expected_usage:.2f} = {variance:.2f}\nVariance % = ({variance:.2f} / {expected_usage:.2f}) × 100 = {variance_percent:.2f}%",
        interpretation=_interpret_variance(variance_percent),
        recommendations=_get_variance_recommendations(variance_percent)
    )

    return {
        "status": "success",
        "expected_usage": expected_usage,
        "actual_usage": actual_usage,
        "variance": round(variance, 2),
        "variance_percent": round(variance_percent, 2),
        "business_report": report
    }


def _interpret_variance(variance_percent):
    """Interpret inventory variance percentage"""
    if abs(variance_percent) <= 5:
        return f"A variance of {variance_percent:.1f}% is within acceptable range (±5%). This indicates good inventory control and accurate forecasting."
    elif abs(variance_percent) <= 10:
        return f"A variance of {variance_percent:.1f}% is moderate and requires attention. This suggests some forecasting inaccuracies or operational issues."
    else:
        return f"A variance of {variance_percent:.1f}% is significant and requires immediate action. This indicates major forecasting errors or operational problems."


def _get_variance_recommendations(variance_percent):
    """Get recommendations based on variance percentage"""
    recommendations = []

    if abs(variance_percent) <= 5:
        recommendations.extend([
            "Maintain current inventory management practices",
            "Continue monitoring variance trends",
            "Consider implementing automated reordering systems"
        ])
    elif abs(variance_percent) <= 10:
        recommendations.extend([
            "Review forecasting methods and historical data",
            "Improve communication between kitchen and management",
            "Implement daily inventory tracking",
            "Train staff on proper portion control"
        ])
    else:
        recommendations.extend([
            "Conduct immediate inventory audit",
            "Review and update forecasting algorithms",
            "Implement stricter inventory controls",
            "Investigate potential theft or waste issues",
            "Consider hiring inventory management specialist"
        ])

    return recommendations
