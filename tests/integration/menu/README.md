# Menu Engineering Integration Tests

Integration tests for Menu Engineering features (Product Mix, Pricing, Design).

## Test Files

### `test_menu_engineering.py` (Main Test Suite)
**Purpose:** Comprehensive test suite for all 3 menu engineering features

**Coverage:**
- Product Mix Analysis (Menu Engineering Matrix)
- Pricing Strategy (Optimal pricing & revenue optimization)
- Design Recommendations (Golden Triangle & visual hierarchy)
- Category filtering
- Custom parameters
- Business report generation

**Tests:** 6 tests (100% passing)

**Run:**
```bash
source ../../../venv/bin/activate
python test_menu_engineering.py
```

**Expected Output:**
```
✅ PASS - Product Mix - Happy Path
✅ PASS - Pricing Strategy - Happy Path
✅ PASS - Design Recommendations - Happy Path
✅ PASS - Category Filter
✅ PASS - Custom Target Food Cost
✅ PASS - Business Report Generation

RESULTS: 6/6 tests passed (100.0%)
```

### `test_direct.py` (Quick Debug Test)
**Purpose:** Minimal test for quick debugging during development

**Usage:**
```bash
python test_direct.py
```

### `test_category_filter.py` (Specific Feature Test)
**Purpose:** Isolated test for category filter functionality

**Usage:**
```bash
python test_category_filter.py
```

## Data Requirements

These tests require the `restaurant_inventory_app` data files:
- `/restaurant_inventory_app/data/recipes.json`
- `/restaurant_inventory_app/data/menu_items.json`
- `/restaurant_inventory_app/data/sales_data.json`

## Test Data

**Sample Data Used:**
- 20 menu items (5 Appetizers, 8 Main Course, 3 Beverages, 4 Desserts)
- October 2025 sales data
- $29,975.35 total revenue
- $25,087.70 total profit

## Related Documentation

- [Menu Engineering Implementation](../../../docs/MENU_ENGINEERING_IMPLEMENTATION.md)
- [Quick Start Guide](../../../docs/MENU_ENGINEERING_QUICK_START.md)
- [Business Logic Workflow](../../../docs/BUSINESS_LOGIC_WORKFLOW.md)
