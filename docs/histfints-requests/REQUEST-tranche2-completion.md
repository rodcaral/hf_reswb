# REQUEST — Tranche 2 Schema: Complete Both Items

**Status:** pending · **Filed:** 2026-08-17 · **Blocking:** `SPEC-panel-eligibility.md` implementation

Referenced by: D-035 (F-009 freeze, pending), D-040 (observation-suitability freeze, pending), D-041 (next decision).

---

## Context

D-035 and D-039 completed F-009 evidence consumption and observation-suitability classification. Both are blocked at the boundary by two unfinished Tranche 2 items:

1. **Adjustment basis population** — The `provider.adjustment_basis` column exists (schema present), but is NULL for all three providers (`FRED`, `Yahoo Finance`, `BYMA`). This must be backfilled so SPEC-panel-eligibility.md's `adjustment_policy` parameter can be activated.
2. **Provider-assignment availability marker** — This was never built. Only `provider_symbol` (Catalog-side, unreachable from most Series per D-025) holds `first_available_date`/`last_available_date`. A provider-assignment-level availability marker is needed to populate SPEC-panel-eligibility.md's `minimum_coverage` parameter. (This is distinct from the Q-062 question "is provider_symbol reachable from series_id?" — even if reachable, the wrong table currently holds the data.)

Neither item has a dependency on the other. Both must be in the same request so that:
- a complete list of what Tranche 2 actually covered vs. what was left open is produced
- D-040's cleanup decision (live verification vs. assumption, D-009b) is closed as a unit

---

## Item 1: Adjustment Basis Population

**What:** Backfill `provider.adjustment_basis` with the documented basis for each provider's historical observations:
- `FRED` → `NULL` or `UNADJUSTED` (FRED publishes no adjustments in the NBER dataset the project uses)
- `yahoo_finance` → `SPLIT_ADJUSTED` (Yahoo applies split adjustments; dividend-unadjusted per D-005, D-021)
- `byma` → `UNADJUSTED` (BYMA publishes raw prices)

**Why:** `SPEC-panel-eligibility.md` defines an `adjustment_policy` parameter (active once this field is populated) that screened Series must declare their basis, and the panel must apply a consistent basis to all members. Without this, heterogeneous adjustment bases are silently mixed into the consensus.

**Schema:** The column already exists; this is a one-time backfill task, not a schema migration.

---

## Item 2: Provider-Assignment Availability Marker

**What:** Add two columns to `provider_assignment`:
- `first_available_date` (TEXT, nullable, ISO 8601) — the earliest date in HistFinTS.observation for this assignment
- `last_available_date` (TEXT, nullable, ISO 8601) — the latest date in HistFinTS.observation for this assignment

or, alternatively, a single availability-status column if a finer grain is required (e.g., `status IN ('AVAILABLE', 'TRUNCATED', 'NO_DATA')`).

**Why:** `SPEC-panel-eligibility.md` defines a `minimum_coverage` parameter that currently cannot distinguish *"the provider has little data"* from *"our fetch was truncated"* (F-017 documents this as a confirmed live condition on the `import_run` side, and it propagates to the provider-assignment level as well). Without a marker on the operational path (`Series → ProviderAssignment`), this parameter is unreachable for directly-created Series (D-026) and will describe the wrong provider for all others.

**Schema:** New columns on `provider_assignment` (not on `provider_symbol`, which is Catalog-side and has a different structural role).

---

## Timeline and Integration

No dependency order between items 1 and 2. Both are needed before `SPEC-panel-eligibility.md` implementation can resume. The project's next step (D-041) waits for confirmation that both are resolved before proceeding to domain review on Q-061.
