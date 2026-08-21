# Post-Class-D Class-E Observation Study

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: read-only observation study. No mutation performed. No candidate dispositioned. All
findings below are technical signal only — none is a financial-identity adjudication,
observation-history disposition, or remediation authorization.**

---

## 0. D-execution state, confirmed independently before this study proceeded

Before characterizing "post-D" signals, Workbench independently re-queried (read-only) whether
the live database actually reflects D's seven mutations, rather than assuming SE's "completed
D execution" premise.

**Confirmed**: all seven referrer rows now carry the proposed (correct) `underlying_series_id`,
not the previous (wrong) one:

| Referrer | `underlying_series_id` now | Matches gate package's proposed target |
|---|---|---|
| 11323 (MU) | 6672 | Yes |
| 11324 (MSFT) | 6602 | Yes |
| 11325 (AMD) | 426 | Yes |
| 11326 (MELI) | 6319 | Yes |
| 11327 (NU) | 7085 | Yes |
| 11328 (QQQ) | 8193 | Yes |
| 11329 (AMZN) | 484 | Yes |

**D has executed** — the FK state matches the authorized mapping exactly on all seven.

**One anomaly flagged, not resolved**: all seven referrer rows carry an identical
`updated_at` of `2026-08-18 16:15:46` — a timestamp that **predates** both SE's execution
authorization to SDT HistFinTS and this session's gate package (both 2026-08-21). Workbench has
no independent way to observe when or by whom the mutation was applied (that execution was
addressed to SDT HistFinTS, not to Workbench, and Workbench performed no write). **This is
reported as an open question for SE to resolve with SDT HistFinTS's own execution report** (the
ten-item return specified in SE's execution instruction, item 1: exact execution timestamp) —
it does not change the fact that the FK state matches the authorized mapping, but it means
Workbench cannot itself corroborate the timestamp SDT HistFinTS reports.

**Other invariants spot-checked, consistent with no scope creep**:
- Total `observation` count: **27,972,816** — unchanged from every previously recorded
  baseline.
- The seven current-target series' observation counts unchanged (3,282 each; 1,535 for
  NU/11351).
- The seven current-target series now have **zero** incoming references each (confirmed by
  query) — the expected orphaning consequence.
- Series 11345/11346 (BABA/BIDU): observation counts unchanged (1,513/1,512), still zero
  `provider_assignment` rows — untouched.
- Referrer `ratio` still `1.0` on all seven — no ratio change occurred (none was authorized).

---

## 1–2. Re-run of the identity signal — actual result, reported precisely

`detect_identity_candidates()` was re-run against the real, current production labels and
`provider_assignment` rows for all 21 affected series (7 referrers, 7 now-orphaned current
targets, 7 proposed targets).

**The result is not a clean 7 `SAME_INSTRUMENT` / 7 `RELATED_BUT_DISTINCT` split.** Reporting
the actual output rather than the expected shape, per this project's standing verify-before-
reporting discipline:

**`SAME_INSTRUMENT`: 13 candidates, not 7.**

| Pair | Series A | Series B | Evidence |
|---|---|---|---|
| MU | 11342 (orphaned current target) | 6672 (proposed target) | provider 2 (Yahoo Finance), symbol `MU` |
| MSFT | 11324 (referrer) | 11348 (orphaned current target) | provider 5 (Twelve Data), symbol `MSFT` |
| MSFT | 11348 (orphaned current target) | 6602 (proposed target) | provider 2 (Yahoo Finance), symbol `MSFT` |
| AMD | 11325 (referrer) | 11349 (orphaned current target) | provider 5 (Twelve Data), symbol `AMD` |
| AMD | 11349 (orphaned current target) | 426 (proposed target) | provider 2 (Yahoo Finance), symbol `AMD` |
| MELI | 11326 (referrer) | 11350 (orphaned current target) | provider 5 (Twelve Data), symbol `MELI` |
| MELI | 11350 (orphaned current target) | 6319 (proposed target) | provider 2 (Yahoo Finance), symbol `MELI` |
| NU | 11327 (referrer) | 11351 (orphaned current target) | provider 5 (Twelve Data), symbol `NU` |
| NU | 11351 (orphaned current target) | 7085 (proposed target) | provider 2 (Yahoo Finance), symbol `NU` |
| QQQ | 11328 (referrer) | 11352 (orphaned current target) | provider 5 (Twelve Data), symbol `QQQ` |
| QQQ | 11352 (orphaned current target) | 8193 (proposed target) | provider 2 (Yahoo Finance), symbol `QQQ` |
| AMZN | 11329 (referrer) | 11353 (orphaned current target) | provider 5 (Twelve Data), symbol `AMZN` |
| AMZN | 11353 (orphaned current target) | 484 (proposed target) | provider 2 (Yahoo Finance), symbol `AMZN` |

**`RELATED_BUT_DISTINCT`: 8 candidates, not 7.**

| Pair | Series A | Series B | Evidence |
|---|---|---|---|
| MU | 11323 (referrer) | 11342 (orphaned current target) | provider 2: `MU.BA` vs. `MU` |
| MU | 11323 (referrer) | 6672 (proposed target) | provider 2: `MU.BA` vs. `MU` |
| MSFT | 11324 (referrer) | 6602 (proposed target) | provider 2: `MSFT.BA` vs. `MSFT` |
| AMD | 11325 (referrer) | 426 (proposed target) | provider 2: `AMD.BA` vs. `AMD` |
| MELI | 11326 (referrer) | 6319 (proposed target) | provider 2: `MELI.BA` vs. `MELI` |
| NU | 11327 (referrer) | 7085 (proposed target) | provider 2: `NU.BA` vs. `NU` |
| QQQ | 11328 (referrer) | 8193 (proposed target) | provider 2: `QQQ.BA` vs. `QQQ` |
| AMZN | 11329 (referrer) | 484 (proposed target) | provider 2: `AMZN.BA` vs. `AMZN` |

**Root cause of the deviation from the expected 7/7 split, verified by direct query, not
assumed**: six of the seven referrer CEDEARs (all except MU) carry a **second, independent
provider assignment on provider 5 ("Twelve Data")** whose symbol is identical (no suffix) to
the plain symbol their own now-orphaned current target also has on provider 5. Example:
referrer 11324 (MSFT CEDEAR) has `(provider 5, "MSFT")`; orphaned current target 11348 also has
`(provider 5, "MSFT")` — an exact match under the detector's primary signal, independent of the
already-known Yahoo Finance (`provider 2`) `.BA`-suffix relationship. **MU's referrer (11323)
has no provider-5 assignment at all** (its fourth assignment is `provider 6` "MERVAL", not
"Twelve Data", and does not match anything on 11342) — so MU alone follows the originally
predicted 1 `SAME_INSTRUMENT` + 2 `RELATED_BUT_DISTINCT` pattern; the other six each produce 2
`SAME_INSTRUMENT` + 1 `RELATED_BUT_DISTINCT`.

**This is new evidence, not previously documented in any prior Class-E deliverable this
session** (the gate package's Class-E containment section, §5, predicted the clean 7+7 split
based on the previously-examined provider-2 evidence only; it did not examine provider-5
assignments on the referrer rows, since those were out of scope for the D mutation itself).
**Reported as a technical finding, not a financial-domain conclusion**: the detector does not
determine whether the Twelve Data assignment reflects a genuine additional identity signal or
a data-entry/catalog artifact — that determination, if wanted, is DFA's, not Workbench's.

---

## 3. Confirmation: post-D active candidates, not D-contingent

All 21 candidates listed in §1–2 involve at least one of the seven now-orphaned current-target
series (11342/11348/11349/11350/11351/11352/11353), each of which has zero incoming references
as of this study (§0). **These are now post-D active candidates** — the D-contingency condition
(`CLASS_E_IDENTITY_EVIDENCE_POPULATION_STUDY_2026-08-20.md`'s "not live candidates unless/until
D executes") has been satisfied by D's confirmed execution. Groups 5–11 are therefore no
longer described as inactive/contingent as of this study — they are active Class-E candidates,
in the same unresolved/candidate terminal state DFA has already ruled sufficient (2026-08-21
gate ruling).

---

## 4. Standing distinctions preserved

- **Technical identity signal** (this document, §1–2): a classification of provider-catalog
  evidence, produced by `class_e_identity_signal.py`. Not a financial determination.
- **Financial identity adjudication**: remains DFA's role. This document adjudicates nothing —
  it reports what the detector found and flags the new Twelve Data evidence for DFA's
  awareness, without characterizing its financial meaning.
- **Observation-history disposition**: untouched. No proposal, in this document, for what
  happens to the seven now-orphaned series' observation history (2,866+416-style dual-regime
  data per series, per the earlier Matrix 2 study). Remains an open, named-but-unresolved
  disposition element.
- **Remediation authorization**: none granted or implied by this document. No deletion, merge,
  reassignment, or provenance change proposed or performed.

---

## 5. Not combined with Groups 1–4 or 10165↔11340

The 21 candidates in §1–2 are reported as their own, distinct population — **not merged, added
to a shared count, or treated as evidence toward** Groups 1–4's (11344/11345/11346/11347)
unresolved status or the previously-surfaced 10165↔11340 `SAME_INSTRUMENT` pair
(`CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md` §1.3). Each population retains its own,
separately-evidenced state; no shared financial disposition is implied by their co-occurrence
in this project's Class-E work.

---

## 6. Population count — reported as observed, not retroactively redefining the lower bound

**Currently observed, as of this study**: 21 new candidate pairs (13 `SAME_INSTRUMENT` + 8
`RELATED_BUT_DISTINCT`) among the 21 series directly affected by D's seven mutations, plus the
previously-reported Groups 1–4 (4 unresolved candidates) and the 10165↔11340 pair (1
`SAME_INSTRUMENT` candidate) — **35 total candidate-pairs currently on record across all
Class-E work this session**, none of them a claim of completeness.

**The ≥11 figure is not retroactively reinterpreted.** That figure was, and remains, a
provisional lower bound reached under a different counting convention (distinct *series*
identified as candidates, not candidate *pairs*) at a specific point in time
(`CLASS_E_IDENTITY_EVIDENCE_POPULATION_STUDY_2026-08-20.md`). This study's 21-pair,
pair-counted result is additive new evidence from a later point in time (post-D), reported on
its own terms — it is not substituted for, does not correct, and does not extend the earlier
figure's stated scope. **Completeness of the Class-E population remains unestablished after
this study, exactly as before it.**

---

## 7. Confirmation: no detector output invokes or implies automatic remediation

Re-confirmed by code inspection (unchanged since `CLASS_E_IDENTITY_SIGNAL_2026-08-21.md`):
`class_e_identity_signal.py` exposes no database write access, and no code path in this
codebase (grep-confirmed, no matches in `panel_eligibility_service.py`, `panel_integration.py`,
`calibration_analyzer.py`, `calibration_utilities.py`, or any application-layer module) consumes
an `IdentityVerdict` value to trigger a mutation. Every candidate in §1–2, §5's referenced
populations, and any future run remains in a report-only, preserve-and-do-nothing state until a
human (DFA/SE/PO) acts on it.

---

## 8. New evidence for DFA's financial-identity adjudication

**Yes — one item.** The Twelve Data (`provider 5`) exact-symbol match between six of the seven
referrer CEDEARs and their own now-orphaned current-target series (§1–2) was not previously
surfaced in any prior Class-E document. It is an independent identity signal (a different data
provider than the Yahoo Finance evidence already before DFA), present on 6 of 7 pairs and
absent on MU specifically. **Workbench reports this as new evidence only** — no interpretation
of its financial significance (whether it strengthens, is redundant with, or is irrelevant to
the already-established same-financial-instrument ruling for these seven pairs) is offered
here; that judgment, if DFA wants to make one, is DFA's.

No other new evidence requiring DFA adjudication was found in this study — Groups 1–4's
evidence gap, the 10165↔11340 pair's status, and the ADR/depositary-layer question all remain
exactly as previously reported, unchanged by D's execution.

---

## Evidence note (summary format, as requested)

| Observed | Technical Finding | Financial status | Required next decision |
|---|---|---|---|
| Seven referrer FK values now match the D-authorized mapping | D executed as scoped; FK state consistent with the gate package; execution timestamp not independently corroborable by Workbench | Not a Workbench determination — the seven pairs' same-instrument status was already established by DFA prior to execution | None from Workbench; SE to reconcile execution timestamp with SDT HistFinTS's own report |
| Seven current-target series now have zero incoming references | Confirms the predicted orphaning consequence exactly | N/A (structural fact, not identity) | None — matches gate package §4/§5 prediction |
| Re-running the identity signal on the 21 affected series yields 13 `SAME_INSTRUMENT` + 8 `RELATED_BUT_DISTINCT`, not the predicted 7+7 | Six of seven referrer/current-target pairs carry an additional, independent Twelve Data (provider 5) exact-symbol match, not previously examined | Unresolved — a technical signal only; no financial meaning assigned | DFA awareness recommended; no action required unless DFA wants to interpret this new evidence |
| 11345/11346 obs counts, provider_assignment counts, ratios all unchanged | No scope creep; the seven-row mutation did not reach these series | Untouched — same open ADR/depositary-layer question as before | None from this study |
| Total observation count, seven Class-C rows' series, and the 338/406 population untouched (by construction — mutation scope cannot reach `observation` rows) | Confirmed no observation-level change occurred | Both remain exactly as previously adjudicated/unresolved | None from this study |
| No code path consumes `IdentityVerdict` for mutation | Confirmed unchanged | N/A | None |

**No mutation proposed. No candidate dispositioned. No remediation authorized or implied.**
