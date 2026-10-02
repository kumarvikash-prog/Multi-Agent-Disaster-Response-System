# DisasterAI — Multi-Agent Disaster Response System

> Citizens report emergencies; an AI pipeline structures and prioritises them; a single authority reviews, edits, and approves a dispatch of seeded response units; the citizen sees status.

---

## What is DisasterAI?

DisasterAI is a deliberately simple, deployable-from-day-one modular monolith that:
- Lets citizens submit emergency reports (flood, fire, building collapse, etc.)
- Runs an LLM-powered analysis pipeline (LangGraph + Gemini) to classify and score urgency
- Presents a structured recommendation to a human authority for review and approval
- Dispatches seeded response units (ambulances, fire trucks, rescue teams, medical teams)
- Shows the citizen their incident status in real time (polling)

---

## Architecture at a glance

```
Browser (React/Vite) ──► /api rewrite ──► FastAPI (uvicorn)
                                              │
                          ┌───────────────────┤
                          │                   │
                     PostgreSQL          LangGraph
                     (Neon, cloud)       + Gemini API
```

| Layer | Technology |
|---|---|
| Frontend | React 18 + TypeScript, Vite, Tailwind CSS, TanStack Query, React Hook Form + Zod |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.x (sync), psycopg 3, Alembic |
| AI | LangGraph, LangChain, `langchain-google-genai` (Gemini default) |
| Database | PostgreSQL 16 (Neon in cloud, local native install for dev) |
| Hosting | Render (web service + static site) |

---

## Repository structure

```
disasterai/
├── backend/          # FastAPI app (Python 3.12)
│   ├── app/
│   │   ├── core/     # config, db, security, errors, logging, middleware, rate_limit, deps
│   │   ├── shared/   # enums, pagination, time helpers
│   │   └── modules/  # auth, users, incidents, resources, hospitals, triage, ai, workflow, audit
│   ├── alembic/      # database migrations
│   └── scripts/      # seed, create_authority, reset_demo, etc.
├── frontend/         # React + TypeScript (Vite)
│   └── src/
│       ├── app/      # router, providers
│       ├── pages/    # thin route components
│       ├── features/ # auth, citizen-reports, authority-incidents, resources, hospitals
│       └── shared/   # api client, components, hooks, utils
├── docs/             # architecture, data model, API conventions, ADRs, runbook, onboarding
├── evals/            # AI evaluation datasets (Phase 5+)
└── .github/          # CODEOWNERS, PR template
```

---

## Local prerequisites

| Tool | Version |
|---|---|
| Python | **3.12** |
| Node.js | Current LTS (22+) |
| npm | 10+ |
| PostgreSQL | **16** (native install, no Docker) |
| Git | Latest stable |

Create two local databases before starting:

```bash
createdb disasterai_dev
createdb disasterai_test
```

---

## Starting the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env
# Edit .env — fill in DATABASE_URL, JWT_SECRET, etc.

uvicorn app.main:app --reload --port 8000
# or from the root:
npm run dev:api
```

Health check: `GET http://localhost:8000/api/v1/health`

---

## Starting the frontend

```bash
cd frontend
npm install
cp .env.example .env   # no changes needed for local dev

npm run dev
# or from the root:
npm run dev:web
```

The frontend proxies `/api` to `http://localhost:8000` via Vite, matching production layout.

---

## Running tests

```bash
# Backend
npm run test:api
# or:  cd backend && python -m pytest

# Frontend
npm run test:web
# or:  cd frontend && npm run test
```

---

## Linting

```bash
npm run lint
# Runs ruff, mypy, eslint, prettier, tsc --noEmit
```

Or run individually:

```bash
# Python
cd backend
ruff check app/ && ruff format --check app/
mypy app/

# TypeScript
cd frontend
npm run lint && npm run type-check
```

---

## Migrations

```bash
# Run all pending migrations
npm run migrate
# or:  cd backend && alembic upgrade head

# Create a new migration after changing models
cd backend && alembic revision --autogenerate -m "describe the change"
# Always review the generated file before committing.
```

> ⚠️ **Neon and Render are configured separately.** The local setup uses your local PostgreSQL.

---

## Important notes

- **No Docker.** Local dev uses native installs.
- **No Redis.** Rate limiting is in-memory (single-process only; documented limit).
- **No WebSockets in Phase 1.** Both dashboards use polling.
- **Neon** (cloud PostgreSQL) and **Render** (hosting) are connected after Phase 0 scaffolding.
- **The LLM is an advisor, never an actor.** Every AI recommendation requires human approval before anything is dispatched.
- **Secrets** go in `.env` (git-ignored). Never commit a real `.env`.
