# Menu Engineering Implementation Documentation

**Date:** October 27, 2025
**Status:** ✅ Complete - Production Ready
**Test Coverage:** 6/6 (100%)

---

## Table of Contents

1. [Overview](#overview)
2. [What Was Implemented](#what-was-implemented)
3. [Architecture](#architecture)
4. [Data Flow](#data-flow)
5. [API Endpoints](#api-endpoints)
6. [Business Logic](#business-logic)
7. [Testing](#testing)
8. [How to Use](#how-to-use)
9. [Next Steps](#next-steps)

---

## Overview

This implementation provides comprehensive **Menu Engineering** analysis for restaurant managers using the **Menu Engineering Matrix** methodology. It integrates with the existing `restaurant_inventory_app` to analyze recipes, menu items, and sales data.

### Features Delivered

1. **Product Mix Analysis** - Menu Engineering Matrix classification (Stars, Plowhorses, Puzzles, Dogs)
2. **Menu Pricing Strategy** - Optimal pricing with psychological pricing rules
3. **Menu Design Recommendations** - Golden Triangle placement and visual hierarchy

---

## What Was Implemented

### Core Files Created/Updated

#### 1. Business Logic (`analysis_functions.py`)
**Location:** `/apps/agent_core/tasks/menu/analysis_functions.py`
**Lines:** 1,270
**Purpose:** Core business logic for all 3 menu engineering features

**Functions Implemented:**

**Data Integration Layer:**
- `load_restaurant_data()` - Loads 3 JSON files from restaurant_inventory_app
- `validate_data_integrity()` - Validates FK relationships and data consistency
- `join_menu_data()` - Joins recipes → menu_items → sales using foreign keys

**Menu Engineering Calculations:**
- `classify_quadrant()` - Classifies items into 4 quadrants
- `calculate_thresholds()` - Calculates popularity/profitability thresholds
- `rank_items()` - Ranks items by various metrics
- `calculate_menu_engineering_matrix()` - Main matrix calculation

**Feature 1: Product Mix Analysis:**
- `calculate_product_mix_analysis()` - Complete product mix analysis with quadrant classification

**Feature 2: Menu Pricing Strategy:**
- `calculate_optimal_price()` - Calculates optimal price with psychological pricing
- `analyze_price_positioning()` - Price distribution and gap analysis
- `identify_pricing_opportunities()` - Identifies underpriced/overpriced items
- `calculate_menu_pricing_strategy()` - Complete pricing strategy analysis

**Feature 3: Menu Design Recommendations:**
- `analyze_golden_triangle_placement()` - Identifies items for premium menu positions
- `generate_menu_layout_strategy()` - Category ordering and item placement
- `calculate_menu_design_recommendations()` - Complete design recommendation system

#### 2. API Endpoints

**Product Mix Endpoint:**
- **File:** `/apps/agent_core/tasks/menu/product_mix.py` (225 lines)
- **Endpoint:** `menu/product_mix`
- **Purpose:** Analyzes menu item performance using Menu Engineering Matrix

**Pricing Endpoint:**
- **File:** `/apps/agent_core/tasks/menu/pricing.py` (203 lines)
- **Endpoint:** `menu/pricing`
- **Purpose:** Provides pricing optimization recommendations

**Design Endpoint:**
- **File:** `/apps/agent_core/tasks/menu/design.py` (231 lines)
- **Endpoint:** `menu/design`
- **Purpose:** Generates menu design and layout recommendations

#### 3. Test Suite

**File:** `/test_menu_engineering.py`
**Tests:** 6 comprehensive test cases
**Coverage:** All 3 features plus edge cases

---

## Architecture

### System Integration

```
restaurant_inventory_app/
└── data/
    ├── recipes.json          ← Recipe costs and ingredients
    ├── menu_items.json       ← Menu prices and margins
    └── sales_data.json       ← Monthly sales performance

                    ↓

hospitality_ai_agent/
└── apps/agent_core/tasks/menu/
    ├── analysis_functions.py  ← Core business logic
    ├── product_mix.py        ← API endpoint
    ├── pricing.py            ← API endpoint
    └── design.py             ← API endpoint

                    ↓

            Business Reports
            (HTML + Text)
```

### Data Structure

**recipes.json** (keyed by recipe name):
```json
{
  "Bruschetta al Pomodoro": {
    "recipe_id": "recipe_001",
    "name": "Bruschetta al Pomodoro",
    "category": "Appetizer",
    "total_cost": 1.25,
    "servings": 6,
    ...
  }
}
```

**menu_items.json** (keyed by menu_item_id):
```json
{
  "menu_001": {
    "menu_item_id": "menu_001",
    "recipe_id": "recipe_001",        ← FK to recipes
    "menu_name": "Bruschetta al Pomodoro",
    "menu_price": 8.99,
    "recipe_cost": 1.25,
    "food_cost_percent": 13.9,
    "contribution_margin": 7.74,
    ...
  }
}
```

**sales_data.json** (has sales_records array):
```json
{
  "period": "monthly",
  "month": "2025-10",
  "sales_records": [
    {
      "menu_item_id": "menu_001",    ← FK to menu_items
      "total_units_sold": 180,
      "total_revenue": 1618.20,
      "total_profit": 1393.20,
      ...
    }
  ]
}
```

---

## Data Flow

### End-to-End Flow

1. **API Request** → Django endpoint receives request with parameters
2. **Load Data** → Read 3 JSON files from restaurant_inventory_app
3. **Validate** → Check FK relationships and data integrity
4. **Join** → Merge data using recipe_id and menu_item_id foreign keys
5. **Analyze** → Run feature-specific business logic calculations
6. **Report** → Generate comprehensive business report (HTML + text)
7. **Response** → Return JSON with analysis results and recommendations

### Data Transformation Pipeline

```
Load:
  recipes.json (by name) → Convert to dict keyed by recipe_id
  menu_items.json (by menu_item_id) → Use as-is
  sales_data.json (array) → Convert to dict keyed by menu_item_id

Validate:
  - Check menu_items.recipe_id exists in recipes
  - Check sales.menu_item_id exists in menu_items
  - Optionally validate precalculated metrics

Join:
  For each menu_item:
    1. Get recipe data using recipe_id FK
    2. Get sales data using menu_item_id FK
    3. Combine into unified record

  Result: List of unified menu item records with all data

Analyze:
  - Calculate popularity scores (item units / category avg)
  - Calculate profitability scores (item margin / category avg)
  - Classify into quadrants (Stars/Plowhorses/Puzzles/Dogs)
  - Generate recommendations
```

---

## API Endpoints

### 1. Product Mix Analysis

**Endpoint:** `POST /api/agent/safe/`
**Service:** `menu`
**Subtask:** `product_mix`

**Request:**
```json
{
  "service": "menu",
  "subtask": "product_mix",
  "params": {
    "category_filter": "Main Course"  // Optional
  }
}
```

**Response:**
```json
{
  "service": "menu",
  "subtask": "product_mix",
  "status": "success",
  "data": {
    "menu_engineering_matrix": {
      "stars": [...],
      "plowhorses": [...],
      "puzzles": [...],
      "dogs": [...]
    },
    "quadrant_summary": {
      "stars": {"count": 3, "total_revenue": 6623.93, ...},
      "plowhorses": {"count": 7, ...},
      "puzzles": {"count": 6, ...},
      "dogs": {"count": 4, ...}
    },
    "overall_metrics": {
      "total_menu_items": 20,
      "total_revenue": 29975.35,
      "total_profit": 25087.70,
      ...
    },
    "top_performers": {...},
    "business_report": "...",
    "business_report_html": "..."
  },
  "insights": [
    "Promote your 3 Star items - they generate 22.1% of revenue",
    ...
  ]
}
```

### 2. Menu Pricing Strategy

**Endpoint:** `POST /api/agent/safe/`
**Service:** `menu`
**Subtask:** `pricing`

**Request:**
```json
{
  "service": "menu",
  "subtask": "pricing",
  "params": {
    "target_food_cost": 32.0  // Optional, default: 32%
  }
}
```

**Response:**
```json
{
  "service": "menu",
  "subtask": "pricing",
  "status": "success",
  "data": {
    "pricing_opportunities": {
      "underpriced_items": [...],
      "overpriced_items": [...],
      "well_priced_items": [...],
      "total_revenue_opportunity": 0.0
    },
    "price_positioning": {
      "price_distribution": {...},
      "price_gaps": [...],
      "anchor_opportunities": [...]
    },
    "revenue_impact": {
      "total_opportunity": 0.0,
      "percentage_improvement": 0.0
    },
    "business_report": "...",
    "business_report_html": "..."
  }
}
```

### 3. Menu Design Recommendations

**Endpoint:** `POST /api/agent/safe/`
**Service:** `menu`
**Subtask:** `design`

**Request:**
```json
{
  "service": "menu",
  "subtask": "design",
  "params": {}
}
```

**Response:**
```json
{
  "service": "menu",
  "subtask": "design",
  "status": "success",
  "data": {
    "golden_triangle": [
      {
        "position": "Top Right (Primary)",
        "menu_item": "Grilled Atlantic Salmon",
        "reason": "Highest profit Star item",
        "design_notes": "Use larger font, highlight with box"
      },
      ...
    ],
    "layout_strategy": {
      "section_order": ["Appetizer", "Main Course", "Side", "Dessert"],
      "visual_hierarchy": [...],
      "psychological_techniques": [...]
    },
    "design_principles": {
      "stars_treatment": {...},
      "puzzles_treatment": {...},
      ...
    },
    "implementation_guide": {
      "phase_1_immediate": [...],
      "phase_2_short_term": [...],
      "phase_3_medium_term": [...]
    },
    "business_report": "...",
    "business_report_html": "..."
  }
}
```

---

## Business Logic

### Menu Engineering Matrix

The Menu Engineering Matrix is a 2x2 grid that classifies menu items based on:
- **Popularity** (x-axis): How many units sold vs category average
- **Profitability** (y-axis): Contribution margin vs category average

**Quadrants:**

1. **Stars** (High popularity, High profitability)
   - **Strategy:** Promote heavily, feature prominently
   - **Placement:** Golden Triangle positions
   - **Font:** 18-20pt, bold, highlighted

2. **Plowhorses** (High popularity, Low profitability)
   - **Strategy:** Increase prices slightly, reduce costs
   - **Placement:** Middle of sections
   - **Font:** 14pt, standard

3. **Puzzles** (Low popularity, High profitability)
   - **Strategy:** Increase marketing, better descriptions
   - **Placement:** Near top of sections
   - **Font:** 16pt, descriptive text

4. **Dogs** (Low popularity, Low profitability)
   - **Strategy:** Remove or replace
   - **Placement:** Bottom or remove entirely
   - **Font:** 12pt, minimal

### Scoring Algorithm

```python
# For each category:
category_avg_units = mean(units_sold for all items in category)
category_avg_margin = mean(contribution_margin for all items in category)

# For each item:
popularity_score = item_units_sold / category_avg_units
profitability_score = item_contribution_margin / category_avg_margin

# Classification:
if popularity_score >= 1.0 and profitability_score >= 1.0:
    quadrant = "star"
elif popularity_score >= 1.0 and profitability_score < 1.0:
    quadrant = "plowhorse"
elif popularity_score < 1.0 and profitability_score >= 1.0:
    quadrant = "puzzle"
else:
    quadrant = "dog"
```

### Pricing Strategy

**Optimal Price Calculation:**
```python
optimal_price = recipe_cost / (target_food_cost_percent / 100)

# Apply psychological pricing:
if optimal_price < $10:
    optimal_price = round(optimal_price) - 0.01  # e.g., $8.99
elif optimal_price < $20:
    optimal_price = round(optimal_price) - 0.05  # e.g., $14.95
else:
    optimal_price = round(optimal_price)  # e.g., $25.00

# Ensure minimum markup:
if optimal_price < recipe_cost * 1.5:
    optimal_price = recipe_cost * 1.5  # 33% max food cost
```

**Variance Analysis:**
- **Underpriced:** Current price > 10% below optimal
- **Well-priced:** Current price within ±10% of optimal
- **Overpriced:** Current price > 10% above optimal

### Golden Triangle

The Golden Triangle refers to the areas of a menu that get the most visual attention:

1. **Top Right (Primary)** - Gets most attention, place highest-profit Star
2. **Top Center (Secondary)** - Second-most attention, place second-best Star
3. **Middle Center (Tertiary)** - Third position, place best Puzzle to build awareness

**Eye Tracking Research:** Studies show customers look at these positions first, making them premium real estate for high-margin items.

---

## Testing

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run full test suite
python test_menu_engineering.py
```

### Test Coverage

1. **Product Mix - Happy Path** - Tests complete analysis with default parameters
2. **Pricing Strategy - Happy Path** - Tests pricing recommendations
3. **Design Recommendations - Happy Path** - Tests Golden Triangle and layout
4. **Category Filter** - Tests filtering to specific category (Main Course)
5. **Custom Target Food Cost** - Tests parameter customization (28%)
6. **Business Report Generation** - Tests all 3 features generate reports

### Current Test Results

```
✅ PASS - Product Mix - Happy Path
✅ PASS - Pricing Strategy - Happy Path
✅ PASS - Design Recommendations - Happy Path
✅ PASS - Category Filter
✅ PASS - Custom Target Food Cost
✅ PASS - Business Report Generation

RESULTS: 6/6 tests passed (100.0%)
```

### Sample Test Data

**Test Configuration:**
- 20 menu items (5 Appetizers, 8 Main Course, 3 Beverages, 4 Desserts)
- October 2025 sales data
- Total revenue: $29,975.35
- Total profit: $25,087.70

**Expected Results:**
- 3 Stars, 7 Plowhorses, 6 Puzzles, 4 Dogs
- Top profit item: Grilled Atlantic Salmon
- Golden Triangle: Salmon (Top Right), Carbonara (Top Center), Ravioli (Middle)

---

## How to Use

### For Restaurant Managers

**1. Analyze Product Mix:**
```bash
curl -X POST "http://localhost:8000/api/agent/safe/" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "menu",
    "subtask": "product_mix",
    "params": {}
  }'
```

**2. Optimize Pricing:**
```bash
curl -X POST "http://localhost:8000/api/agent/safe/" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "menu",
    "subtask": "pricing",
    "params": {
      "target_food_cost": 30.0
    }
  }'
```

**3. Get Design Recommendations:**
```bash
curl -X POST "http://localhost:8000/api/agent/safe/" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "menu",
    "subtask": "design",
    "params": {}
  }'
```

### For Developers

**Importing and Using:**

```python
from apps.agent_core.tasks.menu import product_mix, pricing, design

# Run product mix analysis
result, status = product_mix.run({"category_filter": "Main Course"}, None)

# Run pricing strategy
result, status = pricing.run({"target_food_cost": 28.0}, None)

# Run design recommendations
result, status = design.run({}, None)
```

**Direct Function Access:**

```python
from apps.agent_core.tasks.menu.analysis_functions import (
    load_restaurant_data,
    join_menu_data,
    calculate_product_mix_analysis
)

# Load data
recipes, menu_items, sales = load_restaurant_data(
    recipe_path,
    menu_items_path,
    sales_path
)

# Join and analyze
unified_data = join_menu_data(recipes, menu_items, sales)
results = calculate_product_mix_analysis(unified_data)
```

---

## Next Steps

### Immediate Enhancements (Optional)

1. **Historical Analysis** - Compare current month to previous months
2. **Trend Analysis** - Track quadrant changes over time
3. **A/B Testing** - Test menu changes and measure impact
4. **Seasonal Adjustments** - Factor in seasonal menu variations

### Integration Opportunities

1. **Dashboard UI** - Build React frontend for visual analysis
2. **Automated Alerts** - Notify when items change quadrants
3. **Export Reports** - PDF generation for sharing with stakeholders
4. **Recipe Recommendations** - Suggest recipe modifications to improve margins

### Additional Features to Consider

1. **Competitor Analysis** - Compare pricing to local restaurants
2. **Customer Feedback Integration** - Incorporate ratings/reviews
3. **Inventory Optimization** - Link to ingredient availability
4. **Labor Cost Analysis** - Factor in prep time and labor costs

---

## Industry Benchmarks Reference

### Food Cost Percentages
- **Excellent:** < 28%
- **Good:** 28-32%
- **Acceptable:** 32-35%
- **Needs Improvement:** > 35%

### Quadrant Distribution (Ideal Menu)
- **Stars:** 25-35% of items
- **Plowhorses:** 25-35% of items
- **Puzzles:** 15-25% of items
- **Dogs:** < 15% of items

### Menu Design Best Practices
- **Items per Category:** 6-8 maximum (reduce decision fatigue)
- **Font Sizes:** 18-20pt (Stars) → 14pt (Standard) → 12pt (Dogs)
- **Section Order:** Appetizers → Entrees → Sides → Desserts
- **Price Format:** No dollar signs (e.g., "15.99" not "$15.99")

---

## Key Formulas

### Food Cost Percentage
```
food_cost_percent = (recipe_cost / menu_price) × 100
```

### Contribution Margin
```
contribution_margin = menu_price - recipe_cost
```

### Popularity Score
```
popularity_score = item_units_sold / category_avg_units
```

### Profitability Score
```
profitability_score = item_contribution_margin / category_avg_margin
```

---

## Troubleshooting

### Common Issues

**Issue:** "Data file not found" error
**Solution:** Ensure `restaurant_inventory_app/data/` contains all 3 JSON files

**Issue:** "Data integrity errors" about missing FKs
**Solution:** Verify recipe_id and menu_item_id match between files

**Issue:** Empty quadrants in results
**Solution:** Check that sales_data.json has recent sales records

**Issue:** All items classified as "Dogs"
**Solution:** Verify contribution_margin and total_units_sold are populated

---

## Support & Maintenance

### File Locations
- **Business Logic:** `/apps/agent_core/tasks/menu/analysis_functions.py`
- **API Endpoints:** `/apps/agent_core/tasks/menu/{product_mix,pricing,design}.py`
- **Tests:** `/test_menu_engineering.py`
- **Data:** `/restaurant_inventory_app/data/*.json`

### Version Info
- **Implementation Version:** 1.0.0
- **Django Version:** Compatible with existing hospitality_ai_agent
- **Python Version:** 3.12+
- **Dependencies:** Standard Django + existing project dependencies

---

## Credits & References

**Implementation Methodology:**
- Menu Engineering Matrix (Kasavana & Smith, 1982)
- Restaurant industry best practices
- Menu psychology research

**Followed Workflow:**
- `/docs/BUSINESS_LOGIC_WORKFLOW.md` (8-step process)

---

**Document Version:** 1.0
**Last Updated:** October 27, 2025
**Status:** Production Ready ✅
