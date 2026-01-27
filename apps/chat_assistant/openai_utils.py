# chat_assistant/openai_utils.py
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def sanitize_response(text: str) -> str:
    """
    Clean response text by removing markdown, LaTeX, and other formatting artifacts.
    Ensures the output is natural, human-readable text.
    """
    if not text:
        return text
    
    # Remove LaTeX-style commands: \text{...}, \frac{...}, \left, \right, etc.
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'\1 divided by \2', text)
    text = re.sub(r'\\left[(\[\{]', '', text)
    text = re.sub(r'\\right[)\]\}]', '', text)
    text = re.sub(r'\\times', 'times', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # Remove any remaining backslash commands
    
    # Remove markdown bold: **text** -> text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    
    # Remove markdown italic: *text* or _text_ -> text
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_([^_]+)_(?!_)', r'\1', text)
    
    # Remove markdown headers: ## Header -> Header
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    
    # Remove markdown code blocks and inline code
    text = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Replace bullet point symbols with dashes
    text = re.sub(r'^[•◦▪]\s*', '- ', text, flags=re.MULTILINE)
    
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Clean up extra spaces
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def extract_kpi_data(prompt: str) -> dict:
    """Extract KPI data from user prompt using regex patterns."""
    import urllib.parse
    import logging
    
    logger = logging.getLogger(__name__)

    data = {}
    # Decode URL encoding if present
    decoded_prompt = urllib.parse.unquote(prompt)
    
    logger.debug(f"Extracting KPI data from: {decoded_prompt}")

    # Find all dollar amounts first (e.g., $50,000 or $14,000)
    dollar_matches = re.findall(r'\$([0-9,]+(?:\.[0-9]+)?)', decoded_prompt)
    dollar_values = []
    for val in dollar_matches:
        try:
            dollar_values.append(float(val.replace(',', '')))
        except ValueError:
            continue
    
    logger.debug(f"Dollar values found: {dollar_values}")

    # Find all numbers (including those with commas, but not already captured as dollars)
    number_matches = re.findall(r'(?<!\$)([0-9,]+(?:\.[0-9]+)?)', decoded_prompt)
    number_values = []
    for val in number_matches:
        if val and val.strip() and val not in [m.replace(',', '') for m in dollar_matches]:
            try:
                num = float(val.replace(',', ''))
                # Filter out very small numbers that are likely not KPI data (like single digits in text)
                if num >= 1:
                    number_values.append(num)
            except ValueError:
                continue

    # Combine dollar values with other numbers, prioritizing dollar values
    all_values = dollar_values + number_values
    
    logger.debug(f"All values found: {all_values}")

    # Simple keyword-based extraction
    prompt_lower = decoded_prompt.lower()

    # Extract total sales - look for explicit patterns first
    # Pattern handles: "total sales are $50,000" or "sales: 50000" or "my sales are $50,000"
    sales_match = re.search(r'(?:total\s+)?sales\s+(?:are|is|of|:)?\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if sales_match:
        data['total_sales'] = float(sales_match.group(1).replace(',', ''))
        logger.debug(f"Sales extracted via regex: {data['total_sales']}")
    elif any(word in prompt_lower for word in ['sales', 'revenue', 'total']) and all_values:
        # Fall back to first dollar value if "sales" mentioned
        data['total_sales'] = all_values[0]
        logger.debug(f"Sales extracted via fallback: {data['total_sales']}")

    # Extract food cost - look for explicit patterns with $ sign support
    # Pattern handles: "food cost is $14,000" or "food cost: 14000"
    food_match = re.search(r'food\s+cost\s+(?:is|are|of|:)?\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if food_match:
        data['food_cost'] = float(food_match.group(1).replace(',', ''))
        logger.debug(f"Food cost extracted via regex: {data['food_cost']}")
    elif 'food cost' in prompt_lower and len(all_values) > 1:
        # Food cost is likely the second dollar value when mentioned
        data['food_cost'] = all_values[1]
        logger.debug(f"Food cost extracted via fallback (second value): {data['food_cost']}")
    elif 'food' in prompt_lower and 'cost' in prompt_lower and len(all_values) > 1:
        data['food_cost'] = all_values[1]
        logger.debug(f"Food cost extracted via keyword fallback: {data['food_cost']}")
    # Also try to match just "food" followed by a dollar amount if not already found
    elif 'food_cost' not in data and 'food' in prompt_lower:
        food_alt_match = re.search(r'food[^0-9]*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
        if food_alt_match:
            data['food_cost'] = float(food_alt_match.group(1).replace(',', ''))
            logger.debug(f"Food cost extracted via alt pattern: {data['food_cost']}")
    
    logger.debug(f"Final extracted data: {data}")

    # Extract labor cost - look for explicit patterns with $ sign support
    labor_match = re.search(r'labor\s+cost\s+(?:is|are|of|:)?\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if labor_match:
        data['labor_cost'] = float(labor_match.group(1).replace(',', ''))
    elif 'labor cost' in prompt_lower and len(all_values) > 1:
        data['labor_cost'] = all_values[1] if 'food_cost' not in data else (all_values[2] if len(all_values) > 2 else all_values[1])
    elif 'labor' in prompt_lower and len(all_values) > 1:
        data['labor_cost'] = all_values[1] if 'food_cost' not in data else (all_values[2] if len(all_values) > 2 else None)

    # Extract hours worked - look for "hours worked: NUMBER" or "NUMBER hours"
    # First try "hours worked: NUMBER" pattern (more specific)
    hours_match = re.search(r'hours\s+worked[:\s]+(\d+(?:,\d+)?)', prompt_lower)
    if hours_match:
        data['hours_worked'] = float(hours_match.group(1).replace(',', ''))
    else:
        # Try "NUMBER hours" pattern (but not "overtime hours")
        hours_match2 = re.search(r'(?<!overtime\s)(\d+(?:,\d+)?)\s*hours?(?!\s*:)', prompt_lower)
        if hours_match2:
            data['hours_worked'] = float(hours_match2.group(1).replace(',', ''))
        else:
            # Try "hours: NUMBER" pattern
            hours_match3 = re.search(r'(?<!overtime\s)hours?[:\s]+(\d+(?:,\d+)?)', prompt_lower)
            if hours_match3:
                data['hours_worked'] = float(hours_match3.group(1).replace(',', ''))
            elif any(word in prompt_lower for word in ['hours', 'hour']):
                # Find the largest number that could be hours (fallback)
                for num in sorted(number_values, reverse=True):
                    if num > 0 and num < 1000:  # Reasonable range for hours
                        data['hours_worked'] = num
                        break

    # =====================================================
    # OPTIONAL KPI PARAMETERS - Labor Cost Analysis
    # =====================================================
    
    # Extract overtime hours - patterns: "overtime hours: 40", "40 overtime hours", "overtime: 40"
    # First try "overtime hours: NUMBER" pattern (most specific for new format)
    overtime_match = re.search(r'overtime\s+hours?[:\s]+(\d+(?:,\d+)?)', prompt_lower)
    if overtime_match:
        data['overtime_hours'] = float(overtime_match.group(1).replace(',', ''))
    else:
        # Try "NUMBER overtime hours" pattern
        overtime_match2 = re.search(r'(\d+(?:,\d+)?)\s*overtime\s*hours?', prompt_lower)
        if overtime_match2:
            data['overtime_hours'] = float(overtime_match2.group(1).replace(',', ''))
        else:
            # Try "overtime: NUMBER" pattern
            overtime_match3 = re.search(r'overtime[:\s]+(\d+(?:,\d+)?)', prompt_lower)
            if overtime_match3:
                data['overtime_hours'] = float(overtime_match3.group(1).replace(',', ''))
            else:
                # Try "includes NUMBER overtime" pattern
                overtime_match4 = re.search(r'includes?\s+(\d+(?:,\d+)?)\s*(?:overtime|ot)', prompt_lower)
                if overtime_match4:
                    data['overtime_hours'] = float(overtime_match4.group(1).replace(',', ''))
    
    # Extract covers (guests served) - patterns: "covers served: 2,000", "2,000 covers", "served 2000 guests"
    # First try "covers served: NUMBER" pattern (most specific for new format)
    covers_match = re.search(r'covers?\s+served[:\s]+(\d+(?:,\d+)?)', prompt_lower)
    if covers_match:
        data['covers'] = int(float(covers_match.group(1).replace(',', '')))
    else:
        # Try "NUMBER covers" pattern
        covers_match2 = re.search(r'(\d+(?:,\d+)?)\s*covers?', prompt_lower)
        if covers_match2:
            data['covers'] = int(float(covers_match2.group(1).replace(',', '')))
        else:
            # Try "served NUMBER guests/customers/covers" pattern
            covers_match3 = re.search(r'served\s+(\d+(?:,\d+)?)\s*(?:guests?|customers?|covers?)?', prompt_lower)
            if covers_match3:
                data['covers'] = int(float(covers_match3.group(1).replace(',', '')))
            else:
                # Try "guests/customers: NUMBER" pattern
                covers_match4 = re.search(r'(?:guests?|customers?)[:\s]+(\d+(?:,\d+)?)', prompt_lower)
                if covers_match4:
                    data['covers'] = int(float(covers_match4.group(1).replace(',', '')))
    
    # =====================================================
    # OPTIONAL KPI PARAMETERS - Food Cost Analysis
    # =====================================================
    
    # Extract waste cost - patterns: "waste cost: $800", "waste cost is $800", "waste: $800"
    waste_cost_match = re.search(r'waste\s+cost[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if waste_cost_match:
        data['waste_cost'] = float(waste_cost_match.group(1).replace(',', ''))
    else:
        waste_match2 = re.search(r'waste\s+cost\s+(?:is|are|of)\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
        if waste_match2:
            data['waste_cost'] = float(waste_match2.group(1).replace(',', ''))
        else:
            waste_match3 = re.search(r'waste[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
            if waste_match3:
                data['waste_cost'] = float(waste_match3.group(1).replace(',', ''))
    
    # Extract beginning inventory - patterns: "beginning inventory: $5,000", "beginning inventory was $5,000"
    begin_inv_match = re.search(r'(?:beginning|starting|start)\s+inventory[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if begin_inv_match:
        data['beginning_inventory'] = float(begin_inv_match.group(1).replace(',', ''))
    else:
        begin_inv_match2 = re.search(r'(?:beginning|starting|start)\s+inventory\s+(?:is|was|of)\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
        if begin_inv_match2:
            data['beginning_inventory'] = float(begin_inv_match2.group(1).replace(',', ''))
    
    # Extract ending inventory - patterns: "ending inventory: $4,500", "ending inventory is $4,500"
    end_inv_match = re.search(r'(?:ending|end|final)\s+inventory[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if end_inv_match:
        data['ending_inventory'] = float(end_inv_match.group(1).replace(',', ''))
    else:
        end_inv_match2 = re.search(r'(?:ending|end|final)\s+inventory\s+(?:is|was|of)\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
        if end_inv_match2:
            data['ending_inventory'] = float(end_inv_match2.group(1).replace(',', ''))
    
    # =====================================================
    # OPTIONAL KPI PARAMETERS - Sales Performance Analysis
    # =====================================================
    
    # Extract previous sales - patterns: "previous sales: $48,000", "previous sales were $48,000"
    prev_sales_match = re.search(r'previous\s+(?:period\s+)?sales[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if prev_sales_match:
        data['previous_sales'] = float(prev_sales_match.group(1).replace(',', ''))
    else:
        prev_match2 = re.search(r'previous\s+(?:period\s+)?sales\s+(?:were|was|is|of)\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
        if prev_match2:
            data['previous_sales'] = float(prev_match2.group(1).replace(',', ''))
        else:
            prev_match3 = re.search(r'last\s+(?:period|month|week)\s+(?:sales\s+)?(?:were|was|is|of|:)?\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
            if prev_match3:
                data['previous_sales'] = float(prev_match3.group(1).replace(',', ''))
    
    # Extract average check - patterns: "average check: $25", "average check of $25", "avg check: 25"
    avg_check_match = re.search(r'(?:average|avg)\s+check[:\s]+\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
    if avg_check_match:
        data['avg_check'] = float(avg_check_match.group(1).replace(',', ''))
    else:
        avg_check_match2 = re.search(r'(?:average|avg)\s+check\s+(?:is|of)\s*\$?([0-9,]+(?:\.[0-9]+)?)', prompt_lower)
        if avg_check_match2:
            data['avg_check'] = float(avg_check_match2.group(1).replace(',', ''))

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

    efficiency_score_match2 = re.search(r'efficiency\s+score[:\s]*([0-9,]+)', prompt_lower)
    if efficiency_score_match2:
        data['efficiency_score'] = float(efficiency_score_match2.group(1).replace(',', ''))
    return data


def handle_kpi_analysis(prompt: str) -> str:
    """Handle KPI analysis requests by calling our specialized functions."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Import here to avoid circular imports
        from backend.consulting_services.kpi.kpi_utils import (
            calculate_labor_cost_analysis,
            calculate_prime_cost_analysis,
            calculate_sales_performance_analysis,
            calculate_kpi_summary,
            calculate_food_cost_analysis
        )
        from backend.consulting_services.inventory.tracking import calculate_inventory_variance

        data = extract_kpi_data(prompt)
        
        logger.info(f"KPI Analysis - Extracted data: {data}")
        logger.info(f"KPI Analysis - Original prompt: {prompt}")

        # Determine which analysis to run based on keywords
        prompt_lower = prompt.lower()

        # Import here to avoid circular imports
        from apps.agent_core.task_registry import task_registry
        
        # =====================================================
        # IMPORTANT: Check for ANALYSIS REQUEST keywords first
        # Use regex patterns that look for "analyze X" or "X analysis"
        # This prevents data mentions like "food cost: $14,000" from 
        # triggering the wrong analysis type
        # =====================================================
        
        # Helper function to detect analysis request type
        def is_requesting_analysis(analysis_type):
            """Check if user is requesting a specific analysis type (not just mentioning data)"""
            patterns = [
                rf'analyze\s+(?:my\s+)?{analysis_type}',
                rf'{analysis_type}\s+analysis',
                rf'calculate\s+(?:my\s+)?{analysis_type}',
                rf'check\s+(?:my\s+)?{analysis_type}',
                rf'show\s+(?:me\s+)?(?:my\s+)?{analysis_type}',
                rf'what\s+is\s+(?:my\s+)?{analysis_type}',
                rf'get\s+(?:my\s+)?{analysis_type}',
            ]
            return any(re.search(pattern, prompt_lower) for pattern in patterns)

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

        # =====================================================
        # CORE KPI ANALYSIS - Use is_requesting_analysis() to detect intent
        # Order matters: more specific analyses first
        # =====================================================
        
        # PRIME COST ANALYSIS - Check first (contains both labor and food, so must come before individual checks)
        elif is_requesting_analysis('prime cost') or is_requesting_analysis('prime') or 'prime cost' in prompt_lower.split('analyze')[-1] if 'analyze' in prompt_lower else False:
            logger.info(f"Prime cost analysis requested")
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
            else:
                return """To analyze your prime cost, I need your actual data. Please provide:

**Required:**
1. Total Sales (e.g., $50,000)
2. Labor Cost (e.g., $15,000)  
3. Food Cost (e.g., $14,000)

**Optional:**
- Covers served (e.g., 2,000)

Example: "Analyze my prime cost. Total sales: $50,000. Labor cost: $15,000. Food cost: $14,000. Covers served: 2,000."

Or upload a CSV file with columns: date, sales, labor_cost, food_cost"""

        # SALES PERFORMANCE ANALYSIS - Check second (requires all 4 core metrics)
        elif is_requesting_analysis('sales performance') or is_requesting_analysis('sales') or is_requesting_analysis('revenue') or is_requesting_analysis('growth'):
            logger.info(f"Sales performance analysis requested")
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
            else:
                return """To analyze your sales performance, I need your actual data. Please provide:

**Required:**
1. Total Sales (e.g., $50,000)
2. Labor Cost (e.g., $15,000)
3. Food Cost (e.g., $14,000)
4. Hours Worked (e.g., 800 hours)

**Optional:**
- Previous Sales (e.g., $48,000)
- Covers served (e.g., 2,000)
- Average Check (e.g., $25)

Example: "Analyze my sales performance. Total sales: $50,000. Labor cost: $15,000. Food cost: $14,000. Hours worked: 800. Previous sales: $48,000. Covers served: 2,000. Average check: $25."

Or upload a CSV file with columns: date, sales, labor_cost, food_cost, labor_hours"""

        # LABOR COST ANALYSIS - Check for explicit labor cost request
        elif is_requesting_analysis('labor cost') or is_requesting_analysis('labor'):
            logger.info(f"Labor cost analysis requested")
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
            else:
                return """To analyze your labor cost, I need your actual data. Please provide:

**Required:**
1. Total Sales (e.g., $50,000)
2. Labor Cost (e.g., $15,000)
3. Hours Worked (e.g., 800 hours)

**Optional:**
- Overtime Hours (e.g., 40)
- Covers served (e.g., 2,000)

Example: "Analyze my labor cost. Total sales: $50,000. Labor cost: $15,000. Hours worked: 800. Overtime hours: 40. Covers served: 2,000."

Or upload a CSV file with columns: date, sales, labor_cost, labor_hours"""

        # FOOD COST ANALYSIS - Check for explicit food cost request
        elif is_requesting_analysis('food cost') or is_requesting_analysis('food') or is_requesting_analysis('cogs'):
            logger.info(f"Food cost analysis requested")
            if 'total_sales' in data and 'food_cost' in data:
                result, status = task_registry.execute_task(
                    service="kpi",
                    subtask="food_cost",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"
            else:
                return """To analyze your food cost, I need your actual data. Please provide:

**Required:**
1. Total Sales (e.g., $50,000)
2. Food Cost (e.g., $14,000)

**Optional:**
- Waste Cost (e.g., $800)
- Covers served (e.g., 2,000)
- Beginning Inventory (e.g., $5,000)
- Ending Inventory (e.g., $4,500)

Example: "Analyze my food cost. Total sales: $50,000. Food cost: $14,000. Waste cost: $800. Covers served: 2,000. Beginning inventory: $5,000. Ending inventory: $4,500."

Or upload a CSV file with columns: date, sales, food_cost"""

        # Check for simple labor cost calculation with hourly rate - use task registry for proper HTML output
        elif any(keyword in prompt_lower for keyword in ['labor hours', 'hourly rate']):
            if 'total_sales' in data and 'hours_worked' in data:
                # Extract hourly rate from prompt or use default
                hourly_rate_match = re.search(r'(?:hourly\s+rate|rate)[:\s]*\$?([0-9.]+)', prompt, re.IGNORECASE)
                hourly_rate = float(hourly_rate_match.group(1)) if hourly_rate_match else 15.0
                
                # Calculate labor cost from hourly rate if not provided
                if 'labor_cost' not in data:
                    data['labor_cost'] = data['hours_worked'] * hourly_rate
                
                # Use task registry for HTML output
                result, status = task_registry.execute_task(
                    service="kpi",
                    subtask="labor_cost",
                    params=data
                )
                if result.get('status') == 'success':
                    return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
                else:
                    return f"Error: {result.get('error', 'Analysis failed')}"

        # Check for KPI summary - use sales_performance task for proper HTML output
        elif 'total_sales' in data and 'labor_cost' in data and 'food_cost' in data and 'hours_worked' in data:
            result, status = task_registry.execute_task(
                service="kpi",
                subtask="sales_performance",
                params=data
            )
            if result.get('status') == 'success':
                return result.get('data', {}).get('business_report_html', result.get('data', {}).get('business_report', 'Analysis completed but no report generated.'))
            else:
                return f"Error: {result.get('error', 'Analysis failed')}"


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
                    # Use HTML version if available, fall back to text
                    return result.get('business_report_html', result.get('business_report', 'Analysis completed but no report generated.'))
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
            if answer.startswith("What I Can Help You With:") or answer.startswith("I'm not sure I understood that"):
                return None  # Fall through to GPT-4 for general questions

            # Format the conversational response
            insights = data.get("insights", [])
            suggestions = data.get("suggestions", [])

            # Build response with insights and suggestions
            response_parts = [answer]

            if insights:
                response_parts.append("\nInsights:")
                for insight in insights:
                    response_parts.append(f"- {insight}")

            if suggestions:
                response_parts.append("\nYou can also ask:")
                for suggestion in suggestions[:3]:  # Limit to 3 suggestions
                    response_parts.append(f"- {suggestion}")

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
        return sanitize_response(conversational_response)

    # STEP 2: Try specific KPI analysis handlers (legacy keyword-based routing)
    kpi_response = handle_kpi_analysis(prompt)
    if kpi_response:
        return sanitize_response(kpi_response)

    # STEP 3: Fall back to GPT-4 for general hospitality advice
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."

    base_system_message = """You are an expert restaurant business consultant with 20+ years of experience in the hospitality industry. Your role is to provide comprehensive, actionable, and data-driven advice to restaurant owners and managers.

CRITICAL FORMATTING RULES - YOU MUST FOLLOW THESE:
1. NEVER use markdown formatting like asterisks, bold, or headers (no **, no ##, no ###)
2. NEVER use LaTeX or mathematical notation (no \\text{}, no \\frac{}, no \\left, no \\right, no backslash commands)
3. NEVER use code blocks or backticks
4. Write in plain, natural English like a human conversation
5. For formulas, write them in simple words: "Food Cost Percentage equals Cost of Goods Sold divided by Total Sales, multiplied by 100"
6. Use natural paragraph structure, not rigid formatting

Your Communication Style:
- Write like you're having a friendly conversation with a restaurant owner
- Use natural paragraphs and sentences
- When listing items, use simple numbered lists (1. 2. 3.) or dashes (-)
- Explain calculations in plain English with the actual numbers
- Be warm, professional, and approachable

When Analyzing Data:
- Acknowledge what the user is asking
- Explain calculations in conversational language with actual numbers
- Compare results to industry standards (mention the benchmark ranges naturally)
- Provide 3-5 specific action items the owner can take
- Quantify potential savings when possible
- Suggest what they could do next

Your Expertise Areas:
- KPI Analysis: labor costs, food costs, prime costs, sales per labor hour
- Menu Engineering: identifying best sellers, profit drivers, and underperformers  
- Recipe Costing: ingredient costs, portion control, margin optimization
- Beverage Management: liquor cost control, inventory management, pricing
- HR Solutions: staff retention, scheduling, performance management
- Strategic Planning: sales forecasting, market analysis, growth strategies

Industry Benchmarks to Reference (mention these naturally in conversation):
- Food Cost: 28-32% of sales
- Labor Cost: 25-30% of sales
- Prime Cost: 55-65% of sales
- Beverage Cost: 18-24% of sales
- Sales Per Labor Hour: $35-50 or higher

Remember: Write naturally like a trusted advisor having a conversation. No special formatting, no technical markup, just clear and helpful guidance."""

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
        return sanitize_response(response.choices[0].message.content)

    except Exception as exc:  # pragma: no cover - network/SDK errors
        return f"Error: Unable to process request. {exc}"
