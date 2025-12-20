"""
Menu Engineering Analysis Functions
Comprehensive business logic for menu optimization using Menu Engineering Matrix.
Integrates with restaurant_inventory_app data (recipes.json, menu_items.json, sales_data.json).
"""

import json
import logging
import os
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from backend.consulting_services.kpi.kpi_utils import format_business_report

logger = logging.getLogger(__name__)


# ============================================================================
# DATA INTEGRATION LAYER
# ============================================================================

def verify_data_files(recipe_path: str, menu_items_path: str, sales_path: str) -> None:
    """
    Verify that all required restaurant data files exist and are readable.

    This function checks file availability and logs diagnostic information
    to help troubleshoot data integration issues.

    Args:
        recipe_path: Path to recipes.json
        menu_items_path: Path to menu_items.json
        sales_path: Path to sales_data.json

    Raises:
        FileNotFoundError: If any required file is missing

    Logs:
        INFO: Data directory location and file status
        WARNING: If files exist but may have permission issues
        ERROR: Missing files with absolute paths for troubleshooting
    """
    data_dir = os.getenv("RESTAURANT_DATA_DIR", "not set")
    logger.info(f"Restaurant data directory (RESTAURANT_DATA_DIR): {data_dir}")

    required_files = {
        "recipes.json": recipe_path,
        "menu_items.json": menu_items_path,
        "sales_data.json": sales_path
    }

    missing_files = []
    for name, path in required_files.items():
        abs_path = Path(path).resolve()
        if not abs_path.exists():
            logger.error(f"Missing data file: {name} at {abs_path}")
            missing_files.append(f"{name} (expected at: {abs_path})")
        else:
            file_size = abs_path.stat().st_size
            logger.info(f"Found {name}: {abs_path} ({file_size:,} bytes)")

            # Check readability
            if not os.access(abs_path, os.R_OK):
                logger.warning(f"File exists but may not be readable: {abs_path}")

    if missing_files:
        error_msg = (
            f"Missing required data files: {', '.join(missing_files)}. "
            f"Check RESTAURANT_DATA_DIR environment variable (currently: {data_dir})"
        )
        raise FileNotFoundError(error_msg)

def load_restaurant_data(
    recipe_data_path: str,
    menu_items_path: str,
    sales_data_path: str
) -> Tuple[Dict, Dict, Dict]:
    """
    Load the 3 JSON files from restaurant_inventory_app.

    Args:
        recipe_data_path: Path to recipes.json (keyed by recipe name)
        menu_items_path: Path to menu_items.json (keyed by menu_item_id)
        sales_data_path: Path to sales_data.json (has sales_records array)

    Returns:
        Tuple of (recipes_dict, menu_items_dict, sales_dict)
        - recipes_dict: Keyed by recipe_id
        - menu_items_dict: Keyed by menu_item_id
        - sales_dict: Keyed by menu_item_id

    Raises:
        FileNotFoundError: If any file doesn't exist
        JSONDecodeError: If any file is invalid JSON
    """
    # Verify all data files exist before attempting to load
    verify_data_files(recipe_data_path, menu_items_path, sales_data_path)

    # Load recipes (keyed by name, need to convert to keyed by recipe_id)
    try:
        with open(recipe_data_path, 'r') as f:
            recipes_by_name = json.load(f)

        # Convert to keyed by recipe_id
        recipes = {}
        for recipe_name, recipe_data in recipes_by_name.items():
            recipe_id = recipe_data.get('recipe_id')
            if recipe_id:
                recipes[recipe_id] = recipe_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Recipe data file not found: {recipe_data_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in recipe data file: {str(e)}")

    # Load menu items (already keyed by menu_item_id)
    try:
        with open(menu_items_path, 'r') as f:
            menu_items = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Menu items file not found: {menu_items_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in menu items file: {str(e)}")

    # Load sales data (has sales_records array, need to convert to dict by menu_item_id)
    try:
        with open(sales_data_path, 'r') as f:
            sales_data = json.load(f)

        # Extract sales_records array and convert to dictionary keyed by menu_item_id
        sales_records = sales_data.get('sales_records', [])
        sales = {}
        for record in sales_records:
            menu_item_id = record.get('menu_item_id')
            if menu_item_id:
                sales[menu_item_id] = record
    except FileNotFoundError:
        raise FileNotFoundError(f"Sales data file not found: {sales_data_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in sales data file: {str(e)}")

    return recipes, menu_items, sales


def validate_data_integrity(
    recipes: Dict,
    menu_items: Dict,
    sales: Dict,
    validate_calculations: bool = False
) -> Dict:
    """
    Validate FK relationships and optionally recalculate metrics.

    Args:
        recipes: Recipes dictionary
        menu_items: Menu items dictionary
        sales: Sales dictionary
        validate_calculations: If True, recalculate and compare

    Returns:
        Validation report with any errors/warnings
    """
    errors = []
    warnings = []
    discrepancies = []

    # Check FK integrity: menu_items.recipe_id exists in recipes
    for menu_item_id, menu_item in menu_items.items():
        recipe_id = menu_item.get('recipe_id')
        if recipe_id and recipe_id not in recipes:
            errors.append(f"Menu item {menu_item_id} references non-existent recipe {recipe_id}")

    # Check FK integrity: sales.menu_item_id exists in menu_items
    for menu_item_id in sales.keys():
        if menu_item_id not in menu_items:
            errors.append(f"Sales data references non-existent menu item {menu_item_id}")

    # Check data completeness
    for recipe_id, recipe in recipes.items():
        if 'total_cost' not in recipe or recipe.get('total_cost', 0) <= 0:
            warnings.append(f"Recipe {recipe_id} missing or invalid total_cost")

    for menu_item_id, menu_item in menu_items.items():
        if 'menu_price' not in menu_item or menu_item.get('menu_price', 0) <= 0:
            warnings.append(f"Menu item {menu_item_id} missing or invalid menu_price")

    for menu_item_id, sales_record in sales.items():
        if 'total_units_sold' not in sales_record:
            warnings.append(f"Sales record {menu_item_id} missing total_units_sold")

    # Optional: Validate calculations
    if validate_calculations:
        for menu_item_id, menu_item in menu_items.items():
            if menu_item_id in sales:
                recipe_id = menu_item.get('recipe_id')
                if recipe_id and recipe_id in recipes:
                    recipe = recipes[recipe_id]

                    # Recalculate food_cost_percent
                    recipe_cost = recipe.get('total_cost', 0)
                    menu_price = menu_item.get('menu_price', 0)
                    if menu_price > 0:
                        calc_food_cost_percent = (recipe_cost / menu_price) * 100
                        precalc_food_cost_percent = menu_item.get('food_cost_percent', 0)

                        diff = abs(calc_food_cost_percent - precalc_food_cost_percent)
                        if diff > 0.1:  # tolerance of 0.1%
                            discrepancies.append({
                                "menu_item_id": menu_item_id,
                                "field": "food_cost_percent",
                                "precalculated": precalc_food_cost_percent,
                                "recalculated": round(calc_food_cost_percent, 2),
                                "difference": round(diff, 2)
                            })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "discrepancies": discrepancies
    }


def join_menu_data(
    recipes: Dict,
    menu_items: Dict,
    sales: Dict,
    use_precalculated: bool = True
) -> List[Dict]:
    """
    Join the 3 data sources using FK relationships.

    Args:
        recipes: Dict[recipe_id, recipe_data]
        menu_items: Dict[menu_item_id, menu_item_data]
        sales: Dict[menu_item_id, sales_data]
        use_precalculated: Use existing calculations or recalculate

    Returns:
        List of unified menu item records with all data
    """
    unified_data = []

    for menu_item_id, sales_record in sales.items():
        # Get menu item
        if menu_item_id not in menu_items:
            continue  # Skip if menu_item doesn't exist

        menu_item = menu_items[menu_item_id]

        # Get recipe via FK
        recipe_id = menu_item.get('recipe_id')
        if not recipe_id or recipe_id not in recipes:
            continue  # Skip if recipe doesn't exist

        recipe = recipes[recipe_id]

        # Merge all 3 records
        unified_record = {
            # IDs
            "menu_item_id": menu_item_id,
            "recipe_id": recipe_id,

            # Names & Category
            "menu_name": menu_item.get("menu_name", ""),
            "recipe_name": recipe.get("name", ""),
            "category": recipe.get("category", "Uncategorized"),

            # Recipe details
            "servings": recipe.get("servings", 1),
            "prep_time": recipe.get("prep_time", 0),
            "cook_time": recipe.get("cook_time", 0),
            "total_cost": recipe.get("total_cost", 0),

            # Menu item pricing
            "menu_price": menu_item.get("menu_price", 0),
            "recipe_cost": menu_item.get("recipe_cost", recipe.get("total_cost", 0)),

            # Sales performance
            "total_units_sold": sales_record.get("total_units_sold", 0),
            "total_revenue": sales_record.get("total_revenue", 0),
            "total_cost": sales_record.get("total_cost", 0),
            "total_profit": sales_record.get("total_profit", 0),
            "average_daily_units": sales_record.get("average_daily_units", 0),
        }

        # Use precalculated or recalculate
        if use_precalculated:
            unified_record["food_cost_percent"] = menu_item.get("food_cost_percent", 0)
            unified_record["contribution_margin"] = menu_item.get("contribution_margin", 0)
            unified_record["quadrant"] = sales_record.get("quadrant", "unknown")
            unified_record["quadrant_source"] = "precalculated"
        else:
            # Recalculate
            menu_price = unified_record["menu_price"]
            recipe_cost = unified_record["total_cost"]

            if menu_price > 0:
                unified_record["food_cost_percent"] = (recipe_cost / menu_price) * 100
                unified_record["contribution_margin"] = menu_price - recipe_cost
            else:
                unified_record["food_cost_percent"] = 0
                unified_record["contribution_margin"] = 0

            unified_record["quadrant"] = "recalculated_later"  # Will be set by classify_quadrant
            unified_record["quadrant_source"] = "recalculated"

        unified_data.append(unified_record)

    return unified_data


# ============================================================================
# MENU ENGINEERING CALCULATIONS
# ============================================================================

def classify_quadrant(
    popularity_score: float,
    profitability_score: float
) -> str:
    """
    Classify an item into one of 4 quadrants.

    Args:
        popularity_score: Relative popularity (1.0 = average)
        profitability_score: Relative profitability (1.0 = average)

    Returns:
        "star" | "plowhorse" | "puzzle" | "dog"
    """
    if popularity_score >= 1.0 and profitability_score >= 1.0:
        return "star"
    elif popularity_score >= 1.0 and profitability_score < 1.0:
        return "plowhorse"
    elif popularity_score < 1.0 and profitability_score >= 1.0:
        return "puzzle"
    else:  # popularity < 1.0 and profitability < 1.0
        return "dog"


def calculate_thresholds(
    items: List[Dict],
    method: str = "average"
) -> Tuple[float, float]:
    """
    Calculate popularity and profitability thresholds.

    Args:
        items: List of menu items
        method: "average" | "median"

    Returns:
        Tuple of (popularity_threshold, profitability_threshold)
    """
    if not items:
        return 0.0, 0.0

    units_sold = [item.get("total_units_sold", 0) for item in items]
    margins = [item.get("contribution_margin", 0) for item in items]

    if method == "median":
        popularity_threshold = statistics.median(units_sold) if units_sold else 0
        profitability_threshold = statistics.median(margins) if margins else 0
    else:  # average
        popularity_threshold = statistics.mean(units_sold) if units_sold else 0
        profitability_threshold = statistics.mean(margins) if margins else 0

    return popularity_threshold, profitability_threshold


def rank_items(
    items: List[Dict],
    by: str
) -> List[Dict]:
    """
    Rank items by specified metric.

    Args:
        items: List of menu items
        by: "total_profit" | "contribution_margin" | "total_units_sold" | "total_revenue"

    Returns:
        Sorted list of items (highest to lowest) with rank added
    """
    if not items:
        return []

    # Sort by the specified field (descending)
    sorted_items = sorted(
        items,
        key=lambda x: x.get(by, 0),
        reverse=True
    )

    # Add rank
    for i, item in enumerate(sorted_items, 1):
        item[f"rank_by_{by}"] = i

    return sorted_items


def calculate_menu_engineering_matrix(
    items: List[Dict],
    popularity_method: str = "average",
    profitability_method: str = "average"
) -> Dict:
    """
    Classify menu items into the 4 quadrants.

    Args:
        items: List of menu items for a category
        popularity_method: "average" | "median"
        profitability_method: "average" | "median"

    Returns:
        Dictionary with stars, plowhorses, puzzles, dogs
    """
    if not items:
        return {"stars": [], "plowhorses": [], "puzzles": [], "dogs": []}

    # Calculate thresholds
    popularity_threshold, profitability_threshold = calculate_thresholds(
        items,
        method=popularity_method
    )

    # Initialize quadrants
    matrix = {
        "stars": [],
        "plowhorses": [],
        "puzzles": [],
        "dogs": []
    }

    # Classify each item
    for item in items:
        units_sold = item.get("total_units_sold", 0)
        margin = item.get("contribution_margin", 0)

        # Calculate scores relative to threshold
        popularity_score = (units_sold / popularity_threshold) if popularity_threshold > 0 else 0
        profitability_score = (margin / profitability_threshold) if profitability_threshold > 0 else 0

        # Classify
        quadrant = classify_quadrant(popularity_score, profitability_score)

        # Add scores to item
        item["popularity_score"] = round(popularity_score, 2)
        item["profitability_score"] = round(profitability_score, 2)
        item["quadrant_calculated"] = quadrant

        # Add action recommendation based on quadrant
        if quadrant == "star":
            item["action"] = "Promote heavily - maintain quality and portion size"
            item["placement_recommendation"] = "Golden Triangle (top right corner)"
        elif quadrant == "plowhorse":
            item["action"] = "Increase price or reduce cost to improve margin"
            item["placement_recommendation"] = "Standard placement"
        elif quadrant == "puzzle":
            item["action"] = "Feature prominently to boost sales volume"
            item["placement_recommendation"] = "Center or featured section"
        else:  # dog
            item["action"] = "Consider repricing, repositioning, or removing"
            item["placement_recommendation"] = "De-emphasize or remove"

        # Add to appropriate quadrant
        matrix[quadrant + "s"].append(item)

    return matrix


# ============================================================================
# FEATURE 1: PRODUCT MIX ANALYSIS
# ============================================================================

def calculate_product_mix_analysis(
    unified_data: List[Dict],
    category_filter: Optional[str] = None
) -> Dict:
    """
    Main function for Feature 1: Product Mix Analysis.

    Args:
        unified_data: Joined menu data from join_menu_data()
        category_filter: Optional filter by category

    Returns:
        Complete product mix analysis with menu engineering matrix
    """
    # Filter by category if specified
    if category_filter:
        filtered_data = [item for item in unified_data if item.get("category") == category_filter]
    else:
        filtered_data = unified_data

    if not filtered_data:
        return {
            "menu_engineering_matrix": {"stars": [], "plowhorses": [], "puzzles": [], "dogs": []},
            "quadrant_summary": {
                "stars": {"count": 0, "total_revenue": 0, "total_profit": 0, "avg_food_cost_percent": 0, "revenue_percent": 0, "percentage_of_menu": 0},
                "plowhorses": {"count": 0, "total_revenue": 0, "total_profit": 0, "avg_food_cost_percent": 0, "revenue_percent": 0, "percentage_of_menu": 0},
                "puzzles": {"count": 0, "total_revenue": 0, "total_profit": 0, "avg_food_cost_percent": 0, "revenue_percent": 0, "percentage_of_menu": 0},
                "dogs": {"count": 0, "total_revenue": 0, "total_profit": 0, "avg_food_cost_percent": 0, "revenue_percent": 0, "percentage_of_menu": 0}
            },
            "category_breakdown": {},
            "top_performers": {"by_units_sold": [], "by_revenue": [], "by_total_profit": []},
            "bottom_performers": {"by_units_sold": [], "by_revenue": [], "by_total_profit": []},
            "overall_metrics": {"total_menu_items": 0, "total_units_sold": 0, "total_revenue": 0, "total_cost": 0, "total_profit": 0, "overall_food_cost_percent": 0, "avg_menu_price": 0, "avg_contribution_margin": 0, "avg_units_per_item": 0}
        }

    # Group items by category
    categories = {}
    for item in filtered_data:
        category = item.get("category", "Uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append(item)

    # Calculate menu engineering matrix for each category
    all_stars = []
    all_plowhorses = []
    all_puzzles = []
    all_dogs = []

    category_breakdown = {}

    for category, items in categories.items():
        # Calculate matrix for this category
        matrix = calculate_menu_engineering_matrix(items)

        # Aggregate across categories
        all_stars.extend(matrix["stars"])
        all_plowhorses.extend(matrix["plowhorses"])
        all_puzzles.extend(matrix["puzzles"])
        all_dogs.extend(matrix["dogs"])

        # Calculate category metrics
        total_units = sum(item.get("total_units_sold", 0) for item in items)
        total_revenue = sum(item.get("total_revenue", 0) for item in items)
        total_cost = sum(item.get("total_cost", 0) for item in items)
        total_profit = sum(item.get("total_profit", 0) for item in items)

        avg_food_cost_percent = statistics.mean([
            item.get("food_cost_percent", 0) for item in items
        ]) if items else 0

        avg_contribution_margin = statistics.mean([
            item.get("contribution_margin", 0) for item in items
        ]) if items else 0

        category_breakdown[category] = {
            "total_items": len(items),
            "stars": len(matrix["stars"]),
            "plowhorses": len(matrix["plowhorses"]),
            "puzzles": len(matrix["puzzles"]),
            "dogs": len(matrix["dogs"]),
            "total_units_sold": total_units,
            "total_revenue": round(total_revenue, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "avg_food_cost_percent": round(avg_food_cost_percent, 2),
            "avg_contribution_margin": round(avg_contribution_margin, 2)
        }

    # Overall menu engineering matrix
    menu_engineering_matrix = {
        "stars": all_stars,
        "plowhorses": all_plowhorses,
        "puzzles": all_puzzles,
        "dogs": all_dogs
    }

    # Rank items for top/bottom performers
    ranked_by_profit = rank_items(filtered_data, "total_profit")
    ranked_by_margin = rank_items(filtered_data, "contribution_margin")
    ranked_by_volume = rank_items(filtered_data, "total_units_sold")
    ranked_by_revenue = rank_items(filtered_data, "total_revenue")

    top_performers = {
        "by_total_profit": ranked_by_profit[:5],
        "by_contribution_margin": ranked_by_margin[:5],
        "by_units_sold": ranked_by_volume[:5],
        "by_revenue": ranked_by_revenue[:5]
    }

    bottom_performers = {
        "by_total_profit": ranked_by_profit[-5:],
        "by_contribution_margin": ranked_by_margin[-5:],
        "by_units_sold": ranked_by_volume[-5:]
    }

    # Calculate overall metrics
    total_revenue = sum(item.get("total_revenue", 0) for item in filtered_data)
    total_cost = sum(item.get("total_cost", 0) for item in filtered_data)
    total_profit = sum(item.get("total_profit", 0) for item in filtered_data)
    total_units = sum(item.get("total_units_sold", 0) for item in filtered_data)

    overall_food_cost_percent = (total_cost / total_revenue * 100) if total_revenue > 0 else 0
    avg_menu_price = statistics.mean([item.get("menu_price", 0) for item in filtered_data]) if filtered_data else 0
    avg_contribution_margin = statistics.mean([item.get("contribution_margin", 0) for item in filtered_data]) if filtered_data else 0

    overall_metrics = {
        "total_menu_items": len(filtered_data),
        "total_units_sold": total_units,
        "total_revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "total_profit": round(total_profit, 2),
        "overall_food_cost_percent": round(overall_food_cost_percent, 2),
        "avg_menu_price": round(avg_menu_price, 2),
        "avg_contribution_margin": round(avg_contribution_margin, 2),
        "avg_units_per_item": round(total_units / len(filtered_data), 2) if filtered_data else 0
    }

    return {
        "menu_engineering_matrix": menu_engineering_matrix,
        "quadrant_summary": {
            "stars": {
                "count": len(all_stars),
                "total_revenue": round(sum(s.get("total_revenue", 0) for s in all_stars), 2),
                "total_profit": round(sum(s.get("total_profit", 0) for s in all_stars), 2),
                "avg_food_cost_percent": round(statistics.mean([s.get("food_cost_percent", 0) for s in all_stars]), 2) if all_stars else 0,
                "revenue_percent": round((sum(s.get("total_revenue", 0) for s in all_stars) / total_revenue * 100), 2) if total_revenue > 0 else 0
            },
            "plowhorses": {
                "count": len(all_plowhorses),
                "total_revenue": round(sum(p.get("total_revenue", 0) for p in all_plowhorses), 2),
                "total_profit": round(sum(p.get("total_profit", 0) for p in all_plowhorses), 2),
                "avg_food_cost_percent": round(statistics.mean([p.get("food_cost_percent", 0) for p in all_plowhorses]), 2) if all_plowhorses else 0,
                "revenue_percent": round((sum(p.get("total_revenue", 0) for p in all_plowhorses) / total_revenue * 100), 2) if total_revenue > 0 else 0
            },
            "puzzles": {
                "count": len(all_puzzles),
                "total_revenue": round(sum(pz.get("total_revenue", 0) for pz in all_puzzles), 2),
                "total_profit": round(sum(pz.get("total_profit", 0) for pz in all_puzzles), 2),
                "avg_food_cost_percent": round(statistics.mean([pz.get("food_cost_percent", 0) for pz in all_puzzles]), 2) if all_puzzles else 0,
                "revenue_percent": round((sum(pz.get("total_revenue", 0) for pz in all_puzzles) / total_revenue * 100), 2) if total_revenue > 0 else 0
            },
            "dogs": {
                "count": len(all_dogs),
                "total_revenue": round(sum(d.get("total_revenue", 0) for d in all_dogs), 2),
                "total_profit": round(sum(d.get("total_profit", 0) for d in all_dogs), 2),
                "avg_food_cost_percent": round(statistics.mean([d.get("food_cost_percent", 0) for d in all_dogs]), 2) if all_dogs else 0,
                "revenue_percent": round((sum(d.get("total_revenue", 0) for d in all_dogs) / total_revenue * 100), 2) if total_revenue > 0 else 0
            }
        },
        "category_breakdown": category_breakdown,
        "top_performers": top_performers,
        "bottom_performers": bottom_performers,
        "overall_metrics": overall_metrics
    }


# ============================================================================
# FEATURE 2: MENU PRICING STRATEGY
# ============================================================================

def calculate_optimal_price(
    recipe_cost: float,
    target_food_cost_percent: float,
    psychological_pricing: bool = True
) -> Dict:
    """
    Calculate optimal menu price based on recipe cost and target food cost %.

    Args:
        recipe_cost: Cost to produce one serving of the recipe
        target_food_cost_percent: Target food cost percentage (e.g., 30.0 for 30%)
        psychological_pricing: Apply psychological pricing rules (e.g., $9.99 instead of $10.00)

    Returns:
        Dictionary with optimal_price, contribution_margin, and pricing_strategy
    """
    if recipe_cost <= 0:
        raise ValueError("Recipe cost must be positive")

    if target_food_cost_percent <= 0 or target_food_cost_percent >= 100:
        raise ValueError("Target food cost percent must be between 0 and 100")

    # Calculate optimal price: cost / (target_food_cost% / 100)
    optimal_price = recipe_cost / (target_food_cost_percent / 100)

    # Apply psychological pricing if requested
    if psychological_pricing:
        # Round to nearest psychological price point
        if optimal_price < 10:
            # For prices under $10, use .95 or .99 endings
            optimal_price = round(optimal_price) - 0.01
        elif optimal_price < 20:
            # For prices $10-20, use .95 endings
            optimal_price = round(optimal_price) - 0.05
        else:
            # For prices over $20, round to nearest dollar
            optimal_price = round(optimal_price)

    # Ensure minimum price
    if optimal_price < recipe_cost * 1.5:
        optimal_price = recipe_cost * 1.5  # Minimum 33% food cost

    contribution_margin = optimal_price - recipe_cost
    actual_food_cost_percent = (recipe_cost / optimal_price * 100) if optimal_price > 0 else 0

    return {
        "optimal_price": round(optimal_price, 2),
        "contribution_margin": round(contribution_margin, 2),
        "actual_food_cost_percent": round(actual_food_cost_percent, 2),
        "markup_multiplier": round(optimal_price / recipe_cost, 2) if recipe_cost > 0 else 0
    }


def analyze_price_positioning(unified_data: List[Dict]) -> Dict:
    """
    Analyze price positioning across menu items and categories.

    Identifies price gaps, clustering, and opportunities for price anchoring.

    Args:
        unified_data: List of unified menu item records

    Returns:
        Dictionary with price distribution analysis and positioning recommendations
    """
    if not unified_data:
        return {
            "price_distribution": {},
            "price_gaps": [],
            "anchor_opportunities": [],
            "category_price_ranges": {}
        }

    # Extract all prices
    all_prices = sorted([item.get("menu_price", 0) for item in unified_data if item.get("menu_price", 0) > 0])

    if not all_prices:
        return {
            "price_distribution": {},
            "price_gaps": [],
            "anchor_opportunities": [],
            "category_price_ranges": {}
        }

    # Calculate price distribution
    price_distribution = {
        "min_price": round(min(all_prices), 2),
        "max_price": round(max(all_prices), 2),
        "avg_price": round(statistics.mean(all_prices), 2),
        "median_price": round(statistics.median(all_prices), 2),
        "price_range": round(max(all_prices) - min(all_prices), 2)
    }

    # Identify price gaps (gaps > $3 between consecutive prices)
    price_gaps = []
    for i in range(len(all_prices) - 1):
        gap = all_prices[i + 1] - all_prices[i]
        if gap > 3.0:
            price_gaps.append({
                "lower_price": round(all_prices[i], 2),
                "upper_price": round(all_prices[i + 1], 2),
                "gap_size": round(gap, 2),
                "recommendation": f"Consider adding menu item priced around ${round((all_prices[i] + all_prices[i + 1]) / 2, 2)}"
            })

    # Identify anchor opportunities (high-priced items that make others look reasonable)
    anchor_opportunities = []
    if price_distribution["max_price"] > price_distribution["avg_price"] * 1.5:
        anchor_opportunities.append({
            "type": "High-price anchor",
            "item_price": price_distribution["max_price"],
            "strategy": "Use as menu anchor to make mid-range items appear more affordable",
            "placement": "Top-right of menu (Golden Triangle position)"
        })

    # Low-price anchor (draws customers in)
    if price_distribution["min_price"] < price_distribution["avg_price"] * 0.6:
        anchor_opportunities.append({
            "type": "Low-price entry point",
            "item_price": price_distribution["min_price"],
            "strategy": "Use to attract price-sensitive customers and increase traffic",
            "placement": "Appetizers or sides section"
        })

    # Category price ranges
    category_price_ranges = {}
    categories = {}
    for item in unified_data:
        category = item.get("category", "Other")
        if category not in categories:
            categories[category] = []
        categories[category].append(item.get("menu_price", 0))

    for category, prices in categories.items():
        valid_prices = [p for p in prices if p > 0]
        if valid_prices:
            category_price_ranges[category] = {
                "min": round(min(valid_prices), 2),
                "max": round(max(valid_prices), 2),
                "avg": round(statistics.mean(valid_prices), 2),
                "range": round(max(valid_prices) - min(valid_prices), 2)
            }

    return {
        "price_distribution": price_distribution,
        "price_gaps": price_gaps,
        "anchor_opportunities": anchor_opportunities,
        "category_price_ranges": category_price_ranges
    }


def identify_pricing_opportunities(unified_data: List[Dict], target_food_cost: float = 32.0) -> Dict:
    """
    Identify specific pricing adjustment opportunities across the menu.

    Args:
        unified_data: List of unified menu item records
        target_food_cost: Target food cost percentage (default: 32%)

    Returns:
        Dictionary with underpriced, overpriced, and well-priced items
    """
    if not unified_data:
        return {
            "underpriced_items": [],
            "overpriced_items": [],
            "well_priced_items": [],
            "total_revenue_opportunity": 0.0
        }

    underpriced = []
    overpriced = []
    well_priced = []
    total_revenue_opportunity = 0.0

    for item in unified_data:
        menu_item_id = item.get("menu_item_id", "unknown")
        menu_name = item.get("menu_name", "Unknown Item")
        current_price = item.get("menu_price", 0)
        recipe_cost = item.get("recipe_cost", 0)
        food_cost_percent = item.get("food_cost_percent", 0)
        total_units_sold = item.get("total_units_sold", 0)
        quadrant = item.get("quadrant", "unknown")

        if current_price <= 0 or recipe_cost <= 0:
            continue

        # Calculate optimal pricing
        optimal = calculate_optimal_price(recipe_cost, target_food_cost, psychological_pricing=True)
        optimal_price = optimal["optimal_price"]

        # Calculate variance from optimal
        price_variance_percent = ((current_price - optimal_price) / optimal_price * 100) if optimal_price > 0 else 0

        # Calculate potential revenue impact
        revenue_opportunity = (optimal_price - current_price) * total_units_sold

        # Categorize based on variance
        if price_variance_percent < -10:  # More than 10% below optimal
            underpriced.append({
                "menu_item_id": menu_item_id,
                "menu_name": menu_name,
                "current_price": round(current_price, 2),
                "optimal_price": round(optimal_price, 2),
                "suggested_price": round(optimal_price, 2),
                "current_food_cost_percent": round(food_cost_percent, 2),
                "variance_percent": round(price_variance_percent, 2),
                "revenue_opportunity": round(revenue_opportunity, 2),
                "quadrant": quadrant,
                "priority": "High" if quadrant in ["star", "plowhorse"] else "Medium",
                "recommendation": f"Increase price from ${current_price:.2f} to ${optimal_price:.2f} (+{abs(price_variance_percent):.1f}%)"
            })
            if revenue_opportunity > 0:
                total_revenue_opportunity += revenue_opportunity

        elif price_variance_percent > 10:  # More than 10% above optimal
            overpriced.append({
                "menu_item_id": menu_item_id,
                "menu_name": menu_name,
                "current_price": round(current_price, 2),
                "optimal_price": round(optimal_price, 2),
                "suggested_price": round(optimal_price, 2),
                "current_food_cost_percent": round(food_cost_percent, 2),
                "variance_percent": round(price_variance_percent, 2),
                "sales_volume": total_units_sold,
                "quadrant": quadrant,
                "priority": "High" if quadrant == "puzzle" else "Medium",
                "recommendation": f"Consider lowering price from ${current_price:.2f} to ${optimal_price:.2f} ({price_variance_percent:.1f}%) to increase volume"
            })

        else:  # Within ±10% of optimal
            well_priced.append({
                "menu_item_id": menu_item_id,
                "menu_name": menu_name,
                "current_price": round(current_price, 2),
                "food_cost_percent": round(food_cost_percent, 2),
                "variance_percent": round(price_variance_percent, 2),
                "status": "Well-priced"
            })

    # Sort by revenue opportunity / priority
    underpriced.sort(key=lambda x: x["revenue_opportunity"], reverse=True)
    overpriced.sort(key=lambda x: x["sales_volume"], reverse=True)

    return {
        "underpriced_items": underpriced,
        "overpriced_items": overpriced,
        "well_priced_items": well_priced,
        "total_revenue_opportunity": round(total_revenue_opportunity, 2),
        "summary": {
            "underpriced_count": len(underpriced),
            "overpriced_count": len(overpriced),
            "well_priced_count": len(well_priced),
            "avg_variance": round(statistics.mean([abs(item["variance_percent"]) for item in underpriced + overpriced]), 2) if underpriced or overpriced else 0
        }
    }


def calculate_menu_pricing_strategy(unified_data: List[Dict], target_food_cost: float = 32.0) -> Dict:
    """
    FEATURE 2: Comprehensive menu pricing strategy analysis.

    Analyzes current pricing, identifies opportunities, and provides strategic recommendations
    for pricing optimization across the menu.

    Args:
        unified_data: List of unified menu item records from join_menu_data()
        target_food_cost: Target food cost percentage (default: 32%)

    Returns:
        Dictionary containing:
            - pricing_opportunities: Underpriced, overpriced, well-priced items
            - price_positioning: Price distribution and gap analysis
            - strategic_recommendations: Prioritized pricing actions
            - revenue_impact: Potential revenue from pricing adjustments
    """
    if not unified_data:
        raise ValueError("Cannot calculate pricing strategy with empty data")

    # Analyze pricing opportunities
    pricing_opportunities = identify_pricing_opportunities(unified_data, target_food_cost)

    # Analyze price positioning
    price_positioning = analyze_price_positioning(unified_data)

    # Generate strategic recommendations
    recommendations = []

    # Recommendation 1: Underpriced items
    if pricing_opportunities["underpriced_items"]:
        top_underpriced = pricing_opportunities["underpriced_items"][:3]
        total_opportunity = sum(item["revenue_opportunity"] for item in top_underpriced)
        recommendations.append({
            "priority": "High",
            "category": "Price Increases",
            "action": f"Increase prices on {len(pricing_opportunities['underpriced_items'])} underpriced items",
            "impact": f"${total_opportunity:,.2f} additional monthly revenue",
            "items": [item["menu_name"] for item in top_underpriced],
            "rationale": "These items have food cost % above target and room for price increases"
        })

    # Recommendation 2: Overpriced puzzles
    overpriced_puzzles = [item for item in pricing_opportunities["overpriced_items"] if item["quadrant"] == "puzzle"]
    if overpriced_puzzles:
        recommendations.append({
            "priority": "High",
            "category": "Price Reductions",
            "action": f"Reduce prices on {len(overpriced_puzzles)} overpriced Puzzle items",
            "impact": "Increase sales volume on high-margin items",
            "items": [item["menu_name"] for item in overpriced_puzzles[:3]],
            "rationale": "These items have high profitability but low sales - price reduction may boost volume"
        })

    # Recommendation 3: Price anchoring
    if price_positioning["anchor_opportunities"]:
        recommendations.append({
            "priority": "Medium",
            "category": "Menu Psychology",
            "action": "Leverage price anchoring opportunities",
            "impact": "Make mid-range items appear more affordable",
            "details": price_positioning["anchor_opportunities"],
            "rationale": "Strategic placement of high/low priced items influences customer perception"
        })

    # Recommendation 4: Fill price gaps
    if price_positioning["price_gaps"]:
        recommendations.append({
            "priority": "Low",
            "category": "Menu Balance",
            "action": f"Fill {len(price_positioning['price_gaps'])} price gaps in menu",
            "impact": "Provide more price point options for customers",
            "gaps": price_positioning["price_gaps"][:3],
            "rationale": "Large price gaps limit customer choice and may lose sales"
        })

    # Calculate overall revenue impact
    revenue_impact = {
        "total_opportunity": pricing_opportunities["total_revenue_opportunity"],
        "underpriced_items_impact": pricing_opportunities["total_revenue_opportunity"],
        "percentage_improvement": 0.0
    }

    # Calculate percentage improvement based on current total revenue
    total_current_revenue = sum(item.get("total_revenue", 0) for item in unified_data)
    if total_current_revenue > 0:
        revenue_impact["percentage_improvement"] = round(
            (revenue_impact["total_opportunity"] / total_current_revenue * 100), 2
        )

    return {
        "pricing_opportunities": pricing_opportunities,
        "price_positioning": price_positioning,
        "strategic_recommendations": recommendations,
        "revenue_impact": revenue_impact,
        "target_food_cost_percent": target_food_cost
    }


# ============================================================================
# FEATURE 3: MENU DESIGN RECOMMENDATIONS
# ============================================================================

def analyze_golden_triangle_placement(menu_engineering_matrix: Dict) -> List[Dict]:
    """
    Analyze which items should be placed in the "Golden Triangle" of the menu.

    The Golden Triangle is the area where customer eyes naturally go first:
    - Top right corner (primary focus)
    - Top center (secondary focus)
    - Middle center (tertiary focus)

    Args:
        menu_engineering_matrix: Menu engineering matrix from calculate_menu_engineering_matrix()

    Returns:
        List of placement recommendations for Golden Triangle positions
    """
    recommendations = []

    # Position 1: Top Right (Primary - highest priority)
    # Place highest profit STAR item here
    stars = menu_engineering_matrix.get("stars", [])
    if stars:
        top_star = max(stars, key=lambda x: x.get("total_profit", 0))
        recommendations.append({
            "position": "Top Right (Primary)",
            "menu_item": top_star.get("menu_name", "Unknown"),
            "reason": "Highest profit Star item - maximize visibility",
            "quadrant": "star",
            "expected_impact": "High - this position gets most attention",
            "design_notes": "Use larger font, highlight with box or color"
        })

    # Position 2: Top Center (Secondary)
    # Place second-best star or best plowhorse
    if len(stars) > 1:
        second_star = sorted(stars, key=lambda x: x.get("total_profit", 0), reverse=True)[1]
        recommendations.append({
            "position": "Top Center (Secondary)",
            "menu_item": second_star.get("menu_name", "Unknown"),
            "reason": "Second-best Star item - strong visibility",
            "quadrant": "star",
            "expected_impact": "Medium-High",
            "design_notes": "Emphasize with descriptive text"
        })
    else:
        plowhorses = menu_engineering_matrix.get("plowhorses", [])
        if plowhorses:
            top_plowhorse = max(plowhorses, key=lambda x: x.get("contribution_margin", 0))
            recommendations.append({
                "position": "Top Center (Secondary)",
                "menu_item": top_plowhorse.get("menu_name", "Unknown"),
                "reason": "Popular Plowhorse with best margin - upsell opportunity",
                "quadrant": "plowhorse",
                "expected_impact": "Medium",
                "design_notes": "Add premium ingredients to justify higher price"
            })

    # Position 3: Middle Center (Tertiary)
    # Place best puzzle item to increase awareness
    puzzles = menu_engineering_matrix.get("puzzles", [])
    if puzzles:
        top_puzzle = max(puzzles, key=lambda x: x.get("contribution_margin", 0))
        recommendations.append({
            "position": "Middle Center (Tertiary)",
            "menu_item": top_puzzle.get("menu_name", "Unknown"),
            "reason": "High-margin Puzzle needs visibility boost",
            "quadrant": "puzzle",
            "expected_impact": "Medium - can convert to Star with better placement",
            "design_notes": "Add appetizing description and chef recommendation"
        })

    return recommendations


def generate_menu_layout_strategy(menu_engineering_matrix: Dict, unified_data: List[Dict]) -> Dict:
    """
    Generate comprehensive menu layout strategy based on quadrant analysis.

    Args:
        menu_engineering_matrix: Menu engineering matrix with quadrant classifications
        unified_data: Original unified menu data

    Returns:
        Dictionary with layout recommendations by section
    """
    # Group items by category
    categories = {}
    for item in unified_data:
        category = item.get("category", "Other")
        if category not in categories:
            categories[category] = []
        categories[category].append(item)

    layout_strategy = {
        "section_order": [],
        "category_layouts": {},
        "visual_hierarchy": [],
        "psychological_techniques": []
    }

    # Recommended section order (based on menu engineering principles)
    # 1. Appetizers (low barrier to entry)
    # 2. Entrees (main profit center)
    # 3. Sides (upsell opportunities)
    # 4. Desserts (final upsell)

    category_priority = {
        "Appetizer": 1,
        "Entree": 2,
        "Side": 3,
        "Dessert": 4
    }

    sorted_categories = sorted(categories.keys(), key=lambda x: category_priority.get(x, 99))
    layout_strategy["section_order"] = sorted_categories

    # Layout recommendations for each category
    for category in sorted_categories:
        items = categories[category]

        # Classify items by quadrant
        stars = [item for item in items if item.get("quadrant") == "star"]
        plowhorses = [item for item in items if item.get("quadrant") == "plowhorse"]
        puzzles = [item for item in items if item.get("quadrant") == "puzzle"]
        dogs = [item for item in items if item.get("quadrant") == "dog"]

        layout_strategy["category_layouts"][category] = {
            "item_count": len(items),
            "recommended_order": [
                {"position": 1, "items": [s.get("menu_name") for s in stars[:2]], "emphasis": "High", "note": "Lead with Stars"},
                {"position": 2, "items": [p.get("menu_name") for p in puzzles[:2]], "emphasis": "Medium-High", "note": "Build awareness for Puzzles"},
                {"position": 3, "items": [p.get("menu_name") for p in plowhorses], "emphasis": "Medium", "note": "Fill middle positions with Plowhorses"},
                {"position": 4, "items": [d.get("menu_name") for d in dogs], "emphasis": "Low", "note": "Bury Dogs at bottom or remove"}
            ],
            "stars_count": len(stars),
            "puzzles_count": len(puzzles),
            "plowhorses_count": len(plowhorses),
            "dogs_count": len(dogs)
        }

    # Visual hierarchy recommendations
    layout_strategy["visual_hierarchy"] = [
        {
            "level": "Primary (Largest font, highlighted)",
            "items": "Star items - especially top 3 by profit",
            "design": "18-20pt font, bold, colored box or border"
        },
        {
            "level": "Secondary (Medium emphasis)",
            "items": "Puzzle items - need visibility boost",
            "design": "16pt font, descriptive text, appetizing adjectives"
        },
        {
            "level": "Tertiary (Standard)",
            "items": "Plowhorse items - already popular",
            "design": "14pt font, standard formatting"
        },
        {
            "level": "Minimal (Smallest, least emphasis)",
            "items": "Dog items - or consider removing",
            "design": "12pt font, minimal description, bottom of section"
        }
    ]

    # Psychological techniques
    layout_strategy["psychological_techniques"] = [
        {
            "technique": "Price Anchoring",
            "application": "Place highest-priced item first in each category",
            "benefit": "Makes other items seem more affordable by comparison"
        },
        {
            "technique": "Decoy Pricing",
            "application": "Position a similar but slightly inferior item near your target item",
            "benefit": "Makes target item appear as better value"
        },
        {
            "technique": "Remove Dollar Signs",
            "application": "Write prices as '15.99' instead of '$15.99'",
            "benefit": "Reduces pain of paying - prices feel less expensive"
        },
        {
            "technique": "Strategic Descriptions",
            "application": "Add evocative descriptions to high-margin items",
            "benefit": "Justifies premium pricing and increases perceived value"
        },
        {
            "technique": "Limited Items Per Section",
            "application": "Keep each category to 6-8 items maximum",
            "benefit": "Reduces decision fatigue and increases conversion"
        },
        {
            "technique": "Box Highlights",
            "application": "Put Star and Puzzle items in visual boxes",
            "benefit": "Draws eye naturally to high-profit items"
        }
    ]

    return layout_strategy


def calculate_menu_design_recommendations(
    unified_data: List[Dict],
    menu_engineering_matrix: Dict
) -> Dict:
    """
    FEATURE 3: Comprehensive menu design and layout recommendations.

    Applies menu psychology principles including Golden Triangle placement,
    visual hierarchy, and psychological pricing techniques.

    Args:
        unified_data: List of unified menu item records
        menu_engineering_matrix: Menu engineering matrix with quadrant classifications

    Returns:
        Dictionary containing:
            - golden_triangle: Placement recommendations for prime menu positions
            - layout_strategy: Category order and item positioning
            - design_principles: Visual hierarchy and emphasis guidelines
            - implementation_guide: Step-by-step menu redesign instructions
    """
    if not unified_data:
        raise ValueError("Cannot generate design recommendations with empty data")

    if not menu_engineering_matrix:
        raise ValueError("Menu engineering matrix required for design recommendations")

    # Generate Golden Triangle placement recommendations
    golden_triangle = analyze_golden_triangle_placement(menu_engineering_matrix)

    # Generate comprehensive layout strategy
    layout_strategy = generate_menu_layout_strategy(menu_engineering_matrix, unified_data)

    # Design principles based on quadrant analysis
    stars = menu_engineering_matrix.get("stars", [])
    puzzles = menu_engineering_matrix.get("puzzles", [])
    plowhorses = menu_engineering_matrix.get("plowhorses", [])
    dogs = menu_engineering_matrix.get("dogs", [])

    design_principles = {
        "stars_treatment": {
            "count": len(stars),
            "strategy": "Maximize Visibility",
            "tactics": [
                "Place in Golden Triangle positions",
                "Use largest font size (18-20pt)",
                "Add visual highlights (boxes, colors, icons)",
                "Include mouth-watering descriptions",
                "Consider adding photos"
            ],
            "items": [item.get("menu_name") for item in stars[:5]]
        },
        "puzzles_treatment": {
            "count": len(puzzles),
            "strategy": "Build Awareness",
            "tactics": [
                "Position near top of category sections",
                "Add descriptive language to justify price",
                "Include chef recommendations or awards",
                "Use medium emphasis (16pt font)",
                "Consider limited-time offers to boost trial"
            ],
            "items": [item.get("menu_name") for item in puzzles[:5]]
        },
        "plowhorses_treatment": {
            "count": len(plowhorses),
            "strategy": "Maintain Sales While Improving Margins",
            "tactics": [
                "Keep standard formatting - already popular",
                "Position in middle of sections",
                "Look for upsell opportunities (add premium options)",
                "Consider slight price increases (<5%)",
                "Add modifiers to increase check average"
            ],
            "items": [item.get("menu_name") for item in plowhorses[:5]]
        },
        "dogs_treatment": {
            "count": len(dogs),
            "strategy": "Minimize or Remove",
            "tactics": [
                "Remove from menu if possible",
                "If kept, place at bottom with minimal emphasis",
                "Use smallest font size (12pt)",
                "No descriptions or highlights",
                "Consider replacing with new test items"
            ],
            "items": [item.get("menu_name") for item in dogs[:5]]
        }
    }

    # Implementation guide
    implementation_guide = {
        "phase_1_immediate": [
            "Identify Golden Triangle positions on current menu",
            "Move top 3 Star items to these premium positions",
            "Increase font size for Star items by 20-30%",
            "Bury or remove Dog items from prominent positions"
        ],
        "phase_2_short_term": [
            "Rewrite descriptions for Puzzle items to increase appeal",
            "Add visual boxes or borders around Star and Puzzle items",
            "Reorder items within categories (Stars first, Dogs last)",
            "Remove dollar signs from prices",
            "Ensure 6-8 items maximum per category"
        ],
        "phase_3_medium_term": [
            "Redesign menu layout following recommended section order",
            "Implement full visual hierarchy system",
            "Add high-quality photos for top 3 Star items",
            "Create decoy items near target high-margin items",
            "Test limited-time offers for Puzzle items"
        ],
        "success_metrics": [
            "Track sales changes for repositioned items (target: +15-25%)",
            "Monitor average check size (target: +10-15%)",
            "Measure Stars category sales mix (target: 30-35% of total)",
            "Track food cost % improvement (target: -2-3%)",
            "Survey customer satisfaction with new menu design"
        ]
    }

    return {
        "golden_triangle": golden_triangle,
        "layout_strategy": layout_strategy,
        "design_principles": design_principles,
        "implementation_guide": implementation_guide,
        "quadrant_counts": {
            "stars": len(stars),
            "puzzles": len(puzzles),
            "plowhorses": len(plowhorses),
            "dogs": len(dogs)
        }
    }
