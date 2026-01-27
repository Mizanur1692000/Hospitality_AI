"""
Safe Task Registry for Business Insight Cards
Provides a controlled way to register new tasks without breaking existing functionality.
"""

from typing import Dict, Any, Callable, Optional
import importlib
import logging

logger = logging.getLogger(__name__)


class TaskRegistry:
    """Registry for business insight card tasks with safety controls."""

    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._locked = False

    def register_task(self, service: str, subtask: str, module_path: str, function_name: str = "run") -> bool:
        """
        Register a new task with safety checks.

        Args:
            service: Service name (e.g., 'kpi', 'hr', 'beverage')
            subtask: Subtask name (e.g., 'labor_cost', 'prime_cost')
            module_path: Full module path (e.g., 'agent_core.tasks.kpi_labor_cost')
            function_name: Function name to call (default: 'run')

        Returns:
            True if registration successful, False otherwise
        """
        if self._locked:
            logger.warning(f"Task registry is locked. Cannot register {service}.{subtask}")
            return False

        task_key = f"{service}.{subtask}"

        try:
            # Validate module exists
            module = importlib.import_module(module_path)

            # Validate function exists
            if not hasattr(module, function_name):
                logger.error(f"Function {function_name} not found in {module_path}")
                return False

            # Store task definition
            self._tasks[task_key] = {
                "service": service,
                "subtask": subtask,
                "module_path": module_path,
                "function_name": function_name,
                "module": module
            }

            logger.info(f"Successfully registered task: {task_key}")
            return True

        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to register task {task_key}: {e}")
            return False

    def get_task(self, service: str, subtask: str) -> Optional[Dict[str, Any]]:
        """Get a registered task."""
        task_key = f"{service}.{subtask}"
        return self._tasks.get(task_key)

    def list_tasks(self) -> Dict[str, Dict[str, Any]]:
        """List all registered tasks."""
        return self._tasks.copy()

    def lock(self) -> None:
        """Lock the registry to prevent further modifications."""
        self._locked = True
        logger.info("Task registry locked")

    def is_locked(self) -> bool:
        """Check if registry is locked."""
        return self._locked

    def execute_task(self, service: str, subtask: str, params: dict, file_bytes: Optional[bytes] = None) -> tuple[dict, int]:
        """
        Execute a registered task safely.

        Returns:
            Tuple of (response_dict, status_code)
        """
        task = self.get_task(service, subtask)
        if not task:
            return ({
                "service": service,
                "subtask": subtask,
                "status": "error",
                "error": f"Task {service}.{subtask} not found",
                "meta": {"version": "1.0.0", "generated_at": "2025-01-01T00:00:00Z"}
            }, 404)

        try:
            function = getattr(task["module"], task["function_name"])
            return function(params, file_bytes)
        except Exception as e:
            logger.error(f"Error executing task {service}.{subtask}: {e}")
            return ({
                "service": service,
                "subtask": subtask,
                "status": "error",
                "error": f"Internal error: {str(e)}",
                "meta": {"version": "1.0.0", "generated_at": "2025-01-01T00:00:00Z"}
            }, 500)


# Global registry instance
task_registry = TaskRegistry()

# Register the new KPI tasks
task_registry.register_task("kpi", "labor_cost", "backend.consulting_services.kpi.labor_cost")
task_registry.register_task("kpi", "food_cost", "backend.consulting_services.kpi.food_cost")
task_registry.register_task("kpi", "prime_cost", "backend.consulting_services.kpi.prime_cost")
task_registry.register_task("kpi", "sales_performance", "backend.consulting_services.kpi.sales_performance")

# Register the new HR tasks
task_registry.register_task("hr", "staff_retention", "backend.consulting_services.hr.staff_retention")
task_registry.register_task("hr", "labor_scheduling", "backend.consulting_services.hr.labor_scheduling")
task_registry.register_task("hr", "performance_management", "backend.consulting_services.hr.performance_management")

# Register the new Beverage Management tasks
task_registry.register_task("beverage", "liquor_cost", "backend.consulting_services.beverage.liquor_cost")
task_registry.register_task("beverage", "inventory", "backend.consulting_services.beverage.inventory")
task_registry.register_task("beverage", "pricing", "backend.consulting_services.beverage.pricing")

# Register the new Menu Engineering tasks
task_registry.register_task("menu", "product_mix", "backend.consulting_services.menu.product_mix")
task_registry.register_task("menu", "pricing", "backend.consulting_services.menu.pricing")
task_registry.register_task("menu", "design", "backend.consulting_services.menu.design")
task_registry.register_task("menu", "questions", "backend.consulting_services.menu.menu_questions")

# Register the new Recipe Management tasks
task_registry.register_task("recipe", "costing", "backend.consulting_services.recipe.costing")
# TODO: Ingredient optimization not yet implemented - missing calculate_ingredient_optimization_analysis function
# task_registry.register_task("recipe", "ingredient_optimization", "backend.consulting_services.menu.ingredient_optimization")
task_registry.register_task("recipe", "scaling", "backend.consulting_services.recipe.scaling")

# Register the new Strategic Planning tasks
task_registry.register_task("strategic", "sales_forecasting", "backend.consulting_services.strategy.sales_forecasting")
task_registry.register_task("strategic", "growth_strategy", "backend.consulting_services.strategy.growth")
task_registry.register_task("strategic", "operational_excellence", "backend.consulting_services.strategy.operational")

# Register the new KPI Dashboard tasks
task_registry.register_task("kpi_dashboard", "comprehensive_analysis", "backend.consulting_services.strategy.comprehensive")
task_registry.register_task("kpi_dashboard", "performance_optimization", "backend.consulting_services.hr.performance_optimization")

# Register the Conversational AI endpoints
task_registry.register_task("conversational", "ai", "backend.shared.ai.conversational_ai")
task_registry.register_task("conversational", "history", "backend.shared.ai.conversational_ai", "get_conversation_history")
task_registry.register_task("conversational", "clear", "backend.shared.ai.conversational_ai", "clear_conversation")
