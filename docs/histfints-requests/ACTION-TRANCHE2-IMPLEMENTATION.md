# ACTION REQUEST — Tranche 2 Schema Implementation

**To:** HistFinTS Development Team  
**From:** hf_reswb Workbench (SDT)  
**Date:** 2026-08-17  
**Priority:** Blocking (gates panel-eligibility and adjustment-basis enforcement in Workbench)  
**Status:** Two independent items, both actionable, no architectural changes required

---

## Executive Summary

Two concrete schema/data tasks are required to unblock Workbench panel-eligibility implementation:

1. **Adjustment Basis Backfill** — Populate `provider.adjustment_basis` with provider-specific values (mechanical, no schema change)
2. **Provider-Assignment Availability Marker** — Add two columns to `provider_assignment` and backfill from observation data (schema migration + mechanical backfill)

Both items are independent and deterministic. No new architecture. No feature development. Both can be completed from existing data.

---

## Item 1: Adjustment Basis Population

### What
Populate `provider.adjustment_basis` column for all three active providers.

### Current State
```sql
SELECT display_name, adjustment_basis FROM provider ORDER BY display_name;
```
**Result:** BYMA | NULL, FRED | NULL, Yahoo Finance | NULL

### Required Values
- **FRED** → `UNADJUSTED` (FRED publishes raw macro data, no adjustments)
- **Yahoo Finance** → `SPLIT_ADJUSTED` (Yahoo applies split adjustments; dividend-unadjusted)
- **BYMA** → `UNADJUSTED` (BYMA publishes raw prices)

### Implementation
Three UPDATE statements:
```sql
UPDATE provider SET adjustment_basis = 'UNADJUSTED' WHERE implementation_key = 'fred';
UPDATE provider SET adjustment_basis = 'SPLIT_ADJUSTED' WHERE implementation_key = 'yahoo_finance';
UPDATE provider SET adjustment_basis = 'UNADJUSTED' WHERE implementation_key = 'byma';
```

### Verification
```sql
SELECT display_name, adjustment_basis FROM provider ORDER BY display_name;
```
Expected:
```
BYMA | UNADJUSTED
FRED | UNADJUSTED
Yahoo Finance | SPLIT_ADJUSTED
```

### Workbench Consumption
Once populated, `SPEC-panel-eligibility.md` can activate the `adjustment_policy` parameter:
```sql
SELECT s.id, s.label, p.display_name, p.adjustment_basis
FROM series s
JOIN provider_assignment pa ON s.id = pa.series_id
JOIN provider p ON pa.provider_id = p.id
WHERE s.id = 11312;
-- Returns: 11312 | YPF Sociedad Anonima CEDEAR | Yahoo Finance | SPLIT_ADJUSTED
```

**Effort:** Minimal (3 UPDATE statements)  
**Risk:** None (adding factual metadata to existing column)  
**Reversal:** Simple (UPDATE back to NULL if needed)

---

## Item 2: Provider-Assignment Availability Marker

### What
Add `first_available_date` and `last_available_date` columns to `provider_assignment`, populated with the earliest and latest observation dates for each assignment.

### Current State
**Table:** `provider_assignment`  
**Missing columns:** `first_available_date` (TEXT), `last_available_date` (TEXT)

**Current schema:**
```
id | series_id | provider_id | priority | provider_series_identifier | ... | adjustment_basis_override | last_revalidated_at | ...
```

### Why Not Use Existing Data?
`provider_symbol` has `first_available_date` and `last_available_date`, but:
- `provider_symbol` is Catalog-side (discovery/metadata), not operational
- It links to `provider.id` only, not to `provider_assignment` or `series`
- No join path exists from Series → ProviderAssignment → ProviderSymbol
- Confirmed structural gap (per `TRANCHE2-VERIFICATION-2026-08-17.md`)

The operational path must have its own availability marker on `provider_assignment`.

### Schema Migration
Add two columns to `provider_assignment`:
```sql
ALTER TABLE provider_assignment ADD COLUMN first_available_date TEXT;
ALTER TABLE provider_assignment ADD COLUMN last_available_date TEXT;
```

### Data Backfill
**Deterministic approach:** For each provider_assignment row, compute from `observation` table:

```sql
UPDATE provider_assignment pa
SET 
  first_available_date = (
    SELECT DATE(MIN(o.observed_at))
    FROM observation o
    WHERE o.series_id = pa.series_id
      AND o.import_run_id IN (
        SELECT ir.id FROM import_run ir 
        WHERE ir.provider_assignment_id = pa.id
      )
  ),
  last_available_date = (
    SELECT DATE(MAX(o.observed_at))
    FROM observation o
    WHERE o.series_id = pa.series_id
      AND o.import_run_id IN (
        SELECT ir.id FROM import_run ir 
        WHERE ir.provider_assignment_id = pa.id
      )
  )
WHERE first_available_date IS NULL
  AND last_available_date IS NULL;
```

**Alternative (if single import_run per assignment is more reliable):**
```sql
UPDATE provider_assignment pa
SET 
  first_available_date = (
    SELECT DATE(MIN(o.observed_at))
    FROM observation o
    WHERE o.series_id = pa.series_id
  ),
  last_available_date = (
    SELECT DATE(MAX(o.observed_at))
    FROM observation o
    WHERE o.series_id = pa.series_id
  );
```

### Verification
```sql
-- Query 1: Check that columns exist and are populated
SELECT 
  pa.id, s.label, p.display_name,
  pa.first_available_date, pa.last_available_date,
  COUNT(o.id) as observation_count
FROM provider_assignment pa
JOIN series s ON pa.series_id = s.id
JOIN provider p ON pa.provider_id = p.id
LEFT JOIN observation o ON pa.series_id = o.series_id
  AND o.observed_at::date >= pa.first_available_date
  AND o.observed_at::date <= pa.last_available_date
GROUP BY pa.id, s.id, p.id
LIMIT 10;

-- Expected sample result:
-- id | label | provider | first_available_date | last_available_date | observation_count
-- 123 | AAPL | Yahoo Finance | 2000-01-03 | 2026-08-14 | 6624
```

```sql
-- Query 2: Spot-check data consistency (no negative date ranges)
SELECT pa.id, s.label, pa.first_available_date, pa.last_available_date
FROM provider_assignment pa
JOIN series s ON pa.series_id = s.id
WHERE pa.first_available_date > pa.last_available_date
  OR pa.first_available_date IS NULL
  OR pa.last_available_date IS NULL;

-- Expected: No results (data is consistent)
```

### Workbench Consumption
Once implemented, Workbench will use this to implement `minimum_coverage` parameter:

```sql
-- Determine whether an assignment has adequate coverage
SELECT 
  pa.id, s.label, p.display_name,
  pa.first_available_date, pa.last_available_date,
  COUNT(o.id) as total_observations,
  COUNT(CASE WHEN DATE(o.observed_at) BETWEEN pa.first_available_date AND pa.last_available_date THEN 1 END) as covered_observations
FROM provider_assignment pa
JOIN series s ON pa.series_id = s.id
JOIN provider p ON pa.provider_id = p.id
LEFT JOIN observation o ON pa.series_id = o.series_id
WHERE s.id = 11312
GROUP BY pa.id, s.id, p.id;
```

**Effort:** Schema migration (1 ALTER statement) + deterministic backfill (1-2 UPDATE statements)  
**Risk:** Low (adding metadata derived from existing observations)  
**Reversal:** Simple (DROP columns if needed)

---

## Implementation Order

**No dependency between Item 1 and Item 2.** Both can proceed in parallel or either can go first.

Suggested order:
1. **Item 1** — Faster, immediate: 3 UPDATE statements
2. **Item 2** — Requires schema migration: ALTER TABLE + backfill

Both should be complete before Workbench panel-eligibility implementation begins.

---

## Acceptance Criteria

### Item 1
- [ ] `provider.adjustment_basis` is populated for FRED, Yahoo Finance, BYMA
- [ ] Values match specification (FRED/BYMA → UNADJUSTED, Yahoo → SPLIT_ADJUSTED)
- [ ] Workbench verification query returns correct results
- [ ] No NULL values for active providers

### Item 2
- [ ] `provider_assignment.first_available_date` column exists and is populated
- [ ] `provider_assignment.last_available_date` column exists and is populated
- [ ] No date ranges are inverted (first > last)
- [ ] No NULL values (all assignments have explicit date ranges)
- [ ] Spot-check queries confirm data consistency
- [ ] Workbench verification query joins correctly and returns observations in range

---

## Workbench Dependencies

**Workbench is ready to proceed immediately upon completion:**
- `SPEC-panel-eligibility.md` §8 (inclusion parameters) is specified and approved
- Calibration methodology is documented (§8.5)
- Observation-suitability classification is implemented and frozen (D-035–D-040)

**What is blocked:**
- Cannot activate `adjustment_policy` parameter (awaiting Item 1)
- Cannot implement `minimum_coverage` parameter (awaiting Item 2)
- Cannot complete full panel-eligibility implementation without both

**Timeline:** Both items must be complete before Workbench can proceed to implementation.

---

## Questions for HistFinTS SE

1. **Item 1:** Can the backfill be applied directly, or should the column be marked as "populated as of [date]" with a migration timestamp?
2. **Item 2:** Should `first_available_date` and `last_available_date` be nullable (allowing for incomplete assignments) or NOT NULL (requiring complete data)?
3. **Item 2:** Are there any provider_assignment rows that should be excluded from the backfill (e.g., reassigned rows, deprecated assignments)?
4. **Verification:** Can HistFinTS confirm both items with the acceptance criteria queries above?

---

## References

- `REQUEST-tranche2-completion.md` — Initial requirements (filed 2026-08-17)
- `TRANCHE2-VERIFICATION-2026-08-17.md` — Verification against live database, structural analysis
- `SPEC-panel-eligibility.md` — Workbench spec that depends on both items
- D-041, D-042, D-043 — Decisions tracking this work

---

## Contact

SDT Workbench team — Ready to integrate once items complete.
