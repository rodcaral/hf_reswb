# Validation Checklist — Tranche 2 Data Assumptions (Pre-Implementation)

> **Closed 2026-08-27.** This checklist's gate is cleared: D-044 authorized it, and
> `TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md` (also in `docs/evidence/`) is the completed
> run reporting the results. The "Gate: ...blocked" line below is retained as originally
> written and is no longer current — read it as historical, not a live blocker. No other
> content on this page has been edited.

**Date:** 2026-08-17  
**Status:** Tranche 2 migrations deployed (D-044)  
**Gate:** Panel-eligibility implementation blocked until these validations pass  
**Owner:** Workbench team  

---

## Purpose

Before `SPEC-panel-eligibility.md` implementation proceeds, Workbench must verify that the deployed Tranche 2 data actually satisfies the assumptions the spec makes. This is not a gate imposed by SE; it is a necessary checkpoint to confirm the upstream changes landed correctly and are usable.

---

## Validation Queries

Run all queries below against the live HistFinTS database attached to Workbench. Report the results.

### Query 1: Adjustment Basis Population

**Purpose:** Verify all three providers have correct `adjustment_basis` values.

```sql
SELECT display_name, adjustment_basis 
FROM histfints.provider 
WHERE implementation_key IN ('fred', 'yahoo_finance', 'byma')
ORDER BY display_name;
```

**Expected Result:**
| display_name | adjustment_basis |
|---|---|
| BYMA | UNADJUSTED |
| FRED | UNADJUSTED |
| Yahoo Finance | SPLIT_ADJUSTED |

**Pass Criteria:** All three present with correct values (no NULL, no typos).

---

### Query 2: Availability Marker Columns Exist

**Purpose:** Confirm columns were added to `provider_assignment`.

```sql
PRAGMA table_info(histfints.provider_assignment);
```

**Expected Result:** Column list includes:
- `first_available_date` (TEXT, nullable)
- `last_available_date` (TEXT, nullable)

**Pass Criteria:** Both columns present and queryable.

---

### Query 3: Availability Data Coverage

**Purpose:** Verify backfill completed at expected scale (99%+).

```sql
SELECT 
  COUNT(*) as total_assignments,
  COUNT(CASE WHEN first_available_date IS NOT NULL AND last_available_date IS NOT NULL THEN 1 END) as with_dates,
  COUNT(CASE WHEN first_available_date IS NULL AND last_available_date IS NULL THEN 1 END) as both_null,
  ROUND(100.0 * COUNT(CASE WHEN first_available_date IS NOT NULL THEN 1 END) / COUNT(*), 2) as coverage_percent
FROM histfints.provider_assignment;
```

**Expected Result:**
| total_assignments | with_dates | both_null | coverage_percent |
|---|---|---|---|
| 11321 | ~11248 | ~73 | ~99.4 |

**Pass Criteria:** Coverage ≥ 98% (allows for legitimate edge cases like zero-observation assignments).

---

### Query 4: Data Consistency (No Inverted Ranges)

**Purpose:** Confirm no data quality issues in backfill.

```sql
SELECT 
  COUNT(*) as anomaly_count,
  COUNT(CASE WHEN first_available_date > last_available_date THEN 1 END) as inverted_ranges,
  COUNT(CASE WHEN (first_available_date IS NULL) != (last_available_date IS NULL) THEN 1 END) as partial_nulls
FROM histfints.provider_assignment
WHERE first_available_date IS NOT NULL OR last_available_date IS NOT NULL;
```

**Expected Result:** All counts = 0

| anomaly_count | inverted_ranges | partial_nulls |
|---|---|---|
| 0 | 0 | 0 |

**Pass Criteria:** Zero anomalies.

---

### Query 5: Representative Assignment Rows

**Purpose:** Spot-check actual data quality with sample rows spanning providers and eras.

```sql
SELECT 
  pa.id, s.label, p.display_name,
  pa.first_available_date, pa.last_available_date,
  COUNT(o.id) as total_observations
FROM histfints.provider_assignment pa
JOIN histfints.series s ON pa.series_id = s.id
JOIN histfints.provider p ON pa.provider_id = p.id
LEFT JOIN histfints.observation o ON pa.series_id = o.series_id
GROUP BY pa.id, s.id, p.id
ORDER BY pa.id
LIMIT 20;
```

**Expected Result:** Sample rows with:
- Valid date ranges (first ≤ last)
- Reasonable dates (2000–2026 span)
- Observation counts matching the date span (no zero-observation rows with non-null dates)

**Pass Criteria:** All sample rows are consistent and reasonable.

---

### Query 6: NULL Semantics (Legitimate Edge Cases)

**Purpose:** Verify NULL assignments are those with zero observations (not a backfill failure).

```sql
SELECT 
  COUNT(*) as null_assignments,
  COUNT(CASE WHEN obs_count = 0 THEN 1 END) as with_zero_observations,
  COUNT(CASE WHEN obs_count > 0 THEN 1 END) as with_observations_but_null
FROM (
  SELECT 
    pa.id,
    pa.first_available_date, pa.last_available_date,
    COUNT(o.id) as obs_count
  FROM histfints.provider_assignment pa
  LEFT JOIN histfints.observation o ON pa.series_id = o.series_id
  WHERE pa.first_available_date IS NULL AND pa.last_available_date IS NULL
  GROUP BY pa.id
) sub;
```

**Expected Result:**
| null_assignments | with_zero_observations | with_observations_but_null |
|---|---|---|
| ~73 | ~73 | 0 |

**Pass Criteria:** All NULL assignments have zero observations (no backfill failures).

---

## Validation Results Template

**Run date:** [DATE]  
**Workbench DB:** [PATH]  
**HistFinTS instance:** [URL/PATH]  
**Schema version:** [USER_VERSION from PRAGMA]  

### Query 1: Adjustment Basis ✅ / ❌
[Paste full result]

### Query 2: Availability Columns ✅ / ❌
[Paste relevant columns from PRAGMA output]

### Query 3: Coverage ✅ / ❌
[Paste result row]

### Query 4: Consistency ✅ / ❌
[Paste result row]

### Query 5: Sample Rows ✅ / ❌
[Paste first 5 rows]

### Query 6: NULL Semantics ✅ / ❌
[Paste result row]

---

## Decision Gate

**Panel-eligibility implementation may proceed if and only if:**

- ✅ Query 1: All three providers have correct `adjustment_basis` values
- ✅ Query 2: Both availability columns exist and are queryable
- ✅ Query 3: Coverage ≥ 98%
- ✅ Query 4: Zero anomalies (no inverted ranges, partial NULLs)
- ✅ Query 5: Sample rows are consistent and reasonable
- ✅ Query 6: All NULL assignments have zero observations

**If any check fails:** Do not proceed. Report the failure to SE for investigation.

---

## Next Step (After Validation Passes)

Once all validations pass, Workbench may proceed with implementing `SPEC-panel-eligibility.md`:

1. Implement `include_delisted` parameter (default TRUE for historical research)
2. Implement `staleness_policy` (time-local exclusion, detection separate from eligibility)
3. Implement `dispersion_threshold` (parameterized aggregate suppression)
4. Integrate with observation-suitability classification (`classify_series()` → `derive_calendar()` → `apply_calendar()`)
5. Begin calibration study for provisional parameters (`staleness_policy`, `dispersion_threshold`)

---

**No further Workbench development proceeds until validation complete and passed.**
