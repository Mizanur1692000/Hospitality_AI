# Menu Engineering Data Source Guide

## Where the Data Comes From

The menu engineering questions pull data from your **restaurant_inventory_app** repository:

```
📁 /home/jkatz015/repos/restaurant_inventory_app/data/
├── 📄 recipes.json         (47 KB - Recipe details, ingredients, costs)
├── 📄 menu_items.json      (11 KB - Menu pricing, margins, quadrants)
└── 📄 sales_data.json      (6.4 KB - Sales volume, revenue, profit)
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Restaurant Inventory App                                       │
│  /home/jkatz015/repos/restaurant_inventory_app/data/           │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ recipes.json │  │menu_items.   │  │sales_data.   │          │
│  │              │  │json          │  │json          │          │
│  │ • Ingredients│  │ • Prices     │  │ • Units sold │          │
│  │ • Prep time  │  │ • Costs      │  │ • Revenue    │          │
│  │ • Recipe cost│  │ • Margins    │  │ • Profit     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Loaded by menu_questions.py
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  analysis_functions.py                                          │
│                                                                  │
│  1. load_restaurant_data() - Reads 3 JSON files                │
│  2. validate_data_integrity() - Checks foreign keys            │
│  3. join_menu_data() - Combines into unified dataset           │
│  4. calculate_menu_engineering_matrix() - Stars/Dogs/etc       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  menu_questions.py (20 question handlers)                       │
│                                                                  │
│  • answer_highest_contribution_margin()                         │
│  • answer_price_increase_impact()                               │
│  • answer_dog_quadrant()                                        │
│  • ... 17 more handlers                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                      User gets answer
```

## What's in Each File

### 1. menu_items.json (11 KB)
**Contains:** Menu pricing and profitability data

```json
{
  "menu_001": {
    "menu_item_id": "menu_001",
    "recipe_id": "recipe_001",
    "menu_name": "Bruschetta al Pomodoro",
    "category": "Appetizer",
    "menu_price": 8.99,              // Selling price
    "recipe_cost": 1.25,              // Cost to make
    "food_cost_percent": 13.9,        // Cost as % of price
    "contribution_margin": 7.74,      // Profit per item
    "quadrant": "STAR",               // Menu Engineering quadrant
    "featured": true,
    "dietary_tags": ["Vegetarian"]
  }
}
```

**Key Fields:**
- `menu_price` - What customers pay
- `recipe_cost` - What it costs to make
- `food_cost_percent` - Cost percentage (target: 28-35%)
- `contribution_margin` - Profit dollars per item
- `quadrant` - STAR, PUZZLE, PLOWHORSE, or DOG

### 2. sales_data.json (6.4 KB)
**Contains:** Sales volume and revenue data

```json
{
  "period": "monthly",
  "month": "2025-10",
  "sales_records": [
    {
      "sale_id": "sale_001",
      "menu_item_id": "menu_001",
      "menu_name": "Bruschetta al Pomodoro",
      "total_units_sold": 180,        // Volume sold
      "avg_daily_sales": 6,            // Daily velocity
      "total_revenue": 1618.20,        // Total sales $
      "total_cost": 225.00,            // Total COGS
      "total_profit": 1393.20,         // Total profit $
      "quadrant": "STAR"
    }
  ]
}
```

**Key Fields:**
- `total_units_sold` - Sales volume (for popularity)
- `total_revenue` - Revenue generated
- `total_profit` - Profit contribution
- `avg_daily_sales` - Sales velocity

### 3. recipes.json (47 KB)
**Contains:** Recipe details, ingredients, and costing

```json
{
  "Bruschetta al Pomodoro": {
    "recipe_id": "recipe_001",
    "name": "Bruschetta al Pomodoro",
    "category": "Appetizer",
    "servings": 6,
    "prep_time": 15,
    "cook_time": 5,
    "ingredients": [
      {
        "product_name": "Tomatoes Roma Fresh",
        "quantity": 1.5,
        "unit": "lb"
      },
      {
        "product_name": "Basil Fresh",
        "quantity": 1,
        "unit": "bunch"
      }
    ],
    "ingredient_costs": [
      {
        "product_name": "Tomatoes Roma Fresh",
        "cost_per_unit": 2.49,
        "total_cost": 3.74
      }
    ],
    "recipe_cost": 1.25,
    "cost_per_serving": 0.21
  }
}
```

**Key Fields:**
- `ingredients` - What goes into the dish
- `ingredient_costs` - Cost breakdown
- `recipe_cost` - Total cost to make
- `prep_time` / `cook_time` - Labor estimates

## How Data is Joined

The system joins these 3 files using **foreign keys**:

```
recipes.json (recipe_id)
     ↓
menu_items.json (recipe_id → menu_item_id)
     ↓
sales_data.json (menu_item_id)
```

Result: **Unified dataset** with everything needed for analysis:
- Menu pricing (from menu_items.json)
- Sales volume (from sales_data.json)
- Recipe details (from recipes.json)

## Configuration

### Current Setup (Default)

Location: `menu_questions.py:929`

```python
default_data_dir = os.getenv(
    "RESTAURANT_DATA_DIR",
    "/home/jkatz015/repos/restaurant_inventory_app/data"
)
```

### How to Use Different Data

**Option 1: Environment Variable (Recommended)**

```bash
# In your shell or .env file
export RESTAURANT_DATA_DIR="/path/to/your/data"
```

**Option 2: Pass Paths in API Call**

```python
params = {
    "question": "Which items have highest margin?",
    "recipe_data_path": "/custom/path/recipes.json",
    "menu_items_path": "/custom/path/menu_items.json",
    "sales_data_path": "/custom/path/sales_data.json"
}

response, status = menu_questions.run(params, None)
```

**Option 3: Modify Default Path**

Edit `menu_questions.py:929` to change the default directory.

## Sample Data Statistics

**Current dataset contains:**
- 47 KB of recipe data
- 11 KB of menu items
- 6.4 KB of sales data
- Sample period: October 2025
- Categories: Appetizers, Entrees, Desserts, etc.

**Data includes real restaurant items:**
- Bruschetta al Pomodoro ($8.99, 180 units sold)
- Asian Lettuce Wraps ($11.99, 65 units sold)
- Loaded Potato Skins ($9.99, 165 units sold)
- Grilled Atlantic Salmon
- Herb-Roasted Pork Tenderloin
- And many more...

## Data Requirements

For the system to work, your data must include:

**menu_items.json:**
- `menu_item_id` (unique)
- `recipe_id` (links to recipes)
- `menu_name`
- `menu_price`
- `recipe_cost`
- `food_cost_percent`
- `contribution_margin`
- `quadrant` (STAR/PUZZLE/PLOWHORSE/DOG)

**sales_data.json:**
- `menu_item_id` (links to menu_items)
- `total_units_sold`
- `total_revenue`
- `total_profit`

**recipes.json:**
- `recipe_id` (unique)
- `name`
- `ingredients` (array)
- `recipe_cost`

## Validation

The system automatically validates:
- ✅ All foreign keys exist
- ✅ No orphaned records
- ✅ Required fields present
- ✅ Numeric values are valid

If validation fails, you'll get clear error messages.

## For Your Demo Tomorrow

**Good news:** You already have a complete, validated dataset with:
- Real restaurant menu items
- Actual cost and pricing data
- Sales volume and revenue
- Menu Engineering quadrant classifications

**No changes needed** - the system is ready to demonstrate with realistic data!

## Want to Use Your Own Data?

If you want to use different data in the future:

1. **Format your data** to match the JSON structure shown above
2. **Place files** in a directory
3. **Set environment variable** or pass paths in API calls
4. **Run validation** to ensure data integrity

The system is flexible and works with any restaurant's data as long as it follows the schema.
