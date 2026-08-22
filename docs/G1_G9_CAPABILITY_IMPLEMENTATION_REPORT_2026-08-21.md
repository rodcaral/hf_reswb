# G1/G9 Evidence-Gated Identity Capability — Implementation Report

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SDT Workbench / SDT HistFinTS
**Status: read-only, non-production capability. No production data or schema modified. No
completed remediation reopened.**

---

## What was already in place before this instruction

This instruction's requirements overlap almost entirely with work already implemented and
independently validated (`G1_G9_EVALUATOR_DESIGN_2026-08-21.md`,
`G1_G9_INDEPENDENT_VALIDATION_2026-08-21.md`, PASS on all nine checked items). Rather than
duplicate that work, this report identifies what was already satisfied, and implements the one
genuinely new requirement: an **inspectable evidence matrix** in the output itself, not only
in the caller's own input.

| Requirement | Status before this instruction |
|---|---|
| Three financial conclusions preserved separately from technical `IdentityVerdict` | Already implemented and validated |
| Evidence gates and mandatory `UNRESOLVED` conditions | Already implemented and validated |
| `automatic_resolution_enabled=False` by default, no production caller | Already implemented and validated |
| No connection to remediation/mutation/reassignment/merge/delete/provider-assignment change | Already implemented and validated (no DB access in the module at all) |
| Tests for missing, stale, contradictory, cross-provider, technical-signal-only, sufficient-authoritative-evidence | Already implemented (20 tests) and validated |
| **Inspectable evidence matrix with source authority and temporal validity** | **Not previously in the output structure — implemented now.** |

---

## Implementation location

`src/hf_reswb/application/evidence_gated_identity_evaluator.py` (existing module, extended,
not a new module):

- **`DimensionEvaluation`** (new frozen dataclass) — one row of the evidence matrix:
  `dimension`, `tier` (source authority — `None` if no evidence was supplied), `status`,
  `source_description`, `effective_from`/`effective_to` (temporal validity),
  `is_stale_as_of_evaluation` (computed against the call's `as_of`), `is_mandatory` (whether
  this dimension is required for automatic `SAME_INSTRUMENT` eligibility per G1/G9 §5).
- **`_build_evidence_matrix()`** (new private helper) — always builds all seven rows, one per
  `IdentityDimension`, regardless of what the caller supplied; a dimension absent from the
  caller's input appears as its own row (`UNKNOWN`, `tier=None`, `"no evidence supplied"`),
  never omitted.
- **`EvidenceGatedAssessment.evidence_matrix`** (new field, `tuple[DimensionEvaluation, ...]`)
  — attached to **every** return path in `evaluate_financial_identity()`, including the
  disabled-by-default path and every `UNRESOLVED` early-return, not only the two positive
  conclusions. This was a deliberate design choice: a human reviewing why a pair came back
  `UNRESOLVED` can now see the full seven-dimension state directly on the result, rather than
  needing to re-derive it from the `reason` string or re-inspect their own input.

No other function signature changed. `evaluate_financial_identity()`'s existing parameters,
gating logic, and predicate structure (already validated PASS) are untouched.

---

## Tests

`tests/test_evidence_gated_identity_evaluator.py` — 5 new tests in `TestEvidenceMatrix`, 25
total in the file:

- Matrix always has exactly seven rows, covering all `IdentityDimension` members, regardless of
  how few dimensions the caller supplied.
- A dimension missing from the caller's input appears as its own `UNKNOWN`/`tier=None` row,
  never silently omitted.
- The matrix is populated even when `automatic_resolution_enabled=False` (the default) — the
  disabled-gate early return still returns useful, inspectable evidence.
- `is_mandatory` correctly distinguishes `PROVIDER_IDENTIFIER` (not mandatory, per §5's
  corroborate-not-substitute clause) from `ISSUER_SECURITY_IDENTITY` (mandatory).
- `is_stale_as_of_evaluation` correctly flags a lapsed (`effective_to` before `as_of`) dimension
  on its own row.

**Full suite: 114 passed, 1 skipped, 1 pre-existing unrelated failure** (series 11312's live
`configured_interval` — restated, unrelated to this work), zero regression from the prior
109-test baseline.

---

## Evidence limitations, restated (unchanged by this instruction)

Exactly as found in `G1_G9_EVALUATOR_DESIGN_2026-08-21.md` §3, re-confirmed unchanged: no
candidate examined this session has Tier 1 evidence for any of the seven dimensions in
HistFinTS today, and Tier 2 evidence is either absent or explicitly marked `UNVERIFIED` where
it exists (`provider_symbol.verification_status`). The `identifier` table's only populated type
(`FIGI`) carries `provenance='BRIDGED'` and has zero rows for any candidate series checked. The
`provider_event` table (the natural home for corporate-action/effective-date history, dimension
7) has zero rows. **This capability's evidence matrix would, run against any real candidate
today, show all seven rows as `UNKNOWN` or `tier=TIER_3_PROVIDER_OPERATIONAL`/lower** — which is
exactly why the matrix is valuable as a *diagnostic* tool even while automatic resolution stays
disabled: it makes the specific evidence gap visible per-dimension, rather than only as an
aggregate "insufficient evidence" statement.

---

## Domain decision required if the approved rule cannot be implemented faithfully

**None identified.** The rule as written in `G1_G9_Final_Domain_Ruling.md` was implementable
without any ambiguity requiring a domain decision — every predicate in §5–§7 mapped onto a
concrete, testable condition. The one interpretive choice made (documented already in
`G1_G9_EVALUATOR_DESIGN_2026-08-21.md` §1: modeling `RelationshipEvidence` as a structure
separate from the seven dimensions, since §6 frames "a meaningful relationship" as its own
predicate rather than one of the seven) was a structural implementation choice, not a
deviation from the rule's substance, and was already surfaced in the design document
independently validated PASS.

---

## Confirmation: no production change, no remediation reopened

- No database import exists in the module (confirmed by reading the full file).
- Grep of `src/` confirms zero production callers of `evaluate_financial_identity` and zero
  occurrences of `automatic_resolution_enabled=True` outside the module's own definition and
  the test file.
- Re-verified live (read-only) at the time of this report: 11345/11346 remain `SUPERSEDED`,
  10165/11340 remain `ACTIVE` — identical to `G1_G9_INDEPENDENT_VALIDATION_2026-08-21.md`, no
  completed remediation was touched or reopened by this work. The total `observation` count has
  moved (27,972,837 → 27,974,322, +1,485) since that validation — consistent with ordinary
  scheduled import activity in the intervening time, not with anything this code change could
  cause (the module has no database access, confirmed above), and reported here rather than
  omitted or misstated as unchanged.
