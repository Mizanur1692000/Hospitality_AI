"""
Cost Analysis CSV Data Processor
Handles CSV file uploads for Labor Cost, Food Cost, Prime Cost, and Beverage/Liquor Analysis.
"""

import io
from typing import Any, Dict, List
import pandas as pd

from backend.consulting_services.kpi.kpi_analysis import run as run_kpi_analysis


def process_cost_csv_data(csv_file, analysis_type: str = "auto") -> Dict[str, Any]:
    """
    Process uploaded CSV file for cost analysis.
    
    Args:
        csv_file: Uploaded CSV file object
        analysis_type: Type of analysis - "labor", "food", "prime", "liquor", or "auto" (detect from columns)
    
    Expected CSV columns for each analysis type:
    
    Labor Cost Analysis:
        Required: total_sales, labor_cost, hours_worked
        Optional: overtime_hours, covers, department
    
    Food Cost Analysis:
        Required: total_sales, food_cost
        Optional: waste_cost, covers, beginning_inventory, ending_inventory
    
    Prime Cost Analysis:
        Required: total_sales, labor_cost, food_cost
        Optional: covers, department
    
    Liquor/Beverage Analysis:
        Required: total_sales, liquor_cost OR beverage_cost
        Optional: covers, waste_cost, beginning_inventory, ending_inventory
    
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
        labor_columns = {
            "total_sales": ["total_sales", "sales", "revenue", "daily_sales"],
            "labor_cost": ["labor_cost", "labor_costs", "payroll", "wages"],
            "hours_worked": ["hours_worked", "labor_hours", "total_hours", "hours"],
            "overtime_hours": ["overtime_hours", "overtime", "ot_hours"],
            "covers": ["covers", "customer_count", "guests"],
            "department": ["department", "dept", "team"]
        }
        
        food_columns = {
            "total_sales": ["total_sales", "sales", "revenue", "daily_sales"],
            "food_cost": ["food_cost", "food_costs", "cogs", "cost_of_goods"],
            "waste_cost": ["waste_cost", "waste", "spoilage", "food_waste"],
            "covers": ["covers", "customer_count", "guests"],
            "beginning_inventory": ["beginning_inventory", "start_inventory", "opening_inventory"],
            "ending_inventory": ["ending_inventory", "end_inventory", "closing_inventory"]
        }
        
        prime_columns = {
            "total_sales": ["total_sales", "sales", "revenue", "daily_sales"],
            "labor_cost": ["labor_cost", "labor_costs", "payroll", "wages"],
            "food_cost": ["food_cost", "food_costs", "cogs", "cost_of_goods"],
            "covers": ["covers", "customer_count", "guests"],
            "department": ["department", "dept", "team"]
        }
        
        liquor_columns = {
            "total_sales": ["total_sales", "sales", "revenue", "daily_sales"],
            "liquor_cost": ["liquor_cost", "beverage_cost", "bar_cost", "alcohol_cost", "drink_cost"],
            "waste_cost": ["waste_cost", "waste", "spillage", "breakage"],
            "covers": ["covers", "customer_count", "guests"],
            "beginning_inventory": ["beginning_inventory", "start_inventory", "opening_inventory"],
            "ending_inventory": ["ending_inventory", "end_inventory", "closing_inventory"]
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
            labor_mapped = map_columns(labor_columns)
            food_mapped = map_columns(food_columns)
            prime_mapped = map_columns(prime_columns)
            liquor_mapped = map_columns(liquor_columns)
            
            # Score each type by number of matched required columns
            scores = {
                "labor": len([k for k in ["total_sales", "labor_cost", "hours_worked"] if k in labor_mapped]),
                "food": len([k for k in ["total_sales", "food_cost"] if k in food_mapped]),
                "prime": len([k for k in ["total_sales", "labor_cost", "food_cost"] if k in prime_mapped]),
                "liquor": len([k for k in ["total_sales", "liquor_cost"] if k in liquor_mapped])
            }
            
            # Pick the type with highest score
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                analysis_type = best_type
            else:
                # Provide helpful error message
                return {
                    "status": "error",
                    "message": "Could not determine cost analysis type from CSV columns",
                    "found_columns": original_columns,
                    "help": """Cost Analysis requires specific columns based on analysis type:

**Labor Cost Analysis:**
- Required: total_sales, labor_cost, hours_worked
- Optional: overtime_hours, covers, department

**Food Cost Analysis:**
- Required: total_sales, food_cost
- Optional: waste_cost, covers, beginning_inventory, ending_inventory

**Prime Cost Analysis:**
- Required: total_sales, labor_cost, food_cost
- Optional: covers, department

**Liquor/Beverage Analysis:**
- Required: total_sales, liquor_cost (or beverage_cost)
- Optional: waste_cost, covers, beginning_inventory, ending_inventory""",
                    "expected_formats": {
                        "labor": {"required": ["total_sales", "labor_cost", "hours_worked"], "optional": ["overtime_hours", "covers"]},
                        "food": {"required": ["total_sales", "food_cost"], "optional": ["waste_cost", "covers"]},
                        "prime": {"required": ["total_sales", "labor_cost", "food_cost"], "optional": ["covers"]},
                        "liquor": {"required": ["total_sales", "liquor_cost"], "optional": ["waste_cost", "covers"]}
                    }
                }
        
        # Process based on analysis type
        if analysis_type == "labor":
            return _process_labor_cost_csv(df, labor_columns, original_columns)
        elif analysis_type == "food":
            return _process_food_cost_csv(df, food_columns, original_columns)
        elif analysis_type == "prime":
            return _process_prime_cost_csv(df, prime_columns, original_columns)
        elif analysis_type == "liquor":
            return _process_liquor_cost_csv(df, liquor_columns, original_columns)
        else:
            return {
                "status": "error",
                "message": f"Unknown analysis type: {analysis_type}",
                "supported_types": ["labor", "food", "prime", "liquor", "auto"]
            }
    
    except pd.errors.EmptyDataError:
        return {
            "status": "error",
            "message": "The CSV file is empty or has no valid data"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing cost analysis CSV: {str(e)}",
            "error_type": type(e).__name__
        }


def _process_labor_cost_csv(df: pd.DataFrame, column_def: Dict, original_columns: List[str]) -> Dict[str, Any]:
    """Process CSV for Labor Cost Analysis."""
    col_map = {c.lower().strip(): c for c in df.columns}
    
    def find_column(target_variations):
        for var in target_variations:
            if var in col_map:
                return col_map[var]
        return None
    
    # Check required columns
    sales_col = find_column(column_def["total_sales"])
    labor_col = find_column(column_def["labor_cost"])
    hours_col = find_column(column_def["hours_worked"])
    
    missing = []
    if not sales_col:
        missing.append("total_sales")
    if not labor_col:
        missing.append("labor_cost")
    if not hours_col:
        missing.append("hours_worked")
    
    if missing:
        return {
            "status": "error",
            "message": f"Missing required columns: {', '.join(missing)}",
            "found_columns": original_columns,
            "help": """Labor Cost Analysis requires:
- **Required:** total_sales, labor_cost, hours_worked
- **Optional:** overtime_hours, covers (for productivity metrics)

Example CSV format:
date,total_sales,labor_cost,hours_worked,overtime_hours,covers
2025-01-01,50000,15000,800,40,2000
2025-01-02,45000,14000,750,35,1800""",
            "expected_format": {
                "required": ["total_sales", "labor_cost", "hours_worked"],
                "optional": ["overtime_hours", "covers", "department"],
                "example_row": {"total_sales": 50000, "labor_cost": 15000, "hours_worked": 800, "overtime_hours": 40, "covers": 2000}
            }
        }
    
    # Find optional columns
    overtime_col = find_column(column_def.get("overtime_hours", []))
    covers_col = find_column(column_def.get("covers", []))
    dept_col = find_column(column_def.get("department", []))
    
    # Process each row using KPI analysis
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            total_sales = float(row[sales_col])
            labor_cost = float(row[labor_col])
            hours_worked = float(row[hours_col])
            
            params = {
                "total_sales": total_sales,
                "labor_cost": labor_cost,
                "hours_worked": hours_worked
            }
            
            if overtime_col and pd.notna(row[overtime_col]):
                params["overtime_hours"] = float(row[overtime_col])
            if covers_col and pd.notna(row[covers_col]):
                params["covers"] = int(row[covers_col])
            
            # Use KPI analysis for labor cost calculations
            result, status_code = run_kpi_analysis(params)
            if result.get("status") == "success":
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
    
    # Generate summary
    total_sales = sum(r.get("total_sales", 0) for r in results)
    total_labor_cost = sum(r.get("labor_cost", 0) for r in results)
    avg_labor_pct = (total_labor_cost / total_sales * 100) if total_sales > 0 else 0
    total_hours = sum(r.get("hours_worked", 0) for r in results)
    
    return {
        "status": "success",
        "analysis_type": "labor_cost",
        "summary": {
            "total_records": len(results),
            "total_sales": round(total_sales, 2),
            "total_labor_cost": round(total_labor_cost, 2),
            "labor_cost_percent": round(avg_labor_pct, 2),
            "total_hours": round(total_hours, 2),
            "errors_count": len(errors)
        },
        "results": results,
        "errors": errors if errors else None,
        "business_report": _generate_labor_cost_report(results)
    }


def _process_food_cost_csv(df: pd.DataFrame, column_def: Dict, original_columns: List[str]) -> Dict[str, Any]:
    """Process CSV for Food Cost Analysis."""
    col_map = {c.lower().strip(): c for c in df.columns}
    
    def find_column(target_variations):
        for var in target_variations:
            if var in col_map:
                return col_map[var]
        return None
    
    # Check required columns
    sales_col = find_column(column_def["total_sales"])
    food_col = find_column(column_def["food_cost"])
    
    missing = []
    if not sales_col:
        missing.append("total_sales")
    if not food_col:
        missing.append("food_cost")
    
    if missing:
        return {
            "status": "error",
            "message": f"Missing required columns: {', '.join(missing)}",
            "found_columns": original_columns,
            "help": """Food Cost Analysis requires:
- **Required:** total_sales, food_cost
- **Optional:** waste_cost, covers, beginning_inventory, ending_inventory

Example CSV format:
date,total_sales,food_cost,waste_cost,covers
2025-01-01,50000,14000,800,2000
2025-01-02,45000,13000,750,1800""",
            "expected_format": {
                "required": ["total_sales", "food_cost"],
                "optional": ["waste_cost", "covers", "beginning_inventory", "ending_inventory"],
                "example_row": {"total_sales": 50000, "food_cost": 14000, "waste_cost": 800, "covers": 2000}
            }
        }
    
    # Find optional columns
    waste_col = find_column(column_def.get("waste_cost", []))
    covers_col = find_column(column_def.get("covers", []))
    
    # Process each row
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            total_sales = float(row[sales_col])
            food_cost = float(row[food_col])
            
            params = {
                "total_sales": total_sales,
                "food_cost": food_cost
            }
            
            if waste_col and pd.notna(row[waste_col]):
                params["waste_cost"] = float(row[waste_col])
            if covers_col and pd.notna(row[covers_col]):
                params["covers"] = int(row[covers_col])
            
            result, status_code = run_kpi_analysis(params)
            if result.get("status") == "success":
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
    
    # Generate summary
    total_sales = sum(r.get("total_sales", 0) for r in results)
    total_food_cost = sum(r.get("food_cost", 0) for r in results)
    avg_food_pct = (total_food_cost / total_sales * 100) if total_sales > 0 else 0
    
    return {
        "status": "success",
        "analysis_type": "food_cost",
        "summary": {
            "total_records": len(results),
            "total_sales": round(total_sales, 2),
            "total_food_cost": round(total_food_cost, 2),
            "food_cost_percent": round(avg_food_pct, 2),
            "errors_count": len(errors)
        },
        "results": results,
        "errors": errors if errors else None,
        "business_report": _generate_food_cost_report(results)
    }


def _process_prime_cost_csv(df: pd.DataFrame, column_def: Dict, original_columns: List[str]) -> Dict[str, Any]:
    """Process CSV for Prime Cost Analysis."""
    col_map = {c.lower().strip(): c for c in df.columns}
    
    def find_column(target_variations):
        for var in target_variations:
            if var in col_map:
                return col_map[var]
        return None
    
    # Check required columns
    sales_col = find_column(column_def["total_sales"])
    labor_col = find_column(column_def["labor_cost"])
    food_col = find_column(column_def["food_cost"])
    
    missing = []
    if not sales_col:
        missing.append("total_sales")
    if not labor_col:
        missing.append("labor_cost")
    if not food_col:
        missing.append("food_cost")
    
    if missing:
        return {
            "status": "error",
            "message": f"Missing required columns: {', '.join(missing)}",
            "found_columns": original_columns,
            "help": """Prime Cost Analysis requires:
- **Required:** total_sales, labor_cost, food_cost
- **Optional:** covers, department

Example CSV format:
date,total_sales,labor_cost,food_cost,covers
2025-01-01,50000,15000,14000,2000
2025-01-02,45000,14000,13000,1800""",
            "expected_format": {
                "required": ["total_sales", "labor_cost", "food_cost"],
                "optional": ["covers", "department"],
                "example_row": {"total_sales": 50000, "labor_cost": 15000, "food_cost": 14000, "covers": 2000}
            }
        }
    
    # Find optional columns
    covers_col = find_column(column_def.get("covers", []))
    dept_col = find_column(column_def.get("department", []))
    
    # Process each row
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            total_sales = float(row[sales_col])
            labor_cost = float(row[labor_col])
            food_cost = float(row[food_col])
            
            params = {
                "total_sales": total_sales,
                "labor_cost": labor_cost,
                "food_cost": food_cost
            }
            
            if covers_col and pd.notna(row[covers_col]):
                params["covers"] = int(row[covers_col])
            
            result, status_code = run_kpi_analysis(params)
            if result.get("status") == "success":
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
    
    # Generate summary
    total_sales = sum(r.get("total_sales", 0) for r in results)
    total_labor_cost = sum(r.get("labor_cost", 0) for r in results)
    total_food_cost = sum(r.get("food_cost", 0) for r in results)
    total_prime_cost = total_labor_cost + total_food_cost
    avg_prime_pct = (total_prime_cost / total_sales * 100) if total_sales > 0 else 0
    
    return {
        "status": "success",
        "analysis_type": "prime_cost",
        "summary": {
            "total_records": len(results),
            "total_sales": round(total_sales, 2),
            "total_prime_cost": round(total_prime_cost, 2),
            "prime_cost_percent": round(avg_prime_pct, 2),
            "errors_count": len(errors)
        },
        "results": results,
        "errors": errors if errors else None,
        "business_report": _generate_prime_cost_report(results)
    }


def _process_liquor_cost_csv(df: pd.DataFrame, column_def: Dict, original_columns: List[str]) -> Dict[str, Any]:
    """Process CSV for Liquor/Beverage Cost Analysis."""
    col_map = {c.lower().strip(): c for c in df.columns}
    
    def find_column(target_variations):
        for var in target_variations:
            if var in col_map:
                return col_map[var]
        return None
    
    # Check required columns
    sales_col = find_column(column_def["total_sales"])
    liquor_col = find_column(column_def["liquor_cost"])
    
    missing = []
    if not sales_col:
        missing.append("total_sales")
    if not liquor_col:
        missing.append("liquor_cost (or beverage_cost)")
    
    if missing:
        return {
            "status": "error",
            "message": f"Missing required columns: {', '.join(missing)}",
            "found_columns": original_columns,
            "help": """Liquor/Beverage Analysis requires:
- **Required:** total_sales, liquor_cost (or beverage_cost)
- **Optional:** waste_cost, covers, beginning_inventory, ending_inventory

Example CSV format:
date,total_sales,liquor_cost,waste_cost,covers
2025-01-01,50000,8000,200,2000
2025-01-02,45000,7500,180,1800""",
            "expected_format": {
                "required": ["total_sales", "liquor_cost"],
                "optional": ["waste_cost", "covers", "beginning_inventory", "ending_inventory"],
                "example_row": {"total_sales": 50000, "liquor_cost": 8000, "waste_cost": 200, "covers": 2000}
            }
        }
    
    # Find optional columns
    waste_col = find_column(column_def.get("waste_cost", []))
    covers_col = find_column(column_def.get("covers", []))
    
    # Process each row
    results = []
    errors = []
    
    for idx, row in df.iterrows():
        try:
            total_sales = float(row[sales_col])
            liquor_cost = float(row[liquor_col])
            
            # Calculate liquor cost percentage
            liquor_pct = (liquor_cost / total_sales * 100) if total_sales > 0 else 0
            
            result_data = {
                "total_sales": total_sales,
                "liquor_cost": liquor_cost,
                "liquor_cost_percent": liquor_pct,
                "status": "success"
            }
            
            if waste_col and pd.notna(row[waste_col]):
                waste_cost = float(row[waste_col])
                result_data["waste_cost"] = waste_cost
                result_data["effective_liquor_cost"] = liquor_cost + waste_cost
                result_data["effective_liquor_percent"] = ((liquor_cost + waste_cost) / total_sales * 100) if total_sales > 0 else 0
                
            if covers_col and pd.notna(row[covers_col]):
                covers = int(row[covers_col])
                result_data["covers"] = covers
                result_data["liquor_cost_per_cover"] = liquor_cost / covers if covers > 0 else 0
            
            results.append(result_data)
            
        except Exception as e:
            errors.append({"row": idx + 1, "error": str(e)})
    
    if not results and errors:
        return {
            "status": "error",
            "message": f"Failed to process any rows. First error: {errors[0]['error']}",
            "errors": errors[:5]
        }
    
    # Generate summary
    total_sales = sum(r["total_sales"] for r in results)
    total_liquor_cost = sum(r["liquor_cost"] for r in results)
    avg_liquor_pct = (total_liquor_cost / total_sales * 100) if total_sales > 0 else 0
    
    return {
        "status": "success",
        "analysis_type": "liquor_cost",
        "summary": {
            "total_records": len(results),
            "total_sales": round(total_sales, 2),
            "total_liquor_cost": round(total_liquor_cost, 2),
            "liquor_cost_percent": round(avg_liquor_pct, 2),
            "errors_count": len(errors)
        },
        "results": results,
        "errors": errors if errors else None,
        "business_report": _generate_liquor_cost_report(results)
    }


def _generate_labor_cost_report(results: List[Dict]) -> str:
    """Generate a summary business report for labor cost analysis."""
    if not results:
        return "No data available for report."
    
    total_sales = sum(r.get("total_sales", 0) for r in results)
    total_labor_cost = sum(r.get("labor_cost", 0) for r in results)
    avg_labor_pct = (total_labor_cost / total_sales * 100) if total_sales > 0 else 0
    total_hours = sum(r.get("hours_worked", 0) for r in results)
    
    report = f"""
RESTAURANT CONSULTING REPORT — LABOR COST ANALYSIS
==================================================
Records Analyzed: {len(results)}

KEY METRICS:
• Total Sales: ${total_sales:,.2f}
• Total Labor Cost: ${total_labor_cost:,.2f}
• Labor Cost Percentage: {avg_labor_pct:.1f}%
• Total Hours Worked: {total_hours:,.1f}
• Sales per Labor Hour: ${total_sales/total_hours:.2f}

PERFORMANCE ASSESSMENT:
• Target Range: 25-35%
• Current Status: {'✓ EXCELLENT' if avg_labor_pct <= 28 else '✓ GOOD' if avg_labor_pct <= 32 else '⚠ NEEDS ATTENTION' if avg_labor_pct <= 40 else '❌ CRITICAL'}

RECOMMENDATIONS:
1. Monitor scheduling to avoid overstaffing during slow periods
2. Cross-train staff for operational flexibility
3. Track productivity metrics (sales per labor hour)
4. Review overtime usage and implement controls
5. Consider labor scheduling software for optimization
"""
    
    return report.strip()


def _generate_food_cost_report(results: List[Dict]) -> str:
    """Generate a summary business report for food cost analysis."""
    if not results:
        return "No data available for report."
    
    total_sales = sum(r.get("total_sales", 0) for r in results)
    total_food_cost = sum(r.get("food_cost", 0) for r in results)
    avg_food_pct = (total_food_cost / total_sales * 100) if total_sales > 0 else 0
    
    report = f"""
RESTAURANT CONSULTING REPORT — FOOD COST ANALYSIS
=================================================
Records Analyzed: {len(results)}

KEY METRICS:
• Total Sales: ${total_sales:,.2f}
• Total Food Cost: ${total_food_cost:,.2f}
• Food Cost Percentage: {avg_food_pct:.1f}%

PERFORMANCE ASSESSMENT:
• Target Range: 28-35%
• Current Status: {'✓ EXCELLENT' if avg_food_pct <= 30 else '✓ GOOD' if avg_food_pct <= 33 else '⚠ NEEDS ATTENTION' if avg_food_pct <= 38 else '❌ CRITICAL'}

RECOMMENDATIONS:
1. Implement portion control standards
2. Monitor waste and spoilage closely
3. Review supplier pricing regularly
4. Update menu pricing based on true costs
5. Train staff on food handling best practices
"""
    
    return report.strip()


def _generate_prime_cost_report(results: List[Dict]) -> str:
    """Generate a summary business report for prime cost analysis."""
    if not results:
        return "No data available for report."
    
    total_sales = sum(r.get("total_sales", 0) for r in results)
    total_labor_cost = sum(r.get("labor_cost", 0) for r in results)
    total_food_cost = sum(r.get("food_cost", 0) for r in results)
    total_prime_cost = total_labor_cost + total_food_cost
    avg_prime_pct = (total_prime_cost / total_sales * 100) if total_sales > 0 else 0
    
    report = f"""
RESTAURANT CONSULTING REPORT — PRIME COST ANALYSIS
==================================================
Records Analyzed: {len(results)}

KEY METRICS:
• Total Sales: ${total_sales:,.2f}
• Total Prime Cost: ${total_prime_cost:,.2f}
  - Labor Cost: ${total_labor_cost:,.2f}
  - Food Cost: ${total_food_cost:,.2f}
• Prime Cost Percentage: {avg_prime_pct:.1f}%

PERFORMANCE ASSESSMENT:
• Target Range: 55-65%
• Current Status: {'✓ EXCELLENT' if avg_prime_pct <= 60 else '✓ GOOD' if avg_prime_pct <= 65 else '⚠ NEEDS ATTENTION' if avg_prime_pct <= 70 else '❌ CRITICAL'}

RECOMMENDATIONS:
1. Balance labor and food costs for optimal profitability
2. Implement menu engineering strategies
3. Optimize staff scheduling and portion control
4. Review pricing strategy to maintain margins
5. Monitor daily prime cost targets
"""
    
    return report.strip()


def _generate_liquor_cost_report(results: List[Dict]) -> str:
    """Generate a summary business report for liquor cost analysis."""
    if not results:
        return "No data available for report."
    
    total_sales = sum(r["total_sales"] for r in results)
    total_liquor_cost = sum(r["liquor_cost"] for r in results)
    avg_liquor_pct = (total_liquor_cost / total_sales * 100) if total_sales > 0 else 0
    
    report = f"""
RESTAURANT CONSULTING REPORT — BEVERAGE COST ANALYSIS
=====================================================
Records Analyzed: {len(results)}

KEY METRICS:
• Total Sales: ${total_sales:,.2f}
• Total Beverage Cost: ${total_liquor_cost:,.2f}
• Beverage Cost Percentage: {avg_liquor_pct:.1f}%

PERFORMANCE ASSESSMENT:
• Target Range: 18-25%
• Current Status: {'✓ EXCELLENT' if avg_liquor_pct <= 20 else '✓ GOOD' if avg_liquor_pct <= 25 else '⚠ NEEDS ATTENTION' if avg_liquor_pct <= 30 else '❌ CRITICAL'}

RECOMMENDATIONS:
1. Monitor pour costs and implement jiggers
2. Control waste and spillage
3. Review pricing on high-cost items
4. Implement inventory tracking systems
5. Train staff on proper pouring techniques
"""
    
    return report.strip()