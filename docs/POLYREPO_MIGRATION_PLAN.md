# Hospitality AI Monorepo to Polyrepo Migration Plan

## Overview
Migrate from Django monorepo to polyrepo architecture with clear service boundaries, preserved git history, and independent development workflows. Start with 3 core services (gateway, KPI, HR) to avoid service sprawl.

## Key Decisions

1. **Service Count:** Start with 3 services (gateway, kpi-ai-service, hr-ai-service). Fold beverage/menu/recipe/strategy into "menu-engineering" slice later if needed.
2. **Tech Stack:**
   - **Gateway:** Django/DRF (auth, admin, ORM, middleware)
   - **Microservices:** FastAPI (lean, great OpenAPI, async)
   - **Frontend:** React + Vite + TypeScript (extract JS from Django templates)
3. **Shared Libraries:** GitHub Packages (not submodules)
   - Python: `shared-python-utils` → PyPI via GitHub Packages
   - JS: `@curatedrc/shared-js` → npm via GitHub Packages
4. **Standardized Endpoints:** All tasks use `/analyze/{task_id}` with uniform request/response schema

## Target Repositories (Phase 1)

| Repo | Source Path(s) | Tech Stack |
|------|----------------|------------|
| **hospitality-ai-frontend** | `apps/dashboard/templates/`<br>`staticfiles/dashboard/js/` | React + Vite + TypeScript |
| **hospitality-ai-gateway** | `apps/agent_core/views*.py`<br>`apps/chat_assistant/`<br>`config/`<br>`manage.py` | Django/DRF |
| **kpi-ai-service** | `apps/agent_core/tasks/kpi/`<br>`apps/agent_core/schemas/kpi_analysis.py` | FastAPI |
| **hr-ai-service** | `apps/agent_core/tasks/hr/` | FastAPI |
| **shared-python-utils** | `apps/agent_core/utils/` | Python package |
| **shared-js-utils** | `staticfiles/dashboard/js/translations.js` | npm package |
| **hospitality-ai-infra** | `infrastructure/` | Docker Compose |

## Uniform Service Contract

### Request Format
```json
{
  "task": "labor_cost",
  "params": { "...": "..." },
  "context": { "location": "MN", "currency": "USD" }
}
```

### Response Format
```json
{
  "service": "kpi",
  "task": "labor_cost",
  "status": "success",
  "data": { "labor_pct": 0.312, "band": "target" },
  "meta": { "version": "1.0.0", "elapsed_ms": 42 }
}
```

## Phase 0: Preparation & Freeze (1-2 hours)

### 0.1 Branch & Tag
```bash
git checkout -b migration/polyrepo
git tag -a v1.0.0-monorepo -m "Pre-migration snapshot"
```

### 0.2 Create GitHub Repositories
Create empty repos with branch protection:
- `hospitality-ai-frontend`
- `hospitality-ai-gateway`
- `kpi-ai-service`
- `hr-ai-service`
- `shared-python-utils`
- `shared-js-utils`
- `hospitality-ai-infra`

## Phase 1: Extract History-Preserving Repos (2-3 hours)

### Install git-filter-repo
```bash
# Ubuntu/WSL
sudo apt-get install git-filter-repo
# OR via pip
pip install git-filter-repo
```

### Extract Commands (Ready to Run)

```bash
# FRONTEND
git clone --no-tags <MONO_REMOTE> hospitality-ai-frontend && cd $_
git filter-repo \
  --path apps/dashboard/templates/ \
  --path staticfiles/dashboard/js/ \
  --path-rename apps/dashboard/templates/:templates/dashboard/ \
  --path-rename staticfiles/dashboard/js/:static/js/
git remote remove origin
git remote add origin git@github.com:CuratedRC/hospitality-ai-frontend.git
git push -u origin HEAD:main
cd ..

# GATEWAY
git clone --no-tags <MONO_REMOTE> hospitality-ai-gateway && cd $_
git filter-repo \
  --path apps/agent_core/views.py \
  --path apps/agent_core/views_safe.py \
  --path apps/agent_core/urls.py \
  --path apps/agent_core/task_registry.py \
  --path apps/agent_core/task_map.py \
  --path apps/agent_core/middleware.py \
  --path apps/chat_assistant/ \
  --path config/ \
  --path manage.py \
  --path requirements.txt \
  --path pyproject.toml
git remote remove origin
git remote add origin git@github.com:CuratedRC/hospitality-ai-gateway.git
git push -u origin HEAD:main
cd ..

# KPI SERVICE
git clone --no-tags <MONO_REMOTE> kpi-ai-service && cd $_
git filter-repo \
  --path apps/agent_core/tasks/kpi/ \
  --path apps/agent_core/schemas/kpi_analysis.py \
  --path-rename apps/agent_core/tasks/kpi/:src/kpi/ \
  --path-rename apps/agent_core/schemas/kpi_analysis.py:src/schemas/kpi_analysis.py
git remote remove origin
git remote add origin git@github.com:CuratedRC/kpi-ai-service.git
git push -u origin HEAD:main
cd ..

# HR SERVICE
git clone --no-tags <MONO_REMOTE> hr-ai-service && cd $_
git filter-repo \
  --path apps/agent_core/tasks/hr/ \
  --path-rename apps/agent_core/tasks/hr/:src/hr/
git remote remove origin
git remote add origin git@github.com:CuratedRC/hr-ai-service.git
git push -u origin HEAD:main
cd ..

# SHARED PYTHON
git clone --no-tags <MONO_REMOTE> shared-python-utils && cd $_
git filter-repo \
  --path apps/agent_core/utils/ \
  --path-rename apps/agent_core/utils/:src/utils/
git remote remove origin
git remote add origin git@github.com:CuratedRC/shared-python-utils.git
git push -u origin HEAD:main
cd ..

# SHARED JS
git clone --no-tags <MONO_REMOTE> shared-js-utils && cd $_
git filter-repo \
  --path staticfiles/dashboard/js/translations.js \
  --path-rename staticfiles/dashboard/js/:src/
git remote remove origin
git remote add origin git@github.com:CuratedRC/shared-js-utils.git
git push -u origin HEAD:main
cd ..

# INFRA
git clone --no-tags <MONO_REMOTE> hospitality-ai-infra && cd $_
git filter-repo \
  --path infrastructure/ \
  --path-rename infrastructure/:infra/
git remote remove origin
git remote add origin git@github.com:CuratedRC/hospitality-ai-infra.git
git push -u origin HEAD:main
```

## Phase 2: Bootstrap Repositories (3-4 hours)

### 2.1 Gateway: Microservice Client

**File: `apps/agent_core/microservices/clients.py`**
```python
import httpx
from django.conf import settings

class MicroserviceClient:
    def __init__(self, base_url: str, timeout=30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def post(self, path: str, payload: dict):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(f"{self.base_url}{path}", json=payload)
            r.raise_for_status()
            return r.json()

kpi_client = MicroserviceClient(settings.MICROSERVICES["KPI_SERVICE_URL"])
hr_client = MicroserviceClient(settings.MICROSERVICES["HR_SERVICE_URL"])
```

**File: `apps/agent_core/task_registry.py` (core execute)**
```python
from .microservices.clients import kpi_client, hr_client

ENDPOINTS = {
    "kpi": {
        "labor_cost": "/analyze/labor_cost",
        "prime_cost": "/analyze/prime_cost",
    },
    "hr": {
        "staff_retention": "/analyze/staff_retention",
    },
}

async def execute_task(service: str, task: str, params: dict, context: dict | None = None):
    client_map = {"kpi": kpi_client, "hr": hr_client}
    client = client_map.get(service)
    endpoint = ENDPOINTS.get(service, {}).get(task)
    if not client or not endpoint:
        return {"status": "error", "error": "unknown_service_or_task"}
    payload = {"task": task, "params": params, "context": context or {}}
    return await client.post(endpoint, payload)
```

**File: `config/settings.py` (add)**
```python
MICROSERVICES = {
    "KPI_SERVICE_URL": os.environ.get("KPI_SERVICE_URL", "http://localhost:8001"),
    "HR_SERVICE_URL": os.environ.get("HR_SERVICE_URL", "http://localhost:8002"),
}
```

### 2.2 KPI Service: FastAPI Skeleton

**File: `app/main.py`**
```python
from fastapi import FastAPI
from .routes import router

app = FastAPI(title="KPI AI Service")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "healthy"}
```

**File: `app/routes.py`**
```python
from fastapi import APIRouter
from pydantic import BaseModel
from src.kpi.labor_cost.analyzer import run as labor_cost_run
from src.kpi.prime_cost.analyzer import run as prime_cost_run

router = APIRouter()

class AnalyzeRequest(BaseModel):
    task: str
    params: dict
    context: dict | None = None

@router.post("/analyze/{task_id}")
def analyze(task_id: str, req: AnalyzeRequest):
    dispatch = {
        "labor_cost": labor_cost_run,
        "prime_cost": prime_cost_run,
    }
    fn = dispatch.get(task_id)
    if not fn:
        return {"status": "error", "error": "unknown_task"}
    data = fn(req.params, req.context or {})
    return {
        "service": "kpi",
        "task": task_id,
        "status": "success",
        "data": data,
        "meta": {"version": "1.0.0"}
    }
```

### 2.3 Frontend: React + Vite Setup

**Structure:**
```
hospitality-ai-frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx
│   │   ├── CalculationResults.tsx
│   │   └── Dashboard/
│   ├── hooks/
│   │   └── useChat.ts
│   ├── lib/
│   │   ├── api.ts           # Gateway API client
│   │   └── types.ts         # Generated from OpenAPI
│   └── App.tsx
├── vite.config.ts
├── package.json
└── .env.example
```

**Generate typed client from gateway OpenAPI:**
```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/lib/types.ts
```

**File: `src/lib/api.ts`**
```typescript
const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8000';

export async function callAgent(task: string, params: object) {
  const response = await fetch(`${GATEWAY_URL}/api/agent/safe/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      service: task.split('.')[0],
      subtask: task.split('.')[1],
      params
    })
  });
  return response.json();
}
```

### 2.4 Infrastructure: Docker Compose

**File: `infra/docker-compose.yml`**
```yaml
version: "3.8"

services:
  gateway:
    build: ../hospitality-ai-gateway
    ports: ["8000:8000"]
    environment:
      KPI_SERVICE_URL: http://kpi-service:8001
      HR_SERVICE_URL: http://hr-service:8002
      DJANGO_SETTINGS_MODULE: config.settings
    depends_on:
      kpi-service:
        condition: service_healthy
      hr-service:
        condition: service_healthy

  kpi-service:
    build: ../kpi-ai-service
    ports: ["8001:8001"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  hr-service:
    build: ../hr-ai-service
    ports: ["8002:8002"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ../hospitality-ai-frontend
    ports: ["3000:3000"]
    environment:
      VITE_GATEWAY_URL: http://localhost:8000
```

**File: `infra/dev/Makefile`**
```makefile
.PHONY: up down logs restart test

up:    ; docker compose up -d
down:  ; docker compose down
logs:  ; docker compose logs -f
restart: ; docker compose restart
test:  ; echo "Run cross-service integration tests here"
```

## Phase 3: CI/CD Templates (2-3 hours)

### Python Services: `.github/workflows/ci.yml`
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pip install ruff pytest
      - run: ruff check .
      - run: pytest -q
      - run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .
```

### Frontend: `.github/workflows/ci.yml`
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --ci
      - run: docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .
```

### Release on Tags (All Repos)
```yaml
on:
  push:
    tags: ['v*']

jobs:
  publish-image:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
      - run: docker build -t ghcr.io/${{ github.repository }}:${{ github.ref_name }} .
      - run: docker push ghcr.io/${{ github.repository }}:${{ github.ref_name }}
```

## Phase 4: Task Separation (Your Requirement)

### Structure for Each Microservice

**Example: kpi-ai-service/**
```
kpi-ai-service/
├── src/
│   └── kpi/
│       ├── labor_cost/          # Separate folder
│       │   ├── __init__.py
│       │   ├── analyzer.py     # Main logic
│       │   ├── benchmarks.py   # Industry benchmarks
│       │   └── tests_unit.py    # Unit tests
│       ├── prime_cost/
│       │   ├── __init__.py
│       │   ├── analyzer.py
│       │   └── tests_unit.py
│       └── ...
├── tests/
│   └── integration/              # Integration tests
└── app/
    └── routes.py
```

**Test Organization:**
- Per-task unit tests: `src/kpi/labor_cost/tests_unit.py`
- Integration tests: `tests/integration/` (call HTTP endpoints)

## Phase 5: Verification Checklist

### Per Repo
- [ ] `git clone && make dev` works (or `docker compose up`)
- [ ] `/health` returns 200 for all services
- [ ] CI green on push
- [ ] Tagged releases publish Docker images

### Integration
- [ ] Frontend → Gateway → Microservice flow works
- [ ] Chat interface end-to-end
- [ ] All investor demo features work
- [ ] Performance acceptable (no regressions)

## Timeline

| Phase | Duration | Critical Path |
|-------|----------|---------------|
| Phase 0: Prep | 1-2 hours | ✅ Must complete |
| Phase 1: Extract repos | 2-3 hours | ✅ Must complete |
| Phase 2: Bootstrap repos | 3-4 hours | ✅ Must complete |
| Phase 3: CI/CD | 2-3 hours | Can defer |
| Phase 4: Task separation | 2-3 hours | ✅ Your requirement |
| Phase 5: Verification | 1 hour | ✅ Must complete |

**Total: 11-16 hours** (critical path: 9-13 hours)

## Ready to Execute

All code examples, git commands, and configurations are provided above. You can start executing immediately with:

1. Phase 0: Create branch and tag
2. Phase 1: Run git filter-repo commands (copy-paste ready)
3. Phase 2: Bootstrap each repo with provided code
4. Phase 3: Add CI/CD workflows
5. Phase 4: Separate tasks into folders
6. Phase 5: Verify end-to-end

