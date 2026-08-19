# Dispersion Calibration Attempt — Closed as Insufficient Evidence

**Date:** 2026-08-18
**Requested by:** SE
**Nature of this document:** Closure record. No threshold is selected, changed, or promoted.

---

## Disposition

The 2026-08-18 dispersion-calibration attempt on the verified post-May-29 CEDEAR population
(392 observations, 7 pairs) is **closed as insufficient evidence**, not converted into a
calibration result and not used to adjust any parameter.

## What is preserved as evidence

- The full seven-pair implied-FX calculation (`CALIBRATION_EVIDENCE_REOPENED_DISPERSION_
  2026-08-18.md`), computed with all seven pairs retained throughout.
- The machine-precision equality finding: the six-pair group {MU, MSFT, AMD, MELI, AMZN, NU}
  has an internal relative range of 2.25×10⁻¹⁶ (IEEE 754 double-precision machine epsilon)
  across all 54 dates with full coverage — a demonstrated fact, not an inference.
- QQQ's independent deviation pattern (+4.85% mean, 0.83%–10.24% range, 2.43% stdev) as the
  only non-degenerate series in the cohort.
- `DEFECT-F033.md` and its status: blocking, now evidenced quantitatively.

None of this is discarded. It remains available for the next calibration attempt and for
whoever resolves F-033 upstream.

## What is explicitly recorded as not a calibration result

- **`dispersion_threshold` = CV 0.167 remains provisional**, exactly as set by the FDA ruling
  of 2026-08-18 (raw-CEDEAR-price-level era). This attempt neither confirms, refutes, nor
  recalibrates it. It was not compared against, applied as a suppression rule, or treated as
  a baseline for the numbers below.
- **The observed per-date CV distribution (P90 ≈ 0.0302, P95 ≈ 0.0321) is not a population
  calibration result.** It is the numerical output of a sample with effective cross-sectional
  width 2 (one degenerate six-pair block plus QQQ), over one temporal regime. It describes
  this specific insufficient sample, not the panel-coherence behavior of the V0 CEDEAR
  population. It must not be read, cited, or transferred as if it were a calibrated dispersion
  distribution.

## Why closed rather than continued

Per the 2026-08-18 sufficiency reassessment: a cross-sectional dispersion statistic requires
multiple independent members varying against each other to mean anything. This sample has
one such member (QQQ) and one degenerate block. No amount of further computation on this
population changes that — the insufficiency is structural (a data-availability fact), not a
methodology defect that better statistics could work around.

## Next step

A data-gap specification identifying what independent CEDEAR population is required to reopen
calibration with meaningful cross-sectional width is provided separately:
`CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md`.
