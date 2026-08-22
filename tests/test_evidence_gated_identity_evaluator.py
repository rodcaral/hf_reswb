"""Tests for the G1/G9 evidence-gated financial-identity evaluator.

Covers the required cases from SE's directive: missing, contradictory, stale, cross-provider,
provider-symbol-only, depositary-layer, and complete-authoritative-evidence, plus the
disabled-by-default gate.
"""
from __future__ import annotations

from datetime import date

import pytest

from hf_reswb.application.evidence_gated_identity_evaluator import (
    MANDATORY_DIMENSIONS,
    DimensionAssessment,
    DimensionStatus,
    EvidenceTier,
    FinancialIdentityConclusion,
    IdentityDimension,
    RelationshipEvidence,
    evaluate_financial_identity,
)

AS_OF = date(2026, 8, 21)


def _complete_authoritative_evidence() -> dict[IdentityDimension, DimensionAssessment]:
    """A fabricated (not real-world) complete evidence set satisfying every §5 predicate --
    used to test the evaluator's own logic, not a claim that HistFinTS has this evidence."""
    common = dict(tier=EvidenceTier.TIER_1_PRIMARY, status=DimensionStatus.ESTABLISHED_EQUIVALENT, effective_from=date(2020, 1, 1))
    return {
        IdentityDimension.ISSUER_SECURITY_IDENTITY: DimensionAssessment(
            dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
            source_description="issuer security-program documentation",
            **common,
        ),
        IdentityDimension.INSTRUMENT_CLASS_SUBTYPE: DimensionAssessment(
            dimension=IdentityDimension.INSTRUMENT_CLASS_SUBTYPE,
            source_description="regulated exchange listing documentation",
            **common,
        ),
        IdentityDimension.LISTING_VENUE: DimensionAssessment(
            dimension=IdentityDimension.LISTING_VENUE,
            source_description="regulated exchange listing documentation",
            **common,
        ),
        IdentityDimension.CURRENCY_DENOMINATION: DimensionAssessment(
            dimension=IdentityDimension.CURRENCY_DENOMINATION,
            source_description="issuer documentation, single currency",
            **common,
        ),
        IdentityDimension.ADJUSTMENT_CONVERSION_BASIS: DimensionAssessment(
            dimension=IdentityDimension.ADJUSTMENT_CONVERSION_BASIS,
            tier=EvidenceTier.TIER_1_PRIMARY,
            status=DimensionStatus.IRRELEVANT,
            source_description="no adjustment/conversion applies to either representation",
        ),
        IdentityDimension.CORPORATE_ACTION_EFFECTIVE_DATE_HISTORY: DimensionAssessment(
            dimension=IdentityDimension.CORPORATE_ACTION_EFFECTIVE_DATE_HISTORY,
            source_description="no corporate action affecting identity on record",
            **common,
        ),
        IdentityDimension.PROVIDER_IDENTIFIER: DimensionAssessment(
            dimension=IdentityDimension.PROVIDER_IDENTIFIER,
            tier=EvidenceTier.TIER_3_PROVIDER_OPERATIONAL,
            status=DimensionStatus.ESTABLISHED_EQUIVALENT,
            source_description="identical provider symbol (corroborating only)",
            effective_from=date(2020, 1, 1),
        ),
    }


class TestDisabledByDefault:
    def test_automatic_resolution_disabled_by_default_returns_unresolved(self) -> None:
        result = evaluate_financial_identity(
            1, 2, _complete_authoritative_evidence(), as_of=AS_OF
        )
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert "disabled by default" in result.reason

    def test_disabled_gate_overrides_even_complete_evidence(self) -> None:
        # Same evidence that produces SAME_INSTRUMENT when enabled must not leak through
        # when the caller omits automatic_resolution_enabled.
        enabled = evaluate_financial_identity(
            1, 2, _complete_authoritative_evidence(), as_of=AS_OF, automatic_resolution_enabled=True
        )
        disabled = evaluate_financial_identity(1, 2, _complete_authoritative_evidence(), as_of=AS_OF)
        assert enabled.conclusion == FinancialIdentityConclusion.SAME_INSTRUMENT
        assert disabled.conclusion == FinancialIdentityConclusion.UNRESOLVED

    def test_technical_candidate_existence_alone_does_not_enable_resolution(self) -> None:
        # A caller that has ONLY a technical SAME_INSTRUMENT signal (e.g. from
        # class_e_identity_signal.py) and passes no automatic_resolution_enabled=True still
        # gets UNRESOLVED -- the technical signal itself never flips the gate.
        evidence = {
            IdentityDimension.PROVIDER_IDENTIFIER: DimensionAssessment(
                dimension=IdentityDimension.PROVIDER_IDENTIFIER,
                tier=EvidenceTier.TIER_3_PROVIDER_OPERATIONAL,
                status=DimensionStatus.ESTABLISHED_EQUIVALENT,
                source_description="identical provider symbol",
            )
        }
        result = evaluate_financial_identity(10165, 11340, evidence, as_of=AS_OF)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED


class TestCompleteAuthoritativeEvidence:
    def test_complete_evidence_yields_same_instrument(self) -> None:
        result = evaluate_financial_identity(
            1, 2, _complete_authoritative_evidence(), as_of=AS_OF, automatic_resolution_enabled=True
        )
        assert result.conclusion == FinancialIdentityConclusion.SAME_INSTRUMENT


class TestMissingEvidence:
    def test_missing_issuer_dimension_is_unresolved(self) -> None:
        evidence = _complete_authoritative_evidence()
        del evidence[IdentityDimension.ISSUER_SECURITY_IDENTITY]
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert "security identity" in result.reason

    def test_missing_mandatory_dimension_other_than_issuer_is_unresolved(self) -> None:
        evidence = _complete_authoritative_evidence()
        del evidence[IdentityDimension.CURRENCY_DENOMINATION]
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED

    def test_unknown_status_is_not_silently_treated_as_established(self) -> None:
        evidence = _complete_authoritative_evidence()
        evidence[IdentityDimension.CURRENCY_DENOMINATION] = DimensionAssessment(
            dimension=IdentityDimension.CURRENCY_DENOMINATION,
            tier=EvidenceTier.TIER_1_PRIMARY,
            status=DimensionStatus.UNKNOWN,
            source_description="no currency documentation available",
        )
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED

    def test_unknown_never_becomes_different(self) -> None:
        # G1/G9 §7: "UNKNOWN must not become DIFFERENT." An UNKNOWN dimension must route to
        # UNRESOLVED, never be silently reinterpreted as ESTABLISHED_DIFFERENT.
        evidence = {
            IdentityDimension.ISSUER_SECURITY_IDENTITY: DimensionAssessment(
                dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
                tier=EvidenceTier.TIER_1_PRIMARY,
                status=DimensionStatus.UNKNOWN,
                source_description="no documentation found",
            )
        }
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        # The evaluator itself never assigns ESTABLISHED_DIFFERENT -- only a caller-supplied
        # DimensionAssessment can, and none was supplied here.


class TestContradictoryEvidence:
    def test_contradictory_dimensions_force_unresolved(self) -> None:
        result = evaluate_financial_identity(
            1,
            2,
            _complete_authoritative_evidence(),
            as_of=AS_OF,
            automatic_resolution_enabled=True,
            contradictory_dimensions=frozenset({IdentityDimension.ISSUER_SECURITY_IDENTITY}),
        )
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert "ISSUER_SECURITY_IDENTITY" in result.contradictions

    def test_contradiction_is_not_majority_vote_or_latest_wins(self) -> None:
        # Even with otherwise-complete evidence, a single flagged contradiction is decisive --
        # the evaluator has no mechanism to "outvote" it with other established dimensions.
        result = evaluate_financial_identity(
            1,
            2,
            _complete_authoritative_evidence(),
            as_of=AS_OF,
            automatic_resolution_enabled=True,
            contradictory_dimensions=frozenset({IdentityDimension.CURRENCY_DENOMINATION}),
        )
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED


class TestStaleEvidence:
    def test_stale_evidence_before_effective_from_is_unresolved(self) -> None:
        evidence = _complete_authoritative_evidence()
        evidence[IdentityDimension.ISSUER_SECURITY_IDENTITY] = DimensionAssessment(
            dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
            tier=EvidenceTier.TIER_1_PRIMARY,
            status=DimensionStatus.ESTABLISHED_EQUIVALENT,
            source_description="documentation effective only from 2027",
            effective_from=date(2027, 1, 1),
        )
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert "stale" in result.reason

    def test_stale_evidence_after_effective_to_is_unresolved(self) -> None:
        evidence = _complete_authoritative_evidence()
        evidence[IdentityDimension.ISSUER_SECURITY_IDENTITY] = DimensionAssessment(
            dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
            tier=EvidenceTier.TIER_1_PRIMARY,
            status=DimensionStatus.ESTABLISHED_EQUIVALENT,
            source_description="documentation lapsed before the transition",
            effective_from=date(2015, 1, 1),
            effective_to=date(2020, 1, 1),
        )
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED

    def test_unknown_effective_period_on_established_evidence_is_unresolved(self) -> None:
        evidence = _complete_authoritative_evidence()
        evidence[IdentityDimension.ISSUER_SECURITY_IDENTITY] = DimensionAssessment(
            dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
            tier=EvidenceTier.TIER_1_PRIMARY,
            status=DimensionStatus.ESTABLISHED_EQUIVALENT,
            source_description="documentation with no stated effective date",
            effective_from=None,
        )
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert "effective period" in result.reason


class TestCrossProviderAndProviderSymbolOnly:
    def test_provider_symbol_only_evidence_cannot_establish_identity(self) -> None:
        # G1/G9 §5: "Provider identifiers may corroborate but cannot substitute for missing
        # security identity." Even a perfect cross-provider symbol match is Tier 3.
        evidence = {
            IdentityDimension.ISSUER_SECURITY_IDENTITY: DimensionAssessment(
                dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
                tier=EvidenceTier.TIER_3_PROVIDER_OPERATIONAL,
                status=DimensionStatus.ESTABLISHED_EQUIVALENT,
                source_description="identical symbol across two independent providers",
            ),
        }
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert "provider/analytical evidence" in result.reason

    def test_cross_provider_agreement_is_corroborating_not_decisive(self) -> None:
        # Two providers agreeing on a Tier-3 symbol does not upgrade the tier.
        evidence = _complete_authoritative_evidence()
        # Downgrade issuer evidence to Tier 3 despite "agreement" framing.
        evidence[IdentityDimension.ISSUER_SECURITY_IDENTITY] = DimensionAssessment(
            dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
            tier=EvidenceTier.TIER_3_PROVIDER_OPERATIONAL,
            status=DimensionStatus.ESTABLISHED_EQUIVALENT,
            source_description="two independent providers agree on the same symbol",
        )
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED


class TestDepositaryLayer:
    def test_depositary_context_with_unresolved_subtype_is_unresolved(self) -> None:
        evidence = _complete_authoritative_evidence()
        evidence[IdentityDimension.INSTRUMENT_CLASS_SUBTYPE] = DimensionAssessment(
            dimension=IdentityDimension.INSTRUMENT_CLASS_SUBTYPE,
            tier=EvidenceTier.TIER_1_PRIMARY,
            status=DimensionStatus.UNKNOWN,
            source_description="ADR/ordinary-share status not independently documented",
        )
        result = evaluate_financial_identity(
            1,
            2,
            evidence,
            as_of=AS_OF,
            automatic_resolution_enabled=True,
            depositary_context_plausible=True,
        )
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert "depositary" in result.reason.lower()

    def test_documented_depositary_relationship_yields_related_but_distinct(self) -> None:
        evidence = {
            IdentityDimension.ISSUER_SECURITY_IDENTITY: DimensionAssessment(
                dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
                tier=EvidenceTier.TIER_1_PRIMARY,
                status=DimensionStatus.ESTABLISHED_EQUIVALENT,
                source_description="same issuer, documented depositary program",
                effective_from=date(2020, 1, 1),
            ),
            IdentityDimension.INSTRUMENT_CLASS_SUBTYPE: DimensionAssessment(
                dimension=IdentityDimension.INSTRUMENT_CLASS_SUBTYPE,
                tier=EvidenceTier.TIER_1_PRIMARY,
                status=DimensionStatus.ESTABLISHED_DIFFERENT,
                source_description="ordinary share vs. ADR, documented by depositary program",
                effective_from=date(2020, 1, 1),
            ),
            IdentityDimension.LISTING_VENUE: DimensionAssessment(
                dimension=IdentityDimension.LISTING_VENUE,
                tier=EvidenceTier.TIER_1_PRIMARY,
                status=DimensionStatus.ESTABLISHED_DIFFERENT,
                source_description="distinct listing venues, documented",
                effective_from=date(2020, 1, 1),
            ),
            IdentityDimension.CURRENCY_DENOMINATION: DimensionAssessment(
                dimension=IdentityDimension.CURRENCY_DENOMINATION,
                tier=EvidenceTier.TIER_1_PRIMARY,
                status=DimensionStatus.ESTABLISHED_DIFFERENT,
                source_description="distinct denomination currencies, documented",
                effective_from=date(2020, 1, 1),
            ),
            IdentityDimension.ADJUSTMENT_CONVERSION_BASIS: DimensionAssessment(
                dimension=IdentityDimension.ADJUSTMENT_CONVERSION_BASIS,
                tier=EvidenceTier.TIER_1_PRIMARY,
                status=DimensionStatus.IRRELEVANT,
                source_description="not material to the relationship question",
            ),
            IdentityDimension.CORPORATE_ACTION_EFFECTIVE_DATE_HISTORY: DimensionAssessment(
                dimension=IdentityDimension.CORPORATE_ACTION_EFFECTIVE_DATE_HISTORY,
                tier=EvidenceTier.TIER_1_PRIMARY,
                status=DimensionStatus.IRRELEVANT,
                source_description="no relevant corporate action",
            ),
        }
        result = evaluate_financial_identity(
            1,
            2,
            evidence,
            as_of=AS_OF,
            automatic_resolution_enabled=True,
            relationship_evidence=RelationshipEvidence(
                tier=EvidenceTier.TIER_1_PRIMARY,
                established=True,
                source_description="documented depositary program linking issuer's ordinary share and ADR",
                effective_from=date(2020, 1, 1),
            ),
        )
        assert result.conclusion == FinancialIdentityConclusion.RELATED_BUT_DISTINCT

    def test_relationship_evidence_alone_without_material_distinction_is_unresolved(self) -> None:
        evidence = _complete_authoritative_evidence()
        # All dimensions equivalent -- no material distinction -- should fall to
        # SAME_INSTRUMENT via the primary path, not RELATED_BUT_DISTINCT; but if forced away
        # from that path (e.g. missing a mandatory dim), RELATED_BUT_DISTINCT still requires
        # an ESTABLISHED_DIFFERENT dimension, which none here provides.
        del evidence[IdentityDimension.CURRENCY_DENOMINATION]
        result = evaluate_financial_identity(
            1,
            2,
            evidence,
            as_of=AS_OF,
            automatic_resolution_enabled=True,
            relationship_evidence=RelationshipEvidence(
                tier=EvidenceTier.TIER_1_PRIMARY,
                established=True,
                source_description="documented relationship, but no distinction evidenced",
                effective_from=date(2020, 1, 1),
            ),
        )
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED


class TestBoundaryStructure:
    def test_mandatory_dimensions_excludes_provider_identifier(self) -> None:
        assert IdentityDimension.PROVIDER_IDENTIFIER not in MANDATORY_DIMENSIONS

    def test_all_seven_dimensions_defined(self) -> None:
        assert len(list(IdentityDimension)) == 7


class TestEvidenceMatrix:
    """The inspectable evidence matrix (SE's next-stage instruction, 2026-08-21): a human
    reviewing any result -- including UNRESOLVED -- must be able to see the per-dimension
    state without re-deriving it from the reason string."""

    def test_matrix_always_has_seven_rows_regardless_of_input(self) -> None:
        result = evaluate_financial_identity(1, 2, {}, as_of=AS_OF, automatic_resolution_enabled=True)
        assert len(result.evidence_matrix) == 7
        assert {row.dimension for row in result.evidence_matrix} == set(IdentityDimension)

    def test_missing_dimension_appears_as_unknown_with_no_tier(self) -> None:
        evidence = _complete_authoritative_evidence()
        del evidence[IdentityDimension.CURRENCY_DENOMINATION]
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        row = next(r for r in result.evidence_matrix if r.dimension == IdentityDimension.CURRENCY_DENOMINATION)
        assert row.status == DimensionStatus.UNKNOWN
        assert row.tier is None

    def test_matrix_populated_even_when_automatic_resolution_disabled(self) -> None:
        result = evaluate_financial_identity(1, 2, _complete_authoritative_evidence(), as_of=AS_OF)
        assert result.conclusion == FinancialIdentityConclusion.UNRESOLVED
        assert len(result.evidence_matrix) == 7

    def test_matrix_flags_mandatory_dimensions(self) -> None:
        result = evaluate_financial_identity(
            1, 2, _complete_authoritative_evidence(), as_of=AS_OF, automatic_resolution_enabled=True
        )
        provider_row = next(r for r in result.evidence_matrix if r.dimension == IdentityDimension.PROVIDER_IDENTIFIER)
        issuer_row = next(r for r in result.evidence_matrix if r.dimension == IdentityDimension.ISSUER_SECURITY_IDENTITY)
        assert provider_row.is_mandatory is False
        assert issuer_row.is_mandatory is True

    def test_matrix_flags_staleness_per_row(self) -> None:
        evidence = _complete_authoritative_evidence()
        evidence[IdentityDimension.ISSUER_SECURITY_IDENTITY] = DimensionAssessment(
            dimension=IdentityDimension.ISSUER_SECURITY_IDENTITY,
            tier=EvidenceTier.TIER_1_PRIMARY,
            status=DimensionStatus.ESTABLISHED_EQUIVALENT,
            source_description="lapsed documentation",
            effective_from=date(2015, 1, 1),
            effective_to=date(2020, 1, 1),
        )
        result = evaluate_financial_identity(1, 2, evidence, as_of=AS_OF, automatic_resolution_enabled=True)
        row = next(r for r in result.evidence_matrix if r.dimension == IdentityDimension.ISSUER_SECURITY_IDENTITY)
        assert row.is_stale_as_of_evaluation is True
