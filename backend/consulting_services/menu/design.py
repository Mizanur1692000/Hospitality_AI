"""
Menu Design Recommendations Task
Analyzes menu layout using Menu Engineering Matrix and provides Golden Triangle placement,
visual hierarchy, and psychological design recommendations.
"""

import os
from backend.shared.utils.common import success_payload, error_payload
from backend.consulting_services.kpi.kpi_utils import format_business_report
from .analysis_functions import (
    load_restaurant_data,
    validate_data_integrity,
    join_menu_data,
    calculate_menu_engineering_matrix,
    calculate_menu_design_recommendations
)


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Generate comprehensive menu design recommendations using Menu Engineering principles.

    Integrates with restaurant_inventory_app data to provide Golden Triangle placement,
    layout strategy, visual hierarchy, and implementation guide.

    Args:
        params: Dictionary containing:
            - recipe_data_path (str, optional): Path to recipes.json
            - menu_items_path (str, optional): Path to menu_items.json
            - sales_data_path (str, optional): Path to sales_data.json
            - validate_calculations (bool, optional): Validate precalculated metrics (default: False)
            - use_precalculated (bool, optional): Use precalculated metrics (default: True)
        file_bytes: Optional file data (not used in this task)

    Returns:
        Tuple of (response_dict, status_code)
    """
    service, subtask = "menu", "design"

    try:
        # Default data paths (use environment variable for flexibility)
        default_data_dir = os.getenv("RESTAURANT_DATA_DIR", "/home/jkatz015/repos/restaurant_inventory_app/data")

        # Extract parameters with defaults
        recipe_data_path = params.get("recipe_data_path", os.path.join(default_data_dir, "recipes.json"))
        menu_items_path = params.get("menu_items_path", os.path.join(default_data_dir, "menu_items.json"))
        sales_data_path = params.get("sales_data_path", os.path.join(default_data_dir, "sales_data.json"))

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

        # STEP 4: Calculate Menu Engineering Matrix (needed for design recommendations)
        try:
            # Group by category and calculate matrix for each
            categories = {}
            for item in unified_data:
                category = item.get("category", "Other")
                if category not in categories:
                    categories[category] = []
                categories[category].append(item)

            # Calculate menu engineering matrix for all items combined
            all_matrix = calculate_menu_engineering_matrix(unified_data)
        except Exception as e:
            return error_payload(service, subtask, f"Menu engineering matrix calculation failed: {str(e)}")

        # STEP 5: Calculate Menu Design Recommendations
        try:
            design_result = calculate_menu_design_recommendations(
                unified_data,
                all_matrix
            )
        except Exception as e:
            return error_payload(service, subtask, f"Design recommendations failed: {str(e)}")

        # STEP 6: Generate comprehensive business report
        try:
            golden_triangle = design_result["golden_triangle"]
            layout_strategy = design_result["layout_strategy"]
            design_principles = design_result["design_principles"]
            implementation_guide = design_result["implementation_guide"]
            quadrant_counts = design_result["quadrant_counts"]

            # Build metrics dictionary
            metrics = {
                "Total Menu Items": len(unified_data),
                "Stars (High visibility)": quadrant_counts["stars"],
                "Puzzles (Need awareness)": quadrant_counts["puzzles"],
                "Plowhorses (Maintain)": quadrant_counts["plowhorses"],
                "Dogs (Minimize/Remove)": quadrant_counts["dogs"],
                "Golden Triangle Items": len(golden_triangle),
                "Categories": len(layout_strategy["section_order"]),
                "Psychological Techniques": len(layout_strategy["psychological_techniques"]),
                "Implementation Phases": 3
            }

            # Determine performance rating based on current menu structure
            star_percent = (quadrant_counts["stars"] / len(unified_data) * 100) if unified_data else 0
            dog_percent = (quadrant_counts["dogs"] / len(unified_data) * 100) if unified_data else 0

            if star_percent >= 25 and dog_percent <= 15:
                performance = "Well-Structured"
            elif star_percent >= 15 and dog_percent <= 25:
                performance = "Moderate Optimization Needed"
            else:
                performance = "Significant Redesign Recommended"

            # Build recommendations list
            recommendations = []

            # Golden Triangle recommendations
            if golden_triangle:
                recommendations.append(
                    f"Place '{golden_triangle[0]['menu_item']}' in Top Right (Primary) position - {golden_triangle[0]['reason']}"
                )
                if len(golden_triangle) > 1:
                    recommendations.append(
                        f"Place '{golden_triangle[1]['menu_item']}' in Top Center (Secondary) position"
                    )

            # Design principle recommendations
            if design_principles["stars_treatment"]["count"] > 0:
                recommendations.append(
                    f"Maximize visibility for {design_principles['stars_treatment']['count']} Star items - use 18-20pt font and visual highlights"
                )

            if design_principles["puzzles_treatment"]["count"] > 0:
                recommendations.append(
                    f"Build awareness for {design_principles['puzzles_treatment']['count']} Puzzle items - add descriptive language"
                )

            if design_principles["dogs_treatment"]["count"] > 0:
                recommendations.append(
                    f"Minimize or remove {design_principles['dogs_treatment']['count']} Dog items - they have low performance"
                )

            # Immediate action items
            for action in implementation_guide["phase_1_immediate"][:2]:
                recommendations.append(f"Immediate: {action}")

            # Industry benchmarks
            benchmarks = {
                "Golden Triangle": "Top-right, top-center, middle-center positions",
                "Font Hierarchy": "18-20pt (Stars), 16pt (Puzzles), 14pt (Standard), 12pt (Dogs)",
                "Items Per Category": "6-8 items maximum (reduce decision fatigue)",
                "Star Distribution Target": "25-35% of menu items",
                "Dog Distribution Max": "< 15% of menu items",
                "Section Order": "Appetizers → Entrees → Sides → Desserts"
            }

            # Additional insights
            additional_data = {
                "Top Golden Triangle Item": golden_triangle[0]["menu_item"] if golden_triangle else "N/A",
                "Categories Analyzed": len(layout_strategy["section_order"]),
                "Visual Hierarchy Levels": len(layout_strategy["visual_hierarchy"]),
                "Psychology Techniques": len(layout_strategy["psychological_techniques"]),
                "Implementation Phases": "3 (Immediate, Short-term, Medium-term)",
                "Validation Warnings": len(validation_report.get("warnings", []))
            }

            # Generate business report
            business_report = format_business_report(
                analysis_type="Menu Design Recommendations (Menu Psychology)",
                metrics=metrics,
                performance={"rating": performance, "color": "purple"},
                recommendations=recommendations,
                benchmarks=benchmarks,
                additional_data=additional_data
            )

        except Exception as e:
            return error_payload(service, subtask, f"Failed to generate business report: {str(e)}")

        # STEP 7: Return success payload
        return success_payload(
            service, subtask, params, {
                "analysis_type": "Menu Design Recommendations",
                "business_report": business_report["business_report"],
                "business_report_html": business_report["business_report_html"],
                "metrics": metrics,
                "performance": performance,
                "recommendations": recommendations,
                "golden_triangle": golden_triangle,
                "layout_strategy": layout_strategy,
                "design_principles": design_principles,
                "implementation_guide": implementation_guide,
                "quadrant_counts": quadrant_counts,
                "validation_report": validation_report
            }, recommendations
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Unexpected error: {str(e)}")
