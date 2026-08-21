# Remediation Package — Class D (7 Repointed `underlying_series_id` Values)

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: design only. Nothing executed. No FK repointed, no observation touched, no
`import_run_id` or `origin_import_run_id` altered, no schema/calibration/policy change,
frozen baseline untouched.**

---

## Evidence

**Structural violation** (not a label heuristic): every one of the seven CEDEAR series'
current `underlying_series_id` points at a target series **created after** the referring
series — re-verified by fresh read-only query, exact timestamps below.

| Referrer | Referrer created | Current (wrong) target | Target created | Postdates referrer? | Proposed (correct) target | Target created | Predates referrer? |
|---|---|---|---|---|---|---|---|
| 11323 (MU) | 2026-08-18 16:15:46 | 11342 | 2026-08-18T19:32:06.655209 | **Yes** | 6672 | 2026-08-11T03:45:35.806959Z | **Yes** |
| 11324 (MSFT) | 2026-08-18 16:15:46 | 11348 | 2026-08-18 19:43:28 | **Yes** | 6602 | 2026-08-11T03:45:35.796607Z | **Yes** |
| 11325 (AMD) | 2026-08-18 16:15:46 | 11349 | 2026-08-18 19:43:28 | **Yes** | 426 | 2026-08-11T03:45:30.701515Z | **Yes** |
| 11326 (MELI) | 2026-08-18 16:15:46 | 11350 | 2026-08-18 19:43:28 | **Yes** | 6319 | 2026-08-11T03:45:35.568639Z | **Yes** |
| 11327 (NU) | 2026-08-18 16:15:46 | 11351 | 2026-08-18 19:43:28 | **Yes** | 7085 | 2026-08-11T03:45:36.057637Z | **Yes** |
| 11328 (QQQ) | 2026-08-18 16:15:46 | 11352 | 2026-08-18 19:43:28 | **Yes** | 8193 | 2026-08-11T03:45:36.722574Z | **Yes** |
| 11329 (AMZN) | 2026-08-18 16:15:46 | 11353 | 2026-08-18 19:43:28 | **Yes** | 484 | 2026-08-11T03:45:30.717768Z | **Yes** |

**All seven current targets postdate their referrer by ~3–3.5 hours; all seven proposed
targets predate their referrer by about a week** — a structural asymmetry consistent with the
current pointers being an ingestion artifact (pointing at series that didn't exist yet when
the referrer was created is not possible for a legitimately-resolved reference) rather than a
label-matching error.

**Corroborating evidence, independent of the structural check**: the current targets are the
same series independently identified throughout this project's F-033 work as bit-identical
duplicates of their referring CEDEAR (`DEFECT-F033.md`); the proposed targets are the same
series independently identified via label search plus price-plausibility (e.g. real MSFT
trading $15–542 across 2015–2026) and used throughout this project's F-033 reconciliation
work, including the now-confirmed `RECONCILIATION-F033-2026-08-19.md` finding.

---

## Exact proposed scope

`series.underlying_series_id` for `series.id ∈ {11323, 11324, 11325, 11326, 11327, 11328,
11329}` — **seven metadata field values, zero observation rows.**

---

## Proposed mutation (described, not executed)

Update each of the seven `series.underlying_series_id` values per the map above:

```
11323 → 6672    11326 → 6319    11329 → 484
11324 → 6602    11327 → 7085
11325 → 426     11328 → 8193
```

No `observation` row is touched. No `import_run_id` or `origin_import_run_id` is touched —
this class does not intersect the observation-level provenance concern at all.

**Ordering constraint, restated from the governing framework, unchanged**: this class must be
addressed before Class E, because Class E's shadow-series removal is blocked by
`underlying_series_id`'s `ON DELETE RESTRICT` constraint while it still references those
series.

---

## Independent verification

**Primary — the strongest verification signal in any of the three packages returned today,
because the expected value was established independently and before any repair could
exist to satisfy it**: recompute this project's F-033 implied-FX statistic against the
corrected pointers. It must reproduce **15/21 pairs at exactly `1.000000000000`** — the value
independently confirmed in `RECONCILIATION-F033-2026-08-19.md`, predating this remediation
package by a full day and arrived at through a completely separate line of investigation (the
correlation-discrepancy exchange with HistFinTS). A repair producing any other value is
falsified, not "explained" — this criterion is preserved exactly as specified, not adjusted.

**Secondary**: a structural sweep over **all** series carrying an `underlying_series_id` (not
only these seven), asserting none points at a target created after its own referrer. The
governing framework states this half is explicitly **not** a label heuristic, so a clean
result here is meaningful on its own, unlike Class E's label-based checks.

**Falsified by**: the F-033 statistic not reproducing exactly; any structural violation
remaining anywhere in the series table, not only among these seven.

---

## Rollback

Trivial and complete: seven `UPDATE` statements restoring the prior values
(`{11323→11342, 11324→11348, 11325→11349, 11326→11350, 11327→11351, 11328→11352,
11329→11353}`, captured above and in the frozen baseline's `series_catalog.csv`). No
observation data is involved, so there is no data-loss risk in either direction — this is the
lowest-risk rollback of the three classes in this delivery.

---

## Unresolved cases

**None within the seven-row population itself** — the boundary is exact, the structural
evidence is not heuristic, and the verification value is pre-registered.

**One residual explicitly not resolved by this class**: the governing framework notes "the
*label* half remains a floor — a pointer aimed at a wrong target created on the same day
would not trip the structural signal." This package's evidence (the ~3-hour and ~1-week
timestamp gaps) is comfortably outside same-day ambiguity for all seven, so this residual does
not apply to the seven rows scoped here — but it is restated as a general limitation of the
structural check, not specific to this class's population, should it ever be applied to
series not covered by this package.

---

## Explicit execution prerequisites

1. SE/product authorization to execute (not granted by this package).
2. The pre-repair F-033 statistic re-confirmed at execution time (not merely cited from
   `RECONCILIATION-F033-2026-08-19.md`), so the post-repair comparison is against a
   contemporaneous baseline, not a day-old one, in case anything in the underlying data has
   shifted since.
3. Confirmation that Class E work has **not** begun and is not scheduled concurrently — this
   class must complete first per the `ON DELETE RESTRICT` dependency; running D and E
   concurrently risks an ordering violation even though D itself has no technical blocker.
4. Immediate re-run of both verification signals (F-033 statistic, structural sweep) after
   execution, before this class is considered closed.
