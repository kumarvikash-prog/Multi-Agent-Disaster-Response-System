# Contributing to DisasterAI

Welcome! This document covers our workflow, conventions, and standards. Read it before writing any code.

---

## Branch naming

| Prefix | When to use |
|---|---|
| `feat/` | New feature or endpoint |
| `fix/` | Bug fix |
| `refactor/` | Refactor without behaviour change |
| `test/` | Adding or fixing tests only |
| `docs/` | Documentation update |
| `chore/` | Tooling, config, dependency updates |

**Examples:** `feat/auth-login`, `fix/priority-score-edge-case`, `docs/onboarding-update`

---

## Conventional commits

Format: `<type>(<scope>): <short description>`

```
feat(incidents): add PATCH triage endpoint
fix(auth): correct timing-safe comparison on unknown email
docs(adr): add ADR-0005 for LLM limiter design
chore(deps): pin langchain to 0.3.x
```

Types match branch prefixes above. Scope is the module or area. Description is imperative, lowercase, no period.

---

## PR workflow

1. Keep PRs **small** (aim < 400 changed lines).
2. Fill out the PR template — it includes the Definition of Done checklist.
3. Link the milestone task in the description.
4. Request **at least one** reviewer.
5. Do **not** merge your own PR.
6. Use **squash merge** onto `main`.
7. Delete the branch after merge.
8. Tag the finished milestone: e.g. `git tag v0.1.0 && git push origin v0.1.0`.

---

## Testing

- Every bug fix ships with a regression test.
- Tests **never call the real LLM** by default (use the fake chat model fixture).
- Tests use `disasterai_test` database and roll back between tests.
- No test should depend on execution order.

```bash
cd backend && python -m pytest          # all tests
cd backend && python -m pytest tests/unit/  # unit only
cd frontend && npm run test
```

---

## Linting and type-checking

Pre-commit runs everything automatically. To run manually:

```bash
# Python
ruff check app/ && ruff format --check app/
mypy app/
python -m import_linter

# TypeScript
cd frontend && npm run lint && npm run type-check
```

---

## Migration rules

- **One Alembic head at all times.** If two branches add migrations, the second to merge rebases and renumbers.
- **Never edit a migration that has been deployed.** Add a new one instead.
- Every migration must have a working `downgrade()`.
- Run `alembic upgrade head` and `alembic downgrade -1` locally before committing.

---

## Adding things

- **New module:** follow the template (`router.py`, `service.py`, `repository.py`, `models.py`, `schemas.py`, `errors.py`, `__init__.py`). Register the router in `main.py`.
- **New endpoint:** add role guard, input validation (Pydantic), error codes, and an integration test.
- **New env var:** add to `.env.example` with a comment, and to `core/config.py`.
- **New ADR:** copy `docs/adr/0000-template.md`, pick the next number.

---

## Module boundary rules (enforced by import-linter)

1. A module imports another only through its `__init__.py`.
2. `triage/` is pure — no FastAPI, no SQLAlchemy, no database imports.
3. `ai/` never imports a repository.
4. Only `workflow/` orchestrates writes across multiple modules.
5. Routers never touch a Session or a model directly.
6. No raw SQL outside `repository.py`.
