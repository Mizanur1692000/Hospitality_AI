"""
Response Templates and Prompts

Contains templates, patterns, and constants for generating conversational responses.
"""

# Greeting messages
GREETINGS = [
    "Hi! I'm your hospitality AI assistant. What would you like to know about your restaurant?",
    "Hello! I can help with menu analysis, pricing, design, and more. What can I analyze for you?",
    "Welcome! Ask me anything about your menu, sales, or operations.",
]

# Error messages
ERROR_MESSAGES = {
    "no_data": "I couldn't find any data for that query. Please make sure your data files are up to date.",
    "api_error": "I encountered an error while analyzing your data. Please try again.",
    "invalid_query": "I'm not sure I understood that. Try asking 'What are my highest selling items?' or type 'help' for examples.",
    "no_results": "I didn't find any results for that query.",
}

# Success confirmations
CONFIRMATIONS = [
    "Got it! Let me analyze that for you...",
    "Sure thing! Analyzing your data...",
    "On it! Pulling that information...",
]

# Insight prefixes (for variety)
INSIGHT_PREFIXES = [
    "Key insight:",
    "Important:",
    "Note:",
    "Fun fact:",
    "Quick tip:",
]

# Action recommendations
ACTION_TEMPLATES = {
    "raise_price": "Consider raising the price on {item_name} from ${current_price:.2f} to ${suggested_price:.2f}",
    "lower_price": "Try lowering the price on {item_name} to increase volume",
    "remove_item": "Consider removing {item_name} - it's underperforming",
    "promote_item": "Feature {item_name} more prominently - it's a top performer",
    "improve_description": "Add an enticing description to {item_name} to boost orders",
    "reposition": "Move {item_name} to {position} on your menu",
}

# Performance ratings and colors
PERFORMANCE_RATINGS = {
    "excellent": {"emoji": "", "color": "#10b981", "message": "Excellent performance!"},
    "good": {"emoji": "", "color": "#3b82f6", "message": "Good performance"},
    "acceptable": {"emoji": "", "color": "#f59e0b", "message": "Acceptable, room for improvement"},
    "needs_improvement": {"emoji": "", "color": "#ef4444", "message": "Needs improvement"},
}

# Quadrant descriptions
QUADRANT_INFO = {
    "stars": {
        "emoji": "",
        "name": "Stars",
        "description": "High profit + High popularity",
        "action": "Keep and promote these items!",
        "placement": "Top-right of menu (Golden Triangle)",
        "font_size": "18-20pt, bold",
    },
    "plowhorses": {
        "emoji": "",
        "name": "Plowhorses",
        "description": "Low profit + High popularity",
        "action": "Raise prices or reduce costs",
        "placement": "Middle sections",
        "font_size": "14pt, standard",
    },
    "puzzles": {
        "emoji": "",
        "name": "Puzzles",
        "description": "High profit + Low popularity",
        "action": "Improve marketing and descriptions",
        "placement": "Near top of sections",
        "font_size": "16pt, appetizing descriptions",
    },
    "dogs": {
        "emoji": "",
        "name": "Dogs",
        "description": "Low profit + Low popularity",
        "action": "Remove or replace ASAP",
        "placement": "Bottom or off menu entirely",
        "font_size": "12pt (if you must keep)",
    },
}

# Industry benchmarks (for reference in responses)
BENCHMARKS = {
    "food_cost": {
        "excellent": 28,
        "good": 32,
        "acceptable": 35,
        "poor": 40,
    },
    "stars_percentage": {
        "excellent": 30,
        "good": 25,
        "acceptable": 20,
        "poor": 15,
    },
    "dogs_percentage": {
        "excellent": 10,
        "good": 15,
        "acceptable": 20,
        "poor": 25,
    },
}

# Response templates for different intents
RESPONSE_TEMPLATES = {
    "top_items": """
Your top {count} {type} are:

{items_list}

{insights}

{suggestions}
    """,

    "quadrant_summary": """
You have {count} {quadrant_name} ({percentage:.1f}% of menu):

{items_list}

{action_advice}

{insights}
    """,

    "pricing_opportunity": """
Found {count} {opportunity_type} (${total_opportunity:,.0f} revenue opportunity):

{items_list}

{insights}

{suggestions}
    """,

    "menu_analysis": """
Menu Engineering Analysis

Analyzing {total_items} items (${total_revenue:,.2f} total revenue):

Stars: {stars_count} items ({stars_pct:.1f}%)
Plowhorses: {plowhorses_count} items ({plowhorses_pct:.1f}%)
Puzzles: {puzzles_count} items ({puzzles_pct:.1f}%)
Dogs: {dogs_count} items ({dogs_pct:.1f}%)

{performance_assessment}

{insights}
    """,
}

# Follow-up suggestion templates
SUGGESTION_TEMPLATES = {
    "after_menu_analysis": [
        "Show me my star items",
        "What items should I remove?",
        "Are any items underpriced?",
    ],
    "after_pricing": [
        "Show me my highest selling items",
        "What's my menu analysis?",
        "Show me menu design recommendations",
    ],
    "after_design": [
        "Show me my most profitable items",
        "What are my star items?",
        "Are any items underpriced?",
    ],
}

# Help text
HELP_TEXT = """
What I Can Help You With:

Menu Analysis:
- What are my highest selling items?
- Show me my most profitable items
- What are my star items?
- Which items should I remove?
- Show me my menu analysis

Pricing Strategy:
- Are any items underpriced?
- Show me overpriced items
- What's my pricing strategy?
- Show me pricing opportunities

Menu Design:
- Where should I place items on my menu?
- Show me menu design recommendations
- What is the golden triangle?

Pro Tips:
- You can filter by category: "Show me underpriced appetizers"
- Ask follow-up questions for deeper insights
- Type 'help' anytime to see this message

Example Questions:
- "What were my highest selling items?"
- "Are any of my star items underpriced?"
- "Where should I place my most profitable items?"
"""

# Formatting helpers
def format_currency(amount: float) -> str:
    """Format number as currency."""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format number as percentage."""
    return f"{value:.1f}%"

def format_item_list(items: list, include_metrics: bool = True) -> str:
    """
    Format list of items for display.

    Args:
        items: List of item dictionaries
        include_metrics: Whether to include revenue/profit metrics

    Returns:
        Formatted string
    """
    if not items:
        return "No items found."

    output = []
    for i, item in enumerate(items[:5], 1):  # Max 5 items
        name = item.get("name", "Unknown")
        if include_metrics:
            revenue = item.get("revenue", 0)
            profit = item.get("total_profit", 0)
            output.append(f"{i}. {name} - {format_currency(revenue)} revenue, {format_currency(profit)} profit")
        else:
            output.append(f"{i}. {name}")

    if len(items) > 5:
        output.append(f"\n...and {len(items) - 5} more")

    return "\n".join(output)


def get_performance_emoji(rating: str) -> str:
    """Get emoji for performance rating (returning empty string for clean text)."""
    return ""


def get_quadrant_emoji(quadrant: str) -> str:
    """Get emoji for menu engineering quadrant (returning empty string for clean text)."""
    return ""
