# Calibration Safeguards: Origin-Provenance Extension

**Date:** 2026-08-20
**Requested by:** SDT directive — review `independence_detector.py`/`provenance_guard.py`
against the newly established `origin_import_run_id` semantics; determine whether the
safeguards should distinguish historical-NULL origin from a post-epoch provenance failure.
**Nature of this document:** design/status report for SE. **No calibration policy or panel
eligibility modified. Not integrated into `panel_eligibility_service.py`. Not used to
authorize PRIMARY calibration.**

---

## What was verified before designing anything

The schema change referenced in the directive was not assumed — checked directly against the
live database first:

- `PRAGMA user_version` is now **15** (was 14 at the time of the prior infrastructure work).
- `observation` gained a new column, `origin_import_run_id INTEGER REFERENCES import_run(id)`,
  nullable, added by `ALTER TABLE` (visible in the live schema dump as appended after
  `updated_at`, outside the original column block).
- **A clean epoch cutover exists**: earliest `created_at` with non-NULL
  `origin_import_run_id` is `2026-08-20T12:08:12.982123+00:00`; latest `created_at` with NULL
  `origin_import_run_id` is `2026-08-19T23:27:28.537258+00:00`. Verified with both directions
  of the boundary check: **zero** post-epoch rows have NULL origin, **zero** pre-epoch rows
  have non-NULL origin (out of 27,961,375 total observations, 11,401 of them post-epoch as of
  the check).
- On sampled post-epoch rows, `origin_import_run_id == import_run_id` — expected: a freshly
  written row hasn't yet had `import_run_id` overwritten by a later revalidation, so the two
  fields coincide until the mutability behavior HistFinTS previously described actually fires
  on a row.

This matches the directive's framing: `origin_import_run_id` is the fix for the mutability
issue in `PROVENANCE_INTEGRITY_import_run_id_mutability.md`, and the historical/post-epoch
distinction is real and cleanly observable, not hypothetical.

---

## Correction to the directive's premise, stated plainly

The directive frames this as distinguishing what `PROVENANCE_UNVERIFIED` already represents
("historical NULL origin") from a new post-epoch case. **`PROVENANCE_UNVERIFIED` does not
currently represent origin-provenance at all.** It was defined in the 2026-08-19 infrastructure
work for a different, series-level concern — an FK target (e.g. `underlying_series_id`) not
yet passing `verify_fk_target`'s duplicate-of-source/plausible-range check — and no code path
assigns it to anything today (confirmed by `grep`: it appears only in its own definition and
this project's documentation). The `origin_import_run_id` NULL states are a **different
provenance axis** (row-level write provenance: which import run first wrote this observation)
from what `PROVENANCE_UNVERIFIED` was built for (series-level reference provenance: does this
FK point somewhere independent). Conflating the two under one `ExclusionReason` would blur a
distinction this project's existing enum design otherwise keeps narrow (`STALE` vs.
`INSUFFICIENT_HISTORY` vs. `COVERAGE_INCOMPLETE` are all single-purpose). This is flagged
rather than silently reinterpreted.

---

## Proposed domain/API change

### `provenance_guard.py` — new function, additive, no change to `verify_fk_target`

`classify_origin_provenance(observation_id, created_at, origin_import_run_id, *, epoch) ->
OriginProvenanceCheckResult`, with `OriginProvenanceVerdict` carrying three values:

| Verdict | Meaning | Live-DB count as of 2026-08-20 |
|---|---|---|
| `ORIGIN_RECORDED` | `origin_import_run_id` populated | 11,401 |
| `HISTORICAL_NULL_ORIGIN` | NULL, `created_at` < epoch — expected, not a defect | 27,949,974 (99.96%) |
| `ORIGIN_MISSING_POST_EPOCH` | NULL, `created_at` ≥ epoch — candidate anomaly | **0** (theoretical case, no observed instance) |

`epoch` is a **required keyword argument with no module-level default** — the empirically
observed cutover is documented in the module and this report, but is deliberately not baked in
as a constant (see "Dependency on HistFinTS verification" below). Enforced by a test
(`test_epoch_is_a_required_argument`) that inspects the function signature rather than relying
on convention.

### `domain/panel.py` — new `ExclusionReason` member

`ORIGIN_PROVENANCE_MISSING`, mapped to `ORIGIN_MISSING_POST_EPOCH` only. **Deliberately no
`ExclusionReason` is proposed for `HISTORICAL_NULL_ORIGIN`** — assigning one would flag 99.96%
of the database as excludable for a condition that is expected and carries no evidentiary
weight. `PROVENANCE_UNVERIFIED`'s definition is annotated to state explicitly that it is
series-level-only and distinct from this new row-level reason, closing the ambiguity the
directive's framing raised.

**Not yet assigned by any production code path** — same status as the prior round's two
additions, added to the vocabulary for a future decision, not wired to panel eligibility now.

### Tests added

`tests/test_provenance_guard.py`, `TestClassifyOriginProvenance` (5 tests, all passing):
`ORIGIN_RECORDED` on a real post-epoch row shape (`origin_import_run_id == import_run_id`,
matching the live sample); `HISTORICAL_NULL_ORIGIN` using the actual observed latest pre-epoch
NULL timestamp; `ORIGIN_MISSING_POST_EPOCH` as the theoretical case (no live instance exists to
test against, stated as such in the test docstring rather than implied to be observed);
epoch-boundary exclusivity (`created_at == epoch` classifies as post-epoch, not historical);
and the required-argument enforcement.

---

## Dependency on the HistFinTS verification result — explicit, unresolved

The epoch used throughout (`2026-08-20T12:08:12.982123+00:00`) is **empirically observed
against the live database at the time this work was done, not confirmed by HistFinTS as an
authoritative migration boundary.** Three specific open questions, none answered by this
report:

1. **Is the cutover guaranteed monotonic going forward?** If a delayed-arrival import run
   from before the migration ever writes a row with an old `created_at` after the fact, the
   "historical" classification by `created_at` comparison would misfire. Not something this
   project can rule out from outside the ingestion pipeline.
2. **Is a historical backfill of `origin_import_run_id` planned?** If HistFinTS backfills the
   27.9M pre-epoch NULLs later, every `HISTORICAL_NULL_ORIGIN` classification made against
   today's snapshot becomes stale the moment that backfill lands, and any caller holding this
   project's current epoch constant would need to know to stop trusting it.
3. **Is `origin_import_run_id` itself guaranteed immutable going forward**, or could a future
   schema/process change re-introduce a mutability gap under a new name — the same failure
   mode `PROVENANCE_INTEGRITY_import_run_id_mutability.md` described for `import_run_id`?

**Recommendation:** before this classification is used for anything beyond the diagnostic
tests in this repository, confirm these three points with HistFinTS directly, the same way
the F-033 dispute was resolved by exchanging exact specifications rather than assumptions.
This report does not file that request — flagging it as the open item for SE to route.

---

## Verification: no behavior change

- Full test suite rerun: **68 passed** (63 + 5 new), 1 skipped, 1 failed — the same
  pre-existing, unrelated failure as before (`test_ground_truth_against_real_production_
  series_11312`, `configured_interval='1h'`), untouched.
- `grep` for `origin_import_run_id`, `ORIGIN_PROVENANCE_MISSING`, `classify_origin_provenance`,
  `OriginProvenance` across `panel_eligibility_service.py`, `panel_integration.py`,
  `calibration_analyzer.py`, `calibration_utilities.py`: zero matches.
- No calibration policy, panel-eligibility computation, or PRIMARY-cohort admissibility
  claim is touched by this work.
