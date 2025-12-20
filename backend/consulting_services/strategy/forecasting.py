"""
Sales Forecasting Module
Handles sales predictions, demand forecasting, and revenue projections
"""

from backend.shared.utils.response import success_response


def run():
    forecast = [1000, 1100, 1050]
    return success_response("Sales Forecasting", {"forecast": forecast})


def run_forecast(sales_data):
    """
    Run forecasting analysis on provided sales data with input validation

    Args:
        sales_data (list): List of sales data points

    Returns:
        dict: Forecasting results or error response
    """
    # Input validation
    if not sales_data:
        return {"status": "error", "message": "No sales data provided"}

    if not isinstance(sales_data, list):
        return {"status": "error", "message": "sales_data must be a list"}

    if len(sales_data) == 0:
        return {"status": "error", "message": "sales_data cannot be empty"}

    # Validate each data point
    numeric_data = []
    for i, value in enumerate(sales_data):
        if value is None:
            return {"status": "error", "message": f"sales_data[{i}] cannot be null"}

        if not isinstance(value, (int, float)):
            return {"status": "error", "message": f"sales_data[{i}] must be a number, got {type(value).__name__}"}

        if value < 0:
            return {"status": "error", "message": f"sales_data[{i}] cannot be negative"}

        numeric_data.append(float(value))

    # Simple forecasting logic (placeholder)
    try:
        avg_sales = sum(numeric_data) / len(numeric_data)
        forecast_values = [round(avg_sales * 1.1, 2), round(avg_sales * 1.15, 2), round(avg_sales * 1.2, 2)]

        return {
            "status": "success",
            "forecast": forecast_values,
            "data_points": len(numeric_data),
            "method": "average_based",
            "average_sales": round(avg_sales, 2),
        }
    except Exception as e:
        return {"status": "error", "message": f"Calculation error: {str(e)}"}
