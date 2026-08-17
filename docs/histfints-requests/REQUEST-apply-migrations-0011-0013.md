# REQUEST — Apply migrations 0011–0013 to a copy, run capture once, report what landed

**Type:** Mechanical activation of existing code. No new development requested.
**Filed:** 2026-08-17 · **From:** Research Workbench
**Companion filings:** `DEFECT-F009.md` · `REQUEST-tranche2-migration.md` ·
`REQUEST-event-capture.md`
**Governing decisions:** `DECISIONS.md` D-032, D-033, D-034

---

## The ask, in one sentence

Migrations 0011–0013 and the capture mechanisms they support are already written and
committed in `histfints-v3`. **Apply them to a copy of the production database, run the
existing capture commands once, and report what was actually captured.** Nothing here asks
for new code.

---

## Why this is filed separately from the halted F-009 workstream

Research Workbench has stopped requesting further F-009 remediation *inside* HistFinTS —
development has moved to proving the Workbench can consume evidence correctly
(`hf_reswb`'s `SPEC-f009-evidence-consumption.md`, D-034). This request is not a reopening
of that work. It is a deployment step for functionality that has already shipped in code:

| Item | Migration | Code that consumes it |
|---|---|---|
| Adjustment basis | `0011_add_adjustment_basis.sql` | `provider.adjustment_basis`, `provider_assignment.adjustment_basis_override` |
| Revalidation tracking | `0012_add_revalidation_tracking.sql` | `application/revalidation_service.py` |
| Provider events | `0013_add_provider_event.sql` | `domain/provider_event.py`, `providers/yahoo_finance.py:get_splits_and_dividends()`, `providers/fred.py:get_vintage_dates()`/`get_observations_at_vintage()` |

Verified against the live database on 2026-08-17: `PRAGMA user_version` is **10**; none of
`provider_event`, `observation_correction`, `revalidation_run` exist in `sqlite_master`;
`provider` and `provider_assignment` carry no adjustment-basis columns. The backup trail
confirms nothing has run since migration 0010. This is not a gap in the code — it is a gap
between what is written and what has been switched on.

---

## The ask, precisely

1. **Apply migrations 0011–0013 to a copy of the production database.** The production file
   itself should stay untouched until the copy is validated — we are not asking for this to
   happen directly against the live file on the first pass.
2. **Verify the resulting schema and `PRAGMA user_version`** (expected: 13) against the copy.
3. **Run the existing capture commands once** against the copy — whatever the current
   equivalents are of Yahoo event capture and FRED vintage-date capture (`get_vintage_dates`,
   `get_observations_at_vintage`).
4. **Inspect the resulting evidence** — row counts per table, a sample of what a
   `provider_event` row actually looks like for a known Series, whether FRED vintage *values*
   (not just dates) were captured.
5. **Report back what was actually captured**, including any gaps or surprises. Per this
   project's own standing discipline (D-009/D-009b), a report that migrations ran without
   inspecting what they produced is not sufficient — the ask is for verified results, not a
   status flag.

---

## What this unblocks on the Workbench side

Nothing in the current `hf_reswb` implementation increment is blocked on this landing — per
D-034, the reconciler is being built and tested against the current (unmigrated) schema
first, specifically to prove it handles absent and non-explanatory evidence correctly. This
request unblocks the **second** stage of that plan: validating the `explained by captured
evidence` verdict against real captured data, once it exists. Until this request is
fulfilled, that verdict remains structurally untestable outside a hand-built fixture.

---

## Out of scope for this request

- **No new HistFinTS development.** Everything asked for here already exists in
  `histfints-v3` as committed code.
- **No changes to F-009's own remediation status.** That workstream is deliberately halted
  (D-034); this is unrelated deployment work.
- **No commitment to run capture on a schedule.** One run against one copy, to establish
  what the current code actually produces.
