# Calibration Infrastructure: Independence and Provenance Safeguards

**Date:** 2026-08-20
**Requested by:** SDT directive — infrastructure and safeguards only, no calibration
conclusions
**Nature of this document:** Engineering record. **No calibration, ratio, threshold, or
admissibility conclusion is drawn by this work.** Nothing was run against live data; nothing
in `docs/DECISIONS.md`'s standing findings is revisited or reopened.

---

## What was built

Two of this project's most expensive-to-repeat manual diagnostics — the F-033 shared-driver
detection and the FK-duplicate-of-source check that both Workbench and HistFinTS independently
rediscovered on 2026-08-19 — are now reusable, tested code rather than one-off scratchpad
scripts:

### `src/hf_reswb/application/independence_detector.py`

Codifies the cross-sectional identity check developed across the F-033 investigation:
- `relative_range()` — the `(max-min)/|median|` primitive used throughout this project's
  manual diagnostics.
- `day_over_day_returns()` — percent-change series, used to detect the returns-locked variant
  found on 2026-08-19 (exact-level circularity resolved, but return correlation stayed
  locked — a ratio fix cannot repair that, since correlation of returns is scale-invariant).
- `classify_cohort_independence()` — classifies every series in a candidate cohort against
  the **per-date median of the whole cohort** (not a pairwise group range, which would let one
  outlier contaminate every other series' statistic — a bug caught by this module's own test
  suite before being shipped, see below), returning `EXACT_IDENTITY`, `RETURNS_LOCKED`, or
  `INDEPENDENT` per series and the cohort's **effective independent width**.
- `MACHINE_EPSILON_RELATIVE_TOLERANCE = 1e-8`: documented explicitly, in the module and here,
  as a **numerical-precision bound, not a financial or statistical threshold**. It answers
  "is this the same computed number," which is upstream of and orthogonal to any
  `dispersion_threshold` calibration question. It is not a candidate for D-046's provisional
  parameters and should never be conflated with one.

### `src/hf_reswb/application/provenance_guard.py`

Codifies the FK-verification check that resolved the 2026-08-19 HistFinTS dispute:
- `verify_fk_target()` — checks a candidate FK target (e.g. `series.underlying_series_id`)
  against the series it's attached to, returning `SUSPECT_DUPLICATE_OF_SOURCE` (the exact
  signature found for the corrupted FK on the seven F-033-affected series — and the specific
  mistake HistFinTS's own first audit made before self-correcting), `IMPLAUSIBLE_RANGE` (an
  optional, caller-supplied plausibility check), `TRUSTED`, or `NO_COMMON_DATES`.
- Explicitly documented as **not** a claim that a `TRUSTED` verdict makes an FK correct for
  production use — only that it does not exhibit the one specific, already-observed failure
  mode this project has now found twice independently.

### Domain model extended

`ExclusionReason` (`src/hf_reswb/domain/panel.py`) gains two members —
`NON_INDEPENDENT_SOURCE` and `PROVENANCE_UNVERIFIED` — so a future panel-eligibility
computation can represent "excluded because it failed an independence/provenance check" using
this project's existing exclusion-record machinery, rather than inventing a new one.

---

## Testing

18 new tests (`tests/test_independence_detector.py`, `tests/test_provenance_guard.py`), all
synthetic data, all passing. Cases mirror the real patterns this project found by hand, not
arbitrary examples:

- Six series sharing one computed origin (the original F-033 signature) → `EXACT_IDENTITY`,
  effective width 1.
- The 2026-08-19 variant — different levels, identical returns → `RETURNS_LOCKED`, still
  collapses to effective width 1.
- A BABA/BIDU/UBER/GLD-style genuinely independent cohort (correlated, never identical) →
  `INDEPENDENT` for all, effective width unchanged.
- A mixed cohort (six locked + one QQQ-style outlier) → effective width 2, matching this
  project's own F-033 finding exactly.
- FK duplicate-of-source, genuine distinct underlying, distinct-but-implausible-range, and
  no-common-dates cases for the provenance guard.

**One implementation bug was caught and fixed by this test suite before being shipped**: the
first version of `classify_cohort_independence` computed a single group-wide range per date
(shared across all series), which let one independent outlier's spread contaminate every
locked series' statistic in a mixed cohort — the test built to mirror the six-plus-QQQ case
failed immediately, and the fix (compare each series against the per-date median, not a
whole-group range) is the same method this project's manual diagnostics used throughout
(residual against panel median). Recorded here because it's a concrete demonstration of why
this infrastructure is worth having: the bug was caught by a test built from an already-known
real case, not discovered later against live data.

**Full suite run**: 63 passed, 1 skipped, 1 failed. The one failure
(`test_ground_truth_against_real_production_series_11312`) is **pre-existing and unrelated**
— it queries the real production database and now finds `configured_interval='1h'` for series
11312, where the test was written against a daily interval. This is consistent with the
intraday-granularity drift already documented elsewhere this session (GLD's intraday rows,
the multi-row-per-date pattern found in the 2026-08-19 reconciliation work) — a live-data
change, not something introduced by this infrastructure work, and out of scope for this
instruction (infrastructure/safeguards only). Flagged, not fixed.

---

## What this does not do

- Does not run against the live PRIMARY or SECONDARY cohorts.
- Does not certify any pair admissible or inadmissible.
- Does not select, propose, or imply a value for `dispersion_threshold` or `staleness_policy`.
- Does not close F-033, the ratio-diagnosis open items, or any other standing finding in
  `DECISIONS.md`.
- Does not modify `panel_eligibility_service.py` or wire these checks into the existing panel
  computation path — that integration (deciding *when* and *how* a real calibration attempt
  should call these functions) is a separate decision, not made here.
