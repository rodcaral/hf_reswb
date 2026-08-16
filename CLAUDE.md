# HistFinTS Research Workbench

Multi-asset financial research application, built on top of the **HistFinTS** local
time-series database (separate project, read-only from here — see `docs/DECISIONS.md` D-001).

**Before writing any code, read `docs/DECISIONS.md` in full.** It is the actual
specification. This file is an index into it, not a substitute.

## What this project is

A provenance-first research workbench over HistFinTS's price/macro data, covering US
equities, macro indicators, and a manually-verified set of Argentine/CEDEAR names. Not a
Yahoo Finance clone — see `docs/DECISIONS.md` §"Inherited principles" for the six governing
principles (P1–P43), especially **P1** (a ticker is never identity) and **P3** (every
displayed value must be traceable).

## Where things are

| File | What it is |
|---|---|
| `docs/DECISIONS.md` | **The specification.** Every architectural decision (`D-###`), open question (`Q-###`), known defect (`F-###`), and queued spec amendment (`A-###`), each with evidence. Read before implementing anything touching identity, adjustment, currency, or panels. |
| `docs/SPEC-panel-eligibility.md` | Converged spec for panel-derived analytics (implied FX, cross-section screening). Status: design-complete, gated on Q-027 (trading calendar) and the HistFinTS Tranche 2 migration. |
| `docs/KB-argentine-instruments.md` | Standing reference on CEDEARs, Argentine market structure, and the multiple-dollar FX regime. Not HistFinTS-specific — background knowledge. |
| `docs/histfints-requests/` | Filings sent to (or pending for) the HistFinTS team: `DEFECT-F009.md`, `REQUEST-tranche2-migration.md`, `REQUEST-event-capture.md`. Track their status in `DECISIONS.md`'s Tranche table before assuming any of them have landed. |
| `.claude/agents/spec-interrogator.md` | Subagent for continuing the requirements-interrogation process (one question at a time, verify-before-log, D-009/D-009b discipline). Use it when a design question needs the same rigor as the original review, not for routine coding. |

## Non-negotiable constraints, extracted for quick reference

- **HistFinTS is read-only.** Never write to its database. Workbench owns its own SQLite
  file, attached read-only via `ATTACH DATABASE ... AS histfints`. (D-001)
- **`series_id` is a convention-level FK, not enforced.** Check `series.status` /
  `archived_at` for staleness, not row existence — rows are never hard-deleted, only
  archived on MERGE. (D-003)
- **Never apply a CEDEAR ratio without checking its effective date.** A constant ratio is
  confirmed wrong for at least one real historical span (AAPL CEDEAR, 2024-01-24 step).
  (D-015, F-021)
- **Adjustment basis is currently unrecorded in HistFinTS.** Yahoo = split-adjusted,
  dividend-unadjusted; Alpha Vantage = raw. Don't assume a uniform basis across providers
  until the Tranche 2 field lands. (D-005, D-021)
- **`import_run.status = SUCCESS` does not imply a complete range.** Confirmed live
  truncation (19 of ~408 bars). Don't build a completeness assumption on `status` alone.
  (F-017)
- **Coverage ≠ availability.** Don't infer "this Series has little history" from a low
  observation count without first checking whether the fetch was truncated. (D-029–D-031)
- **A clean empirical result from this database is not evidence of anything old enough to
  need testing.** The database is young; several early findings in `DECISIONS.md` were
  wrong for exactly this reason (see D-009, D-009b). Verify defect-adjacent assumptions by
  construction, not by observing today's data.
- **Direct-entry Series (`add_series`) are permanent, not a bypass** — the primary creation
  path, alongside Catalog resolution for bulk discovery. But they currently carry no
  evidence trail. Treat their identity as `Asserted` (P4), not `Observed`. (D-026)

## Terminology (binding)

Use **Series**, not "instrument". Use **series_master_list**, not "instrument universe".
Full glossary in `docs/DECISIONS.md` §5.

## Status as of handoff (2026-08-15)

- V0 scope confirmed: US equities + macro + a manually-verified BYMA-linked subset via
  Yahoo `.BA` (not the BYMA adapter itself, which remains unexercised for prices).
- Three items filed with the HistFinTS team, not yet confirmed landed: a defect report, a
  schema migration request (adjustment basis + availability marker), and an event-capture
  request. Check their status before assuming any schema changes exist.
- The panel-eligibility design (implied FX via CEDEAR pairs) is finished at the spec level
  and ready to implement for the parts not gated on HistFinTS changes.
- Several open questions remain unanswered — search `docs/DECISIONS.md` for `**blocking**`
  to find the current one(s).
