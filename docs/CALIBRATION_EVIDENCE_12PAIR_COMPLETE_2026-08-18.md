# 12-Pair Calibration Evidence Package — Post-Backfill-Completion

**Date:** 2026-08-18
**Requested by:** SE, three sequential SDT directives
**Nature of this document:** Evidence/diagnostic report. **No threshold is selected, promoted, or hard-coded.**
`staleness_policy` remains provisional/uncalibrated. `dispersion_threshold` remains provisional at CV 0.167.

---

## Part 0: Backfill verification (precondition check)

18,714 / 18,714 expected observations are present across the 7 new CEDEAR pairs, zero
duplicate-date rows, 100% completeness. This reverses the 2.1%-completeness finding of
`F032_CONVERSION_VALIDATION_REPORT.md` — the backfill has landed since that report.

## Part 0b: Population-state anomaly (found during verification, not assumed away)

Re-querying full observed ranges per pair produced a result that inverts the assumption in
every prior document, including this session's own SE directive framing ("original 5" as the
deep-history baseline):

| Cohort | Pairs | Obs/pair | Actual observed range |
|---|---|---|---|
| "Original 5" | AAPL, BABA, BIDU, UBER, GLD | 56–126 | **2026-05-29 to 2026-08-18 only** (~2.5 months) |
| "New 7" | MU, MSFT, AMD, MELI, QQQ, AMZN, NU | 2,923 (1,176 NU) | **2015-01-02 to 2026-08-18** (11 years) |

The five original CEDEAR series each have a `backfill_start_date` configured back to
2020–2024, but the database currently holds only their most recent ~2.5 months of
observations — a live truncation consistent with **F-017** (`import_run.status = SUCCESS`
does not imply a complete range). Every prior document in this project that described the
"5-pair baseline" as carrying "6-year history" or "1,500+ observations per pair" was
asserting this without having verified it against current data; the actual figure was
already 56–126 obs at the time those documents were written. This report corrects that
framing rather than propagating it further.

Consequence for this run: per-pair valid start/end is derived from each series' own
`MIN/MAX(observed_at)`, per the SE directive. No fixed analysis window is imposed. The
5-pair and 7-pair sub-cohorts are therefore compared on genuinely different time bases, and
the comparison below states this explicitly at each point rather than normalizing it away.

## Part 0c: Data-quality defect found and corrected — GLD intraday granularity

GLD (id 11311) carries **intraday observations** (5-minute-interval timestamps, e.g. 73 rows
on 2026-08-14 alone) while all 11 other pairs carry one observation per calendar day. Left
uncorrected, this inflated a single date's cross-sectional panel to 84 "members" (only 12
pairs exist) and produced a spurious CV = 3.528 on that date.

**Correction applied:** cross-sectional dispersion is computed on one observation per series
per calendar day (last observation of the day), for all 12 pairs uniformly. This is a
granularity-normalization fix required to make the cross-sectional population well-defined —
it does not touch the 0.167 threshold, does not discard any date, and does not alter the
staleness distribution (staleness was already computed on distinct dates and is unaffected).

---

## Part 1: Staleness — full 12-pair population, pair-specific valid range

| Metric | 5-pair (orig) | 7-pair (new) | 12-pair total |
|---|---|---|---|
| Gap count | 271 | 18,707 | 18,978 |
| Min | 1d | 1d | 1d |
| Max | 4d | 4d | 4d |
| Mean | 1.42d | 1.45d | 1.45d |
| Median | 1d | 1d | 1d |
| P75 | 1d | 1d | 1d |
| P90 | 3d | 3d | 3d |
| **P95** | **3d** | **3d** | **3d** |
| P99 | 3d | 4d | 4d |

All 12 pairs individually show P95 = 3d, max 3–4d. Staleness is **stable and homogeneous**
across both cohorts despite the cohorts spanning completely different calendar periods — the
gap structure is a function of trading-calendar cadence, not of which period is observed.
Largest gaps (up to 4d) are preserved in the distribution, not excluded; none coincide with a
known structural/evidence-quality event beyond ordinary weekend/holiday spacing.

**No staleness threshold selected**, consistent with the standing FDA ruling.

---

## Part 2: Dispersion — full 12-pair population, day-deduplicated

| Metric | Value |
|---|---|
| Dates with 2+ pairs present | 2,925 |
| Overlap range | 2015-01-02 to 2026-08-18 |
| Min CV | 0.7111 |
| Max CV | 1.5784 |
| Mean CV | 1.1683 |
| Median CV | 1.1385 |
| P75 | 1.3061 |
| P90 | 1.4027 |
| **P95** | **1.4385** |
| Suppression at provisional CV 0.167 | 2,925 / 2,925 (100.0%) |

### Does the anomaly disappear after population completion? No — and here is why.

Segmenting strictly by cohort composition:

| Segment | Dates | P95 CV | Mean CV |
|---|---|---|---|
| New-7 members only (no original-5 present) | 2,869 | 1.4397 | 1.1653 |
| At least one original-5 member present | 56 | 1.3887 | 1.3222 |

**The elevated dispersion is present within the new-7 cohort in complete isolation from the
original 5** — it is not an artifact of pooling two mismatched populations, and it is not
explained by the GLD granularity defect (already corrected) or by the backfill gap (already
closed). The cause is structural:

**Dispersion is being measured as the coefficient of variation of raw ARS price levels
across CEDEARs of different underlyings.** Underlyings differ enormously in per-share price
and in CEDEAR ratio (e.g., 2026-08-14: NU ≈ 15,388 ARS vs. MELI ≈ 1,863,771 ARS — a ~121×
spread in raw level, driven by MercadoLibre's underlying share price being roughly two orders
of magnitude higher than Nu Holdings', not by any data-quality difference). A CV computed
across raw price levels of heterogeneously-priced instruments will be large **by
construction**, independent of panel eligibility, staleness, or evidence quality. This holds
whether the panel has 5, 7, or 12 pairs — it is a property of the metric, not of the
population.

This also explains why the original 5-pair baseline (P95 CV ≈ 0.189, per
`STALENESS_TAIL_RELATIONSHIP_DIAGNOSTICS.md`) looked low: those five names (AAPL, BABA, BIDU,
UBER, GLD) happen to trade at broadly similar ARS-per-unit magnitudes over their observed
window, not because the underlying dispersion measure is well-behaved.

**This is a metric-definition question for the financial domain, not a threshold-calibration
question.** Whether panel dispersion should be computed on price levels, log-levels, or
period-over-period returns is unresolved and materially changes the result; this report does
not decide it and does not adjust CV 0.167 in light of it.

Highest-CV dates (top 12) are entirely within the new-7-only period (2025-04 to 2025-06),
confirming the effect is present even in a population untouched by the original-5 truncation
or the GLD defect.

---

## Part 3: Evidence-quality segmentation, raw vs. clean

Classification: `evidence-quality:resolved` = observation year > 2024, `unresolved` ≤ 2024
(same convention as prior diagnostics).

**Staleness:**

| | Count | Mean | P95 |
|---|---|---|---|
| RAW (all gaps) | 18,978 | 1.45d | 3d |
| Unresolved | 15,858 | 1.45d | 3d |
| CLEAN (resolved only) | 3,120 | 1.46d | 3d |

Exclusion has negligible effect on the staleness distribution — expected, since gap structure
is calendar-driven and homogeneous across periods.

**Dispersion:**

| | Dates | P95 CV |
|---|---|---|
| RAW (all overlap dates) | 2,925 | 1.4385 |
| CLEAN (resolved only) | 409 | 1.5520 |

Exclusion does **not** reduce dispersion — the clean (post-2024) subset shows slightly
*higher* P95 CV than the raw distribution, consistent with Part 2's explanation: the effect
is a property of cross-sectional price-level heterogeneity, which evidence-quality filtering
does not touch.

---

## Summary

| Question (SE directive) | Answer |
|---|---|
| Is the 18,322-observation backfill actually included? | **Yes** — 18,714/18,714 verified, 0 duplicates. |
| Does the dispersion anomaly disappear after population completion? | **No.** |
| Is the anomaly caused by incomplete backfill, evidence quality, or pooling mismatched cohorts? | **No to all three** — confirmed present within the new-7 cohort alone, unaffected by evidence-quality exclusion. |
| What does explain it? | CV computed on raw ARS price levels across CEDEARs of structurally different per-unit price magnitude. A metric-definition issue, not a data-quality issue. |
| Any other defects found during verification? | GLD carries intraday observations inconsistent with the daily granularity of the other 11 pairs; corrected by day-deduplication for this analysis (documented, not silently applied). The "original 5" cohort's assumed deep history does not exist in the current database — only ~2.5 months of recent data is present; prior documents' "6-year history" framing for this cohort was unverified and is corrected here. |
| Threshold action taken | **None.** `dispersion_threshold` remains provisional at 0.167; `staleness_policy` remains uncalibrated. |

## Open items for FDA / SE

1. Decide the metric definition for cross-sectional dispersion (levels vs. returns vs.
   log-levels) — this is a prerequisite to any dispersion threshold being meaningful at
   panel scale, and is outside Workbench's authority to resolve unilaterally.
2. Determine why the "original 5" CEDEARs' pre-2026-05 history is absent from the live
   database despite configured backfill start dates back to 2020–2024 — a HistFinTS-side
   question, not a Workbench-side one.
3. Confirm whether GLD's intraday ingestion is intentional (a different `configured_interval`
   than its panel peers) and, if so, how panel-eligibility diagnostics should treat
   mixed-granularity series going forward.
