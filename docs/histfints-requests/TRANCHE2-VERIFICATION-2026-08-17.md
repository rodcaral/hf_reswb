# Tranche 2 Schema Verification — Current Implementation State

**Date:** 2026-08-17  
**Status:** Both items unresolved; verification against live production database  
**Database:** `C:\Users\CarlonTinto\AppData\Local\histfints\histfints\histfints.db`

---

## Executive Summary

**ITEM 1 — Adjustment Basis Population: NOT IMPLEMENTED**
- `provider.adjustment_basis` column exists
- **All three values are NULL** for all providers (FRED, Yahoo Finance, BYMA)
- No backfill has occurred

**ITEM 2 — Provider-Assignment Availability Marker: NOT IMPLEMENTED, STRUCTURAL GAP DISCOVERED**
- `provider_assignment` table has NO availability columns
- `first_available_date` and `last_available_date` exist only on `provider_symbol`
- **`provider_symbol` has NO connection to `provider_assignment` or `series`** — unreachable from the operational path
- No foreign key or join path exists to traverse Series → ProviderAssignment → Availability

Both items are genuinely missing, not partially completed or overlooked.

---

## Detailed Findings

### Item 1: Adjustment Basis Population

**Current state of `provider.adjustment_basis`:**

```sql
SELECT display_name, adjustment_basis FROM provider ORDER BY display_name;
```

| display_name | adjustment_basis |
|---|---|
| BYMA | NULL |
| FRED | NULL |
| Yahoo Finance | NULL |

**Required values (per D-042 specification):**
- FRED → `UNADJUSTED`
- Yahoo Finance → `SPLIT_ADJUSTED`
- BYMA → `UNADJUSTED`

**Status:** Column exists, no data. A straightforward backfill, no schema migration needed.

---

### Item 2: Provider-Assignment Availability Marker

**Current `provider_assignment` schema:**

```
Column name                  | Type    | Nullable | Notes
-----------------------------|---------|----------|----------
id                           | INTEGER | NO       | PK
series_id                    | INTEGER | NO       | FK to series
provider_id                  | INTEGER | NO       | FK to provider
priority                     | INTEGER | NO       |
provider_series_identifier   | TEXT    | NO       |
created_at                   | TEXT    | NO       |
updated_at                   | TEXT    | NO       |
reassigned_via_series_merge_id | INTEGER | YES     |
adjustment_basis_override    | TEXT    | YES      | ← Exists but is NULL for all 11,321 rows
last_revalidated_at          | TEXT    | YES      |
next_revalidation_at         | TEXT    | YES      |
revalidation_window_days     | INTEGER | YES      |
```

**Availability columns needed:**
- `first_available_date` (TEXT, nullable, ISO 8601)
- `last_available_date` (TEXT, nullable, ISO 8601)

**Current status:** Neither column exists. Required schema addition.

---

### Item 2 Structural Issue: Unreachability of `provider_symbol`

The request assumed `provider_symbol.first_available_date` and `last_available_date` could serve as a fallback. They cannot, for architectural reasons:

**`provider_symbol` schema:**

```
Column name          | Type    | Nullable | FK
---------------------|---------|----------|------------------
id                   | INTEGER | NO       | PK
provider_id          | INTEGER | NO       | FK to provider (NOT to provider_assignment)
raw_ticker           | TEXT    | NO       |
base_symbol          | TEXT    | YES      |
currency             | TEXT    | YES      |
settlement_mechanism | TEXT    | YES      |
venue                | TEXT    | YES      |
share_class          | TEXT    | YES      |
security_type        | TEXT    | YES      |
valid_from           | TEXT    | NO       |
valid_to             | TEXT    | YES      |
last_verified_at     | TEXT    | YES      |
first_available_date | TEXT    | YES      | ← Desired data is here
last_available_date  | TEXT    | YES      | ← Desired data is here
verification_status  | TEXT    | NO       | DEFAULT 'UNVERIFIED'
created_at           | TEXT    | NO       |
updated_at           | TEXT    | NO       |
```

**The structural problem:**

```
Series
  │
  ├─ provider_assignment (series_id FK)
  │    └─ provider_id FK → provider
  │
provider_symbol
  │
  └─ provider_id FK → provider
  
[NO LINK between provider_assignment and provider_symbol]
[NO series_id column in provider_symbol]
```

**Why `provider_symbol` cannot substitute:**

1. **No direct path from Series:** To find availability for series X via provider_assignment Y, you need to join provider_assignment → provider_symbol. But provider_symbol links only to provider.id, not to provider_assignment.id.

2. **No series context:** provider_symbol does not contain which specific Series it relates to. It is a Catalog object (mapping raw tickers to provider-internal IDs), not an operational object tied to a Series.

3. **Wrong layer:** The Catalog (provider_symbol) serves bulk discovery. The operational side (provider_assignment) serves Series identity. Workbench reads Series → ProviderAssignment; it does not read the Catalog.

**Concrete example — Query that would be needed but is impossible:**

```sql
-- What we need to do: get availability for a Series from its assignment
SELECT 
  s.id, s.label,
  pa.id as assignment_id,
  pa.first_available_date,  -- ← This doesn't exist
  pa.last_available_date    -- ← This doesn't exist
FROM series s
JOIN provider_assignment pa ON s.id = pa.series_id
WHERE s.id = 11312;
```

**What actually exists (doesn't help):**

```sql
-- provider_symbol data is not indexed by provider_assignment
SELECT ps.first_available_date, ps.last_available_date
FROM provider_symbol ps
WHERE ps.provider_id = 2  -- Yahoo Finance
LIMIT 1;
-- Returns data, but for which provider_assignment? Unknown.
-- No way to match it back to series 11312.
```

---

## Implementation Requirements

**Item 1: Adjustment Basis Backfill**

Schema task: Populate `provider.adjustment_basis` with:
- FRED: `UNADJUSTED`
- Yahoo Finance: `SPLIT_ADJUSTED`
- BYMA: `UNADJUSTED`

No schema migration. Three UPDATE statements.

**Item 2: Add Availability Marker to Provider-Assignment**

Schema migration: Add two columns to `provider_assignment`:

```sql
ALTER TABLE provider_assignment ADD COLUMN first_available_date TEXT;
ALTER TABLE provider_assignment ADD COLUMN last_available_date TEXT;
```

Application task: Populate these columns. For each provider_assignment row:
1. Find the corresponding provider (via provider_id)
2. Determine the earliest and latest `observed_at` in HistFinTS.observation for this assignment
3. Populate first_available_date and last_available_date accordingly

This is deterministic from the data (no inference needed). Can be run as a backfill after the schema lands.

---

## Verification Queries (Workbench-side — what will work once Items 1 & 2 land)

**Once both items are implemented, these queries will be available to Workbench:**

```sql
-- Get a Series' adjustment basis
SELECT 
  s.id, s.label,
  p.display_name as provider,
  p.adjustment_basis
FROM series s
JOIN provider_assignment pa ON s.id = pa.series_id
JOIN provider p ON pa.provider_id = p.id
WHERE s.id = 11312;
```

**Expected result after Item 1 backfill:**
```
id   | label                               | provider      | adjustment_basis
-----|-------------------------------------|---------------|------------------
11312| YPF Sociedad Anonima CEDEAR (BYMA) | Yahoo Finance | SPLIT_ADJUSTED
```

```sql
-- Get availability status for a Series' provider assignment
SELECT 
  s.id, s.label,
  pa.id as assignment_id,
  pa.first_available_date,
  pa.last_available_date,
  COUNT(o.id) as observation_count
FROM series s
JOIN provider_assignment pa ON s.id = pa.series_id
LEFT JOIN observation o ON pa.series_id = o.series_id 
  AND o.observed_at >= pa.first_available_date
  AND o.observed_at <= pa.last_available_date
WHERE s.id = 11312
GROUP BY s.id, pa.id;
```

**Expected result after Item 2 implementation:**
```
id   | label                               | assignment_id | first_available_date | last_available_date | observation_count
-----|-------------------------------------|---------------|----------------------|---------------------|---------
11312| YPF Sociedad Anonima CEDEAR (BYMA) | NNN           | 2000-01-03           | 2026-08-14          | 6624
```

---

## Blockers for Workbench Implementation

**`SPEC-panel-eligibility.md` cannot be implemented without:**

1. ✗ Item 1: `provider.adjustment_basis` populated for all three providers
2. ✗ Item 2: `provider_assignment.first_available_date` and `provider_assignment.last_available_date` columns added and populated

**Neither item is in place as of 2026-08-17.**

---

## Recommendation

File both items as a single schema+application request to HistFinTS team:

1. **Schema migration:** Add two columns to `provider_assignment`
2. **Data backfill:**
   - Populate `provider.adjustment_basis` (3 UPDATEs)
   - Populate `provider_assignment.first_available_date` and `.last_available_date` (deterministic from observation data)
3. **Verification:** Run the queries above to confirm both are usable from Series

This is a straightforward backfill task, not a complex feature. No architectural changes. Both items are deterministic from existing data.
