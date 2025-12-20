import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from apps.agent_core.tasks import forecasting, human_resources, inventory, labor, liquor, product_mix
from backend.consulting_services.forecasting import run_forecast
from backend.consulting_services.human_resources import retention_insights
from backend.consulting_services.inventory import calculate_inventory_variance
from backend.consulting_services.kpi import (
    calculate_kpi_summary,
    process_kpi_csv_data,
    calculate_labor_cost_analysis,
    calculate_prime_cost_analysis,
    calculate_sales_performance_analysis
)
from backend.consulting_services.labor import calculate_labor_cost
from backend.consulting_services.liquor import calculate_liquor_variance
from backend.consulting_services.product_mix import generate_pmix_report

# Task mapping for the agent view
task_map = {
    "forecast": lambda data: run_forecast(data.get("sales_data", [])),
    "hr_retention": lambda data: retention_insights(data.get("turnover_rate"), data.get("industry_avg", 70)),
    "inventory_variance": lambda data: calculate_inventory_variance(data.get("expected_usage"), data.get("actual_usage")),
    "labor_cost": lambda data: calculate_labor_cost(data.get("total_sales"), data.get("labor_hours"), data.get("hourly_rate")),
    "liquor_variance": lambda data: calculate_liquor_variance(data.get("expected_oz"), data.get("actual_oz")),
    "kpi_summary": lambda data: calculate_kpi_summary(
        total_sales=data.get("total_sales"),
        labor_cost=data.get("labor_cost"),
        food_cost=data.get("food_cost"),
        hours_worked=data.get("hours_worked"),
    ),
    "pmix_report": lambda data: generate_pmix_report(data.get("items", [])),
    # New KPI Analysis tasks
    "labor_cost_analysis": lambda data: calculate_labor_cost_analysis(
        total_sales=data.get("total_sales"),
        labor_cost=data.get("labor_cost"),
        hours_worked=data.get("hours_worked"),
        target_labor_percent=data.get("target_labor_percent", 30.0)
    ),
    "prime_cost_analysis": lambda data: calculate_prime_cost_analysis(
        total_sales=data.get("total_sales"),
        labor_cost=data.get("labor_cost"),
        food_cost=data.get("food_cost"),
        target_prime_percent=data.get("target_prime_percent", 60.0)
    ),
    "sales_performance_analysis": lambda data: calculate_sales_performance_analysis(
        total_sales=data.get("total_sales"),
        labor_cost=data.get("labor_cost"),
        food_cost=data.get("food_cost"),
        hours_worked=data.get("hours_worked"),
        previous_sales=data.get("previous_sales")
    ),
}


@csrf_exempt
def agent_view(request):
    if request.method == "POST":
        # Check if this is a file upload request
        if request.FILES:
            return handle_file_upload(request)

        # Handle regular JSON requests
        try:
            body = json.loads(request.body)
            task = body.get("task")
            data = body.get("data", {})  # Default to empty dict instead of None

            # Validate required task parameter
            if not task:
                return JsonResponse({"status": "error", "message": "task parameter is required"}, status=400)

            # Validate data is a dictionary
            if not isinstance(data, dict):
                return JsonResponse({"status": "error", "message": "data must be an object"}, status=400)

            if task in task_map:
                handler = task_map[task]
                result = handler(data)
                status_code = 400 if isinstance(result, dict) and result.get("status") == "error" else 200
                return JsonResponse(result, status=status_code)
            else:
                available_tasks = list(task_map.keys())
                return JsonResponse(
                    {"status": "error", "message": f"Unknown task: {task}", "available_tasks": available_tasks}, status=400
                )

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


def handle_file_upload(request):
    """
    Handle file upload requests for data analysis
    """
    task = request.POST.get("task")
    uploaded_file = request.FILES.get("file")

    if not task:
        return JsonResponse({"status": "error", "message": "task parameter is required"}, status=400)

    if not uploaded_file:
        return JsonResponse({"status": "error", "message": "file is required"}, status=400)

    # Validate file type
    if not uploaded_file.name.lower().endswith(".csv"):
        return JsonResponse(
            {"status": "error", "message": "Only CSV files are supported", "supported_formats": [".csv"]}, status=400
        )

    try:
        # Route to appropriate task handler
        if task == "product_mix":
            from backend.consulting_services.product_mix import process_csv_data

            result = process_csv_data(uploaded_file)
            status_code = 400 if result.get("status") == "error" else 200
            return JsonResponse(result, status=status_code)
        elif task == "kpi_analysis":
            result = process_kpi_csv_data(uploaded_file)
            status_code = 400 if result.get("status") == "error" else 200
            return JsonResponse(result, status=status_code)
        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"File upload not supported for task: {task}",
                    "supported_tasks": ["product_mix", "kpi_analysis"],
                },
                status=400,
            )

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"File processing error: {str(e)}"}, status=500)


def agent_status(request):
    return JsonResponse({"status": "Agent is running."})


def agent_index(request):
    return JsonResponse(
        {
            "message": "Hospitality AI Agent API",
            "endpoints": {"admin": "/admin/", "agent_status": "/agent/status/", "agent_index": "/agent/"},
        }
    )


def agent_run(request):
    tool = request.GET.get("tool")

    match tool:
        case "forecasting":
            return JsonResponse(forecasting.run())
        case "product_mix":
            return JsonResponse(product_mix.run())
        case "human_resources":
            return JsonResponse(human_resources.run())
        case "labor":
            return JsonResponse(labor.run())
        case "liquor":
            return JsonResponse(liquor.run())
        case "inventory":
            return JsonResponse(inventory.run())
        case _:
            return JsonResponse({"status": "error", "message": "Tool not found"}, status=400)


@csrf_exempt
def forecast_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)

            # Validate sales_data is provided
            if "sales_data" not in body:
                return JsonResponse({"status": "error", "message": "sales_data field is required"}, status=400)

            sales_data = body.get("sales_data", [])
            response = run_forecast(sales_data)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def hr_retention_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required field
            if "turnover_rate" not in data:
                return JsonResponse({"status": "error", "message": "turnover_rate field is required"}, status=400)

            turnover = data.get("turnover_rate")
            industry_avg = data.get("industry_avg", 70)

            # Validate numeric types
            try:
                turnover = float(turnover) if turnover is not None else None
                industry_avg = float(industry_avg)
            except (ValueError, TypeError):
                return JsonResponse(
                    {"status": "error", "message": "turnover_rate and industry_avg must be numeric values"}, status=400
                )

            response = retention_insights(turnover, industry_avg)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def inventory_variance_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ["expected_usage", "actual_usage"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse(
                    {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, status=400
                )

            # Extract and validate data types
            try:
                expected = float(data["expected_usage"])
                actual = float(data["actual_usage"])
            except (ValueError, TypeError):
                return JsonResponse(
                    {"status": "error", "message": "expected_usage and actual_usage must be numeric values"}, status=400
                )

            response = calculate_inventory_variance(expected, actual)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def labor_cost_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ["total_sales", "labor_hours", "hourly_rate"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse(
                    {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, status=400
                )

            # Extract and validate data types
            try:
                total_sales = float(data["total_sales"])
                labor_hours = float(data["labor_hours"])
                hourly_rate = float(data["hourly_rate"])
            except (ValueError, TypeError):
                return JsonResponse({"status": "error", "message": "All fields must be numeric values"}, status=400)

            response = calculate_labor_cost(total_sales, labor_hours, hourly_rate)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def liquor_variance_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ["expected_oz", "actual_oz"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse(
                    {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, status=400
                )

            # Extract and validate data types
            try:
                expected = float(data["expected_oz"])
                actual = float(data["actual_oz"])
            except (ValueError, TypeError):
                return JsonResponse(
                    {"status": "error", "message": "expected_oz and actual_oz must be numeric values"}, status=400
                )

            response = calculate_liquor_variance(expected, actual)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def kpi_summary_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ["total_sales", "labor_cost", "food_cost", "hours_worked"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse(
                    {"status": "error", "message": f"Missing required fields: {', '.join(missing_fields)}"}, status=400
                )

            # Extract and validate data types
            try:
                total_sales = float(data["total_sales"])
                labor_cost = float(data["labor_cost"])
                food_cost = float(data["food_cost"])
                hours_worked = float(data["hours_worked"])
            except (ValueError, TypeError):
                return JsonResponse({"status": "error", "message": "All fields must be numeric values"}, status=400)

            response = calculate_kpi_summary(
                total_sales=total_sales,
                labor_cost=labor_cost,
                food_cost=food_cost,
                hours_worked=hours_worked,
            )
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def pmix_report_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate items field is provided
            if "items" not in data:
                return JsonResponse({"status": "error", "message": "items field is required"}, status=400)

            items = data.get("items", [])

            # Validate items is a list
            if not isinstance(items, list):
                return JsonResponse({"status": "error", "message": "items must be a list"}, status=400)

            response = generate_pmix_report(items)
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def labor_cost_analysis_view(request):
    """Labor Cost Analysis API endpoint"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ["total_sales", "labor_cost", "hours_worked"]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"status": "error", "message": f"{field} field is required"}, status=400)

            response = calculate_labor_cost_analysis(
                total_sales=data.get("total_sales"),
                labor_cost=data.get("labor_cost"),
                hours_worked=data.get("hours_worked"),
                target_labor_percent=data.get("target_labor_percent", 30.0)
            )
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def prime_cost_analysis_view(request):
    """Prime Cost Analysis API endpoint"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ["total_sales", "labor_cost", "food_cost"]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"status": "error", "message": f"{field} field is required"}, status=400)

            response = calculate_prime_cost_analysis(
                total_sales=data.get("total_sales"),
                labor_cost=data.get("labor_cost"),
                food_cost=data.get("food_cost"),
                target_prime_percent=data.get("target_prime_percent", 60.0)
            )
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)


@csrf_exempt
def sales_performance_analysis_view(request):
    """Sales Performance Analysis API endpoint"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ["total_sales", "labor_cost", "food_cost", "hours_worked"]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"status": "error", "message": f"{field} field is required"}, status=400)

            response = calculate_sales_performance_analysis(
                total_sales=data.get("total_sales"),
                labor_cost=data.get("labor_cost"),
                food_cost=data.get("food_cost"),
                hours_worked=data.get("hours_worked"),
                previous_sales=data.get("previous_sales")
            )
            return JsonResponse(response)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON payload"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Internal error: {str(e)}"}, status=500)
    return JsonResponse({"status": "error", "message": "Only POST method allowed"}, status=405)
