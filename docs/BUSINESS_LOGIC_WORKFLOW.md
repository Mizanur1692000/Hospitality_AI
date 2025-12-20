# Business Logic Implementation Workflow

**Version:** 1.1
**Purpose:** Standardized workflow for implementing comprehensive business logic for each core agent card
**Status:** Draft - To be validated with first implementation (Liquor Cost Analysis)

---

## Overview

This workflow provides a step-by-step process for building out thorough, production-ready business logic for each hospitality management card. After completing the first implementation together, this workflow will be used to independently build out the remaining cards.

---

## 🛡️ APPROVAL PROCESS (CRITICAL)

**IMPORTANT:** Each step requires explicit approval before proceeding to the next step.

### **Approval Gates:**
- ✋ **STOP after each step** and present deliverable for review
- ⏸️ **DO NOT proceed** until user explicitly approves
- 🔄 **If changes needed**, revise and resubmit for approval
- ✅ **Only move forward** after receiving approval

### **Especially Critical:**
- **Step 2 (Data Model Design)** → MUST be approved before ANY code is written
- **Step 3 (Implementation Plan)** → MUST be approved before implementation begins
- **Step 4-5 (Feature Implementation)** → Each feature can be approved individually

### **Approval Format:**
After each step, present:
1. **Step Name & Number**
2. **Deliverable** (as specified in workflow)
3. **Explicit question:** "Ready for your approval to proceed to Step X?"

**If something breaks, we know exactly where it went wrong because each step was validated.**

### **Summary of 8 Approval Checkpoints:**
1. ✅ **After Step 1:** Requirements & feature identification
2. ✅ **After Step 2:** Data model design (CRITICAL - no code until approved)
3. ✅ **After Step 3:** Implementation plan & function signatures
4. ✅ **After Step 4:** Feature 1 complete code
5. ✅ **After Step 5:** Features 2 & 3 complete code
6. ✅ **After Step 6:** Business report generation
7. ✅ **After Step 7:** Main integration function
8. ✅ **After Step 8:** Final testing & validation (COMPLETE)

---

## Core Agents & Cards Inventory

### 1. **Beverage Management**
- [ ] Liquor Cost Analysis (3 features)
- [ ] Bar Inventory (3 features)
- [ ] Beverage Pricing (3 features)

### 2. **KPI Analysis**
- [ ] Labor Cost Analysis
- [ ] Prime Cost Analysis
- [ ] Sales Performance

### 3. **Human Resources**
- [ ] Staff Retention
- [ ] Labor Scheduling
- [ ] Performance Management

### 4. **Menu Engineering**
- [x] Product Mix Analysis ✅ COMPLETE
- [x] Menu Pricing ✅ COMPLETE
- [x] Menu Design ✅ COMPLETE

### 5. **Recipe Management**
- [ ] Recipe Costing
- [ ] Ingredient Optimization
- [ ] Recipe Scaling

### 6. **Strategic Planning**
- [ ] Sales Forecasting
- [ ] Growth Strategy
- [ ] Operational Excellence

### 7. **Inventory Management**
- [ ] Food Inventory Tracking
- [ ] Inventory Variance
- [ ] Reorder Optimization

### 8. **Dashboard/Reporting**
- [ ] Comprehensive Analysis
- [ ] Performance Optimization

---

## Standard Workflow (8 Steps)

### **STEP 1: Discovery & Requirements** ✓

**Objective:** Understand what needs to be built

**Tasks:**
- [ ] Identify the card from the dashboard HTML template
- [ ] Extract the 3 core features listed on the card
- [ ] Read existing business logic file (if any)
- [ ] Document current state vs. desired state
- [ ] Identify industry-specific requirements

**Deliverable:** Requirements document with:
- Card name
- 3 features to implement
- Current implementation status
- Expected inputs/outputs
- Industry benchmarks needed

**Time Estimate:** 15 minutes

---

**🛑 APPROVAL CHECKPOINT #1**
- Present requirements document
- Confirm all 3 features are identified correctly
- Verify understanding of business requirements
- **WAIT FOR APPROVAL BEFORE PROCEEDING TO STEP 2**

---

### **STEP 2: Data Model Design** 📋

**Objective:** Define comprehensive data structures

**Tasks:**
- [ ] Define input parameters (all possible inputs)
- [ ] Define output data structure
- [ ] Identify optional vs. required fields
- [ ] Define validation rules
- [ ] Map to existing schema patterns (see `/apps/agent_core/tasks/common.py`)

**Deliverable:** Data model specification with:
```python
# Input Schema
{
    "required": ["field1", "field2"],
    "optional": {
        "field3": default_value,
        "field4": default_value
    }
}

# Output Schema
{
    "metrics": {},
    "performance": {},
    "recommendations": [],
    "business_report": "",
    "business_report_html": ""
}
```

**Time Estimate:** 20 minutes

---

**🛑 APPROVAL CHECKPOINT #2 (CRITICAL - NO CODE UNTIL APPROVED)**
- Present complete data model specification
- Review input parameters (required vs optional)
- Review output structure
- Confirm validation rules make sense
- **THIS MUST BE APPROVED BEFORE ANY CODE IS WRITTEN**
- **WAIT FOR APPROVAL BEFORE PROCEEDING TO STEP 3**

---

### **STEP 3: Feature Implementation Plan** 🗺️

**Objective:** Break down each feature into specific functions

**Tasks:**
- [ ] Create function signature for Feature 1
- [ ] Create function signature for Feature 2
- [ ] Create function signature for Feature 3
- [ ] Define helper functions needed
- [ ] Identify reusable utilities from existing codebase
- [ ] Plan integration between features

**Deliverable:** Implementation plan with:
- Function names and signatures
- Input/output for each function
- Dependencies between functions
- Order of implementation

**Example:**
```python
# Feature 1: Variance Analysis
def calculate_variance_analysis(expected, actual, cost, size):
    """Calculate comprehensive variance with dollar impact"""
    pass

# Feature 2: Cost Per Ounce
def calculate_cost_per_ounce(bottle_data, drink_recipes, sales_data):
    """Track cost per ounce with profitability analysis"""
    pass

# Feature 3: Waste Identification
def identify_waste_sources(variance, breakage, comps, spillage):
    """Break down waste by category with cost impact"""
    pass
```

**Time Estimate:** 30 minutes

---

**🛑 APPROVAL CHECKPOINT #3**
- Present implementation plan with all function signatures
- Review function breakdown for all 3 features
- Confirm implementation order
- Verify no critical functions are missing
- **WAIT FOR APPROVAL BEFORE PROCEEDING TO STEP 4**

---

### **STEP 4: Implement Feature 1** 💻

**Objective:** Build first feature with full business logic

**Tasks:**
- [ ] Write function implementation
- [ ] Add comprehensive input validation
- [ ] Implement all calculations
- [ ] Add industry benchmarks
- [ ] Generate insights/recommendations
- [ ] Add inline documentation
- [ ] Handle edge cases

**Quality Checklist:**
- [ ] Handles division by zero
- [ ] Validates all inputs (type, range, nulls)
- [ ] Returns standardized error messages
- [ ] Includes industry benchmarks
- [ ] Provides 3-5 actionable recommendations
- [ ] Calculates ALL relevant metrics (not just basics)

**Time Estimate:** 45-60 minutes

---

**🛑 APPROVAL CHECKPOINT #4**
- Present completed Feature 1 code
- Review all calculations and logic
- Verify validation and error handling
- Test Feature 1 with sample data
- Confirm recommendations are actionable
- **WAIT FOR APPROVAL BEFORE PROCEEDING TO STEP 5**

---

### **STEP 5: Implement Features 2 & 3** 💻

**Objective:** Complete remaining features

**Tasks:**
- [ ] Implement Feature 2 following same pattern as Feature 1
- [ ] Implement Feature 3 following same pattern as Feature 1
- [ ] Ensure consistency across all 3 features
- [ ] Create integration function that ties all 3 together

**Quality Checklist:** (Same as Step 4 for each feature)

**Time Estimate:** 90-120 minutes (both features)

---

**🛑 APPROVAL CHECKPOINT #5**
- Present completed Features 2 & 3 code
- Review calculations and logic for both features
- Verify all 3 features work together
- Test with sample data
- Confirm consistency across features
- **WAIT FOR APPROVAL BEFORE PROCEEDING TO STEP 6**

---

### **STEP 6: Business Report Generation** 📊

**Objective:** Create comprehensive, formatted report output

**Tasks:**
- [ ] Use existing `format_business_report()` from kpi_utils.py
- [ ] Compile metrics from all 3 features
- [ ] Generate performance rating
- [ ] Create recommendation list (prioritized)
- [ ] Add industry benchmarks section
- [ ] Generate both HTML and text versions

**Deliverable:** Full business report with:
- Executive summary
- Key metrics (from all 3 features)
- Performance rating
- Industry benchmarks
- Strategic recommendations
- Additional insights

**Time Estimate:** 30 minutes

---

**🛑 APPROVAL CHECKPOINT #6**
- Present business report output (both HTML and text)
- Review executive summary and metrics
- Verify performance rating logic
- Confirm recommendations are prioritized correctly
- Test report rendering
- **WAIT FOR APPROVAL BEFORE PROCEEDING TO STEP 7**

---

### **STEP 7: Main Integration Function** 🔗

**Objective:** Wire everything together in main `run()` function

**Tasks:**
- [ ] Update or create main `run(params, file_bytes)` function
- [ ] Add parameter extraction with defaults
- [ ] Add validation using `validate_positive_numbers()`
- [ ] Call all 3 feature functions
- [ ] Aggregate results
- [ ] Generate business report
- [ ] Return success_payload with all data
- [ ] Add comprehensive error handling

**Pattern to Follow:**
```python
def run(params: dict, file_bytes: bytes | None = None) -> tuple[dict, int]:
    service, subtask = "service_name", "task_name"

    try:
        # 1. Extract & validate params
        # 2. Call Feature 1 function
        # 3. Call Feature 2 function
        # 4. Call Feature 3 function
        # 5. Generate business report
        # 6. Return success_payload
    except Exception as e:
        return error_payload(service, subtask, str(e))
```

**Time Estimate:** 30 minutes

---

**🛑 APPROVAL CHECKPOINT #7**
- Present complete `run()` function code
- Review parameter extraction and defaults
- Verify error handling is comprehensive
- Test integration with sample API call
- Confirm success_payload format is correct
- **WAIT FOR APPROVAL BEFORE PROCEEDING TO STEP 8**

---

### **STEP 8: Testing & Validation** ✅

**Objective:** Ensure everything works correctly

**Tasks:**
- [ ] Test with valid inputs (happy path)
- [ ] Test with edge cases (zeros, very large numbers)
- [ ] Test with invalid inputs (negative, null, wrong types)
- [ ] Test with minimal inputs (only required fields)
- [ ] Test with all optional inputs
- [ ] Verify output format matches schema
- [ ] Verify recommendations are actionable
- [ ] Verify HTML report renders correctly

**Test Data Template:**
```python
# Happy path
test_valid = {
    "field1": 1000,
    "field2": 950,
    # ... all required fields
}

# Edge cases
test_edge = {
    "field1": 0,  # zero value
    "field2": 999999,  # very large
}

# Invalid
test_invalid = {
    "field1": -100,  # negative
    "field2": "not_a_number",  # wrong type
}
```

**Time Estimate:** 45 minutes

---

**🛑 APPROVAL CHECKPOINT #8 (FINAL)**
- Present all test results
- Demonstrate happy path test
- Demonstrate edge case handling
- Demonstrate error handling
- Show complete output with business report
- Verify all quality standards met
- **FINAL APPROVAL = CARD COMPLETE**

---

## Quality Standards

### **Code Quality**
- [ ] Follows existing code patterns from kpi_utils.py
- [ ] Uses type hints for all functions
- [ ] Includes docstrings with Args/Returns
- [ ] No hardcoded values (use constants or parameters)
- [ ] DRY principle (no duplicate logic)

### **Business Logic Quality**
- [ ] All calculations are accurate
- [ ] Industry benchmarks are realistic
- [ ] Recommendations are specific and actionable
- [ ] Handles restaurant industry edge cases
- [ ] Provides value to hospitality managers

### **Error Handling**
- [ ] All possible errors caught
- [ ] Error messages are clear and actionable
- [ ] No unhandled exceptions
- [ ] Graceful degradation where possible

---

## File Structure Reference

```
apps/agent_core/
├── tasks/
│   ├── common.py                    # Common utilities (use these!)
│   ├── kpi_utils.py                 # KPI calculations & report formatting
│   │
│   ├── beverage/
│   │   ├── liquor_cost.py          # ← Liquor Cost Analysis (FIRST)
│   │   ├── inventory.py            # ← Bar Inventory
│   │   └── pricing.py              # ← Beverage Pricing
│   │
│   ├── kpi/
│   │   ├── labor_cost.py
│   │   ├── prime_cost.py
│   │   └── sales_performance.py
│   │
│   ├── hr/
│   │   ├── staff_retention.py
│   │   ├── labor_scheduling.py
│   │   └── performance_management.py
│   │
│   ├── menu/
│   │   ├── product_mix.py
│   │   ├── pricing.py
│   │   └── design.py
│   │
│   ├── recipe/
│   │   ├── costing.py
│   │   ├── scaling.py
│   │   └── (ingredient_optimization in menu/)
│   │
│   ├── strategy/
│   │   ├── sales_forecasting.py
│   │   ├── growth.py
│   │   └── operational.py
│   │
│   └── inventory/
│       ├── tracking.py
│       └── liquor.py
```

---

## Utility Functions Reference

### **From `common.py`:**
```python
success_payload(service, subtask, params, data, insights)
error_payload(service, subtask, message, code)
require(body, fields)
validate_positive_numbers(data, fields)
safe_float(value, field_name)
```

### **From `kpi_utils.py`:**
```python
format_business_report(analysis_type, metrics, performance, recommendations, benchmarks, additional_data)
```

---

## Industry Benchmarks Reference

### **Liquor/Beverage:**
- Liquor Cost %: 18-22% (Excellent: <18%, Good: 18-22%, Acceptable: 22-25%)
- Variance Tolerance: ±5% (Excellent), ±10% (Acceptable)
- Waste %: <3% (Excellent), 3-5% (Acceptable), >5% (Needs Improvement)
- Pour Cost: 15-20% per drink

### **Labor:**
- Labor Cost %: <25% (Excellent), 25-30% (Good), 30-35% (Acceptable)
- Sales per Labor Hour: >$100 (Excellent), $75-100 (Good), $50-75 (Acceptable)

### **Food Cost:**
- Food Cost %: 28-32% (Full Service), 25-30% (Quick Service)
- Prime Cost %: <60% (Excellent), 60-65% (Acceptable)

### **Inventory:**
- Inventory Turnover: 4-6x per month (perishables), 1-2x (dry goods)
- Days of Stock: 3-7 days (optimal for most items)

---

## Success Criteria

**A business logic implementation is complete when:**

1. ✅ All 3 features are fully implemented
2. ✅ All calculations are accurate and comprehensive
3. ✅ Industry benchmarks are included
4. ✅ Recommendations are specific and actionable
5. ✅ Business report (HTML + text) is generated
6. ✅ All test cases pass
7. ✅ Error handling is comprehensive
8. ✅ Code follows existing patterns
9. ✅ Documentation is complete
10. ✅ Ready for production use by hospitality managers

---

## Validation Checklist (Use for First Implementation)

After completing Liquor Cost Analysis, verify:

- [ ] Can I execute this workflow independently for other cards?
- [ ] Are the instructions clear and unambiguous?
- [ ] Are there any gaps in the workflow?
- [ ] Do the time estimates seem accurate?
- [ ] Is the quality bar high enough?
- [ ] Are there any missing standards or patterns?

---

## Next Steps

1. **Execute this workflow together** for Liquor Cost Analysis
2. **Refine workflow** based on what we learn
3. **Validate completeness** - confirm first card meets all criteria
4. **Document any changes** to workflow
5. **Execute independently** for remaining cards using validated workflow

---

## Notes & Lessons Learned

_(To be filled in after first implementation)_

-
-
-

---

**End of Workflow Document**
