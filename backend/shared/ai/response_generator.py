"""
Response Generation Module

Formats API responses into natural, conversational text with insights and suggestions.
"""

from typing import Dict, List, Any, Optional
from backend.consulting_services.kpi.kpi_utils import format_business_report


def generate_response(intent: Dict, api_response: Dict, user_query: str) -> Dict:
    """
    Generate conversational response from API data.

    Args:
        intent: Intent classification result
        api_response: Raw API response
        user_query: Original user question

    Returns:
        Dict with conversational response:
        {
            "answer": str,           # Main conversational answer
            "insights": List[str],   # Key insights (bullet points)
            "suggestions": List[str], # Follow-up suggestions
            "data_summary": Dict,    # Key metrics for display
            "business_report_html": str  # HTML formatted business report (optional)
        }
    """
    intent_name = intent["intent"]
    category = intent["category"]

    # Handle system intents
    if category == "system":
        return _generate_system_response(intent_name)

    # Extract data based on intent
    data = api_response.get("data", {})
    extract_path = intent.get("extract")

    if extract_path:
        # Extract specific data path (e.g., "top_performers.by_units_sold")
        extracted_data = _extract_nested_data(data, extract_path)
    else:
        extracted_data = data

    # Check if API response already has business_report_html (from menu_questions)
    if "business_report_html" in data:
        return {
            "answer": data.get("business_report_html", ""),
            "insights": [],
            "suggestions": [],
            "data_summary": {},
            "business_report_html": data.get("business_report_html", "")
        }

    # Generate response based on intent
    if intent_name in ["highest_selling", "most_profitable"]:
        return _generate_top_items_response(intent_name, extracted_data, data)
    elif intent_name in ["stars", "dogs"]:
        return _generate_quadrant_response(intent_name, extracted_data, data)
    elif intent_name == "menu_analysis":
        return _generate_menu_analysis_response(data)
    elif intent_name in ["underpriced_items", "overpriced_items"]:
        return _generate_pricing_opportunity_response(intent_name, extracted_data, data)
    elif intent_name == "pricing_strategy":
        return _generate_pricing_strategy_response(data)
    elif intent_name == "golden_triangle":
        return _generate_golden_triangle_response(extracted_data, data)
    elif intent_name == "menu_design":
        return _generate_menu_design_response(data)
    else:
        return _generate_generic_response(data)


def _extract_nested_data(data: Dict, path: str) -> Any:
    """Extract nested data using dot notation path."""
    keys = path.split(".")
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, {})
        else:
            return None
    return result


def _generate_top_items_response(intent: str, items: List[Dict], full_data: Dict) -> Dict:
    """Generate response for top selling/profitable items."""
    if not items or len(items) == 0:
        return {
            "answer": "I couldn't find any items matching that criteria.",
            "insights": [],
            "suggestions": ["Try analyzing your full menu with 'show me menu analysis'"],
            "data_summary": {}
        }

    # Take top items (up to 10 for business report)
    top_items = items[:10] if len(items) >= 10 else items

    # Build metrics for business report
    if intent == "highest_selling":
        analysis_type = "Top Selling Items Analysis"
        total_units = sum(item.get("total_units_sold", 0) for item in top_items)
        total_revenue = sum(item.get("total_revenue", 0) for item in top_items)
        
        metrics = {
            "Top Items Count": len(top_items),
            "Total Units Sold": f"{total_units:,}",
            "Total Revenue": f"${total_revenue:,.2f}",
            "Top Seller": top_items[0].get("menu_name", "Unknown") if top_items else "N/A"
        }
        
        # Build recommendations
        recommendations = [
            f"Promote top seller ({top_items[0].get('menu_name', 'Unknown')}) on menu and marketing materials",
            "Consider bundling top sellers with complementary items to increase ticket size",
            "Monitor top sellers for pricing optimization opportunities"
        ]
        
        # Build additional data with item details
        item_details = []
        for i, item in enumerate(top_items, 1):
            item_details.append({
                "Rank": i,
                "Item": item.get("menu_name", "Unknown"),
                "Units Sold": item.get("total_units_sold", 0),
                "Revenue": f"${item.get('total_revenue', 0):,.2f}"
            })
        
        additional_data = {
            "Top Items": item_details
        }
        
        # Determine performance rating
        if total_units > 0:
            performance_rating = "Excellent"
        else:
            performance_rating = "Needs Improvement"
            
    else:  # most_profitable
        analysis_type = "Top Profitable Items Analysis"
        total_profit = sum(item.get("total_profit", 0) for item in top_items)
        avg_margin = sum(item.get("contribution_margin", 0) for item in top_items) / len(top_items) if top_items else 0
        
        metrics = {
            "Top Items Count": len(top_items),
            "Total Profit": f"${total_profit:,.2f}",
            "Average Margin": f"${avg_margin:,.2f}",
            "Top Profitable Item": top_items[0].get("menu_name", "Unknown") if top_items else "N/A"
        }
        
        # Build recommendations
        recommendations = [
            f"Focus marketing efforts on top profitable item ({top_items[0].get('menu_name', 'Unknown')})",
            "Review pricing strategy to maximize profit margins across menu",
            "Consider menu engineering to improve profitability of lower performers"
        ]
        
        # Build additional data with item details
        item_details = []
        for i, item in enumerate(top_items, 1):
            item_details.append({
                "Rank": i,
                "Item": item.get("menu_name", "Unknown"),
                "Profit": f"${item.get('total_profit', 0):,.2f}",
                "Margin": f"${item.get('contribution_margin', 0):,.2f}"
            })
        
        additional_data = {
            "Top Items": item_details
        }
        
        # Determine performance rating
        if total_profit > 0:
            performance_rating = "Excellent"
        else:
            performance_rating = "Needs Improvement"

    # Format as business report
    business_report = format_business_report(
        analysis_type=analysis_type,
        metrics=metrics,
        performance={"rating": performance_rating},
        recommendations=recommendations,
        additional_data=additional_data
    )

    # Generate insights (for backward compatibility)
    insights = format_insights(intent, full_data, top_items)

    # Suggestions
    suggestions = [
        "Show me underpriced items",
        "What are my dog items?",
        "Show me menu design recommendations"
    ]

    # Data summary
    data_summary = {
        "top_item": top_items[0].get("menu_name") if top_items else None,
        "count": len(top_items)
    }

    return {
        "answer": business_report["business_report"],
        "business_report_html": business_report["business_report_html"],
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": data_summary
    }


def _generate_quadrant_response(intent: str, quadrant_data: Dict, full_data: Dict) -> Dict:
    """Generate response for Stars/Dogs quadrant."""
    items = quadrant_data.get("items", [])
    count = quadrant_data.get("count", 0)
    percentage = quadrant_data.get("percentage_of_menu", 0)

    quadrant_name = "Stars" if intent == "stars" else "Dogs"
    emoji = "⭐" if intent == "stars" else "🐕"

    if count == 0:
        return {
            "answer": f"Great news! You have no {quadrant_name} items.",
            "insights": [],
            "suggestions": ["Show me my menu analysis"],
            "data_summary": {}
        }

    # Format answer
    answer = f"You have {count} {quadrant_name} ({percentage:.1f}% of menu):\n\n"
    for i, item in enumerate(items[:5], 1):  # Show max 5
        name = item.get("menu_name", "Unknown")
        revenue = item.get("total_revenue", 0)
        profit = item.get("total_profit", 0)
        answer += f"{i}. {name} - ${revenue:,.0f} revenue, ${profit:,.0f} profit\n"

    if len(items) > 5:
        answer += f"\n...and {len(items) - 5} more"

    # Generate insights
    insights = []
    if intent == "stars":
        insights.append(f"These are your best items - high profit AND high popularity!")
        insights.append("Feature these prominently in your menu's Golden Triangle")
        insights.append("Never remove these items")
        if percentage < 25:
            insights.append(f"Only {percentage:.1f}% of menu are Stars - aim for 25-35%")
    else:  # dogs
        insights.append(f"These items have low profit AND low popularity")
        insights.append("Consider removing or replacing these items")
        insights.append("If keeping them, move to bottom of menu")
        if percentage > 15:
            insights.append(f"{percentage:.1f}% of menu are Dogs - aim for less than 15%")

    # Suggestions
    if intent == "stars":
        suggestions = [
            "Where should I place these on my menu?",
            "Show me pricing opportunities",
            "What items should I remove?"
        ]
    else:
        suggestions = [
            "Show me my star items",
            "What are my highest selling items?",
            "Show me menu design recommendations"
        ]

    return {
        "answer": answer,
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": {"count": count, "percentage": percentage}
    }


def _generate_menu_analysis_response(data: Dict) -> Dict:
    """Generate response for full menu analysis."""
    quadrant_summary = data.get("quadrant_summary", {})
    overall_metrics = data.get("overall_metrics", {})

    stars = quadrant_summary.get("stars", {})
    plowhorses = quadrant_summary.get("plowhorses", {})
    puzzles = quadrant_summary.get("puzzles", {})
    dogs = quadrant_summary.get("dogs", {})

    total_items = data.get("total_items", 0)
    total_revenue = overall_metrics.get("total_revenue", 0)

    # Format answer
    answer = f"Menu Engineering Analysis\n\n"
    answer += f"Analyzing {total_items} items (${total_revenue:,.2f} total revenue):\n\n"
    answer += f"Stars: {stars.get('count', 0)} items ({stars.get('percentage_of_menu', 0):.1f}%) - Keep and promote these!\n"
    answer += f"Plowhorses: {plowhorses.get('count', 0)} items ({plowhorses.get('percentage_of_menu', 0):.1f}%) - Popular but low profit\n"
    answer += f"Puzzles: {puzzles.get('count', 0)} items ({puzzles.get('percentage_of_menu', 0):.1f}%) - Profitable but unpopular\n"
    answer += f"Dogs: {dogs.get('count', 0)} items ({dogs.get('percentage_of_menu', 0):.1f}%) - Remove or improve\n"

    # Generate insights
    insights = []
    star_pct = stars.get('percentage_of_menu', 0)
    dog_pct = dogs.get('percentage_of_menu', 0)

    if star_pct < 25:
        insights.append(f"Only {star_pct:.1f}% Stars - aim for 25-35%")
    elif star_pct >= 30:
        insights.append(f"Great! {star_pct:.1f}% Stars (target: 25-35%)")

    if dog_pct > 15:
        insights.append(f"Too many Dogs ({dog_pct:.1f}%) - aim for less than 15%")
    elif dog_pct < 10:
        insights.append(f"Excellent! Only {dog_pct:.1f}% Dogs")

    # Suggestions
    suggestions = [
        "Show me my star items",
        "What items should I remove?",
        "Show me pricing opportunities"
    ]

    return {
        "answer": answer,
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": {
            "total_items": total_items,
            "stars": stars.get('count', 0),
            "dogs": dogs.get('count', 0)
        }
    }


def _generate_pricing_opportunity_response(intent: str, items: List[Dict], full_data: Dict) -> Dict:
    """Generate response for pricing opportunities."""
    if not items or len(items) == 0:
        return {
            "answer": f"Good news! I didn't find any {intent.replace('_', ' ')}.",
            "insights": ["Your pricing looks good across the board"],
            "suggestions": ["Show me my menu analysis"],
            "data_summary": {}
        }

    pricing_data = full_data.get("pricing_opportunities", {})
    total_opportunity = pricing_data.get("total_revenue_opportunity", 0)

    # Take top 5 items
    top_items = items[:5] if len(items) >= 5 else items

    # Format answer
    if intent == "underpriced_items":
        answer = f"Found {len(items)} underpriced items (${total_opportunity:,.2f} revenue opportunity):\n\n"
        for i, item in enumerate(top_items, 1):
            name = item.get("name", "Unknown")
            current = item.get("current_price", 0)
            suggested = item.get("suggested_price", 0)
            opportunity = item.get("revenue_opportunity", 0)
            answer += f"{i}. {name} - ${current:.2f} to ${suggested:.2f} (+${opportunity:,.0f}/month)\n"
    else:  # overpriced_items
        answer = f"Found {len(items)} potentially overpriced items:\n\n"
        for i, item in enumerate(top_items, 1):
            name = item.get("name", "Unknown")
            current = item.get("current_price", 0)
            suggested = item.get("suggested_price", 0)
            answer += f"{i}. {name} - ${current:.2f} to ${suggested:.2f}\n"

    if len(items) > 5:
        answer += f"\n...and {len(items) - 5} more"

    # Generate insights
    insights = []
    if intent == "underpriced_items":
        insights.append(f"Raising these prices could add ${total_opportunity:,.0f}/month revenue")
        insights.append("Start with your Star items for lowest risk")
        insights.append("Use psychological pricing (.99, .95, or round dollars)")
    else:
        insights.append("Lowering prices on these items may increase volume")
        insights.append("Test price changes on one item at a time")

    # Suggestions
    suggestions = [
        "Show me my star items",
        "What's my menu analysis?",
        "Show me menu design recommendations"
    ]

    return {
        "answer": answer,
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": {
            "count": len(items),
            "opportunity": total_opportunity if intent == "underpriced_items" else 0
        }
    }


def _generate_pricing_strategy_response(data: Dict) -> Dict:
    """Generate response for full pricing strategy."""
    pricing_opps = data.get("pricing_opportunities", {})
    underpriced_count = len(pricing_opps.get("underpriced_items", []))
    overpriced_count = len(pricing_opps.get("overpriced_items", []))
    total_opportunity = pricing_opps.get("total_revenue_opportunity", 0)

    answer = f"Pricing Strategy Analysis\n\n"
    answer += f"Underpriced: {underpriced_count} items (+${total_opportunity:,.0f} opportunity)\n"
    answer += f"Overpriced: {overpriced_count} items\n\n"
    answer += "Use psychological pricing rules:\n"
    answer += "- Under $10: use .99 endings\n"
    answer += "- $10-20: use .95 endings\n"
    answer += "- Over $20: use round dollars\n"

    insights = [
        f"Total revenue opportunity: ${total_opportunity:,.0f}/month",
        "Focus on underpriced Star items first",
        "Test price changes one at a time"
    ]

    suggestions = [
        "Show me underpriced items",
        "What are my star items?",
        "Show me menu design recommendations"
    ]

    return {
        "answer": answer,
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": {
            "underpriced_count": underpriced_count,
            "opportunity": total_opportunity
        }
    }


def _generate_golden_triangle_response(triangle_data: Dict, full_data: Dict) -> Dict:
    """Generate response for Golden Triangle placement."""
    # triangle_data is the full data dict, extract golden_triangle (which is a list)
    positions = triangle_data.get("golden_triangle", [])

    answer = "Golden Triangle Placement (Where customers look first):\n\n"
    for pos in positions[:3]:  # Top 3 positions
        position = pos.get("position", "")
        item_name = pos.get("menu_item", "Unknown")  # Field is "menu_item" not "item_name"
        reason = pos.get("reason", "")
        answer += f"{position}: {item_name}\n   {reason}\n\n"

    insights = [
        "Top-right corner gets most attention (70% of diners look here first)",
        "Place your Star items in these prime positions",
        "Avoid putting Dog items in the Golden Triangle"
    ]

    suggestions = [
        "Show me my star items",
        "Show me full menu design recommendations",
        "What items should I remove?"
    ]

    return {
        "answer": answer,
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": {}
    }


def _generate_menu_design_response(data: Dict) -> Dict:
    """Generate response for full menu design recommendations."""
    golden_triangle = data.get("golden_triangle", [])  # It's a list, not a dict
    visual_hierarchy = data.get("visual_hierarchy", {})
    implementation_guide = data.get("implementation_guide", {})

    answer = "Menu Design Recommendations\n\n"
    answer += "Phase 1: Golden Triangle\n"
    positions = golden_triangle  # Already a list
    for pos in positions[:3]:
        answer += f"- {pos.get('position')}: {pos.get('menu_item')}\n"  # Field is "menu_item"

    answer += "\nVisual Hierarchy:\n"
    for quadrant in ["stars", "plowhorses", "puzzles", "dogs"]:
        quad_data = visual_hierarchy.get(quadrant, {})
        if quad_data:
            answer += f"- {quadrant.title()}: {quad_data.get('font_size')} - {quad_data.get('emphasis')}\n"

    insights = [
        "Implement Golden Triangle first - easiest & biggest impact",
        "Use larger fonts (18-20pt) for Stars",
        "Place Dogs at bottom or remove entirely"
    ]

    suggestions = [
        "Show me my star items",
        "What items should I remove?",
        "Show me pricing opportunities"
    ]

    return {
        "answer": answer,
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": {}
    }


def _generate_system_response(intent: str) -> Dict:
    """Generate system responses (help, etc.)."""
    if intent == "help":
        answer = "What I Can Help You With:\n\n"
        answer += "Menu Analysis:\n"
        answer += "- What are my highest selling items?\n"
        answer += "- Show me my most profitable items\n"
        answer += "- What are my star items?\n"
        answer += "- Which items should I remove?\n\n"
        answer += "Pricing:\n"
        answer += "- Are any items underpriced?\n"
        answer += "- Show me pricing opportunities\n\n"
        answer += "Menu Design:\n"
        answer += "- Where should I place items?\n"
        answer += "- Show me menu design recommendations\n"

        return {
            "answer": answer,
            "insights": [],
            "suggestions": [],
            "data_summary": {}
        }

    return {
        "answer": "I'm not sure how to help with that. Type 'help' to see what I can do.",
        "insights": [],
        "suggestions": ["help"],
        "data_summary": {}
    }


def _generate_generic_response(data: Dict) -> Dict:
    """Fallback for unhandled response types."""
    return {
        "answer": "Here's what I found:\n\n" + str(data)[:500],
        "insights": [],
        "suggestions": ["Show me my menu analysis"],
        "data_summary": {}
    }


def format_insights(intent: str, full_data: Dict, items: List[Dict]) -> List[str]:
    """
    Generate contextual insights based on intent and data.

    Args:
        intent: Intent name
        full_data: Full API response data
        items: Specific items being discussed

    Returns:
        List of insight strings
    """
    insights = []

    # Check if top items are Stars
    if items and len(items) > 0:
        top_item = items[0]
        classification = top_item.get("classification", "")

        if classification == "star":
            insights.append("These are Star items - high popularity AND profitability!")
        elif classification == "plowhorse":
            insights.append("These are Plowhorses - popular but could be more profitable")
        elif classification == "puzzle":
            insights.append("These are Puzzles - profitable but need better marketing")
        elif classification == "dog":
            insights.append("These are Dogs - consider removing or improving")

    return insights
