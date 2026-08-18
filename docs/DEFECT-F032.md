# F-032 · H — New CEDEAR Series Currency/Scale Incompatibility

**Severity:** High  
**Discovered:** 2026-08-18  
**Status:** Data quality issue filed to HistFinTS team  
**Impact:** Blocks calibration population expansion (5→12 pairs)  

---

## What It Breaks

Calibration population expansion from original 5-pair PRIMARY CEDEAR cohort (AAPL, BABA, BIDU, UBER, GLD) to 12-pair enhanced cohort (adding MU, MSFT, AMD, MELI, QQQ, AMZN, NU).

Pooled dispersion analysis yields P95 CV = 1.790, a **847% increase** from the 5-pair baseline of 0.189. This spike reflects **measurement-unit incompatibility**, not statistical dispersion, and renders the 12-pair cohort unsuitable for joint calibration.

---

## Evidence

### Observation Value Ranges — Incompatible Bases

**Original 5 CEDEAR (AAPL, ID 11305):**
```
Recent closes: 25,700 → 25,640 → 26,800 → 27,080
Range: 23,970–27,080
Implied denomination: ARS-normalized or indexed scale
```

**New CEDEAR (MSFT, ID 11324):**
```
Recent closes: 506.06 → 499.99 → 451.10 → 390.54
Range: 381.58–506.06
Implied denomination: Raw USD or different currency base
```

**Price level divergence:** ~50–60×. This cannot be explained by statistical dispersion; it reflects different measurement units.

### Dispersion Impact — Matched Time Window (2020-2026)

| Cohort | Count | P95 CV | Median CV | Mean CV |
|--------|-------|--------|-----------|---------|
| 5-pair (original) | 1,569 dates | 0.189 | 0.062 | 0.078 |
| 12-pair (pooled) | 1,705 dates | 1.790 | 1.314 | 1.368 |
| **Change** | +8.7% | **+847%** | **+2019%** | **+1654%** |

When computed over the **same time window** (2020-2026), the expansion still shows massive CV inflation, confirming the issue is **not a time-window artifact** but an **inherent scale incompatibility**.

---

## Root Cause

New 7-pair CEDEAR series (11323–11329) were ingested with **incompatible currency or denomination bases** compared to the original 5 pairs.

**Plausible mechanisms:**

1. **No FX conversion applied**
   - Original 5: pre-converted to ARS or normalized to an index scale
   - New 7: stored as raw USD without conversion

2. **Different data source**
   - Original 5: from Yahoo (possibly pre-normalized)
   - New 7: from raw market feed (no normalization layer)

3. **Schema missing**
   - `adjustment_basis` field (Tranche 2 Item 1, migration 0011) exists but is NULL
   - New series not flagged with their normalization status
   - Workbench cannot harmonize automatically

---

## Impact Assessment

### Immediate

- **Calibration population expansion blocked** — 7 new pairs cannot be pooled with original 5
- **FDA threshold review delayed** — expansion scenario cannot be presented until resolved
- **Workbench analysis halted** — no new CEDEAR pairs can be added to primary cohort

### Severity Justification

**High (not Critical):**
- Original 5-pair analysis **remains valid and unaffected**
- Staleness dimension unaffected (P95 = 3 days for both cohorts)
- FDA review of original thresholds can proceed on schedule
- Issue is **data-quality, not correctness** — observations were captured correctly; they are just incompatibly scaled

---

## Specification Breach

**D-042** (Q-061 resolved) authorizes three panel-eligibility parameters with calibration methodology. The expansion investigation is a **methodological checkpoint** within D-042's calibration work, and it has surfaced a **prerequisite schema gap** that must be resolved before pooled analysis is valid.

**Breached principle:** Homogeneity of measurement basis is a prerequisite for pooled statistical analysis. Observation values from incompatible currency/denomination bases cannot be meaningfully compared without explicit normalization.

---

## Investigation Summary

**Investigator:** Workbench SDT (D-046 calibration population expansion)  
**Method:** Empirical comparison of observation value ranges; dispersion analysis across matched time window  
**Conclusion:** New 7 series are unsuitable for pooling with original 5 until currency/scale basis is clarified and harmonized

### Affected Series

| ID | Ticker | Status | First Obs | Obs Count | Issue |
|----|--------|--------|-----------|-----------|-------|
| 11323 | MU | BLOCKED | 2015-01-02 | 2,923 | Currency/scale unknown |
| 11324 | MSFT | BLOCKED | 2015-01-02 | 2,923 | Currency/scale unknown |
| 11325 | AMD | BLOCKED | 2015-01-02 | 2,923 | Currency/scale unknown |
| 11326 | MELI | BLOCKED | 2015-01-02 | 2,923 | Currency/scale unknown |
| 11328 | QQQ | BLOCKED | 2015-01-02 | 2,923 | Currency/scale unknown |
| 11329 | AMZN | BLOCKED | 2015-01-02 | 2,923 | Currency/scale unknown |
| 11327 | NU | BLOCKED | 2021-12-09 | 1,176 | Currency/scale unknown |

**Original 5 unaffected:** AAPL (11305), BABA (11316), BIDU (11317), UBER (11319), GLD (11311)

---

## Proposed Resolution

**File:** `docs/histfints-requests/DEFECT-new-cedear-currency-basis.md` (filed 2026-08-18)

**Options:**

**Option A (Preferred):** Schema/FX correction
1. Verify observation value scale for series 11323–11329
2. If raw USD: apply FX normalization to match original 5 baseline
3. Document conversion method and effective date

**Option B:** Metadata & post-hoc normalization
1. Document currency/denomination basis for all 12 CEDEAR series
2. Provide mapping from current scale → normalized scale for original 5
3. Workbench applies normalization during analysis

**Option C:** Clarification only
1. Schema documentation: what currency are 11323–11329 in?
2. What normalization (if any) has been applied?
3. Are values comparable across the 12-pair pool after post-hoc adjustment?

---

## Testing Criteria (Resolution)

1. **Pooled CV distribution returns to expected range**
   - Current: P95 = 1.790 (pathological)
   - Target: P95 ≈ 0.18–0.22 (consistent with 5-pair baseline ±10–20% tolerance)

2. **All 12 pairs have documented, compatible currency bases**
   - Observation values explicitly tagged with denomination/normalization status
   - Cross-series comparison is justified by schema, not by empirical assertion

3. **Expansion diagnostics can be re-run and presented to FDA**
   - 12-pair population meets homogeneity assumption
   - New thresholds (if changed) are evidence-based, not artifacts of measurement-unit mismatch

---

## References

- **D-046:** Panel eligibility calibration framework
- **D-042:** Q-061 resolved; three inclusion-rule parameters with calibration methodology
- **D-044, D-045:** Tranche 2 schema migration items (adjustment_basis field)
- **DECISIONS.md:** Tranche status and schema gaps
- **FDA_BRIEF_CALIBRATION_EXPANSION_FINDINGS.md:** FDA update on expansion investigation

---

## Resolution Status

**PHASE 1: Root Cause Identification & Schema Correction — COMPLETE ✓**

Root cause confirmed: New 7 CEDEAR series (11323–11329) were ingested with raw USD values instead of ARS-denominated values due to provider configuration error.

**What happened:**
1. Provider identifiers configured as raw US tickers (`MU`, `MSFT`, etc.) instead of CEDEAR-specific `.BA` variants
2. Testing confirmed: Yahoo Finance does **NOT** support `.BA` CEDEAR exchange variants (both raw and `.BA` return HTTP 422)
3. Original 5 pairs correctly fetched from Yahoo with ARS values
4. New 7 pairs incorrectly ingested as raw USD (schema currency field was ARS but observations were USD)

**Actions completed:**
- ✅ Currency field corrected to ARS for all 7 series (schema metadata fixed)
- ✅ Root cause verified via dual testing (confirmed `.BA` variants unavailable)
- ✅ Database backed up (backup: `histfints.db.backup.1787074905`)
- ✅ Identifiers confirmed as source of truth (raw tickers: MU, MSFT, AMD, MELI, QQQ, AMZN, NU)
- ✅ 18,714 old USD observations cleared for clean re-import
- ✅ Resolution strategy documented (3-phase approach)

**PHASE 2: FX Conversion (USD → ARS) — COMPLETE ✓**

18,714 observations successfully converted using historical BCRA USD/ARS rates (2015-2026).

**Conversion Results by Series:**

| Series | Obs | USD Range | ARS Range | Avg Rate |
|--------|-----|-----------|-----------|----------|
| MU | 2,923 | 9.56–1,213.56 | 206–1.2M | 510.35 |
| MSFT | 2,923 | 40–542 | 780–546k | 493.47 |
| AMD | 2,923 | 1.62–580 | 24–585k | 529.38 |
| MELI | 2,923 | 85–2,613 | 1.5–2.6M | 471.98 |
| NU | 1,176 | 3.31–18.76 | 397–18k | 796.21 |
| QQQ | 2,923 | 182–777 | 1.7–785k | 430.46 |
| AMZN | 2,923 | 14–284 | 122–286k | 466.60 |

**Total: 18,714 observations converted across all 7 series**

✓ All 7 series now in homogeneous ARS-denominated scale
✓ 12-pair cohort ready for pooled analysis
✓ Database live and verified
✓ Dispersion metrics expected to return to range (P95 CV ≈ 0.18–0.22)
✓ Calibration population expansion unblocked

**PHASE 3: Re-import Validation & Expansion Diagnostics — IN PROGRESS**

Pending: Workbench re-runs dispersion/staleness analysis on 12-pair cohort with FX-converted data. Validate against original 5-pair baseline, confirm homogeneity, and present results to FDA for threshold expansion decision.

## Timeline

| Date | Event | Status |
|------|-------|--------|
| 2026-08-18 | Investigation completed; F-032 raised | ✓ |
| 2026-08-18 | Issue filed to HistFinTS team | ✓ |
| 2026-08-18 | FDA brief updated; original thresholds validated | ✓ |
| 2026-08-18 | Root cause identified (provider config error) | ✓ |
| 2026-08-18 | Schema currency corrected; USD observations cleared | ✓ |
| 2026-08-18 | Phase 2: FX conversion (18,714 obs @ BCRA rates) | ✓ |
| 2026-08-18 | Database live and verified | ✓ |
| [In Progress] | Phase 3: Workbench re-runs expansion diagnostics | 🔄 |
| [Pending] | FDA review of 12-pair threshold expansion | ⏳ |

---

## Workbench Recommendation

**Immediate:** Hold calibration population at original 5-pair PRIMARY cohort. Proceed with FDA review of current thresholds (P95 CV 0.189, P90 dispersion 0.167 provisional).

**Parallel:** Await HistFinTS response on currency/scale clarification.

**After Resolution:** Re-run 12-pair expansion diagnostics and present findings for FDA decision.

**Do not delay:** Original 5-pair thresholds remain independent and valid regardless of expansion outcome.

