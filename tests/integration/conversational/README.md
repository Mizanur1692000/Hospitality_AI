# Conversational AI Integration Tests

Integration tests for the Conversational AI natural language interface.

## Overview

The Conversational AI feature provides a natural language interface to all business logic features. Users can ask questions like "What are my highest selling items?" and get conversational responses with insights and suggestions.

## Test Suite

### `test_conversational_ai.py` (Main Test Suite)

**Purpose:** Comprehensive test suite for all conversational AI features

**Coverage:**
- Intent Classification (8 test cases)
- Parameter Extraction (3 test cases)
- Natural Language Queries (Product Mix, Pricing, Design)
- Conversation State Management
- Category Filtering
- Help System

**Tests:** 9 tests (100% passing)

**Run:**
```bash
source ../../../venv/bin/activate
python test_conversational_ai.py
```

**Expected Output:**
```
✅ PASS - Intent Classification
✅ PASS - Parameter Extraction
✅ PASS - Highest Selling Items
✅ PASS - Star Items
✅ PASS - Underpriced Items
✅ PASS - Golden Triangle
✅ PASS - Help Command
✅ PASS - Conversation State
✅ PASS - Category Filter

RESULTS: 9/9 tests passed (100.0%)
```

## Example Queries

### Menu Analysis
- "What are my highest selling items?"
- "Show me my most profitable items"
- "What are my star items?"
- "Which items should I remove?"
- "Show me my menu analysis"

### Pricing
- "Are any items underpriced?"
- "Show me overpriced items"
- "What's my pricing strategy?"
- "Show me pricing opportunities"

### Menu Design
- "Where should I place items on my menu?"
- "Show me menu design recommendations"
- "What is the golden triangle?"

### Category Filtering
- "What are my highest selling appetizers?"
- "Show me underpriced main course items"
- "What desserts are stars?"

## Architecture

### Intent Classification (`intent_classifier.py`)
Maps natural language queries to API endpoints using keyword matching:
- Confidence scoring based on keyword matches
- Parameter extraction (category filters, percentages, etc.)
- Follow-up suggestion generation

### Response Generation (`response_generator.py`)
Formats API responses into conversational text:
- Natural language answers
- Key insights and recommendations
- Smart follow-up suggestions
- Data summaries

### Conversation State (`conversation_state.py`)
Manages conversation context:
- Session tracking
- Turn history
- Last API call caching
- Context for follow-ups

### API Endpoint (`conversational_ai.py`)
Main integration point:
- Receives natural language queries
- Classifies intent and extracts parameters
- Calls appropriate business logic API
- Generates conversational response
- Manages conversation state

## Data Flow

```
User Query
    ↓
Intent Classification
    ↓
Parameter Extraction
    ↓
Call Business Logic API (product_mix, pricing, design)
    ↓
Generate Conversational Response
    ↓
Update Conversation State
    ↓
Return to User with Insights & Suggestions
```

## Example API Call

```bash
curl -X POST "http://localhost:8000/api/agent/conversational" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are my highest selling items?",
    "session_id": "user_123"
  }'
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "answer": "Your top 3 best-selling items are:\n1. Grilled Atlantic Salmon - 245 orders...",
    "insights": [
      "💡 These are Star items - high popularity AND profitability!"
    ],
    "suggestions": [
      "Show me underpriced items",
      "What are my dog items?",
      "Show me menu design recommendations"
    ],
    "session_id": "user_123",
    "conversation_metadata": {
      "turn_count": 1,
      "last_intent": "highest_selling",
      "endpoint_called": "menu/product_mix"
    }
  }
}
```

## Intent Mapping

| User Intent | Keywords | API Endpoint | Extract Path |
|-------------|----------|--------------|--------------|
| **highest_selling** | "highest selling", "top selling", "most popular" | menu/product_mix | top_performers.by_units_sold |
| **most_profitable** | "most profitable", "highest profit", "best margin" | menu/product_mix | top_performers.by_total_profit |
| **stars** | "star items", "stars", "best items" | menu/product_mix | quadrant_summary.stars |
| **dogs** | "dog items", "dogs", "worst items", "remove" | menu/product_mix | quadrant_summary.dogs |
| **underpriced_items** | "underpriced", "too cheap", "raise price" | menu/pricing | pricing_opportunities.underpriced_items |
| **pricing_strategy** | "pricing strategy", "optimize pricing", "pricing opportunities" | menu/pricing | None |
| **golden_triangle** | "where should i place", "placement", "golden triangle" | menu/design | None |

## Conversation Features

### Session Management
- Auto-generated session IDs if not provided
- Session history tracking
- Context retention across turns

### Smart Follow-ups
Based on the current intent and data, the system suggests relevant next questions:
- After menu analysis → Show pricing opportunities
- After pricing → Show menu design
- After design → Show top performers

### Parameter Extraction
Automatically extracts:
- **Category filters**: "appetizers", "main course", "desserts", "beverages"
- **Target food cost**: "28% food cost"
- **Time periods** (planned for future)

## Error Handling

- Low confidence queries → Suggest help
- Invalid parameters → Return error with examples
- API errors → Graceful error messages
- Empty results → Conversational "no results" message

## Future Enhancements

### Planned Features
1. Multi-turn context awareness (reference previous answers)
2. More complex parameter extraction (date ranges, multiple filters)
3. Integration with KPI, HR, and Inventory features
4. Voice interface support
5. Multi-language support

### Integration Points
When new business logic features are added:
1. Add intent mapping in `intent_classifier.py`
2. Add response template in `response_generator.py`
3. Update endpoint map in `conversational_ai.py`
4. Add tests in `test_conversational_ai.py`

## Related Documentation

- [Conversational AI Implementation Plan](../../../docs/CONVERSATIONAL_AI_PLAN.md)
- [Menu Engineering Implementation](../../../docs/MENU_ENGINEERING_IMPLEMENTATION.md)
- [Business Logic Workflow](../../../docs/BUSINESS_LOGIC_WORKFLOW.md)

## Code Locations

| Component | File | Lines |
|-----------|------|-------|
| Intent Classifier | `apps/agent_core/conversational/intent_classifier.py` | 260 |
| Response Generator | `apps/agent_core/conversational/response_generator.py` | 570 |
| Conversation State | `apps/agent_core/conversational/conversation_state.py` | 155 |
| Response Templates | `apps/agent_core/conversational/prompts.py` | 285 |
| API Endpoint | `apps/agent_core/tasks/conversational_ai.py` | 210 |
| Tests | `tests/integration/conversational/test_conversational_ai.py` | 387 |

---

**✅ All tests passing (9/9) - Ready for production**
