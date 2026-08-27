# Prompt changelog

## triage_v1 — 2026-08-27
Initial ticket classifier. Structured JSON, closed enums, `Unknown` for ambiguous products, no invented error codes. KB excerpts are supplied by retrieval, not by the model.

## brief_v1 — 2026-08-27
Initial TAM brief writer. Model may only produce `executive_summary` and `talking_points`. Risks and quotes are injected from the rule extractor and must not be invented.
