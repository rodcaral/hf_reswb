"""Acquisition-quality capability model — D1-D5 (DFA-approved next increment).

Read-only, DB-free evidence classifiers for the four acquisition-quality domains DFA approved
(`ACQUISITION_QUALITY_INVENTORY_2026-08-22.md`, docs/evidence/, follow-up items), plus D5 as a diagnostic-only
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
    classification (`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`, docs/evidence/) stands unchanged."""

    ASSIGNED_NOT_YET_RUN = "ASSIGNED_NOT_YET_RUN"
    """A `provider_assignment` exists but no `import_run` has ever been attempted — a
    scheduling/timing gap, not a structural one."""

    NON_PRODUCTION_FIXTURE_CANDIDATE = "NON_PRODUCTION_FIXTURE_CANDIDATE"
    """Heuristically flagged as a probable test/smoke-test/verification artifact based on its
    own label or provider identifier. **A candidate flag, not a determination** — exclusion
    from acquisition-quality metrics requires this to be confirmed by a human, not acted on
    automatically, per D3's "exclude explicit test/non-production fixtures" wording (an
    explicit exclusion, not an inferred one)."""

    SUPERSEDED_NOT_CURRENT_ATTRIBUTION = "SUPERSEDED_NOT_CURRENT_ATTRIBUTION"
    """`series.status = 'SUPERSEDED'` (SE directive 2026-08-26): "retained for historical/
    provenance purposes; no longer the current attribution." Unlike
    `NON_PRODUCTION_FIXTURE_CANDIDATE`, this is **not a heuristic requiring confirmation** —
    `Series.status` is an authoritative, already-established fact, so a SUPERSEDED Series is
    unconditionally excluded from acquisition-quality "needs attention" aggregates the moment
    its status is known, with no pending-review state."""


_FIXTURE_MARKERS = ("smoke test", "duplicate warning test", "test series", "bulk-verify", "-test")
"""A narrow, explicit, inspectable list — not a general fuzzy-match. Extending it is a product
decision, not something this module does silently."""


def looks_like_non_production_fixture(label: str, provider_identifier: str | None) -> bool:
    """Heuristic only — the caller must still confirm before treating a Series as excluded from
    metrics. Case-insensitive substring match against `_FIXTURE_MARKERS`."""
    haystack = f"{label} {provider_identifier or ''}".lower()
    return any(marker in haystack for marker in _FIXTURE_MARKERS)


def classify_never_state(
    *, has_provider_assignment: bool, fixture_candidate: bool, is_superseded: bool = False
) -> NeverStateReason:
    """Classify why a Series has no `import_run` at all. `fixture_candidate` is supplied by the
    caller (typically from `looks_like_non_production_fixture()`, itself confirmed by a human
    before being trusted) — this function does not compute it itself, keeping the heuristic and
    the state classification separately inspectable. `is_superseded` is checked first: unlike
    the fixture heuristic, `Series.status = 'SUPERSEDED'` is an authoritative fact requiring no
    confirmation, so it takes priority over a mere candidate flag."""
    if is_superseded:
        return NeverStateReason.SUPERSEDED_NOT_CURRENT_ATTRIBUTION
    if fixture_candidate:
        return NeverStateReason.NON_PRODUCTION_FIXTURE_CANDIDATE
    if not has_provider_assignment:
        return NeverStateReason.NO_PROVIDER_ASSIGNMENT
    return NeverStateReason.ASSIGNED_NOT_YET_RUN


# ---------------------------------------------------------------------------------------------
# D3 continued -- formal population semantics and exclusion mechanism (SR-approved increment)
#
# "Exclusion" here is a read-only reporting-layer concept only: which rows a metrics view
# includes or omits. Nothing in this section deletes, archives, or otherwise mutates a Series —
# there is no database access anywhere in this module, and confirmation is a caller-supplied,
# attributable fact (who, when, why), never inferred or silently applied.
# ---------------------------------------------------------------------------------------------


class NonProductionFixtureStatus(str, Enum):
    NOT_A_FIXTURE = "NOT_A_FIXTURE"
    """No fixture heuristic matched — treated as ordinary financial-acquisition population."""

    CANDIDATE_UNCONFIRMED = "CANDIDATE_UNCONFIRMED"
    """`looks_like_non_production_fixture()` matched, but no human confirmation is on record.
    **Errs toward inclusion**: a candidate stays in the reported population (flagged for
    review) until explicitly confirmed — silent exclusion on a heuristic alone is exactly what
    D3's "explicit" wording was read as prohibiting."""

    CONFIRMED_FIXTURE = "CONFIRMED_FIXTURE"
    """A human has explicitly confirmed this Series is a non-production artifact (an attributed
    `FixtureConfirmation` is on record). Only this status is eligible for exclusion from
    acquisition-quality metrics."""


@dataclass(frozen=True)
class FixtureConfirmation:
    """An explicit, attributable confirmation — never inferred. `confirmed_by` and
    `confirmed_at` exist so a confirmed exclusion is itself auditable, the same standard this
    project has applied to every other disposition this session (e.g. the 11345/11346
    disposition's retained history)."""

    confirmed_by: str
    confirmed_at: object  # date | datetime — left loosely typed to avoid importing datetime twice
    reason: str


def determine_fixture_status(
    *, candidate_flag: bool, confirmation: FixtureConfirmation | None
) -> NonProductionFixtureStatus:
    """`candidate_flag` is typically `looks_like_non_production_fixture()`'s output.
    `confirmation`, if present, is what actually authorizes exclusion — the flag alone never
    does."""
    if confirmation is not None:
        return NonProductionFixtureStatus.CONFIRMED_FIXTURE
    if candidate_flag:
        return NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED
    return NonProductionFixtureStatus.NOT_A_FIXTURE


class AcquisitionQualityPopulationMembership(str, Enum):
    """The formal population semantics D3 asked for: which reported metric bucket a Series
    belongs in, distinct from (but derived from) its raw `ImportState`/`NeverStateReason`."""

    INCLUDED_ACQUISITION_CANDIDATE = "INCLUDED_ACQUISITION_CANDIDATE"
    """A real financial Series whose acquisition state (FAILED/STALE/NEVER/OK/etc.) should be
    reported in acquisition-quality metrics."""

    INCLUDED_PENDING_FIXTURE_REVIEW = "INCLUDED_PENDING_FIXTURE_REVIEW"
    """Flagged as a possible fixture but not yet confirmed — still counted, but distinguishable
    in a report so a reviewer can act on it, rather than either silently counting it as a real
    gap or silently dropping it."""

    EXCLUDED_CONFIRMED_FIXTURE = "EXCLUDED_CONFIRMED_FIXTURE"
    """Confirmed non-production artifact — a membership value a metrics view may omit
    from its financial-acquisition-quality counts."""

    EXCLUDED_SUPERSEDED = "EXCLUDED_SUPERSEDED"
    """`series.status = 'SUPERSEDED'` (SE directive 2026-08-26) — unconditionally excluded from
    acquisition-quality "needs attention" aggregates, with no pending-review state, since
    `Series.status` is already authoritative and requires no human confirmation the way the
    fixture heuristic does."""


def classify_population_membership(
    fixture_status: NonProductionFixtureStatus, *, is_superseded: bool = False
) -> AcquisitionQualityPopulationMembership:
    """Pure mapping — fixture status plus the authoritative SUPERSEDED fact determine reporting
    membership under this design. A Series' `NeverStateReason`/`ImportState` still applies
    independently for included rows; this function only decides in/out/pending.
    `is_superseded` is checked first: it is an already-established fact, not a heuristic, so it
    takes priority over fixture status regardless of what the latter says."""
    if is_superseded:
        return AcquisitionQualityPopulationMembership.EXCLUDED_SUPERSEDED
    if fixture_status == NonProductionFixtureStatus.CONFIRMED_FIXTURE:
        return AcquisitionQualityPopulationMembership.EXCLUDED_CONFIRMED_FIXTURE
    if fixture_status == NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED:
        return AcquisitionQualityPopulationMembership.INCLUDED_PENDING_FIXTURE_REVIEW
    return AcquisitionQualityPopulationMembership.INCLUDED_ACQUISITION_CANDIDATE


@dataclass(frozen=True)
class PopulationRow:
    """One Series, carrying just enough for the exclusion mechanism to decide membership —
    a minimal, presentation-agnostic shape, not tied to any particular UI or query."""

    series_id: int
    fixture_status: NonProductionFixtureStatus
    is_superseded: bool = False


@dataclass(frozen=True)
class PopulationFilterResult:
    included: tuple[int, ...]
    pending_review: tuple[int, ...]
    excluded: tuple[int, ...]


def filter_for_acquisition_quality_metrics(rows: list[PopulationRow]) -> PopulationFilterResult:
    """The exclusion mechanism itself: a pure, in-memory partition. No schema, query, or
    storage change is implied or required to use this — a caller (e.g. a future read-only
    reporting view) would build `PopulationRow`s from its own already-fetched data and get back
    which series ids to report, review, or omit. `pending_review` is never silently merged into
    either `included` or `excluded` — a report using this result must surface it as its own
    category, or the whole point of D3's "explicit" requirement is lost."""
    included: list[int] = []
    pending: list[int] = []
    excluded: list[int] = []
    for row in rows:
        membership = classify_population_membership(
            row.fixture_status, is_superseded=row.is_superseded
        )
        if membership == AcquisitionQualityPopulationMembership.INCLUDED_ACQUISITION_CANDIDATE:
            included.append(row.series_id)
        elif membership == AcquisitionQualityPopulationMembership.INCLUDED_PENDING_FIXTURE_REVIEW:
            pending.append(row.series_id)
        else:
            excluded.append(row.series_id)
    return PopulationFilterResult(
        included=tuple(included), pending_review=tuple(pending), excluded=tuple(excluded)
    )


# ---------------------------------------------------------------------------------------------
# D4 -- Conditional fallback-provider consideration
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class FallbackCandidateEvidence:
    """The adequacy dimensions D4 names, supplied by the caller — this module does not infer
    any of them. Absence of a dimension (`None`) means "not evidenced," never "assumed
    acceptable." `comparability_acceptable` was added per SR's 2026-08-22 conditional-approval
    message, which named financial identity, adjustment basis, provenance, coverage/quality,
    and comparability explicitly — comparability (can the fallback's values be meaningfully
    compared against the primary's, e.g. consistent units/timing/methodology) is distinct from
    raw `coverage_adequate` (does the fallback have data at all) and is tracked separately
    rather than folded into it."""

    identity_compatible: bool | None
    history_available: bool | None
    adjustment_convention_documented: bool | None
    coverage_adequate: bool | None
    provenance_acceptable: bool | None
    quality_acceptable: bool | None
    comparability_acceptable: bool | None = None

    def is_fully_adequate(self) -> bool:
        values = (
            self.identity_compatible,
            self.history_available,
            self.adjustment_convention_documented,
            self.coverage_adequate,
            self.provenance_acceptable,
            self.quality_acceptable,
            self.comparability_acceptable,
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
            "comparability_acceptable": self.comparability_acceptable,
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


_ALL_FALLBACK_DIMENSIONS: tuple[str, ...] = (
    "identity_compatible", "history_available", "adjustment_convention_documented",
    "coverage_adequate", "provenance_acceptable", "quality_acceptable", "comparability_acceptable",
)


def consider_fallback(
    *, material_impact: bool | None, candidate_evidence: FallbackCandidateEvidence | None
) -> FallbackConsiderationResult:
    """D4's gate, exactly as specified: materiality first, then per-candidate adequacy across
    all seven named dimensions. Returns no verdict implying any Series *should* have a fallback
    configured — this classifies one candidate for one already-identified incompatibility, not
    a coverage policy (D4: "do not require universal multi-provider coverage")."""
    if material_impact is not True:
        return FallbackConsiderationResult(verdict=FallbackConsiderationVerdict.MATERIALITY_UNKNOWN)
    if candidate_evidence is None or not candidate_evidence.is_fully_adequate():
        unresolved = (
            candidate_evidence.unresolved_dimensions()
            if candidate_evidence
            else _ALL_FALLBACK_DIMENSIONS
        )
        return FallbackConsiderationResult(
            verdict=FallbackConsiderationVerdict.WARRANTED_CANDIDATE_INADEQUATE,
            unresolved_dimensions=unresolved,
        )
    return FallbackConsiderationResult(verdict=FallbackConsiderationVerdict.WARRANTED_CANDIDATE_ADEQUATE)


class FallbackActivationVerdict(str, Enum):
    """The activation-gate outcome — layered on top of `consider_fallback()`'s adequacy
    assessment, exactly as `evaluate_financial_identity()` layers `automatic_resolution_enabled`
    on top of its own predicates. Distinguishes "this candidate is adequate" from "this
    capability may actually be used," per SR's "unblocks the next technical design increment...
    but not activation.\""""

    DISABLED_BY_DEFAULT = "DISABLED_BY_DEFAULT"
    """`fallback_activation_enabled=False` (the default) — no fallback is ever activated
    regardless of evidence. No caller in this codebase sets this to `True`."""

    ELIGIBLE_PENDING_ACTIVATION = "ELIGIBLE_PENDING_ACTIVATION"
    """Materiality asserted and the candidate is fully adequate on all seven dimensions, but the
    activation gate is off — reported so a reviewer can see the capability *would* qualify,
    without it taking effect. Distinct from `DISABLED_BY_DEFAULT` alone so "gate is closed" and
    "gate is closed but nothing would happen anyway" are not conflated."""

    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    """Even with the gate open, the underlying `consider_fallback()` result is not
    `WARRANTED_CANDIDATE_ADEQUATE` (materiality unknown or the candidate is inadequate) — the
    gate being open would not matter here."""

    ACTIVATED = "ACTIVATED"
    """`fallback_activation_enabled=True`, materiality asserted, and the candidate is fully
    adequate on all seven dimensions. **No caller in this codebase sets the gate to `True`** —
    this value exists so the function has a real "on" state to test against, not because
    anything in this repository currently reaches it."""


@dataclass(frozen=True)
class FallbackActivationResult:
    verdict: FallbackActivationVerdict
    underlying: FallbackConsiderationResult


def evaluate_fallback_activation(
    *,
    material_impact: bool | None,
    candidate_evidence: FallbackCandidateEvidence | None,
    fallback_activation_enabled: bool = False,
) -> FallbackActivationResult:
    """The evidence-gated fallback capability SR's message asked for: D4's activation must stay
    gated on financial identity, adjustment basis, provenance, coverage/quality, and
    comparability evidence — enforced by requiring `consider_fallback()`'s full seven-dimension
    adequacy result — **and** on an explicit activation flag that defaults to `False` and is
    never set `True` anywhere in this codebase, mirroring
    `evidence_gated_identity_evaluator.evaluate_financial_identity()`'s
    `automatic_resolution_enabled` gate exactly. This function performs no action regardless of
    its output — it classifies, and returns.
    """
    underlying = consider_fallback(material_impact=material_impact, candidate_evidence=candidate_evidence)
    is_adequate = underlying.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_ADEQUATE

    if not fallback_activation_enabled:
        verdict = (
            FallbackActivationVerdict.ELIGIBLE_PENDING_ACTIVATION
            if is_adequate
            else FallbackActivationVerdict.DISABLED_BY_DEFAULT
        )
        return FallbackActivationResult(verdict=verdict, underlying=underlying)

    if not is_adequate:
        return FallbackActivationResult(verdict=FallbackActivationVerdict.NOT_ELIGIBLE, underlying=underlying)

    return FallbackActivationResult(verdict=FallbackActivationVerdict.ACTIVATED, underlying=underlying)


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
