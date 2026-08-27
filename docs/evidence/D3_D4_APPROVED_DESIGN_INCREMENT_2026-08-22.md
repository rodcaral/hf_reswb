# D3/D4 Approved Design Increment — Population Semantics, Exclusion Mechanism, Evidence-Gated Fallback Activation

**Date:** 2026-08-22
**From:** SDT Workbench
**To:** SR
**Status: read-only technical design only. No schema, provider assignment, Series,
observation, migration, or production-policy change. Automatic fallback, provider
reassignment, scheduling changes, and remediation remain disabled — no caller anywhere in this
codebase invokes `evaluate_fallback_activation()` with `fallback_activation_enabled=True`
(grep-confirmed), and `filter_for_acquisition_quality_metrics()` touches no database or schema.**

Extends `src/hf_reswb/application/acquisition_quality_capability.py`
(`ACQUISITION_QUALITY_CAPABILITY_DESIGN_D1_D5_2026-08-22.md`) per SR's conditional approval:
D3 may design formal population semantics and the exclusion mechanism; D4 may design the
evidence-gated fallback capability. Neither is activated.

---

## D3 — Formal population semantics and exclusion mechanism

**Design principle, stated once and enforced structurally throughout**: a heuristic match
alone never excludes a Series from reported metrics. Exclusion requires an explicit,
attributed human confirmation. This is the direct technical answer to D3's "exclude *explicit*
test/non-production fixtures" wording.

**Types added**:
- `NonProductionFixtureStatus` (`NOT_A_FIXTURE` / `CANDIDATE_UNCONFIRMED` / `CONFIRMED_FIXTURE`)
  — three states, not two, specifically so a heuristic match has somewhere to live short of
  exclusion.
- `FixtureConfirmation` (`confirmed_by`, `confirmed_at`, `reason`) — an auditable record, the
  same standard applied to every other disposition this session (e.g. the 11345/11346
  disposition's retained history).
- `determine_fixture_status(candidate_flag, confirmation)` — `confirmation` is what actually
  authorizes `CONFIRMED_FIXTURE`; the flag alone can only ever reach `CANDIDATE_UNCONFIRMED`.
- `AcquisitionQualityPopulationMembership` (`INCLUDED_ACQUISITION_CANDIDATE` /
  `INCLUDED_PENDING_FIXTURE_REVIEW` / `EXCLUDED_CONFIRMED_FIXTURE`) — the formal population
  semantics: only `EXCLUDED_CONFIRMED_FIXTURE` may be omitted from acquisition-quality counts;
  `INCLUDED_PENDING_FIXTURE_REVIEW` stays counted but distinguishable, so a candidate is never
  silently folded into either "real gap" or "excluded."
- `filter_for_acquisition_quality_metrics(rows: list[PopulationRow]) -> PopulationFilterResult`
  — the exclusion mechanism itself: a pure, in-memory partition into `included`/
  `pending_review`/`excluded` series-id tuples. No schema or query-layer change is required to
  use it — a future reporting view would build `PopulationRow`s from its own already-fetched
  data.

**Not reinterpreting Class-C**: a dedicated test builds the real inventory shape (11344/11347
alongside real test-fixture ids) and confirms 11344/11347 land in `included`, unchanged from
`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`.

**Evidence required**: the existing `looks_like_non_production_fixture()` candidate flag, plus
(only when exclusion is actually intended) a human-supplied `FixtureConfirmation`.

**Tests** (`TestD3PopulationSemanticsAndExclusion`, 7 tests): unconfirmed-stays-unconfirmed even
with a candidate flag; confirmation present yields `CONFIRMED_FIXTURE`; no flag/no confirmation
is `NOT_A_FIXTURE`; unconfirmed candidates stay `INCLUDED_PENDING_FIXTURE_REVIEW` (the core D3
guarantee); confirmed fixtures are the only excludable status; a full-shape partition test
using the real 2026-08-22 inventory's series ids; confirmation the filter function has no
database parameter.

**Limitations/dependencies**: this design provides the classification and partition logic
only. Actually *using* `pending_review`/`excluded` in a real report still requires a product
decision on where confirmations are recorded and by whom — explicitly out of this read-only
task's scope, restated from the prior design doc, not newly discovered.

**Blocked?** No, for the mechanism itself — implementable and tested today. The storage/
recording location for a real `FixtureConfirmation` remains a product decision.

---

## D4 — Evidence-gated fallback capability

**Design principle**: activation requires two independent gates to both be open —
(1) `consider_fallback()`'s existing seven-dimension adequacy predicate, and (2) an explicit
`fallback_activation_enabled` flag defaulting to `False`, mirroring
`evidence_gated_identity_evaluator.evaluate_financial_identity()`'s
`automatic_resolution_enabled` gate exactly. Neither gate can compensate for the other being
closed.

**Extension to `FallbackCandidateEvidence`**: added a seventh dimension,
`comparability_acceptable`, per SR's 2026-08-22 message naming "financial identity, adjustment
basis, provenance, coverage/quality, and comparability" explicitly — comparability (can the
fallback's values be meaningfully compared against the primary's — consistent units, timing,
methodology) is tracked separately from raw `coverage_adequate` (does the fallback have data at
all), since the two questions are distinct. `is_fully_adequate()` and `unresolved_dimensions()`
were extended to include it; existing D4 tests were updated to supply it explicitly.

**New types**:
- `FallbackActivationVerdict` (`DISABLED_BY_DEFAULT` / `ELIGIBLE_PENDING_ACTIVATION` /
  `NOT_ELIGIBLE` / `ACTIVATED`) — four states so "the gate is closed" and "the gate is closed
  but nothing would happen anyway" are distinguishable, and so "the gate is open but the
  candidate still isn't adequate" is its own state rather than being conflated with either.
- `evaluate_fallback_activation(material_impact, candidate_evidence,
  fallback_activation_enabled=False)` — layers the activation gate on top of the existing
  `consider_fallback()` predicate without duplicating its logic.

**No caller anywhere in this codebase sets `fallback_activation_enabled=True`** — confirmed by
grep and by a structural test asserting the module never calls its own activation function
(the only occurrence of the function name in its own source is the `def` line).

**Tests** (`TestD4EvidenceGatedFallbackActivation`, 6 tests, plus 2 more added to the existing
`TestD4ConditionalFallback` for the new seventh dimension): disabled by default even with no
evidence; eligible-pending-activation when adequate but the gate is closed; activated only when
both the gate is open and the candidate is fully adequate; not-eligible when the gate is open
but the candidate is inadequate; the gate being open never activates when materiality itself is
unknown; a structural test confirming the module never invokes its own activation function.

**Limitations/dependencies**: restated from the prior design — most real-world evaluations
today would receive `None` on several of the seven dimensions (adjustment basis, provenance,
and now comparability are largely undocumented in HistFinTS), so `evaluate_fallback_activation()`
would in practice return `ELIGIBLE_PENDING_ACTIVATION` or `DISABLED_BY_DEFAULT` rarely and
`NOT_ELIGIBLE`/inadequate results commonly — an accurate reflection of the evidence gap, not a
defect.

**Blocked?** No, for the classifier and its activation gate — both implementable and tested
today. **Activation itself remains blocked** by SR's own explicit condition (financial
identity, adjustment basis, provenance, coverage/quality, and comparability evidence) and by
the same underlying data gaps already documented for G1/G9 and D4's first design pass — this is
restated, not new.

---

## Summary

| Item | New types | Tests | Blocked? |
|---|---|---|---|
| D3 | `NonProductionFixtureStatus`, `FixtureConfirmation`, `AcquisitionQualityPopulationMembership`, `PopulationRow`, `PopulationFilterResult` | 7 | No, for the mechanism. Storage/recording location is a separate product decision. |
| D4 | `FallbackActivationVerdict`, `FallbackActivationResult`, `comparability_acceptable` field | 6 (+2 updated) | No, for the classifier/gate. Actual activation blocked by SR's own stated evidence condition. |

**Implementation**: `src/hf_reswb/application/acquisition_quality_capability.py` (extended, not
a new file). **Tests**: `tests/test_acquisition_quality_capability.py` — 39 tests total in the
file (25 from the first pass + 14 new/updated for this increment), all passing. **Full suite**:
153 passed, 1 skipped, 1 pre-existing unrelated failure (series 11312), zero regression. No
database access anywhere in the module; zero production callers (grep-confirmed); no automatic
fallback, provider reassignment, scheduling change, or remediation implemented or triggered.
