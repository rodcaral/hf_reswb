# Class D Execution Gate Package — Seven Authorized D Relationships

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: gate-preparation only. No mutation, staging, merge, activation, or execution
performed. This package is not authorization to execute D. All facts below were gathered by
read-only `SELECT` queries against the live HistFinTS database at package-preparation time;
none constitutes a new financial-identity or disposition ruling — every identity/disposition
fact is recorded as already established, with its source document cited, not re-derived.**

---

## 1. Exact mutation scope

**Field**: `series.underlying_series_id` (and, contingent on domain confirmation, `series.ratio`
— currently `1.0` on all seven referrer rows; **this package proposes no ratio change and
flags ratio as explicitly out of scope for D unless SE separately authorizes it**, since a
ratio revision was never part of the seven D relationships as characterized in any prior
document).

**The seven relationships**, current stored FK vs. proposed corrected FK:

| Pair | Referrer (CEDEAR) series id | Current `underlying_series_id` (wrong target) | Proposed `underlying_series_id` (correct target) |
|---|---|---|---|
| MU | 11323 | 11342 | 6672 |
| MSFT | 11324 | 11348 | 6602 |
| AMD | 11325 | 11349 | 426 |
| MELI | 11326 | 11350 | 6319 |
| NU | 11327 | 11351 | 7085 |
| QQQ | 11328 | 11352 | 8193 |
| AMZN | 11329 | 11353 | 484 |

**Confirmed by direct query at package-preparation time** (2026-08-21): all seven referrer rows
currently carry `underlying_series_id` equal to their listed current (wrong) target, `ratio =
1.0` on all seven, matching every prior D document without deviation.

**Mutation is a single-column `UPDATE` on the `series` table, seven rows, one column
(`underlying_series_id`), nothing else.** Confirmed by schema inspection that:
- `underlying_series_id` lives only on `series`, not on `observation` — no observation row is
  a candidate for this mutation by construction.
- No `observation.import_run_id`, `observation.origin_import_run_id`, `observation.value`,
  `observation.open/high/low/volume`, or any `provider_assignment` row is addressed by an
  `UPDATE ... SET underlying_series_id = ...` statement scoped to these seven `series.id`
  values.

**Confirmed scope boundary**: the mutation changes seven referrer rows' pointer to their
own correct target. It does not touch the current-target rows (11342/11348/11349/11350/
11351/11352/11353) or the proposed-target rows (6672/6602/426/6319/7085/8193/484) themselves
— those rows are read (as the FK's destination), never written, by this mutation.

---

## 2. Financial identity gate

**Recorded as established, not reopened**: DFA ruled the seven D pairs represent the same
financial instrument across two historical data regimes (pre-2026-05-28 regime tracking the
referrer bit-for-bit; post-2026-05-28 regime independently tracking a plausible real-USD
value), with the 1h (current target) vs. 1d (proposed target) `configured_interval` difference
characterized as a sampling-configuration/representation difference, not a financial-identity
distinction (`REMEDIATION_ANALYSIS_UPDATE_DFA_RULING_2026-08-20.md`,
`CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md` Part B.1). **Confirmed unchanged at
package-preparation time**: current target `configured_interval='1h'`, proposed target
`configured_interval='1d'`, on all seven pairs, matching the ruling exactly. **This identity
question is not reopened, re-litigated, or re-verified by this package** — it is cited, not
re-decided.

---

## 3. 338/406 evidence boundary

**Recorded as established and preserved unresolved**: the post-transition leading-edge window
(405 stable dates under the stability rule, `CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md` Part
B.1) contains the 338/406 discrepancy population between current target and proposed target
values — an unresolved, un-adjudicated observation-level question, explicitly not to be
resolved by majority vote, destination-identity preference, or current-source preference
(`REMEDIATION_ANALYSIS_UPDATE_DFA_RULING_2026-08-20.md`). **D's mutation does not touch this
population**: the proposed `UPDATE` addresses `series.underlying_series_id` only, on the
referrer rows; it reads no `observation` row belonging to any of the fourteen series involved
(seven referrers, seven current targets, seven proposed targets) and writes none. **No
observation is adjudicated, deleted, overwritten, or reclassified by this mutation** — the 338
discrepancies remain exactly as many, exactly as unresolved, after D executes as before.

**The seven previously-adjudicated Class-C rows** (one crossed observation per current-target
series, 2026-05-28, seven-pair episode — verified value-correct/attribution accepted,
disposition closed, `CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md`) are **observation rows on
the current-target series, not the referrer series D's mutation writes to**. D's `UPDATE`
statement addresses `series.id IN (11323,11324,11325,11326,11327,11328,11329)` — none of the
seven Class-C rows live on those series ids. **Not reopened, not touched, not reachable by this
mutation's scope.**

---

## 4. Affected-row and reference analysis

**Rows affected by the mutation**: exactly 7 (the `series` table rows for the seven referrer
CEDEARs listed in §1). Zero `observation` rows. Zero `provider_assignment` rows.

**Incoming-reference finding, reconfirmed by direct query at package-preparation time**:

| Current target series id | Incoming references (`series.underlying_series_id = this id`) today |
|---|---|
| 11342 (MU) | 1 |
| 11348 (MSFT) | 1 |
| 11349 (AMD) | 1 |
| 11350 (MELI) | 1 |
| 11351 (NU) | 1 |
| 11352 (QQQ) | 1 |
| 11353 (AMZN) | 1 |

Each current-target series has **exactly one** incoming FK reference today — its own referrer,
the row this mutation repoints. **Post-mutation reference state**: each of the seven current-
target series will have **zero** incoming references (the sole referrer now points to the
proposed target instead) — each becomes a fully-orphaned series, still ACTIVE, still holding
its complete observation history (3,282 rows each, 1,535 for NU — reconfirmed at
package-preparation time), referenced by nothing. This is the exact, already-identified Groups
5–11 consequence (`CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md`), reconfirmed here as current
fact, not re-derived.

**Distinguished explicitly from the unrelated BABA/BIDU orphan population**: series 11345
(BABA-target, 1,513 observations) and 11346 (BIDU-target, 1,512 observations) are **not** part
of the seven D relationships, are not written by this mutation, and are not referenced by any
`underlying_series_id` value this mutation changes. Their disposition is a separate, standing
question (§6), and their obs counts are cited here only to make the distinction explicit, not
as evidence toward D.

---

## 5. Class-E containment gate

**Post-D catalog consequence, stated precisely**: at the moment D executes, the seven current-
target series (11342/11348/11349/11350/11351/11352/11353) transition from "D-contingent, not a
current Class-E candidate" to "orphaned series with a confirmed `SAME_INSTRUMENT`-tier
provider-symbol match against their own proposed target" — i.e., they become live Class-E
candidates only at that moment, not before (`CLASS_E_IDENTITY_SIGNAL_2026-08-21.md`,
`CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md` §2, which reproduced this exact
`SAME_INSTRUMENT` classification for the MU pair using real production data as a correctness
check, explicitly not as an activation).

**Containment demonstrated**: the identity-detection signal's output classes
(`SAME_INSTRUMENT` / `RELATED_BUT_DISTINCT` / `UNRESOLVED`) are evidence classifications only —
the implementation performs no deletion, reassignment, consolidation, or provenance rewriting,
and cannot be invoked to do so (`class_e_identity_signal.py`, pure function, no DB write
access). A `SAME_INSTRUMENT` verdict for one of the seven new post-D candidates enters the same
terminal state DFA has already ruled sufficient: **evidence recorded, no automatic
remediation triggered** (per the 2026-08-21 DFA gate ruling). **No code path exists in this
project that consumes an `IdentityVerdict` value to perform a mutation** — confirmed by the
same grep-based zero-integration check applied to every prior piece of this safeguard
infrastructure (`independence_detector.py`, `provenance_guard.py`).

**Explicitly not treated as complete**: the resulting population (≥11 pre-D, growing to at
least 18 post-D — 11 plus the seven newly-orphaned series, each producing at least one
`SAME_INSTRUMENT` candidate against its own proposed target) remains a **provisional discovery
lower bound**, per the standing DFA ruling — not asserted here as a closed count.

---

## 6. 11345/11346 boundary

**Recorded, not re-derived**: series 11345 (BABA-target) and 11346 (BIDU-target) are ACTIVE,
carry **zero `provider_assignment` rows** (confirmed by direct query, both package-preparation
time and in the prior discovery run), and hold 1,513 and 1,512 orphan observations
respectively (`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`).

**No duplicate financial identity is inferred from this fact by this package.** The
assignment-less state is a catalog/observation-provenance fact (these series have no
configured path by which a legitimate observation could ever have been written to them,
per `CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`), not evidence toward or against these series
being the same financial instrument as any counterpart — that remains the open ADR/
depositary-layer identity question DFA has not yet ruled on
(`CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`).

**Not included in the seven-row D mutation.** Confirmed: neither 11345 nor 11346 appears as a
referrer, a current target, or a proposed target in any of the seven relationships in §1. The
mutation's `WHERE` scope (`series.id IN (11323,11324,11325,11326,11327,11328,11329)`) cannot
reach either series.

---

## 7. Concurrency and baseline gate

**Recorded evidence point**: the observation table was previously reported quiescent at
27,972,816 rows (scheduler run completed, no in-flight import).

**Reconfirmed by direct query at this package's preparation time (2026-08-21)**:
`SELECT COUNT(*) FROM observation` returns **27,972,816** — matching the recorded baseline
exactly, with no drift observed between the original evidence point and this package's
preparation.

**This reconfirmation is not a substitute for a pre-execution check.** Per instruction, the
following checks are required **immediately before any future execution authorization**, not
satisfied by this package's confirmation alone (state can still drift between package approval
and actual execution):

1. `SELECT COUNT(*) FROM observation` — must equal the value recorded at the most recent
   evidence point immediately prior to execution; any difference means a scheduler run
   occurred in the interim and the evidence package must be refreshed before proceeding.
2. `SELECT MAX(id) FROM observation` — a secondary, monotonic check catching any insert even if
   a concurrent delete masked the count (defense against a coincidental count match).
3. Query `import_run` for any run in `RUNNING`/`PENDING`-equivalent status (no in-flight
   import at the moment of execution) — exact status-value check to be confirmed against the
   live `import_run.status` enum immediately before execution, since this package does not
   re-derive that enum's values.
4. Re-confirm all seven referrer rows' current `underlying_series_id` values still match §1's
   "current (wrong) target" column exactly — protects against a concurrent, unrelated change
   to these same seven rows between package approval and execution.
5. Re-confirm the seven current-target series' incoming-reference count is still exactly 1
   each (§4) — protects against a second referrer having been added to one of the seven current
   targets in the interim, which would change the post-mutation orphan analysis in §4/§5.

---

## 8. Integrity invariants (pre/post assertions)

All assertions are read-only `SELECT`s, to be run both immediately before and immediately
after execution, with the pre-execution values recorded as the comparison baseline.

| # | Invariant | Assertion |
|---|---|---|
| 1 | Total observation count unchanged | `SELECT COUNT(*) FROM observation` — pre value must equal post value exactly. |
| 2 | Seven target series' expected observations unchanged | `SELECT series_id, COUNT(*) FROM observation WHERE series_id IN (11342,11348,11349,11350,11351,11352,11353) GROUP BY series_id` — each series' count pre must equal post (3,282 each; 1,535 for NU/11351). |
| 3 | No change to `import_run_id` | `SELECT COUNT(*) FROM observation WHERE series_id IN (<all 21 series ids: 7 referrer + 7 current + 7 proposed>) AND import_run_id != <pre-recorded per-row value>` — expect 0 post-execution (requires a pre-execution row-level snapshot of `(id, import_run_id)` for exact comparison, not just an aggregate). |
| 4 | No change to `origin_import_run_id` | Same row-level snapshot approach as #3, applied to `origin_import_run_id` — expect 0 changed rows. |
| 5 | No change to provider assignments | `SELECT COUNT(*) FROM provider_assignment WHERE series_id IN (<all 21 series ids>)` and a row-level hash/snapshot of each row's non-`updated_at` columns — pre must equal post exactly. |
| 6 | No observation values changed | Row-level snapshot of `(id, value, open, high, low, volume)` for all observations on the 21 series — expect 0 changed rows post-execution. |
| 7 | Expected reference/catalog state after mutation | `SELECT underlying_series_id FROM series WHERE id IN (11323,11324,11325,11326,11327,11328,11329)` must equal the §1 "proposed (correct) target" column exactly, one-to-one; `SELECT COUNT(*) FROM series WHERE underlying_series_id IN (11342,11348,11349,11350,11351,11352,11353)` must equal 0 (confirming the seven current targets are now unreferenced, per §4). |
| 8 | Post-D Class-E candidates detectable and non-remediated | Run `detect_identity_candidates()` (`class_e_identity_signal.py`) against the fourteen affected series' real labels/provider assignments post-execution; expect exactly seven new `SAME_INSTRUMENT` candidates (current target vs. its own proposed target, per pair) and seven `RELATED_BUT_DISTINCT` candidates (referrer vs. proposed target, same `.BA`-suffix pattern as §5) — and confirm by code inspection (already true by construction, re-confirm post-execution that no code path was added that consumes this output for mutation) that none of these candidates triggers any automated action. |

---

## 9. Rollback

**Per-mutation rollback selector** — each of the seven `UPDATE`s is reversible by restoring the
single pre-execution value on the uniquely-identified row:

| Referrer series id | Rollback selector | Value to restore |
|---|---|---|
| 11323 | `series.id = 11323` | `underlying_series_id = 11342` |
| 11324 | `series.id = 11324` | `underlying_series_id = 11348` |
| 11325 | `series.id = 11325` | `underlying_series_id = 11349` |
| 11326 | `series.id = 11326` | `underlying_series_id = 11350` |
| 11327 | `series.id = 11327` | `underlying_series_id = 11351` |
| 11328 | `series.id = 11328` | `underlying_series_id = 11352` |
| 11329 | `series.id = 11329` | `underlying_series_id = 11353` |

**Why the rollback selector cannot select unrelated rows**: each selector is a primary-key
equality on `series.id` — a single, unique row per statement, not a range, a `LIKE` pattern, or
a join. No other `series` row shares any of these seven ids by definition. **Why it cannot
silently reverse unrelated work**: the rollback restores exactly one column
(`underlying_series_id`) to exactly one previously-recorded value per row; it does not touch
`ratio`, `configured_interval`, `status`, or any other column that might have been legitimately
changed by unrelated activity between execution and a rollback decision. If any of those seven
rows' `underlying_series_id` has been further modified by unrelated activity after D executes
(a scenario this package flags but does not consider likely, given no other code path writes
this field), the rollback would overwrite that later change too — this is an inherent property
of a value-restore rollback, not specific to D, and is why the pre-execution row-level snapshot
(§8, invariants #3–#6) must be retained as the authoritative "value to restore" record, not
re-derived from memory or this table at rollback time.

**Evidence/export to retain before execution**:
1. A complete row-level export of all seven referrer rows (`series.id IN (11323..11329)`,
   every column) — the primary rollback source.
2. A complete row-level export of `observation` for all 21 affected series (7 referrer + 7
   current target + 7 proposed target) — `(id, series_id, import_run_id, origin_import_run_id,
   observed_at, value, open, high, low, volume, created_at, updated_at)` — the invariant-check
   baseline for §8 #3, #4, #6.
3. A complete row-level export of `provider_assignment` for the same 21 series — the invariant
   baseline for §8 #5.
4. The pre-execution `SELECT COUNT(*) FROM observation` and `SELECT MAX(id) FROM observation`
   values (§7) — the concurrency baseline.
5. This package itself, timestamped, as the authorized-scope record against which any
   deviation at execution time must be checked (§7 checks 4–5).

---

## 10. Execution classification

| Gate | Status | Outstanding condition (if not GO) |
|---|---|---|
| Domain authorization | **GO** | DFA has ruled the seven relationships financially established and authorized SE to prepare this gate package (2026-08-21 gate ruling). No outstanding domain condition for the seven D relationships themselves. |
| Mutation scope | **GO** | Scope confirmed single-column, seven-row, `series.underlying_series_id` only, reconfirmed by query at package-preparation time. |
| Provenance safety | **GO** | Confirmed by schema inspection that no `observation`, `import_run_id`, `origin_import_run_id`, or `provider_assignment` field is reachable by this mutation's `WHERE` scope. |
| Concurrency/state | **CONDITIONAL GO** | Baseline reconfirmed quiescent at 27,972,816 as of this package's preparation, but §7's five pre-execution checks have not yet been run *immediately before* execution (they cannot be, until an execution time is set) — outstanding condition: run the §7 checklist immediately before execution and confirm no drift. |
| Class-E containment | **GO** | Containment demonstrated by construction (no code path consumes `IdentityVerdict` for mutation) and by the DFA gate ruling accepting unresolved/contingent as a terminal state. |
| Rollback | **GO** | Per-row, primary-key-scoped rollback selectors defined for all seven mutations; required pre-execution export list specified in §9. |
| Post-execution verification | **CONDITIONAL GO** | All eight invariants in §8 are defined and executable, but none has been run yet — cannot be GO until execution occurs and the checks are actually performed. This is expected sequencing (verification cannot precede execution), not a gap in the package. |

---

## Conclusion

**READY FOR SE/PO AUTHORIZATION** — all gates are satisfied at the package-preparation level;
the two CONDITIONAL GO items (concurrency/state, post-execution verification) are sequencing
conditions inherent to any execution gate, not open design or evidence questions. Both
conditions have an exact, already-specified procedure (§7's five checks; §8's eight
assertions) that requires only the act of running them at execution time — no further
Workbench investigation, evidence gathering, or DFA ruling is needed to satisfy either.

**This package does not authorize execution.** It returns to SE for final gate review and, if
appropriate, routing of the execution decision to DFA/PO. No mutation, staging, merge,
activation, or execution was performed in preparing it. No SQL in this document is intended to
be run as-is; the `UPDATE` scope described in §1 is stated as a specification for SE/DFA/PO
review, not as an executable migration.
