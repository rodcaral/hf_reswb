# Evidence-Gated Financial-Identity Evaluator — Design (G1/G9 Implementation)

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: read-only design and test specification only. No production data or schema
modified. `evaluate_financial_identity()` performs no database access and is disabled by
default — see §4.**

Implements `docs/G1_G9_Final_Domain_Ruling.md` as
`src/hf_reswb/application/evidence_gated_identity_evaluator.py`, following the established
safeguard-infrastructure conventions (frozen dataclasses, `str, Enum` types with per-member
docstrings, pure functions, no DB access).

---

## 1. Type design and how it maps to the ruling

| Ruling concept | Implementation |
|---|---|
| §1 three financial states | `FinancialIdentityConclusion` (`SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT`/`UNRESOLVED`) — a **distinct type** from `class_e_identity_signal.IdentityVerdict`, deliberately, so the two can never be conflated at the type level, not just by convention. |
| §2 Tier 1-4 hierarchy | `EvidenceTier` enum, four members, each docstring quoting its ruling definition verbatim. |
| §4 seven identity dimensions | `IdentityDimension` enum, seven members exactly matching the ruling's list. |
| §4/§5 "established... or demonstrated irrelevant" | `DimensionStatus` enum: `ESTABLISHED_EQUIVALENT`, `ESTABLISHED_DIFFERENT`, `IRRELEVANT`, `UNKNOWN` — four states, not a boolean, so "irrelevant" and "unknown" are never conflated (§7's "`UNKNOWN` must not become `DIFFERENT`" is enforced by construction: nothing in the evaluator ever assigns `ESTABLISHED_DIFFERENT` — only a caller-supplied `DimensionAssessment` can, and the evaluator never infers it from absence). |
| A single dimension's evidence, tier, and temporal window | `DimensionAssessment` — carries `dimension`, `tier`, `status`, `source_description`, `effective_from`/`effective_to`, plus `is_stale(as_of)` and `has_unknown_effective_period()` helper methods. |
| §6's "documented relationship" requirement | `RelationshipEvidence` — a separate, smaller evidence object distinct from the seven dimensions, since the ruling frames "a meaningful relationship" as its own predicate, not one of the seven. |
| The evaluation itself | `evaluate_financial_identity()` — pure function, returns `EvidenceGatedAssessment` (conclusion + reason + whether resolution was actually enabled + any flagged contradictions). |

---

## 2. How each ruling section is represented

- **§3 precedence/temporal validity**: `DimensionAssessment.is_stale(as_of)` and
  `has_unknown_effective_period()`; both are checked for every supplied assessment before any
  conclusion is reached. A `contradictory_dimensions` parameter lets the caller flag dimensions
  where two authoritative sources conflict and cannot be resolved by effective date — any
  non-empty set forces `UNRESOLVED` immediately, with no "majority" or "latest wins" logic
  anywhere in the function.
- **§5 minimum evidence for `SAME_INSTRUMENT`**: `MANDATORY_DIMENSIONS` (six of the seven —
  `PROVIDER_IDENTIFIER` excluded, per §5's explicit "may corroborate but cannot substitute").
  All six must be `ESTABLISHED_EQUIVALENT` or `IRRELEVANT`, on Tier 1/2 evidence only — Tier 3/4
  evidence on any mandatory dimension fails the predicate.
- **§6 minimum evidence for `RELATED_BUT_DISTINCT`**: requires `relationship_evidence` to be
  `established` on Tier 1/2, **and** at least one dimension `ESTABLISHED_DIFFERENT` on Tier 1/2
  (the "material distinction," explicitly not satisfiable by Tier 3/4 — ruling: "Correlation,
  ticker differences, or labels alone cannot establish this state"), **and** no mandatory
  dimension left at `UNKNOWN` ("no unresolved evidence could reasonably reverse the
  conclusion").
- **§7 mandatory `UNRESOLVED` conditions**: implemented as an ordered sequence of early
  returns, each citing its ruling clause — missing/unknown issuer identity, Tier-3/4-only
  security-identity evidence, unresolved depositary context, unknown effective period, staleness,
  and (falling through to the final `return`) "insufficient authoritative evidence" as the
  catch-all for anything not explicitly covered above.
- **§8 detection/adjudication boundary**: satisfied structurally — the module has no database
  import, no write call, and returns a dataclass, never performs an action.
- **§11 disabled-by-default posture**: `automatic_resolution_enabled: bool = False` is the
  first check in the function body; when `False`, every other parameter is ignored and the
  function returns `UNRESOLVED` unconditionally, with the reason string stating exactly why.
  **No caller anywhere in this codebase passes `True`** — enabling it is left as a future,
  separate change.

---

## 3. Which required dimensions are currently unavailable in HistFinTS — verified by query

Read-only inspection of the live schema and data for this design, not assumed from memory:

| Dimension | Tier 1 available today? | Tier 2 available today? | What exists |
|---|---|---|---|
| Issuer/security identity | **No.** | **No, not authoritative.** | `identifier` table exists (1,256 rows) but its only `identifier_type` is `FIGI`, and every row's `provenance` is `BRIDGED` (i.e. derived/mapped, not sourced from an authoritative registry per the schema's own tag) — and **zero rows exist for any of the six candidate series checked this session** (10165, 11340, 903, 1169, 11316, 11317). No issuer field exists on `series` at all. |
| Instrument class/subtype | Partial. | Partial. | `series.instrument_subtype` exists but is `NULL` on most series examined (only explicitly populated as `ADR`/`CEDEAR` for a handful); `provider_symbol.security_type` exists (`CD`, `CS` observed) but `provider_symbol.verification_status` is `UNVERIFIED` on every row checked this session (e.g. the `BABA`/`BIDU`/`UBER` rows) — fails the Tier 2 bar of "sufficiently authoritative." |
| Listing/venue | No. | Partial, unverified. | `provider_symbol.venue` populated (e.g. `XBUE`) but same `UNVERIFIED` status issue as above. |
| Currency/denomination | No. | Partial. | `series.currency` exists and is populated for many series — the most-available dimension today, but still catalog-sourced (Tier 2/3 at best), not independently documented. |
| Provider identifier | N/A (Tier 3 by definition) | N/A | Fully available — this is exactly what `class_e_identity_signal.py` already uses; per §5 it can never substitute for the missing dimensions above regardless of availability. |
| Adjustment/conversion basis | No. | No. | Unrecorded at the series/observation level (D-005, D-021 — already-documented HistFinTS gap: Yahoo vs. Alpha Vantage basis differs, not tracked per-series). `provider.adjustment_basis` exists only as a provider-wide default, not a per-series/per-assignment authoritative fact; `provider_assignment.adjustment_basis_override` exists as a column but was `NULL` on every row checked this session. |
| Corporate-action/effective-date history | No. | No. | `provider_event` table exists in the schema (columns for `event_type`, `event_date`, `structured_data`) but **contains zero rows** — fully unpopulated, confirmed by query. |

**Consequence, stated exactly as the ruling's own §9 anticipates**: no candidate pair examined
this session (Groups 1-4, 10165↔11340, the seven post-D pairs, the BABA/BIDU cluster) has
Tier 1 evidence for any dimension, and Tier 2 evidence is either absent or explicitly marked
`UNVERIFIED` where it exists at all. **Every real-data evaluation this evaluator would perform
today, honestly assessed, would return `UNRESOLVED`** via the "security identity cannot be
independently established" branch (§7) before reaching any other check — not because the
evaluator is broken, but because the evidence prerequisites the ruling requires do not yet
exist in this database. This matches §9's own statement exactly and is not a new finding.

---

## 4. Automatic resolution: disabled by default, and why a technical candidate cannot enable it

`automatic_resolution_enabled` defaults to `False` and is checked before any other logic runs.
There is no code path — in this module or in `class_e_identity_signal.py` — by which the mere
existence of a technical `SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT` candidate flips this
parameter. The two modules are not wired together at all; a caller wishing to feed a technical
signal into this evaluator would have to explicitly map it into a `DimensionAssessment` at
`EvidenceTier.TIER_3_PROVIDER_OPERATIONAL`, which (per §5's exclusion of Tier 3 from every
mandatory dimension) can never by itself satisfy the `SAME_INSTRUMENT` predicate — confirmed by
`TestCrossProviderAndProviderSymbolOnly` and
`TestDisabledByDefault::test_technical_candidate_existence_alone_does_not_enable_resolution`.

---

## 5. Tests

`tests/test_evidence_gated_identity_evaluator.py` — 20 tests, all passing; full suite 109
passed / 1 skipped / 1 pre-existing unrelated failure (series 11312), zero regression:

- **Disabled by default** (3 tests): default gate returns `UNRESOLVED` even with complete
  evidence; a technical-candidate-only input never enables resolution.
- **Complete authoritative evidence** (1 test): a fabricated (explicitly labeled as such, not a
  claim about real HistFinTS data) complete Tier-1 evidence set yields `SAME_INSTRUMENT` when
  the gate is explicitly enabled.
- **Missing evidence** (4 tests): missing issuer dimension, missing any other mandatory
  dimension, explicit `UNKNOWN` status, and the `UNKNOWN`-never-becomes-`DIFFERENT` guarantee.
- **Contradictory evidence** (2 tests): flagged contradiction forces `UNRESOLVED`; a single
  contradiction is decisive regardless of how much other evidence is established (no
  majority-vote logic).
- **Stale evidence** (3 tests): evidence before its `effective_from`, evidence after its
  `effective_to`, and `ESTABLISHED_*` evidence with no stated effective period at all.
- **Cross-provider / provider-symbol-only** (2 tests): Tier-3 issuer evidence (even a perfect
  cross-provider symbol match) cannot establish identity; agreement between two providers does
  not upgrade the tier.
- **Depositary-layer** (3 tests): unresolved subtype in a plausible depositary context forces
  `UNRESOLVED`; a fully-documented depositary relationship with a material Tier-1 distinction
  yields `RELATED_BUT_DISTINCT`; relationship evidence alone without a material distinction does
  not.
- **Structural** (2 tests): `PROVIDER_IDENTIFIER` confirmed excluded from `MANDATORY_DIMENSIONS`;
  all seven dimensions confirmed defined.

One bug was caught and fixed by this test suite during development, in the spirit of this
project's other test-driven infrastructure work: the `_complete_authoritative_evidence()` test
fixture originally left `PROVIDER_IDENTIFIER`'s `effective_from` unset while marking it
`ESTABLISHED_EQUIVALENT`, which correctly tripped the "unknown effective period" check and
returned `UNRESOLVED` instead of the expected `SAME_INSTRUMENT` — the evaluator's logic was
correct (any `ESTABLISHED_*` assessment without a stated effective period is temporally
unverifiable, and the check applies to all supplied evidence, not only the mandatory
dimensions); the test fixture was the one that needed a fix, not the evaluator.

---

## 6. What this design does not do

- Does not modify production data or schema — confirmed by the module having no database
  import.
- Does not enable automatic resolution for any real pair — no caller in this codebase sets
  `automatic_resolution_enabled=True`.
- Does not wire this evaluator into `class_e_identity_signal.py`, `panel_eligibility_service.py`,
  or any calibration path.
- Does not resolve 10165↔11340 or any other pending Class-E candidate — its financial
  disposition remains `UNRESOLVED`, exactly as G1/G9 §9 states, since no Tier 1/2 evidence for
  it exists in HistFinTS today.
- Does not propose a schema change, evidence-collection mechanism, or timeline for populating
  the missing dimensions identified in §3 — that is a separate scope/authorization decision
  per the ruling's §11, not something this design proposes on its own.
