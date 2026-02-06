"""Unified JSON API endpoint for agent tasks with entitlement enforcement."""

from __future__ import annotations

import functools
import json
import logging
from enum import Enum
from http import HTTPStatus
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pydantic import ValidationError

from apps.agent_core.task_map import TASK_DEFINITIONS, TaskDefinition

logger = logging.getLogger(__name__)


# Constants
ENTITLEMENT_HEADER = "X-KPI-Analysis-Entitled"
_TRUTHY_VALUES = {"1", "true", "yes", "allowed"}


class ErrorCodes(str, Enum):
    """Standard error codes for API responses."""
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    INVALID_INPUT = "INVALID_INPUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    LOCKED = "LOCKED"
    INVALID_JSON = "INVALID_JSON"
    MISSING_TASK = "MISSING_TASK"
    UNKNOWN_TASK = "UNKNOWN_TASK"
    INVALID_PAYLOAD = "INVALID_PAYLOAD"
    VALIDATION_FAILED = "VALIDATION_FAILED"


class ErrorMessages(str, Enum):
    """Standard error messages for API responses."""
    POST_ONLY = "Only POST method allowed."
    INVALID_JSON = "Invalid JSON payload."
    TASK_REQUIRED = '"task" is required and must be a string.'
    PAYLOAD_MUST_BE_OBJECT = '"payload" must be an object.'
    UPGRADE_REQUIRED = "Upgrade to unlock KPI Analysis."
    UNEXPECTED_ERROR = "Unexpected error."
    VALIDATION_FAILED = "Payload validation failed."
    INVALID_RESPONSE = "Task returned invalid response type."


def build_error_response(
    code: ErrorCodes,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status: HTTPStatus = HTTPStatus.BAD_REQUEST,
    trace_id: Optional[str] = None
) -> JsonResponse:
    """Build a standardized error response.

    Args:
        code: Error code from ErrorCodes enum
        message: Human-readable error message
        details: Optional additional error details
        status: HTTP status code
        trace_id: Optional trace ID for error tracking

    Returns:
        JsonResponse with standardized error format
    """
    response_data: Dict[str, Any] = {
        "code": code.value,
        "message": message
    }

    if details:
        response_data["details"] = details

    if trace_id:
        response_data["trace_id"] = trace_id

    # For backwards compatibility with some responses expecting "status" field
    if code == ErrorCodes.LOCKED:
        response_data["status"] = "locked"

    return JsonResponse(response_data, status=status)


def require_post_json(view_func: Callable) -> Callable:
    """Decorator to ensure POST method with valid JSON.

    This decorator:
    - Validates the request method is POST
    - Parses JSON body and attaches it to request.json
    - Returns appropriate error responses for invalid requests
    """
    @functools.wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> JsonResponse:
        # Validate POST method
        if request.method != "POST":
            logger.warning(
                "Invalid method %s attempted on %s",
                request.method,
                request.path
            )
            return build_error_response(
                ErrorCodes.METHOD_NOT_ALLOWED,
                ErrorMessages.POST_ONLY,
                status=HTTPStatus.METHOD_NOT_ALLOWED
            )

        # Parse JSON body
        try:
            request.json = json.loads(request.body or "{}")  # type: ignore
            logger.debug("Parsed JSON payload with keys: %s", list(request.json.keys()))  # type: ignore
        except json.JSONDecodeError as e:
            logger.warning(
                "JSON decode error on %s: %s",
                request.path,
                str(e)
            )
            return build_error_response(
                ErrorCodes.INVALID_JSON,
                ErrorMessages.INVALID_JSON,
                details={"error": str(e)}
            )

        return view_func(request, *args, **kwargs)

    return wrapper


@csrf_exempt
def agent_view(request: HttpRequest) -> JsonResponse:
    """Route agent tasks through a single JSON endpoint.

    This endpoint provides a unified interface for all agent tasks,
    with automatic validation, entitlement checking, and error handling.
    Supports both JSON payloads and file uploads (multipart/form-data).

    Args:
        request: Django HTTP request containing task and payload

    Returns:
        JsonResponse with task result or error details

    Examples:
        >>> from django.test import RequestFactory
        >>> factory = RequestFactory()
        >>> request = factory.post(
        ...     "/api/agent/",
        ...     data=json.dumps({"task": "unknown", "payload": {}}),
        ...     content_type="application/json",
        ... )
        >>> agent_view(request).status_code
        400
    """
    # Handle file uploads (multipart/form-data)
    if request.FILES:
        uploaded_file = request.FILES.get("file")
        task = request.POST.get("task")
        
        if not task:
            return build_error_response(
                ErrorCodes.MISSING_TASK,
                ErrorMessages.TASK_REQUIRED
            )
        
        if not uploaded_file:
            return build_error_response(
                ErrorCodes.INVALID_INPUT,
                "File upload requires a 'file' parameter.",
                details={"received_files": list(request.FILES.keys())}
            )
        
        # Validate file type
        if not uploaded_file.name.lower().endswith(".csv"):
            return build_error_response(
                ErrorCodes.INVALID_INPUT,
                "Only CSV files are supported.",
                details={"supported_formats": [".csv"]}
            )
        
        # Route to appropriate CSV processor
        try:
            if task == "product_mix":
                from backend.consulting_services.menu.legacy_product_mix import process_csv_data
                result = process_csv_data(uploaded_file)
                if result.get("status") == "error" and "Missing required columns" in (result.get("message") or ""):
                    def _has_any(col_list, variants):
                        return any(any(v in c for v in variants) for c in col_list)

                    def _has_all(col_list, required):
                        return all(any(r == c or r in c for c in col_list) for r in required)

                    def _detect_task_from_headers(file_obj):
                        import pandas as pd
                        try:
                            file_obj.seek(0)
                        except Exception:
                            pass
                        df = pd.read_csv(file_obj, nrows=0)
                        cols = [c.lower().strip() for c in df.columns]

                        if _has_all(cols, ["expected_oz", "actual_oz"]) and _has_any(cols, ["liquor_cost", "beverage_cost", "bar_cost"]) and _has_any(cols, ["total_sales", "sales", "revenue"]):
                            return "liquor_cost_analysis"
                        if _has_all(cols, ["current_stock", "reorder_point", "monthly_usage", "inventory_value"]):
                            return "bar_inventory_analysis"
                        if _has_all(cols, ["drink_price", "cost_per_drink", "sales_volume", "competitor_price"]):
                            return "beverage_pricing_analysis"

                        has_business_goals = _has_all(cols, ["revenue_target", "budget_total"])
                        if has_business_goals:
                            return "business_goals"
                        if _has_any(cols, ["market_size", "market_share", "competition_level", "investment_budget", "growth_potential", "market_penetration", "target_roi", "roi_target"]):
                            return "growth_strategy"
                        if _has_any(cols, ["efficiency_score", "process_time", "quality_rating", "customer_satisfaction", "cost_per_unit", "waste_percentage", "productivity_score", "industry_benchmark"]):
                            return "operational_excellence"
                        if _has_any(cols, ["historical_sales", "current_sales", "growth_rate", "seasonal_factor", "forecast_periods", "forecast_period"]):
                            return "sales_forecasting"

                        has_item_name = _has_any(cols, ["item_name", "menu_item", "product_name", "product name", "item"])
                        has_qty = _has_any(cols, ["quantity_sold", "quantity", "units_sold", "units sold"])
                        has_opt_specific = _has_any(cols, ["portion_size", "portion_cost", "waste_percent", "waste", "description"])
                        if has_item_name and has_qty and has_opt_specific:
                            return "optimization"

                        has_price = _has_any(cols, ["price", "unit_price", "unit price", "item_price"])
                        if has_item_name and has_qty and has_price:
                            return "product_mix"

                        if _has_any(cols, ["recipe_name", "recipe", "menu_item", "dish"]) and _has_any(cols, ["ingredient_cost", "portion_cost", "recipe_price"]):
                            return "recipe_management"
                        if _has_any(cols, ["date"]) and _has_any(cols, ["sales", "revenue", "total_sales", "daily_sales"]) and _has_any(cols, ["labor_cost", "labor", "wages", "payroll"]) and _has_any(cols, ["food_cost", "cogs", "cost_of_goods", "food"]) and _has_any(cols, ["labor_hours", "hours", "hours_worked", "staff_hours", "labor_hour"]):
                            return "kpi_analysis"

                        if _has_any(cols, ["turnover_rate", "turnover", "attrition_rate"]):
                            return "hr_retention"
                        if _has_any(cols, ["total_sales", "sales", "revenue"]) and _has_any(cols, ["labor_hours", "hours_worked", "hours"]) and _has_any(cols, ["hourly_rate", "pay_rate", "avg_hourly_rate"]):
                            return "hr_scheduling"
                        if _has_any(cols, ["customer_satisfaction", "csat", "sales_performance", "efficiency_score", "attendance_rate"]):
                            return "hr_performance"

                        if _has_all(cols, ["item_name", "item_price", "item_cost", "competitor_price"]):
                            return "pricing"

                        return None

                    try:
                        detected_task = _detect_task_from_headers(uploaded_file)
                    except Exception:
                        detected_task = None

                    if detected_task and detected_task != "product_mix":
                        try:
                            uploaded_file.seek(0)
                        except Exception:
                            pass
                        if detected_task == "liquor_cost_analysis":
                            from backend.consulting_services.beverage.liquor_cost_csv_processor import process_liquor_cost_csv_data
                            result = process_liquor_cost_csv_data(uploaded_file)
                        elif detected_task == "bar_inventory_analysis":
                            from backend.consulting_services.beverage.bar_inventory_csv_processor import process_bar_inventory_csv_data
                            result = process_bar_inventory_csv_data(uploaded_file)
                        elif detected_task == "beverage_pricing_analysis":
                            from backend.consulting_services.beverage.beverage_pricing_csv_processor import process_beverage_pricing_csv_data
                            result = process_beverage_pricing_csv_data(uploaded_file)
                        elif detected_task == "recipe_management":
                            from backend.consulting_services.recipe.analysis_functions import process_recipe_csv_data
                            result = process_recipe_csv_data(uploaded_file)
                        elif detected_task == "kpi_analysis":
                            from backend.consulting_services.kpi.kpi_utils import process_kpi_csv_data
                            result = process_kpi_csv_data(uploaded_file)
                        elif detected_task in ["hr_retention", "hr_scheduling", "hr_performance"]:
                            from backend.consulting_services.hr.hr_csv_processor import process_hr_csv_data
                            analysis_type_map = {
                                "hr_retention": "retention",
                                "hr_scheduling": "scheduling",
                                "hr_performance": "performance",
                            }
                            result = process_hr_csv_data(uploaded_file, analysis_type_map.get(detected_task, "auto"))
                        elif detected_task == "optimization":
                            from backend.consulting_services.menu.optimization_csv_processor import process_optimization_csv_data
                            result = process_optimization_csv_data(uploaded_file)
                        elif detected_task in ["business_goals", "sales_forecasting", "growth_strategy", "operational_excellence"]:
                            from backend.consulting_services.strategy.strategic_csv_processor import (
                                process_business_goals_csv_data,
                                process_sales_forecasting_csv_data,
                                process_growth_strategy_csv_data,
                                process_operational_excellence_csv_data,
                            )
                            if detected_task == "business_goals":
                                result = process_business_goals_csv_data(uploaded_file)
                            elif detected_task == "sales_forecasting":
                                result = process_sales_forecasting_csv_data(uploaded_file)
                            elif detected_task == "growth_strategy":
                                result = process_growth_strategy_csv_data(uploaded_file)
                            else:
                                result = process_operational_excellence_csv_data(uploaded_file)
                        elif detected_task == "pricing":
                            from backend.consulting_services.menu.pricing_csv_processor import process_pricing_csv_data
                            result = process_pricing_csv_data(uploaded_file)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task == "pricing":
                # CSV-based pricing strategy analysis
                from backend.consulting_services.menu.pricing_csv_processor import process_pricing_csv_data
                result = process_pricing_csv_data(uploaded_file)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task == "design":
                # CSV-based menu design recommendations (matrix mapping)
                from backend.consulting_services.menu.design_csv_processor import process_design_csv_data
                result = process_design_csv_data(uploaded_file)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task == "kpi_analysis":
                from backend.consulting_services.kpi.kpi_utils import process_kpi_csv_data
                result = process_kpi_csv_data(uploaded_file)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task == "recipe_management":
                from backend.consulting_services.recipe.analysis_functions import process_recipe_csv_data
                result = process_recipe_csv_data(uploaded_file)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task == "optimization":
                # CSV-based item optimization analysis
                from backend.consulting_services.menu.optimization_csv_processor import process_optimization_csv_data
                result = process_optimization_csv_data(uploaded_file)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task in ["hr_retention", "hr_scheduling", "hr_performance", "hr_analysis"]:
                from backend.consulting_services.hr.hr_csv_processor import process_hr_csv_data
                # Map task to analysis type
                analysis_type_map = {
                    "hr_retention": "retention",
                    "hr_scheduling": "scheduling",
                    "hr_performance": "performance",
                    "hr_analysis": "auto"  # Auto-detect from columns
                }
                analysis_type = analysis_type_map.get(task, "auto")
                result = process_hr_csv_data(uploaded_file, analysis_type)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task in ["labor_cost", "food_cost", "prime_cost", "liquor_cost", "beverage_cost", "liquor_variance", "cost_analysis"]:
                from backend.consulting_services.cost.cost_csv_processor import process_cost_csv_data
                # Map task to analysis type
                analysis_type_map = {
                    "labor_cost": "labor",
                    "food_cost": "food",
                    "prime_cost": "prime",
                    "liquor_cost": "liquor",
                    "beverage_cost": "liquor",
                    "liquor_variance": "liquor",
                    "cost_analysis": "auto"  # Auto-detect from columns
                }
                analysis_type = analysis_type_map.get(task, "auto")
                result = process_cost_csv_data(uploaded_file, analysis_type)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            elif task in ["liquor_cost_analysis", "bar_inventory_analysis", "beverage_pricing_analysis"]:
                # Try the selected beverage processor; on column errors, auto-detect and fallback
                def _try_processor(proc_func):
                    # Ensure we reset file pointer between reads
                    try:
                        uploaded_file.seek(0)
                    except Exception:
                        pass
                    res = proc_func(uploaded_file)
                    return res

                result = None
                if task == "liquor_cost_analysis":
                    from backend.consulting_services.beverage.liquor_cost_csv_processor import process_liquor_cost_csv_data
                    result = _try_processor(process_liquor_cost_csv_data)
                elif task == "bar_inventory_analysis":
                    from backend.consulting_services.beverage.bar_inventory_csv_processor import process_bar_inventory_csv_data
                    result = _try_processor(process_bar_inventory_csv_data)
                elif task == "beverage_pricing_analysis":
                    from backend.consulting_services.beverage.beverage_pricing_csv_processor import process_beverage_pricing_csv_data
                    result = _try_processor(process_beverage_pricing_csv_data)

                # If missing columns error, auto-detect based on CSV headers
                if result and result.get("status") == "error" and "Missing required columns" in (result.get("message") or ""):
                    import pandas as pd
                    try:
                        uploaded_file.seek(0)
                    except Exception:
                        pass
                    try:
                        df = pd.read_csv(uploaded_file)
                        cols = [c.lower().strip() for c in df.columns]
                        def has_all(keys):
                            return all(k in cols for k in keys)
                        # Decide which processor matches the CSV
                        if has_all(["expected_oz", "actual_oz", "liquor_cost", "total_sales"]):
                            from backend.consulting_services.beverage.liquor_cost_csv_processor import process_liquor_cost_csv_data
                            uploaded_file.seek(0)
                            result = process_liquor_cost_csv_data(uploaded_file)
                        elif has_all(["current_stock", "reorder_point", "monthly_usage", "inventory_value"]):
                            from backend.consulting_services.beverage.bar_inventory_csv_processor import process_bar_inventory_csv_data
                            uploaded_file.seek(0)
                            result = process_bar_inventory_csv_data(uploaded_file)
                        elif has_all(["drink_price", "cost_per_drink", "sales_volume", "competitor_price"]):
                            from backend.consulting_services.beverage.beverage_pricing_csv_processor import process_beverage_pricing_csv_data
                            uploaded_file.seek(0)
                            result = process_beverage_pricing_csv_data(uploaded_file)
                        else:
                            # Fallback to general cost auto-detection
                            from backend.consulting_services.cost.cost_csv_processor import process_cost_csv_data
                            uploaded_file.seek(0)
                            result = process_cost_csv_data(uploaded_file, "auto")
                    except Exception as e:
                        result = {
                            "status": "error",
                            "message": f"Failed to auto-detect beverage CSV type: {str(e)}"
                        }

                status_code = 400 if (result or {}).get("status") == "error" else 200
                return JsonResponse(result or {"status": "error", "message": "Unknown CSV processing error"}, status=status_code)
            elif task in ["business_goals", "sales_forecasting", "growth_strategy", "operational_excellence"]:
                from backend.consulting_services.strategy.strategic_csv_processor import (
                    process_business_goals_csv_data,
                    process_sales_forecasting_csv_data,
                    process_growth_strategy_csv_data,
                    process_operational_excellence_csv_data,
                )
                if task == "business_goals":
                    result = process_business_goals_csv_data(uploaded_file)
                elif task == "sales_forecasting":
                    result = process_sales_forecasting_csv_data(uploaded_file)
                elif task == "growth_strategy":
                    result = process_growth_strategy_csv_data(uploaded_file)
                else:
                    result = process_operational_excellence_csv_data(uploaded_file)
                status_code = 400 if result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            else:
                return build_error_response(
                    ErrorCodes.UNKNOWN_TASK,
                    f"File upload not supported for task: {task}",
                    details={"supported_tasks": ["product_mix", "kpi_analysis", "recipe_management", "hr_retention", "hr_scheduling", "hr_performance", "hr_analysis", "labor_cost", "food_cost", "prime_cost", "liquor_cost", "beverage_cost", "liquor_variance", "cost_analysis", "liquor_cost_analysis", "bar_inventory_analysis", "beverage_pricing_analysis", "business_goals", "sales_forecasting", "growth_strategy", "operational_excellence"]}
                )
        except Exception as e:
            trace_id = uuid4().hex
            logger.exception(
                "File processing error for task %s (trace_id=%s): %s",
                task,
                trace_id,
                str(e)
            )
            return build_error_response(
                ErrorCodes.INTERNAL_ERROR,
                f"File processing error: {str(e)}",
                trace_id=trace_id,
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
    
    # Handle JSON payloads
    if request.method != "POST":
        logger.warning(
            "Invalid method %s attempted on %s",
            request.method,
            request.path
        )
        return build_error_response(
            ErrorCodes.METHOD_NOT_ALLOWED,
            ErrorMessages.POST_ONLY,
            status=HTTPStatus.METHOD_NOT_ALLOWED
        )
    
    # Parse JSON body
    try:
        body = json.loads(request.body or "{}")
        logger.debug("Parsed JSON payload with keys: %s", list(body.keys()))
    except json.JSONDecodeError as e:
        logger.warning(
            "JSON decode error on %s: %s",
            request.path,
            str(e)
        )
        return build_error_response(
            ErrorCodes.INVALID_JSON,
            ErrorMessages.INVALID_JSON,
            details={"error": str(e)}
        )

    # Validate task parameter
    task = body.get("task")
    if not isinstance(task, str) or not task.strip():
        logger.warning("Invalid or missing task parameter: %r", task)
        return build_error_response(
            ErrorCodes.MISSING_TASK,
            ErrorMessages.TASK_REQUIRED
        )

    task = task.strip()
    logger.info(
        "Processing task '%s' with entitlement=%s",
        task,
        _has_kpi_entitlement(request)
    )

    # Look up task definition
    definition: Optional[TaskDefinition] = TASK_DEFINITIONS.get(task)
    if definition is None:
        logger.warning("Unknown task requested: %s", task)
        return build_error_response(
            ErrorCodes.UNKNOWN_TASK,
            f"Unknown task '{task}'.",
            details={"available_tasks": sorted(TASK_DEFINITIONS.keys())}
        )

    # Validate payload
    payload = body.get("payload", {})
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        logger.warning("Invalid payload type for task %s: %s", task, type(payload))
        return build_error_response(
            ErrorCodes.INVALID_PAYLOAD,
            ErrorMessages.PAYLOAD_MUST_BE_OBJECT
        )

    # Check entitlement if required
    if definition.requires_entitlement and not _has_kpi_entitlement(request):
        logger.info("Task %s requires entitlement but header not present", task)
        return build_error_response(
            ErrorCodes.LOCKED,
            ErrorMessages.UPGRADE_REQUIRED,
            status=HTTPStatus.FORBIDDEN
        )

    # Validate payload against schema
    try:
        validated = definition.schema(**payload)
        logger.debug("Payload validation successful for task %s", task)
    except ValidationError as error:
        logger.warning("Payload validation failed for task %s: %s", task, error)
        return build_error_response(
            ErrorCodes.VALIDATION_FAILED,
            ErrorMessages.VALIDATION_FAILED,
            details=_format_validation_errors(error)
        )

    # Execute task
    try:
        result = definition.runner(validated)
        logger.info("Task %s executed successfully", task)
    except Exception as e:
        trace_id = uuid4().hex
        logger.exception(
            "Unhandled error executing task %s (trace_id=%s): %s",
            task,
            trace_id,
            str(e)
        )
        return build_error_response(
            ErrorCodes.INTERNAL_ERROR,
            ErrorMessages.UNEXPECTED_ERROR,
            trace_id=trace_id,
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

    # Validate response type
    if not isinstance(result, dict):
        trace_id = uuid4().hex
        logger.error(
            "Task %s returned non-dict response type %s (trace_id=%s)",
            task,
            type(result),
            trace_id
        )
        return build_error_response(
            ErrorCodes.INTERNAL_ERROR,
            ErrorMessages.INVALID_RESPONSE,
            trace_id=trace_id,
            status=HTTPStatus.INTERNAL_SERVER_ERROR
        )

    logger.debug("Task %s completed with result keys: %s", task, list(result.keys()))
    return JsonResponse(result, status=HTTPStatus.OK)


def _format_validation_errors(error: ValidationError) -> Dict[str, List[str]]:
    """Convert Pydantic errors into a {field: [messages]} mapping.

    Args:
        error: Pydantic ValidationError

    Returns:
        Dictionary mapping field names to lists of error messages

    Examples:
        >>> _format_validation_errors(
        ...     ValidationError(
        ...         [
        ...             {"loc": ("field",), "msg": "required", "type": "value_error"},
        ...         ],
        ...         model=type("Model", (), {}),
        ...     )
        ... )
        {'field': ['required']}
    """
    details: Dict[str, List[str]] = {}

    for err in error.errors():
        # Extract field path from error location
        parts = [str(part) for part in err.get("loc", ()) if isinstance(part, (str, int))]
        field = ".".join(parts) if parts else "payload"

        # Add error message to field
        message = err.get("msg", "Invalid value.")
        details.setdefault(field, []).append(message)

        logger.debug("Validation error for field %s: %s", field, message)

    return details


def _has_kpi_entitlement(request: HttpRequest) -> bool:
    """Return whether the request has the KPI entitlement header.

    Args:
        request: Django HTTP request

    Returns:
        True if entitlement header is present with truthy value

    Examples:
        >>> class _DummyRequest:
        ...     headers = {ENTITLEMENT_HEADER: "true"}
        >>> _has_kpi_entitlement(_DummyRequest())
        True
    """
    header_value = request.headers.get(ENTITLEMENT_HEADER)

    if header_value is None:
        return False

    normalized = header_value.strip().lower()
    has_entitlement = normalized in _TRUTHY_VALUES

    logger.debug(
        "Entitlement check: header=%r, normalized=%r, result=%s",
        header_value,
        normalized,
        has_entitlement
    )

    return has_entitlement


@csrf_exempt
def agent_status(request: HttpRequest) -> JsonResponse:
    """Check agent status.

    Args:
        request: Django HTTP request

    Returns:
        JsonResponse with agent status
    """
    logger.debug("Status check requested from %s", request.META.get("REMOTE_ADDR"))
    return JsonResponse(
        {
            "status": "operational",
            "message": "Agent is running.",
            "timestamp": uuid4().hex[:8]  # Simple request ID for tracking
        }
    )


@csrf_exempt
def agent_index(request: HttpRequest) -> JsonResponse:
    """Return API information and available endpoints.

    Args:
        request: Django HTTP request

    Returns:
        JsonResponse with API documentation
    """
    logger.debug("Index requested from %s", request.META.get("REMOTE_ADDR"))

    # Get available tasks if user has entitlement
    available_tasks = None
    if _has_kpi_entitlement(request):
        available_tasks = sorted(TASK_DEFINITIONS.keys())
    else:
        # Only show non-entitlement tasks
        available_tasks = sorted(
            task for task, defn in TASK_DEFINITIONS.items()
            if not defn.requires_entitlement
        )

    return JsonResponse(
        {
            "message": "Hospitality AI Agent API",
            "version": "2.0",
            "endpoints": {
                "agent": {
                    "path": "/agent/",
                    "method": "POST",
                    "description": "Execute agent tasks"
                },
                "status": {
                    "path": "/agent/status/",
                    "method": "GET",
                    "description": "Check agent status"
                },
                "index": {
                    "path": "/agent/index/",
                    "method": "GET",
                    "description": "API documentation"
                }
            },
            "available_tasks": available_tasks
        }
    )


# URL Configuration Helper
def get_urlpatterns():
    """Return URL patterns for inclusion in urls.py.

    Usage in urls.py:
        from agent.views import get_urlpatterns
        urlpatterns += get_urlpatterns()
    """
    from django.urls import path

    return [
        path('agent/', agent_view, name='agent'),
        path('agent/status/', agent_status, name='agent-status'),
        path('agent/index/', agent_index, name='agent-index'),
    ]
