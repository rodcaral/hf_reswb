# Remediation Package — Class B (18,322 `BACKFILL_*`-Owned Rows)

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: design only. Nothing executed. No observation deleted, no `import_run_id` or
`origin_import_run_id` altered, no schema/calibration/policy change, frozen baseline
untouched. Boundary defined below does not use mutable `import_run_id`, per standing
instruction.**

---

## Evidence

Full per-series detail, re-verified by fresh read-only query for this package (all seven
series, not a spot-check):

| Series | Ticker | BACKFILL rows | BACKFILL date range | Non-BACKFILL rows | Non-BACKFILL date range | Overlapping dates |
|---|---|---|---|---|---|---|
| 11323 | MU | 2,867 | 2015-01-02 → 2026-05-28 | 68 | 2026-05-29 → 2026-08-19 | **0** |
| 11324 | MSFT | 2,867 | 2015-01-02 → 2026-05-28 | 69 | 2026-05-29 → 2026-08-19 | **0** |
| 11325 | AMD | 2,867 | 2015-01-02 → 2026-05-28 | 68 | 2026-05-29 → 2026-08-19 | **0** |
| 11326 | MELI | 2,867 | 2015-01-02 → 2026-05-28 | 68 | 2026-05-29 → 2026-08-19 | **0** |
| 11328 | QQQ | 2,867 | 2015-01-02 → 2026-05-28 | 68 | 2026-05-29 → 2026-08-19 | **0** |
| 11329 | AMZN | 2,867 | 2015-01-02 → 2026-05-28 | 68 | 2026-05-29 → 2026-08-19 | **0** |
| 11327 | NU | 1,120 | 2021-12-09 → 2026-05-28 | 68 | 2026-05-29 → 2026-08-19 | **0** |

**Total: 18,322 rows** (2,867 × 6 + 1,120), zero overlapping dates on every one of the seven
series — re-confirmed independently for this package, not carried over unchecked from the
prior boundary analysis.

`byma` absent from `PROVIDER_REGISTRY` and `BACKFILL_` absent from shipped source code
(evidence these rows were written outside the shipped pipeline) is documented by HistFinTS in
the governing framework; not independently re-derived by Workbench, since it requires access
to HistFinTS's own source tree.

---

## Exact proposed scope

`(series_id, observed_at)` such that `series_id ∈ {11323, 11324, 11325, 11326, 11327, 11328,
11329}` **and** `DATE(observed_at) < '2026-05-29'`.

**This scope is defined entirely by series identity and calendar date — it does not reference
`import_run_id` anywhere**, per standing instruction and because ownership of these rows
(which run currently "owns" them via the mutable `import_run_id` field) is not a reliable
boundary: a later legitimate revalidation could in principle have taken ownership of a
`BACKFILL_*`-written row without changing its date, and a date-only scope is immune to that
regardless of which way ownership has moved.

**Why this is safe as a boundary** (not merely convenient): the zero-overlap evidence above
means no legitimate row exists on any date this scope would touch, for any of the seven
series. If a legitimate row *did* exist before 2026-05-29 on any of these series, this scope
would incorrectly catch it — the safety of the date cutoff rests entirely on the zero-overlap
finding, which is why it was re-verified fresh for this package rather than assumed to still
hold.

---

## Proposed mutation (described, not executed)

1. **Export** all 18,322 rows in full, per series, before any change.
2. **Quarantine or delete** the rows matching the scope above. This package does not choose
   between quarantine (retain but mark excluded) and delete (remove entirely) — that choice
   affects the rollback story (§ below) and is left to SE/product.
3. **Preserve** the seven `BACKFILL_*` import runs (58325–58331) regardless of which
   disposition is chosen for the observations — they are the record of how these rows were
   produced.
4. **Separately**, a pipeline correction preventing recurrence of the `BACKFILL_*` mechanism
   is implied by the governing framework but not designed in this package.

No `import_run_id` or `origin_import_run_id` on any surviving row (i.e. any row with
`observed_at >= 2026-05-29`, or any row outside these seven series) is touched.

---

## Independent verification

**Primary**: re-fetch the affected date range (2015-01-02/2021-12-09 → 2026-05-28, per
series) from each series' own legitimate assignment and compare values directly against what
remains (if quarantine) or against the pre-repair export (if delete). Correctness of the
numbers is checked independently of what any provenance field claims — this is the only
verification signal in this package that does not depend on `import_run_id` in any form,
including indirectly.

**Secondary**: `zero_duration_import` count (import runs with `started_at == ended_at`) drops
from 11 to 4 — the remaining 4 being Class A's runs, not this class's. This is a weaker,
supporting signal, not sufficient alone.

**Falsified by**: re-fetched values disagreeing with what remains; the zero-duration count not
dropping as expected.

---

## Rollback

**Depends on the disposition chosen in mutation step 2:**

- **If quarantine**: rollback is trivial — un-mark the quarantined rows. No data is destroyed,
  so this is the lower-risk disposition from a rollback perspective.
- **If delete**: rollback requires the pre-repair export (step 1) to be complete and restored
  exactly, same caveat as Class A — the archive's completeness is the entire rollback
  guarantee, and this package does not itself verify the export schema captures every column.

**A residual limitation regardless of disposition**: per the governing framework's own
"scope problem," rows whose ownership has migrated away from the `BACKFILL_*` runs (visible
only via `import_run_id`, which this package deliberately does not use as a boundary) might
exist outside the date-based scope entirely and would not be touched by this repair at all —
not a rollback concern, but a coverage limitation stated here for completeness.

---

## Unresolved cases

**Value-level re-derivation may not be possible for the full affected range.** The governing
framework states this explicitly: re-derivation is available "only where the provider still
serves that range." This package has not determined which specific dates, within
2015-01-02→2026-05-28, the provider (Yahoo Finance, per the seven series' legitimate
assignments) still serves versus not. **Any date where re-fetch is unavailable should remain
flagged as unresolved rather than assumed correct or assumed safe to delete without
verification** — this is a real, not merely theoretical, limitation on this package's
verification signal, and is not resolved here.

---

## Explicit execution prerequisites

1. SE/product authorization to execute, including a decision on quarantine vs. delete
   disposition (not made by this package).
2. A fresh, complete per-series row export (all columns) immediately preceding execution.
3. A determination of provider re-fetch availability across the full affected date range,
   per series, before claiming the verification signal can be fully satisfied — partial
   coverage should be reported as partial, not rounded up to "verified."
4. Re-confirmation of the zero-overlap finding immediately before execution — this package's
   safety argument depends on it holding at execution time, not only at the time this
   evidence was gathered.
