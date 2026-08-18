# Implementation Roadmap — Panel Eligibility (D-046)

**Authorization:** D-046  
**Date:** 2026-08-17  
**Gate:** Upstream validation complete (D-045)  
**Upstream Contract:** `classify_series()` → `derive_calendar()` → `apply_calendar()` (frozen)

---

## Phase 1: Core Parameter Implementation

### 1.1 `include_delisted` Parameter

**Specification:** SPEC-panel-eligibility.md §8.1

**Implementation:**
- Boolean parameter, defaults to TRUE
- At each panel date, check Series.status for the date's context (historical status, not current)
- Include discontinued Series in historical analysis by default
- When FALSE, exclude retroactively from entire window (rare case; historical research default is TRUE)

**Code location:** `src/hf_reswb/application/panel_eligibility_service.py` (new module)

**Test coverage:** Unit tests covering both TRUE and FALSE cases; verify membership changes at delisting boundary.

**Traceability:** Panel result includes `include_delisted` parameter value and list of affected Series (those with status changes during window).

---

### 1.2 `staleness_policy` Parameter — Time-Local Exclusion

**Specification:** SPEC-panel-eligibility.md §8.2–8.3

**Implementation:**
- **Provisional numerical parameter:** `max_consecutive_no_trade_days` (integer, default TBD pending calibration)
- **Detection:** Row-local, no calendar input required. For each Series on each date, compute days since last observation.
- **Time-local exclusion:** If (date - last_observed) > `max_consecutive_no_trade_days`, Series is stale starting that date.
- **Exclusion scope:** Series excluded from panel on that date and all subsequent dates within window.
- **Earlier observations:** Observations before staleness detected remain eligible for earlier panel dates.
- **State:** Mark `max_consecutive_no_trade_days` as **PROVISIONAL** in code, docs, and UI. Do not describe it as a calibrated financial threshold.

**Code location:** `src/hf_reswb/application/staleness_detector.py` (new module)

**Key invariant:**
```python
# Pseudocode illustrating time-local scope
for date in analysis_window:
    stale_series = []
    for series in panel:
        last_obs = get_last_observation_before(series, date)
        if (date - last_obs) > max_consecutive_no_trade_days:
            stale_series.append(series)
    
    # Series is excluded FROM this date ONWARD
    # not retroactively from the start of the window
```

**Test coverage:**
- Unit tests: staleness detection (row-local logic)
- Integration tests: time-local exclusion (membership changes as of staleness date, not retroactive)
- Edge case: Series that becomes stale then resumes trading (should re-enter on resume date)

**Traceability:**
- Per-date panel includes staleness exclusion count
- Per-Series staleness metadata (first stale date, last observed date)
- Diagnostic report: which Series were excluded due to staleness, on which dates

---

### 1.3 `dispersion_threshold` Parameter — Aggregate Suppression

**Specification:** SPEC-panel-eligibility.md §8.3–8.4

**Implementation:**
- **Provisional numerical parameter:** `dispersion_threshold` (dimensionless, default TBD pending calibration)
- **Computation:** For each panel date, compute dispersion across eligible members (exact metric TBD by calibration; provisional placeholder: coefficient of variation of residuals or IQR)
- **Suppression logic:** If dispersion > `dispersion_threshold`, set `result_status = SUPPRESSED` (do not publish aggregate rate)
- **Underlying data preserved:** Observations, per-member rates, residuals, and dispersion diagnostics remain available for inspection
- **State:** Mark threshold as **PROVISIONAL** in code and UI. Do not describe it as a financially established limit.

**Code location:** `src/hf_reswb/application/dispersion_analyzer.py` (new module)

**Key invariant:**
```python
# Aggregate suppression, not deletion
consensus_rate = compute_consensus(eligible_members)
dispersion = compute_dispersion_metric(eligible_members, consensus_rate)

if dispersion > dispersion_threshold:
    result = {
        'status': 'SUPPRESSED',
        'rate': None,  # Do not publish
        'dispersion': dispersion,
        'member_rates': [...],  # Available for inspection
        'residuals': [...],    # Available for inspection
        'reason': 'dispersion exceeds threshold'
    }
else:
    result = {
        'status': 'PUBLISHED',
        'rate': consensus_rate,
        'dispersion': dispersion,
        'member_rates': [...],
        'residuals': [...]
    }
```

**Test coverage:**
- Unit tests: dispersion metric computation
- Integration tests: aggregate suppression (result excluded from output, diagnostics preserved)
- Sensitivity analysis: how result changes at different thresholds

**Traceability:**
- Suppressed results appear in diagnostic reports with full dispersion data
- Per-date dispersion metric visible
- Diagnostic dashboard can show what would have been published at different thresholds

---

## Phase 2: Integration with Observation-Suitability

### 2.1 Upstream Pipeline (Frozen)

**Do NOT modify:**
```
classify_series()     — Axis A (row-local trade evidence, NO_TRADE_REPORTED / TRADE_OBSERVED / TRADE_EVIDENCE_UNRESOLVED)
  ↓
derive_calendar()     — Derive venue calendar from TRADE_OBSERVED dates
  ↓
apply_calendar()      — Axis B (session status, SESSION_CONFIRMED / SESSION_ABSENT / SESSION_UNRESOLVED)
```

This pipeline is frozen per D-035 (F-009 reconciliation).

### 2.2 Panel-Eligibility Layer (New)

**Depends on observation-suitability output:**
- Trade evidence classification (for liquidity criterion: exclude `NO_TRADE_REPORTED` by default)
- Session status (informational, not gating)
- Venue calendar (for panel alignment)

**Operates downstream:**
```
observation_suitability ──→ panel_eligibility ──→ panel_result
   (frozen)                  (new)                 (this phase)
```

### 2.3 Integration Points

**On each panel date:**
1. Apply `include_delisted` filter (Series.status check)
2. Collect available Series/pairs
3. Apply trade-evidence filters (liquidity: exclude NO_TRADE_REPORTED by default)
4. Apply staleness detection (time-local)
5. Compute panel membership as-of-date
6. Compute consensus and dispersion
7. Apply dispersion_threshold suppression rule
8. Record result with full traceability

**Result structure:**
```python
{
    'date': '2020-04-14',
    'result_status': 'PUBLISHED' | 'SUPPRESSED',
    'rate': float | None,
    'parameters': {
        'include_delisted': True,
        'staleness_policy': {'max_days': '<PROVISIONAL>'},
        'dispersion_threshold': '<PROVISIONAL>'
    },
    'member_count': 3,
    'excluded': {
        'stale': 1,
        'insufficient_history': 0,
        'liquidity': 0,
        'no_ratio': 0
    },
    'dispersion_metric': float,
    'member_rates': [...],
    'residuals': [...],
    'traceability': {
        'member_list': [series_ids],
        'excluded_series': [(id, reason), ...],
        'observation_suitability_run_id': <id>,
        'adjustment_basis': 'SPLIT_ADJUSTED' | 'UNADJUSTED'
    }
}
```

---

## Phase 3: Handle Data Constraints

### 3.1 Incomplete Availability Metadata

**State:** 99.36% of provider_assignment rows have first/last_available_date populated; 0.64% (73 rows) have NULL.

**All NULL cases:** Assignments with zero observations (legitimate edge case).

**Implementation:**
- Apply SPEC-panel-eligibility.md's coverage rule: assignments with NULL availability are marked with coverage status `UNRESOLVED`
- Do not silently treat as complete or incomplete
- Report affected count and impact on panel depth
- Make the 0.64% visible in diagnostic output (not hidden)

**Test coverage:**
- Verify NULL assignments are correctly identified
- Verify eligibility decision for NULL-availability assignments
- Verify diagnostic report includes affected count

### 3.2 Adjustment Basis

**State:** All three providers now have `adjustment_basis` populated (FRED/BYMA=UNADJUSTED, Yahoo=SPLIT_ADJUSTED).

**Implementation:**
- Use `adjustment_basis` for `adjustment_policy` parameter enforcement
- On each panel date, check all members' adjustment basis
- If mixed bases detected, apply the policy rule (currently: bar from consensus if bases differ)
- Record which members were included/excluded due to adjustment basis

**Test coverage:**
- Verify members with same adjustment basis are eligible
- Verify members with different bases are handled per policy
- Verify diagnostic output shows adjustment-basis exclusions

---

## Phase 4: Testing and Validation

### 4.1 Unit Tests

- `test_include_delisted_true`: Discontinued Series included
- `test_include_delisted_false`: Discontinued Series excluded (rare case)
- `test_staleness_time_local`: Exclusion starts on stale date, not retroactive
- `test_staleness_resume`: Series re-enters when trade resumes
- `test_dispersion_suppression`: Result suppressed when metric exceeds threshold
- `test_dispersion_diagnostics`: Suppressed results preserve member rates, residuals

### 4.2 Integration Tests

- Against real observation-suitability output
- Against real CEDEAR/USD panel data (2000–2026)
- Verify traceability chain (panel → eligibility → observations)
- Verify no HistFinTS observations are modified

### 4.3 Regression Tests

- F-009 reconciliation tests remain passing (frozen upstream)
- Observation-suitability tests remain passing (frozen)

---

## Phase 5: Calibration Study

**After** eligibility layer is implemented and tested:

### 5.1 Empirical Analysis

**Using historical panel data (CEDEAR/USD, 2000–2026):**

1. **Staleness calibration:**
   - Compute observed staleness lengths (days between last print)
   - Identify real staleness-caused residual patterns (D-017 signatures)
   - Test candidate thresholds (5, 10, 15, 20 days, etc.)
   - Measure: specificity, false-positive rate, impact on panel depth

2. **Dispersion calibration:**
   - Compute dispersion metrics on every panel date
   - Correlate with known ratio changes, regime shifts, real FX moves
   - Test candidate thresholds across different percentiles
   - Measure: suppression rate, false-suppression rate, missed-signal rate

3. **Sensitivity analysis:**
   - How do panel membership and depth change at different staleness thresholds?
   - How many dates are affected? Which pairs?
   - At what dispersion threshold does the panel become unusable (too many suppressions)?

### 5.2 Deliverable

**Report with:**
- Empirical distributions (staleness lengths, dispersion metrics)
- Candidate parameter values with affected-date/pair counts
- Sensitivity tables (how results change at different thresholds)
- Recommendation for provisional values (NOT final thresholds)
- Caveats and regime dependencies

### 5.3 Domain Review Gate

**Before promoting candidate values to production:**
- Financial advisor reviews calibration evidence
- Confirms that candidate thresholds make financial sense
- Identifies any regime-specific requirements
- Approves or requests adjustment

---

## Implementation Notes

### Code Structure
```
src/hf_reswb/application/
├── panel_eligibility_service.py    (main orchestrator)
├── staleness_detector.py           (time-local exclusion)
├── dispersion_analyzer.py          (aggregate suppression)
└── panel_builder.py                (pair/cross-section assembly)

src/hf_reswb/domain/
├── panel.py                        (result and parameter models)
└── eligibility.py                  (decision types)

tests/
├── test_panel_eligibility.py       (unit tests)
├── test_panel_integration.py       (integration tests)
└── test_panel_calibration.py       (empirical study, post-implementation)
```

### Observation-Suitability Contract
- Input: `observation_suitability` table (classify_series output)
- Do not modify: `classify_series()`, `derive_calendar()`, `apply_calendar()`
- Output: `panel_result` table with eligibility decisions and full traceability

### Provisional Status Visibility
- Configuration: `include_delisted`, `staleness_policy.max_days`, `dispersion_threshold` all marked as provisional in code
- Logging: every panel result notes which values were used and their provisional status
- UI: dashboard prominently displays "these thresholds are provisional pending calibration"
- Calibration: study results feed back into parameter updates without changing the analytical contract

---

## Non-Goals for This Phase

- Implement the calibration study (Phase 5)
- Hard-code staleness or dispersion thresholds
- Mutate or delete HistFinTS observations
- Change the observation-suitability pipeline

---

## Gate for Implementation Complete

✅ All three parameters implemented per SPEC-panel-eligibility.md  
✅ Integrated with observation-suitability (upstream contract unchanged)  
✅ Traceability preserved (panel → eligibility → observations)  
✅ Numerical parameters marked provisional  
✅ No HistFinTS mutations  
✅ 0.64% incomplete availability handled explicitly per spec  
✅ All tests passing  

Then: **Proceed to Phase 5 (calibration study)**
