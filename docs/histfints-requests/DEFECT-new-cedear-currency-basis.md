# HistFinTS Issue: New CEDEAR Series Currency/Scale Incompatibility

**Date:** 2026-08-18  
**Priority:** High  
**Category:** Data Quality / Schema  
**Requestor:** Workbench Research Team (D-046 calibration population expansion)  

---

## Problem Statement

Seven new CEDEAR series were recently added to HistFinTS (IDs 11323-11329: MU, MSFT, AMD, MELI, QQQ, AMZN, NU). These series cannot be analyzed alongside the original 5-pair CEDEAR cohort (AAPL, BABA, BIDU, UBER, GLD) because their **observation values appear to be in incompatible currency or denomination bases**.

### Evidence

**Original 5 CEDEAR pair (AAPL, ID 11305) — Recent observations:**
```
2026-08-14: 25,700.0
2026-08-13: 25,640.0
2026-08-08: 26,800.0
2026-08-07: 27,080.0
Range: 23,970 - 27,080
Implied scale: Likely ARS or normalized against Argentine reference
```

**New CEDEAR pair (MSFT, ID 11324) — Recent observations:**
```
2026-08-14: 506.05999755859375
2026-08-13: 499.989990234375
2026-08-08: 451.1000061035156
2026-08-07: 390.5400085449219
Range: 381.58 - 506.06
Implied scale: Raw USD or different currency base
```

**Dispersion consequence:** Computing coefficient of variation (CV) across these heterogeneous scales yields P95 = 1.790 (847% higher than 5-pair baseline of 0.189). This is **not statistical dispersion**; it is **measurement unit incompatibility**.

---

## Affected Series

| ID | Ticker | Obs | First | Last | Implied Scale | Status |
|----|--------|-----|-------|------|---|---|
| 11323 | MU (Micron) | 2,923 | 2015-01-02 | 2026-08-18 | Raw USD? | BLOCKED |
| 11324 | MSFT | 2,923 | 2015-01-02 | 2026-08-18 | Raw USD? | BLOCKED |
| 11325 | AMD | 2,923 | 2015-01-02 | 2026-08-18 | Raw USD? | BLOCKED |
| 11326 | MELI (MercadoLibre) | 2,923 | 2015-01-02 | 2026-08-18 | Raw USD? | BLOCKED |
| 11328 | QQQ (Invesco ETF) | 2,923 | 2015-01-02 | 2026-08-18 | Raw USD? | BLOCKED |
| 11329 | AMZN (Amazon) | 2,923 | 2015-01-02 | 2026-08-18 | Raw USD? | BLOCKED |
| 11327 | NU (Nu Holdings) | 1,176 | 2021-12-09 | 2026-08-18 | Raw USD? | BLOCKED |

Original 5 (unaffected):
- AAPL (11305), BABA (11316), BIDU (11317), UBER (11319), GLD (11311) — all consistent scale

---

## Root Cause Analysis

**Hypothesis:** New series were ingested with **raw USD values** rather than being normalized to match the **ARS-denominated or normalized scale** of the original 5 CEDEAR pairs.

Possibilities:
1. **No FX conversion applied** — New series stored as USD, original 5 pre-converted to ARS or index-scaled
2. **Different data source** — Original 5 from Yahoo (pre-normalized), new 7 from raw market feed (no normalization)
3. **Schema missing** — Adjustment basis field (Tranche 2 Item 1, migration 0011) not populated for new series, preventing harmonization

---

## Impact

1. **Panel eligibility calibration blocked** — Cannot compute homogeneous dispersion metrics across 12-pair cohort until resolved
2. **Workbench analysis halted** — 7 new CEDEAR pairs cannot be added to primary calibration population pending this fix
3. **FDA decision delayed** — Threshold expansion review on hold

---

## Requested Action

**Option A: Immediate (High Priority)**
- Verify observation value scale for series 11323-11329
- If raw USD: apply FX normalization to match original 5 CEDEAR baseline (document conversion method)
- Populate `adjustment_basis` field (Tranche 2 schema) if available

**Option B: Fallback (Metadata)**
- Document the currency/denomination basis for all 12 CEDEAR series in a metadata table
- Provide mapping from USD → normalized scale used in original 5
- Workbench can apply post-hoc normalization if schema cannot be updated immediately

**Option C: Clarification**
- Provide schema documentation for series 11323-11329:
  - What currency are observations stored in?
  - What normalization (if any) has been applied?
  - Do values require FX adjustment before cross-series analysis?

---

## Testing Criteria (Resolution)

Issue resolved when:
1. New 7-pair series can be pooled with original 5 without artifactual dispersion spikes
2. Coefficient of variation (CV) across 12-pair panel matches expected statistical profile (~0.08-0.20 range, not 1.79)
3. Observation values are documented with explicit currency/scale basis

---

## References

- **D-046:** Panel eligibility calibration framework (Workbench)
- **DECISIONS.md:** Tranche 2 schema migration (adjustment_basis field, D-044/D-045)
- **Parallel issue:** DEFECT-F009.md (evidence consumption) references Tranche 2 schema gaps

---

## Status

**Reported:** 2026-08-18  
**Expected response:** [Awaiting HistFinTS team]  
**Blocker:** Yes — calibration population expansion cannot proceed

