# Chat Assistant Integration Pattern

**Status:** ✅ Implemented (Menu Engineering)
**Purpose:** Standard pattern for integrating GPT-4 chat with business logic features
**Part of:** Business Logic Workflow - Step 9 (New)

---

## Overview

This document describes the standard pattern for integrating conversational AI with business logic features, allowing users to ask natural language questions and get responses using their real restaurant data.

## Architecture

```
User asks question via Chat Assistant
    ↓
┌─────────────────────────────────────────┐
│  chat_with_gpt() - Main Entry Point     │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ STEP 1: Try Conversational AI           │
│  handle_conversational_ai(prompt)       │
│  → Routes to: conversational/ai         │
│  → Uses: Intent classifier + Data       │
│  → Returns: Real data analysis          │
└─────────────────────────────────────────┘
    ↓ If not recognized (help response)
┌─────────────────────────────────────────┐
│ STEP 2: Try Specific KPI Handlers       │
│  handle_kpi_analysis(prompt)            │
│  → Keyword matching (legacy)            │
│  → Returns: Specific business logic     │
└─────────────────────────────────────────┘
    ↓ If no match
┌─────────────────────────────────────────┐
│ STEP 3: Fall back to GPT-4              │
│  OpenAI API call                        │
│  → Returns: General hospitality advice  │
└─────────────────────────────────────────┘
```

---

## Implementation Steps

### Step 1: Create Conversational AI Module (if not exists)

**Location:** `apps/agent_core/conversational/`

**Components:**
- `intent_classifier.py` - Maps natural language to API endpoints
- `response_generator.py` - Formats responses conversationally
- `conversation_state.py` - Manages session state
- `prompts.py` - Response templates

**Register in task_registry.py:**
```python
task_registry.register_task("conversational", "ai", "apps.agent_core.tasks.conversational_ai")
```

### Step 2: Add Integration Function to Chat Assistant

**File:** `apps/chat_assistant/openai_utils.py`

**Add function:**
```python
def handle_conversational_ai(prompt: str) -> str:
    """
    Route natural language queries to Conversational AI.

    Returns:
        Conversational response string, or None if not recognized
    """
    try:
        from apps.agent_core.task_registry import task_registry

        # Call Conversational AI endpoint
        result, status_code = task_registry.execute_task(
            service="conversational",
            subtask="ai",
            params={"query": prompt, "session_id": "chat_assistant"},
            file_bytes=None
        )

        if status_code == 200 and result.get("status") == "success":
            data = result.get("data", {})
            answer = data.get("answer", "")

            # Check if this was a "help" response (not recognized)
            if answer.startswith("**What I Can Help You With:**") or \
               answer.startswith("I'm not sure I understood that"):
                return None  # Fall through to next handler

            # Format response with insights and suggestions
            insights = data.get("insights", [])
            suggestions = data.get("suggestions", [])

            response_parts = [answer]

            if insights:
                response_parts.append("\n**💡 Insights:**")
                for insight in insights:
                    response_parts.append(f"• {insight}")

            if suggestions:
                response_parts.append("\n**💬 You can also ask:**")
                for suggestion in suggestions[:3]:
                    response_parts.append(f"• {suggestion}")

            return "\n".join(response_parts)

        return None

    except Exception as e:
        return None  # Fall through on error
```

### Step 3: Update chat_with_gpt() to Use Integration

**File:** `apps/chat_assistant/openai_utils.py`

**Modify function:**
```python
def chat_with_gpt(prompt: str) -> str:
    """Chat with GPT-4 using the OpenAI API, with business logic integration."""
    if not prompt or not prompt.strip():
        return "Error: Please provide a message."

    # STEP 1: Try Conversational AI (natural language + real data)
    conversational_response = handle_conversational_ai(prompt)
    if conversational_response:
        return conversational_response

    # STEP 2: Try specific KPI handlers (legacy keyword-based)
    kpi_response = handle_kpi_analysis(prompt)
    if kpi_response:
        return kpi_response

    # STEP 3: Fall back to GPT-4 for general advice
    api_key = os.getenv("OPENAI_API_KEY")
    # ... (existing GPT-4 code)
```

### Step 4: Add Intent Mappings for New Feature

**File:** `apps/agent_core/conversational/intent_classifier.py`

**For each new feature, add intent mappings:**
```python
INTENT_MAP = {
    # Example: Menu Engineering
    "highest_selling": {
        "keywords": ["highest selling", "top selling", "best selling"],
        "endpoint": "menu/product_mix",
        "params": {},
        "extract": "top_performers.by_units_sold",
        "category": "menu"
    },

    # Add more for your feature...
}
```

### Step 5: Add Response Templates

**File:** `apps/agent_core/conversational/response_generator.py`

**Add response handler:**
```python
def _generate_your_feature_response(data: Dict, full_data: Dict) -> Dict:
    """Generate response for your feature."""
    # Format answer
    answer = "Your analysis results:\n\n"
    # ... format data

    # Generate insights
    insights = [
        "Key insight 1",
        "Key insight 2"
    ]

    # Suggestions
    suggestions = [
        "Try this next",
        "Check this too"
    ]

    return {
        "answer": answer,
        "insights": insights,
        "suggestions": suggestions,
        "data_summary": {}
    }
```

---

## Testing Checklist

For each new feature integration:

- [ ] ✅ Natural language query routes to Conversational AI
- [ ] ✅ Returns real data (not generic GPT-4 advice)
- [ ] ✅ Includes insights based on data
- [ ] ✅ Provides smart follow-up suggestions
- [ ] ✅ Unrecognized queries fall through to GPT-4
- [ ] ✅ General questions still use GPT-4
- [ ] ✅ Error handling doesn't break chat

**Test queries:**
```bash
# Should use Conversational AI (real data):
"What were my highest selling items?"
"Show me my most profitable items"
"What are my star items?"

# Should use GPT-4 (general advice):
"How do I train my staff?"
"What's the best way to reduce costs?"
```

---

## Example: Menu Engineering Integration

**Supported Queries:**
- "What was the highest selling food item in October?"
- "Show me my most profitable items"
- "What are my star items?"
- "Which items should I remove?"
- "Are any items underpriced?"
- "Where should I place items on my menu?"

**Response Format:**
```
Your top 3 best-selling items are:

1. **Espresso** - 420 orders ($1,470.00 revenue)
2. **Cappuccino** - 380 orders ($1,710.00 revenue)
3. **Spaghetti Carbonara** - 195 orders ($3,313.05 revenue)

💡 Insights:
• These are Star items - high popularity AND profitability!

💬 You can also ask:
• Show me underpriced items
• What are my dog items?
• Show me menu design recommendations
```

---

## Adding to Business Logic Workflow

### New Step 9: Chat Integration (Optional)

**When:** After completing Steps 1-8 of Business Logic Workflow
**Time:** 15-20 minutes
**Prerequisite:** All 3 features implemented and tested

**Tasks:**
1. Add intent mappings in `intent_classifier.py`
2. Add response templates in `response_generator.py`
3. Test natural language queries
4. Verify fallback to GPT-4 works

**Deliverable:** Working chat integration where users can ask natural questions about the feature using real data.

---

## Key Design Principles

### 1. **Fail-Safe Design**
- If Conversational AI fails → Fall through to next handler
- If all handlers fail → Fall back to GPT-4
- Never show error to user, always provide a response

### 2. **Real Data First**
- Conversational AI uses actual restaurant data
- Only use GPT-4 for general questions without data
- This ensures accurate, actionable insights

### 3. **Conversational UX**
- Include insights based on data analysis
- Provide follow-up suggestions
- Use emojis for visual clarity (💡 💬 ⭐ 🐕)

### 4. **Session State**
- Track conversation history (optional)
- Maintain context for follow-ups
- Generate unique session IDs

---

## File Structure

```
apps/
├── chat_assistant/
│   ├── openai_utils.py          # ← Integration point
│   └── views.py                 # Chat API endpoint
│
└── agent_core/
    ├── conversational/
    │   ├── intent_classifier.py  # ← Add intents here
    │   ├── response_generator.py # ← Add templates here
    │   ├── conversation_state.py
    │   └── prompts.py
    │
    └── tasks/
        └── conversational_ai.py  # Main endpoint
```

---

## Troubleshooting

### Conversational AI returns "help" for business queries
- **Problem:** Intent keywords don't match query
- **Solution:** Add more keywords to INTENT_MAP in `intent_classifier.py`

### GPT-4 never gets called
- **Problem:** Conversational AI catching all queries
- **Solution:** Check help detection logic in `handle_conversational_ai()`

### Response shows "Unknown" items
- **Problem:** Field name mismatch in response generator
- **Solution:** Check field names match your API response (e.g., `menu_name` vs `name`)

---

## Success Criteria

✅ **Integration Complete When:**
1. Natural language queries use real restaurant data
2. Responses include insights and suggestions
3. Unrecognized queries gracefully fall back to GPT-4
4. User experience is conversational and helpful
5. No breaking changes to existing functionality

---

**Last Updated:** October 27, 2025
**Status:** Production Ready
