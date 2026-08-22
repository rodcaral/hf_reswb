"""Acquisition-quality capability model — D1-D5 (DFA-approved next increment).

Read-only, DB-free evidence classifiers for the four acquisition-quality domains DFA approved
(`ACQUISITION_QUALITY_INVENTORY_2026-08-22.md`'s follow-up items), plus D5 as a diagnostic-only
qualifier. Follows the established conventions of `class_e_identity_signal.py` and
`evidence_gated_identity_evaluator.py`: frozen dataclasses, `str, Enum` types with per-member
docstrings, pure functions, no database access, no action performed by any function here.

**None of these functions modifies a schedule, provider assignment, Series, or observation.**
Each takes evidence the caller has already gathered and returns a classification only.

D1-D4 deliberately take their governing thresholds/judgments (margin sufficiency, material
impact, candidate adequacy) as caller-supplied evidence rather than baking in a number or rule
this module was not given authority to invent — consistent with D1's "do not assume ... margin
beyond what DFA approved," D2's "do not implement a universal `.`/`$` syntax rule," and D4's
"do not require universal multi-provider coverage."
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum

# ---------------------------------------------------------------------------------------------
# D1 -- Currentness/cadence capability
# ---------------------------------------------------------------------------------------------


class CadenceCapabilityVerdict(str, Enum):
    SUFFICIENT_MARGIN = "SUFFICIENT_MARGIN"
    """Every observed successful-run gap for this Series is within its declared staleness
    tolerance — the acquisition process, as it has actually run, is structurally capable of
    keeping this Series current."""

    INSUFFICIENT_MARGIN = "INSUFFICIENT_MARGIN"
    """At least one observed successful-run gap exceeds the declared tolerance — the process
    could produce a stale reading even when "working" (no failure), because its own historical
    rhythm does not fit inside the tolerance window. Distinct from a transient outage: this is
    evidence about the configured cadence itself, not about any single missed run."""

    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    """Too few successful runs are on record to assess the process's own rhythm (fewer than
    `min_samples`). Returned rather than guessing SUFFICIENT or INSUFFICIENT from a thin
    sample."""


@dataclass(frozen=True)
class CadenceCapabilityAssessment:
    verdict: CadenceCapabilityVerdict
    tolerance: timedelta
    observed_gap_count: int
    max_observed_gap: timedelta | None
    margin: timedelta | None
    """`tolerance - max_observed_gap`. Reported as evidence, not a policy threshold — this
    module does not judge whether a given margin is "enough"; that judgment belongs to whoever
    consumes this assessment, per D1's instruction not to assume a margin DFA has not approved."""


def assess_cadence_capability(
    *,
    tolerance: timedelta,
    successful_run_started_at: list,
    min_samples: int = 3,
) -> CadenceCapabilityAssessment:
    """Assess whether the historically observed cadence of successful runs is capable of
    satisfying `tolerance`, independent of whether the Series is stale *right now*.

    Args:
        tolerance: the Series' own declared staleness tolerance (the existing
            `staleness_tolerance()` computation in `histfints-v3` is the expected source; this
            function does not recompute or assume it).
        successful_run_started_at: `started_at` timestamps of successful runs, any order,
            reflecting only observed history — not a scheduler configuration.
        min_samples: the minimum number of consecutive-gap observations required before a
            SUFFICIENT/INSUFFICIENT verdict is returned rather than INSUFFICIENT_EVIDENCE.
    """
    ordered = sorted(successful_run_started_at)
    gaps = [b - a for a, b in zip(ordered, ordered[1:])]
    if len(gaps) < min_samples:
        return CadenceCapabilityAssessment(
            verdict=CadenceCapabilityVerdict.INSUFFICIENT_EVIDENCE,
            tolerance=tolerance,
            observed_gap_count=len(gaps),
            max_observed_gap=max(gaps) if gaps else None,
            margin=None,
        )
    max_gap = max(gaps)
    margin = tolerance - max_gap
    verdict = (
        CadenceCapabilityVerdict.SUFFICIENT_MARGIN
        if max_gap <= tolerance
        else CadenceCapabilityVerdict.INSUFFICIENT_MARGIN
    )
    return CadenceCapabilityAssessment(
        verdict=verdict,
        tolerance=tolerance,
        observed_gap_count=len(gaps),
        max_observed_gap=max_gap,
        margin=margin,
    )


# ---------------------------------------------------------------------------------------------
# D2 -- Identifier/provider acquisition compatibility (evidence-based, no syntax rule)
# ---------------------------------------------------------------------------------------------


class RunOutcome(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class IdentifierCompatibilityVerdict(str, Enum):
    RESOLVED = "RESOLVED"
    """This exact (provider, identifier) pair has produced at least one successful run.
    Says nothing about financial identity — only that the provider's endpoint accepts and
    returns data for this literal string."""

    CONSISTENTLY_UNRESOLVED = "CONSISTENTLY_UNRESOLVED"
    """Every recorded attempt for this exact (provider, identifier) pair has failed. Does not
    diagnose *why* (format, delisting, or something else) — see D5 for a diagnostic qualifier
    on the failure shape, kept separate from this compatibility verdict by design."""

    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    """No attempts recorded for this pair yet."""


@dataclass(frozen=True)
class IdentifierCompatibilityAssessment:
    verdict: IdentifierCompatibilityVerdict
    attempt_count: int
    success_count: int


def assess_identifier_compatibility(
    outcomes: list[RunOutcome],
) -> IdentifierCompatibilityAssessment:
    """Evidence-based, not syntax-based: this function looks only at recorded outcomes for one
    (provider, identifier) pair, never at the identifier's own characters. D2 explicitly
    prohibits encoding a universal `.`/`$` rule — this is why no pattern-matching on the
    identifier string appears anywhere in this module.

    Deliberately distinct from `class_e_identity_signal.py`'s financial-identity signal and
    from `evidence_gated_identity_evaluator.py`'s `FinancialIdentityConclusion`: acquisition
    compatibility is a question about whether a string resolves at a provider's API, not about
    whether two Series represent the same financial instrument.
    """
    if not outcomes:
        return IdentifierCompatibilityAssessment(
            verdict=IdentifierCompatibilityVerdict.INSUFFICIENT_EVIDENCE,
            attempt_count=0,
            success_count=0,
        )
    success_count = sum(1 for o in outcomes if o == RunOutcome.SUCCESS)
    verdict = (
        IdentifierCompatibilityVerdict.RESOLVED
        if success_count > 0
        else IdentifierCompatibilityVerdict.CONSISTENTLY_UNRESOLVED
    )
    return IdentifierCompatibilityAssessment(
        verdict=verdict, attempt_count=len(outcomes), success_count=success_count
    )


# ---------------------------------------------------------------------------------------------
# D3 -- NEVER-state evidence model
# ---------------------------------------------------------------------------------------------


class NeverStateReason(str, Enum):
    NO_PROVIDER_ASSIGNMENT = "NO_PROVIDER_ASSIGNMENT"
    """No `provider_assignment` exists for this Series — structurally cannot be imported.
    The existing Class-C orphan targets (11344, 11347) fall here; this module does not
    reinterpret or move them — it applies the same rule uniformly, and their prior
    classification (`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`) stands unchanged."""

    ASSIGNED_NOT_YET_RUN = "ASSIGNED_NOT_YET_RUN"
    """A `provider_assignment` exists but no `import_run` has ever been attempted — a
    scheduling/timing gap, not a structural one."""

    NON_PRODUCTION_FIXTURE_CANDIDATE = "NON_PRODUCTION_FIXTURE_CANDIDATE"
    """Heuristically flagged as a probable test/smoke-test/verification artifact based on its
    own label or provider identifier. **A candidate flag, not a determination** — exclusion
    from acquisition-quality metrics requires this to be confirmed by a human, not acted on
    automatically, per D3's "exclude explicit test/non-production fixtures" wording (an
    explicit exclusion, not an inferred one)."""


_FIXTURE_MARKERS = ("smoke test", "duplicate warning test", "test series", "bulk-verify", "-test")
"""A narrow, explicit, inspectable list — not a general fuzzy-match. Extending it is a product
decision, not something this module does silently."""


def looks_like_non_production_fixture(label: str, provider_identifier: str | None) -> bool:
    """Heuristic only — the caller must still confirm before treating a Series as excluded from
    metrics. Case-insensitive substring match against `_FIXTURE_MARKERS`."""
    haystack = f"{label} {provider_identifier or ''}".lower()
    return any(marker in haystack for marker in _FIXTURE_MARKERS)


def classify_never_state(
    *, has_provider_assignment: bool, fixture_candidate: bool
) -> NeverStateReason:
    """Classify why a Series has no `import_run` at all. `fixture_candidate` is supplied by the
    caller (typically from `looks_like_non_production_fixture()`, itself confirmed by a human
    before being trusted) — this function does not compute it itself, keeping the heuristic and
    the state classification separately inspectable."""
    if fixture_candidate:
        return NeverStateReason.NON_PRODUCTION_FIXTURE_CANDIDATE
    if not has_provider_assignment:
        return NeverStateReason.NO_PROVIDER_ASSIGNMENT
    return NeverStateReason.ASSIGNED_NOT_YET_RUN


# ---------------------------------------------------------------------------------------------
# D4 -- Conditional fallback-provider consideration
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FallbackCandidateEvidence:
    """All six adequacy dimensions D4 names, supplied by the caller — this module does not
    infer any of them. Absence of a dimension (`None`) means "not evidenced," never "assumed
    acceptable.\""""

    identity_compatible: bool | None
    history_available: bool | None
    adjustment_convention_documented: bool | None
    coverage_adequate: bool | None
    provenance_acceptable: bool | None
    quality_acceptable: bool | None

    def is_fully_adequate(self) -> bool:
        values = (
            self.identity_compatible,
            self.history_available,
            self.adjustment_convention_documented,
            self.coverage_adequate,
            self.provenance_acceptable,
            self.quality_acceptable,
        )
        return all(v is True for v in values)

    def unresolved_dimensions(self) -> tuple[str, ...]:
        fields_ = {
            "identity_compatible": self.identity_compatible,
            "history_available": self.history_available,
            "adjustment_convention_documented": self.adjustment_convention_documented,
            "coverage_adequate": self.coverage_adequate,
            "provenance_acceptable": self.provenance_acceptable,
            "quality_acceptable": self.quality_acceptable,
        }
        return tuple(name for name, v in fields_.items() if v is not True)


class FallbackConsiderationVerdict(str, Enum):
    NOT_WARRANTED = "NOT_WARRANTED"
    """Primary-provider incompatibility does not materially affect the intended analysis (per
    caller-supplied judgment) — no fallback evaluation proceeds. D4 requires materiality as a
    precondition, not an afterthought."""

    WARRANTED_CANDIDATE_ADEQUATE = "WARRANTED_CANDIDATE_ADEQUATE"
    """Material impact is asserted, and the evaluated candidate is adequate on all six named
    dimensions."""

    WARRANTED_CANDIDATE_INADEQUATE = "WARRANTED_CANDIDATE_INADEQUATE"
    """Material impact is asserted, but the evaluated candidate fails or lacks evidence on at
    least one dimension — fallback is warranted in principle but this specific candidate does
    not qualify. Does not imply no adequate candidate could ever exist."""

    MATERIALITY_UNKNOWN = "MATERIALITY_UNKNOWN"
    """The caller did not assert whether the incompatibility is material — this module never
    assumes materiality by default."""


@dataclass(frozen=True)
class FallbackConsiderationResult:
    verdict: FallbackConsiderationVerdict
    unresolved_dimensions: tuple[str, ...] = field(default_factory=tuple)


def consider_fallback(
    *, material_impact: bool | None, candidate_evidence: FallbackCandidateEvidence | None
) -> FallbackConsiderationResult:
    """D4's gate, exactly as specified: materiality first, then per-candidate adequacy across
    all six named dimensions. Returns no verdict implying any Series *should* have a fallback
    configured — this classifies one candidate for one already-identified incompatibility, not
    a coverage policy (D4: "do not require universal multi-provider coverage")."""
    if material_impact is not True:
        return FallbackConsiderationResult(verdict=FallbackConsiderationVerdict.MATERIALITY_UNKNOWN)
    if candidate_evidence is None or not candidate_evidence.is_fully_adequate():
        unresolved = candidate_evidence.unresolved_dimensions() if candidate_evidence else (
            "identity_compatible", "history_available", "adjustment_convention_documented",
            "coverage_adequate", "provenance_acceptable", "quality_acceptable",
        )
        return FallbackConsiderationResult(
            verdict=FallbackConsiderationVerdict.WARRANTED_CANDIDATE_INADEQUATE,
            unresolved_dimensions=unresolved,
        )
    return FallbackConsiderationResult(verdict=FallbackConsiderationVerdict.WARRANTED_CANDIDATE_ADEQUATE)


# ---------------------------------------------------------------------------------------------
# D5 -- Diagnostic qualification only (NOT a defect classification)
# ---------------------------------------------------------------------------------------------


class FailureDiagnosticQualifier(str, Enum):
    """Purely descriptive triage labels for a failed run's recorded error shape. **None of
    these is a defect classification, a root-cause determination, or a trigger for any
    downstream action** — D5 is explicit that HTTP 422/rate-limit events must not be
    automatically classified as defects. A `LIKELY_TRANSIENT` qualifier, for instance, is not a
    promise the next attempt will succeed."""

    LIKELY_TRANSIENT = "LIKELY_TRANSIENT"
    """Error shape consistent with a rate-limit or throttling response (e.g. HTTP 429)."""

    REQUEST_LEVEL_ANOMALY = "REQUEST_LEVEL_ANOMALY"
    """Error shape consistent with a request-level rejection distinct from "not found" (e.g.
    HTTP 422) — flagged as worth investigating, not diagnosed further by this function."""

    NOT_FOUND_AT_PROVIDER = "NOT_FOUND_AT_PROVIDER"
    """Error shape consistent with the provider reporting the identifier does not resolve
    (e.g. HTTP 404). Says nothing about *why* — see D2 for the evidence-based compatibility
    verdict, which this qualifier only supplements."""

    UNQUALIFIED = "UNQUALIFIED"
    """The error shape does not match any recognized pattern this function checks for."""


_TRANSIENT_STATUS_HINTS = frozenset({429})
_REQUEST_ANOMALY_STATUS_HINTS = frozenset({400, 422})
_NOT_FOUND_STATUS_HINTS = frozenset({404})


def qualify_failure_diagnostic(http_status_hint: int | None) -> FailureDiagnosticQualifier:
    """A diagnostic label only. Explicitly not wired to any defect-classification, alerting, or
    remediation path in this codebase — D5's own instruction."""
    if http_status_hint in _TRANSIENT_STATUS_HINTS:
        return FailureDiagnosticQualifier.LIKELY_TRANSIENT
    if http_status_hint in _REQUEST_ANOMALY_STATUS_HINTS:
        return FailureDiagnosticQualifier.REQUEST_LEVEL_ANOMALY
    if http_status_hint in _NOT_FOUND_STATUS_HINTS:
        return FailureDiagnosticQualifier.NOT_FOUND_AT_PROVIDER
    return FailureDiagnosticQualifier.UNQUALIFIED
