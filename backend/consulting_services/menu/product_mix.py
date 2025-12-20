"""
Menu Product Mix Analysis Task
Analyzes menu item performance using Menu Engineering Matrix with integration to restaurant inventory app data.
"""

import os
from typing import Optional
from backend.shared.utils.common import success_payload, error_payload
from backend.consulting_services.kpi.kpi_utils import format_business_report
from .analysis_functions import (
    load_restaurant_data,
    validate_data_integrity,
    join_menu_data,
    calculate_product_mix_analysis
)


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate comprehensive product mix analysis using Menu Engineering Matrix.

    Integrates with restaurant_inventory_app data (recipes.json, menu_items.json, sales_data.json)
    to perform quadrant classification, category analysis, and strategic recommendations.

    Args:
        params: Dictionary containing:
            - recipe_data_path (str, optional): Path to recipes.json
            - menu_items_path (str, optional): Path to menu_items.json
            - sales_data_path (str, optional): Path to sales_data.json
            - category_filter (str, optional): Filter analysis to specific category
            - validate_calculations (bool, optional): Validate precalculated metrics (default: False)
            - use_precalculated (bool, optional): Use precalculated metrics from source data (default: True)
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "menu", "product_mix"

    try:
        # Default data paths (pointing to restaurant_inventory_app)
        # Use environment variable for flexibility across environments
        default_data_dir = os.getenv("RESTAURANT_DATA_DIR", "/home/jkatz015/repos/restaurant_inventory_app/data")

        # Extract parameters with defaults
        recipe_data_path = params.get("recipe_data_path", os.path.join(default_data_dir, "recipes.json"))
        menu_items_path = params.get("menu_items_path", os.path.join(default_data_dir, "menu_items.json"))
        sales_data_path = params.get("sales_data_path", os.path.join(default_data_dir, "sales_data.json"))

        category_filter = params.get("category_filter", None)
        validate_calculations = params.get("validate_calculations", False)
        use_precalculated = params.get("use_precalculated", True)

        # STEP 1: Load restaurant data from 3 JSON files
        try:
            recipes, menu_items, sales = load_restaurant_data(
                recipe_data_path,
                menu_items_path,
                sales_data_path
            )
        except FileNotFoundError as e:
            return error_payload(service, subtask, f"Data file not found: {str(e)}")
        except Exception as e:
            return error_payload(service, subtask, f"Failed to load restaurant data: {str(e)}")

        # STEP 2: Validate data integrity
        try:
            validation_report = validate_data_integrity(
                recipes,
                menu_items,
                sales,
                validate_calculations=validate_calculations
            )

            # If there are critical errors, return error payload
            if validation_report["errors"]:
                error_messages = "; ".join(validation_report["errors"])
                return error_payload(service, subtask, f"Data integrity errors: {error_messages}")
        except Exception as e:
            return error_payload(service, subtask, f"Data validation failed: {str(e)}")

        # STEP 3: Join data using FK relationships
        try:
            unified_data = join_menu_data(
                recipes,
                menu_items,
                sales,
                use_precalculated=use_precalculated
            )
        except Exception as e:
            return error_payload(service, subtask, f"Failed to join menu data: {str(e)}")

        # STEP 4: Calculate Product Mix Analysis
        try:
            analysis_result = calculate_product_mix_analysis(
                unified_data,
                category_filter=category_filter
            )
        except Exception as e:
            return error_payload(service, subtask, f"Product mix analysis failed: {str(e)}")

        # STEP 5: Generate comprehensive business report
        try:
            # Extract key metrics for report
            overall_metrics = analysis_result["overall_metrics"]
            quadrant_summary = analysis_result["quadrant_summary"]
            top_performers = analysis_result["top_performers"]

            # Build metrics dictionary (pass raw numbers for format_business_report to format)
            metrics = {
                "Total Menu Items": overall_metrics["total_menu_items"],
                "Total Revenue": overall_metrics["total_revenue"],
                "Total Profit": overall_metrics["total_profit"],
                "Avg Contribution Margin": overall_metrics["avg_contribution_margin"],
                "Overall Food Cost Percent": overall_metrics["overall_food_cost_percent"],
                "Stars": quadrant_summary["stars"]["count"],
                "Plowhorses": quadrant_summary["plowhorses"]["count"],
                "Puzzles": quadrant_summary["puzzles"]["count"],
                "Dogs": quadrant_summary["dogs"]["count"]
            }

            # Determine performance rating based on quadrant distribution
            star_percent = (quadrant_summary["stars"]["count"] / overall_metrics["total_menu_items"]) * 100 if overall_metrics["total_menu_items"] > 0 else 0
            dog_percent = (quadrant_summary["dogs"]["count"] / overall_metrics["total_menu_items"]) * 100 if overall_metrics["total_menu_items"] > 0 else 0

            if star_percent >= 30 and dog_percent <= 15:
                performance = "Excellent"
            elif star_percent >= 20 and dog_percent <= 25:
                performance = "Good"
            elif star_percent >= 10 and dog_percent <= 35:
                performance = "Acceptable"
            else:
                performance = "Needs Improvement"

            # Build strategic recommendations
            recommendations = []

            # Recommendation 1: Stars strategy
            if quadrant_summary["stars"]["count"] > 0:
                star_revenue_percent = (quadrant_summary["stars"]["total_revenue"] / overall_metrics["total_revenue"]) * 100 if overall_metrics["total_revenue"] > 0 else 0
                recommendations.append(
                    f"Promote your {quadrant_summary['stars']['count']} Star items - "
                    f"they generate {star_revenue_percent:.1f}% of revenue and should be highlighted on menu."
                )

            # Recommendation 2: Dogs strategy
            if quadrant_summary["dogs"]["count"] > 0:
                recommendations.append(
                    f"Consider removing or repositioning {quadrant_summary['dogs']['count']} Dog items - "
                    f"they have low popularity and profitability."
                )

            # Recommendation 3: Puzzles strategy
            if quadrant_summary["puzzles"]["count"] > 0:
                recommendations.append(
                    f"Increase marketing for {quadrant_summary['puzzles']['count']} Puzzle items - "
                    f"they have high profitability but need better promotion."
                )

            # Recommendation 4: Plowhorses strategy
            if quadrant_summary["plowhorses"]["count"] > 0:
                recommendations.append(
                    f"Optimize costs for {quadrant_summary['plowhorses']['count']} Plowhorse items - "
                    f"they're popular but need better profit margins."
                )

            # Recommendation 5: Category insights
            category_breakdown = analysis_result["category_breakdown"]
            for category_name, category_data in category_breakdown.items():
                if category_data["avg_food_cost_percent"] > 35:
                    recommendations.append(
                        f"{category_name} category has high food cost ({category_data['avg_food_cost_percent']:.1f}%) - "
                        f"review recipes and supplier costs."
                    )

            # Industry benchmarks
            benchmarks = {
                "Food Cost %": "28-35% (Restaurant Industry Standard)",
                "Contribution Margin": "65-72% (Optimal Range)",
                "Stars Distribution": "25-35% of menu items (Ideal)",
                "Dogs Distribution": "< 15% of menu items (Maximum Acceptable)"
            }

            # Additional insights
            additional_data = {
                "Top Profit Item": top_performers["by_total_profit"][0]["menu_name"] if top_performers.get("by_total_profit") and len(top_performers["by_total_profit"]) > 0 else "N/A",
                "Top Revenue Item": top_performers["by_revenue"][0]["menu_name"] if top_performers.get("by_revenue") and len(top_performers["by_revenue"]) > 0 else "N/A",
                "Most Popular Item": top_performers["by_units_sold"][0]["menu_name"] if top_performers.get("by_units_sold") and len(top_performers["by_units_sold"]) > 0 else "N/A",
                "Categories Analyzed": len(category_breakdown),
                "Validation Warnings": len(validation_report.get("warnings", []))
            }

            # Generate business report
            business_report = format_business_report(
                analysis_type="Product Mix Analysis (Menu Engineering Matrix)",
                metrics=metrics,
                performance={"rating": performance, "color": "blue"},
                recommendations=recommendations,
                benchmarks=benchmarks,
                additional_data=additional_data
            )

        except Exception as e:
            return error_payload(service, subtask, f"Failed to generate business report: {str(e)}")

        # STEP 6: Return success payload with comprehensive data
        return success_payload(
            service, subtask, params, {
                "analysis_type": "Product Mix Analysis",
                "business_report": business_report["business_report"],
                "business_report_html": business_report["business_report_html"],
                "metrics": metrics,
                "performance": performance,
                "recommendations": recommendations,
                "menu_engineering_matrix": analysis_result["menu_engineering_matrix"],
                "quadrant_summary": analysis_result["quadrant_summary"],
                "category_breakdown": analysis_result["category_breakdown"],
                "top_performers": analysis_result["top_performers"],
                "bottom_performers": analysis_result["bottom_performers"],
                "overall_metrics": analysis_result["overall_metrics"],
                "validation_report": validation_report
            }, recommendations
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Unexpected error: {str(e)}")
