# Remediation Package — Class A (111 Fabricated MERVAL Observations)

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: design only. Nothing executed. No observation deleted, no `import_run_id` or
`origin_import_run_id` altered, no schema/calibration/policy change, frozen baseline
untouched.**

---

## Evidence

Two independent signals define the identical 111-row set, re-verified by fresh read-only
query for this package:

| Signal | Definition | Result |
|---|---|---|
| Run-id boundary | `import_run_id IN (58332, 58333, 58334, 58335)` | 111 rows |
| Fractional-second signature | `instr(observed_at, '.') > 0` | 111 rows |
| **Agreement** | | **Exact — same 111 rows under both** |

**Full run detail** (re-verified):

| Run | Started/created | Series | Rows |
|---|---|---|---|
| 58332 | 2026-08-19T01:22:16.842980Z | 11364 (Pfizer Inc. CEDEAR) | 26 |
| 58334 | 2026-08-19T01:22:24.585411Z | 11364 (Pfizer Inc. CEDEAR) | 24 |
| 58333 | 2026-08-19T01:22:16.842980Z | 11366 (Vale S.A. CEDEAR) | 33 |
| 58335 | 2026-08-19T01:22:24.585411Z | 11366 (Vale S.A. CEDEAR) | 28 |

All four runs `trigger_type = MANUAL`, `status = SUCCESS`, zero-elapsed (`started_at ==
ended_at` to the microsecond) — consistent with the previously-documented
`ConnectionResetError`-on-all-paths finding (the endpoint was unreachable; these rows were
fabricated, not fetched).

**Series impact, re-verified**: 11364 currently holds 53 total observations (50 fractional +
**3 non-fractional**); 11366 holds 64 total (61 fractional + **3 non-fractional**). Both
series retain legitimate rows after the 111 are removed — neither would be emptied.

---

## Exact proposed scope

`observation.id` values whose `import_run_id ∈ {58332, 58333, 58334, 58335}` — equivalently,
whose `series_id ∈ {11364, 11366}` **and** `instr(observed_at, '.') > 0`. Both formulations
of the scope agree exactly (111 rows each); either may serve as the operative `WHERE` clause
because they are provably identical sets, not because either alone is preferred.

**Explicitly excluded from scope**: the 6 non-fractional rows on 11364/11366 (3 each) —
these are legitimate observations sharing a series with the fabricated rows and must not be
touched by a scope defined loosely as "everything on series 11364/11366."

---

## Proposed mutation (described, not executed)

1. **Archive** all 111 rows in full (already captured in the frozen baseline's
   `class_a_rows.csv`; a second, independent export immediately pre-repair is recommended so
   the archive is contemporaneous with the actual delete, not only with the baseline capture
   date).
2. **Delete** the 111 `observation` rows matching the scope above.
3. **Preserve** the four `import_run` rows (58332–58335) — do not delete them. They are the
   fabrication's own record; removing them alongside the observations would destroy evidence
   that the fabrication happened and how.
4. **Separately**, correct the MERVAL adapter/provider configuration so it cannot write
   against a non-serving endpoint again. This is a distinct, non-data change (code/config, not
   `observation` rows) and is not scoped further in this package.

No `import_run_id` or `origin_import_run_id` value on any surviving row is touched by this
mutation — the deletion removes rows entirely rather than modifying provenance fields on
rows that remain.

---

## Independent verification

**Primary — orthogonal to the deletion mechanism**: the fractional-second count
(`instr(observed_at, '.') > 0`) over the **entire** `observation` table, re-run post-repair,
must return **0**. This is a property of `observed_at` string content alone, unrelated to
`import_run_id`, so it cannot be satisfied by the deletion mechanism accidentally missing rows
that the run-id scope would also miss.

**Secondary**: total `observation` count decreases by exactly 111, net of ordinary BYMA
evidence-cohort accrual (~21 rows/session) in the interval between pre- and post-repair
counts.

**Falsified by**: any remaining fractional-second row anywhere in the table; a total-count
delta that doesn't reconcile to exactly −111 once accrual is netted out.

---

## Rollback

The archived export (step 1 above) is the rollback path: re-insertion of the 111 rows from
the archive, with their original `id`, `series_id`, `import_run_id`, `observed_at`, `value`,
and other fields restored exactly. Because `origin_import_run_id` is `NULL` on all 111 rows
(pre-epoch), rollback does not need to reconstruct an origin value — `NULL` is the correct
restored state, not a gap introduced by rollback.

**Rollback is only as good as the archive's completeness** — if the pre-repair archive omits
any field later found to matter (e.g. `open`/`high`/`low`/`volume`, not explicitly listed in
the frozen baseline's CSV schema as verified in this package), rollback would restore an
incomplete row. This package recommends the pre-repair archive capture every column of
`observation`, not a subset, but does not itself verify what the existing `class_a_rows.csv`
contains column-for-column.

---

## Unresolved cases

None within the 111-row population itself — the boundary is exact and two independent signals
agree on every row. The only adjacent unresolved item is the **separate** provider-correction
obligation (§ "Proposed mutation," item 4): until `merval.py` (or equivalent) is fixed, new
fabricated rows could recur, and this package's verification signal (§ "Independent
verification") would need to be re-run after any subsequent MERVAL activity, not treated as
permanently satisfied by one clean result.

---

## Explicit execution prerequisites

1. SE/product authorization to execute (not granted by this package).
2. A fresh, complete row-level export of all 111 rows (all columns), immediately preceding
   execution — not solely relying on the frozen baseline's earlier capture, which may predate
   the actual execution by an unknown interval.
3. Confirmation that the separate MERVAL provider-correction fix is scheduled or completed —
   not a technical blocker on the deletion itself, but recommended so the verification signal
   in this package isn't immediately re-triggered by new fabricated writes.
4. Re-run of the fractional-second and total-count verification queries, both immediately
   before (to confirm the pre-state matches this package's evidence) and immediately after
   execution.
