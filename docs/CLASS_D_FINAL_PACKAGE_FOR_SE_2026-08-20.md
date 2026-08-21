# Class D — Final Consolidated Package for SE

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: read-only. No repair executed or staged. No observation, FK, provenance field,
schema, or calibration/policy state altered.**

---

## 1. Orphan-series identities and their post-repoint state

Repointing the seven referrer CEDEARs' `underlying_series_id` to the proposed targets leaves
the seven current-target series with **zero incoming FK references** (verified directly —
each has exactly one today, its own referrer). Full profile:

| Ticker | Current-target series | Label | Status | Total obs | Pre-transition obs (dup-of-CEDEAR regime) | Post-transition obs (independent-tracking regime) |
|---|---|---|---|---|---|---|
| MU | 11342 | Micron Technology, Inc. - Stock (NASDAQ) | ACTIVE | 3,274 | 2,866 | 408 |
| MSFT | 11348 | Microsoft Corporation - Stock (NASDAQ) | ACTIVE | 3,274 | 2,866 | 408 |
| AMD | 11349 | Advanced Micro Devices - Stock (NASDAQ) | ACTIVE | 3,274 | 2,866 | 408 |
| MELI | 11350 | MercadoLibre Inc. - Stock (NASDAQ) | ACTIVE | 3,274 | 2,866 | 408 |
| NU | 11351 | Nu Holdings Ltd. - Stock (NYSE) | ACTIVE | 1,527 | 1,119 | 408 |
| QQQ | 11352 | Invesco QQQ Trust - ETF (NASDAQ) | ACTIVE | 3,274 | 2,866 | 408 |
| AMZN | 11353 | Amazon.com Inc. - Stock (NASDAQ) | ACTIVE | 3,274 | 2,866 | 408 |

**Post-repoint state, precisely**: all seven remain `ACTIVE`, fully populated, referenced by
nothing. D's mutation does not delete, archive, or otherwise change any of these seven series
or their observations — it only removes the one incoming pointer each currently has.

---

## 2. The exact Class-E dependency

**Structural (schema-level)**: `series.underlying_series_id REFERENCES series(id) ON DELETE
RESTRICT` — confirmed directly from the live schema. This blocks *deletion* of any series
still referenced by another series' `underlying_series_id`. It does not block D's repoint
itself (an `UPDATE`, not a `DELETE`), and does not block the current targets from continuing
to exist post-repoint — it only means any future *deletion* of a shadow series still
referenced by an FK would fail, which is why D (removing the reference) must precede any E
action that would delete a series still pointed to.

**Newly demonstrated this pass — a second, more specific Class-E dependency beyond the FK
constraint**: after repointing, **all seven current-target series become three-way label
duplicates** with their own referrer CEDEAR and the proposed target, corrected from an
initial pass that found only 5 of 7 due to a punctuation inconsistency (the same
comma-presence/absence pattern already documented for the BIDU case in
`CLASS_E_GATES_FOR_BABA_BIDU_2026-08-20.md`):

| Ticker | Referrer CEDEAR | Current target (orphan-to-be) | Proposed target |
|---|---|---|---|
| MU | Micron Technology, Inc. CEDEAR (BYMA) | Micron Technology, Inc. - Stock (NASDAQ) | Micron Technology, Inc. - Common Stock |
| MSFT | Microsoft Corporation CEDEAR (BYMA) | Microsoft Corporation - Stock (NASDAQ) | Microsoft Corporation - Common Stock |
| AMD | Advanced Micro Devices, Inc. CEDEAR (BYMA) | Advanced Micro Devices - Stock (NASDAQ) | Advanced Micro Devices, Inc. - Common Stock |
| MELI | MercadoLibre, Inc. CEDEAR (BYMA) | MercadoLibre Inc. - Stock (NASDAQ) | MercadoLibre, Inc. - Common Stock |
| NU | Nu Holdings Ltd. CEDEAR (BYMA) | Nu Holdings Ltd. - Stock (NYSE) | Nu Holdings Ltd. Class A Ordinary Shares |
| QQQ | Invesco QQQ Trust Series 1 CEDEAR (BYMA) | Invesco QQQ Trust - ETF (NASDAQ) | Invesco QQQ Trust, Series 1 |
| AMZN | Amazon.com, Inc. CEDEAR (BYMA) | Amazon.com Inc. - Stock (NASDAQ) | Amazon.com, Inc. - Common Stock |

**All seven, not five** — corrected here from the first pass, which missed MELI and AMZN
because their orphan-to-be labels ("MercadoLibre Inc.", "Amazon.com Inc.") omit a comma
present in the referrer/proposed-target labels ("MercadoLibre, Inc.", "Amazon.com, Inc."), the
identical punctuation-sensitivity failure mode already documented for BIDU. **This is now
demonstrated across 3 of 3 checked instances (BIDU, MELI, AMZN) where it applies** — a
consistent, reproducible property of the label-normalization signal's floor, not an isolated
case.

**The dependency, stated precisely**: D's repoint does not merely need to sequence before an
unrelated Class-E cleanup — it **directly creates** seven new members of Class E's candidate
population (in addition to the two, BABA/BIDU, already identified from Class C). Any Class-E
scoping exercise conducted before D executes would miss all seven; any conducted using the
label-normalization signal alone, even after D executes, would still miss at least 2 of the 7
(MELI, AMZN) on the current punctuation pattern.

---

## 3. Whether D can be executed without resolving the 338 discrepancies

**Yes, on the technical evidence gathered.** D's verification signal (F-033 statistic, 15/21
pairs at exactly `1.000000000000`) is computed from deep-history data via the referrer and
the *proposed* target — a data slice structurally separate from the 338 discrepancies, which
exist only in the post-2026-05-28 window comparing *current* target to proposed target. Making
D's metadata change and verifying it does not require the 338 to be adjudicated first. This
was established as a technical determination in `REMEDIATION_ANALYSIS_UPDATE_DFA_RULING_
2026-08-20.md` and is restated, not re-derived, here.

**This is a statement about verifiability, not about advisability** — see gates below.

---

## 4. Remaining gates, separated by category

### Domain gates (require DFA/SE judgment, not resolvable from data alone)
- Whether the 338 post-transition discrepancies should be resolved, tracked, or left open
  *before* D executes, even though D's own verification does not technically require it —
  a risk-tolerance question, not a technical one.
- Whether the seven newly-identified orphan series (§1–2) should be archived, merged, relabeled,
  or left active-but-unreferenced — a disposition decision, not yet made for any of the nine
  total orphan/duplicate candidates now identified across this project's work (2 from BABA/
  BIDU, 7 from D).
- Whether creating seven new Class-E candidates as a direct consequence of D is an acceptable
  cost of proceeding with D now, or a reason to sequence D differently relative to a broader
  Class-E scoping effort.

### Product gates (operational/process decisions)
- No disposition plan exists yet for what happens to the seven orphan series' *data*
  specifically (not just their catalog status) — e.g., whether their post-transition 408 rows
  each have any ongoing value once unreferenced, or whether their pre-transition 2,866-ish
  rows (the duplicate-of-CEDEAR regime) should be handled differently now that they're no
  longer reachable via the referrer's FK.
- No confirmed schedule for when/whether the label-normalization signal itself gets corrected
  for the punctuation-sensitivity issue now demonstrated three times — a process question about
  detector maintenance, not about this specific repoint.

### Technical gates (verifiable/executable preconditions)
- SE/DFA execution authorization — standing, not yet granted.
- Contemporaneous re-confirmation of the pre-repair F-033 statistic at execution time (not
  merely cited from the prior day's reconciliation).
- Confirmation Class E work has not begun concurrently (the `ON DELETE RESTRICT` ordering
  constraint).
- A fresh, complete per-series export of the seven current-target series (all columns), for
  rollback purposes, consistent with the Class D package's existing requirement — unaffected
  by this update but restated as still required.

---

## 5. Proposed execution sequence (no mutation SQL)

**Sequence only — inclusion here does not constitute authorization for any step.**

1. **Confirm domain gates resolved or explicitly deferred** (§4, Domain) — in particular, a
   disposition decision (even "no action") for the seven orphan-to-be series, so D's execution
   does not silently create nine total unaddressed shadow-series candidates project-wide.
2. **Capture a fresh, complete pre-execution export** of the seven referrer series' current
   `underlying_series_id` values and the seven current-target series' full observation history
   (all columns) — the rollback basis, per the existing D package.
3. **Re-confirm the pre-repair F-033 statistic** immediately before execution, against
   live data at that time, not the 2026-08-19 reconciliation's cached value.
4. **Execute the seven-value metadata repoint** (not specified as SQL here; the exact mapping
   is fully documented in `REMEDIATION_PACKAGE_CLASS_D_2026-08-20.md` §"Proposed mutation").
5. **Immediately re-run the F-033 statistic** and the structural sweep (no series'
   `underlying_series_id` points at a target created after itself) — both must pass before D
   is considered complete.
6. **Re-run the Class-E label-normalization and identifier-based signals** against the
   post-repoint catalog state, explicitly including the seven newly-orphaned series — not
   deferred to "whenever Class E is eventually scoped," since these seven are now confirmed,
   not merely hypothetical, candidates the moment D executes.
7. **Route the resulting Class-E candidate count (now at least 9: 2 from BABA/BIDU + 7 from
   D) back to SE/DFA** as a distinct follow-on item, separate from D's own closure.

Steps 1–3 are pre-execution; step 4 is the only mutation in the sequence; steps 5–7 are
post-execution verification and follow-on routing. No step in this sequence is executed by
producing this document.

---

## What this package does not do

- Does not execute or stage step 4, or any other step.
- Does not authorize D's execution — it organizes what would need to happen, in order, if
  authorization is granted separately.
- Does not resolve the 338 discrepancies or propose how to resolve them.
- Does not make a disposition decision for any orphan or duplicate-candidate series.
- Does not reopen the seven Class-C rows.
