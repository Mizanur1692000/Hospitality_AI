# 🗂️ File System Reorganization Plan

## Overview
This document outlines the complete plan to reorganize the Hospitality AI Agent project into a clean, maintainable structure.

## Target Structure
```
hospitality_ai_agent/
├── 📁 config/                          # Django configuration
├── 📁 apps/                            # All Django applications
│   ├── 📁 agent_core/                  # Core AI agent business logic
│   ├── 📁 chat_assistant/              # Chat UI & OpenAI integration
│   └── 📁 dashboard/                   # Dashboard views & templates
├── 📁 infrastructure/                  # DevOps & deployment scripts
├── 📁 static/                          # Static files
├── 📁 templates/                       # Django templates
├── 📁 data/                            # Data files
├── 📁 assets/                          # Assets (QR codes, images)
├── 📁 tests/                           # Test files
├── 📁 docs/                            # Documentation
├── 📁 archive/                         # Backup files
└── Root level files (manage.py, requirements.txt, etc.)
```

---

## 📋 Phase-by-Phase Execution Plan

### ✅ PHASE 1: Create New Structure (COMPLETED)

- [x] Created config/ directory with Django settings
- [x] Created apps/ directory structure
- [x] Created infrastructure/, assets/, tests/, data/, docs/, archive/ directories
- [x] Created task subdirectories (kpi/, hr/, menu/, recipe/, beverage/, inventory/, strategy/)
- [x] Updated manage.py to use config.settings
- [x] Created README.md files for each major directory

### 📦 PHASE 2: Move Django Apps to apps/ Directory

#### Step 2.1: Move agent_core to apps/agent_core/

**Files to move:**

- `agent_core/` → `apps/agent_core/`

**Import changes required:**

1. **config/settings.py** - Update INSTALLED_APPS:
   ```python
   # OLD:
   "agent_core",
   
   # NEW:
   "apps.agent_core",
   ```

2. **config/settings.py** - Update MIDDLEWARE:
   ```python
   # OLD:
   "agent_core.middleware.NgrokHostMiddleware",
   
   # NEW:
   "apps.agent_core.middleware.NgrokHostMiddleware",
   ```

3. **config/urls.py** - No change needed (uses string path)

4. **agent_core/*.py** files - Update imports from tasks:
   ```python
   # OLD:
   from agent_core.tasks import X
   from ..tasks import X
   
   # NEW:
   from apps.agent_core.tasks import X
   from ..tasks import X  # This remains the same (relative import)
   ```

#### Step 2.2: Move chat_assistant to apps/chat_assistant/

**Files to move:**

- `chat_assistant/` → `apps/chat_assistant/`

**Import changes required:**

1. **config/settings.py** - Update INSTALLED_APPS:
   ```python
   # OLD:
   "chat_assistant",
   
   # NEW:
   "apps.chat_assistant",
   ```

2. **chat_assistant/*.py** files - Update internal imports:
   ```python
   # OLD:
   from chat_assistant.openai_utils import X
   
   # NEW:
   from apps.chat_assistant.openai_utils import X
   ```

#### Step 2.3: Move dashboard to apps/dashboard/

**Files to move:**

- `dashboard/` → `apps/dashboard/`

**Import changes required:**

1. **config/settings.py** - Update INSTALLED_APPS:
   ```python
   # OLD:
   "dashboard",
   
   # NEW:
   "apps.dashboard",
   ```

---

### 📂 PHASE 3: Reorganize Task Files into Subdirectories

#### Task File Mapping:

**KPI Tasks** → `apps/agent_core/tasks/kpi/`:

- `kpi_labor_cost.py` → `apps/agent_core/tasks/kpi/labor_cost.py`
- `kpi_prime_cost.py` → `apps/agent_core/tasks/kpi/prime_cost.py`
- `kpi_sales_performance.py` → `apps/agent_core/tasks/kpi/sales_performance.py`
- `kpi_dashboard_analysis_functions.py` → `apps/agent_core/tasks/kpi/dashboard_analysis.py`
- `kpi.py` → Keep as utility module

**HR Tasks** → `apps/agent_core/tasks/hr/`:

- `hr_labor_scheduling.py` → `apps/agent_core/tasks/hr/labor_scheduling.py`
- `hr_performance_management.py` → `apps/agent_core/tasks/hr/performance_management.py`
- `hr_staff_retention.py` → `apps/agent_core/tasks/hr/staff_retention.py`
- `human_resources.py` → Keep as main module

**Menu Tasks** → `apps/agent_core/tasks/menu/`:

- `menu_design.py` → `apps/agent_core/tasks/menu/design.py`
- `menu_pricing.py` → `apps/agent_core/tasks/menu/pricing.py`
- `menu_product_mix.py` → `apps/agent_core/tasks/menu/product_mix.py`
- `menu_analysis_functions.py` → `apps/agent_core/tasks/menu/analysis_functions.py`
- `product_mix.py` → Consolidate with menu_product_mix.py

**Recipe Tasks** → `apps/agent_core/tasks/recipe/`:

- `recipe_costing.py` → `apps/agent_core/tasks/recipe/costing.py`
- `recipe_scaling.py` → `apps/agent_core/tasks/recipe/scaling.py`
- `recipe_analysis_functions.py` → `apps/agent_core/tasks/recipe/analysis_functions.py`

**Beverage Tasks** → `apps/agent_core/tasks/beverage/`:

- `beverage_inventory.py` → `apps/agent_core/tasks/beverage/inventory.py`
- `beverage_liquor_cost.py` → `apps/agent_core/tasks/beverage/liquor_cost.py`
- `beverage_pricing.py` → `apps/agent_core/tasks/beverage/pricing.py`

**Inventory Tasks** → `apps/agent_core/tasks/inventory/`:

- `inventory.py` → `apps/agent_core/tasks/inventory/tracking.py`
- `liquor.py` → `apps/agent_core/tasks/inventory/liquor.py`

**Strategy Tasks** → `apps/agent_core/tasks/strategy/`:

- `forecasting.py` → `apps/agent_core/tasks/strategy/forecasting.py`
- `growth_strategy.py` → `apps/agent_core/tasks/strategy/growth.py`
- `operational_excellence.py` → `apps/agent_core/tasks/strategy/operational.py`
- `comprehensive_analysis.py` → `apps/agent_core/tasks/strategy/comprehensive.py`
- `sales_forecasting.py` → Merge with forecasting.py

**Other files:**

- `common.py` → Keep in `apps/agent_core/tasks/` (root level)
- `labor.py` → Move to `apps/agent_core/tasks/hr/` or consolidate
- `ingredient_optimization.py` → Move to `apps/agent_core/tasks/menu/`
- `performance_optimization.py` → Move to `apps/agent_core/tasks/hr/`

#### Import Updates Needed:

**In each moved task file**, update imports from common:
```python
# OLD:
from .common import success_payload, error_payload

# NEW:
from ...common import success_payload, error_payload  # One more level up
```

**Update apps/agent_core/views.py** to reference new paths:
```python
# OLD:
from agent_core.tasks.kpi_labor_cost import run as labor_run

# NEW:
from apps.agent_core.tasks.kpi.labor_cost import run as labor_run
```

**Update task_map.py and task_registry.py** with new paths.

---

### 🗄️ PHASE 4: Move Infrastructure Files

#### Scripts to Infrastructure:

**Deployment Scripts** → `infrastructure/deployment/`:

- `scripts/start_app.py` → `infrastructure/deployment/start_app.py`
- `scripts/start_with_auto_hosts.py` → `infrastructure/deployment/start_with_auto_hosts.py`

**Ngrok Scripts** → `infrastructure/ngrok/`:

- `scripts/quick_ngrok_setup.py` → `infrastructure/ngrok/setup.py`
- `scripts/setup_ngrok.py` → Delete (duplicate)
- `scripts/simple_ngrok.py` → `infrastructure/ngrok/simple.py`
- `scripts/smart_ngrok.py` → `infrastructure/ngrok/smart.py`
- `scripts/stable_ngrok_simple.py` → `infrastructure/ngrok/stable_simple.py`
- `scripts/stable_ngrok.py` → `infrastructure/ngrok/stable.py`
- `scripts/start_ngrok.py` → `infrastructure/ngrok/start.py`

**Network Scripts** → `infrastructure/network/`:

- `scripts/update_allowed_hosts.py` → `infrastructure/network/update_allowed_hosts.py`

**Test Scripts** → `tests/integration/`:

- `scripts/test_labor_cost_endpoint.py` → `tests/integration/test_labor_cost_endpoint.py`
- `scripts/test_safe_endpoint.py` → `tests/integration/test_safe_endpoint.py`

---

### 📄 PHASE 5: Move Loose Files

#### QR Code Images → `assets/qr_codes/`:

- `*.png` files (11 files) → `assets/qr_codes/`
- `*qr_display.html` files (4 files) → `assets/qr_codes/`

#### Documentation → `docs/`:

- `CODEX_AGENT_INSTRUCTIONS.md` → `docs/`
- `CODEX_BUG_FIXES_SUMMARY.md` → `docs/`
- `investor_demo.py` → `docs/examples/`

#### Test Files → `tests/`:

- `test_regex.py` → `tests/unit/`
- `test_scenarios.ps1` → `tests/integration/`
- `quick_tests.ps1` → `tests/integration/`
- `test_translation.html` → `tests/fixtures/`

#### Backup Files → `archive/`:

- `agent_core/views_backup.py` → `archive/`
- `agent_core/views_safe.py` → `archive/`

#### Data Files → `data/`:

- `simulation_data.json` → Already moved ✅
- `test_menu.csv` → Already moved ✅

---

### 🧹 PHASE 6: Cleanup & Verification

#### Delete Old Directories:

- `hospitality_ai_backend/` → Delete (replaced by config/)
- `scripts/` → Delete (moved to infrastructure/)
- Old `agent_core/tasks/` files → Delete after moving

#### Update Configuration Files:

1. **config/settings.py** - Update STATICFILES_DIRS if needed:
   ```python
   STATICFILES_DIRS = [
       BASE_DIR / "static",
   ]
   ```

2. **Update all import statements** throughout codebase

3. **Update Django manage.py** if needed

#### Create __init__.py files:

- `apps/__init__.py`
- `apps/agent_core/tasks/kpi/__init__.py`
- `apps/agent_core/tasks/hr/__init__.py`
- `apps/agent_core/tasks/menu/__init__.py`
- `apps/agent_core/tasks/recipe/__init__.py`
- `apps/agent_core/tasks/beverage/__init__.py`
- `apps/agent_core/tasks/inventory/__init__.py`
- `apps/agent_core/tasks/strategy/__init__.py`

---

## ⚠️ Critical Points

### Testing After Each Phase:
```bash
# Test Django runs
python manage.py check

# Test imports
python manage.py shell
>>> from apps.agent_core.tasks.kpi.labor_cost import run
>>> # Should work without errors

# Run tests
python manage.py test
```

### Import Path Rules:

- **Absolute imports** (starting with app name): Update to include `apps.` prefix
- **Relative imports** (starting with `.` or `..`): Usually don't change, but verify
- **Within same package**: Keep as-is

### Git Commands (for safety):
```bash
# Create a branch for reorganization
git checkout -b feature/reorganize-file-structure

# Commit after each phase
git add .
git commit -m "Phase X: [Description]"

# If something breaks, easy to revert
git revert HEAD
```

---

## 📝 Summary Checklist

- [ ] Phase 2: Move Django apps to apps/ directory
- [ ] Phase 3: Reorganize task files into subdirectories
- [ ] Phase 4: Move infrastructure files
- [ ] Phase 5: Move loose files
- [ ] Phase 6: Cleanup & verification
- [ ] Update all import statements
- [ ] Create all __init__.py files
- [ ] Test Django runs successfully
- [ ] Test all imports work
- [ ] Run full test suite
- [ ] Update README.md with new structure
- [ ] Commit changes to git

---

## 🎯 Success Criteria

1. ✅ All counter files organized into proper directories
2. ✅ No duplicate files exist
3. ✅ All imports work without errors
4. ✅ Django starts and runs successfully
5. ✅ All tests pass
6. ✅ README files explain each directory's purpose
7. ✅ Structure is maintainable and scalable
