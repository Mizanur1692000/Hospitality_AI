# Hospitality AI Platform

An AI-driven consulting platform for restaurants. It unifies KPI analytics, Menu Engineering, and Beverage Management behind a single agent API and modern dashboard flows.

## Highlights
- Unified agent endpoint for JSON and CSV tasks
- Rich HTML business reports with badges, benchmarks, and tracking sections
- Frontend pages for Beverage Management and Menu Engineering
- Extensible task registry and Pydantic schemas

## Quick Start
- Python 3.10+ and Django 4.2+
- Install: `pip install -r requirements.txt`
- Migrate: `python manage.py migrate`
- Run: `python manage.py runserver`

Environment: see [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md). Deployment: see [docs/AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md).

## Key Flows
- Beverage Management: Liquor Cost Analysis, Bar Inventory, Beverage Pricing. Page: [apps/dashboard/templates/dashboard/beverage.html](apps/dashboard/templates/dashboard/beverage.html)
- Menu Engineering: Product Mix, Pricing Strategy, Item Optimization. See guides: [docs/MENU_ENGINEERING_IMPLEMENTATION.md](docs/MENU_ENGINEERING_IMPLEMENTATION.md), [docs/MENU_QUESTIONS_USAGE.md](docs/MENU_QUESTIONS_USAGE.md)
- KPI Dashboard: Prime, Labor, Food, Sales performance. Core functions: [backend/consulting_services/kpi/kpi_utils.py](backend/consulting_services/kpi/kpi_utils.py)

## Unified API
Endpoint: `/api/agent/` (POST)

Supports:
- JSON payloads: `{ "task": "<task_name>", "payload": { ... } }`
- Multipart CSV: `FormData(task=<task_name>, file=<csv>)`

Common Response:
- `status`: `success|error`
- `analysis_type`: e.g., `Liquor Cost Analysis`
- `business_report_html`: full HTML report (preferred for rendering)
- `business_report`: plain text fallback
- `metrics|summary|performance|recommendations|industry_benchmarks`: structured data

### Task Catalog (examples)
- Beverage: `liquor_cost_analysis`, `bar_inventory_analysis`, `beverage_pricing_analysis`
- KPI: `kpi_summary`, `labor_cost_analysis`, `prime_cost_analysis`, `sales_performance_analysis`, `food_cost_analysis`
- Menu: `product_mix_analysis`, `menu_pricing_strategy`, `item_optimization`

Registry and schemas: [apps/agent_core/task_map.py](apps/agent_core/task_map.py), [apps/agent_core/task_registry.py](apps/agent_core/task_registry.py)

## Endpoints & Logic
- **`/api/agent/`**: Unified POST endpoint for tasks.
  - Logic: Validates JSON payloads via Pydantic schemas; enforces entitlement for KPI tasks using header `X-KPI-Analysis-Entitled`; routes tasks defined in [apps/agent_core/task_map.py](apps/agent_core/task_map.py); supports multipart CSV uploads and dispatches to processors.
  - JSON flow: `{ task, payload }` → schema → runner function → dict response.
  - CSV flow: `FormData(task, file)` → processor chosen per `task`; for beverage tasks, auto-detection attempts based on headers.
- **`/api/agent/safe/`**: Safe POST endpoint for business insight cards.
  - Logic: `{ service, subtask, params }` → executes registered tasks in [apps/agent_core/task_registry.py](apps/agent_core/task_registry.py); optional `file` bytes; isolates card tasks without affecting unified endpoint.
- **`/api/status/`** and **`/api/`**: Index and status.
  - Logic: Index lists available tasks (filtered by entitlement). Status returns operational health.

Entitlement header:
- Name: `X-KPI-Analysis-Entitled`
- Truthy values: `1`, `true`, `yes`, `allowed`

Core routing code: [agent view](apps/agent_core/views.py), [safe view](apps/agent_core/views_safe.py).

## Request Examples

### Liquor Cost (JSON)
```json
{
  "task": "liquor_cost_analysis",
  "payload": {
    "expected_oz": 1500,
    "actual_oz": 1650,
    "liquor_cost": 3500,
    "total_sales": 15000,
    "bottle_cost": 25,
    "bottle_size_oz": 25,
    "target_cost_percentage": 20
  }
}
```

### Bar Inventory (CSV)
- Required columns: `current_stock,reorder_point,monthly_usage,inventory_value`
- Optional: `lead_time_days,safety_stock,item_cost,target_turnover`

### Beverage Pricing (JSON)
```json
{
  "task": "beverage_pricing_analysis",
  "payload": {
    "drink_price": 12,
    "cost_per_drink": 3,
    "sales_volume": 1800,
    "competitor_price": 11,
    "target_margin": 75,
    "market_position": "premium",
    "elasticity_factor": 1.5
  }
}
```

### KPI Summary (CSV)
- Required columns: `date,sales,labor_cost,food_cost,labor_hours`
- Auto-mapping applies for column variants (e.g., `revenue`, `wages`, `cogs`). See function: [process_kpi_csv_data](backend/consulting_services/kpi/kpi_utils.py#L1306).

## CSV Specifications

Each CSV task expects specific columns; optional fields enhance analysis and benchmarks.

- **Product Mix** (`task=product_mix`) → [legacy_product_mix](backend/consulting_services/menu/legacy_product_mix.py)
  - Required: `item_name`, `quantity_sold`, `price`
  - Optional: `cost`, `food_cost_pct`, `contribution_margin_pct`, `revenue`, `profit`, `category`
  - Auto-mapping: Accepts `product_name`/`product name`, `quantity`, `unit_price` and generated analysis formats (`Menu Item`, `Units Sold`, `Price`, etc.).

- **Menu Pricing Strategy** (`task=pricing`) → [pricing_csv_processor](backend/consulting_services/menu/pricing_csv_processor.py)
  - Required: `item_name`, `item_price`, `item_cost`, `competitor_price`
  - Optional: `target_food_cost_percent`, `category`
  - Logic: Computes food cost %, competitor gap, alignment rating and recommendations; returns `business_report_html`.

- **Menu Design (Matrix)** (`task=design`) → [design_csv_processor](backend/consulting_services/menu/design_csv_processor.py)
  - Required: `item_name`, `quantity_sold`, `price`
  - Optional: `cost`, `category`, `description`
  - Logic: Classifies into `star|plowhorse|puzzle|dog`; builds Golden Triangle suggestions; returns `business_report_html`.

- **Item Optimization** (`task=optimization`) → [optimization_csv_processor](backend/consulting_services/menu/optimization_csv_processor.py)
  - Required: `item_name`, `quantity_sold`
  - Optional: `item_cost`, `portion_size`, `portion_cost`, `description`, `waste_percent`, `price`, `category`
  - Logic: Detects high waste, high cost/low sales, missing descriptions; returns `business_report_html`.

- **KPI Analysis** (`task=kpi_analysis`) → [process_kpi_csv_data](backend/consulting_services/kpi/kpi_utils.py)
  - Required: `date`, `sales`, `labor_cost`, `food_cost`, `labor_hours`
  - Optional: Variants auto-mapped (e.g., `revenue`, `wages`, `cogs`)
  - Logic: Generates daily KPIs, averages, trend comparisons, and AI insights; returns `business_report_html`.

- **HR CSV** (`task=hr_retention|hr_scheduling|hr_performance|hr_analysis`) → `process_hr_csv_data`
  - Required: varies by analysis; auto-detection for `hr_analysis`
  - Logic: Validates columns and returns targeted HR insights.

- **Cost CSV** (`task=labor_cost|food_cost|prime_cost|liquor_cost|beverage_cost|liquor_variance|cost_analysis`) → `process_cost_csv_data`
  - Required: varies; `cost_analysis` auto-detects by headers
  - Logic: Computes cost KPIs; returns structured metrics.

- **Recipe Management** (`task=recipe_management`) → `analysis_functions.process_recipe_csv_data`
  - Required: `recipe_name`, `ingredient_cost`, `portion_cost`, `recipe_price`, `servings`, `labor_cost`
  - Logic: Calculates recipe costing and scaling insights.

- Beverage Management CSVs (Beverage page uses these tasks and auto-detection):
  - **Liquor Cost Analysis** (`task=liquor_cost_analysis`) → [liquor_cost_csv_processor](backend/consulting_services/beverage/liquor_cost_csv_processor.py)
    - Required: `expected_oz`, `actual_oz`, `liquor_cost`, `total_sales`
    - Optional: `bottle_cost`, `bottle_size_oz`, `target_cost_percentage`
    - Logic: Computes theoretical vs actual, waste %, cost %, status; returns `business_report_html`.
  - **Bar Inventory** (`task=bar_inventory_analysis`) → [bar_inventory_csv_processor](backend/consulting_services/beverage/bar_inventory_csv_processor.py)
    - Required: `current_stock`, `reorder_point`, `monthly_usage`, `inventory_value`
    - Optional: `lead_time_days`, `safety_stock`, `item_cost`, `target_turnover`
    - Logic: Computes reorder triggers, turnover, valuation; returns `business_report_html`.
  - **Beverage Pricing** (`task=beverage_pricing_analysis`) → [beverage_pricing_csv_processor](backend/consulting_services/beverage/beverage_pricing_csv_processor.py)
    - Required: `drink_price`, `cost_per_drink`, `sales_volume`, `competitor_price`
    - Optional: `target_margin`, `market_position`, `elasticity_factor`
    - Logic: Computes margins, competitive gap, elasticity-adjusted revenue; returns `business_report_html`.

## Backend Logic Reference
- KPI runners: `calculate_kpi_summary`, `calculate_labor_cost_analysis`, `calculate_prime_cost_analysis`, `calculate_sales_performance_analysis` in [kpi_utils.py](backend/consulting_services/kpi/kpi_utils.py)
- Beverage runners: `calculate_liquor_cost_analysis`, `calculate_inventory_analysis`, `calculate_pricing_analysis` in [kpi_utils.py](backend/consulting_services/kpi/kpi_utils.py)
- Menu runners: `generate_pmix_report` in [legacy_product_mix.py](backend/consulting_services/menu/legacy_product_mix.py)
- Task mapping: see [apps/agent_core/task_map.py](apps/agent_core/task_map.py) for schemas and entitlement flags.

## Frontend Integration
- Pages render `business_report_html` directly to avoid duplicate headers.
- Beverage chat routes JSON/CSV to `/api/agent/`; fallback uses `/chat/api/`.
- Parser supports comma-separated labeled inputs for quick analysis.

Core UI file: [apps/dashboard/templates/dashboard/beverage.html](apps/dashboard/templates/dashboard/beverage.html)

## Chat API
Endpoint: `/chat/api/` (POST)
- Parameters: `message`, optional `context` (e.g., `beverage`)
- Sanitizes model output to plain text (see [apps/chat_assistant/openai_utils.py](apps/chat_assistant/openai_utils.py))

## Error Handling
- CSV validation returns `status:error`, `message`, `help`, and `expected_format` when columns are missing
- Beverage CSV auto-fallback attempts to match the correct processor by headers
- Backend formatter returns `business_report_html` with performance badge and tracking sections

## Data Models & Utilities
- KPI utilities and HTML formatter: [backend/consulting_services/kpi/kpi_utils.py](backend/consulting_services/kpi/kpi_utils.py)
- Beverage CSV processors:
  - Liquor: [backend/consulting_services/beverage/liquor_cost_csv_processor.py](backend/consulting_services/beverage/liquor_cost_csv_processor.py)
  - Inventory: [backend/consulting_services/beverage/bar_inventory_csv_processor.py](backend/consulting_services/beverage/bar_inventory_csv_processor.py)
  - Pricing: [backend/consulting_services/beverage/beverage_pricing_csv_processor.py](backend/consulting_services/beverage/beverage_pricing_csv_processor.py)

## Postman Collections
- API: [docs/Hospitality_AI_API.postman_collection.json](docs/Hospitality_AI_API.postman_collection.json)
- Dashboard flows: [docs/Hospitality_AI_Dashboard.postman_collection.json](docs/Hospitality_AI_Dashboard.postman_collection.json)

## Testing
- Run unit/integration tests under [tests/](tests)
- Example fixtures and flows in [tests/integration/](tests/integration)

## Deployment
- See [docs/PRODUCTION_READINESS_REPORT.md](docs/PRODUCTION_READINESS_REPORT.md) and [docs/PRODUCTION_CHECKLIST.md](docs/PRODUCTION_CHECKLIST.md)

## Contributing
- Tasks map and registries allow new analyses to be added with minimal wiring.
- Prefer returning `business_report_html` for consistent frontend rendering.

## License
MIT. See [LICENSE](LICENSE).
