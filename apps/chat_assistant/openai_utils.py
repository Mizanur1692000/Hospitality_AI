# chat_assistant/openai_utils.py
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def extract_kpi_data(prompt: str) -> dict:
    """Extract KPI data from user prompt using regex patterns."""
    import urllib.parse

    data = {}
    # Decode URL encoding if present
    decoded_prompt = urllib.parse.unquote(prompt)

    # Find all numbers (including those with commas)
    number_matches = re.findall(r'([0-9,]+)', decoded_prompt)

    # Convert to floats, filtering out empty strings
    number_values = []
    for val in number_matches:
        if val and val.strip():
            try:
                number_values.append(float(val.replace(',', '')))
            except ValueError:
                continue

    # Simple keyword-based extraction
    prompt_lower = decoded_prompt.lower()

    # Extract values based on keywords and position
    if number_values:
        # Extract total sales - usually the first large number
        if any(word in prompt_lower for word in ['sales', 'revenue', 'total']):
            data['total_sales'] = number_values[0]

        # Extract labor cost - look for "labor cost" or "labor" followed by a number
        labor_match = re.search(r'labor\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if labor_match:
            data['labor_cost'] = float(labor_match.group(1).replace(',', ''))
        elif 'labor' in prompt_lower and len(number_values) > 1:
            data['labor_cost'] = number_values[1]

        # Extract food cost - look for "food cost" or "food" followed by a number
        food_match = re.search(r'food\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if food_match:
            data['food_cost'] = float(food_match.group(1).replace(',', ''))
        elif 'food' in prompt_lower and len(number_values) > 2:
            data['food_cost'] = number_values[2]

        # Extract hours worked - look for "hours" followed by a number
        hours_match = re.search(r'hours?[:\s]*([0-9,]+)', prompt_lower)
        if hours_match:
            data['hours_worked'] = float(hours_match.group(1).replace(',', ''))
        elif any(word in prompt_lower for word in ['hours', 'hour']):
            # Find the largest number that could be hours
            for num in sorted(number_values, reverse=True):
                if num > 0 and num < 1000:  # Reasonable range for hours
                    data['hours_worked'] = num
                    break

        # Extract hourly rate - look for "rate" or "hourly" followed by a number
        rate_match = re.search(r'(?:hourly\s+)?rate[:\s]*([0-9,]+)', prompt_lower)
        if rate_match:
            data['hourly_rate'] = float(rate_match.group(1).replace(',', ''))
        else:
            # Use second dollar value if it's in reasonable range
            for val in number_values[1:]:  # Skip first value (sales)
                if 10 <= val <= 100:  # Reasonable range for hourly rates
                    data['hourly_rate'] = val
                    break

        # Extract HR-specific metrics
        # Turnover rate
        turnover_match = re.search(r'turnover\s+rate[:\s]*([0-9,]+)', prompt_lower)
        if turnover_match:
            data['turnover_rate'] = float(turnover_match.group(1).replace(',', ''))
        elif 'turnover' in prompt_lower and number_values:
            # Use first number if turnover is mentioned
            data['turnover_rate'] = number_values[0]

        # Industry average
        industry_match = re.search(r'industry\s+(?:average|avg)[:\s]*([0-9,]+)', prompt_lower)
        if industry_match:
            data['industry_average'] = float(industry_match.group(1).replace(',', ''))

        # Performance metrics
        satisfaction_match = re.search(r'customer\s+satisfaction[:\s]*([0-9,]+)', prompt_lower)
        if satisfaction_match:
            data['customer_satisfaction'] = float(satisfaction_match.group(1).replace(',', ''))

        performance_match = re.search(r'sales\s+performance[:\s]*([0-9,]+)', prompt_lower)
        if performance_match:
            data['sales_performance'] = float(performance_match.group(1).replace(',', ''))

        efficiency_match = re.search(r'efficiency\s+score[:\s]*([0-9,]+)', prompt_lower)
        if efficiency_match:
            data['efficiency_score'] = float(efficiency_match.group(1).replace(',', ''))

        attendance_match = re.search(r'attendance\s+rate[:\s]*([0-9,]+)', prompt_lower)
        if attendance_match:
            data['attendance_rate'] = float(attendance_match.group(1).replace(',', ''))

        # Extract Beverage Management metrics
        # Liquor cost metrics
        expected_oz_match = re.search(r'expected\s+(?:oz|ounces?)[:\s]*([0-9,]+)', prompt_lower)
        if expected_oz_match:
            data['expected_oz'] = float(expected_oz_match.group(1).replace(',', ''))

        actual_oz_match = re.search(r'actual\s+(?:oz|ounces?)[:\s]*([0-9,]+)', prompt_lower)
        if actual_oz_match:
            data['actual_oz'] = float(actual_oz_match.group(1).replace(',', ''))

        liquor_cost_match = re.search(r'liquor\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if liquor_cost_match:
            data['liquor_cost'] = float(liquor_cost_match.group(1).replace(',', ''))

        # Inventory metrics
        current_stock_match = re.search(r'current\s+stock[:\s]*([0-9,]+)', prompt_lower)
        if current_stock_match:
            data['current_stock'] = float(current_stock_match.group(1).replace(',', ''))

        reorder_point_match = re.search(r'reorder\s+point[:\s]*([0-9,]+)', prompt_lower)
        if reorder_point_match:
            data['reorder_point'] = float(reorder_point_match.group(1).replace(',', ''))

        monthly_usage_match = re.search(r'monthly\s+usage[:\s]*([0-9,]+)', prompt_lower)
        if monthly_usage_match:
            data['monthly_usage'] = float(monthly_usage_match.group(1).replace(',', ''))

        inventory_value_match = re.search(r'inventory\s+value[:\s]*([0-9,]+)', prompt_lower)
        if inventory_value_match:
            data['inventory_value'] = float(inventory_value_match.group(1).replace(',', ''))

        # Pricing metrics
        drink_price_match = re.search(r'drink\s+price[:\s]*([0-9,]+)', prompt_lower)
        if drink_price_match:
            data['drink_price'] = float(drink_price_match.group(1).replace(',', ''))

        cost_per_drink_match = re.search(r'cost\s+per\s+drink[:\s]*([0-9,]+)', prompt_lower)
        if cost_per_drink_match:
            data['cost_per_drink'] = float(cost_per_drink_match.group(1).replace(',', ''))

        sales_volume_match = re.search(r'sales\s+volume[:\s]*([0-9,]+)', prompt_lower)
        if sales_volume_match:
            data['sales_volume'] = float(sales_volume_match.group(1).replace(',', ''))

        competitor_price_match = re.search(r'competitor\s+price[:\s]*([0-9,]+)', prompt_lower)
        if competitor_price_match:
            data['competitor_price'] = float(competitor_price_match.group(1).replace(',', ''))

        # Extract Menu Engineering metrics
        # Product mix metrics
        item_sales_match = re.search(r'item\s+sales[:\s]*([0-9,]+)', prompt_lower)
        if item_sales_match:
            data['item_sales'] = float(item_sales_match.group(1).replace(',', ''))

        item_cost_match = re.search(r'item\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if item_cost_match:
            data['item_cost'] = float(item_cost_match.group(1).replace(',', ''))

        item_profit_match = re.search(r'item\s+profit[:\s]*([0-9,]+)', prompt_lower)
        if item_profit_match:
            data['item_profit'] = float(item_profit_match.group(1).replace(',', ''))

        item_price_match = re.search(r'item\s+price[:\s]*([0-9,]+)', prompt_lower)
        if item_price_match:
            data['item_price'] = float(item_price_match.group(1).replace(',', ''))

        # Menu design metrics
        menu_items_match = re.search(r'menu\s+items[:\s]*([0-9,]+)', prompt_lower)
        if menu_items_match:
            data['menu_items'] = float(menu_items_match.group(1).replace(',', ''))

        high_profit_items_match = re.search(r'high\s+profit\s+items[:\s]*([0-9,]+)', prompt_lower)
        if high_profit_items_match:
            data['high_profit_items'] = float(high_profit_items_match.group(1).replace(',', ''))

        sales_distribution_match = re.search(r'sales\s+distribution[:\s]*([0-9,]+)', prompt_lower)
        if sales_distribution_match:
            data['sales_distribution'] = float(sales_distribution_match.group(1).replace(',', ''))

        visual_hierarchy_match = re.search(r'visual\s+hierarchy[:\s]*([0-9,]+)', prompt_lower)
        if visual_hierarchy_match:
            data['visual_hierarchy'] = float(visual_hierarchy_match.group(1).replace(',', ''))

        # Extract Recipe Management metrics
        # Recipe costing metrics
        ingredient_cost_match = re.search(r'ingredient\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if ingredient_cost_match:
            data['ingredient_cost'] = float(ingredient_cost_match.group(1).replace(',', ''))

        portion_cost_match = re.search(r'portion\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if portion_cost_match:
            data['portion_cost'] = float(portion_cost_match.group(1).replace(',', ''))

        recipe_price_match = re.search(r'recipe\s+price[:\s]*([0-9,]+)', prompt_lower)
        if recipe_price_match:
            data['recipe_price'] = float(recipe_price_match.group(1).replace(',', ''))

        # Ingredient optimization metrics
        current_cost_match = re.search(r'current\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if current_cost_match:
            data['current_cost'] = float(current_cost_match.group(1).replace(',', ''))

        supplier_cost_match = re.search(r'supplier\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if supplier_cost_match:
            data['supplier_cost'] = float(supplier_cost_match.group(1).replace(',', ''))

        waste_percentage_match = re.search(r'waste\s+percentage[:\s]*([0-9,]+)', prompt_lower)
        if waste_percentage_match:
            data['waste_percentage'] = float(waste_percentage_match.group(1).replace(',', ''))

        quality_score_match = re.search(r'quality\s+score[:\s]*([0-9,]+)', prompt_lower)
        if quality_score_match:
            data['quality_score'] = float(quality_score_match.group(1).replace(',', ''))

        # Recipe scaling metrics
        current_batch_match = re.search(r'current\s+batch[:\s]*([0-9,]+)', prompt_lower)
        if current_batch_match:
            data['current_batch'] = float(current_batch_match.group(1).replace(',', ''))

        target_batch_match = re.search(r'target\s+batch[:\s]*([0-9,]+)', prompt_lower)
        if target_batch_match:
            data['target_batch'] = float(target_batch_match.group(1).replace(',', ''))

        yield_percentage_match = re.search(r'yield\s+percentage[:\s]*([0-9,]+)', prompt_lower)
        if yield_percentage_match:
            data['yield_percentage'] = float(yield_percentage_match.group(1).replace(',', ''))

        consistency_score_match = re.search(r'consistency\s+score[:\s]*([0-9,]+)', prompt_lower)
        if consistency_score_match:
            data['consistency_score'] = float(consistency_score_match.group(1).replace(',', ''))

        # Extract Strategic Planning metrics
        # Sales forecasting metrics
        historical_sales_match = re.search(r'historical\s+sales[:\s]*([0-9,]+)', prompt_lower)
        if historical_sales_match:
            data['historical_sales'] = float(historical_sales_match.group(1).replace(',', ''))

        current_sales_match = re.search(r'current\s+sales[:\s]*([0-9,]+)', prompt_lower)
        if current_sales_match:
            data['current_sales'] = float(current_sales_match.group(1).replace(',', ''))

        growth_rate_match = re.search(r'growth\s+rate[:\s]*([0-9,]+)', prompt_lower)
        if growth_rate_match:
            data['growth_rate'] = float(growth_rate_match.group(1).replace(',', ''))

        seasonal_factor_match = re.search(r'seasonal\s+factor[:\s]*([0-9,]+)', prompt_lower)
        if seasonal_factor_match:
            data['seasonal_factor'] = float(seasonal_factor_match.group(1).replace(',', ''))

        # Growth strategy metrics
        market_size_match = re.search(r'market\s+size[:\s]*([0-9,]+)', prompt_lower)
        if market_size_match:
            data['market_size'] = float(market_size_match.group(1).replace(',', ''))

        market_share_match = re.search(r'market\s+share[:\s]*([0-9,]+)', prompt_lower)
        if market_share_match:
            data['market_share'] = float(market_share_match.group(1).replace(',', ''))

        competition_level_match = re.search(r'competition\s+level[:\s]*([0-9,]+)', prompt_lower)
        if competition_level_match:
            data['competition_level'] = float(competition_level_match.group(1).replace(',', ''))

        investment_budget_match = re.search(r'investment\s+budget[:\s]*([0-9,]+)', prompt_lower)
        if investment_budget_match:
            data['investment_budget'] = float(investment_budget_match.group(1).replace(',', ''))

        # Operational excellence metrics
        efficiency_score_match = re.search(r'efficiency\s+score[:\s]*([0-9,]+)', prompt_lower)
        if efficiency_score_match:
            data['efficiency_score'] = float(efficiency_score_match.group(1).replace(',', ''))

        process_time_match = re.search(r'process\s+time[:\s]*([0-9,]+)', prompt_lower)
        if process_time_match:
            data['process_time'] = float(process_time_match.group(1).replace(',', ''))

        quality_rating_match = re.search(r'quality\s+rating[:\s]*([0-9,]+)', prompt_lower)
        if quality_rating_match:
            data['quality_rating'] = float(quality_rating_match.group(1).replace(',', ''))

        customer_satisfaction_match = re.search(r'customer\s+satisfaction[:\s]*([0-9,]+)', prompt_lower)
        if customer_satisfaction_match:
            data['customer_satisfaction'] = float(customer_satisfaction_match.group(1).replace(',', ''))

        # Extract KPI Dashboard metrics
        # Comprehensive analysis metrics
        prime_cost_match = re.search(r'prime\s+cost[:\s]*([0-9,]+)', prompt_lower)
        if prime_cost_match:
            data['prime_cost'] = float(prime_cost_match.group(1).replace(',', ''))

        # Performance optimization metrics
        current_performance_match = re.search(r'current\s+performance[:\s]*([0-9,]+)', prompt_lower)
        if current_performance_match:
            data['current_performance'] = float(current_performance_match.group(1).replace(',', ''))

        target_performance_match = re.search(r'target\s+performance[:\s]*([0-9,]+)', prompt_lower)
        if target_performance_match:
            data['target_performance'] = float(target_performance_match.group(1).replace(',', ''))

        optimization_potential_match = re.search(r'optimization\s+potential[:\s]*([0-9,]+)', prompt_lower)
        if optimization_potential_match:
            data['optimization_potential'] = float(optimization_potential_match.group(1).replace(',', ''))

        efficiency_score_match = re.search(r'efficiency\s+score[:\s]*([0-9,]+)', prompt_lower)
        if efficiency_score_match:
            data['efficiency_score'] = float(efficiency_score_match.group(1).replace(',', ''))

    return data


def handle_kpi_analysis(prompt: str) -> str:
    """Handle KPI analysis requests by calling our specialized functions."""
    try:
        # Import here to avoid circular imports
        from backend.consulting_services.kpi.kpi_utils import (
            calculate_labor_cost_analysis,
            calculate_prime_cost_analysis,
            calculate_sales_performance_analysis,
            calculate_kpi_summary
        )
        from backend.consulting_services.kpi.legacy_labor import calculate_labor_cost
        from backend.consulting_services.inventory.tracking import calculate_inventory_variance

        data = extract_kpi_data(prompt)

        # Determine which analysis to run based on keywords
        prompt_lower = prompt.lower()

        # Import here to avoid circular imports
        from apps.agent_core.task_registry import task_registry

        # Check for KPI Dashboard analysis requests first (most specific)
        if any(keyword in prompt_lower for keyword in ['comprehensive analysis', 'multi-metric analysis', 'industry benchmarking']):
            if 'total_sales' in data and 'labor_cost' in data and 'food_cost' in data and 'prime_cost' in data:
                result, status = task_registry.execute_task(
                    service="kpi_dashboard",
                    subtask="comprehensive_analysis",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['performance optimization', 'optimization strategies', 'goal setting']):
            if 'current_performance' in data and 'target_performance' in data and 'optimization_potential' in data and 'efficiency_score' in data:
                result, status = task_registry.execute_task(
                    service="kpi_dashboard",
                    subtask="performance_optimization",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for Strategic Planning analysis requests
        elif any(keyword in prompt_lower for keyword in ['sales forecasting', 'historical trends', 'growth projections']):
            if 'historical_sales' in data and 'current_sales' in data and 'growth_rate' in data and 'seasonal_factor' in data:
                result, status = task_registry.execute_task(
                    service="strategic",
                    subtask="sales_forecasting",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['growth strategy', 'market analysis', 'competitive positioning']):
            if 'market_size' in data and 'market_share' in data and 'competition_level' in data and 'investment_budget' in data:
                result, status = task_registry.execute_task(
                    service="strategic",
                    subtask="growth_strategy",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['operational excellence', 'process optimization', 'efficiency metrics']):
            if 'efficiency_score' in data and 'process_time' in data and 'quality_rating' in data and 'customer_satisfaction' in data:
                result, status = task_registry.execute_task(
                    service="strategic",
                    subtask="operational_excellence",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for Recipe Management analysis requests
        elif any(keyword in prompt_lower for keyword in ['recipe costing', 'ingredient cost', 'portion cost']):
            if 'ingredient_cost' in data and 'portion_cost' in data and 'recipe_price' in data:
                result, status = task_registry.execute_task(
                    service="recipe",
                    subtask="costing",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['ingredient optimization', 'supplier cost', 'waste reduction']):
            if 'current_cost' in data and 'supplier_cost' in data and 'waste_percentage' in data and 'quality_score' in data:
                result, status = task_registry.execute_task(
                    service="recipe",
                    subtask="ingredient_optimization",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['recipe scaling', 'batch size', 'yield calculation']):
            if 'current_batch' in data and 'target_batch' in data and 'yield_percentage' in data and 'consistency_score' in data:
                result, status = task_registry.execute_task(
                    service="recipe",
                    subtask="scaling",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for Menu Engineering analysis requests
        elif any(keyword in prompt_lower for keyword in ['product mix', 'menu analysis', 'item performance']):
            if 'total_sales' in data and 'item_sales' in data and 'item_cost' in data and 'item_profit' in data:
                result, status = task_registry.execute_task(
                    service="menu",
                    subtask="product_mix",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['menu pricing', 'pricing analysis', 'price optimization']):
            if 'item_price' in data and 'item_cost' in data and 'competitor_price' in data:
                result, status = task_registry.execute_task(
                    service="menu",
                    subtask="pricing",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['menu design', 'design analysis', 'visual hierarchy']):
            if 'menu_items' in data and 'high_profit_items' in data and 'sales_distribution' in data and 'visual_hierarchy' in data:
                result, status = task_registry.execute_task(
                    service="menu",
                    subtask="design",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for Beverage Management analysis requests
        elif any(keyword in prompt_lower for keyword in ['liquor cost', 'liquor analysis', 'liquor variance']):
            if 'expected_oz' in data and 'actual_oz' in data and 'liquor_cost' in data and 'total_sales' in data:
                result, status = task_registry.execute_task(
                    service="beverage",
                    subtask="liquor_cost",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['bar inventory', 'inventory management', 'stock level']):
            if 'current_stock' in data and 'reorder_point' in data and 'monthly_usage' in data and 'inventory_value' in data:
                result, status = task_registry.execute_task(
                    service="beverage",
                    subtask="inventory",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['beverage pricing', 'drink pricing', 'pricing analysis']):
            if 'drink_price' in data and 'cost_per_drink' in data and 'sales_volume' in data and 'competitor_price' in data:
                result, status = task_registry.execute_task(
                    service="beverage",
                    subtask="pricing",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for HR analysis requests
        elif any(keyword in prompt_lower for keyword in ['staff retention', 'retention analysis', 'turnover rate']):
            if 'turnover_rate' in data:
                result, status = task_registry.execute_task(
                    service="hr",
                    subtask="staff_retention",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['labor scheduling', 'scheduling optimization', 'staff scheduling']):
            if 'total_sales' in data and ('labor_hours' in data or 'hours_worked' in data) and 'hourly_rate' in data:
                result, status = task_registry.execute_task(
                    service="hr",
                    subtask="labor_scheduling",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['performance management', 'staff performance', 'performance analysis']):
            # For performance management, we need at least one performance metric
            if any(key in data for key in ['customer_satisfaction', 'sales_performance', 'efficiency_score', 'attendance_rate']):
                result, status = task_registry.execute_task(
                    service="hr",
                    subtask="performance_management",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for KPI analysis requests
        elif any(keyword in prompt_lower for keyword in ['sales performance', 'sales analysis', 'revenue analysis', 'performance analysis', 'growth analysis']):
            if 'total_sales' in data and 'labor_cost' in data and 'food_cost' in data and 'hours_worked' in data:
                result, status = task_registry.execute_task(
                    service="kpi",
                    subtask="sales_performance",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['prime cost', 'prime analysis', 'total cost']):
            if 'total_sales' in data and 'labor_cost' in data and 'food_cost' in data:
                result, status = task_registry.execute_task(
                    service="kpi",
                    subtask="prime_cost",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        elif any(keyword in prompt_lower for keyword in ['labor cost', 'labor analysis', 'labor efficiency']):
            if 'total_sales' in data and 'labor_cost' in data and 'hours_worked' in data:
                result, status = task_registry.execute_task(
                    service="kpi",
                    subtask="labor_cost",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for simple labor cost calculation (using new formatter)
        elif any(keyword in prompt_lower for keyword in ['labor cost', 'labor hours', 'hourly rate']):
            if 'total_sales' in data and 'hours_worked' in data:
                # Extract hourly rate from prompt or use default
                hourly_rate_match = re.search(r'(?:hourly\s+rate|rate)[:\s]*\$?([0-9.]+)', prompt, re.IGNORECASE)
                hourly_rate = float(hourly_rate_match.group(1)) if hourly_rate_match else 15.0

                result = calculate_labor_cost(
                    total_sales=data['total_sales'],
                    labor_hours=data['hours_worked'],
                    hourly_rate=hourly_rate
                )
                if result.get('status') == 'success':
                    return result.get('business_report', 'Analysis completed but no report generated.')
                else:
                    return f"Error: {result.get('message', 'Unknown error')}"

        # Check for KPI summary (using new formatter)
        elif 'total_sales' in data and 'labor_cost' in data and 'food_cost' in data and 'hours_worked' in data:
            result = calculate_kpi_summary(
                total_sales=data['total_sales'],
                labor_cost=data['labor_cost'],
                food_cost=data['food_cost'],
                hours_worked=data['hours_worked']
            )
            if result.get('status') == 'success':
                return result.get('business_report', 'Analysis completed but no report generated.')
            else:
                return f"Error: {result.get('message', 'Unknown error')}"


        # Check for inventory variance
        elif any(keyword in prompt_lower for keyword in ['inventory', 'variance', 'expected', 'actual']):
            expected_match = re.search(r'(?:expected|forecast)[:\s]*([0-9.]+)', prompt, re.IGNORECASE)
            actual_match = re.search(r'(?:actual|used)[:\s]*([0-9.]+)', prompt, re.IGNORECASE)

            if expected_match and actual_match:
                result = calculate_inventory_variance(
                    expected_usage=float(expected_match.group(1)),
                    actual_usage=float(actual_match.group(1))
                )
                if result.get('status') == 'success':
                    return result.get('business_report', 'Analysis completed but no report generated.')
                else:
                    return f"Error: {result.get('message', 'Unknown error')}"

        return None  # No analysis detected

    except Exception as e:
        return f"Error processing KPI analysis: {str(e)}"


def handle_conversational_ai(prompt: str) -> str:
    """
    Route natural language queries to Conversational AI for menu/business analysis.

    This uses the Conversational AI endpoint which:
    - Classifies user intent (highest_selling, most_profitable, stars, dogs, etc.)
    - Calls appropriate business logic (menu engineering, pricing, design)
    - Returns conversational responses with insights and suggestions

    Args:
        prompt: User's natural language question

    Returns:
        Conversational response string, or None if not a conversational AI query
    """
    try:
        from apps.agent_core.task_registry import task_registry

        # Try Conversational AI endpoint
        result, status_code = task_registry.execute_task(
            service="conversational",
            subtask="ai",
            params={"query": prompt, "session_id": "chat_assistant"},
            file_bytes=None
        )

        if status_code == 200 and result.get("status") == "success":
            data = result.get("data", {})

            # Check for business_report_html first (from menu_questions)
            # It might be in data directly or in raw_data
            business_report_html = data.get("business_report_html") or data.get("raw_data", {}).get("business_report_html")
            if business_report_html:
                return business_report_html

            answer = data.get("answer", "")

            # Check if this was a "help" response (means query wasn't recognized)
            # If so, return None to fall through to GPT-4
            if answer.startswith("**What I Can Help You With:**") or answer.startswith("I'm not sure I understood that"):
                return None  # Fall through to GPT-4 for general questions

            # Format the conversational response
            insights = data.get("insights", [])
            suggestions = data.get("suggestions", [])

            # Build response with insights and suggestions
            response_parts = [answer]

            if insights:
                response_parts.append("\n**💡 Insights:**")
                for insight in insights:
                    response_parts.append(f"• {insight}")

            if suggestions:
                response_parts.append("\n**💬 You can also ask:**")
                for suggestion in suggestions[:3]:  # Limit to 3 suggestions
                    response_parts.append(f"• {suggestion}")

            return "\n".join(response_parts)

        return None  # Not a conversational AI query

    except Exception as e:
        # If conversational AI fails, return None to fall through to other handlers
        return None


def chat_with_gpt(prompt: str) -> str:
    """Chat with GPT-4 using the OpenAI API, with KPI analysis integration."""
    if not prompt or not prompt.strip():
        return "Error: Please provide a message."

    # STEP 1: Try Conversational AI first (natural language queries about menu/business)
    conversational_response = handle_conversational_ai(prompt)
    if conversational_response:
        return conversational_response

    # STEP 2: Try specific KPI analysis handlers (legacy keyword-based routing)
    kpi_response = handle_kpi_analysis(prompt)
    if kpi_response:
        return kpi_response

    # STEP 3: Fall back to GPT-4 for general hospitality advice
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."

    base_system_message = """You are an expert restaurant business consultant with 20+ years of experience in the hospitality industry. Your role is to provide comprehensive, actionable, and data-driven advice to restaurant owners and managers.

## Your Communication Style:
- Write in a warm, professional, and approachable tone - like a trusted advisor having a conversation
- Break down complex concepts into easy-to-understand explanations
- Use clear headings, bullet points, and numbered lists for readability
- Include specific calculations with step-by-step breakdowns when relevant
- Provide industry benchmarks and context for all metrics
- Always explain the "why" behind recommendations

## Response Structure (use when appropriate):
1. **Understanding the Situation** - Acknowledge what the user is asking and restate key data points
2. **Analysis** - Provide detailed calculations with formulas shown clearly
3. **Key Findings** - Highlight the most important insights from the analysis
4. **Recommendations** - Provide 3-5 specific, prioritized action items
5. **Impact Assessment** - Quantify potential savings/improvements when possible
6. **Next Steps** - Suggest immediate actions they can take

## Industry Expertise Areas:
- **KPI Analysis**: Labor cost %, food cost %, prime cost %, sales per labor hour
- **Menu Engineering**: Stars, Plowhorses, Puzzles, Dogs matrix analysis
- **Recipe Costing**: Ingredient costs, portion control, margin optimization
- **Beverage Management**: Liquor cost control, inventory variance, pricing
- **HR Solutions**: Staff retention, scheduling optimization, performance management
- **Strategic Planning**: Sales forecasting, market analysis, growth strategies

## Formatting Guidelines:
- Use **bold** for important terms and metrics
- Use mathematical notation for formulas: (Value A / Value B) × 100
- Include specific dollar amounts and percentages
- Reference industry standards: "Industry benchmark: 25-30%"
- Use emojis sparingly for visual hierarchy (📊, 💡, ⚠️, ✅, 📈)

## Example Response Pattern:
When analyzing data, always:
1. Show the calculation formula
2. Plug in the actual numbers
3. Show the result
4. Compare to industry benchmarks
5. Explain what this means for their business
6. Provide specific recommendations to improve

Remember: You're not just providing data - you're helping restaurant operators make better business decisions. Be thorough, be specific, and be helpful."""

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": base_system_message},
                {"role": "user", "content": prompt.strip()},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        return response.choices[0].message.content

    except Exception as exc:  # pragma: no cover - network/SDK errors
        return f"Error: Unable to process request. {exc}"
