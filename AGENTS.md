# HistFinTS Research Workbench

The complete instruction set for working in this repository. Agent-neutral: everything here
applies regardless of which coding agent is doing the work. `CLAUDE.md`, at this repo's root,
adds only the handful of things specific to working here as Claude Code — read it too if
that's what you are.

Multi-asset financial research application, built on top of the **HistFinTS** local
time-series database (separate project, read-only from here — see `docs/DECISIONS.md` D-001).

**Before writing any code, read `docs/HISTFINTS-BRIEF-v2.md`.** It is the corrected,
current-state technical reference — schema facts, known defects, adjustment basis per
provider, V0 data reality — all verified against real code and data, not summarised from
memory. `docs/DECISIONS.md` is the full reasoning and evidence trail behind it; consult that
when the brief's summary isn't enough, not as your first read.

## What this project is

A provenance-first research workbench over HistFinTS's price/macro data, covering US
equities, macro indicators, and a manually-verified set of Argentine/CEDEAR names. Not a
Yahoo Finance clone — see `docs/DECISIONS.md` §"Inherited principles" for the six governing
principles (P1–P43), especially **P1** (a ticker is never identity) and **P3** (every
displayed value must be traceable).

## Sibling repositories

This repo, HistFinTS itself, `histfints_uiue`, and `_shared-standards` (cross-project standards
and the RGC role's own home) all live as siblings under `E:\dev\` (`E:\dev\workbench`,
`E:\dev\histfints`, `E:\dev\histfints_uiue`, `E:\dev\_shared-standards`) as of the 2026-08-28
restructure — see `E:\dev\_shared-standards\HISTFINTS_RESTRUCTURE_RUNBOOK.md` for the full
record. If you're working from an older checkout (e.g. under a `Proyectos\` path, or a
`histfints-v3` folder), that tree still runs but is stale — re-root against `E:\dev\` before
trusting cross-repo references.

## Where things are

| File | What it is |
|---|---|
| `docs/ACTION_PLAN.md` | The master, dependency-ordered coordination plan: parties and settled authority (PO/DFA/SE/SDT/UIUE), the standing prohibitions (SP) and UIUE defaults (UP) that increments cite by ID, the four-gate validation model, and every increment's current state (`CLOSED`/`ACTIVE`/`NEXT`/`BLOCKED`/`DEFERRED`/`CONTINUOUS`). Read this to know what's currently in scope and why before touching an increment. `docs/README.md`'s reading order covers the rest of this table too — this file duplicates only the entries most load-bearing for day-to-day work. |
| `docs/HISTFINTS-BRIEF-v2.md` | **Start here.** Corrected technical brief: schema, known defects, adjustment basis, V0 data reality. Supersedes the original consuming-team brief, which was twice misread as exhaustive during review and caused a retracted finding. |
| `docs/DECISIONS.md` | The full specification and reasoning log. Every architectural decision (`D-###`), open question (`Q-###`), known defect (`F-###`), and queued spec amendment (`A-###`), each with evidence. Read before implementing anything touching identity, adjustment, currency, or panels — the brief gives you the facts, this gives you why. |
| `docs/SPEC_PANEL_ELIGIBILITY.md` | Converged spec for panel-derived analytics (implied FX, cross-section screening). Status: design-complete, gated on Q-027 (trading calendar) and the HistFinTS Tranche 2 migration. |
| `docs/SPEC_F009_EVIDENCE_CONSUMPTION.md` | Design note for the Workbench-side F-009 evidence-consumption/reconciliation capability (D-032–D-034). Reference-by-key evidence model, three-verdict reconciler (`explained` / `not explained` / `insufficient evidence`), full traceability chain. `explained by captured evidence` is structurally unreachable against the live database until HistFinTS migrations 0011–0013 are applied — read §8 before assuming otherwise. |
| `docs/histfints-requests/` | Filings sent to (or pending for) the HistFinTS team: `DEFECT-F009.md` (still active — dormant, unresolved), `REQUEST-event-capture.md`, `REQUEST-apply-migrations-0011-0013.md`. Track their status in `DECISIONS.md`'s Tranche table before assuming any of them have landed. (`REQUEST-tranche2-migration.md` landed — confirmed via D-044 — and now lives in `docs/evidence/` as closed historical, not here.) |

## Documentation lifecycle (structural changes only)

Before creating, classifying, reorganizing, archiving, registering, or otherwise structurally
changing project documentation, consult and follow the **`documentation-lifecycle`**
procedure — the canonical source, no longer stored in this repository. It is cross-project:
canonical text lives at `../_shared-standards/skills/documentation-lifecycle/SKILL.md` (a
sibling repository, one level up from here). This is a pointer, not a copy; the procedure
itself is not restated here and this section must not grow into a second version of it.

Applying it in Workbench means, at minimum:
- Classify before any structural change — never move, archive, or register a file on the
  strength of its filename, date, or apparent completeness alone.
- Preserve the skill's bucket distinctions (Current / Evidence / Active request / Memory
  candidate / Rule-D / HOLD) rather than collapsing them into an ad hoc scheme.
- Never infer closure from age, a filename pattern, the word "implemented," or the existence of
  a downstream mitigation — "implemented" is not "integrated," and a mitigation is not the
  closure of the defect it mitigates.
- When a file's lifecycle status is genuinely ambiguous, leave it HOLD and route the question
  per the procedure's §5 — never resolve it by guess.
- Update the applicable index/register (`docs/README.md`'s reading order, `docs/EVIDENCE_LOG.md`,
  and/or `docs/DECISIONS.md`'s changelog, as applicable) in the *same* change as any structural
  move — never leave an index stale even briefly.
- Use Workbench's own established placement convention — a single flat `docs/evidence/` folder
  with `docs/EVIDENCE_LOG.md` as its pointer register (see `DOCUMENTATION_MIGRATION_PLAN_2026-08-27.md`)
  — rather than importing another repository's folder taxonomy or naming.
- After any structural documentation change, validate discoverability, references, counts, and
  tests per the procedure's §10/§11 — not just that the move itself succeeded.

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
