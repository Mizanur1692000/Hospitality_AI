# Codex Agent Instructions: Labor Cost Analysis Business Insight Card

## Task Overview
Create a Labor Cost Analysis business insight card that calculates labor cost percentage and provides actionable insights for restaurant owners.

## What's Already Done
✅ **Safe Architecture**: The safe endpoint `/api/agent/safe/` is ready
✅ **Task Registry**: System for registering new tasks safely
✅ **Common Utilities**: Validation and response formatting functions
✅ **Testing Framework**: Unit tests and integration tests

## What You Need to Create

### 1. Task Function File
**File**: `agent_core/tasks/kpi_labor_cost.py`
**Status**: ✅ Already exists and working

### 2. Frontend Integration
**File**: `frontend/src/components/LaborCostCard.jsx` (or similar)
**Status**: ❌ Needs to be created

### 3. API Integration
**File**: `frontend/src/lib/api.js` (or similar)
**Status**: ❌ Needs to be created

## Step-by-Step Instructions

### Step 1: Verify the Backend Task
The labor cost task already exists at `agent_core/tasks/kpi_labor_cost.py` and is working. Test it:

```bash
# Test the safe endpoint
curl -X POST "http://127.0.0.1:8000/api/agent/safe/" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "kpi",
    "subtask": "labor_cost",
    "params": {
      "total_sales": 10000,
      "labor_cost": 2100
    }
  }'
```

**Expected Response**:
```json
{
  "service": "kpi",
  "subtask": "labor_cost",
  "status": "success",
  "params": {
    "total_sales": 10000,
    "labor_cost": 2100
  },
  "data": {
    "labor_percent": 21.0,
    "total_sales": 10000.0,
    "labor_cost": 2100.0,
    "labor_efficiency": "Good"
  },
  "insights": [
    "Labor % within target range—maintain current staffing levels."
  ],
  "meta": {
    "version": "1.0.0",
    "generated_at": "2025-10-04T13:31:53.558863Z"
  }
}
```

### Step 2: Create Frontend API Client
Create `frontend/src/lib/api.js`:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000/api';

export async function runLaborCostAnalysis(params) {
  const response = await fetch(`${API_BASE_URL}/agent/safe/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      service: 'kpi',
      subtask: 'labor_cost',
      params: params
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}
```

### Step 3: Create the Business Insight Card Component
Create `frontend/src/components/LaborCostCard.jsx`:

```jsx
import React, { useState } from 'react';
import { runLaborCostAnalysis } from '../lib/api';

export default function LaborCostCard() {
  const [formData, setFormData] = useState({
    total_sales: '',
    labor_cost: ''
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params = {
        total_sales: parseFloat(formData.total_sales),
        labor_cost: parseFloat(formData.labor_cost)
      };

      const response = await runLaborCostAnalysis(params);
      setResult(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="business-insight-card">
      <h3>Labor Cost Analysis</h3>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="total_sales">Total Sales ($)</label>
          <input
            type="number"
            id="total_sales"
            name="total_sales"
            value={formData.total_sales}
            onChange={handleInputChange}
            required
            min="0"
            step="0.01"
          />
        </div>

        <div className="form-group">
          <label htmlFor="labor_cost">Labor Cost ($)</label>
          <input
            type="number"
            id="labor_cost"
            name="labor_cost"
            value={formData.labor_cost}
            onChange={handleInputChange}
            required
            min="0"
            step="0.01"
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="analysis-results">
          <h4>Analysis Results</h4>

          <div className="metric">
            <strong>Labor Cost Percentage:</strong> {result.data.labor_percent}%
          </div>

          <div className="metric">
            <strong>Efficiency Rating:</strong> {result.data.labor_efficiency}
          </div>

          {result.insights && result.insights.length > 0 && (
            <div className="insights">
              <h5>Insights:</h5>
              <ul>
                {result.insights.map((insight, index) => (
                  <li key={index}>{insight}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### Step 4: Add Styling
Create `frontend/src/styles/LaborCostCard.css`:

```css
.business-insight-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
  background: #f9f9f9;
}

.business-insight-card h3 {
  color: #333;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}

button {
  background: #007bff;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.analysis-results {
  background: white;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
  border: 1px solid #ddd;
}

.metric {
  margin-bottom: 10px;
  padding: 5px 0;
}

.insights {
  margin-top: 15px;
}

.insights ul {
  margin: 10px 0;
  padding-left: 20px;
}

.insights li {
  margin-bottom: 5px;
}
```

### Step 5: Integration Test
Test the complete flow:

1. **Start the Django server** (if not running):
   ```bash
   python manage.py runserver
   ```

2. **Test the API endpoint**:
   ```bash
   python scripts/test_safe_endpoint.py
   ```

3. **Test the frontend component** (if you have a React app running)

## Success Criteria
✅ **Backend Task**: Returns correct labor cost percentage and insights
✅ **API Endpoint**: Responds with proper JSON format
✅ **Frontend Component**: Accepts input and displays results
✅ **Error Handling**: Handles invalid inputs gracefully
✅ **User Experience**: Clear, intuitive interface

## What NOT to Do
❌ **Don't modify** existing `agent_core/views.py` or `agent_core/urls.py`
❌ **Don't change** the existing `/api/agent/` endpoint
❌ **Don't break** existing functionality
❌ **Don't create** tasks without proper validation

## Next Steps
Once this card is working, you can create additional cards using the same pattern:
- Prime Cost Analysis
- Sales Performance Analysis
- Inventory Variance Analysis
- HR Turnover Analysis
- Beverage Pour Cost Analysis

## Support
If you encounter issues:
1. Check the Django server logs
2. Test the API endpoint directly with curl
3. Verify the task registry has the correct task registered
4. Check browser console for JavaScript errors
