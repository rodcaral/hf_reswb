"""Tests for the D1-D5 acquisition-quality capability model.

Fixtures grounded in real cases from ACQUISITION_QUALITY_INVENTORY_2026-08-22.md: the 32-Series
1h cadence gap (D1), the 61-Series .{dollar} identifier-format failures and the SLV/UBER/URA
dual-path-failing pattern (D2/D5), the two NEVER sub-populations including the test fixtures
(D3), and the already-documented Class-C orphans (D3, not reinterpreted).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hf_reswb.application.acquisition_quality_capability import (
    AcquisitionQualityPopulationMembership,
    CadenceCapabilityVerdict,
    FailureDiagnosticQualifier,
    FallbackActivationVerdict,
    FallbackCandidateEvidence,
    FallbackConsiderationVerdict,
    FixtureConfirmation,
    IdentifierCompatibilityVerdict,
    NeverStateReason,
    NonProductionFixtureStatus,
    PopulationRow,
    RunOutcome,
    assess_cadence_capability,
    assess_identifier_compatibility,
    classify_never_state,
    classify_population_membership,
    consider_fallback,
    determine_fixture_status,
    evaluate_fallback_activation,
    filter_for_acquisition_quality_metrics,
    looks_like_non_production_fixture,
    qualify_failure_diagnostic,
)


def _t(hours_ago: float) -> datetime:
    return datetime(2026, 8, 22, 12, 0, tzinfo=timezone.utc) - timedelta(hours=hours_ago)


class TestD1CadenceCapability:
    def test_sufficient_margin_when_all_gaps_within_tolerance(self) -> None:
        runs = [_t(72), _t(48), _t(24), _t(0)]  # ~24h gaps, 1h series' real 1-day tolerance
        result = assess_cadence_capability(tolerance=timedelta(days=1), successful_run_started_at=runs)
        assert result.verdict == CadenceCapabilityVerdict.SUFFICIENT_MARGIN
        assert result.margin is not None and result.margin >= timedelta(0)

    def test_insufficient_margin_when_a_gap_exceeds_tolerance(self) -> None:
        # Mirrors the real 32-Series pattern: last successful run over a day before the next
        # (never), against the 1h series' 1-day tolerance.
        runs = [_t(96), _t(72), _t(48), _t(0)]
        # Insert one oversized gap.
        runs = [_t(200), _t(150), _t(50), _t(0)]
        result = assess_cadence_capability(tolerance=timedelta(days=1), successful_run_started_at=runs)
        assert result.verdict == CadenceCapabilityVerdict.INSUFFICIENT_MARGIN
        assert result.margin is not None and result.margin < timedelta(0)

    def test_insufficient_evidence_below_min_samples(self) -> None:
        runs = [_t(24), _t(0)]  # one gap only, default min_samples=3
        result = assess_cadence_capability(tolerance=timedelta(days=1), successful_run_started_at=runs)
        assert result.verdict == CadenceCapabilityVerdict.INSUFFICIENT_EVIDENCE

    def test_no_margin_value_asserted_as_policy(self) -> None:
        # The margin is reported, not judged -- this module takes no position on "how much
        # margin is enough," per D1's instruction not to assume a threshold DFA didn't approve.
        runs = [_t(72), _t(48), _t(24), _t(0)]
        result = assess_cadence_capability(tolerance=timedelta(days=1), successful_run_started_at=runs)
        assert isinstance(result.margin, timedelta)
        # No verdict value like "MARGIN_ADEQUATE_PER_POLICY" exists in the enum.
        assert result.verdict in (CadenceCapabilityVerdict.SUFFICIENT_MARGIN, CadenceCapabilityVerdict.INSUFFICIENT_MARGIN)


class TestD2IdentifierCompatibility:
    def test_resolved_when_at_least_one_success(self) -> None:
        # SLV/UBER/URA's Twelve Data path: succeeded twice historically before rate-limiting.
        outcomes = [RunOutcome.SUCCESS, RunOutcome.SUCCESS, RunOutcome.FAILED, RunOutcome.FAILED]
        result = assess_identifier_compatibility(outcomes)
        assert result.verdict == IdentifierCompatibilityVerdict.RESOLVED
        assert result.success_count == 2

    def test_consistently_unresolved_when_all_fail(self) -> None:
        # A .A/.B-style series: every Yahoo attempt failed with HTTP 404.
        outcomes = [RunOutcome.FAILED] * 5
        result = assess_identifier_compatibility(outcomes)
        assert result.verdict == IdentifierCompatibilityVerdict.CONSISTENTLY_UNRESOLVED

    def test_insufficient_evidence_with_no_attempts(self) -> None:
        result = assess_identifier_compatibility([])
        assert result.verdict == IdentifierCompatibilityVerdict.INSUFFICIENT_EVIDENCE

    def test_no_syntax_inspection_occurs(self) -> None:
        # The function signature takes only outcomes -- no identifier string parameter exists
        # to inspect, by construction (D2: no universal . / $ rule).
        import inspect

        sig = inspect.signature(assess_identifier_compatibility)
        assert "identifier" not in sig.parameters
        assert "provider_symbol" not in sig.parameters


class TestD3NeverState:
    def test_class_c_orphan_pattern_classified_no_provider_assignment(self) -> None:
        # 11344/11347: zero provider_assignment, not a fixture -- not reinterpreted from
        # CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md.
        result = classify_never_state(has_provider_assignment=False, fixture_candidate=False)
        assert result == NeverStateReason.NO_PROVIDER_ASSIGNMENT

    def test_assigned_not_yet_run(self) -> None:
        result = classify_never_state(has_provider_assignment=True, fixture_candidate=False)
        assert result == NeverStateReason.ASSIGNED_NOT_YET_RUN

    def test_fixture_candidate_takes_precedence(self) -> None:
        result = classify_never_state(has_provider_assignment=True, fixture_candidate=True)
        assert result == NeverStateReason.NON_PRODUCTION_FIXTURE_CANDIDATE

    def test_real_fixture_labels_detected(self) -> None:
        # The exact real labels from the investigation's section 1b.
        assert looks_like_non_production_fixture("GLD Smoke Test CEDEAR", "GLD")
        assert looks_like_non_production_fixture("Duplicate Warning Test", "ZZZTEST1")
        assert looks_like_non_production_fixture("UC-6 Test Series", "UC6TEST2")
        assert looks_like_non_production_fixture("Apple Inc. - Common Stock", "AAPL-BULK-VERIFY-DUP")

    def test_real_production_labels_not_flagged(self) -> None:
        assert not looks_like_non_production_fixture("SPDR Gold Shares - ETF (NYSE)", None)
        assert not looks_like_non_production_fixture("Equinor ASA (NYSE)", None)
        assert not looks_like_non_production_fixture("Micron Technology, Inc. - Stock (NASDAQ)", "MU")

    def test_heuristic_is_a_candidate_flag_not_final(self) -> None:
        # classify_never_state never calls the heuristic itself -- the caller must confirm.
        import inspect

        sig = inspect.signature(classify_never_state)
        assert "label" not in sig.parameters


class TestD3PopulationSemanticsAndExclusion:
    """SR-approved D3 increment: formal population semantics and the (read-only, in-memory)
    exclusion mechanism for confirmed test/non-production fixtures."""

    def test_no_confirmation_stays_unconfirmed_even_with_candidate_flag(self) -> None:
        status = determine_fixture_status(candidate_flag=True, confirmation=None)
        assert status == NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED

    def test_confirmation_present_is_confirmed_fixture(self) -> None:
        confirmation = FixtureConfirmation(
            confirmed_by="SE", confirmed_at="2026-08-22", reason="known smoke-test artifact"
        )
        status = determine_fixture_status(candidate_flag=True, confirmation=confirmation)
        assert status == NonProductionFixtureStatus.CONFIRMED_FIXTURE

    def test_no_flag_no_confirmation_is_not_a_fixture(self) -> None:
        status = determine_fixture_status(candidate_flag=False, confirmation=None)
        assert status == NonProductionFixtureStatus.NOT_A_FIXTURE

    def test_unconfirmed_candidate_stays_included_pending_review(self) -> None:
        # The core D3 guarantee: a heuristic match alone never excludes a Series.
        membership = classify_population_membership(NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED)
        assert membership == AcquisitionQualityPopulationMembership.INCLUDED_PENDING_FIXTURE_REVIEW

    def test_confirmed_fixture_is_the_only_excludable_status(self) -> None:
        membership = classify_population_membership(NonProductionFixtureStatus.CONFIRMED_FIXTURE)
        assert membership == AcquisitionQualityPopulationMembership.EXCLUDED_CONFIRMED_FIXTURE

    def test_filter_partitions_real_inventory_shape(self) -> None:
        # Mirrors the real 2026-08-22 inventory: 11344/11347 (real, not fixtures, zero
        # assignment) alongside the six confirmed test-fixture series ids.
        rows = [
            PopulationRow(series_id=11344, fixture_status=NonProductionFixtureStatus.NOT_A_FIXTURE),
            PopulationRow(series_id=11347, fixture_status=NonProductionFixtureStatus.NOT_A_FIXTURE),
            PopulationRow(series_id=11304, fixture_status=NonProductionFixtureStatus.CONFIRMED_FIXTURE),
            PopulationRow(series_id=11306, fixture_status=NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED),
        ]
        result = filter_for_acquisition_quality_metrics(rows)
        assert result.included == (11344, 11347)
        assert result.pending_review == (11306,)
        assert result.excluded == (11304,)

    def test_filter_touches_no_database(self) -> None:
        import inspect

        assert "connection" not in inspect.signature(filter_for_acquisition_quality_metrics).parameters


class TestSupersededExclusionFromNeedsAttention:
    """SE directive 2026-08-26: acquisition-quality needs-attention aggregates must exclude
    SUPERSEDED. Unlike the fixture heuristic, this is a non-heuristic, authoritative exclusion
    -- `Series.status` requires no human confirmation, so there is no pending-review state."""

    def test_superseded_takes_priority_in_never_state_classification(self) -> None:
        reason = classify_never_state(
            has_provider_assignment=False, fixture_candidate=False, is_superseded=True
        )
        assert reason == NeverStateReason.SUPERSEDED_NOT_CURRENT_ATTRIBUTION

    def test_superseded_overrides_fixture_candidate_flag(self) -> None:
        # Status is authoritative; a coincidental heuristic match must not override it.
        reason = classify_never_state(
            has_provider_assignment=True, fixture_candidate=True, is_superseded=True
        )
        assert reason == NeverStateReason.SUPERSEDED_NOT_CURRENT_ATTRIBUTION

    def test_not_superseded_falls_through_to_existing_reasons(self) -> None:
        reason = classify_never_state(
            has_provider_assignment=False, fixture_candidate=False, is_superseded=False
        )
        assert reason == NeverStateReason.NO_PROVIDER_ASSIGNMENT

    def test_population_membership_excludes_superseded_unconditionally(self) -> None:
        membership = classify_population_membership(
            NonProductionFixtureStatus.NOT_A_FIXTURE, is_superseded=True
        )
        assert membership == AcquisitionQualityPopulationMembership.EXCLUDED_SUPERSEDED

    def test_population_membership_superseded_has_no_pending_review_state(self) -> None:
        # Even a candidate-unconfirmed fixture flag doesn't produce a pending state once
        # is_superseded is True -- status is authoritative, not a heuristic needing review.
        membership = classify_population_membership(
            NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED, is_superseded=True
        )
        assert membership == AcquisitionQualityPopulationMembership.EXCLUDED_SUPERSEDED

    def test_filter_excludes_superseded_from_needs_attention(self) -> None:
        # Real cases: 11345/11346 are SUPERSEDED with zero provider assignment -- would
        # otherwise resolve to NOT_A_FIXTURE/included without this exclusion.
        rows = [
            PopulationRow(series_id=11344, fixture_status=NonProductionFixtureStatus.NOT_A_FIXTURE),
            PopulationRow(
                series_id=11345,
                fixture_status=NonProductionFixtureStatus.NOT_A_FIXTURE,
                is_superseded=True,
            ),
            PopulationRow(
                series_id=11346,
                fixture_status=NonProductionFixtureStatus.NOT_A_FIXTURE,
                is_superseded=True,
            ),
        ]
        result = filter_for_acquisition_quality_metrics(rows)
        assert result.included == (11344,)
        assert result.pending_review == ()
        assert 11345 not in result.included and 11345 not in result.pending_review
        assert 11346 not in result.included and 11346 not in result.pending_review
        assert result.excluded == (11345, 11346)


class TestD4EvidenceGatedFallbackActivation:
    """SR-approved D4 increment: activation must stay gated on financial identity, adjustment
    basis, provenance, coverage/quality, and comparability evidence, and on an explicit,
    default-off activation flag mirroring the G1/G9 evaluator's pattern."""

    _adequate_evidence = FallbackCandidateEvidence(
        identity_compatible=True, history_available=True,
        adjustment_convention_documented=True, coverage_adequate=True,
        provenance_acceptable=True, quality_acceptable=True, comparability_acceptable=True,
    )

    def test_disabled_by_default_even_with_no_evidence(self) -> None:
        result = evaluate_fallback_activation(material_impact=None, candidate_evidence=None)
        assert result.verdict == FallbackActivationVerdict.DISABLED_BY_DEFAULT

    def test_eligible_pending_activation_when_adequate_but_gate_closed(self) -> None:
        result = evaluate_fallback_activation(
            material_impact=True, candidate_evidence=self._adequate_evidence
        )
        assert result.verdict == FallbackActivationVerdict.ELIGIBLE_PENDING_ACTIVATION

    def test_activated_only_when_gate_open_and_fully_adequate(self) -> None:
        result = evaluate_fallback_activation(
            material_impact=True,
            candidate_evidence=self._adequate_evidence,
            fallback_activation_enabled=True,
        )
        assert result.verdict == FallbackActivationVerdict.ACTIVATED

    def test_not_eligible_when_gate_open_but_inadequate(self) -> None:
        inadequate = FallbackCandidateEvidence(
            identity_compatible=True, history_available=True,
            adjustment_convention_documented=None, coverage_adequate=True,
            provenance_acceptable=True, quality_acceptable=True, comparability_acceptable=True,
        )
        result = evaluate_fallback_activation(
            material_impact=True, candidate_evidence=inadequate, fallback_activation_enabled=True
        )
        assert result.verdict == FallbackActivationVerdict.NOT_ELIGIBLE

    def test_gate_open_but_materiality_unknown_never_activates(self) -> None:
        result = evaluate_fallback_activation(
            material_impact=None,
            candidate_evidence=self._adequate_evidence,
            fallback_activation_enabled=True,
        )
        assert result.verdict == FallbackActivationVerdict.NOT_ELIGIBLE

    def test_module_never_calls_itself_with_activation_enabled(self) -> None:
        # The only occurrence of "evaluate_fallback_activation(" in the module's own source is
        # its own `def` line -- it never invokes itself, so it cannot be the source of a True
        # activation anywhere in this codebase.
        import inspect
        import hf_reswb.application.acquisition_quality_capability as module

        assert inspect.getsource(module).count("evaluate_fallback_activation(") == 1


class TestD4ConditionalFallback:
    def test_materiality_unknown_when_not_asserted(self) -> None:
        result = consider_fallback(material_impact=None, candidate_evidence=None)
        assert result.verdict == FallbackConsiderationVerdict.MATERIALITY_UNKNOWN

    def test_not_warranted_is_represented_via_caller_not_evaluating(self) -> None:
        # D4: "primary-provider incompatibility must materially affect an intended analysis" --
        # material_impact=False means the caller decided not to proceed; modeled as
        # MATERIALITY_UNKNOWN's sibling case (False is still "not True").
        result = consider_fallback(material_impact=False, candidate_evidence=None)
        assert result.verdict == FallbackConsiderationVerdict.MATERIALITY_UNKNOWN

    def test_warranted_adequate_when_all_seven_dimensions_true(self) -> None:
        evidence = FallbackCandidateEvidence(
            identity_compatible=True, history_available=True,
            adjustment_convention_documented=True, coverage_adequate=True,
            provenance_acceptable=True, quality_acceptable=True,
            comparability_acceptable=True,
        )
        result = consider_fallback(material_impact=True, candidate_evidence=evidence)
        assert result.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_ADEQUATE
        assert result.unresolved_dimensions == ()

    def test_comparability_missing_alone_makes_candidate_inadequate(self) -> None:
        # SR's 2026-08-22 message named comparability explicitly, distinct from coverage.
        evidence = FallbackCandidateEvidence(
            identity_compatible=True, history_available=True,
            adjustment_convention_documented=True, coverage_adequate=True,
            provenance_acceptable=True, quality_acceptable=True,
            comparability_acceptable=None,
        )
        result = consider_fallback(material_impact=True, candidate_evidence=evidence)
        assert result.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_INADEQUATE
        assert result.unresolved_dimensions == ("comparability_acceptable",)

    def test_warranted_inadequate_when_one_dimension_missing(self) -> None:
        # SLV/UBER/URA-style: a second provider assignment exists (Twelve Data) but its
        # adjustment/quality profile relative to Yahoo was never independently documented.
        evidence = FallbackCandidateEvidence(
            identity_compatible=True, history_available=True,
            adjustment_convention_documented=None, coverage_adequate=True,
            provenance_acceptable=True, quality_acceptable=True,
        )
        result = consider_fallback(material_impact=True, candidate_evidence=evidence)
        assert result.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_INADEQUATE
        assert "adjustment_convention_documented" in result.unresolved_dimensions

    def test_no_candidate_evidence_lists_all_seven_unresolved(self) -> None:
        result = consider_fallback(material_impact=True, candidate_evidence=None)
        assert result.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_INADEQUATE
        assert len(result.unresolved_dimensions) == 7

    def test_does_not_assert_universal_coverage(self) -> None:
        # Calling consider_fallback for one Series says nothing about any other Series --
        # no global/aggregate state exists in this module.
        import inspect

        assert "series_id" not in inspect.signature(consider_fallback).parameters


class TestD5DiagnosticQualifierOnly:
    def test_429_qualifies_as_likely_transient(self) -> None:
        assert qualify_failure_diagnostic(429) == FailureDiagnosticQualifier.LIKELY_TRANSIENT

    def test_422_qualifies_as_request_level_anomaly(self) -> None:
        # SLV/UBER/URA/FCX's real Yahoo failure code.
        assert qualify_failure_diagnostic(422) == FailureDiagnosticQualifier.REQUEST_LEVEL_ANOMALY

    def test_404_qualifies_as_not_found_at_provider(self) -> None:
        # The .A/.B/$-series real Yahoo failure code.
        assert qualify_failure_diagnostic(404) == FailureDiagnosticQualifier.NOT_FOUND_AT_PROVIDER

    def test_unrecognized_status_is_unqualified(self) -> None:
        assert qualify_failure_diagnostic(500) == FailureDiagnosticQualifier.UNQUALIFIED
        assert qualify_failure_diagnostic(None) == FailureDiagnosticQualifier.UNQUALIFIED

    def test_qualifier_is_not_a_defect_classification(self) -> None:
        # No member name or return type implies severity, blame, or required action.
        for member in FailureDiagnosticQualifier:
            assert "DEFECT" not in member.value
            assert "BUG" not in member.value
