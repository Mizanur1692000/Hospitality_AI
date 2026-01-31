"""
Recipe Creation Task
Generates a structured HTML recipe summary with metadata, ingredients, and optional costing.
"""

from backend.shared.utils.common import success_payload, error_payload
from backend.consulting_services.kpi.kpi_utils import format_business_report


def _parse_ingredients_list(ingredients):
    """Normalize ingredients into a list of dicts with name, amount, unit."""
    normalized = []
    if isinstance(ingredients, list):
        for item in ingredients:
            if isinstance(item, dict):
                name = item.get('name') or item.get('ingredient') or str(item)
                amount = float(item.get('amount', 0)) if isinstance(item.get('amount'), (int, float, str)) else 0.0
                unit = item.get('unit') or ''
                normalized.append({'name': name, 'amount': amount, 'unit': unit})
            elif isinstance(item, str):
                normalized.append({'name': item, 'amount': 0.0, 'unit': ''})
    elif isinstance(ingredients, str):
        # Split by commas or semicolons and attempt to parse "Name amount unit"
        import re
        parts = [p.strip() for p in re.split(r'[;,]+', ingredients) if p.strip()]
        for p in parts:
            m = re.match(r'^([A-Za-z0-9 \-]+)\s+([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)?$', p)
            if m:
                name, amount, unit = m.group(1).strip(), float(m.group(2)), (m.group(3) or '').strip()
                normalized.append({'name': name, 'amount': amount, 'unit': unit})
            else:
                normalized.append({'name': p, 'amount': 0.0, 'unit': ''})
    return normalized


def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    """
    Create recipe summary and return HTML report.

    Required:
      - recipe_name
      - servings (optional, default 1)
      - prep_time, cook_time (optional, minutes)
      - ingredients (optional string or list)
      - ingredient_cost, labor_cost (optional for cost per serving)
    """
    service, subtask = "recipe", "creation"

    try:
        recipe_name = (params.get('recipe_name') or '').strip()
        if not recipe_name:
            return error_payload(service, subtask, "Missing required field: recipe_name")

        servings = float(params.get('servings', 1) or 1)
        prep_time = float(params.get('prep_time', 0) or 0)
        cook_time = float(params.get('cook_time', 0) or 0)
        ingredient_cost = float(params.get('ingredient_cost', 0) or 0)
        labor_cost = float(params.get('labor_cost', 0) or 0)
        recipe_price = float(params.get('recipe_price', 0) or 0)

        ingredients_raw = params.get('ingredients') or params.get('ingredient_list') or ''
        ingredients = _parse_ingredients_list(ingredients_raw)
        total_ingredients = len(ingredients)

        total_cost = ingredient_cost + labor_cost
        cost_per_serving = (total_cost / servings) if (servings and total_cost) else 0
        profit_margin = ((recipe_price - cost_per_serving) / recipe_price * 100) if recipe_price else 0

        metrics = {
            'recipe_name': recipe_name,
            'servings': servings,
            'prep_time_minutes': prep_time,
            'cook_time_minutes': cook_time,
            'ingredient_cost': ingredient_cost,
            'labor_cost': labor_cost,
            'total_cost': total_cost,
            'cost_per_serving': round(cost_per_serving, 2),
            'recipe_price': recipe_price,
            'estimated_margin_percent': round(profit_margin, 1) if recipe_price else None,
            'total_ingredients': total_ingredients,
        }

        performance = {
            'completeness': 'Complete' if total_ingredients > 0 and servings > 0 else 'Partial',
            'costing_status': 'Calculated' if total_cost > 0 else 'Missing Costs',
        }

        recommendations = []
        if total_cost == 0:
            recommendations.append('Add ingredient_cost and labor_cost to calculate cost per serving.')
        if not ingredients:
            recommendations.append('Provide an ingredient list with quantities and units.')
        if recipe_price and profit_margin < 65:
            recommendations.append('Consider adjusting recipe_price to target 65-70% margin.')
        if not recommendations:
            recommendations.append('Recipe setup looks good. Proceed to costing and scaling as needed.')

        benchmarks = {
            'target_margin': '65-70%',
            'prep_time_guideline': '15-30 minutes typical for simple dishes',
        }

        additional_data = {
            'ingredients': ingredients,
            'notes': 'Steps can be generated via the AI assistant if requested.',
        }

        result = format_business_report(
            "Recipe Creation Summary",
            metrics,
            performance,
            recommendations,
            benchmarks,
            additional_data,
        )

        business_report_html = result.get('business_report_html', '')
        business_report = result.get('business_report', '')

        return success_payload(
            service,
            subtask,
            params,
            {
                'analysis_type': 'Recipe Creation Summary',
                'business_report_html': business_report_html,
                'business_report': business_report,
                'metrics': metrics,
                'performance': performance,
                'recommendations': recommendations,
            },
            recommendations,
        ), 200

    except Exception as e:
        return error_payload(service, subtask, f"Creation failed: {str(e)}")
