# DEFECT-F009 Consultant Review Package

**Prepared for:** External technical review  
**Date:** 2026-08-17  
**Repository:** HistFinTS (v3 branch)  
**Defect ID:** F-009 · **Severity:** High  
**Scope:** Incremental import leaves permanent scale discontinuities at splits/revisions

---

## Package Contents

This package contains everything needed to:
1. Understand the defect mechanism
2. Verify it in the codebase
3. Evaluate remedies
4. Run the reproduction test

### Files Included

1. **DEFECT-F009.md** — Full defect analysis, evidence chain, root cause
2. **REQUEST-basis-factsheet.md** — Provider adjustment-basis inventory (context for why values drift)
3. **REQUEST-event-capture.md** — Proposed event capture mechanism (relates to remedy R2)
4. **SCHEMA-PRIMER.md** (this package) — Quick reference for schema entities
5. **test_import_service_defect_f009.py** — Regression test harness (cases a & b)
6. **REMEDY-EVALUATION-FRAMEWORK.md** (this package) — Framework for comparing remedies

---

## Quick Start

### Understanding the Defect (10 min read)

Read: **DEFECT-F009.md** (top to bottom)

**Key points:**
- `observation.value` is split-adjusted by provider (Yahoo) at fetch time
- Incremental import fetches only from `latest_stored_date - revalidation_window` forward
- Historical rows before the window are never re-fetched
- Result: pre-split rows arrive at old scale, post-split rows arrive at new scale
- No `correction` row, no marker, no log entry — the series silently breaks

**Real-world impact:**
- Series backfilled before a split, then tracked incrementally through it, becomes internally inconsistent
- Discontinuity is exactly the split factor (e.g., 7:1)
- Consumer sees: prices that make no economic sense when plotted or analyzed
- Duration: permanent until manual intervention or historical re-fetch

### Verifying the Mechanism (5 min code review)

File: `src/histfints/application/import_service.py` (lines 183–200)

```python
def _determine_range(self, series_id: int) -> tuple[datetime, datetime]:
    latest = self._observation_repo.latest_date(series_id)
    
    if latest is None:
        # First import: use backfill_start_date
        start = series.backfill_start_date.replace(tzinfo=timezone.utc)
    else:
        # Incremental: start from latest minus look-back window
        # (revalidation_window may be None → zero look-back)
        window = provider.default_revalidation_window_days
        if window:
            start = (latest - timedelta(days=window)).replace(tzinfo=timezone.utc)
        else:
            start = latest  # No look-back at all
    
    return start, end
```

**The issue:** Once the first import completes, `latest` is set. Every subsequent import starts from that `latest` (or `latest - window`). Dates before `latest` are never requested again, so split adjustments applied retroactively by the provider are never visible to the store.

### Running the Regression Test (2 min)

```bash
cd histfints-v3
python -m pytest tests/application/test_import_service_defect_f009.py -v
```

Expected output:
```
test_defect_f009_case_a_split PASSED
test_defect_f009_case_b_fred_revision PASSED
```

What the tests do:
- **Case (a):** Simulates a Yahoo split. Backfill pre-split, import post-split; confirms discontinuity persists with no correction row.
- **Case (b):** Simulates FRED revision. Backfill all data, then provider revises an old value outside the re-fetch window; confirms revision never arrives.

Both tests use real `ImportService`, real SQLite schema, real migrations, and real `_determine_range()` logic with scripted fake provider data.

---

## Background: Why This Matters

### Principle P3: Provenance

> Every displayed externally-sourced or calculated value must have machine-accessible provenance.

A scale break is an externally-sourced event (provider adjustment) that becomes invisible (no correction row, no marker, no log). Consumers cannot trace how a value came to be, violating P3.

### Data Quality

The store is supposed to be a **reliable point of truth** for observation data. A Series with a silent scale discontinuity is:
- Unsuitable for analytics (ratios, correlations, regressions all wrong)
- Unsuitable for comparison (can't tell if two values are from before/after the break)
- Unsuitable for auditing (change is invisible and untracked)

### Affected Providers

**Current confirmed:**
- **Yahoo Finance** — prices are split-adjusted; affected by splits and ticker symbol changes
- **FRED** — values are revised; affected by statistical methodology changes and data corrections

**Potentially affected:**
- Any provider that:
  1. Applies historical adjustments at query time (basis shift)
  2. Revises already-published values
  3. Changes how an identifier resolves over time

---

## Remedy Evaluation

See **REMEDY-EVALUATION-FRAMEWORK.md** (included below) for detailed comparison.

### Three candidate approaches

| Remedy | Mechanism | Cost | Scope | Side effects |
|--------|-----------|------|-------|--------------|
| **R1** | Periodic full-range re-fetch | High bandwidth + rate limits | Complete fix | History becomes mutable by design (logged) |
| **R2** | Event capture backfill | Application logic only | Partial fix (events only) | Requires event parsing for each provider |
| **R3** | Detect-and-refuse consumer-side | Analytical layer only | Consumer-side gate | Doesn't fix the data itself, just warns about it |

Each has different tradeoffs. The framework below helps evaluate which is appropriate for your use case.

---

## Understanding the Schema

### Core entities (relevant to F-009)

**Series** — the instrument record
- `id`, `label`, `series_type` (STOCK, ECONOMIC_INDICATOR, etc.)
- `backfill_start_date` — where incremental import starts on first run
- `provider_assignments` — links to providers that supply observations

**ProviderAssignment** — which provider supplies this Series
- `provider_id`, `series_id`
- `provider_series_identifier` (e.g., ticker "AAPL")
- `priority` (resolved in order)

**Provider** — a data source (Yahoo Finance, FRED, etc.)
- `display_name`, `implementation_key`
- `default_revalidation_window_days` — how far back to re-fetch on incremental import

**Observation** — one data point
- `series_id`, `import_run_id`, `observed_at` (the date)
- `value`, `open`, `high`, `low`, `volume`
- Provider-adjusted, not raw

**Correction** — audit record of a changed Observation
- `observation_id`, `old_value`, `new_value`
- `import_run_id`, `detected_at` (when the change was found)
- **Only created when a value is re-fetched and differs**

**ImportRun** — one import execution
- `provider_assignment_id`, `trigger_type` (MANUAL/SCHEDULED)
- `status` (IN_PROGRESS/SUCCESS/PARTIAL/FAILED)
- `started_at`, `ended_at`

### Relevant SQL queries

```sql
-- Check if a Series has ever been corrected
SELECT COUNT(*) FROM correction
WHERE observation_id IN (
  SELECT id FROM observation WHERE series_id = ?
);

-- Find the oldest date ever corrected across all Series
SELECT MIN(o.observed_at) FROM correction c
JOIN observation o ON c.observation_id = o.id;

-- See the re-fetch window for a provider
SELECT default_revalidation_window_days FROM provider
WHERE display_name = 'Yahoo Finance';
```

---

## Remedy Evaluation Framework

### R1: Periodic Full-Range Re-Fetch

**Mechanism:** On a schedule (e.g., weekly), re-fetch the entire history for each Series.

**Advantages:**
- Complete fix — catches all basis shifts, revisions, symbol changes
- Provider-agnostic — works for any source
- Creates a logged audit trail (correction rows mark every change)
- Healthy Series generate ~zero corrections (low noise)
- Drifted Series generate a burst of corrections on the re-fetch (detectable pattern)

**Disadvantages:**
- High bandwidth cost (many duplicated rows fetched repeatedly)
- Rate-limited endpoints may block (Yahoo, Alpha Vantage have limits)
- Makes history explicitly mutable (by design, but requires explanation)
- Requires robust duplicate-handling (same value fetched multiple times)
- Slow for large datasets

**When to use:**
- You have a small, high-value dataset (< 1,000 Series)
- You can afford the bandwidth
- You need guaranteed accuracy for analytical use
- You want full auditability (correction log is the source of truth)

**Implementation effort:** Medium (fetch scheduling, duplicate handling, test coverage)

---

### R2: Event Capture Backfill

**Mechanism:** Parse provider-reported events (splits, dividends) and persist them. Use events to bridge observed prices across basis changes.

**Advantages:**
- Lower bandwidth than full re-fetch (only request events, not full history)
- Precise: uses provider-reported events, not inferred
- Enables compensation (adjust old data to new basis if needed)
- Yahoo already supplies split/dividend events in API response

**Disadvantages:**
- Only works for events the provider reports (doesn't catch silent revisions)
- Requires parsing and validation per provider
- Doesn't fix data that's already stored — only prevents future breaks
- Event data itself can be wrong or incomplete (requires validation)
- Requires schema change (provider_event table)

**When to use:**
- You want to prevent *future* breaks without re-fetching
- Event data is your system's boundary (only care about splits/dividends, not FRED revisions)
- You're willing to live with historical breaks that occurred before event capture was added
- You want to enable basis-conversion logic downstream

**Implementation effort:** Low-Medium (parsing logic, schema, backfill of historical events, test coverage)

---

### R3: Detect-and-Refuse Consumer-Side

**Mechanism:** At query time, detect a discontinuity (e.g., price ratio > threshold) and refuse to return the Series, flagging it for review.

**Advantages:**
- Zero cost to upstream (no re-fetch, no schema change, no parsing)
- Prevents accidental use of broken data
- Consumer stays safe (won't use bad data by accident)
- Works retrospectively (applies to already-stored data)

**Disadvantages:**
- Doesn't fix the data itself (Series is still broken in the store)
- False positives (real market moves can look like discontinuities)
- Requires calibration (what ratio threshold is a break vs. a move?)
- Doesn't give consumers guidance on how to get the *correct* data
- Purely defensive (prevents harm, but doesn't create value)

**When to use:**
- You want to gate against silent failures but can't afford upstream fixes
- You have domain knowledge to tune detection thresholds
- The analysis pipeline can gracefully handle "Series refused" signals
- You're OK with some Series becoming unavailable for analysis

**Implementation effort:** Low (heuristic detection, consumer-side gating)

---

## Questions for the Consultant

As you review this, consider:

1. **Severity:** Is this defect as severe as presented? Are there scenarios where silent scale breaks are acceptable?

2. **Scope:** Which providers in the HistFinTS ecosystem are actually affected? (Yahoo for splits/symbol changes, FRED for revisions — others?)

3. **Remedy recommendation:** Given the use case (Research Workbench needs reliable data for statistical analysis), which remedy makes sense?

4. **Implementation order:** If multiple remedies: which should ship first?

5. **Testing:** Do the regression tests adequately capture the defect? Are there other scenarios to test?

6. **Graceful degradation:** If we can't fix all providers at once, is it acceptable to have R3 (detect-and-refuse) for some and R1 for others?

---

## Files in This Package

| File | Purpose |
|------|---------|
| `DEFECT-F009.md` | Full analysis and evidence |
| `REQUEST-basis-factsheet.md` | Provider adjustment behavior inventory |
| `REQUEST-event-capture.md` | Event capture proposal (R2 background) |
| `test_import_service_defect_f009.py` | Regression test (runnable) |
| `SCHEMA-PRIMER.md` | This file — quick SQL/schema reference |
| `REMEDY-EVALUATION-FRAMEWORK.md` | This file — detailed remedy analysis |

---

## Contact & Context

**Raised from:** Research Workbench specification review (D-007, D-009)  
**Raised by:** HistFinTS team  
**Date filed:** 2026-08-15  
**Status:** Unfixed, dormant (no production Series yet affected due to survivorship)

**Related filings:**
- **REQUEST-basis-factsheet.md** — What does each provider report as observation basis?
- **REQUEST-event-capture.md** — Can we parse and persist provider events?
- **REQUEST-tranche2-migration.md** — Add adjustment-basis field (orthogonal)

**Access to repository:**
- Code: `histfints-v3` branch, `src/histfints/application/import_service.py:183–200`
- Schema: `src/histfints/persistence/schema.sql` (baseline) + migrations in `src/histfints/persistence/migrations/`
- Tests: `tests/application/test_import_service_defect_f009.py` (regression suite)

---

## Next Steps

1. Review the defect analysis in **DEFECT-F009.md**
2. Run the regression test to confirm the mechanism
3. Evaluate each remedy using the framework
4. Recommend approach + implementation priority
5. Advise on any schema/API implications

Thank you for reviewing this. We appreciate your perspective on data integrity and provider handling.
