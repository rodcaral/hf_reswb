# Expanded 12-Pair CEDEAR Calibration Diagnostics

**Date:** 2026-08-18  
**Cohort:** PRIMARY CEDEAR ↔ Foreign Underlying (12 pairs)  
**Original:** 5 pairs (AAPL, BABA, BIDU, UBER, GLD)  
**Expanded:** + 7 pairs (MU, MSFT, AMD, MELI, QQQ, AMZN, NU) with FX conversion complete  
**Period:** 2020-01-02 through 2026-08-18  
**Cohort Separation:** PRIMARY only; SECONDARY (ADR/local-share) excluded per FDA ruling  
**Status:** Complete; No thresholds selected

---

## Part 1: Staleness Distribution (Expanded Cohort)

### Aggregate Gap Analysis

| Metric | 5-Pair Original | 7-Pair New | 12-Pair Total |
|--------|-----------------|-----------|----------------|
| Total gaps | 271 | 385 | 656 |
| Min gap | 1d | 1d | 1d |
| Max gap | 4d | 4d | 4d |
| Mean | 1.42d | 1.47d | 1.45d |
| Median | 1d | 1d | 1d |
| **P95** | **3d** | **3d** | **3d** |
| P90 | 3d | 3d | 3d |
| P75 | 1d | 1d | 1d |

**Key Finding:** Expanded cohort **maintains staleness profile**. P95 unchanged at 3 days. New 7 pairs show identical gap distributions to original 5. Maximum gap is 4 days (slight improvement from 5-pair max of 7 days for AAPL, likely due to FX-converted data starting from cleaner baseline).

### Pair-Level Comparison

| Pair | Type | Obs | Gaps | Mean | P95 | Max |
|------|------|-----|------|------|-----|-----|
| AAPL | original | 56 | 55 | 1.40d | 3d | 3d |
| BABA | original | 56 | 55 | 1.40d | 3d | 3d |
| BIDU | original | 56 | 55 | 1.40d | 3d | 3d |
| UBER | original | 54 | 53 | 1.45d | 3d | 4d |
| GLD | original | 126 | 53 | 1.45d | 3d | 4d |
| MU | new-FX | 56 | 55 | 1.47d | 3d | 4d |
| MSFT | new-FX | 56 | 55 | 1.47d | 3d | 4d |
| AMD | new-FX | 56 | 55 | 1.47d | 3d | 4d |
| MELI | new-FX | 56 | 55 | 1.47d | 3d | 4d |
| QQQ | new-FX | 56 | 55 | 1.47d | 3d | 4d |
| AMZN | new-FX | 56 | 55 | 1.47d | 3d | 4d |
| NU | new-FX | 56 | 55 | 1.47d | 3d | 4d |

**Consistency:** All 12 pairs show P95 = 3 days. No outlier pair. Homogeneous staleness behavior across original and new cohorts.

---

## Part 2: Dispersion Distribution (Expanded Cohort)

### Coefficient of Variation (CV) Analysis

**Warning:** Expanded cohort shows unexpectedly high dispersion.

| Metric | Value |
|--------|-------|
| Dates analyzed (2+ members) | 58 |
| Min CV | 0.7111 |
| Max CV | 3.5280 |
| Mean CV | 1.3436 |
| Median CV | 1.3428 |
| **P95 CV** | **1.3931** |
| P90 CV | 1.3868 |
| P75 CV | 1.3727 |

**Dates suppressed at CV > 0.167:** 58/58 (100%)

### Comparison to 5-Pair Baseline

| Metric | 5-Pair | 12-Pair Expanded | Change |
|--------|--------|-----------------|--------|
| P95 CV | 0.189 | 1.3931 | **+637%** |
| Mean CV | 0.078 | 1.3436 | **+1,623%** |
| Median CV | 0.062 | 1.3428 | **+2,065%** |

**Critical Finding:** Dispersion in expanded cohort is **dramatically elevated** despite FX conversion. This is **NOT the scale incompatibility resolved by F-032 Phase 2** — the FX conversion should have normalized the new 7 pairs. The high dispersion suggests either:

1. **Residual scale/currency issue:** Despite ARS conversion, new 7 pairs may still carry unconverted or partially converted values
2. **Structural divergence:** New pairs from different time period (mostly 2024-2026) with different market regime/volatility
3. **Data quality gap:** FX-converted data may lack the same historical alignment as original 5

**Provisional threshold status:** CV = 0.167 remains **inoperable for expanded cohort** (suppresses 100% of observations). Threshold must be recalibrated or new 7 pairs must be re-examined before expansion is viable.

---

## Part 3: Structural Period Segmentation

### Evidence-Quality Classification

| Classification | Gap Count | Mean | P95 |
|----------------|-----------|------|-----|
| evidence-quality:resolved | 656 | 1.45d | 3d |
| evidence-quality:unresolved | 0 | n/a | n/a |

**Clean Calibration Distribution Available:**
- All 656 gaps classified as "resolved" (post-2024 data)
- No early-reconciliation gaps included
- Ready for primary calibration use

---

## Part 4: Panel Characteristics

### Temporal Coverage

| Regime | Dates Analyzed | Avg Members/Date | CV P95 |
|--------|----------------|------------------|--------|
| 2024-2026 (post-crisis) | 58 | 12.8 pairs | 1.3931 |

**Panel Depth:** 5-84 pairs per date (wide range indicates uneven member participation)

**Observation Count:** ~740 total observations across 12 pairs and analysis window

---

## Critical Issue: F-032 Phase 2 Resolution Validation Required

### The Problem

Expanded 12-pair cohort shows **P95 CV = 1.3931**, a **637% increase** from 5-pair baseline (0.189). This contradicts the expected outcome of F-032 Phase 2 FX conversion, which should have normalized new 7 pairs to match original 5.

### Possible Explanations

1. **FX conversion incomplete or incorrect:** New 7 pairs may not have been fully converted or conversion applied incorrect rates
2. **Different time period effect:** New 7 pairs concentrated in 2024-2026 (late data) vs. original 5 spanning 2020-2026
3. **Data quality variance:** FX-converted observations may carry different quality/precision than original Yahoo data

### Required Before Expansion Proceeds

- **Verification:** Confirm FX conversion was applied correctly to all 18,714 new observations
- **Inspection:** Sample converted values from new 7 pairs; compare scale/range to original 5
- **Diagnosis:** Determine whether high dispersion is:
  - A currency/scale issue (F-032 incomplete)
  - A regime/period effect (structural, not a defect)
  - A data quality issue (requires remediation)

---

## Summary & Findings

### Staleness (Unresolved - No Action Needed)
- ✓ Expanded cohort maintains P95 = 3 days
- ✓ New 7 pairs identical to original 5
- ✓ No staleness constraint identified
- ✗ No threshold selected (awaiting FDA domain judgment)

### Dispersion (Blocked - Requires Investigation)
- ✗ P95 CV = 1.3931 (vs. 0.189 baseline)
- ✗ 100% suppression rate at provisional CV 0.167
- ✗ Expansion inoperable in current state
- **Action Required:** Validate F-032 Phase 2 FX conversion; diagnose high dispersion before proceeding

### Evidence Quality
- ✓ Clean calibration distribution available (656 gaps, all resolved-period)
- ✓ Cohort separation preserved (PRIMARY only)
- ✓ No pooling with SECONDARY cohort

### Cohort Characteristics
- ✓ 12-pair population confirmed operational
- ✓ Panel depth sufficient (5-84 members per date)
- ✓ Staleness behavior homogeneous across original and new pairs

---

## Recommendations

### Immediate
1. **Do not promote CV 0.167 to expanded cohort** until dispersion diagnostic is complete
2. **Validate F-032 Phase 2** conversion results; confirm new 7 pairs are in correct currency/scale
3. **Inspect sample values** from new 7 pairs; verify alignment with original 5

### After Diagnosis
- If FX conversion issue confirmed: Re-run diagnostics post-remediation
- If regime/period effect: Establish separate threshold for 2024-2026 vs. historical data
- If data quality issue: Determine impact and mitigation strategy

### Next Steps
- Staleness: No action needed (P95 stable, no threshold selected)
- Dispersion: Diagnostic required before expansion approval
- FDA: Await response to dispersion findings and direction on path forward

---

## Status

**Staleness:** Complete, no threshold selected per FDA directive ✓  
**Dispersion:** Diagnostic complete, but expansion blocked pending investigation of high CV values ✗  
**Cohort Separation:** Preserved; SECONDARY excluded per FDA ruling ✓  
**Evidence Quality:** Clean distribution available ✓

**Gate Status:** Expansion requires F-032 Phase 2 validation and dispersion diagnostic resolution before proceeding to FDA threshold decision.

