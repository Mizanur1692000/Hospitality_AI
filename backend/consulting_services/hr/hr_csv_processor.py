"""
HR CSV Data Processor
Handles CSV file uploads for HR Solutions: Staff Retention, Labor Scheduling, Performance Management.
"""

import io
from typing import Any, Dict, List
import pandas as pd

from backend.consulting_services.hr.staff_retention import run as run_retention
from backend.consulting_services.hr.labor_scheduling import run as run_scheduling
from backend.consulting_services.hr.performance_management import run as run_performance


def process_hr_csv_data(csv_file, analysis_type: str = "auto") -> Dict[str, Any]:
    """
    Process uploaded CSV file for HR analysis.
    
    Args:
        csv_file: Uploaded CSV file object
        analysis_type: Type of analysis - "retention", "scheduling", "performance", or "auto" (detect from columns)
    
    Expected CSV columns for each analysis type:
    
    Staff Retention:
        Required: turnover_rate
        Optional: industry_average, department, employee_count
    
    Labor Scheduling:
        Required: total_sales, labor_hours (or hours_worked), hourly_rate
        Optional: peak_hours, department, date
    
    Performance Management:
        Required: At least one of: customer_satisfaction, sales_performance, efficiency_score, attendance_rate
        Optional: employee_name, department, targets for each metric
    
    Returns:
        Dict containing analysis results or error details
    """
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Get original column names for debugging
        original_columns = list(df.columns)
        col_lower = [c.lower().strip() for c in df.columns]
        
        # Create lowercase mapping
        col_map = {c.lower().strip(): c for c in df.columns}
        
        # Define column mappings for each analysis type
        retention_columns = {
            "turnover_rate": ["turnover_rate", "turnover", "turnover_percent", "turnover%", "attrition_rate"],
            "industry_average": ["industry_average", "industry_avg", "benchmark", "industry_benchmark"],
            "department": ["department", "dept", "team", "division"],
            "employee_count": ["employee_count", "employees", "headcount", "staff_count"]
        }
        
        scheduling_columns = {
            "total_sales": ["total_sales", "sales", "revenue", "daily_sales"],
            "labor_hours": ["labor_hours", "hours_worked", "hours", "staff_hours", "work_hours"],
            "hourly_rate": ["hourly_rate", "rate", "wage", "pay_rate", "avg_hourly_rate"],
            "peak_hours": ["peak_hours", "peak_hours_worked", "busy_hours"],
            "date": ["date", "period", "week", "day"]
        }
        
        performance_columns = {
            "customer_satisfaction": ["customer_satisfaction", "csat", "satisfaction", "customer_score"],
            "sales_performance": ["sales_performance", "sales_score", "sales_target", "sales_pct"],
            "efficiency_score": ["efficiency_score", "efficiency", "productivity", "productivity_score"],
            "attendance_rate": ["attendance_rate", "attendance", "attendance_pct"],
            "employee_name": ["employee_name", "name", "employee", "staff_name"],
            "department": ["department", "dept", "team"]
        }
        
        def find_column(target_variations):
            """Find matching column from variations."""
            for var in target_variations:
                if var in col_lower:
                    return col_map[var]
            return None
        
        def map_columns(column_def):
            """Map expected columns to actual columns."""
            mapped = {}
            for target, variations in column_def.items():
                found = find_column(variations)
                if found:
                    mapped[target] = found
            return mapped
        
        # Auto-detect analysis type if needed
        if analysis_type == "auto":
            retention_mapped = map_columns(retention_columns)
            scheduling_mapped = map_columns(scheduling_columns)
            performance_mapped = map_columns(performance_columns)
            
            # Score each type by number of matched columns
            scores = {
                "retention": len([k for k in ["turnover_rate"] if k in retention_mapped]),
                "scheduling": len([k for k in ["total_sales", "labor_hours", "hourly_rate"] if k in scheduling_mapped]),
                "performance": len([k for k in ["customer_satisfaction", "sales_performance", "efficiency_score", "attendance_rate"] if k in performance_mapped])
            }
            
            # Pick the type with highest score
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                analysis_type = best_type
            else:
                # Provide helpful error message
                return {
                    "status": "error",
                    "message": "Could not determine HR analysis type from CSV columns",
                    "found_columns": original_columns,
                    "help": """HR Analysis requires specific columns based on analysis type:

**Staff Retention Analysis:**
- Required: turnover_rate
- Optional: industry_average, department, employee_count

**Labor Scheduling Analysis:**
- Required: total_sales, labor_hours (or hours_worked), hourly_rate
- Optional: peak_hours, date

**Performance Management Analysis:**
- Required: At least one of: customer_satisfaction, sales_performance, efficiency_score, attendance_rate
- Optional: employee_name, department""",
                    "expected_formats": {
                        "retention": {"required": ["turnover_rate"], "optional": ["industry_average", "department"]},
                        "scheduling": {"required": ["total_sales", "labor_hours", "hourly_rate"], "optional": ["peak_hours"]},
                        "performance": {"required": ["customer_satisfaction OR sales_performance OR efficiency_score OR attendance_rate"], "optional": ["employee_name", "department"]}
                    }
                }
        
        # Process based on analysis type
        if analysis_type == "retention":
            return _process_retention_csv(df, retention_columns, original_columns)
        elif analysis_type == "scheduling":
            return _process_scheduling_csv(df, scheduling_columns, original_columns)
        elif analysis_type == "performance":
            return _process_performance_csv(df, performance_columns, original_columns)
        else:
            return {
                "status": "error",
                "message": f"Unknown analysis type: {analysis_type}",
                "supported_types": ["retention", "scheduling", "performance", "auto"]
            }
    
    except pd.errors.EmptyDataError:
        return {
            "status": "error",
            "message": "The CSV file is empty or has no valid data"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing HR CSV: {str(e)}",
            "error_type": type(e).__name__
        }


def _process_retention_csv(df: pd.DataFrame, column_def: Dict, original_columns: List[str]) -> Dict[str, Any]:
    """Process CSV for Staff Retention Analysis."""
    col_map = {c.lower().strip(): c for c in df.columns}
    
    def find_column(target_variations):
        for var in target_variations:
            if var in col_map:
                return col_map[var]
        return None
    
    # Check required column
    turnover_col = find_column(column_def["turnover_rate"])
    if not turnover_col:
        return {
            "status": "error",
            "message": "Missing required column: turnover_rate",
            "found_columns": original_columns,
            "help": """Staff Retention Analysis requires:
- **Required:** turnover_rate (the employee turnover percentage)
- **Optional:** industry_average (benchmark to compare against, default: 70%)

Example CSV format:
turnover_rate,industry_average,department
45,70,Front of House
55,70,Back of House
60,70,Management""",
            "expected_format": {
                "required": ["turnover_rate"],
                "optional": ["industry_average", "department", "employee_count"],
                "example_row": {"turnover_rate": 45, "industry_average": 70, "department": "FOH"}
            }
        }
    
    # Find optional columns
    industry_col = find_column(column_def["industry_average"])
    department_col = find_column(column_def.get("department", []))
    
    # Process each row
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            turnover_rate = float(row[turnover_col])
            industry_average = float(row[industry_col]) if industry_col and pd.notna(row[industry_col]) else 70.0
            
            params = {
                "turnover_rate": turnover_rate,
                "industry_average": industry_average
            }
            
            result, status_code = run_retention(params)
            if result.get("status") == "success":
                if department_col and pd.notna(row[department_col]):
                    result["department"] = row[department_col]
                results.append(result)
            else:
                errors.append({"row": idx + 1, "error": result.get("message", "Unknown error")})
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})
    
    if not results and errors:
        return {
            "status": "error",
            "message": f"Failed to process any rows. First error: {errors[0]['error']}",
            "errors": errors[:5]  # Return first 5 errors
        }
    
    # Generate summary - access data directly from the response structure
    avg_turnover = sum(r["data"]["turnover_rate"] for r in results) / len(results)
    avg_retention = sum(r["data"]["retention_rate"] for r in results) / len(results)
    
    return {
        "status": "success",
        "analysis_type": "staff_retention",
        "summary": {
            "total_records": len(results),
            "average_turnover_rate": round(avg_turnover, 2),
            "average_retention_rate": round(avg_retention, 2),
            "errors_count": len(errors)
        },
        "results": results,
        "errors": errors if errors else None,
        "business_report": _generate_retention_summary_report(results)
    }


def _process_scheduling_csv(df: pd.DataFrame, column_def: Dict, original_columns: List[str]) -> Dict[str, Any]:
    """Process CSV for Labor Scheduling Analysis."""
    col_map = {c.lower().strip(): c for c in df.columns}
    
    def find_column(target_variations):
        for var in target_variations:
            if var in col_map:
                return col_map[var]
        return None
    
    # Check required columns
    sales_col = find_column(column_def["total_sales"])
    hours_col = find_column(column_def["labor_hours"])
    rate_col = find_column(column_def["hourly_rate"])
    
    missing = []
    if not sales_col:
        missing.append("total_sales")
    if not hours_col:
        missing.append("labor_hours")
    if not rate_col:
        missing.append("hourly_rate")
    
    if missing:
        return {
            "status": "error",
            "message": f"Missing required columns: {', '.join(missing)}",
            "found_columns": original_columns,
            "help": """Labor Scheduling Analysis requires:
- **Required:** total_sales, labor_hours (or hours_worked), hourly_rate
- **Optional:** peak_hours (busy period hours)

Example CSV format:
date,total_sales,labor_hours,hourly_rate,peak_hours
2025-01-01,50000,800,15,200
2025-01-02,45000,750,15,180
2025-01-03,55000,850,15,220""",
            "expected_format": {
                "required": ["total_sales", "labor_hours", "hourly_rate"],
                "optional": ["peak_hours", "date"],
                "example_row": {"date": "2025-01-01", "total_sales": 50000, "labor_hours": 800, "hourly_rate": 15, "peak_hours": 200}
            }
        }
    
    # Find optional columns
    peak_col = find_column(column_def.get("peak_hours", []))
    date_col = find_column(column_def.get("date", []))
    
    # Process each row
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            total_sales = float(row[sales_col])
            labor_hours = float(row[hours_col])
            hourly_rate = float(row[rate_col])
            
            params = {
                "total_sales": total_sales,
                "labor_hours": labor_hours,
                "hourly_rate": hourly_rate
            }
            
            if peak_col and pd.notna(row[peak_col]):
                params["peak_hours"] = float(row[peak_col])
            
            result, status_code = run_scheduling(params)
            if result.get("status") == "success":
                if date_col and pd.notna(row[date_col]):
                    result["date"] = str(row[date_col])
                results.append(result)
            else:
                errors.append({"row": idx + 1, "error": result.get("message", "Unknown error")})
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})
    
    if not results and errors:
        return {
            "status": "error",
            "message": f"Failed to process any rows. First error: {errors[0]['error']}",
            "errors": errors[:5]
        }
    
    # Generate summary - access data directly from the response structure
    total_sales = sum(r["data"]["total_sales"] for r in results)
    total_hours = sum(r["data"]["labor_hours"] for r in results)
    avg_labor_pct = sum(r["data"]["labor_percent"] for r in results) / len(results)
    
    return {
        "status": "success",
        "analysis_type": "labor_scheduling",
        "summary": {
            "total_records": len(results),
            "total_sales": round(total_sales, 2),
            "total_labor_hours": round(total_hours, 2),
            "average_labor_percent": round(avg_labor_pct, 2),
            "errors_count": len(errors)
        },
        "results": results,
        "errors": errors if errors else None,
        "business_report": _generate_scheduling_summary_report(results)
    }


def _process_performance_csv(df: pd.DataFrame, column_def: Dict, original_columns: List[str]) -> Dict[str, Any]:
    """Process CSV for Performance Management Analysis."""
    col_map = {c.lower().strip(): c for c in df.columns}
    
    def find_column(target_variations):
        for var in target_variations:
            if var in col_map:
                return col_map[var]
        return None
    
    # Check for at least one performance metric
    csat_col = find_column(column_def["customer_satisfaction"])
    sales_col = find_column(column_def["sales_performance"])
    efficiency_col = find_column(column_def["efficiency_score"])
    attendance_col = find_column(column_def["attendance_rate"])
    
    if not any([csat_col, sales_col, efficiency_col, attendance_col]):
        return {
            "status": "error",
            "message": "At least one performance metric column is required",
            "found_columns": original_columns,
            "help": """Performance Management Analysis requires at least one of:
- customer_satisfaction (0-100 score)
- sales_performance (percentage of target)
- efficiency_score (0-100 score)
- attendance_rate (0-100 percentage)

Example CSV format:
employee_name,department,customer_satisfaction,sales_performance,efficiency_score,attendance_rate
John Smith,FOH,92,105,88,98
Jane Doe,BOH,85,95,92,96
Mike Johnson,Management,88,110,85,99""",
            "expected_format": {
                "required": ["At least one of: customer_satisfaction, sales_performance, efficiency_score, attendance_rate"],
                "optional": ["employee_name", "department"],
                "example_row": {"employee_name": "John Smith", "customer_satisfaction": 92, "sales_performance": 105, "efficiency_score": 88, "attendance_rate": 98}
            }
        }
    
    # Find optional columns
    name_col = find_column(column_def.get("employee_name", []))
    dept_col = find_column(column_def.get("department", []))
    
    # Process each row
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            params = {}
            
            if csat_col and pd.notna(row[csat_col]):
                params["customer_satisfaction"] = float(row[csat_col])
            if sales_col and pd.notna(row[sales_col]):
                params["sales_performance"] = float(row[sales_col])
            if efficiency_col and pd.notna(row[efficiency_col]):
                params["efficiency_score"] = float(row[efficiency_col])
            if attendance_col and pd.notna(row[attendance_col]):
                params["attendance_rate"] = float(row[attendance_col])
            
            if not params:
                errors.append({"row": idx + 1, "error": "No valid performance metrics found"})
                continue
            
            result, status_code = run_performance(params)
            if result.get("status") == "success":
                if name_col and pd.notna(row[name_col]):
                    result["employee_name"] = row[name_col]
                if dept_col and pd.notna(row[dept_col]):
                    result["department"] = row[dept_col]
                results.append(result)
            else:
                errors.append({"row": idx + 1, "error": result.get("message", "Unknown error")})
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})
    
    if not results and errors:
        return {
            "status": "error",
            "message": f"Failed to process any rows. First error: {errors[0]['error']}",
            "errors": errors[:5]
        }
    
    # Generate summary - access data directly from the response structure
    avg_score = sum(r["data"]["overall_score"] for r in results) / len(results)
    
    return {
        "status": "success",
        "analysis_type": "performance_management",
        "summary": {
            "total_records": len(results),
            "average_overall_score": round(avg_score, 2),
            "errors_count": len(errors)
        },
        "results": results,
        "errors": errors if errors else None,
        "business_report": _generate_performance_summary_report(results)
    }


def _generate_retention_summary_report(results: List[Dict]) -> str:
    """Generate a summary business report for retention analysis."""
    if not results:
        return "No data available for report."
    
    avg_turnover = sum(r["data"]["turnover_rate"] for r in results) / len(results)
    avg_retention = sum(r["data"]["retention_rate"] for r in results) / len(results)
    total_cost = sum(r["data"]["estimated_annual_cost"] for r in results)
    
    report = f"""
RESTAURANT CONSULTING REPORT — STAFF RETENTION SUMMARY
=======================================================
Records Analyzed: {len(results)}

KEY METRICS:
• Average Turnover Rate: {avg_turnover:.1f}%
• Average Retention Rate: {avg_retention:.1f}%
• Total Estimated Annual Turnover Cost: ${total_cost:,.0f}

ANALYSIS BY DEPARTMENT:
"""
    
    # Group by department if available
    departments = {}
    for r in results:
        dept = r.get("department", "General")
        if dept not in departments:
            departments[dept] = []
        departments[dept].append(r)
    
    for dept, dept_results in departments.items():
        dept_avg = sum(r["data"]["turnover_rate"] for r in dept_results) / len(dept_results)
        report += f"• {dept}: {dept_avg:.1f}% turnover\n"
    
    report += "\nRECOMMENDATIONS:\n"
    # Aggregate unique recommendations
    all_recs = set()
    for r in results[:3]:  # Take recommendations from first 3 results
        for rec in r.get("insights", [])[:2]:
            all_recs.add(rec)
    
    for i, rec in enumerate(list(all_recs)[:5], 1):
        report += f"{i}. {rec}\n"
    
    return report.strip()


def _generate_scheduling_summary_report(results: List[Dict]) -> str:
    """Generate a summary business report for scheduling analysis."""
    if not results:
        return "No data available for report."
    
    total_sales = sum(r["data"]["total_sales"] for r in results)
    total_hours = sum(r["data"]["labor_hours"] for r in results)
    avg_labor_pct = sum(r["data"]["labor_percent"] for r in results) / len(results)
    total_labor_cost = sum(r["data"]["total_labor_cost"] for r in results)
    
    report = f"""
RESTAURANT CONSULTING REPORT — LABOR SCHEDULING SUMMARY
========================================================
Records Analyzed: {len(results)}

KEY METRICS:
• Total Sales: ${total_sales:,.2f}
• Total Labor Hours: {total_hours:.1f}
• Total Labor Cost: ${total_labor_cost:,.2f}
• Average Labor Percentage: {avg_labor_pct:.1f}%

PERFORMANCE BREAKDOWN:
"""
    
    # Count performance ratings
    ratings = {}
    for r in results:
        rating = r["data"]["performance_rating"]
        ratings[rating] = ratings.get(rating, 0) + 1
    
    for rating, count in sorted(ratings.items()):
        report += f"• {rating}: {count} records ({count/len(results)*100:.0f}%)\n"
    
    report += "\nRECOMMENDATIONS:\n"
    all_recs = set()
    for r in results[:3]:
        for rec in r.get("insights", [])[:2]:
            all_recs.add(rec)
    
    for i, rec in enumerate(list(all_recs)[:5], 1):
        report += f"{i}. {rec}\n"
    
    return report.strip()


def _generate_performance_summary_report(results: List[Dict]) -> str:
    """Generate a summary business report for performance analysis."""
    if not results:
        return "No data available for report."
    
    avg_score = sum(r["data"]["overall_score"] for r in results) / len(results)
    
    report = f"""
RESTAURANT CONSULTING REPORT — PERFORMANCE MANAGEMENT SUMMARY
==============================================================
Records Analyzed: {len(results)}

KEY METRICS:
• Average Overall Score: {avg_score:.1f}

INDIVIDUAL PERFORMANCE:
"""
    
    # List top performers if names available
    named_results = [r for r in results if r.get("employee_name")]
    if named_results:
        sorted_results = sorted(named_results, key=lambda x: x["data"]["overall_score"], reverse=True)
        for r in sorted_results[:5]:
            name = r.get("employee_name", "Unknown")
            score = r["data"]["overall_score"]
            rating = r["data"]["performance_rating"]
            report += f"• {name}: {score:.1f} ({rating})\n"
    else:
        # Group by performance rating
        ratings = {}
        for r in results:
            rating = r["data"]["performance_rating"]
            ratings[rating] = ratings.get(rating, 0) + 1
        
        for rating, count in sorted(ratings.items()):
            report += f"• {rating}: {count} employees\n"
    
    report += "\nRECOMMENDATIONS:\n"
    all_recs = set()
    for r in results[:3]:
        for rec in r.get("insights", [])[:2]:
            all_recs.add(rec)
    
    for i, rec in enumerate(list(all_recs)[:5], 1):
        report += f"{i}. {rec}\n"
    
    return report.strip()
