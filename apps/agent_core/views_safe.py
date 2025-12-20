"""
Safe API View for Business Insight Cards
Extends existing functionality without breaking current endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import logging

from .task_registry import task_registry

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class SafeAgentServiceView(APIView):
    """
    Safe POST /api/agent/safe/
    {
      "service": "kpi",
      "subtask": "labor_cost",
      "params": { ... }
    }

    This endpoint provides a safe way to execute business insight card tasks
    without interfering with the existing agent endpoint.
    """

    def post(self, request):
        try:
            # Extract request data
            service = request.data.get("service")
            subtask = request.data.get("subtask")
            params = request.data.get("params") or {}

            # Validate required fields
            if not service or not subtask:
                return Response({
                    "error": "service and subtask are required",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if task is registered
            if not task_registry.get_task(service, subtask):
                available_tasks = list(task_registry.list_tasks().keys())
                return Response({
                    "error": f"Task {service}.{subtask} not found",
                    "available_tasks": available_tasks,
                    "status": "error"
                }, status=status.HTTP_404_NOT_FOUND)

            # Handle file uploads if present
            file_bytes = None
            if "file" in request.FILES:
                file_bytes = request.FILES["file"].read()

            # Execute the task
            payload, code = task_registry.execute_task(service, subtask, params, file_bytes)

            # Return response with appropriate status code
            return Response(payload, status=code)

        except ValueError as e:
            logger.warning(f"Validation error in SafeAgentServiceView: {e}")
            return Response({
                "error": str(e),
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error in SafeAgentServiceView: {e}")
            return Response({
                "error": f"Internal error: {str(e)}",
                "status": "error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
