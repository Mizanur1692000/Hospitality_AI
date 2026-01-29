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
            else:
                return build_error_response(
                    ErrorCodes.UNKNOWN_TASK,
                    f"File upload not supported for task: {task}",
                    details={"supported_tasks": ["product_mix", "kpi_analysis", "recipe_management", "hr_retention", "hr_scheduling", "hr_performance", "hr_analysis", "labor_cost", "food_cost", "prime_cost", "liquor_cost", "beverage_cost", "liquor_variance", "cost_analysis"]}
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
