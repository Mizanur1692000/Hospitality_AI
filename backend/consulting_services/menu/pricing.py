"""
Menu Pricing Strategy Task
Analyzes menu pricing opportunities, identifies underpriced/overpriced items, and provides strategic pricing recommendations.
"""

import os
from backend.shared.utils.common import success_payload, error_payload
from backend.consulting_services.kpi.kpi_utils import format_business_report
from .analysis_functions import (
    load_restaurant_data,
    validate_data_integrity,
    join_menu_data,
    calculate_menu_pricing_strategy
)


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Calculate comprehensive menu pricing strategy analysis.

    Integrates with restaurant_inventory_app data to identify pricing opportunities,
    analyze price positioning, and provide revenue optimization recommendations.

    Args:
        params: Dictionary containing:
            - recipe_data_path (str, optional): Path to recipes.json
            - menu_items_path (str, optional): Path to menu_items.json
            - sales_data_path (str, optional): Path to sales_data.json
            - target_food_cost (float, optional): Target food cost percentage (default: 32.0)
            - validate_calculations (bool, optional): Validate precalculated metrics (default: False)
            - use_precalculated (bool, optional): Use precalculated metrics (default: True)
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "menu", "pricing"

    try:
        # Default data paths (use environment variable for flexibility)
        default_data_dir = os.getenv("RESTAURANT_DATA_DIR", "/home/jkatz015/repos/restaurant_inventory_app/data")

        # Extract parameters with defaults
        recipe_data_path = params.get("recipe_data_path", os.path.join(default_data_dir, "recipes.json"))
        menu_items_path = params.get("menu_items_path", os.path.join(default_data_dir, "menu_items.json"))
        sales_data_path = params.get("sales_data_path", os.path.join(default_data_dir, "sales_data.json"))

        target_food_cost = float(params.get("target_food_cost", 32.0))
        validate_calculations = params.get("validate_calculations", False)
        use_precalculated = params.get("use_precalculated", True)

        # STEP 1: Load restaurant data
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

            if validation_report["errors"]:
                error_messages = "; ".join(validation_report["errors"])
                return error_payload(service, subtask, f"Data integrity errors: {error_messages}")
        except Exception as e:
            return error_payload(service, subtask, f"Data validation failed: {str(e)}")

        # STEP 3: Join data
        try:
            unified_data = join_menu_data(
                recipes,
                menu_items,
                sales,
                use_precalculated=use_precalculated
            )
        except Exception as e:
            return error_payload(service, subtask, f"Failed to join menu data: {str(e)}")

        # STEP 4: Calculate Pricing Strategy
        try:
            pricing_result = calculate_menu_pricing_strategy(
                unified_data,
                target_food_cost=target_food_cost
            )
        except Exception as e:
            return error_payload(service, subtask, f"Pricing strategy analysis failed: {str(e)}")

        # STEP 5: Generate comprehensive business report
        try:
            pricing_opportunities = pricing_result["pricing_opportunities"]
            price_positioning = pricing_result["price_positioning"]
            revenue_impact = pricing_result["revenue_impact"]
            strategic_recommendations = pricing_result["strategic_recommendations"]

            # Build metrics dictionary (pass raw numbers for format_business_report to format)
            metrics = {
                "Underpriced Items": pricing_opportunities["summary"]["underpriced_count"],
                "Overpriced Items": pricing_opportunities["summary"]["overpriced_count"],
                "Well-Priced Items": pricing_opportunities["summary"]["well_priced_count"],
                "Revenue Opportunity": revenue_impact['total_opportunity'],
                "Potential Improvement Percent": revenue_impact['percentage_improvement'],
                "Avg Price": price_positioning['price_distribution'].get('avg_price', 0),
                "Min Price": price_positioning['price_distribution'].get('min_price', 0),
                "Max Price": price_positioning['price_distribution'].get('max_price', 0),
                "Price Gaps Found": len(price_positioning["price_gaps"]),
                "Anchor Opportunities": len(price_positioning["anchor_opportunities"])
            }

            # Determine performance rating
            revenue_improvement = revenue_impact["percentage_improvement"]
            underpriced_percent = (pricing_opportunities["summary"]["underpriced_count"] /
                                 len(unified_data) * 100) if unified_data else 0

            if revenue_improvement > 10 or underpriced_percent > 30:
                performance = "Significant Opportunity"
            elif revenue_improvement > 5 or underpriced_percent > 20:
                performance = "Moderate Opportunity"
            elif revenue_improvement > 2 or underpriced_percent > 10:
                performance = "Minor Adjustments Needed"
            else:
                performance = "Well-Optimized"

            # Build recommendations list (flatten strategic recommendations)
            recommendations = []
            for rec in strategic_recommendations:
                if rec["priority"] == "High":
                    priority_emoji = "🔴"
                elif rec["priority"] == "Medium":
                    priority_emoji = "🟡"
                else:
                    priority_emoji = "🟢"

                recommendations.append(
                    f"{priority_emoji} {rec['category']}: {rec['action']} - {rec.get('impact', 'See details')}"
                )

            # Add top 3 underpriced items as specific recommendations
            if pricing_opportunities["underpriced_items"]:
                recommendations.append(
                    f"Top underpriced items: {', '.join([item['menu_name'] for item in pricing_opportunities['underpriced_items'][:3]])}"
                )

            # Industry benchmarks
            benchmarks = {
                "Target Food Cost %": f"{target_food_cost}%",
                "Pricing Variance Threshold": "±10% from optimal",
                "Psychological Pricing": ".99 endings (<$10), .95 endings ($10-20)",
                "Minimum Markup": "1.5x cost (33% max food cost)",
                "Price Elasticity": "Consider 10-20% volume increase with price reductions"
            }

            # Additional insights
            additional_data = {
                "Total Menu Items Analyzed": len(unified_data),
                "Highest Revenue Opportunity": pricing_opportunities["underpriced_items"][0]["menu_name"] if pricing_opportunities["underpriced_items"] else "N/A",
                "Most Overpriced": pricing_opportunities["overpriced_items"][0]["menu_name"] if pricing_opportunities["overpriced_items"] else "N/A",
                "Avg Pricing Variance": f"{pricing_opportunities['summary']['avg_variance']:.1f}%",
                "Validation Warnings": len(validation_report.get("warnings", []))
            }

            # Generate business report
            business_report = format_business_report(
                analysis_type="Menu Pricing Strategy Analysis",
                metrics=metrics,
                performance={"rating": performance, "color": "green"},
                recommendations=recommendations,
                benchmarks=benchmarks,
                additional_data=additional_data
            )

        except Exception as e:
            return error_payload(service, subtask, f"Failed to generate business report: {str(e)}")

        # STEP 6: Return success payload
        return success_payload(
            service, subtask, params, {
                "analysis_type": "Menu Pricing Strategy",
                "business_report": business_report["business_report"],
                "business_report_html": business_report["business_report_html"],
                "metrics": metrics,
                "performance": performance,
                "recommendations": recommendations,
                "pricing_opportunities": pricing_opportunities,
                "price_positioning": price_positioning,
                "strategic_recommendations": strategic_recommendations,
                "revenue_impact": revenue_impact,
                "target_food_cost_percent": target_food_cost,
                "validation_report": validation_report
            }, recommendations
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Unexpected error: {str(e)}")
