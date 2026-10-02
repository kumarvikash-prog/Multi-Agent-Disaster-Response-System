## Description
<!-- What does this PR do? Why? Link to the task/issue. -->



## Type of change
- [ ] feat — new feature
- [ ] fix — bug fix
- [ ] refactor — no behaviour change
- [ ] test — tests only
- [ ] docs — documentation only
- [ ] chore — tooling / dependencies

---

## Definition of Done

- [ ] Code follows §5.1 standards; `ruff`, `mypy`, `eslint`, `tsc` clean — pre-commit passes.
- [ ] Tests added/updated; **all tests pass locally**.
- [ ] Every new endpoint: role guard, input validation, error codes, audit entry for state changes.
- [ ] Migration included if schema changed; upgrade **and** downgrade both tested locally.
- [ ] OpenAPI types regenerated (`npm run gen:api`) and committed if endpoints changed.
- [ ] No secrets in code or logs; new env vars added to `.env.example`.
- [ ] Docs updated (README / ADR / runbook) if behaviour or ops changed.
- [ ] Deployed to Render and smoke-tested (checks table from the milestone ticked).

---

## How to test this PR
<!-- Steps a reviewer can follow to verify the change. -->

