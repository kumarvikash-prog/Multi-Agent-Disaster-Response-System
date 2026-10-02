# Runbook — DisasterAI

## Phase 0 deployment spike results

> Fill this in after completing §11.8 checks.

| # | Check | Result | Date |
|---|---|---|---|
| 1 | Static site loads, SPA fallback works | — | — |
| 2 | `/api/v1/health` through the proxy | — | — |
| 3 | Cookie round trip through proxy (Chrome, Firefox, Safari/iOS) | — | — |
| 4 | `/api/v1/health/db` against Neon | — | — |
| 5 | Migration in build command (`alembic upgrade head`) | — | — |
| 6 | Cold start after 15+ min idle | — | — |
| 7 | Gemini call from backend (`scripts/llm_smoke.py`) | — | — |
| 8 | Memory at idle (Render metrics) | — | — |
| 9 | Pinger keeps service warm; Neon suspends when idle | — | — |
| 10 | Build filters (frontend-only commit does not redeploy backend) | — | — |

---

## Deploy procedure

1. Merge PR to `main`.
2. Render auto-deploys backend: `pip install -r requirements.txt && alembic upgrade head` then starts uvicorn.
3. Render auto-deploys frontend: `npm ci && npm run build`.
4. Smoke-test health endpoint through the static site URL.

## Rollback procedure

1. Go to Render dashboard → backend service → Deploys.
2. Click **Rollback** on the previous successful deploy.
3. If a migration was deployed, add a new downgrade migration (never edit deployed migrations).

## Database restore drill

1. Go to Neon console → Branches → Restore from point-in-time.
2. Verify on a Neon branch first, then apply to `main` if confirmed.

## Incident response (on-call)

1. Check `GET /api/v1/health/db` — if 503, Neon may be sleeping (wait 10 s and retry) or down (check Neon status page).
2. Check Render logs for stack traces.
3. Use `X-Request-ID` from the error envelope to find the exact log line.
4. If the AI pipeline is failing: incidents accumulate in SUBMITTED → they will be swept to PENDING_REVIEW with `needs_manual_review = true`.

## Environment variables

See `backend/.env.example` for the full list and descriptions.
