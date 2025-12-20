"""
Response Utility Functions
Provides consistent response formatting for all agent tools
"""


def success_response(tool_name, data):
    """
    Create a standardized success response

    Args:
        tool_name (str): Name of the tool that was executed
        data (dict): The results/data from the tool

    Returns:
        dict: Standardized success response
    """
    return {"tool": tool_name, "status": "success", "results": data}


def error_response(message):
    """
    Create a standardized error response

    Args:
        message (str): Error message to return

    Returns:
        dict: Standardized error response
    """
    return {"status": "error", "message": message}


def pending_response(tool_name):
    """
    Create a response for tools that are not yet implemented

    Args:
        tool_name (str): Name of the tool

    Returns:
        dict: Standardized pending response
    """
    return {"tool": tool_name, "status": "pending", "message": "Tool logic not implemented yet"}
