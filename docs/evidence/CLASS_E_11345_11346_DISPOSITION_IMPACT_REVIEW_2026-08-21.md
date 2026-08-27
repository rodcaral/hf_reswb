# Class-E/Catalog-State Impact Review — 11345/11346 Disposition

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: read-only impact review only. No mutation performed. The ADR/CEDEAR identity
question is not reopened — DFA's ruling (11345/11346's observations are CEDEAR content
belonging to 11316/11317; the two series are to be eventually deprecated, not deleted) is
treated as fixed input, not re-evaluated. This document does not authorize, stage, or
recommend execution — it characterizes consequences only. Distinct from, and not rolled into,
Class D, which is already executed and closed as its own gate.**

---

## 0. Series involved, real state confirmed by read-only query

| Series | Label | Status | Obs count | Obs date range | Provider assignments | Incoming refs |
|---|---|---|---|---|---|---|
| 11345 (BABA-target) | Alibaba Group Holding Limited - ADS (NYSE) | ACTIVE | 1,513 | 2020-03-12 → 2026-05-28 | none | 0 |
| 11346 (BIDU-target) | Baidu Inc. - ADS (NASDAQ) | ACTIVE | 1,512 | 2020-03-13 → 2026-05-28 | none | 0 |
| 11316 (target CEDEAR) | Alibaba Group Holding Limited CEDEAR (BYMA) | ACTIVE | 79 | 2026-05-29 → 2026-08-20 | Yahoo `BABA.BA`, MERVAL `BABA` | 0 |
| 11317 (target CEDEAR) | Baidu, Inc. CEDEAR (BYMA) | ACTIVE | 79 | 2026-05-29 → 2026-08-20 | Yahoo `BIDU.BA`, MERVAL `BIDU` | 0 |
| 903 (real ADR, underlying of 11316) | Alibaba Group Holding Limited ADS... | ACTIVE | 2,997 | 2014-09-19 → 2026-08-20 | Yahoo `BABA` | 1 |
| 1169 (real ADR, underlying of 11317) | Baidu, Inc. ADS... | ACTIVE | 5,293 | 2005-08-05 → 2026-08-20 | Yahoo `BIDU` | 1 |

**Key structural fact, verified, load-bearing for §1**: 11345's observation range
(2020-03-12 → 2026-05-28) and 11316's observation range (2026-05-29 → 2026-08-20) do not
overlap — 11316 begins the day immediately after 11345 ends. The identical pattern holds for
11346/11317. This is a clean date boundary, the same structural shape already established for
Class B, though **this document does not propose using it as a repair mechanism** — it is
reported as a relevant fact for SE's own future scoping, not acted on here.

`11345`/`11346` observations: `import_run_id` 25556/25557 respectively (single run each,
consistent with `CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`); `origin_import_run_id` NULL on all
rows (historical-NULL, pre-epoch — not a defect per D-032/D-033).

Only `status = 'ACTIVE'` exists anywhere in the live `series` table today — no series is
currently `ARCHIVED`, so "eventual deprecation" as DFA describes it has no precedent instance
in this database to model against; the schema does carry an `archived_at` column, suggesting
the mechanism exists even though it is unused today.

---

## 1. Impact matrix

| Dimension | Pre-disposition (current) | Post-disposition (if implemented as DFA describes) | Containment requirement |
|---|---|---|---|
| **Observation attribution** | 1,513 rows on 11345 (`import_run_id` 25556), 1,512 rows on 11346 (`import_run_id` 25557) — both isolated, zero-overlap with 11316/11317's own 79 rows each | Rows re-pointed (`observation.series_id`) from 11345/11346 to 11316/11317; 11316 grows from 79 to 1,592 rows spanning 2020-03-12 → 2026-08-20 (no internal date collision, confirmed above), 11317 similarly to 1,591 rows | Must not touch `import_run_id` or `origin_import_run_id` on the moved rows (§2 of the standing invariant set, same principle as Class D's gate); must not silently overwrite any of 11316/11317's own 79 rows — reattribution is additive to a disjoint date range, not a replace |
| **Catalog identity/status** | 11345/11346 `status = 'ACTIVE'`, fully populated, no provider path | 11345/11346 eventually `status = 'ARCHIVED'` (or equivalent — no live precedent value to cite), `archived_at` populated, series row retained (not deleted) per DFA's explicit "deprecated rather than deleted" | Must not delete the 11345/11346 rows; must not delete or truncate their pre-move observation history in the same operation that also moves it — the two are logically the same rows post-move, but the transition mechanism (copy-then-archive vs. move-then-archive) is a design detail SE has not yet specified and this document does not decide |
| **Provider assignments** | 11345/11346: zero rows. 11316/11317: two rows each (Yahoo + MERVAL), unchanged by this disposition | No provider-assignment change proposed or implied by DFA's ruling — 11345/11346 remain assignment-less even after deprecation (they are not being given a live fetch path, they are being retired) | Must not add a `provider_assignment` row to 11345/11346 as a side effect of deprecation — doing so would newly activate the primary Class-E signal for them, a consequence not requested or evidenced here |
| **Underlying relationships** | 11316 → `underlying_series_id = 903`; 11317 → `underlying_series_id = 1169`; 11345/11346 have `underlying_series_id = NULL` (not CEDEARs themselves, not FK-linked to anything) | No `underlying_series_id` change proposed for 11316/11317/903/1169 — the disposition is about *observation and status*, not about the already-correct CEDEAR→ADR relationship, which is untouched | Must not alter `underlying_series_id` on 11316, 11317, 903, or 1169 as part of implementing this disposition — none of that relationship is in scope |
| **Class-E candidate detection** | 11345/11346 resolve to `UNRESOLVED` today (zero provider assignment, real production labels do not match under this project's punctuation-only normalization — `CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md` §1.1) | **Unchanged**, provided no provider assignment is added (see row above): 11345/11346 still have zero provider assignments post-deprecation, so the detector's primary signal remains structurally inapplicable and they remain `UNRESOLVED`. A `status = 'ARCHIVED'` value is not read by `class_e_identity_signal.py` at all — the detector has no status-awareness, so archival alone cannot change any verdict | If a future step ever assigns 11345/11346 a provider identifier (e.g. to formally alias them to 11316/11317), that would newly produce a `SAME_INSTRUMENT` or `RELATED_BUT_DISTINCT` candidate — flagged here as a foreseeable *future* consequence, not something this disposition as currently described does |

---

## 2. Existing candidates vs. candidates that would arise only after this disposition

**Existing (already on record, unaffected by whether this disposition is ever implemented)**:
- Groups 1–4 (11344/11345/11346/11347): `UNRESOLVED`, per the discovery run.
- 10165 ↔ 11340 (UBER): `SAME_INSTRUMENT`, unrelated issuer, unaffected by anything Alibaba/
  Baidu-related by construction (different companies, different provider symbols).
- The 21 post-D candidate pairs (`CLASS_E_POST_D_OBSERVATION_STUDY_2026-08-21.md`).

**Would arise only after this disposition, and only if implemented exactly as currently
scoped by DFA (observation move + status change, no provider-assignment change)**: **none**,
under the detector as it exists today. The disposition as DFA described it (observation
reattribution + eventual archival, no provider-assignment change) produces **zero new
Class-E candidates**, because the detector's primary and secondary signals are both keyed off
`provider_assignment` data, which this disposition does not touch. The only path to a new
candidate would be a *different*, not-yet-proposed future step (assigning 11345/11346 a
provider identifier) — explicitly out of scope for what was described here.

**Confirmed: no unresolved candidate is implicitly promoted.** 11345/11346 remain
`UNRESOLVED` before and after; 10165↔11340 is unaffected (different issuer entirely, no shared
series, no shared provider symbol); no candidate's verdict changes as a mechanical consequence
of implementing this disposition.

---

## 3. Containment requirements, consolidated

For any future execution of this disposition (none proposed or authorized here):

1. Observation reattribution must not alter `import_run_id` or `origin_import_run_id` on the
   moved rows.
2. Must not delete 11345/11346's series rows (DFA: deprecate, not delete).
3. Must not delete observation history in a way that leaves no record of the original
   attribution — an audit trail requirement, not specified further here since the exact
   mechanism (copy-then-archive vs. move-then-archive) is undecided.
4. Must not add a `provider_assignment` row to 11345/11346 as a side effect — doing so would
   change their Class-E status from `UNRESOLVED` to something else, a consequence not
   evidenced or requested by DFA's ruling.
5. Must not alter `underlying_series_id` on 11316, 11317, 903, or 1169 — the CEDEAR→ADR
   relationship is not in scope.
6. Any Class-E candidate that becomes newly detectable at some future point (only if a later,
   separate step adds provider data to 11345/11346) must enter the same unresolved/candidate
   terminal state already established and accepted by DFA's 2026-08-21 gate ruling — not
   trigger automatic deletion, reassignment, provider-assignment mutation, or provenance
   rewriting. No code path in this codebase currently does so (confirmed, `class_e_identity_
   signal.py` has no DB write access).

---

## 4. Standing rules preserved

- **The ≥11 Class-E population figure remains a provisional discovery lower bound.** This
  review adds no new candidate count and does not reinterpret the figure.
- **The ADR/CEDEAR identity question is not reopened.** DFA's ruling is treated as fixed input
  throughout.
- **This is a separate remediation decision from Class D.** D is already executed and closed
  under its own gate; nothing in this document rolls the 11345/11346 disposition into that
  gate, and DFA's ruling here is not treated as execution authorization for anything.
- **No production mutation of any kind was performed in preparing this review.** All facts
  above were gathered via read-only `SELECT` against the live database.

---

## Conclusion

Implementing the disposition exactly as DFA described it — observation reattribution to
11316/11317, eventual archival (not deletion) of 11345/11346, no provider-assignment or
`underlying_series_id` change — is, on the catalog-state evidence gathered here, **mechanically
clean**: no date-range collision, no incoming-reference conflict, no Class-E candidate
promotion, no effect on 10165↔11340 or any other unresolved candidate. The open items are
process questions for SE (exact status value to use, copy-vs-move mechanism, audit-trail
retention), not evidence gaps — this document does not resolve those, and does not authorize
implementation.
