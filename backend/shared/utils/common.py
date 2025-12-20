"""
Common utilities for agent tasks.
Provides standardized response formatting and validation.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, Any, List, Optional


def success_payload(service: str, subtask: str, params: dict, data: dict, insights: Optional[List[str]] = None) -> Dict[str, Any]:
    """Create a standardized success response payload."""
    return {
        "service": service,
        "subtask": subtask,
        "status": "success",
        "params": params,
        "data": data,
        "insights": insights or [],
        "meta": {"version": "1.0.0", "generated_at": datetime.utcnow().isoformat() + "Z"},
    }


def error_payload(service: str, subtask: str, message: str, code: int = 400) -> tuple[Dict[str, Any], int]:
    """Create a standardized error response payload."""
    return ({
        "service": service,
        "subtask": subtask,
        "status": "error",
        "error": message,
        "meta": {"version": "1.0.0", "generated_at": datetime.utcnow().isoformat() + "Z"},
    }, code)


def require(body: dict, fields: List[str]) -> None:
    """Validate that required fields are present in the request body."""
    missing = [f for f in fields if f not in body]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


def validate_positive_numbers(data: dict, fields: List[str]) -> None:
    """Validate that specified fields contain positive numbers."""
    for field in fields:
        if field in data:
            try:
                value = float(data[field])
                if value < 0:
                    raise ValueError(f"{field} must be >= 0")
            except (ValueError, TypeError):
                raise ValueError(f"{field} must be a valid number")


def safe_float(value: Any, field_name: str) -> float:
    """Safely convert a value to float with proper error handling."""
    try:
        return float(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field_name} must be a valid number")
