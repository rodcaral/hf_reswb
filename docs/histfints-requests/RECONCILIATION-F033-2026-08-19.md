# F-033 Reconciliation — Point of Divergence Confirmed, Findings Restated

**Date:** 2026-08-19
**Status:** Reconciled. **F-033's shared-driver finding is CONFIRMED**, not disputed.
**No data, ratio, threshold, or calibration policy changed. No admissibility or DFA
escalation.** Per SE's standing instruction, this document reports the reconciliation; it does
not convert it into a calibration or admissibility decision.

---

## What happened

HistFinTS reran the line-by-line comparison package (`LINE_BY_LINE_COMPARISON_PACKAGE_
2026-08-19.md`) and identified the exact point of divergence: their original audit
dereferenced `series.underlying_series_id` as stored, which resolves to a block of duplicate
series created 2026-08-18 19:32–19:43 — not the authoritative catalog series (created
2026-08-11 03:45:xx) Workbench used throughout the F-033 investigation. HistFinTS's original
"methodology artifact" and "deep-history = duplicated USD" conclusions are both withdrawn.

**Independently verified before accepting, not taken on assertion:**

| Claim | Verification |
|---|---|
| Duplicate series (11342, 11348–11353) created 2026-08-18 19:32–19:43 | Confirmed via `series.created_at` |
| Authoritative underlying series (6672, 6602, 426, 6319, 7085, 8193, 484) created 2026-08-11 03:45 | Confirmed via `series.created_at` |
| `BACKFILL_*` import runs created 2026-08-18 20:01:56, ~20–30 min after the duplicates | Confirmed via `import_run.created_at` for all seven `BACKFILL_*` provider assignments |
| MU 2026-08-17: duplicate ≈1,011.62 vs. authoritative 1,011.75 (the "small difference" HistFinTS cites) | Confirmed — duplicate series carries 7 intraday rows that day (last: 1,011.62 at 19:30 UTC), authoritative carries one clean close (1,011.75 at 13:30 UTC) |

This matches HistFinTS's account exactly. The `underlying_series_id` FK does not merely point
to a corrupted series (already known from `DEFECT-F033.md`) — it points to a *different*
corrupted series than the one Workbench had already excluded and worked around, and HistFinTS's
first audit used the FK rather than an independently-identified authoritative series, producing
noise large enough to mask the correlation Workbench had reported (and, separately, to produce
a spurious "implied FX = 1.0" reading when the FK denominator happened to be its own near-copy).

---

## Corrected findings — restated with authoritative denominators, both sides now aligned

**Live window (2026-05-29 → 2026-08-17, 2026-08-18 excluded, exact-timestamp join):**

| Denominator | Correlation min | median | max | Pairs at exactly 1.00 |
|---|---|---|---|---|
| Duplicate (HistFinTS's original) | −0.3776 | 0.0737 | 0.7742 | 0/21 |
| **Authoritative** | −0.1933 | **1.0000** | **1.0000** | **15/21** |

All 15 non-QQQ pairs (MU/MSFT/AMD/MELI/NU/AMZN) at exactly 1.000000000000. Mean implied FX
identical across all six to ten decimal places (1,009.5257641921).

**This corroborates Workbench's own prior, independent result**: `verify_correlation_
artifact.py` (filed 2026-08-19, prior to this exchange) already found — using the same
authoritative underlying ids, a date-only join instead of exact-timestamp, and 2026-08-18
excluded — correlation exactly 1.0000 across the six pairs. Two independently-run
extractions, different join logic, same authoritative denominators, same result.

**Deep history (2015-01-02 → 2026-05-28):** same six pairs at exactly 1.000000000000
correlation over 1,120 common dates; implied FX identical across the five directly-compared
series at the sampled date (277.2473704302) — consistent with Workbench's own deep-history
finding that the shared implied-FX value drifts over time but remains identical across pairs
on any given date (e.g. 14.18 in 2016, 64.95 in 2020, 853.70 in 2024, ~1,008–1,010 in 2026,
independently found in `RESPONSE-F033-reproducibility-package-2026-08-19.md` §3).

**F-033's original claim — shared driver present in both live and backfilled data, not
confined to backfill — is confirmed, not an artifact.**

---

## Withdrawn: "deep-history = underlying USD prices"

HistFinTS's separate claim (implied FX exactly 1.0 across four sampled 2016–2026 dates,
i.e. the CEDEAR series literally storing the underlying's USD price) is withdrawn by HistFinTS
itself — wrong denominator, and generalized from four sampled dates rather than the full
series. Against authoritative denominators, deep-history implied FX is ~277 (an FX-magnitude
value), not 1.0. This matches the reconciliation Workbench had already reached independently
in §3 of `RESPONSE-F033-reproducibility-package-2026-08-19.md`, which flagged the same claim
as likely traceable to the FK before HistFinTS confirmed it.

---

## New, unresolved: QQQ's separate driver

Confirmed by both parties independently: QQQ does not correlate with the other six
(HistFinTS: −0.1933 live, +0.5727 deep, identical across all six of its pairings — "itself a
structured signature"). Consistent with Workbench's own QQQ findings throughout this
investigation (e.g. `CALIBRATION_REOPENED_PROVENANCE_CORRECTED_2026-08-18.md`). **Mechanism
not determined by either party** — second FX series, a ratio difference, or an ETF-specific
path are named as possibilities, none confirmed.

---

## Open items, per HistFinTS, not answered by this reconciliation

1. Origin of the duplicate series block (11342, 11348–11353) — why it exists, what process
   created it 2026-08-18 19:32–19:43.
2. Whether the `underlying_series_id` repointing to the duplicate block was deliberate or an
   ingestion error.
3. QQQ's separate driver mechanism.

## Provenance-integrity scope widened

HistFinTS has extended `PROVENANCE_INTEGRITY_import_run_id_mutability.md` to state that
`series.underlying_series_id` is untrustworthy for these seven series specifically — citing
their own error as the demonstration. Noted for Workbench's own future reference: any FK
traversal in this database should be independently sanity-checked (label + price-plausibility,
as this project has done throughout the F-033 work) rather than trusted as stored, consistent
with this project's standing caution on undocumented/unverified metadata (F-021/D-015).

---

## Status against SE's instruction

| Item | Status |
|---|---|
| Wait for HistFinTS's rerun | ✅ received and reviewed |
| Independently verify before accepting | ✅ timestamps, value discrepancy, and correlation figures cross-checked against this project's own database and prior results — not accepted on assertion |
| Return the resulting reconciliation | ✅ this document |
| Data, ratio, threshold, or calibration policy changed | ❌ none |
| Admissibility or DFA escalation | ❌ none |

**F-033 status: confirmed, not disputed. Still blocking** — the reconciliation identifies the
cause of the *dispute*, not a resolution of the underlying defect. The seven pairs' shared
driver (six of seven; QQQ separately unexplained) remains unresolved and the original defect
filing (`DEFECT-F033-shared-driver-mechanism.md`) stands as filed.
