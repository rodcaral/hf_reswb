"""Evidence-gated financial-identity evaluator — G1/G9 Final Domain Ruling implementation.

Implements `docs/G1_G9_Final_Domain_Ruling.md`'s evidence-gated identity model as read-only,
DB-free infrastructure, following the same conventions as `class_e_identity_signal.py`,
`independence_detector.py`, and `provenance_guard.py`: frozen dataclasses, `str, Enum` types
with per-member docstrings, pure functions with no database access.

**This module is deliberately distinct from `class_e_identity_signal.py`.** That module
produces a *technical* candidate signal (`IdentityVerdict`) from provider-catalog and label
evidence. This module produces a *financial* identity conclusion
(`FinancialIdentityConclusion`) from a structured evidence assessment across G1/G9's evidence
hierarchy (Tier 1-4) and identity dimensions. The two share state names (`SAME_INSTRUMENT`,
`RELATED_BUT_DISTINCT`, `UNRESOLVED`) because G1/G9 §1 requires the same three financial
conclusion states — **they are not the same type and must never be conflated**: a technical
`SAME_INSTRUMENT` from the other module is Tier 3 (provider operational) evidence at best, and
per G1/G9 §5 "provider identifiers may corroborate but cannot substitute for missing security
identity" — it can inform, but can never by itself satisfy, this evaluator's conclusion.

**Automatic resolution is disabled by default and cannot be enabled by the existence of a
technical candidate.** `evaluate_financial_identity()` takes `automatic_resolution_enabled`
as an explicit, separate keyword argument that defaults to `False`; when `False` (the default),
the function returns `UNRESOLVED` unconditionally, regardless of how strong the supplied
evidence is (G1/G9 §11: "Automatic resolution must remain disabled by default. Any subsequent
production activation requires a separate scope/authorization decision"). No caller in this
codebase sets this argument to `True` — enabling it is a future, separate authorization
decision, not something this module can trigger on its own.

**No mutation.** This module performs no database access, modifies no Series, observation,
provider assignment, or provenance field, and merges or deletes nothing (G1/G9 §8, "Detection
must not").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class EvidenceTier(str, Enum):
    TIER_1_PRIMARY = "TIER_1_PRIMARY"
    """Issuer/security-program documentation, regulated exchange/listing documentation,
    regulatory filings, official depositary/program documentation, or an authoritative
    structured security identifier with independently-established issuer/security mapping
    (G1/G9 §2, Tier 1). May establish an identity-bearing dimension directly."""

    TIER_2_STRUCTURED_MARKET_DATA = "TIER_2_STRUCTURED_MARKET_DATA"
    """Structured provider/catalog data whose semantics are documented and whose provider
    mapping is sufficiently authoritative for the specific dimension (G1/G9 §2, Tier 2).
    Normally corroborates Tier 1 rather than overriding it."""

    TIER_3_PROVIDER_OPERATIONAL = "TIER_3_PROVIDER_OPERATIONAL"
    """Provider symbol, assignment, ticker, label, normalized symbol, import path, and similar
    operational metadata (G1/G9 §2, Tier 3). Supporting/candidate evidence only — never
    primary financial identity evidence, and can never by itself satisfy this evaluator's
    minimum-evidence predicates for `SAME_INSTRUMENT` or `RELATED_BUT_DISTINCT`."""

    TIER_4_ANALYTICAL_INFERENCE = "TIER_4_ANALYTICAL_INFERENCE"
    """Correlation, price similarity, timestamps, inferred venue, label parsing, ticker
    normalization, common provenance, and similar calculations (G1/G9 §2, Tier 4). Can detect
    candidates or corroborate a conclusion, never establish financial identity by itself."""


class DimensionStatus(str, Enum):
    ESTABLISHED_EQUIVALENT = "ESTABLISHED_EQUIVALENT"
    """Authoritative evidence establishes the two Series are equivalent on this dimension."""

    ESTABLISHED_DIFFERENT = "ESTABLISHED_DIFFERENT"
    """Authoritative evidence establishes the two Series materially differ on this dimension
    — a genuine `DIFFERENT` conclusion, distinct from `UNKNOWN` (G1/G9 §7: "`UNKNOWN` must not
    become `DIFFERENT`" — this status must never be assigned merely because evidence is
    missing; it requires its own positive, authoritative support)."""

    IRRELEVANT = "IRRELEVANT"
    """Authoritative evidence (or documented domain knowledge) establishes this dimension is
    not material to the identity question for this pair — e.g. adjustment basis is irrelevant
    when neither series' representation depends on it."""

    UNKNOWN = "UNKNOWN"
    """No sufficient evidence exists on this dimension. The default status for any dimension
    not explicitly assessed. Per G1/G9 §7, `UNKNOWN` is a mandatory-`UNRESOLVED` trigger on any
    dimension that is not demonstrated `IRRELEVANT` — it must never be silently treated as
    `ESTABLISHED_DIFFERENT` or `ESTABLISHED_EQUIVALENT`."""


class IdentityDimension(str, Enum):
    """The seven identity dimensions G1/G9 §4 requires be assessed independently."""

    ISSUER_SECURITY_IDENTITY = "ISSUER_SECURITY_IDENTITY"
    INSTRUMENT_CLASS_SUBTYPE = "INSTRUMENT_CLASS_SUBTYPE"
    LISTING_VENUE = "LISTING_VENUE"
    CURRENCY_DENOMINATION = "CURRENCY_DENOMINATION"
    PROVIDER_IDENTIFIER = "PROVIDER_IDENTIFIER"
    ADJUSTMENT_CONVERSION_BASIS = "ADJUSTMENT_CONVERSION_BASIS"
    CORPORATE_ACTION_EFFECTIVE_DATE_HISTORY = "CORPORATE_ACTION_EFFECTIVE_DATE_HISTORY"


MANDATORY_DIMENSIONS: frozenset[IdentityDimension] = frozenset(
    {
        IdentityDimension.ISSUER_SECURITY_IDENTITY,
        IdentityDimension.INSTRUMENT_CLASS_SUBTYPE,
        IdentityDimension.LISTING_VENUE,
        IdentityDimension.CURRENCY_DENOMINATION,
        IdentityDimension.ADJUSTMENT_CONVERSION_BASIS,
        IdentityDimension.CORPORATE_ACTION_EFFECTIVE_DATE_HISTORY,
    }
)
"""Dimensions that must reach `ESTABLISHED_EQUIVALENT` or `IRRELEVANT` (never bare `UNKNOWN`)
for automatic `SAME_INSTRUMENT` eligibility, per G1/G9 §5. `PROVIDER_IDENTIFIER` is excluded —
per §5, provider identifiers "may corroborate but cannot substitute for missing security
identity," so it is never a required-for-establishment dimension on its own."""


@dataclass(frozen=True)
class DimensionAssessment:
    dimension: IdentityDimension
    tier: EvidenceTier
    status: DimensionStatus
    source_description: str
    effective_from: date | None = None
    effective_to: date | None = None

    def is_stale(self, as_of: date) -> bool:
        """G1/G9 §3, §7: temporal validity is part of the evidence; stale evidence is a
        mandatory-`UNRESOLVED` trigger, not something an evaluator may treat as still valid."""
        if self.effective_from is not None and as_of < self.effective_from:
            return True
        if self.effective_to is not None and as_of >= self.effective_to:
            return True
        return False

    def has_unknown_effective_period(self) -> bool:
        """An `ESTABLISHED_*` dimension whose effective period is entirely unstated cannot be
        temporally verified against the evaluation date — G1/G9 §7: "Relevant evidence is
        stale or its effective period is unknown" is itself a mandatory-`UNRESOLVED` trigger."""
        return (
            self.status in (DimensionStatus.ESTABLISHED_EQUIVALENT, DimensionStatus.ESTABLISHED_DIFFERENT)
            and self.effective_from is None
        )


@dataclass(frozen=True)
class RelationshipEvidence:
    """Evidence of a documented, non-identity relationship between two Series (e.g. an
    issuer's ordinary share vs. its ADR, or a documented depositary relationship) — the
    positive-relationship half of G1/G9 §6's `RELATED_BUT_DISTINCT` predicate."""

    tier: EvidenceTier
    established: bool
    source_description: str
    effective_from: date | None = None
    effective_to: date | None = None


class FinancialIdentityConclusion(str, Enum):
    """The three financial identity states G1/G9 §1 requires — distinct from, and never to be
    conflated with, `class_e_identity_signal.IdentityVerdict`'s technical states."""

    SAME_INSTRUMENT = "SAME_INSTRUMENT"
    """Authoritative evidence establishes the two Series represent the same financial
    instrument (G1/G9 §1, §5)."""

    RELATED_BUT_DISTINCT = "RELATED_BUT_DISTINCT"
    """Authoritative evidence establishes a meaningful financial relationship and a material
    security/instrument distinction (G1/G9 §1, §6)."""

    UNRESOLVED = "UNRESOLVED"
    """Evidence is insufficient, unavailable, stale, contradictory, or otherwise unsuitable to
    establish either conclusion (G1/G9 §1, §7). The mandatory default whenever automatic
    resolution is disabled, and the mandatory outcome for every condition listed in G1/G9 §7."""


@dataclass(frozen=True)
class DimensionEvaluation:
    """One row of the inspectable evidence matrix — the per-dimension state actually used (or
    found missing) in reaching a conclusion, independent of whether that conclusion was
    `UNRESOLVED`. Always populated for all seven `IdentityDimension` members, so a human
    reviewing an `UNRESOLVED` result can see exactly which dimension(s) were insufficient
    without re-deriving it from the `reason` string alone."""

    dimension: IdentityDimension
    tier: EvidenceTier | None
    status: DimensionStatus
    source_description: str
    effective_from: date | None
    effective_to: date | None
    is_stale_as_of_evaluation: bool
    is_mandatory: bool


@dataclass(frozen=True)
class EvidenceGatedAssessment:
    series_a: int
    series_b: int
    conclusion: FinancialIdentityConclusion
    reason: str
    automatic_resolution_was_enabled: bool
    evidence_matrix: tuple[DimensionEvaluation, ...] = field(default_factory=tuple)
    contradictions: tuple[str, ...] = field(default_factory=tuple)


def _build_evidence_matrix(
    dimension_assessments: dict[IdentityDimension, DimensionAssessment], as_of: date
) -> tuple[DimensionEvaluation, ...]:
    """Build the inspectable evidence matrix — one row per `IdentityDimension`, always all
    seven, regardless of which dimensions the caller actually supplied. A dimension absent
    from `dimension_assessments` is represented as `UNKNOWN` with no tier, not omitted."""
    rows = []
    for dim in IdentityDimension:
        assessment = dimension_assessments.get(dim)
        if assessment is None:
            rows.append(
                DimensionEvaluation(
                    dimension=dim,
                    tier=None,
                    status=DimensionStatus.UNKNOWN,
                    source_description="no evidence supplied",
                    effective_from=None,
                    effective_to=None,
                    is_stale_as_of_evaluation=False,
                    is_mandatory=dim in MANDATORY_DIMENSIONS,
                )
            )
        else:
            rows.append(
                DimensionEvaluation(
                    dimension=dim,
                    tier=assessment.tier,
                    status=assessment.status,
                    source_description=assessment.source_description,
                    effective_from=assessment.effective_from,
                    effective_to=assessment.effective_to,
                    is_stale_as_of_evaluation=assessment.status != DimensionStatus.UNKNOWN
                    and assessment.is_stale(as_of),
                    is_mandatory=dim in MANDATORY_DIMENSIONS,
                )
            )
    return tuple(rows)


def evaluate_financial_identity(
    series_a: int,
    series_b: int,
    dimension_assessments: dict[IdentityDimension, DimensionAssessment],
    *,
    relationship_evidence: RelationshipEvidence | None = None,
    contradictory_dimensions: frozenset[IdentityDimension] = frozenset(),
    depositary_context_plausible: bool = False,
    as_of: date,
    automatic_resolution_enabled: bool = False,
) -> EvidenceGatedAssessment:
    """Evaluate financial identity per G1/G9's evidence-gated model. Pure function, no
    database access, no mutation of any kind — returns a classification only.

    Args:
        dimension_assessments: assessment per `IdentityDimension`; a dimension absent from
            this dict is treated as `DimensionStatus.UNKNOWN` (never silently assumed
            established).
        relationship_evidence: the positive-relationship evidence for a potential
            `RELATED_BUT_DISTINCT` conclusion (G1/G9 §6.1). `None` if no relationship has been
            documented.
        contradictory_dimensions: dimensions on which two independently authoritative (Tier
            1/2) sources conflict and the conflict cannot be resolved by effective date/version
            (G1/G9 §3). Any non-empty set here forces `UNRESOLVED`.
        depositary_context_plausible: set when the pair plausibly involves an
            ADR/ADS/CEDEAR/depositary relationship (e.g. one series' label or instrument
            subtype suggests it) but that status has not been independently established
            (G1/G9 §7: "ADR/ADS/CEDEAR/depositary status is unresolved where it matters").
        as_of: the evaluation date, for temporal-validity checks (G1/G9 §3).
        automatic_resolution_enabled: **must be explicitly set to `True` by the caller.**
            Defaults to `False`. When `False`, returns `UNRESOLVED` unconditionally — this is
            the module-level disabled-by-default gate (G1/G9 §11), and no caller in this
            codebase sets it to `True`.
    """
    evidence_matrix = _build_evidence_matrix(dimension_assessments, as_of)

    if not automatic_resolution_enabled:
        return EvidenceGatedAssessment(
            series_a=series_a,
            series_b=series_b,
            conclusion=FinancialIdentityConclusion.UNRESOLVED,
            reason=(
                "automatic resolution is disabled by default (G1/G9 §11); a technical "
                "candidate signal alone never enables it"
            ),
            automatic_resolution_was_enabled=False,
            evidence_matrix=evidence_matrix,
        )

    if contradictory_dimensions:
        return EvidenceGatedAssessment(
            series_a=series_a,
            series_b=series_b,
            conclusion=FinancialIdentityConclusion.UNRESOLVED,
            reason="authoritative evidence conflicts and cannot be resolved by effective date/version (G1/G9 §3, §7)",
            automatic_resolution_was_enabled=True,
            evidence_matrix=evidence_matrix,
            contradictions=tuple(d.value for d in sorted(contradictory_dimensions, key=lambda d: d.value)),
        )

    issuer = dimension_assessments.get(IdentityDimension.ISSUER_SECURITY_IDENTITY)
    if issuer is None or issuer.status == DimensionStatus.UNKNOWN:
        return EvidenceGatedAssessment(
            series_a=series_a,
            series_b=series_b,
            conclusion=FinancialIdentityConclusion.UNRESOLVED,
            reason="security identity cannot be independently established (G1/G9 §7)",
            automatic_resolution_was_enabled=True,
            evidence_matrix=evidence_matrix,
        )
    if issuer.tier == EvidenceTier.TIER_3_PROVIDER_OPERATIONAL or issuer.tier == EvidenceTier.TIER_4_ANALYTICAL_INFERENCE:
        return EvidenceGatedAssessment(
            series_a=series_a,
            series_b=series_b,
            conclusion=FinancialIdentityConclusion.UNRESOLVED,
            reason=(
                "the only positive evidence for security identity is provider/analytical "
                "evidence, which cannot substitute for authoritative Tier 1/2 support (G1/G9 §5, §7)"
            ),
            automatic_resolution_was_enabled=True,
            evidence_matrix=evidence_matrix,
        )

    if depositary_context_plausible:
        depositary_dim = dimension_assessments.get(IdentityDimension.INSTRUMENT_CLASS_SUBTYPE)
        if depositary_dim is None or depositary_dim.status == DimensionStatus.UNKNOWN:
            return EvidenceGatedAssessment(
                series_a=series_a,
                series_b=series_b,
                conclusion=FinancialIdentityConclusion.UNRESOLVED,
                reason="ADR/ADS/CEDEAR/depositary status is unresolved where it matters (G1/G9 §7)",
                automatic_resolution_was_enabled=True,
                evidence_matrix=evidence_matrix,
            )

    for dim, assessment in dimension_assessments.items():
        if assessment.has_unknown_effective_period():
            return EvidenceGatedAssessment(
                series_a=series_a,
                series_b=series_b,
                conclusion=FinancialIdentityConclusion.UNRESOLVED,
                reason=f"evidence for {dim.value} has an unknown effective period (G1/G9 §7)",
                automatic_resolution_was_enabled=True,
                evidence_matrix=evidence_matrix,
            )
        if assessment.status != DimensionStatus.UNKNOWN and assessment.is_stale(as_of):
            return EvidenceGatedAssessment(
                series_a=series_a,
                series_b=series_b,
                conclusion=FinancialIdentityConclusion.UNRESOLVED,
                reason=f"evidence for {dim.value} is stale as of {as_of.isoformat()} (G1/G9 §3, §7)",
                automatic_resolution_was_enabled=True,
                evidence_matrix=evidence_matrix,
            )

    same_instrument_ok = True
    same_instrument_reasons: list[str] = []
    for dim in MANDATORY_DIMENSIONS:
        assessment = dimension_assessments.get(dim)
        if assessment is None or assessment.status not in (
            DimensionStatus.ESTABLISHED_EQUIVALENT,
            DimensionStatus.IRRELEVANT,
        ):
            same_instrument_ok = False
            same_instrument_reasons.append(f"{dim.value} not established equivalent/irrelevant")
        elif assessment.tier not in (EvidenceTier.TIER_1_PRIMARY, EvidenceTier.TIER_2_STRUCTURED_MARKET_DATA):
            same_instrument_ok = False
            same_instrument_reasons.append(f"{dim.value} evidence is not Tier 1/2")

    if same_instrument_ok:
        return EvidenceGatedAssessment(
            series_a=series_a,
            series_b=series_b,
            conclusion=FinancialIdentityConclusion.SAME_INSTRUMENT,
            reason=(
                "all mandatory identity dimensions established equivalent or irrelevant by "
                "Tier 1/2 evidence, no contradictions, no stale/unbounded evidence (G1/G9 §5)"
            ),
            automatic_resolution_was_enabled=True,
            evidence_matrix=evidence_matrix,
        )

    if relationship_evidence is not None and relationship_evidence.established and relationship_evidence.tier in (
        EvidenceTier.TIER_1_PRIMARY,
        EvidenceTier.TIER_2_STRUCTURED_MARKET_DATA,
    ):
        material_distinction = any(
            a.status == DimensionStatus.ESTABLISHED_DIFFERENT
            and a.tier in (EvidenceTier.TIER_1_PRIMARY, EvidenceTier.TIER_2_STRUCTURED_MARKET_DATA)
            for a in dimension_assessments.values()
        )
        no_unresolved_that_could_reverse = not any(
            a.status == DimensionStatus.UNKNOWN and dim in MANDATORY_DIMENSIONS
            for dim, a in dimension_assessments.items()
        )
        if material_distinction and no_unresolved_that_could_reverse:
            return EvidenceGatedAssessment(
                series_a=series_a,
                series_b=series_b,
                conclusion=FinancialIdentityConclusion.RELATED_BUT_DISTINCT,
                reason=(
                    "documented relationship (Tier 1/2) plus a material, non-provider-naming "
                    "security distinction (Tier 1/2), no unresolved dimension that could "
                    "reverse the conclusion (G1/G9 §6)"
                ),
                automatic_resolution_was_enabled=True,
                evidence_matrix=evidence_matrix,
            )

    return EvidenceGatedAssessment(
        series_a=series_a,
        series_b=series_b,
        conclusion=FinancialIdentityConclusion.UNRESOLVED,
        reason=(
            "insufficient authoritative evidence for either automatic conclusion: "
            + "; ".join(same_instrument_reasons)
        ),
        automatic_resolution_was_enabled=True,
        evidence_matrix=evidence_matrix,
    )
