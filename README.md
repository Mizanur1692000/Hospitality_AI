# Hospitality AI Agent

A comprehensive AI-powered platform for restaurant consulting, providing automated solutions for hospitality management and business intelligence.

## Overview

The Hospitality AI Agent is designed for restaurant consulting companies to automate critical business functions including sales forecasting, labor management, inventory control, and performance analytics.

## Architecture

```text
agent_core/
├── tasks/               # Core business logic modules
│   ├── forecasting.py          # Sales predictions & demand forecasting
│   ├── product_mix.py          # Menu analysis & optimization
│   ├── human_resources.py      # Employee management & HR
│   ├── kpi.py                  # KPI calculations & analytics
│   ├── labor.py                # Staff scheduling & workforce planning
│   ├── liquor.py               # Bar management & cost tracking
│   └── inventory.py            # Stock management & ordering
├── utils/               # Utility functions
│   └── response.py      # Standardized API responses
└── views.py             # API endpoints & routing
```

## Getting Started

### Prerequisites

- Python 3.8+
- Django 4.2+

### Quick Setup

```bash
# Clone the repository
git remote add origin https://github.com/Mizanur1692000/Hospitality_AI.git

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
# Edit .env and set DJANGO_SECRET_KEY

# Run database migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Static Files (Production)

```bash
# Collect static files (do not commit staticfiles/)
python manage.py collectstatic
```

### Packaging

For production deployment, see the deployment section below.

### API Endpoints

#### Unified Agent Endpoint

**POST** `/api/agent/` - Centralized task dispatcher

```json
{
  "task": "task_name",
  "data": {
    // Task-specific data
  }
}
```

Available tasks:

- `forecast` - Sales forecasting
- `hr_retention` - HR retention analysis
- `inventory_variance` - Inventory variance calculation
- `labor_cost` - Labor cost analysis
- `liquor_variance` - Liquor variance analysis
- `kpi_summary` - KPI summary calculations
- `pmix_report` - Product mix analysis

#### Direct Endpoints

**POST** `/api/kpi/summary/` - KPI Summary Analysis

```json
{
  "total_sales": 45000,
  "labor_cost": 12500,
  "food_cost": 11000,
  "hours_worked": 980
}
```

**POST** `/api/pmix/report/` - Product Mix Analysis

```json
{
  "items": [
    {
      "name": "Ribeye",
      "quantity_sold": 55,
      "price": 42,
      "cost": 17
    },
    {
      "name": "Lobster Roll",
      "quantity_sold": 40,
      "price": 32,
      "cost": 13
    }
  ]
}
```

**POST** `/api/liquor/variance/` - Liquor Variance Analysis

```json
{
  "expected_oz": 100,
  "actual_oz": 85
}
```

#### Legacy Endpoints

- `/agent/` - Main API index
- `/agent/status/` - Agent status check
- `/agent/run/` - Tool execution endpoint

## Core Capabilities

### 1. KPI Summary Analysis

Calculates comprehensive restaurant performance metrics:

- **Labor Cost %** - Labor cost as percentage of total sales
- **Food Cost %** - Food cost as percentage of total sales  
- **Prime Cost** - Combined labor and food costs
- **Prime Cost %** - Prime cost as percentage of total sales
- **Sales per Labor Hour** - Revenue generated per hour worked

**Example Response:**

```json
{
  "status": "success",
  "labor_percent": 27.78,
  "food_percent": 24.44,
  "prime_cost": 23500,
  "prime_percent": 52.22,
  "sales_per_labor_hour": 45.92
}
```

### 2. Product Mix Analysis

Analyzes menu item profitability and performance:

- **Contribution Margin** - Price minus cost per item
- **Total Profit** - Contribution margin × quantity sold
- **Item Performance** - Comparative analysis across menu items

**Example Response:**

```json
{
  "status": "success",
  "pmix_report": [
    {
      "name": "Ribeye",
      "quantity_sold": 55,
      "price": 42,
      "cost": 17,
      "contribution_margin": 25,
      "total_profit": 1375
    },
    {
      "name": "Lobster Roll",
      "quantity_sold": 40,
      "price": 32,
      "cost": 13,
      "contribution_margin": 19,
      "total_profit": 760
    }
  ]
}
```

### 3. Sales Forecasting

- Revenue predictions and trend analysis
- Demand pattern recognition
- Seasonal forecasting models

### 4. Human Resources

- Employee management and scheduling
- Performance tracking
- Training program management

### 5. Labor Management

- Staff scheduling optimization
- Workforce planning
- Labor cost analysis

### 6. Liquor Cost Management

- Bar inventory tracking
- Cost control and analysis
- Profit margin optimization

### 7. Inventory Management

- Stock level monitoring
- Automated ordering systems
- Waste reduction strategies

## Testing the API

### Using PowerShell (Recommended)

```powershell
# KPI Summary
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/kpi/summary/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"total_sales": 45000, "labor_cost": 12500, "food_cost": 11000, "hours_worked": 980}'

# Product Mix Report
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/pmix/report/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"items": [{"name": "Ribeye", "quantity_sold": 55, "price": 42, "cost": 17}, {"name": "Lobster Roll", "quantity_sold": 40, "price": 32, "cost": 13}]}'

# Unified Agent (Product Mix)
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/agent/" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"task": "pmix_report", "data": {"items": [{"name": "Ribeye", "quantity_sold": 55, "price": 42, "cost": 17}, {"name": "Lobster Roll", "quantity_sold": 40, "price": 32, "cost": 13}]}}'
```

### Using Python

```python
import requests
import json

# KPI Summary
response = requests.post(
    "http://127.0.0.1:8000/api/kpi/summary/",
    json={
        "total_sales": 45000,
        "labor_cost": 12500,
        "food_cost": 11000,
        "hours_worked": 980
    }
)
print(response.json())
```

## Development

### Project Structure

- Django Backend - RESTful API architecture
- Modular Design - Each business function is a separate module
- Standardized Responses - Consistent API response formatting
- Scalable Architecture - Easy to add new capabilities

### Adding New Tools

1. Create a new file in `agent_core/tasks/`
2. Implement the business logic functions
3. Add routing in `agent_core/views.py`
4. Update URL patterns in `agent_core/urls.py`
5. Add task mapping to the unified agent view

## Roadmap

- [x] KPI Summary Analysis
- [x] Product Mix Analysis  
- [x] Unified Agent API
- [x] Liquor Variance Analysis
- [ ] AI/ML integration for predictive analytics
- [ ] Database models for data persistence
- [ ] Authentication and user management
- [ ] Frontend dashboard interface
- [ ] Real-time data integration
- [ ] Advanced reporting features

## Contributing

This project is designed for restaurant consulting companies. For contributions or partnerships, please contact the development team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built for the hospitality industry by restaurant consultants, for restaurant consultants.
