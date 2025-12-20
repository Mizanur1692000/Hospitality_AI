# Menu Engineering Questions - Usage Guide

## How It Works for Demo Tomorrow

### User Experience Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Dashboard Chat Interface (Already Exists)                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 💬 Ask me anything about your menu...                    │   │
│  │                                                           │   │
│  │ [Type your question here]                          [Send]│   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  User Types Natural Language Question                           │
│                                                                  │
│  Examples:                                                       │
│  • "Which items have the highest contribution margin?"          │
│  • "What if I increase prices by $0.50?"                        │
│  • "Show me my dog quadrant items"                              │
│  • "What's the impact of 5% inflation?"                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Intent Classifier (Automatic - No Code Changes Needed)         │
│                                                                  │
│  Detects question type and routes to:                           │
│  → menu/questions endpoint                                      │
│  → Loads restaurant data from restaurant_inventory_app          │
│  → Calls appropriate handler (1 of 20 questions)                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  AI Response with Insights                                      │
│                                                                  │
│  📊 Analysis Results:                                           │
│  ─────────────────────────────────────────────────────────      │
│  Top item: Grilled Salmon with 21.2% margin                    │
│                                                                  │
│  💡 Insight:                                                    │
│  Your highest margin items are in the Star quadrant            │
│                                                                  │
│  🎯 Recommendation:                                             │
│  Focus on promoting high-margin items with strong velocity     │
│                                                                  │
│  📈 Top 3 Items:                                                │
│  1. Grilled Salmon - 21.2% margin                              │
│  2. Pork Tenderloin - 17.4% margin                             │
│  3. Mushroom Risotto - 16.0% margin                            │
└─────────────────────────────────────────────────────────────────┘
```

## Direct API Usage (For Testing/Integration)

### Python Example

```python
from backend.consulting_services.menu import menu_questions

# Ask a question
params = {
    "question": "Which menu items have the highest contribution margin?"
}

response, status_code = menu_questions.run(params, None)

# Get the answer
if status_code == 200:
    data = response['data']
    print(f"Question: {data['question']}")
    print(f"Insight: {data['insight']}")
    print(f"Recommendation: {data['recommendation']}")
    print(f"Top Items: {data['top_10_by_margin'][:3]}")
```

### HTTP API Example

```bash
# POST to conversational AI endpoint
curl -X POST http://localhost:8000/api/agent/conversational \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which items have the highest contribution margin?",
    "session_id": "demo_session_123"
  }'
```

### Response Format

```json
{
  "service": "menu",
  "subtask": "questions",
  "status": "success",
  "data": {
    "question": "Which menu items have the highest contribution margin versus their sales volume?",
    "top_10_by_margin": [
      {
        "name": "Grilled Atlantic Salmon",
        "contribution_margin": 21.2,
        "units_sold": 150,
        "total_profit": 3180.00,
        "quadrant": "STAR"
      }
    ],
    "insight": "Top item: Grilled Salmon with 21.2% margin and 150 units sold.",
    "recommendation": "Focus on promoting high-margin items with strong sales velocity (Stars quadrant)."
  }
}
```

## All 20 Questions Available

### Product Mix (8 questions)

1. **Highest Contribution Margin**
   - "Which items have the highest contribution margin?"
   - Returns: Top items by margin with sales volume

2. **Top 5 Profit % (Pareto Analysis)**
   - "What percentage of profit is from the top 5 selling items?"
   - Returns: Pareto analysis showing profit concentration

3. **Dog Quadrant Items**
   - "Which items are in the dog quadrant?"
   - Returns: Low popularity + low profit items to remove

4. **Sales Trends by Category**
   - "How have sales trends changed month over month?"
   - Returns: Category-level trend analysis

5. **Menu Mix Percentages**
   - "What are the menu mix percentages by category?"
   - Returns: Category distribution vs industry benchmarks

6. **Hidden Stars**
   - "Which items have high margins but low sales?"
   - Returns: High-potential items needing visibility

7. **Profit per Labor Minute**
   - "What's the profit per labor minute by category?"
   - Returns: Labor efficiency analysis

8. **Average Check Influence**
   - "How does product mix influence average check size?"
   - Returns: Category contribution to check size

### Pricing (7 questions)

9. **Undervalued Items**
   - "Which items are undervalued?"
   - Returns: Items priced below optimal based on cost %

10. **Price Increase Impact**
    - "What if I increase prices by $0.50?"
    - Returns: Financial impact of flat or % increase

11. **Price Elasticity**
    - "What is the price elasticity for each item?"
    - Returns: Safe price increase ranges by elasticity

12. **Food Cost vs Target**
    - "How do food costs compare to target margins?"
    - Returns: Items above/below target food cost %

13. **Pricing Strategy**
    - "What pricing strategy yields the best results?"
    - Returns: Cost-plus vs competitive vs value-based analysis

14. **Bundling Opportunities**
    - "What bundling opportunities exist?"
    - Returns: High-potential item combinations

15. **Vendor Inflation Impact**
    - "What's the impact of 5% vendor inflation?"
    - Returns: Cost increase and required price adjustments

### Menu Design (5 questions)

16. **Visual Zone Performance**
    - "Which items should be in prime visual zones?"
    - Returns: Golden triangle placement recommendations

17. **Callout Effectiveness**
    - "What callouts should I use on my menu?"
    - Returns: Icon/badge recommendations by item type

18. **Category Sequencing**
    - "Does category sequencing affect guest spend?"
    - Returns: Optimal menu order based on psychology

19. **Design Value Perception**
    - "What design elements increase perceived value?"
    - Returns: Typography, spacing, pricing format recommendations

20. **Limited-Time Offers**
    - "How can I prioritize limited-time offers?"
    - Returns: LTO placement and visual treatment strategies

## Demo Tips for Tomorrow

### Show These Examples

1. **Start Simple**
   ```
   "Which items have the highest contribution margin?"
   ```
   Shows basic product mix analysis

2. **Show Financial Impact**
   ```
   "What if I increase all prices by $0.50?"
   ```
   Demonstrates profit modeling

3. **Show Strategic Insights**
   ```
   "Which items should I place in the golden triangle?"
   ```
   Shows menu psychology expertise

4. **Show Scenario Planning**
   ```
   "What's the impact of 5% vendor inflation?"
   ```
   Demonstrates real-world business planning

### Key Points to Emphasize

✅ **Natural Language** - No technical knowledge required
✅ **Instant Insights** - Answers in seconds using real data
✅ **Actionable Recommendations** - Not just data, but what to DO
✅ **Industry Expertise** - Built-in menu engineering best practices
✅ **Connected to Real Data** - Uses actual restaurant inventory data

## Technical Integration

All questions automatically work through:
- ✅ Dashboard chat interface (apps/dashboard/)
- ✅ Conversational AI endpoint (/api/agent/conversational)
- ✅ Task registry (apps/agent_core/task_registry.py)
- ✅ Intent classification (backend/shared/ai/intent_classifier.py)

**No additional configuration needed - Ready to demo!**

## Testing

Run test suite:
```bash
source venv/bin/activate
python test_menu_questions.py
```

Run demo:
```bash
python demo_menu_questions.py
```

## Data Source

All analysis uses real restaurant data from:
- `/home/jkatz015/repos/restaurant_inventory_app/data/recipes.json`
- `/home/jkatz015/repos/restaurant_inventory_app/data/menu_items.json`
- `/home/jkatz015/repos/restaurant_inventory_app/data/sales_data.json`

Connected via Menu Engineering Matrix calculations in `analysis_functions.py`
