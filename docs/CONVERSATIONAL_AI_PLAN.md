# Conversational AI Interface - Implementation Plan

**Date:** October 27, 2025
**Purpose:** Add natural language interface to all business logic features
**Status:** Planning Phase
**Estimated Time:** 2-3 hours (broken into 30-minute increments)

---

## Overview

Add a conversational AI layer that lets users ask questions in natural language and get intelligent responses with insights and suggestions.

### User Experience Goal

```
User: "What were my highest selling items?"

AI: "Your top 3 sellers this month were:
    1. Grilled Atlantic Salmon ($4,247 revenue, 180 orders)
    2. Spaghetti Carbonara ($2,658 revenue, 142 orders)
    3. Bruschetta al Pomodoro ($1,618 revenue, 180 orders)

    💡 Insight: These 3 items are classified as 'Stars' - they're
    both popular AND profitable. I recommend featuring them
    prominently on your menu.

    Would you like me to:
    • Analyze pricing opportunities for these items?
    • Show menu design recommendations?
    • Compare to last month's performance?"

User: "Yes, analyze pricing"

AI: [calls pricing API, returns conversational response]
```

---

## Architecture Overview

### Non-Breaking Design

```
User Question
    ↓
Conversational AI Layer (NEW)
    ├── Intent Classifier → "What does user want?"
    ├── Parameter Extractor → "What filters/options?"
    └── Response Generator → "Format results conversationally"
    ↓
Existing Business Logic (UNCHANGED)
    ├── Product Mix Analysis
    ├── Pricing Strategy
    ├── Menu Design
    └── [Future Features]
    ↓
Conversational Response + Suggestions
```

**Key Principle:** Conversational layer **wraps** existing APIs, never modifies them.

---

## Implementation Steps (10 Safe, Small Steps)

### Phase 1: Foundation (30 minutes)

#### Step 1.1: Create Conversational Module Structure (5 min)
**What:** Create new folder structure without touching existing code

**Files to Create:**
```
apps/agent_core/conversational/
├── __init__.py
├── intent_classifier.py     # Maps questions to endpoints
├── response_generator.py    # Formats results conversationally
├── conversation_state.py    # Tracks conversation history
└── prompts.py              # LLM prompt templates
```

**Success Criteria:** Files created, imports work, no errors

**Testing:**
```python
from apps.agent_core.conversational import intent_classifier
# Should import without errors
```

---

#### Step 1.2: Define Intent Mapping Schema (10 min)
**What:** Create a simple mapping of user intents to existing endpoints

**File:** `apps/agent_core/conversational/intent_classifier.py`

**Code:**
```python
INTENT_MAP = {
    # Product Mix related
    "highest_selling": {
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "top_performers.by_units_sold"
    },
    "most_profitable": {
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "top_performers.by_total_profit"
    },
    "menu_performance": {
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "quadrant_summary"
    },

    # Pricing related
    "pricing_opportunities": {
        "endpoint": "menu/pricing",
        "params": {},
        "extract": "pricing_opportunities"
    },
    "underpriced_items": {
        "endpoint": "menu/pricing",
        "params": {},
        "extract": "pricing_opportunities.underpriced_items"
    },

    # Design related
    "menu_layout": {
        "endpoint": "menu/design",
        "params": {},
        "extract": "golden_triangle"
    }
}

def classify_intent(user_question: str) -> dict:
    """
    Use simple keyword matching initially.
    Later: use LLM for better understanding.
    """
    question_lower = user_question.lower()

    # Simple keyword matching
    if any(word in question_lower for word in ["highest selling", "top selling", "best sellers"]):
        return INTENT_MAP["highest_selling"]
    elif any(word in question_lower for word in ["most profitable", "highest profit"]):
        return INTENT_MAP["most_profitable"]
    elif any(word in question_lower for word in ["underpriced", "raise prices", "pricing opportunities"]):
        return INTENT_MAP["underpriced_items"]
    # ... more patterns

    return None  # Unknown intent
```

**Success Criteria:** Function returns correct intent for test questions

**Testing:**
```python
intent = classify_intent("What were my highest selling items?")
assert intent["endpoint"] == "menu/product_mix"
```

---

#### Step 1.3: Create Response Templates (15 min)
**What:** Create conversational response templates

**File:** `apps/agent_core/conversational/response_generator.py`

**Code:**
```python
RESPONSE_TEMPLATES = {
    "highest_selling": """
Your top {count} sellers this month were:
{items_list}

💡 Insight: {insight}

Would you like me to:
• Analyze pricing opportunities for these items?
• Show menu design recommendations?
• Compare performance by category?
""",

    "most_profitable": """
Your most profitable items are:
{items_list}

💰 Revenue Impact: These {count} items generated ${total_profit:,.2f}
in profit ({percent:.1f}% of total profit).

{insight}

Next steps:
• Check if they're positioned prominently on your menu
• See if they're priced optimally
• Analyze what makes them successful
""",

    "underpriced_items": """
I found {count} items that could be priced higher:

{items_list}

💰 Revenue Opportunity: ${opportunity:,.2f}/month if you adjust pricing

{insight}

Would you like me to:
• Show detailed pricing recommendations?
• Analyze customer acceptance risk?
• Compare to competitor pricing?
"""
}

def generate_response(intent: str, data: dict) -> str:
    """Generate conversational response from analysis data."""
    template = RESPONSE_TEMPLATES.get(intent)
    if not template:
        return "I analyzed that for you. Here's what I found:\n" + str(data)

    # Format template with data
    return template.format(**data)
```

**Success Criteria:** Templates render correctly with sample data

**Testing:**
```python
response = generate_response("highest_selling", {
    "count": 3,
    "items_list": "1. Salmon\n2. Pasta\n3. Salad",
    "insight": "These are Star items!"
})
assert "top 3 sellers" in response
```

---

### Phase 2: Simple Chat Endpoint (30 minutes)

#### Step 2.1: Create Chat View (10 min)
**What:** Create a new chat endpoint that doesn't touch existing endpoints

**File:** `apps/agent_core/views.py` (add new function, don't modify existing)

**Code:**
```python
@require_http_methods(["POST"])
def chat(request):
    """
    Conversational AI endpoint.

    Request:
    {
        "message": "What were my highest selling items?",
        "conversation_id": "optional_session_id"
    }

    Response:
    {
        "response": "Your top 3 sellers...",
        "suggestions": ["Analyze pricing", "Show menu design"],
        "conversation_id": "session_id",
        "data": {...}  # Full analysis data if needed
    }
    """
    from apps.agent_core.conversational.intent_classifier import classify_intent
    from apps.agent_core.conversational.response_generator import generate_response
    from apps.agent_core.tasks.menu import product_mix, pricing, design

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")
        conversation_id = data.get("conversation_id", None)

        # Step 1: Classify intent
        intent = classify_intent(user_message)
        if not intent:
            return JsonResponse({
                "response": "I'm not sure I understand. Could you rephrase that?",
                "suggestions": [
                    "What are my highest selling items?",
                    "Show me pricing opportunities",
                    "How should I design my menu?"
                ]
            })

        # Step 2: Call appropriate endpoint
        endpoint = intent["endpoint"]
        params = intent.get("params", {})

        if endpoint == "menu/product_mix":
            result, status = product_mix.run(params, None)
        elif endpoint == "menu/pricing":
            result, status = pricing.run(params, None)
        elif endpoint == "menu/design":
            result, status = design.run(params, None)

        if status != 200:
            return JsonResponse({
                "response": "I encountered an error analyzing that. Please try again.",
                "error": result.get("error")
            }, status=500)

        # Step 3: Extract relevant data
        extract_path = intent.get("extract", "")
        relevant_data = _extract_data(result["data"], extract_path)

        # Step 4: Generate conversational response
        response_text = generate_response(intent["intent_name"], relevant_data)

        # Step 5: Generate suggestions
        suggestions = _generate_suggestions(intent, result["data"])

        return JsonResponse({
            "response": response_text,
            "suggestions": suggestions,
            "conversation_id": conversation_id or str(uuid.uuid4()),
            "raw_data": result["data"]  # Include for transparency
        })

    except Exception as e:
        return JsonResponse({
            "response": "I encountered an unexpected error.",
            "error": str(e)
        }, status=500)


def _extract_data(data: dict, path: str) -> dict:
    """Extract nested data using dot notation."""
    if not path:
        return data

    keys = path.split(".")
    result = data
    for key in keys:
        result = result.get(key, {})
    return result


def _generate_suggestions(intent: dict, data: dict) -> list:
    """Generate contextual follow-up suggestions."""
    # Based on current intent, suggest related actions
    suggestions = []

    if "product_mix" in intent["endpoint"]:
        suggestions = [
            "Analyze pricing opportunities",
            "Show menu design recommendations",
            "Compare performance by category"
        ]
    elif "pricing" in intent["endpoint"]:
        suggestions = [
            "Show which items to feature prominently",
            "Analyze menu layout",
            "See full product mix analysis"
        ]
    elif "design" in intent["endpoint"]:
        suggestions = [
            "Check pricing optimization",
            "See top performers",
            "Get profitability breakdown"
        ]

    return suggestions
```

**Success Criteria:** New endpoint works, existing endpoints unchanged

**Testing:**
```bash
curl -X POST "http://localhost:8000/api/agent/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What were my highest selling items?"}'
```

---

#### Step 2.2: Add Chat URL Route (5 min)
**What:** Add URL route for chat endpoint

**File:** `apps/agent_core/urls.py` (add new route, don't modify existing)

**Code:**
```python
urlpatterns = [
    # Existing routes (DO NOT MODIFY)
    path('safe/', views.safe_agent_endpoint, name='safe_agent'),
    path('run/', views.run_agent_task, name='run_task'),

    # NEW: Conversational interface
    path('chat/', views.chat, name='chat'),  # NEW
]
```

**Success Criteria:** Route accessible, existing routes still work

**Testing:**
```bash
# Test new endpoint
curl -X POST "http://localhost:8000/api/agent/chat/" \
  -d '{"message": "test"}'

# Test old endpoints still work
curl -X POST "http://localhost:8000/api/agent/safe/" \
  -d '{"service": "menu", "subtask": "product_mix", "params": {}}'
```

---

#### Step 2.3: Test with One Simple Question (15 min)
**What:** End-to-end test with "What were my highest selling items?"

**Success Criteria:** Get conversational response with suggestions

**Expected Response:**
```json
{
  "response": "Your top 3 sellers this month were:\n1. Grilled Atlantic Salmon ($4,247 revenue)\n2. Spaghetti Carbonara ($2,658 revenue)\n3. Bruschetta al Pomodoro ($1,618 revenue)\n\n💡 These are Star items...",
  "suggestions": [
    "Analyze pricing opportunities",
    "Show menu design recommendations"
  ],
  "conversation_id": "abc-123"
}
```

---

### Phase 3: Enhance Intent Recognition (30 minutes)

#### Step 3.1: Add More Intent Patterns (15 min)
**What:** Expand keyword matching for more questions

**Patterns to Add:**
- "show me my stars" → product_mix (filter stars)
- "what should I remove" → product_mix (filter dogs)
- "which items to raise prices on" → pricing (underpriced)
- "where should I place [item]" → design (golden_triangle)
- "compare [category] performance" → product_mix (category filter)

**File:** `intent_classifier.py`

---

#### Step 3.2: Add Parameter Extraction (15 min)
**What:** Extract filters/options from questions

**Examples:**
- "Show me Main Course performance" → params: {"category_filter": "Main Course"}
- "Use 28% food cost target" → params: {"target_food_cost": 28.0}

**Code:**
```python
def extract_parameters(user_question: str, intent: dict) -> dict:
    """Extract parameters from natural language."""
    params = intent.get("params", {}).copy()

    # Category extraction
    categories = ["Appetizer", "Main Course", "Dessert", "Beverage"]
    for category in categories:
        if category.lower() in user_question.lower():
            params["category_filter"] = category

    # Number extraction
    import re
    numbers = re.findall(r'\d+', user_question)
    if numbers and "food cost" in user_question.lower():
        params["target_food_cost"] = float(numbers[0])

    return params
```

---

### Phase 4: Conversation Memory (30 minutes)

#### Step 4.1: Add Conversation State Storage (15 min)
**What:** Remember conversation context

**File:** `apps/agent_core/conversational/conversation_state.py`

**Code:**
```python
# Simple in-memory storage (use Redis/DB for production)
CONVERSATIONS = {}

class ConversationState:
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.messages = []
        self.last_intent = None
        self.last_data = None

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        })

    def set_context(self, intent: dict, data: dict):
        self.last_intent = intent
        self.last_data = data

    def get_context(self):
        return {
            "last_intent": self.last_intent,
            "last_data": self.last_data,
            "history": self.messages[-5:]  # Last 5 messages
        }

def get_conversation(conversation_id: str) -> ConversationState:
    if conversation_id not in CONVERSATIONS:
        CONVERSATIONS[conversation_id] = ConversationState(conversation_id)
    return CONVERSATIONS[conversation_id]
```

---

#### Step 4.2: Handle Follow-up Questions (15 min)
**What:** Use context to understand follow-ups

**Examples:**
```
User: "What are my highest selling items?"
AI: [shows top sellers]

User: "Show me pricing for those"  ← "those" refers to previous items
AI: [analyzes pricing for the 3 items from previous response]

User: "What about Main Course only?"  ← Continues same analysis type
AI: [filters to Main Course]
```

**Code:**
```python
def classify_intent_with_context(user_question: str, context: dict) -> dict:
    """Classify intent using conversation context."""
    question_lower = user_question.lower()

    # Check for follow-up indicators
    follow_up_words = ["those", "them", "these", "that", "it", "also", "too"]
    is_follow_up = any(word in question_lower for word in follow_up_words)

    if is_follow_up and context.get("last_intent"):
        # Modify last intent based on new question
        intent = context["last_intent"].copy()

        # Check for intent shift
        if "pricing" in question_lower:
            intent["endpoint"] = "menu/pricing"
        elif "design" in question_lower or "layout" in question_lower:
            intent["endpoint"] = "menu/design"

        return intent

    # Regular intent classification
    return classify_intent(user_question)
```

---

### Phase 5: Intelligent Response Generation (30 minutes)

#### Step 5.1: Add Context-Aware Insights (15 min)
**What:** Generate insights based on actual data

**Code:**
```python
def generate_insights(intent: str, data: dict) -> list:
    """Generate intelligent insights from analysis data."""
    insights = []

    if intent == "highest_selling":
        # Check if top sellers are also profitable
        top_items = data.get("top_performers", {}).get("by_units_sold", [])[:3]
        for item in top_items:
            if item.get("quadrant") == "star":
                insights.append(f"✨ {item['menu_name']} is a Star - keep promoting it!")
            elif item.get("quadrant") == "plowhorse":
                insights.append(f"⚠️ {item['menu_name']} sells well but has low profit - consider raising price")

    elif intent == "underpriced_items":
        opportunity = data.get("revenue_impact", {}).get("total_opportunity", 0)
        if opportunity > 1000:
            insights.append(f"🚀 You could gain ${opportunity:,.2f}/month by adjusting prices!")

    return insights
```

---

#### Step 5.2: Add Smart Suggestions (15 min)
**What:** Contextual next-step suggestions

**Code:**
```python
def generate_smart_suggestions(intent: dict, data: dict) -> list:
    """Generate contextual suggestions based on data."""
    suggestions = []

    # Analyze data to suggest relevant actions
    if "quadrant_summary" in data:
        stars = data["quadrant_summary"]["stars"]["count"]
        dogs = data["quadrant_summary"]["dogs"]["count"]

        if dogs > 0:
            suggestions.append(f"💡 Remove {dogs} underperforming items")
        if stars > 0:
            suggestions.append(f"✨ Feature {stars} Star items prominently")

    if "pricing_opportunities" in data:
        underpriced = data["pricing_opportunities"]["summary"]["underpriced_count"]
        if underpriced > 0:
            suggestions.append(f"💰 Raise prices on {underpriced} items")

    # Always offer to dig deeper
    suggestions.append("🔍 See detailed analysis")
    suggestions.append("📊 Compare to industry benchmarks")

    return suggestions[:5]  # Max 5 suggestions
```

---

### Phase 6: Integration & Testing (30 minutes)

#### Step 6.1: Create Comprehensive Tests (15 min)
**What:** Test all conversation flows

**File:** `tests/integration/conversational/test_chat.py`

**Test Cases:**
```python
def test_simple_question():
    """Test: 'What were my highest selling items?'"""
    response = chat("What were my highest selling items?")
    assert "top" in response["response"].lower()
    assert len(response["suggestions"]) > 0

def test_follow_up_question():
    """Test: Follow-up with 'Show me pricing for those'"""
    # First question
    response1 = chat("What are my stars?", conversation_id="test-123")

    # Follow-up
    response2 = chat("Show me pricing for those", conversation_id="test-123")
    assert response2["response"] != "I don't understand"

def test_category_filter():
    """Test: 'Show me Main Course performance'"""
    response = chat("Show me Main Course performance")
    # Should filter to Main Course
    assert response["raw_data"]["overall_metrics"]["total_menu_items"] == 8

def test_pricing_question():
    """Test: 'Which items should I raise prices on?'"""
    response = chat("Which items should I raise prices on?")
    assert "underpriced" in response["response"].lower()
```

---

#### Step 6.2: End-to-End Testing (15 min)
**What:** Test complete conversation flows

**Test Conversation 1:**
```
User: "What were my highest selling items?"
→ Should return top sellers

User: "Are they profitable?"
→ Should check quadrant classification

User: "Show me pricing recommendations"
→ Should run pricing analysis
```

**Test Conversation 2:**
```
User: "How's my menu performing?"
→ Should run product mix analysis

User: "What about just appetizers?"
→ Should filter to Appetizers category

User: "Which ones should I remove?"
→ Should show Dog items in Appetizers
```

---

## Integration with Business Logic Workflow

### Add to Workflow Document

**New Step 9: Conversational Interface (Optional)**

After completing Step 8 (Testing & Validation), optionally add conversational interface:

```markdown
### STEP 9: Conversational Interface (Optional)

**Objective:** Add natural language interface

**Tasks:**
- [ ] Add intent patterns for this feature
- [ ] Create response templates
- [ ] Test conversational flow
- [ ] Add follow-up suggestions

**Deliverable:** Users can ask questions in natural language

**Time Estimate:** 30 minutes per feature
```

---

## Deployment Checklist

### Before Production

- [ ] All existing endpoints still work (backward compatibility)
- [ ] Chat endpoint handles errors gracefully
- [ ] Conversation state persists (use Redis/DB, not memory)
- [ ] Rate limiting added to chat endpoint
- [ ] Logging for user questions (analytics)
- [ ] Privacy: Don't log sensitive data

### Security Considerations

- [ ] Input validation (prevent injection)
- [ ] Rate limiting (prevent abuse)
- [ ] Authentication (who can chat?)
- [ ] Data access control (users see only their data)

---

## Success Metrics

### Track These After Launch

1. **Adoption Rate:** % of users using chat vs direct API
2. **Intent Recognition:** % of questions understood correctly
3. **Follow-up Rate:** % of users asking follow-up questions
4. **Task Completion:** Users getting answers without API docs

### Target Goals

- 90%+ intent recognition accuracy
- 3+ questions per conversation (shows engagement)
- 50%+ users prefer chat over API

---

## Example Conversations

### Conversation 1: Menu Analysis
```
User: "What were my highest selling items this month?"

AI: "Your top 3 sellers were:
    1. Grilled Atlantic Salmon - $4,247 revenue (180 orders)
    2. Spaghetti Carbonara - $2,658 revenue (142 orders)
    3. Bruschetta al Pomodoro - $1,618 revenue (180 orders)

    💡 All 3 are 'Star' items - high popularity AND profitability!

    Next steps:
    • Feature these items prominently on your menu
    • Check if they're priced optimally
    • See menu design recommendations"

User: "Show me pricing for those items"

AI: "Here's the pricing analysis for your top 3 items:

    ✅ Grilled Atlantic Salmon: Well-priced at $23.59
       (Food cost: 23.4%, optimal for this category)

    ⚠️ Spaghetti Carbonara: Slightly underpriced
       Current: $18.72, Optimal: $19.95 (+$1.23)
       💰 Opportunity: $175/month if adjusted

    ✅ Bruschetta al Pomodoro: Well-priced at $8.99

    Would you like me to:
    • Show detailed pricing recommendations for all items?
    • Analyze customer price sensitivity?
    • See menu design suggestions?"
```

### Conversation 2: Quick Insights
```
User: "How's my menu performing?"

AI: "Your menu analysis (20 items total):

    ⭐ Stars: 3 items (15%) - Great performers!
    🐴 Plowhorses: 7 items (35%) - Popular but low profit
    🧩 Puzzles: 6 items (30%) - High profit, need promotion
    🐕 Dogs: 4 items (20%) - Consider removing

    📊 Overall: $29,975 revenue, $25,088 profit this month

    🎯 Top Priority: You have 4 Dog items that aren't performing.

    Quick wins:
    • Remove or improve your 4 Dog items
    • Promote your 6 Puzzle items (they're profitable!)
    • Feature your 3 Star items prominently"

User: "Which items should I remove?"

AI: "Your 4 Dog items (low profit + low popularity):

    1. Veggie Burger - $892 revenue, $623 profit
       (Low margin: 69.8%)

    2. Greek Salad - $624 revenue, $418 profit
       (Low popularity: 48 orders)

    3. Iced Tea - $195 revenue, $156 profit
       (Minimal impact: 0.6% of revenue)

    4. [Item 4]

    💡 Recommendation: Start by removing Iced Tea (lowest impact).
    Test for 1 month and measure if customers miss it.

    Would you like me to:
    • Suggest replacement items?
    • Show what to do with freed-up menu space?
    • Analyze cost savings from simpler menu?"
```

---

## Future Enhancements

### Phase 7+ (Future)

1. **Multi-turn Reasoning**
   - "Compare this month to last month"
   - "Show me trends over time"

2. **Proactive Suggestions**
   - "I noticed your Stars dropped this month..."
   - Weekly email: "Here's your menu performance summary"

3. **Voice Interface**
   - Integrate with voice assistants
   - Phone call interface for busy managers

4. **Visual Responses**
   - Generate charts inline
   - Send formatted email reports

---

## Rollout Plan

### Week 1: Foundation
- Steps 1.1 - 1.3 (Foundation)
- Step 2.1 - 2.3 (Simple Chat Endpoint)

### Week 2: Enhancement
- Steps 3.1 - 3.2 (Intent Recognition)
- Steps 4.1 - 4.2 (Conversation Memory)

### Week 3: Polish
- Steps 5.1 - 5.2 (Smart Responses)
- Steps 6.1 - 6.2 (Testing)

### Week 4: Deploy
- Security review
- Performance testing
- Production deployment
- User training

---

## Questions to Decide

Before implementing, decide:

1. **LLM Provider:** Use OpenAI GPT-4? Claude? Local model?
2. **Conversation Storage:** Redis? PostgreSQL? In-memory for now?
3. **Rate Limiting:** How many questions per user per minute?
4. **Authentication:** Who can use chat? API key? Login required?
5. **Logging:** What to log for analytics vs privacy?

---

**Next Step:** Review this plan, then start with Step 1.1 (5 minutes)

Ready to build this? 🚀
