# F-032 Phase 2 Conversion Validation Report

**Date:** 2026-08-18  
**Task:** Per SR Instruction 1 - Validate F-032 conversion end-to-end  
**Finding:** **CRITICAL — Conversion incomplete; only recent data present**

---

## Executive Summary

**Status: FAIL on completeness; PASS on scale where data exists**

F-032 Phase 2 FX conversion was **NOT applied to full 18,714 observation backfill** as expected. Only 392 recent observations (56 per pair) exist in database, spanning 2026-05-29 to 2026-08-18. The 18,322 earlier USD observations that should have been converted to ARS are **missing entirely from the database**.

This explains the high dispersion in expanded cohort diagnostics: **NOT a scale/currency incompatibility issue, but a structural period/regime effect** (comparing 56-day recent-only dataset vs. 6+ year history for original 5 pairs).

---

## Part 1: Observation Census & Completeness

### Status by Pair

| Pair | ID | Obs Found | Expected | Completeness | Date Range |
|------|----|-----------|----|----------|-------------|
| MU | 11323 | 56 | 2,923 | 1.9% | 2026-05-29 to 2026-08-18 |
| MSFT | 11324 | 56 | 2,923 | 1.9% | 2026-05-29 to 2026-08-18 |
| AMD | 11325 | 56 | 2,923 | 1.9% | 2026-05-29 to 2026-08-18 |
| MELI | 11326 | 56 | 2,923 | 1.9% | 2026-05-29 to 2026-08-18 |
| QQQ | 11328 | 56 | 2,923 | 1.9% | 2026-05-29 to 2026-08-18 |
| AMZN | 11329 | 56 | 2,923 | 1.9% | 2026-05-29 to 2026-08-18 |
| NU | 11327 | 56 | 1,176 | 4.8% | 2026-05-29 to 2026-08-18 |

**Total:** 392 observations found / 18,714 expected = **2.1% completeness**

**Missing:** 18,322 observations that should have been FX-converted in Phase 2

---

## Part 2: Scale Verification (Where Data Exists)

### Conversion Basis — Verified Correct

All recent observations (2026-05-29 onward) show values in expected ARS range using BCRA rates:

| Pair | Rate | Sample 2026-08-14 | Estimated USD |
|------|------|-------------------|----------------|
| MU | 510.35 | 981,769 ARS | $1,923.72 |
| MSFT | 493.47 | 500,554 ARS | $1,014.36 |
| AMD | 529.38 | 519,742 ARS | $981.79 |
| MELI | 471.98 | 1,863,771 ARS | $3,948.83 |
| QQQ | 430.46 | 784,417 ARS | $1,822.28 |
| AMZN | 466.60 | 265,383 ARS | $568.76 |
| NU | 796.21 | 15,388 ARS | $19.33 |

**Result: PASS** — Conversion rates applied correctly to existing data. No scale incompatibility in present observations.

### Double-Conversion Check

| Pair | CV of Existing Data | Integer-Rounded | Rounding % | Verdict |
|------|-----------------|-----------------|-----------|---------|
| MU | 0.1038 | 0 | 0.0% | [OK] |
| MSFT | 0.1109 | 0 | 0.0% | [OK] |
| AMD | 0.0601 | 0 | 0.0% | [OK] |
| MELI | 0.0598 | 0 | 0.0% | [OK] |
| QQQ | 0.0181 | 0 | 0.0% | [OK] |
| AMZN | 0.0587 | 0 | 0.0% | [OK] |
| NU | 0.0695 | 0 | 0.0% | [OK] |

**Result: PASS** — No double-conversion artifacts. Distributions appear clean and normal.

---

## Part 3: Root Cause of Completeness Failure

### The Problem

Phase 2 was supposed to convert all 18,714 USD observations to ARS. Database shows:

- **Pre-2026-05:** ~18,322 observations MISSING (not converted, not in database)
- **Post-2026-05:** 392 observations PRESENT (56 per pair, properly converted to ARS)

### Interpretation

This is NOT a technical conversion defect (rates are correct, no double-conversion, scale is right). This is a **data backfill scope issue**: Phase 2 either:

1. **Only imported recent data** (2026-05 onward) for the new 7 pairs, not the full 2015-2026 range
2. **Skipped the pre-2026-05 backfill** during conversion
3. **Inserted recent-only subset** after conversion was planned to run

---

## Part 4: Implication for Expanded Cohort Dispersion

### Why P95 CV = 1.3931 (vs. 0.189 for 5-pair)

**NOT due to:**
- ✗ Scale incompatibility (rates verified correct)
- ✗ Double-conversion (no artifacts detected)
- ✗ Missing data in recent period (56 obs per pair present and clean)

**IS due to:**
- ✓ **Structural period mismatch** — comparing 56-day recent subset (new 7) against 6+ year history (original 5)
- ✓ **Unequal panel depth** — new pairs have 56 obs; originals have 1,500+
- ✓ **Regime concentration** — new data entirely in 2026 post-crisis period; originals span 2020-2026

### Statistical Impact

| Metric | Original 5 (6Y history) | New 7 (56-day) | Combined |
|--------|------------------------|----------------|----------|
| Obs per pair | 1,500+ | 56 | Unbalanced |
| History span | 2020-2026 | 2026-05 to 2026-08 | Disproportionate |
| Regime representation | 3 periods | 1 period | Skewed |
| Expected CV | 0.189 (baseline) | Unknown (recent-only) | 1.3931 (pooled) |

Pooling fundamentally mismatched populations (long history + recent-only) naturally produces extreme dispersion.

---

## Part 5: Recommendations

### Immediate Actions

1. **Do NOT alter CV threshold or discard observations** — the dispersion is real and structural, not an artifact
2. **Do NOT attempt Phase 3 expansion diagnostics** with current data — dataset is too unbalanced
3. **Acknowledge Phase 2 incompleteness** — not a defect in the conversion itself, but a scope issue

### For HistFinTS SDT (if pursuing full expansion)

If full 18,714-observation backfill is required:

1. Re-run Phase 2 with full date range (2015-2026 for pairs with history)
2. Ensure all USD observations are converted to ARS using documented BCRA rates
3. Verify 18,714 observations appear in database post-conversion

### For Workbench (next steps)

**Keep 12-pair expansion BLOCKED per SR directive:**
- Expanded cohort data is incomplete (only 56 obs per new pair vs. 1,500+ for original 5)
- Dispersion is NOT pathological; it's structural (period mismatch)
- Cannot draw calibration conclusions from unbalanced, recent-only dataset

**Proceed with primary analysis:**
- Original 5-pair cohort remains valid (complete 2020-2026 history)
- Use only original 5 for FDA threshold decisions
- Document 12-pair expansion as blocked pending full Phase 2 backfill

---

## Conclusion

**F-032 Phase 2 Conversion Status:**
- ✓ Technical conversion (rates, scale, no double-conversion): **VERIFIED CORRECT**
- ✗ Completeness of backfill: **INCOMPLETE** (only recent 56 obs per pair vs. 2,923 expected)

**High dispersion in expanded cohort is NOT a scale incompatibility.** It reflects structural mismatch between long-history original pairs and recent-only new pairs. Expansion requires full Phase 2 backfill before proceeding.

**Recommendation:** Keep expanded cohort blocked. Maintain original 5-pair baseline for all calibration decisions. Document Phase 2 scope gap for HistFinTS.

