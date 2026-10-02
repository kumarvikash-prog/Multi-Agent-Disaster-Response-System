# Onboarding — Local Setup Guide

> Target: a new developer should reach a running local setup with seeded data in **≤ 15 minutes**.

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | **3.12** | `brew install python@3.12` (macOS) or python.org |
| Node.js | Current LTS (22+) | nodejs.org |
| PostgreSQL | **16** | `brew install postgresql@16` (macOS) |
| Git | Latest | pre-installed on macOS |

## 1. Clone and enter the repo

```bash
git clone <your-repo-url> disasterai
cd disasterai
```

## 2. Create local databases

```bash
createdb disasterai_dev
createdb disasterai_test
```

If `createdb` is not found: `brew services start postgresql@16` first.

## 3. Backend setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -r requirements-dev.txt

cp .env.example .env
```

Edit `.env` — at minimum fill in:

```env
ENV=development
DATABASE_URL=postgresql+psycopg://localhost/disasterai_dev
DATABASE_URL_DIRECT=postgresql+psycopg://localhost/disasterai_dev
JWT_SECRET=any-32-char-string-for-local-dev-only
```

Run migrations:

```bash
alembic upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify: `http://localhost:8000/api/v1/health` → `{"status": "ok", ...}`

## 4. Frontend setup

```bash
cd ../frontend
npm install
cp .env.example .env   # no changes needed for local dev
npm run dev
```

Open `http://localhost:5173` — you should see the StatusPage showing the backend is healthy.

## 5. Install pre-commit hooks

```bash
cd ..   # repo root
pip install pre-commit   # or: cd backend && .venv/bin/pip install pre-commit
pre-commit install
```

## 6. (Optional) Seed demo data

```bash
cd backend
source .venv/bin/activate
python scripts/seed.py
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `createdb: command not found` | Start PostgreSQL: `brew services start postgresql@16`; add `/opt/homebrew/opt/postgresql@16/bin` to PATH |
| `psycopg` install error | `brew install libpq` then retry |
| Port 8000 in use | `kill $(lsof -ti:8000)` |
| Port 5173 in use | Vite will pick the next port — check the terminal output |
| `alembic: command not found` | Activate the venv first: `source .venv/bin/activate` |
| Pre-commit eslint fails | `cd frontend && npm install` then retry |
