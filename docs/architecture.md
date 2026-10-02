# Architecture — DisasterAI

> This document is kept current with the implemented system. For the full implementation plan see `docs/` and the ADRs.

## System context

```
 ┌───────────┐        ┌─────────────────────────────┐
 │  Citizen  │──────► │  Render Static Site         │        ┌────────────────┐
 └───────────┘  HTTPS │  (React build, /api rewrite) │        │ Google Gemini  │
 ┌───────────┐        └──────────────┬──────────────┘        │ API (LLM)      │
 │ Authority │──────►                │ /api/* proxied        └───────▲────────┘
 └───────────┘        ┌──────────────▼──────────────┐                │
                       │ Render Web Service          │────────────────┘
                       │ FastAPI + LangGraph         │
                       └──────────────┬──────────────┘
                                      │ SQL (pooled, TLS)
                            ┌─────────▼─────────┐
                            │ Neon PostgreSQL   │
                            └───────────────────┘
```

## Core flow

```
Citizen submits report
        │
        ▼
 Incident created (SUBMITTED) ──► background AI analysis (ANALYZING)
        │                                  │  1 LLM call: hazards, urgency, risk flags, suggested units
        ▼                                  ▼
 PENDING_REVIEW ◄────── deterministic priority score + nearest-unit / hospital plan
        │
        ├── Authority edits (people, hazards, unit counts) → plan recomputed
        ├── Approve & Dispatch ──► DISPATCHED ── Resolve ──► RESOLVED (units released)
        └── Reject ──► REJECTED
Citizen polls status: Under Review → Dispatched → Resolved | Not Confirmed
```

## Backend module map

| Module | Responsibility | Depends on |
|---|---|---|
| `auth` | Register, login, refresh, logout, me, role guards | `users` |
| `users` | User model and queries | — |
| `incidents` | Incident + report models, queries, state machine | `users`, `audit` |
| `resources` | Response units: models, availability | — |
| `hospitals` | Hospital capacity: models, update | `audit` |
| `triage` | **Pure** priority scoring, allocation, haversine, ETA | stdlib only |
| `ai` | LangGraph graph, analysis agent, LLM provider, prompts, limiter | `triage` |
| `workflow` | Use-cases spanning modules: submit, analyse, recompute, approve, reject, resolve, sweep | all above |
| `audit` | Append-only audit log writes and timeline reads | — |

## AI pipeline

```
START ──► Analysis agent (LLM) ──► Priority agent (pure) ──► Allocation agent (pure) ──► END
                 │ on failure
                 └──► needs_manual_review ──► END
```

The graph does **not** touch the database. `workflow/run_analysis.py` loads context, invokes the graph, and persists everything in one transaction.

## Technology decisions

See `docs/adr/` for the rationale behind each decision.

| Decision | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, sync SQLAlchemy 2.x, psycopg 3, Alembic |
| Frontend | React 18, TypeScript strict, Vite, Tailwind CSS, TanStack Query |
| AI | LangGraph (inside the backend), Gemini default, OpenAI-compatible adapter ready |
| Database | PostgreSQL 16 (Neon cloud, local native for dev) |
| Auth | Cookie JWT (15 min access + 7 day refresh, HTTP-only, Secure, SameSite=Lax) |
| Hosting | Render (web service + static site with /api rewrite proxy) |
| No | Docker, Redis, WebSockets (Phase 1), PostGIS (Phase 1), CI/CD (Phase 1) |
