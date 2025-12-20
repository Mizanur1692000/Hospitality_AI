"""
Intent Classification Module

Maps natural language queries to specific API endpoints and extracts parameters.
Uses keyword matching and pattern recognition.
"""

from typing import Dict, List, Tuple, Optional
import re


# Intent mapping: natural language patterns → API endpoints
INTENT_MAP = {
    # Menu Engineering - Product Mix
    "highest_selling": {
        "keywords": ["highest selling", "top selling", "best selling", "most popular", "top food seller", "top seller", "best seller", "what sells", "popular items"],
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "top_performers.by_units_sold",
        "category": "menu"
    },
    "most_profitable": {
        "keywords": ["most profitable", "highest profit", "best margin", "biggest earners"],
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "top_performers.by_total_profit",
        "category": "menu"
    },
    "stars": {
        "keywords": ["star items", "stars", "best items", "top performers"],
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "quadrant_summary.stars",
        "category": "menu"
    },
    "dogs": {
        "keywords": ["dog items", "dogs", "worst items", "underperformers", "remove"],
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "quadrant_summary.dogs",
        "category": "menu"
    },
    "menu_analysis": {
        "keywords": ["menu analysis", "analyze menu", "menu engineering", "product mix"],
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": None,
        "category": "menu"
    },

    # Menu Engineering - Pricing
    "pricing_strategy": {
        "keywords": ["pricing strategy", "optimize pricing", "pricing analysis", "pricing opportunities"],
        "endpoint": "menu/pricing",
        "params": {},
        "extract": None,
        "category": "menu"
    },
    "underpriced_items": {
        "keywords": ["underpriced", "too cheap", "raise price"],
        "endpoint": "menu/pricing",
        "params": {},
        "extract": "pricing_opportunities.underpriced_items",
        "category": "menu"
    },
    "overpriced_items": {
        "keywords": ["overpriced", "too expensive", "lower price"],
        "endpoint": "menu/pricing",
        "params": {},
        "extract": "pricing_opportunities.overpriced_items",
        "category": "menu"
    },

    # Menu Engineering - Design
    "golden_triangle": {
        "keywords": ["where should i place", "where to place", "placement", "golden triangle"],
        "endpoint": "menu/design",
        "params": {},
        "extract": None,  # Don't extract - we need full data for response generation
        "category": "menu"
    },
    "menu_design": {
        "keywords": ["menu design", "visual hierarchy", "menu layout", "design recommendations"],
        "endpoint": "menu/design",
        "params": {},
        "extract": None,
        "category": "menu"
    },

    # Menu Engineering - Specific Questions (20 questions)
    # Product Mix Questions (8)
    "q_highest_contribution_margin": {
        "keywords": ["highest contribution margin", "best margin versus sales", "margin vs sales volume"],
        "endpoint": "menu/questions",
        "params": {"question": "highest contribution margin"},
        "extract": None,
        "category": "menu"
    },
    "q_top_profit_percentage": {
        "keywords": ["top 5", "top selling profit", "pareto", "percentage of total profit"],
        "endpoint": "menu/questions",
        "params": {"question": "top 5 profit percentage"},
        "extract": None,
        "category": "menu"
    },
    "q_dog_quadrant": {
        "keywords": ["dog quadrant", "remove items", "re-engineer", "low popularity low profit"],
        "endpoint": "menu/questions",
        "params": {"question": "dog quadrant"},
        "extract": None,
        "category": "menu"
    },
    "q_sales_trends_category": {
        "keywords": ["sales trends", "month over month", "category trends", "trend analysis"],
        "endpoint": "menu/questions",
        "params": {"question": "sales trends category"},
        "extract": None,
        "category": "menu"
    },
    "q_menu_mix_percentages": {
        "keywords": ["menu mix", "category percentage", "mix percentages", "industry benchmark"],
        "endpoint": "menu/questions",
        "params": {"question": "menu mix percentages"},
        "extract": None,
        "category": "menu"
    },
    "q_hidden_stars": {
        "keywords": ["hidden stars", "high margin low sales", "strong margins low velocity"],
        "endpoint": "menu/questions",
        "params": {"question": "hidden stars"},
        "extract": None,
        "category": "menu"
    },
    "q_profit_per_labor_minute": {
        "keywords": ["profit per labor", "labor minute", "efficiency by category"],
        "endpoint": "menu/questions",
        "params": {"question": "profit per labor minute"},
        "extract": None,
        "category": "menu"
    },
    "q_average_check_influence": {
        "keywords": ["average check", "check size", "product mix influence"],
        "endpoint": "menu/questions",
        "params": {"question": "average check influence"},
        "extract": None,
        "category": "menu"
    },

    # Pricing Questions (7)
    "q_undervalued_items": {
        "keywords": ["undervalued", "perceived value", "cost percentage"],
        "endpoint": "menu/questions",
        "params": {"question": "undervalued items"},
        "extract": None,
        "category": "menu"
    },
    "q_price_increase_impact": {
        "keywords": ["price increase", "increase by", "profit gained", "what if"],
        "endpoint": "menu/questions",
        "params": {"question": "price increase impact"},
        "extract": None,
        "category": "menu"
    },
    "q_price_elasticity": {
        "keywords": ["price elasticity", "sales don't drop", "ideal price range"],
        "endpoint": "menu/questions",
        "params": {"question": "price elasticity"},
        "extract": None,
        "category": "menu"
    },
    "q_food_cost_vs_target": {
        "keywords": ["food cost percentage", "target margin", "compare to target"],
        "endpoint": "menu/questions",
        "params": {"question": "food cost vs target"},
        "extract": None,
        "category": "menu"
    },
    "q_pricing_strategy": {
        "keywords": ["pricing strategy", "cost-plus", "competitive parity", "value-based"],
        "endpoint": "menu/questions",
        "params": {"question": "pricing strategy"},
        "extract": None,
        "category": "menu"
    },
    "q_bundling_opportunities": {
        "keywords": ["bundling", "re-priced", "ticket size", "combo"],
        "endpoint": "menu/questions",
        "params": {"question": "bundling opportunities"},
        "extract": None,
        "category": "menu"
    },
    "q_vendor_inflation_impact": {
        "keywords": ["inflation", "vendor price", "sysco", "cost changes"],
        "endpoint": "menu/questions",
        "params": {"question": "vendor inflation impact"},
        "extract": None,
        "category": "menu"
    },

    # Design Questions (5)
    "q_visual_zone_performance": {
        "keywords": ["visual zones", "upper-right", "prime position", "menu positioning"],
        "endpoint": "menu/questions",
        "params": {"question": "visual zone performance"},
        "extract": None,
        "category": "menu"
    },
    "q_callout_effectiveness": {
        "keywords": ["callouts", "icons", "chef recommendation", "selection rate"],
        "endpoint": "menu/questions",
        "params": {"question": "callout effectiveness"},
        "extract": None,
        "category": "menu"
    },
    "q_category_sequencing": {
        "keywords": ["category sequencing", "sequencing", "order effect"],
        "endpoint": "menu/questions",
        "params": {"question": "category sequencing"},
        "extract": None,
        "category": "menu"
    },
    "q_design_value_perception": {
        "keywords": ["design elements", "perceived value", "price sensitivity", "visual impact"],
        "endpoint": "menu/questions",
        "params": {"question": "design value perception"},
        "extract": None,
        "category": "menu"
    },
    "q_limited_time_offers": {
        "keywords": ["limited time", "chef features", "LTO", "short-term sales"],
        "endpoint": "menu/questions",
        "params": {"question": "limited time offers"},
        "extract": None,
        "category": "menu"
    },

    # Generic queries
    "help": {
        "keywords": ["help", "what can you do", "commands", "how to use"],
        "endpoint": None,
        "params": {},
        "extract": None,
        "category": "system"
    },
}


def classify_intent(user_query: str) -> Dict:
    """
    Classify user's natural language query into an intent.

    Args:
        user_query: Natural language question from user

    Returns:
        Dict with intent classification:
        {
            "intent": str,           # Intent key (e.g., "highest_selling")
            "confidence": float,     # 0.0-1.0 confidence score
            "endpoint": str,         # API endpoint to call
            "extract": str,          # Data path to extract (if specific)
            "category": str          # Category (menu, kpi, etc.)
        }
    """
    query_lower = user_query.lower().strip()

    best_match = None
    best_score = 0.0

    # Try to match against each intent
    for intent_key, intent_data in INTENT_MAP.items():
        keywords = intent_data["keywords"]

        # Calculate match score based on keyword presence
        matches = 0
        for keyword in keywords:
            if keyword in query_lower:
                matches += 1

        if matches > 0:
            # Score = (matches / total_keywords) weighted by keyword length
            score = matches / len(keywords)

            # Boost score for exact matches
            if any(keyword == query_lower for keyword in keywords):
                score = 1.0

            if score > best_score:
                best_score = score
                best_match = intent_key

    # If no match found, default to help
    if best_match is None:
        best_match = "help"
        best_score = 0.0

    intent_data = INTENT_MAP[best_match]

    return {
        "intent": best_match,
        "confidence": best_score,
        "endpoint": intent_data["endpoint"],
        "extract": intent_data["extract"],
        "category": intent_data["category"],
        "params": intent_data["params"].copy()
    }


def extract_parameters(user_query: str, intent: Dict) -> Dict:
    """
    Extract parameters from user query based on intent.

    Args:
        user_query: Natural language question
        intent: Intent classification result

    Returns:
        Dict of parameters to pass to API
    """
    params = intent["params"].copy()
    query_lower = user_query.lower()

    # Extract category filter
    categories = ["appetizers", "main course", "entrees", "desserts", "beverages", "drinks"]
    for category in categories:
        if category in query_lower:
            # Normalize category names
            if category in ["entrees", "main course"]:
                params["category_filter"] = "Main Course"
            elif category == "drinks":
                params["category_filter"] = "Beverages"
            else:
                params["category_filter"] = category.title()

    # Extract target food cost percentage
    food_cost_pattern = r"(\d+)%?\s*food cost"
    match = re.search(food_cost_pattern, query_lower)
    if match:
        params["target_food_cost"] = float(match.group(1))

    # Extract time period (if applicable in future)
    # month_pattern = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
    # match = re.search(month_pattern, query_lower)
    # if match:
    #     params["month"] = match.group(1)

    return params


def get_intent_examples() -> List[str]:
    """
    Get example queries for each intent category.

    Returns:
        List of example queries users can ask
    """
    return [
        # Menu Engineering
        "What were my highest selling items?",
        "Show me my most profitable items",
        "What are my star items?",
        "Which items should I remove?",
        "Are any items underpriced?",
        "What's my pricing strategy?",
        "Where should I place items on my menu?",
        "Show me menu design recommendations",

        # Filtering examples
        "What were my highest selling appetizers?",
        "Show me underpriced main course items",
        "What desserts are stars?",

        # Future features (placeholders)
        # "What's my labor cost this month?",
        # "Show me prime cost analysis",
        # "How's my inventory turnover?",
    ]


def suggest_follow_ups(intent: str, data: Dict) -> List[str]:
    """
    Generate smart follow-up suggestions based on intent and results.

    Args:
        intent: The classified intent
        data: API response data

    Returns:
        List of suggested follow-up questions
    """
    suggestions = []

    if intent in ["highest_selling", "most_profitable", "menu_analysis"]:
        suggestions.append("Show me underpriced items")
        suggestions.append("What are my dog items?")
        suggestions.append("Show me menu design recommendations")

    elif intent in ["underpriced_items", "overpriced_items", "pricing_strategy"]:
        suggestions.append("Show me my star items")
        suggestions.append("What's my menu analysis?")

    elif intent in ["golden_triangle", "menu_design"]:
        suggestions.append("Show me my most profitable items")
        suggestions.append("What items should I remove?")

    elif intent in ["stars", "dogs"]:
        suggestions.append("Show me pricing opportunities")
        suggestions.append("Where should I place these on my menu?")

    return suggestions[:3]  # Return max 3 suggestions
