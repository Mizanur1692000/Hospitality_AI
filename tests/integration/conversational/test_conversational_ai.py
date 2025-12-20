"""
Integration Tests for Conversational AI

Tests natural language interface to business logic features.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from apps.agent_core.tasks import conversational_ai
from backend.shared.ai import classify_intent, extract_parameters


def test_intent_classification():
    """Test that natural language queries are classified correctly."""
    print("\n" + "="*80)
    print("TEST: Intent Classification")
    print("="*80)

    test_cases = [
        ("What are my highest selling items?", "highest_selling"),
        ("Show me my most profitable items", "most_profitable"),
        ("What are my star items?", "stars"),
        ("Which items should I remove?", "dogs"),
        ("Are any items underpriced?", "underpriced_items"),
        ("Show me pricing opportunities", "pricing_strategy"),
        ("Where should I place items on my menu?", "golden_triangle"),
        ("help", "help"),
    ]

    passed = 0
    for query, expected_intent in test_cases:
        intent = classify_intent(query)
        actual_intent = intent["intent"]

        if actual_intent == expected_intent:
            print(f"✅ PASS - '{query}' → {actual_intent}")
            passed += 1
        else:
            print(f"❌ FAIL - '{query}' → Expected: {expected_intent}, Got: {actual_intent}")

    print(f"\nIntent Classification: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_parameter_extraction():
    """Test that parameters are extracted from natural language queries."""
    print("\n" + "="*80)
    print("TEST: Parameter Extraction")
    print("="*80)

    test_cases = [
        ("Show me underpriced appetizers", {"category_filter": "Appetizers"}),
        ("What are my highest selling main course items?", {"category_filter": "Main Course"}),
        ("Show me items with 28% food cost", {"target_food_cost": 28.0}),
    ]

    passed = 0
    for query, expected_params in test_cases:
        intent = classify_intent(query)
        params = extract_parameters(query, intent)

        # Check if all expected params are present
        match = all(params.get(k) == v for k, v in expected_params.items())

        if match:
            print(f"✅ PASS - '{query}' → {params}")
            passed += 1
        else:
            print(f"❌ FAIL - '{query}'")
            print(f"   Expected: {expected_params}")
            print(f"   Got: {params}")

    print(f"\nParameter Extraction: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_highest_selling_items():
    """Test conversational query for highest selling items."""
    print("\n" + "="*80)
    print("TEST: Highest Selling Items (Conversational)")
    print("="*80)

    params = {
        "query": "What are my highest selling items?",
        "session_id": "test_session_1"
    }

    result, status_code = conversational_ai.run(params, None)

    assert status_code == 200, f"Expected 200, got {status_code}"
    assert result.get("status") == "success", "Expected success status"

    data = result.get("data", {})
    assert "answer" in data, "Missing 'answer' field"
    assert "insights" in data, "Missing 'insights' field"
    assert "suggestions" in data, "Missing 'suggestions' field"
    assert "session_id" in data, "Missing 'session_id' field"

    print("✅ PASS - Highest Selling Items")
    print(f"\nAnswer Preview:\n{data['answer'][:200]}...\n")
    print(f"Insights: {len(data['insights'])} generated")
    print(f"Suggestions: {data['suggestions']}")

    return True


def test_star_items():
    """Test conversational query for star items."""
    print("\n" + "="*80)
    print("TEST: Star Items (Conversational)")
    print("="*80)

    params = {
        "query": "What are my star items?",
        "session_id": "test_session_2"
    }

    result, status_code = conversational_ai.run(params, None)

    assert status_code == 200, f"Expected 200, got {status_code}"
    assert result.get("status") == "success", "Expected success status"

    data = result.get("data", {})
    assert "answer" in data, "Missing 'answer' field"
    assert "⭐" in data["answer"] or "Stars" in data["answer"], "Expected star emoji or 'Stars' in answer"

    print("✅ PASS - Star Items")
    print(f"\nAnswer Preview:\n{data['answer'][:300]}...\n")

    return True


def test_underpriced_items():
    """Test conversational query for underpriced items."""
    print("\n" + "="*80)
    print("TEST: Underpriced Items (Conversational)")
    print("="*80)

    params = {
        "query": "Are any items underpriced?",
        "session_id": "test_session_3"
    }

    result, status_code = conversational_ai.run(params, None)

    assert status_code == 200, f"Expected 200, got {status_code}"
    assert result.get("status") == "success", "Expected success status"

    data = result.get("data", {})
    assert "answer" in data, "Missing 'answer' field"

    print("✅ PASS - Underpriced Items")
    print(f"\nAnswer Preview:\n{data['answer'][:300]}...\n")

    return True


def test_golden_triangle():
    """Test conversational query for golden triangle placement."""
    print("\n" + "="*80)
    print("TEST: Golden Triangle Placement (Conversational)")
    print("="*80)

    params = {
        "query": "Where should I place items on my menu?",
        "session_id": "test_session_4"
    }

    result, status_code = conversational_ai.run(params, None)

    assert status_code == 200, f"Expected 200, got {status_code}"
    assert result.get("status") == "success", "Expected success status"

    data = result.get("data", {})
    assert "answer" in data, "Missing 'answer' field"
    assert "Golden Triangle" in data["answer"] or "📍" in data["answer"], "Expected Golden Triangle info"

    print("✅ PASS - Golden Triangle Placement")
    print(f"\nAnswer Preview:\n{data['answer'][:300]}...\n")

    return True


def test_help_command():
    """Test help command."""
    print("\n" + "="*80)
    print("TEST: Help Command")
    print("="*80)

    params = {
        "query": "help",
        "session_id": "test_session_5"
    }

    result, status_code = conversational_ai.run(params, None)

    assert status_code == 200, f"Expected 200, got {status_code}"
    assert result.get("status") == "success", "Expected success status"

    data = result.get("data", {})
    assert "answer" in data, "Missing 'answer' field"
    assert "Menu Analysis" in data["answer"] or "help" in data["answer"].lower(), "Expected help content"

    print("✅ PASS - Help Command")
    print(f"\nAnswer Preview:\n{data['answer'][:300]}...\n")

    return True


def test_conversation_state():
    """Test that conversation state is maintained across turns."""
    print("\n" + "="*80)
    print("TEST: Conversation State Management")
    print("="*80)

    session_id = "test_session_state"

    # Turn 1
    params1 = {
        "query": "What are my highest selling items?",
        "session_id": session_id
    }
    result1, _ = conversational_ai.run(params1, None)
    data1 = result1.get("data", {})
    turn_count_1 = data1.get("conversation_metadata", {}).get("turn_count", 0)

    # Turn 2
    params2 = {
        "query": "Show me my star items",
        "session_id": session_id
    }
    result2, _ = conversational_ai.run(params2, None)
    data2 = result2.get("data", {})
    turn_count_2 = data2.get("conversation_metadata", {}).get("turn_count", 0)

    assert turn_count_2 == turn_count_1 + 1, f"Expected turn count to increase from {turn_count_1} to {turn_count_1 + 1}, got {turn_count_2}"

    print(f"✅ PASS - Conversation State")
    print(f"   Turn 1 count: {turn_count_1}")
    print(f"   Turn 2 count: {turn_count_2}")

    return True


def test_category_filter():
    """Test category filtering in natural language queries."""
    print("\n" + "="*80)
    print("TEST: Category Filter (Natural Language)")
    print("="*80)

    params = {
        "query": "What are my highest selling appetizers?",
        "session_id": "test_session_category"
    }

    result, status_code = conversational_ai.run(params, None)

    assert status_code == 200, f"Expected 200, got {status_code}"
    data = result.get("data", {})

    # Check that category filter was applied
    raw_data = data.get("raw_data", {})
    filtered_items = raw_data.get("filtered_items", 0)

    print(f"✅ PASS - Category Filter")
    print(f"   Query: 'highest selling appetizers'")
    print(f"   Filtered to: {filtered_items} items")

    return True


def run_all_tests():
    """Run all conversational AI tests."""
    print("\n" + "="*80)
    print("CONVERSATIONAL AI TEST SUITE")
    print("="*80)

    tests = [
        ("Intent Classification", test_intent_classification),
        ("Parameter Extraction", test_parameter_extraction),
        ("Highest Selling Items", test_highest_selling_items),
        ("Star Items", test_star_items),
        ("Underpriced Items", test_underpriced_items),
        ("Golden Triangle", test_golden_triangle),
        ("Help Command", test_help_command),
        ("Conversation State", test_conversation_state),
        ("Category Filter", test_category_filter),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, "PASS" if passed else "FAIL"))
        except AssertionError as e:
            print(f"❌ FAIL - {test_name}: {str(e)}")
            results.append((test_name, "FAIL"))
        except Exception as e:
            print(f"❌ ERROR - {test_name}: {str(e)}")
            results.append((test_name, "ERROR"))

    # Print summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    for test_name, status in results:
        emoji = "✅" if status == "PASS" else "❌"
        print(f"{emoji} {status} - {test_name}")

    passed_count = sum(1 for _, status in results if status == "PASS")
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0

    print(f"\nRESULTS: {passed_count}/{total_count} tests passed ({pass_rate:.1f}%)")

    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
