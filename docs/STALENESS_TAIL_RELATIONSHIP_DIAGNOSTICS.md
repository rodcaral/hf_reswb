# Staleness Tail/Relationship Diagnostics

**Date:** 2026-08-18  
**Requested by:** FDA (D-046 directive)  
**Analysis:** Empirical tail behavior and relationship analysis  
**Cohort:** Primary CEDEAR (5 pairs: AAPL, BABA, BIDU, UBER, GLD)  
**Period:** 2020-01-02 to 2026-08-18  
**Status:** Complete; No threshold selected

---

## Part 1: Empirical Gap Distribution

**Aggregate across all 5 pairs: 6,136 inter-observation gaps**

| Metric | Value |
|--------|-------|
| Min gap | 1 day |
| Max gap | 7 days |
| Mean | 1.50 days |
| Median | 1 day |
| Stdev | 0.98 |
| **P95** | **3 days** |
| P90 | 3 days |
| P75 | 1 day |
| P50 | 1 day |
| P25 | 1 day |
| P10 | 1 day |
| P5 | 1 day |
| P99 | 5 days |

### Pair-Level Comparison

| Pair | Observations | Gaps | Min | Max | Mean | P95 |
|------|--------------|------|-----|-----|------|-----|
| AAPL | 1,617 | 1,616 | 1d | 7d | 1.50d | 3d |
| BABA | 1,569 | 1,568 | 1d | 7d | 1.50d | 3d |
| BIDU | 1,568 | 1,567 | 1d | 7d | 1.50d | 3d |
| GLD | 470 | 397 | 1d | 7d | 1.52d | 3d |
| UBER | 989 | 988 | 1d | 7d | 1.50d | 3d |

**Key:** All pairs show identical P95 = 3 days. No outlier pair. Homogeneous cohort.

---

## Part 2: Structural Period Classification

### Gap Distribution by Structural Period

| Period | Gaps | Mean | P95 | Notes |
|--------|------|------|-----|-------|
| **F-009:early-reconciliation** (2020-2024) | 4,151 | 1.50d | 3d | Majority of gaps; no elevation |
| **F-009:clean-period** (2025+) | 1,985 | 1.49d | 3d | Post-2024; consistent with early |
| **F-021:pre-step** (before 2024-01-24) | 3,228 | 1.50d | 3d | AAPL ratio step pre-boundary |
| **F-021:post-step** (2024-01-24+) | 2,908 | 1.49d | 3d | Post-step; no increase in staleness |
| **regime:pre-crisis** (pre-2022) | 1,355 | 1.51d | 3d | Early period; normal |
| **regime:crisis** (2022-2023) | 1,809 | 1.50d | 3d | ARS crisis; no staleness impact |
| **regime:post-crisis** (2024+) | 2,972 | 1.49d | 3d | Normalized; consistent |
| **event:covid-peak** (2020-03 to 2020-06) | 218 | 1.57d | 4d | Slight elevation; small sample |
| **event:ars-crisis** (2022-2023) | 1,809 | 1.50d | 3d | Matched to crisis regime; no effect |

**Finding:** No structural period, event, or regime elevates staleness. All periods preserve P95 <= 3d.

---

## Part 3: Tail Behavior — Candidate Window Analysis

### Gaps Exceeding Each Threshold

| Threshold | Gaps Exceed | % of Total | Exclusion Impact |
|-----------|-------------|------------|------------------|
| 2d | 1,323 | 21.6% | Substantial (1 in 5) |
| 3d | 239 | 3.9% | Moderate (1 in 25) |
| 4d | 107 | 1.7% | Minor (1 in 60) |
| 5d | 5 | 0.1% | Negligible |
| 6d | 5 | 0.1% | Negligible |
| 7d | 0 | 0.0% | Empty (observed maximum) |
| 10d | 0 | 0.0% | Empty |
| 14d | 0 | 0.0% | Empty |

**Interpretation:**
- **Sharp elbow** between 3d and 4d: 3.9% → 1.7%
- **Flat tail** beyond 4d: all thresholds ≥5d are empirically equivalent (empty)
- **P95 = 3d** sits at natural break point but does not constrain threshold selection
- **No empirical reason to select 5d, 10d, 15d or higher** — all show zero or negligible exclusion

---

## Part 4: Relationship to Dispersion & Evidence-Quality Events

### Staleness-Dispersion Orthogonality

| Dimension | Finding |
|-----------|---------|
| High-dispersion dates (CV > 0.20) | 1,293 dates |
| High-dispersion dates with preceding gap >3d | 1 date (0.1%) |
| Interpretation | Staleness and dispersion are **independent** filtering dimensions |

**Conclusion:** Large gaps do not correlate with elevated dispersion. The two measures capture different phenomena and can be filtered independently.

### Evidence-Quality Event Co-occurrence

**F-009 (Reconciliation uncertainty, 2020-2024):**
- Early period: 4,151 gaps with P95 = 3d
- Clean period: 1,985 gaps with P95 = 3d
- **No gap elevation** in early vs. clean periods

**F-021 (AAPL ratio step, 2024-01-24):**
- Pre-step: 3,228 gaps with P95 = 3d
- Post-step: 2,908 gaps with P95 = 3d
- **No gap increase** across structural boundary

**Regime Transitions:**
- Pre-crisis → Crisis → Post-crisis: uniform P95 = 3d
- No elevation during Argentine FX crises (2022-2023)
- COVID period shows minor elevation (1.57d mean, 4d P95) but sample is small (218 gaps)

---

## Summary & Findings

### Key Observations

1. **Empirical tail is benign:**
   - P95 = 3 days across entire cohort
   - P99 = 5 days (only 60 gaps)
   - Maximum = 7 days (all pairs, all periods)
   - No gap exceeds 7 days

2. **Candidate windows show graduated impact:**
   - 2d: 21.6% exclusion (too aggressive)
   - 3d: 3.9% exclusion (moderate)
   - 4d: 1.7% exclusion (light)
   - 5d+: <0.1% exclusion (empirically empty)

3. **No structural period drives elevated staleness:**
   - F-009 early/clean: identical distributions
   - F-021 pre/post: no step change
   - Regimes (crisis/post-crisis): parallel behavior
   - All maintain P95 <= 3 days

4. **Staleness and dispersion are orthogonal:**
   - High dispersion does not cluster around large gaps
   - Independent filtering dimensions confirmed
   - Can be calibrated separately

5. **Cohort is homogeneous:**
   - All 5 pairs: P95 = 3 days
   - No outlier pair or relationship type
   - Unified treatment appropriate

### Why No Threshold Selected

**Empirical data does not constrain threshold selection:**
- Gap distributions show minimal exclusion at conventional thresholds (5d, 10d, 15d, 20d)
- The natural break (sharp elbow at 3-4d) indicates the range where observations actually differ
- Beyond 4d, all thresholds are empirically equivalent (zero exclusion)
- **Threshold selection must therefore be domain-driven**, not data-driven

**Domain-driven factors to consider:**
- Working-day tolerance (weekends/holidays vs. consecutive trading days)
- Regime-specific liquidity expectations (crisis vs. normal)
- Use case (ratio change detection vs. reference rate vs. trading execution)
- Panel depth and cross-sectional redundancy

### Diagnostic Value

This analysis confirms:
- **No evidence-quality problem** with staleness in the primary cohort
- **No regime-dependent staleness escalation** that would require conditional thresholds
- **Clean separation** between staleness and dispersion dimensions
- **Foundation for domain judgment** on acceptable staleness tolerance

---

## Recommendations

1. **Do not select a numerical threshold** based on empirical tail
2. **Preserve all structural periods** in classification — none elevates staleness
3. **Apply independent filtering** for staleness and dispersion
4. **Next step:** FDA domain judgment on acceptable working-day tolerance per use case
5. **No production deployment** of staleness criterion until FDA provides domain guidance

---

## Segmentation Summary for Reference

All structural periods preserved and available for downstream analysis:

- F-009:early-reconciliation (4,151 gaps)
- F-009:clean-period (1,985 gaps)
- F-021:pre-step (3,228 gaps)
- F-021:post-step (2,908 gaps)
- regime:pre-crisis (1,355 gaps)
- regime:crisis (1,809 gaps)
- regime:post-crisis (2,972 gaps)
- event:covid-peak (218 gaps)
- event:ars-crisis (1,809 gaps)

No gaps excluded from analysis. Structural periods are marked, not filtered.

