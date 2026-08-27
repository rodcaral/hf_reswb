# Calibration Safeguards — Module Contracts

**Date:** 2026-08-20
**Scope:** documents the input/output contract of `independence_detector.py` and
`provenance_guard.py` for SE/DFA review. **Not a calibration document.** These modules
classify observed conditions; they do not decide admissibility, calibration, threshold, or
policy. No function in either module reads from or writes to the live database, selects a
cohort, or is called from `panel_eligibility_service.py` or any calibration entry point.

---

## `independence_detector.py`

### `relative_range(values: list[float]) -> float`

**Input:** a list of numbers meant to be directly comparable (e.g. implied-FX values for
several series on one date).
**Output:** `(max − min) / |median|`. Returns `0.0` for an empty list or a zero median (never
raises).
**Contract:** pure function, no I/O, no state. This is the shared dispersion primitive both
modules build on — its output is a plain float, not a verdict.

### `day_over_day_returns(values_by_date: dict[str, float]) -> dict[str, float]`

**Input:** one series' `{date_string -> value}`, any date-string format sortable
lexicographically (ISO `YYYY-MM-DD` assumed, not enforced).
**Output:** `{date_string -> percent_change}`, keyed by the *later* date of each transition.
The first date in the input has no return and is omitted. A transition from a zero prior
value is skipped, not raised.
**Contract:** pure function. Does not resample, forward-fill, or infer missing dates — gaps in
the input produce gaps in the output.

### `classify_cohort_independence(values_by_series: dict[str, dict[str, float]]) -> IndependenceReport`

**Input:** `{series_key -> {date -> value}}` for a candidate cohort, already on a comparable
basis (the function does not perform unit conversion or ratio normalization — feeding it raw
price levels of heterogeneously-priced instruments will produce a meaningless classification,
the same trap this project documented for raw-CEDEAR-price CV before the FDA's implied-FX
metric redefinition).
**Output:** `IndependenceReport`:
- `results: list[PairwiseIdentityResult]` — one per input series, each carrying
  `relative_range_levels`, `relative_range_returns` (`None` if too few dates for a return
  series), and `flag: IndependenceFlag`.
- `effective_independent_width: int` — count of groups after collapsing every
  `EXACT_IDENTITY`/`RETURNS_LOCKED` series into one group.
- `groups: list[list[str]]` — the collapsed groups themselves, for inspection.

**Classification rule** (see module docstring for full rationale): a series' value on each
date is compared to that date's cohort median, not to a pairwise group range — this isolates
one outlier from contaminating every other series' statistic. `EXACT_IDENTITY` if the maximum
level residual across all common dates is below `MACHINE_EPSILON_RELATIVE_TOLERANCE`;
`RETURNS_LOCKED` if levels differ but the maximum *return* residual is below the same
tolerance; otherwise `INDEPENDENT`.

**Contract:** pure function, deterministic, no I/O. Empty input returns an empty report
(`effective_independent_width=0`) without raising. Does not mutate its input.

### `MACHINE_EPSILON_RELATIVE_TOLERANCE = 1e-8`

**Not a parameter of any calibration.** A numerical-precision constant distinguishing "the
same computed floating-point number" from "a different number." Two orders of magnitude
looser than true IEEE 754 double-precision epsilon (~2.22e-16) to absorb ordinary arithmetic
drift across different computation paths, and many orders of magnitude tighter than any real
market bid/ask spread or quote-timing difference — the empirical basis (real independent
CEDEARs at 1%–91% relative range vs. the circular pairs at 2.25e-16) is documented in
`DEFECT-F033.md` and `RATIO_DIAGNOSIS_2026-08-19.md`. This value is not exposed as a
configurable calibration input anywhere in this module, and should not be conflated with
`dispersion_threshold` (D-046) if a caller ever wires the two together — they answer different
questions at different stages (is this data point independent at all, vs. how much should
independent members be allowed to disagree).

---

## `provenance_guard.py`

### `verify_fk_target(source_series_id, fk_target_series_id, source_values, fk_target_values, *, expected_min=None, expected_max=None) -> ProvenanceCheckResult`

**Input:**
- `source_series_id`, `fk_target_series_id`: `int` identifiers, carried through to the result
  for traceability only — not looked up or validated against any database.
- `source_values`, `fk_target_values`: `{date -> value}` for the two series being compared.
- `expected_min`, `expected_max`: optional plausible price range for the FK target. If either
  is omitted, the range check is skipped entirely (opt-in, not required).

**Output:** `ProvenanceCheckResult` with `verdict: ProvenanceVerdict`,
`max_relative_range_vs_source: float | None`, `dates_checked: int`, and a human-readable
`detail` string.

**Verdicts, in the order checked:**
1. `NO_COMMON_DATES` — source and target share no dates; nothing else is evaluated.
2. `SUSPECT_DUPLICATE_OF_SOURCE` — target matches the *source itself* (not another cohort
   member — this is a single-pair check, distinct from `independence_detector`'s cohort-wide
   check) to within `MACHINE_EPSILON_RELATIVE_TOLERANCE` on every common date.
3. `IMPLAUSIBLE_RANGE` — target is distinct from the source, but (only if both `expected_min`
   and `expected_max` were supplied) at least one target value falls outside that range.
4. `TRUSTED` — distinct from the source, and within the supplied range if one was given, or
   no range was requested.

**Contract:** pure function, deterministic, no I/O. Never raises on empty or mismatched
inputs — `NO_COMMON_DATES` is a normal return value, not an exception path.
**Explicitly not claimed:** a `TRUSTED` verdict is not a claim that the FK is correct for
production use, financially meaningful, or currently in use anywhere — only that it does not
exhibit the one specific, previously-observed failure mode (a referenced series being a
near-copy of the series that references it).

---

## Domain additions

`hf_reswb.domain.panel.ExclusionReason` gains `NON_INDEPENDENT_SOURCE` and
`PROVENANCE_UNVERIFIED`. Both are `str` enum members like the existing seven; nothing in the
codebase iterates `ExclusionReason` exhaustively (verified — no `match`/`case`, no
serialization schema enumerates all members), so this addition changes no existing behavior.
Neither reason is currently assigned by any production code path — `grep` across
`src/hf_reswb/application/` confirms zero references to either new reason, or to either new
module, outside the modules' own files and this documentation.

---

## Regression coverage, mapped to the real failure modes already identified

| Documented real failure mode | Test | File |
|---|---|---|
| F-033 original signature: six pairs bit-identical, drifting together over time | `test_exact_identity_flagged_f033_pattern` | `test_independence_detector.py` |
| 2026-08-19 returns-locked variant: levels differ, returns still locked, ratio-invariant | `test_returns_locked_but_different_levels_still_flagged` | `test_independence_detector.py` |
| Genuinely independent cohort (BABA/BIDU/UBER/GLD pattern): correlated, never identical | `test_genuinely_independent_cohort_not_flagged` | `test_independence_detector.py` |
| Mixed cohort, QQQ-style exception among a locked six-pair group | `test_mixed_cohort_separates_locked_group_from_independent_outlier` | `test_independence_detector.py` |
| Corrupted FK: `series.underlying_series_id` pointing to a near-duplicate of the source | `test_duplicate_of_source_flagged` | `test_provenance_guard.py` |
| Genuine underlying (the AAPL/BABA/BIDU/UBER/GLD real-underlying pattern) | `test_genuinely_distinct_underlying_trusted` | `test_provenance_guard.py` |
| FK distinct from source but outside a known-plausible range | `test_distinct_but_implausible_range_flagged` | `test_provenance_guard.py` |

Plus edge-case coverage not tied to a specific incident (empty cohort, zero median, single-date
series, no-common-dates FK pair) — 18 tests total, all passing.

---

## Verified: no change to existing production behavior

- `git show --stat` on the introducing commit confirms only `domain/panel.py` (additive enum
  members) and `application/__init__.py` (additive exports) were modified among existing
  files; both new modules and both new test files are new files.
- `grep` confirms zero references to `independence_detector`, `provenance_guard`,
  `NON_INDEPENDENT_SOURCE`, or `PROVENANCE_UNVERIFIED` in `panel_eligibility_service.py`,
  `panel_integration.py`, `calibration_analyzer.py`, or `calibration_utilities.py`.
- Full test suite, rerun for this deliverable: **63 passed, 1 skipped, 1 failed** — identical
  to the pre-existing baseline. The one failure
  (`test_ground_truth_against_real_production_series_11312`) is unchanged, unrelated
  (production series 11312 now reports `configured_interval='1h'` against live data),
  **not modified or fixed by this work**, and remains tracked separately.
- `tests/test_panel_eligibility_phase1.py`, `phase2.py`, `phase3.py`,
  `test_panel_eligibility_integration.py`, and `test_panel_calibration.py` — the direct
  panel-eligibility and calibration-framework suites — rerun in isolation: **35 passed, 1
  skipped**, identical to baseline.

---

## Remaining design dependency

`panel_eligibility_service.py` integration (deciding when and how a real calibration attempt
should call `classify_cohort_independence` or `verify_fk_target`, and what a
`NON_INDEPENDENT_SOURCE`/`PROVENANCE_UNVERIFIED` exclusion should mean for a panel-eligibility
computation in practice) **remains out of scope until SE/DFA explicitly authorize it** — no
integration work has been done or proposed beyond adding the two enum members so the
vocabulary exists for that future decision.
