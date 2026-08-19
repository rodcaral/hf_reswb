# Tranche 2 and Migrations 0011–0013 — Live Status Check, 2026-08-19

**Date:** 2026-08-19
**Trigger:** answering "what should HistFinTS work on" required first checking what they'd
already done — two previously-blocking filings (`ACTION-TRANCHE2-IMPLEMENTATION.md`,
`REQUEST-apply-migrations-0011-0013.md`) had never been re-checked against live data after
D-032/D-043 declared them outstanding.
**Nature of this document:** Status verification. **No threshold selected or promoted.**

---

## Headline: both filings have substantially landed, undetected until this check

`PRAGMA user_version` is now **14** (was 10 at D-032's last check, 2026-08-15/17). Both
outstanding schema asks have measurable progress:

### Tranche 2 Item 1 (adjustment basis) — done, with a vocabulary difference to reconcile

| Provider | Requested value | Actual value |
|---|---|---|
| FRED | `UNADJUSTED` | `NOT_APPLICABLE` |
| Yahoo Finance | `SPLIT_ADJUSTED` | `SPLIT_ADJUSTED` ✓ exact match |
| BYMA | `UNADJUSTED` | `RAW` |

Populated, not NULL, for all three original providers — semantically consistent with what was
asked (FRED and BYMA are both "not adjusted," just labeled differently) but **not the exact
enum values requested**. Workbench's consuming logic should be checked against the actual
values (`RAW`, `NOT_APPLICABLE`), not the ones originally specified, before relying on this.

**New gap, not a failure of the original ask:** three providers added after the original
Tranche 2 filing — Finnhub, Twelve Data, MERVAL (all created 2026-08-18/19) — have
`adjustment_basis = NULL`. These didn't exist when Tranche 2 was filed.

### Tranche 2 Item 2 (availability marker) — 98.3% done, with a staleness concern

`first_available_date`/`last_available_date` populated on 11,248 of 11,446
`provider_assignment` rows. 198 unpopulated rows are all Yahoo Finance assignments for
special-character tickers (preferred-share notation like `AHL$D`, `ATH$B`) — a plausible
pattern (special characters breaking a backfill script), not investigated further here.

**Spot-check of accuracy found a staleness issue**: all three sampled rows show
`last_available_date` lagging the series' actual latest observation by several days (e.g.
stored `2026-08-14` vs. actual `2026-08-18`). The marker appears to have been populated as a
one-time historical backfill rather than kept current with ongoing ingestion. If Workbench
begins relying on this field for coverage decisions, it needs to confirm whether it updates on
each new import or requires periodic re-backfill.

### Migrations 0011–0013 (F-009 evidence tables) — schema landed, zero data captured

`provider_event`, `observation_correction`, and `revalidation_run` **now exist** with the
schema this project's `SPEC-f009-evidence-consumption.md` was designed against — a genuine
unblock of D-032/D-034's "structurally unreachable" finding. **All three tables are empty (0
rows).** The schema deployment (the mechanical ask in `REQUEST-apply-migrations-0011-0013.md`)
appears complete; the capture/reconciliation mechanisms that would populate these tables (R1
`RevalidationService`, R2a/R2b event capture — described as already code-complete in D-032)
do not appear to be running, or have not run yet.

---

## What this changes

- **Tranche 2 is no longer a blocking gate for `SPEC-panel-eligibility.md`'s
  `adjustment_policy` and `minimum_coverage` parameters** in the way `DECISIONS.md`'s prior
  entries describe — the schema is present. Activation work can proceed on Workbench's side
  (with the vocabulary and staleness caveats above accounted for), independent of any further
  HistFinTS schema work.
- **`SPEC-f009-evidence-consumption.md`'s Stage 2 ("explained by captured evidence") is
  schema-reachable but practically still empty.** The `explained` verdict remains
  unreachable in practice — not because of an unapplied migration anymore, but because no
  events have been captured. This is a different, narrower gap than the one on record.
- **None of this was tracked or noticed by Workbench until this check.** Both filings sat in
  `docs/histfints-requests/` marked "awaiting HistFinTS team" with no process that re-verified
  them against live state. This is itself worth noting for how this project tracks outstanding
  asks going forward.

---

## Open items for HistFinTS, restated with current, accurate scope

1. **Adjustment basis for the three newer providers** (Finnhub, Twelve Data, MERVAL) —
   small, mechanical, same shape as the original Item 1.
2. **The 198 unpopulated `provider_assignment` availability-marker rows** — likely a
   backfill-script edge case (special-character tickers), not investigated further by
   Workbench.
3. **Whether the availability marker is meant to update on ongoing ingestion** or requires
   periodic re-backfill — a process question, not a data question.
4. **Whether R1/R2 capture (revalidation, event capture) is scheduled to run** — this is the
   actual remaining blocker on F-009 evidence-consumption reaching a real `explained` verdict,
   now that the schema exists.
5. **`DEFECT-F033-shared-driver-mechanism.md` + its 2026-08-19 addendum** — unrelated to
   Tranche 2, still the highest-priority open item, unaffected by this finding.

No threshold, ratio, or admissibility change results from this document.
