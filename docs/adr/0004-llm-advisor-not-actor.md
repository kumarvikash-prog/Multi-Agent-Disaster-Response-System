# ADR-0004 — LLM as Advisor, Not Actor

**Status:** Accepted
**Date:** 2026-10-02

## Context

The AI pipeline (LangGraph + Gemini) analyses incident reports and suggests hazard types, urgency, risk flags, and required resource counts. A naive design might let the LLM directly write to the database, pick resource IDs, or trigger dispatches.

## Decision

The LLM is a **read-only advisor**. It receives a sanitised text snapshot of the report (inside delimiters, stripped of control characters, capped at 2000 chars) and returns a validated `AnalysisOutput` Pydantic object. It has no access to the database, no ability to call external APIs, and no ability to perform any write operation. After the LLM responds, deterministic Python code (`triage/`) computes the priority score and allocation plan. A human authority must approve before any units are assigned.

## Consequences

**Good:** Human oversight is always in the loop before anything is dispatched. A fully jailbroken LLM response can at most affect hazard labels, urgency, flags, and suggested counts — all reviewed by a human. The AI is trivially replaceable (swap the provider via env var). The graph is testable without a real LLM.

**Bad:** Adds a step before dispatch; the authority cannot automate approval. This is an intentional safety feature.

**Revisit when:** We have high confidence in model reliability and want to add an auto-approve path for low-risk, high-confidence analyses (not currently planned).
