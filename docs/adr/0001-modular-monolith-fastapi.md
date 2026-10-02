# ADR-0001 — Modular Monolith with FastAPI

**Status:** Accepted
**Date:** 2026-10-02

## Context

The team has six members and needs a clean separation of concerns to allow parallel development without stepping on each other. We also need a system that is easy to deploy to Render's free tier, easy to test, and easy to read for evaluators.

## Decision

Use a **modular monolith**: one FastAPI backend process, one React frontend. Modules are separated by strict import boundaries enforced with `import-linter`. The AI pipeline (LangGraph) runs inside the backend process — no separate service. Python 3.12 with sync SQLAlchemy 2.x and psycopg 3 for simplicity and LangGraph compatibility.

## Consequences

**Good:** Single deployment unit. No network hops between modules. Easy to read and debug. LangGraph is Python-first. Free hosting on Render.

**Bad:** Single process means in-memory rate limiting and background tasks do not scale horizontally. This is a documented limit; a separate AI service can be extracted later if needed.

**Revisit when:** a module needs independent scaling or a separate team owns it exclusively.
