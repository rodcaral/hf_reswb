# Acquisition-Quality Capability Design — D1–D5

**Date:** 2026-08-22
**From:** SDT Workbench
**To:** SE
**Status: read-only design only. No schedule, provider assignment, Series, observation,
schema, migration, production policy, or remediation state modified. No automatic fallback or
other acquisition change implemented — `src/hf_reswb/application/acquisition_quality_
capability.py` performs no database access and has zero production callers, confirmed by
grep.**

Builds directly on `ACQUISITION_QUALITY_INVENTORY_2026-08-22.md`'s findings and follow-up
items. Each of D1–D4 is implemented as a pure evidence classifier, following the conventions of
`class_e_identity_signal.py` and `evidence_gated_identity_evaluator.py`. D5 is implemented as a
diagnostic-only qualifier, per instruction, with no defect-classification semantics.

---

## D1 — Currentness/cadence capability

**Current mechanism**: `histfints-v3`'s `classify_import_state()` compares a Series' *most
recent* run against `staleness_tolerance(configured_interval)` — a point-in-time check ("is it
stale right now"), not an assessment of whether the acquisition process's own historical rhythm
could ever satisfy the tolerance even when nothing is broken.

**Proposed technical representation**: `CadenceCapabilityVerdict` (`SUFFICIENT_MARGIN` /
`INSUFFICIENT_MARGIN` / `INSUFFICIENT_EVIDENCE`) and `CadenceCapabilityAssessment`
(`tolerance`, `observed_gap_count`, `max_observed_gap`, `margin`). `assess_cadence_capability()`
takes the Series' tolerance and its successful-run timestamps, computes the gaps between
consecutive successes, and classifies whether the *worst* observed gap fits inside tolerance.
**No margin threshold is asserted as sufficient or insufficient by this module** — `margin`
(`tolerance - max_observed_gap`) is reported as evidence; SUFFICIENT/INSUFFICIENT only reflects
whether that margin is positive or negative, not a policy judgment about how much margin should
be required. This directly satisfies the instruction not to assume a margin DFA has not
approved.

**Evidence required**: the Series' `staleness_tolerance` value (already computed elsewhere,
not recomputed here) and a list of successful runs' `started_at` timestamps.

**Test cases** (`TestD1CadenceCapability`, 4 tests): sufficient margin when all gaps fit;
insufficient margin when a gap exceeds tolerance (modeled on the real 32-Series 1h-cohort
pattern — §2 of the acquisition-quality inventory); insufficient evidence below the sample
floor; confirmation that no verdict encodes a specific "adequate margin" policy.

**Limitations/dependencies**: cannot distinguish "the process is structurally incapable of this
cadence" from "the process is capable but has been paused/broken since a specific date" (the
real 32-Series case is the latter, per the inventory's own finding) — `INSUFFICIENT_MARGIN`
covers both without discriminating; a caller wanting that distinction would need to additionally
check whether the gap pattern is a single outlier (likely an outage) versus a recurring
characteristic (likely a structural cadence problem). This was left out deliberately rather than
guessed at, since DFA has not specified how that distinction should be drawn.

**Blocked by missing data or product decisions?** **Not blocked for the capability itself** —
implementable and tested today against historical run data already in HistFinTS. **Blocked for
any policy use of the output** (e.g. "flag INSUFFICIENT_MARGIN Series for remediation") pending
DFA's own margin-sufficiency threshold, which this module deliberately does not assume.

---

## D2 — Identifier/provider acquisition-compatibility validation

**Current mechanism**: none exists today beyond the raw `ImportRun.status`/`ImportErrorRecord`
per attempt — there is no aggregated view of "has this identifier ever worked at this
provider."

**Proposed technical representation**: `IdentifierCompatibilityVerdict` (`RESOLVED` /
`CONSISTENTLY_UNRESOLVED` / `INSUFFICIENT_EVIDENCE`) and `assess_identifier_compatibility()`,
which takes only a list of `RunOutcome` values (`SUCCESS`/`FAILED`) for one (provider,
identifier) pair — **no identifier string is inspected anywhere in the function** (confirmed by
a test asserting the parameter doesn't exist), satisfying D2's explicit prohibition on a
universal `.`/`$` syntax rule. Compatibility is purely outcome-history-based: a pair that has
ever succeeded is `RESOLVED`; a pair with only failures is `CONSISTENTLY_UNRESOLVED` (not
diagnosed further — D5 supplies an optional, separate diagnostic label on the *failure shape*
for whoever wants it, kept structurally apart from this verdict).

**Preserving the identity/adjudication boundary**: this verdict says only "does this string
resolve at this provider's endpoint" — it carries no claim about financial identity. It is
architecturally separate from both `class_e_identity_signal.IdentityVerdict` (technical
candidate signal from catalog data) and `evidence_gated_identity_evaluator.
FinancialIdentityConclusion` (DFA's G1/G9 model) — none of the three modules imports or
references another's verdict type.

**Evidence required**: a per-(provider, identifier) history of run outcomes.

**Test cases** (`TestD2IdentifierCompatibility`, 4 tests): resolved with at least one success
(modeled on the real SLV/UBER/URA Twelve Data history — two successes before rate-limiting);
consistently unresolved (modeled on the `.A`/`.B`/`$`-series 404 pattern); insufficient
evidence with zero attempts; confirmation the function signature contains no identifier
parameter to inspect.

**Limitations/dependencies**: says nothing about *why* a pair is `CONSISTENTLY_UNRESOLVED` —
by design (D2 forbids the syntax rule that would explain the dominant real-world cause). A
human or a separate, explicitly-authorized future capability would still need to diagnose format
mismatches; this module deliberately stops at "does it resolve," not "why doesn't it."

**Blocked by missing data or product decisions?** **Not blocked.** Implementable today against
existing `import_run`/`import_error` history.

---

## D3 — NEVER-state evidence model

**Current mechanism**: `classify_import_state()` collapses "no provider assignment" and
"assigned but never run" into one `ImportState.NEVER` value — the exact ambiguity the
acquisition-quality inventory's §1 reconciliation had to manually untangle.

**Proposed technical representation**: `NeverStateReason` (`NO_PROVIDER_ASSIGNMENT` /
`ASSIGNED_NOT_YET_RUN` / `NON_PRODUCTION_FIXTURE_CANDIDATE`) and `classify_never_state()`,
which takes `has_provider_assignment: bool` and a caller-supplied `fixture_candidate: bool` —
the function itself does not compute the fixture flag, keeping the (separately testable)
heuristic and the state classification apart. `looks_like_non_production_fixture(label,
provider_identifier)` is the heuristic — a narrow, explicit, inspectable keyword list matching
exactly the real test-fixture labels found in the inventory ("Smoke Test", "Duplicate Warning
Test", "Test Series", "bulk-verify", "-test"), **explicitly documented as a candidate flag, not
a determination**: exclusion from acquisition-quality metrics requires human confirmation, per
D3's "exclude explicit test/non-production fixtures" wording (explicit, not inferred).

**Not reinterpreting Class-C**: `NO_PROVIDER_ASSIGNMENT` applies uniformly to any Series with
zero assignments, including 11344/11347 — their existing disposition
(`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`) is unchanged; this model does not single them out or
move them to a different category. A dedicated test asserts this classification for the exact
zero-assignment/non-fixture combination those two Series represent.

**Evidence required**: whether a `provider_assignment` exists, and (separately, caller-supplied)
whether the Series looks like a non-production fixture.

**Test cases** (`TestD3NeverState`, 6 tests): the Class-C orphan pattern classified correctly
and not reinterpreted; assigned-not-yet-run; fixture-candidate precedence; the real fixture
labels from the inventory detected; real production labels (GLD, Equinor, Micron) not
flagged; confirmation the classification function itself takes no label parameter (keeping the
heuristic optional and separately auditable).

**Limitations/dependencies**: the fixture heuristic is a fixed, narrow list — it will miss a
test fixture that doesn't happen to contain one of its markers, and this is by design (a
broader fuzzy match risks false-positive exclusion of real financial series, which D3's
"explicit" wording was read as prohibiting).

**Blocked by missing data or product decisions?** **Not blocked for the classification
mechanism.** **A product decision is still needed** on whether/how confirmed fixture Series are
actually excluded from reported metrics (e.g. a stored flag vs. a query-time filter) — this
design provides the evidence model, not the exclusion mechanism itself, since that would touch
the live schema or query layer, out of this task's read-only scope.

---

## D4 — Conditional fallback-provider consideration

**Current mechanism**: none — a Series either has a second `provider_assignment` or it doesn't;
nothing evaluates whether using it would actually be appropriate.

**Proposed technical representation**: `FallbackCandidateEvidence` (six boolean-or-`None`
fields, one per dimension D4 names: `identity_compatible`, `history_available`,
`adjustment_convention_documented`, `coverage_adequate`, `provenance_acceptable`,
`quality_acceptable`) and `consider_fallback()`, gated in the exact order D4 specifies:
materiality first (`material_impact: bool | None`, caller-supplied — this module never assumes
materiality), then per-candidate adequacy across all six dimensions. `FallbackConsiderationVerdict`
has four members: `NOT_WARRANTED`/`MATERIALITY_UNKNOWN` (materiality not asserted —
modeled as one state, since D4 requires materiality as a precondition, not an inference),
`WARRANTED_CANDIDATE_ADEQUATE`, `WARRANTED_CANDIDATE_INADEQUATE` (with the specific unresolved
dimensions listed, e.g. the real SLV/UBER/URA case where a second assignment exists but its
adjustment-convention comparability to the primary was never documented).

**No universal coverage requirement**: `consider_fallback()` evaluates one candidate for one
already-identified incompatibility — it has no Series-id parameter, no aggregate state, and
asserts nothing about any other Series (confirmed by a dedicated test). It cannot be used to
generate a "every Series needs N providers" policy.

**Evidence required**: a materiality judgment (from whoever determines the intended analysis is
actually affected) and, if material, the six-dimension adequacy assessment of the specific
fallback candidate.

**Test cases** (`TestD4ConditionalFallback`, 6 tests): materiality unknown/not-asserted;
materiality explicitly false modeled the same way (no evaluation proceeds); fully adequate
candidate; the real SLV/UBER/URA-style partially-evidenced candidate (adjustment convention
undocumented); no-candidate-evidence-at-all listing all six dimensions unresolved;
confirmation no Series-level parameter exists to assert universal coverage.

**Limitations/dependencies**: this module takes the six adequacy booleans as given — it does
not itself determine, say, whether "adjustment convention documented" is true for a real pair.
That determination requires evidence this session has repeatedly found absent in HistFinTS
today (D-005/D-021, and the G1/G9 dimension-availability survey) — so in practice, most
real-world calls to `consider_fallback()` today would receive `None` for several dimensions and
land on `WARRANTED_CANDIDATE_INADEQUATE`, an accurate reflection of the evidence gap rather than
a defect in the module.

**Blocked by missing data or product decisions?** **The classifier itself is not blocked** —
implementable and tested today. **Its productive use is blocked** by the same evidence gaps
already documented in `G1_G9_EVALUATOR_DESIGN_2026-08-21.md` §3 (adjustment basis, provenance,
and quality dimensions are largely unrecorded in HistFinTS today) — this is restated, not a new
finding.

---

## D5 — Diagnostic qualification only (explicitly not a defect classification)

**Representation**: `FailureDiagnosticQualifier` (`LIKELY_TRANSIENT` / `REQUEST_LEVEL_ANOMALY` /
`NOT_FOUND_AT_PROVIDER` / `UNQUALIFIED`) and `qualify_failure_diagnostic(http_status_hint)`, a
pure status-code-to-label mapping (429→transient, 400/422→request-level anomaly,
404→not-found), with no severity, blame, or action implied by any member — enforced by a test
asserting no enum value contains "DEFECT" or "BUG." **Not wired to D2's compatibility verdict,
D1's cadence verdict, D4's fallback consideration, or any alerting/remediation path** — it is a
standalone label a caller may attach to a failure record for human triage, matching the exact
real status codes found in the acquisition-quality inventory (429 for the Twelve Data
rate-limiting, 422 for the SLV/UBER/URA/FCX anomaly, 404 for the `.A`/`.B`/`$`-series pattern).

**Test cases** (`TestD5DiagnosticQualifierOnly`, 5 tests): each real status code classified
correctly; an unrecognized code and `None` both fall to `UNQUALIFIED`; a structural test
confirming no enum member name implies a defect classification.

**Blocked by missing data or product decisions?** Not blocked — implementable today, and
deliberately scoped to remain a label only.

---

## Summary

| Item | Blocked? | What's needed to unblock |
|---|---|---|
| D1 (cadence capability) | No, for the classifier. Policy use blocked. | A DFA-approved margin-sufficiency threshold, if the output is ever to drive a decision. |
| D2 (identifier compatibility) | No. | — |
| D3 (NEVER semantics) | No, for classification. Exclusion mechanism blocked. | A product decision on how confirmed fixtures are excluded from reported metrics (schema/query change, out of this task's scope). |
| D4 (conditional fallback) | No, for the classifier. Productive use blocked. | The same adjustment-basis/provenance/quality evidence gaps already documented for G1/G9 — restated, not new. |
| D5 (diagnostic qualifier) | No. | — |

**Implementation**: `src/hf_reswb/application/acquisition_quality_capability.py`.
**Tests**: `tests/test_acquisition_quality_capability.py` — 25 tests, all passing. Full suite:
139 passed, 1 skipped, 1 pre-existing unrelated failure (series 11312), zero regression. No
database access in the module; zero production callers (grep-confirmed). No fallback,
scheduling, or identifier-remediation behavior is implemented or triggered by anything in this
module.
