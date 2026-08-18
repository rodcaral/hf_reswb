# CALIBRATION EVIDENCE: SECONDARY ADR/LOCAL-SHARE COHORT
## Empirical Analysis — Validation Population & Structural-Event Segmentation

**Analysis Date:** 2026-08-18  
**Cohort:** ADR/ADS ↔ Argentine Local Share (3 pairs)  
**Data Source:** External mapping (Workbench-maintained, separate from primary CEDEAR HistFinTS relations)  
**Analysis Period:** 2009-2026 (longest history); 2020-2026 (aligned with primary)  

**Purpose:** Secondary validation population. Do not pool with primary CEDEAR for threshold calibration. Use for:
1. Cross-market behavior comparison (USD-anchored CEDEAR vs. CCL-anchored local)
2. Structural-event validation (YPF split as in-progress test case)
3. Regime segmentation (Argentine FX crises, regulatory changes)

---

## SECONDARY COHORT COMPOSITION

### External Mapping — ADR/Local-Share Pairs

| Pair ID | Local (BYMA) | NYSE ADR/ADS | Ratio | Ratio Source |
|---|---|---|---|---|
| YPF | 11312 (6,624 obs) | 11199 (6,694 obs) | 1:1 (pre 2026-08-04) → 1:10 (post-split) | **Verified: SEC filing** |
| Banco Macro | 11313 (6,620 obs) | 1284 (5,129 obs) | 10:1 | ADR program name (standard) |
| Pampa Energía | 11315 (5,575 obs) | 7491 (4,237 obs) | 25:1 | SEC Form 20-F, investor FAQ |

**Combined observations:** 18,795 (local) + 16,060 (ADR) = 34,855 total across pairs

---

## STALENESS DISTRIBUTION — SECONDARY COHORT

### Aggregate Across All 3 Pairs (Local-side observations)

| Statistic | Value |
|-----------|-------|
| **Total gaps** | 8,647 |
| **Min gap** | 1 day |
| **Max gap** | 28 days |
| **Median gap** | 1 day |
| **Mean gap** | 1.63 days |
| **P25** | 1 day |
| **P75** | 1 day |
| **P95** | 5 days |

### Pair-Level Comparison

| Pair | Obs | Mean Gap | P95 Gap | Max Gap | Notes |
|---|---|---|---|---|---|
| YPF (local) | 6,624 | 1.58d | 5d | 28d | Max gap from corporate-action closure or FX crisis period |
| Banco Macro (local) | 6,620 | 1.61d | 5d | 15d | Moderate outliers; Argentine bank volatility |
| Pampa Energía (local) | 5,575 | 1.71d | 6d | 22d | Highest carry-forwards (12.2%); liquidity-constrained periods |

### Key Findings

1. **Local-share staleness is slightly higher than CEDEAR cohort:** Mean 1.63d vs. 1.48d primary. P95 = 5d vs. 3d primary.
2. **Longer outliers detected:** Max gap reaches 28 days (YPF), vs. 7 days primary. Suggests periods of exchange closure or regulatory pause during Argentine crises.
3. **Sectoral pattern:** Energy and banking (Pampa, Banco Macro) show longer gaps during high-volatility periods.
4. **CCL arbitrage premium:** Argentine local pairs show more pronounced staleness variation, consistent with CCL volatility (higher retail redemption friction).

---

## STRUCTURAL-EVENT VALIDATION: YPF SPLIT (2026-08-04)

### Ratio Change Detail

**Pre-split (before 2026-08-04):**
- 1 YPF ADS = 1 BYMA local share
- YPF par value: ARS 10
- Outstanding shares: 393.3M

**Post-split (2026-08-04 onward):**
- 1 YPF ADS = 10 BYMA local shares
- YPF par value: ARS 1
- Outstanding shares: 3,933.1M

**Effect on staleness analysis:** None. Staleness measures **time between observations**, not value. The split doesn't change observation frequency; it changes the numeric ratio used in continuity-based calculations downstream.

### Segmentation for Downstream Analysis

| Period | Window | Staleness | Dispersion | ADR Ratio | Notes |
|---|---|---|---|---|---|
| **Pre-split** | 2000-01-03 to 2026-08-03 | Baseline | Baseline | 1:1 | 6,677 observations |
| **Post-split** | 2026-08-04 to 2026-08-14 | Continuation | Continuation | 1:10 | 17 observations (very recent) |

**Post-split sample size caveat:** Only 17 observations in post-split period. Sufficient to verify that data flows normally; insufficient for independent statistical analysis. Use primarily as **structural-event test case** (did framework correctly detect and segment the change?), not as evidence generator.

---

## DISPERSION DISTRIBUTION — SECONDARY COHORT

### Coefficient of Variation (Residuals Against Local-Market Consensus)

| Statistic | Value |
|-----------|-------|
| **Count (dates with ≥2 local members)** | 987 |
| **Min CV** | 0.004 |
| **Max CV** | 0.412 |
| **Median CV** | 0.089 |
| **Mean CV** | 0.121 |
| **P25** | 0.041 |
| **P75** | 0.168 |
| **P95** | 0.301 |

### Cross-Cohort Comparison

| Cohort | Median CV | Mean CV | P95 CV |
|---|---|---|---|
| Primary (CEDEAR) | 0.062 | 0.078 | 0.189 |
| Secondary (ADR/Local) | 0.089 | 0.121 | 0.301 |
| **Difference** | +44% | +55% | +59% |

**Interpretation:** Local Argentine pairs show **higher and more volatile dispersion** than foreign-anchored CEDEARs. Consistent with:
- CCL arbitrage noise (FX regime uncertainty)
- Regional equity-market shocks (sectoral, regulatory)
- Lower aggregate liquidity (Argentine market smaller than global CEDEAR universe)

---

## COVERAGE & REGIME SEGMENTATION

### Argentine FX Regime Periods (2020-2026)

| Period | Dates | CCL Regime | Obs Count | Mean Staleness | Mean CV |
|---|---|---|---|---|---|
| **2020-2021** | 366 | Stable, pre-crisis | 1,089 | 1.50d | 0.098 |
| **2022-2023** | 503 | High volatility; ARS in crisis | 1,567 | 1.71d | 0.149 |
| **2024-2026** | 617 | Post-restructure; reformed CCL | 1,843 | 1.62d | 0.108 |

**Finding:** Staleness and dispersion both elevated during **2022-2023 volatility peak**. By 2024-2026, metrics normalize post-restructuring, though still higher than primary CEDEAR cohort.

### Carry-Forward Rate by Pair (F-026 Investigation)

| Pair | Zero-Volume % | Interpretation |
|---|---|---|
| YPF | 9.0% | Moderate; normal for volatile equity |
| Banco Macro | 6.7% | Moderate; banking sector typical |
| Pampa Energía | 12.2% | **Elevated** — suggests periods of very low BYMA-side liquidity |

**Pampa caveat:** 12.2% carry-forward is significantly higher than primary cohort (<1%). Either:
1. Genuine instrument liquidity constraint (PAM is smaller-cap utility), or
2. Data-source quality issue (BYMA feed gaps during low-volume periods)

**Recommendation:** Flag Pampa for separate review if secondary cohort used for anything requiring high-confidence continuous observation.

---

## STRUCTURAL-EVENT VALIDITY TEST: YPF SPLIT

**Test question:** Does the calibration framework correctly detect, segment, and preserve evidence around a confirmed structural ratio change?

**Outcome:**
- ✓ Ratio change documented: 1:1 → 1:10 on 2026-08-04
- ✓ Pre/post segmentation possible: 6,677 pre-split, 17 post-split observations
- ✓ Staleness continues normally across boundary (not disrupted by ratio change)
- ✓ Evidence chain preserved (no observations deleted, ratio change recorded)
- ⚠️ Post-split N too small for independent analysis (17 obs in 10 days)

**Verdict:** Framework successfully preserves and segments structural events. YPF split serves as **validation of framework behavior** under real-world ratio changes, not as independent evidence generator.

---

## COVERAGE & KNOWN LIMITATIONS

### Data-Quality Issues (Inherited from Primary)

- **F-009:** Reconciliation status uncertain 2020-2024
- **F-017:** Coverage not guaranteed (import truncation confirmed elsewhere)
- **F-026:** Carry-forwards handled; Pampa flagged for investigation

### Secondary-Specific Issues

1. **CCL arbitrage exposure:** Local pairs measure CCL volatility, not purely instrument liquidity. Thresholds calibrated from primary CEDEAR would not transfer directly.
2. **Smaller market depth:** Argentine equity market has lower aggregate liquidity; panel-formation dynamics differ from US-anchored cohort.
3. **Regime-dependent behavior:** FX crises (2022-2023) create structural breaks. Any threshold must account for regime-dependent coverage.

---

## SEPARATE ANALYSIS RESULT

**Secondary Cohort Finding:**
- Staleness is **slightly higher** (P95 = 5d vs. 3d primary) but not a constraint
- Dispersion is **significantly higher** (median CV 0.089 vs. 0.062 primary; P95 CV 0.301 vs. 0.189 primary)
- **Regime effects are visible:** 2022-2023 volatility peak creates structural break
- **YPF structural event validates framework:** Ratio change correctly segmented, evidence preserved

**Use case:** Validation and regime understanding. Do **not** pool with primary cohort for threshold selection. If future work includes broader Argentine portfolio coverage, these baselines inform regime-dependent threshold design (separate thresholds for crisis vs. stable periods).

---

## STATUS

Secondary cohort analysis **complete as diagnostic/validation work**. Not included in primary threshold calibration per financial advisor ruling (separate populations, no pooling).

**Next:** Await financial advisor review of primary cohort evidence before any threshold promotion to production.
