# Provisional Calibration Status and Forward Path

**Date:** 2026-08-19  
**Status:** PROVISIONAL — development may continue; primary calibration is not promoted

## 1. Current conclusion

The project should move forward provisionally rather than remain blocked by the unresolved calibration-sufficiency question.

The six-pair technical admissibility gate has passed:

- AAPL
- BABA
- AMD
- AMZN
- AZN
- BBD

AMZN's 2026-08-18 conflicting-source observations remain classified as `CONFLICTING_SOURCE` and excluded from analysis, without modifying the underlying records.

This admissibility result does **not** constitute authorization for primary threshold calibration.

## 2. Provisional operating position

The current provisional analytical state may be retained for continued development:

- `dispersion_threshold = CV 0.167`: provisional and uncalibrated.
- `staleness_policy`: provisional and uncalibrated.
- Primary calibration status: **not promoted / not validated**.
- The six-pair admissible population may be used for development and evidence gathering, but not represented as a fully calibrated population.

## 3. Risk assessment

The principal risk of moving forward is methodological, not data-preservation risk.

The project may continue with engineering and analytical work that does not depend on treating the provisional parameters as validated production policy.

Do not:
- promote the staleness policy as calibrated;
- promote CV 0.167 as a validated production threshold;
- claim that the current six-pair population has sufficient temporal/regime coverage for calibration;
- derive stronger financial conclusions from the provisional parameters.

## 4. Reversibility

This provisional decision is explicitly reversible.

Existing provenance, import runs, admissibility classifications, difficult observations, provider identities, and prior analytical evidence must remain preserved. The provisional parameters must remain configurable rather than being embedded as irreversible production semantics.

When better evidence becomes available, the primary population and calibration can be rerun and the provisional state superseded.

## 5. BYMA as the preferred resolution path

Authoritative BYMA data could substantially reduce current evidence uncertainty, particularly around CEDEAR identity and ratios, effective dates, authoritative pricing, provider representation differences, and historical evidence quality if sufficiently deep coverage is available.

BYMA availability does **not automatically resolve temporal/regime sufficiency**. If authoritative BYMA data only provides reliable observations from May 29, 2026 onward, source quality improves but the short single-regime window remains. If BYMA provides sufficiently deep historical CEDEAR observations, the primary population can be rebuilt around that evidence and calibration rerun.

## 6. Forward sequence

**Continue development provisionally**
→ **obtain authoritative BYMA evidence**
→ **rebuild/validate the primary evidence population**
→ **DFA methodological review**
→ **final primary calibration, if approved**

No additional threshold calibration is required merely to continue development.

## 7. Governance boundary

This status preserves the distinction between technical admissibility, analytical sufficiency, calibrated methodology, and production promotion.

**Admissible candidate population:** YES  
**Calibration evidence sufficient:** NOT YET ESTABLISHED  
**Thresholds calibrated:** NO  
**Development continuation:** YES, provisionally  
**BYMA evidence pursuit:** PREFERRED NEXT RESOLUTION PATH
