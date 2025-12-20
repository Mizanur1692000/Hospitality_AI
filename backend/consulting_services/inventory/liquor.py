"""
Liquor Cost Module
Handles liquor inventory, cost tracking, and bar management
"""


def run():
    return {"tool": "Liquor Management", "status": "OK — logic not implemented yet"}


def calculate_liquor_variance(expected_oz, actual_oz):
    """
    Calculate liquor variance with input validation

    Args:
        expected_oz (float): Expected liquor usage in ounces
        actual_oz (float): Actual liquor usage in ounces

    Returns:
        dict: Variance calculations or error response
    """
    # Input validation
    if expected_oz is None:
        return {"status": "error", "message": "expected_oz cannot be null"}
    if actual_oz is None:
        return {"status": "error", "message": "actual_oz cannot be null"}

    # Check for numeric types
    if not isinstance(expected_oz, (int, float)):
        return {"status": "error", "message": f"expected_oz must be a number, got {type(expected_oz).__name__}"}
    if not isinstance(actual_oz, (int, float)):
        return {"status": "error", "message": f"actual_oz must be a number, got {type(actual_oz).__name__}"}

    # Check for negative values
    if expected_oz < 0:
        return {"status": "error", "message": "expected_oz cannot be negative"}
    if actual_oz < 0:
        return {"status": "error", "message": "actual_oz cannot be negative"}

    # Check for zero expected_oz (division by zero)
    if expected_oz == 0:
        return {"status": "error", "message": "expected_oz cannot be zero"}

    # Perform calculations
    variance = actual_oz - expected_oz
    variance_percent = (variance / expected_oz) * 100

    return {
        "status": "success",
        "expected_oz": expected_oz,
        "actual_oz": actual_oz,
        "variance_oz": round(variance, 2),
        "variance_percent": round(variance_percent, 2),
    }
