#!/usr/bin/env python3
"""
Demo: How to Use Menu Engineering Questions
Shows practical examples of asking questions and getting insights
"""

import os
import sys
import django
import json

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from backend.consulting_services.menu import menu_questions
from backend.shared.ai.intent_classifier import classify_intent


def demo_direct_api_call():
    """Example 1: Direct API call to menu_questions.run()"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Direct API Call")
    print("="*80)

    # Ask a question directly
    params = {
        "question": "Which menu items have the highest contribution margin?"
    }

    print(f"\n📝 Question: {params['question']}")
    print("\n🔧 API Call:")
    print(f"   menu_questions.run(params={params})")

    response, status_code = menu_questions.run(params, None)

    print(f"\n📊 Response (Status: {status_code}):")

    if status_code == 200:
        data = response.get('data', {})
        print(f"\n   Question: {data.get('question')}")
        print(f"\n   💡 Insight: {data.get('insight')}")
        print(f"\n   🎯 Recommendation: {data.get('recommendation')}")

        # Show top items
        top_items = data.get('top_10_by_margin', [])[:3]
        if top_items:
            print(f"\n   📈 Top 3 Items by Margin:")
            for i, item in enumerate(top_items, 1):
                print(f"      {i}. {item['name']}")
                print(f"         - Margin: {item['contribution_margin']:.1f}%")
                print(f"         - Units Sold: {item['units_sold']}")
                print(f"         - Quadrant: {item['quadrant']}")


def demo_conversational_query():
    """Example 2: Using natural language through intent classifier"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Natural Language Query (How Users Will Ask)")
    print("="*80)

    user_query = "What if I increase my prices by $0.50?"

    print(f"\n💬 User asks: \"{user_query}\"")

    # Step 1: Classify the intent
    intent = classify_intent(user_query)
    print(f"\n🧠 System classifies intent:")
    print(f"   - Detected: {intent['intent']}")
    print(f"   - Confidence: {intent['confidence']:.0%}")
    print(f"   - Will route to: {intent['endpoint']}")

    # Step 2: Call the API
    params = {"question": user_query, "increase_amount": 0.50}
    response, status_code = menu_questions.run(params, None)

    print(f"\n💬 AI responds:")

    if status_code == 200:
        data = response.get('data', {})
        print(f"\n   {data.get('insight')}")
        print(f"\n   💡 {data.get('recommendation')}")

        # Show financial impact
        flat_profit = data.get('flat_increase_profit', 0)
        percent_profit = data.get('percent_increase_profit', 0)

        print(f"\n   📊 Financial Impact:")
        print(f"      • $0.50 flat increase = ${flat_profit:,.2f} additional profit")
        print(f"      • 1% increase = ${percent_profit:,.2f} additional profit")
        print(f"      • Better strategy: {data.get('better_strategy')}")


def demo_pricing_question():
    """Example 3: Pricing strategy question"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Pricing Analysis")
    print("="*80)

    user_query = "Which items are undervalued?"

    print(f"\n💬 User asks: \"{user_query}\"")

    params = {"question": user_query}
    response, status_code = menu_questions.run(params, None)

    if status_code == 200:
        data = response.get('data', {})
        print(f"\n📊 Analysis:")
        print(f"   - Undervalued items found: {data.get('undervalued_count', 0)}")
        print(f"   - Total revenue opportunity: ${data.get('total_potential_revenue', 0):,.2f}")

        print(f"\n   💡 {data.get('insight')}")
        print(f"\n   🎯 {data.get('recommendation')}")

        # Show top undervalued items
        items = data.get('undervalued_items', [])[:3]
        if items:
            print(f"\n   Top 3 Undervalued Items:")
            for item in items:
                print(f"\n      📌 {item['name']}")
                print(f"         Current: ${item['current_price']:.2f}")
                print(f"         Optimal: ${item['optimal_price']:.2f}")
                print(f"         Gap: ${item['price_gap']:.2f}")


def demo_design_question():
    """Example 4: Menu design question"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Menu Design Recommendations")
    print("="*80)

    user_query = "What callouts should I use on my menu?"

    print(f"\n💬 User asks: \"{user_query}\"")

    params = {"question": user_query}
    response, status_code = menu_questions.run(params, None)

    if status_code == 200:
        data = response.get('data', {})

        print(f"\n   💡 {data.get('insight')}")

        # Show icon effectiveness
        icon_effectiveness = data.get('icon_effectiveness', {})
        if icon_effectiveness:
            print(f"\n   📋 Callout Performance:")
            for icon, lift in icon_effectiveness.items():
                print(f"      {icon}: {lift}")

        print(f"\n   🎯 {data.get('recommendation')}")

        # Show specific recommendations
        recommendations = data.get('callout_recommendations', [])[:3]
        if recommendations:
            print(f"\n   Recommended Callouts:")
            for rec in recommendations:
                print(f"\n      {rec['recommended_callout']} - {rec['name']}")
                print(f"         Reason: {rec['reason']}")
                print(f"         Expected: {rec['expected_lift']}")


def demo_all_question_types():
    """Show all 20 question types available"""
    print("\n" + "="*80)
    print("ALL 20 AVAILABLE QUESTIONS")
    print("="*80)

    questions = {
        "Product Mix (8 questions)": [
            "Which menu items have the highest contribution margin?",
            "What percentage of profit is from the top 5 selling items?",
            "Which items are in the dog quadrant?",
            "How have sales trends changed month over month?",
            "What are the menu mix percentages by category?",
            "Which items are hidden stars?",
            "What's the profit per labor minute by category?",
            "What is the average check size?",
        ],
        "Pricing (7 questions)": [
            "Which menu items are undervalued?",
            "What if I increase prices by $0.50?",
            "What is the price elasticity for each item?",
            "How do food costs compare to target margins?",
            "What pricing strategy yields the best results?",
            "What bundling opportunities exist?",
            "What's the impact of 5% vendor inflation?",
        ],
        "Menu Design (5 questions)": [
            "Which items should be in prime visual zones?",
            "What callouts should I use?",
            "Does category sequencing affect guest spend?",
            "What design elements increase perceived value?",
            "How can I prioritize limited-time offers?",
        ]
    }

    for category, question_list in questions.items():
        print(f"\n{category}:")
        for i, q in enumerate(question_list, 1):
            print(f"   {i}. {q}")


if __name__ == "__main__":
    print("\n" + "🍽️ " * 20)
    print("MENU ENGINEERING QUESTIONS - USAGE DEMO")
    print("How to ask questions and get actionable insights")
    print("🍽️ " * 20)

    # Run all demos
    demo_direct_api_call()
    demo_conversational_query()
    demo_pricing_question()
    demo_design_question()
    demo_all_question_types()

    print("\n" + "="*80)
    print("✅ DEMO COMPLETE")
    print("="*80)
    print("\n💡 How to use in production:")
    print("   1. User types question in chat interface")
    print("   2. System routes to conversational AI endpoint")
    print("   3. Intent classifier detects question type")
    print("   4. menu_questions.run() generates analysis")
    print("   5. User receives insights + recommendations\n")
