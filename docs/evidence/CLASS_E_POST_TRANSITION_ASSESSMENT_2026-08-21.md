# Class-E Post-Transition Assessment — After the 11345/11346 Disposition ("SDT-1")

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: read-only assessment only. No remediation performed or proposed. No production
mutation, staging, or provenance change of any kind.**

---

## 1. Re-run against current production state, by population

### 1.1 The six previously-related series (BABA/BIDU cluster: 11345, 11346, 11316, 11317, 903, 1169)

| Series | Status | Provider assignments | Role |
|---|---|---|---|
| 11345 | `SUPERSEDED` | none | former BABA orphan, now emptied |
| 11346 | `SUPERSEDED` | none | former BIDU orphan, now emptied |
| 11316 | `ACTIVE` | Yahoo `BABA.BA`, MERVAL `BABA` | Alibaba CEDEAR |
| 11317 | `ACTIVE` | Yahoo `BIDU.BA`, MERVAL `BIDU` | Baidu CEDEAR |
| 903 | `ACTIVE` | Yahoo `BABA` | Alibaba ADR |
| 1169 | `ACTIVE` | Yahoo `BIDU` | Baidu ADR |

**Detector output on this set of six**: exactly two candidates, unchanged in kind and
evidence from every prior run this session —

- 11316 ↔ 903: `RELATED_BUT_DISTINCT` (Yahoo, `.BA`-suffix)
- 11317 ↔ 1169: `RELATED_BUT_DISTINCT` (Yahoo, `.BA`-suffix)

**11345 and 11346 produce zero candidates now, as they did before** — they carry zero
`provider_assignment` rows both before and after the disposition (the disposition never added
one, matching the containment requirement from the prior impact review), so the detector's
primary and secondary signals remain structurally inapplicable to them regardless of their
`status` value. **The detector does not read `status` at all** — `SUPERSEDED` changes nothing
about its output; this is confirmed by inspection of `class_e_identity_signal.py`, which has no
status-aware branch.

**On "SHADOW_SERIES" (per instruction §3)**: Workbench queried the live schema and found no
`SHADOW_SERIES` value, flag, or column anywhere in HistFinTS's tables (`series.status` has only
ever contained `ACTIVE` and, as of this disposition, `SUPERSEDED`; `match_candidate` and
`series_merge` — HistFinTS's own separate catalog-discovery/merge mechanism, distinct from this
project's detector — contain no `SHADOW_SERIES` value either). **No inference is drawn from
this absence**, per instruction — it is reported as a fact about what was and wasn't found, not
interpreted as evidence toward or against any identity conclusion. `SHADOW_SERIES` appears to
be a term from the original governing A–F framework documents (`histfints-v3/docs/`)
describing a class of duplicate, not a live, queryable database state — Workbench's detector
uses its own three-value taxonomy (`SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT`/`UNRESOLVED`) and
does not implement or reference `SHADOW_SERIES` as a concept.

### 1.2 Groups 1–4 remainder (11344 GLD-target, 11347 UBER-target)

- **11344**: zero candidates (unchanged — no provider assignment, no label match against its
  counterparts 2/4208, per the 2026-08-21 discovery run).
- **11347**: zero candidates involving 11347 itself (unchanged, same structural gap). The
  candidates that exist in this group involve only its *counterparts*, not 11347: 10165↔11340
  (`SAME_INSTRUMENT`), 10165↔11319 and 11340↔11319 (`RELATED_BUT_DISTINCT`) — identical to the
  2026-08-21 discovery run, no change.

### 1.3 10165 ↔ 11340 (re-checked directly, per instruction)

Unchanged: `SAME_INSTRUMENT`, Yahoo Finance symbol `UBER` on both. Not affected by the
BABA/BIDU disposition (different issuer, no shared series, no shared symbol).

### 1.4 The seven D-relationship series (post-D, active candidates)

Re-run against current data: **13 `SAME_INSTRUMENT` + 8 `RELATED_BUT_DISTINCT`, identical in
count and content to the 2026-08-21 post-D observation study.** All seven current-target series
still show zero incoming references. **No drift detected** — this population is stable since
D's execution; the BABA/BIDU disposition touched none of these 21 series.

### 1.5 D-contingent candidates

**None remain.** D has already executed (confirmed in the prior post-D study and re-confirmed
here); there is no D-contingent population left to report — Groups 5–11 are fully in the active
state described in §1.4, not a separate pending category.

### 1.6 Newly orphaned/superseded catalog records

- 11345, 11346: newly `SUPERSEDED` (this disposition), 0 observations, 0 provider assignments,
  0 incoming references — the only newly orphaned/superseded records produced since the last
  assessment.
- No other series changed status, observation count, or reference count as a side effect of
  this disposition (11316/11317's growth is additive to a disjoint date range, not a new
  orphaning — those two series remain fully active, referenced correctly by 903/1169).

---

## 2. Does the 3,025-row reattribution change the detectable Class-E landscape?

**Verified**: 1,513 (11345) + 1,512 (11346) = 3,025 rows — matches the instruction's stated
figure exactly, confirmed against the counts recorded before and after in this session's own
verification.

**Answer: leaves the detectable Class-E relationships unchanged.** The reattribution moved
`observation` rows and changed two `series.status` values — it did not touch any
`provider_assignment` row, and the detector's evidence surface is provider-assignment- and
label-based only. Before the reattribution, 11316↔903 and 11317↔1169 were already
`RELATED_BUT_DISTINCT`; after, they still are, with no new pair introduced and no existing pair
removed. **The reattribution creates no new detectable relationship, removes none, and leaves
the two pre-existing ones exactly as they were.**

---

## 3. Standing distinctions preserved

- **Technical detector output**: §1 above — evidence classifications only.
- **Financial-domain identity adjudication**: not performed here. The `RELATED_BUT_DISTINCT`
  classification for 11316↔903 and 11317↔1169 was already on record before this disposition (it
  reflects the already-DFA-acknowledged CEDEAR/ADR relationship, not a new finding) and is
  restated, not newly adjudicated.
- **Remediation authorization**: none granted, implied, or required by this assessment.

---

## 4. New candidates requiring DFA adjudication

**None.** No candidate pair appeared in this re-run that was not already on record from a prior
document this session (`CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`,
`CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md`,
`CLASS_E_POST_D_OBSERVATION_STUDY_2026-08-21.md`). The BABA/BIDU disposition's effect on the
Class-E evidence landscape is **null** — it removed two already-`UNRESOLVED`, evidence-free
catalog rows from the pool of things the detector could ever match against (11345/11346 could
never have produced a candidate given their permanent zero-assignment state, disposition or
not) and added no new evidence anywhere else.

---

## 5. Material detector limitations requiring a separate technical decision

**None identified as newly required by this transition.** The detector's already-known,
already-documented limitations stand unchanged and are not newly exposed or worsened by this
disposition:

- Its supporting-label layer still cannot bridge wording differences beyond punctuation
  (`CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md` §1.1) — irrelevant here since neither
  11345 nor 11346 ever depended on that layer to produce a candidate.
- It has no `status`-awareness — confirmed in §1.1 as a fact, not flagged as a defect: nothing
  in this session's scope has asked the detector to change behavior based on `ACTIVE` vs.
  `SUPERSEDED`, and doing so was never part of its evidence semantics (provider identity +
  symbol, with label as supporting-only).
- `DEFAULT_VENUE_SUFFIXES` still covers only `.BA` — unaffected by, and not tested further by,
  this transition.

**No separate technical decision is required as a result of the BABA/BIDU disposition
specifically.**

---

## Summary

| Question | Answer |
|---|---|
| Does the 11345/11346 disposition change the Class-E evidence landscape? | No — net zero. Two evidence-free, `UNRESOLVED` candidates were removed from future consideration by becoming `SUPERSEDED`/emptied; no new evidence was created anywhere. |
| Does the reattribution create/remove/leave unchanged detectable relationships? | Leaves unchanged. The two pre-existing `RELATED_BUT_DISTINCT` pairs (11316↔903, 11317↔1169) are identical before and after. |
| Any new candidates for DFA? | None. |
| Any detector limitation requiring a separate technical decision? | None identified. |
| D-contingent candidates remaining? | None — D has executed; Groups 5–11 are fully active (13 `SAME_INSTRUMENT` + 8 `RELATED_BUT_DISTINCT`, unchanged since the post-D study). |
| Newly orphaned/superseded records? | 11345, 11346 only. |

**No remediation performed, proposed, or required by this assessment.**
