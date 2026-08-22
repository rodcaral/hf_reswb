"""Tests for the D1-D5 acquisition-quality capability model.

Fixtures grounded in real cases from ACQUISITION_QUALITY_INVENTORY_2026-08-22.md: the 32-Series
1h cadence gap (D1), the 61-Series .{dollar} identifier-format failures and the SLV/UBER/URA
dual-path-failing pattern (D2/D5), the two NEVER sub-populations including the test fixtures
(D3), and the already-documented Class-C orphans (D3, not reinterpreted).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from hf_reswb.application.acquisition_quality_capability import (
    CadenceCapabilityVerdict,
    FailureDiagnosticQualifier,
    FallbackCandidateEvidence,
    FallbackConsiderationVerdict,
    IdentifierCompatibilityVerdict,
    NeverStateReason,
    RunOutcome,
    assess_cadence_capability,
    assess_identifier_compatibility,
    classify_never_state,
    consider_fallback,
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

    def test_warranted_adequate_when_all_six_dimensions_true(self) -> None:
        evidence = FallbackCandidateEvidence(
            identity_compatible=True, history_available=True,
            adjustment_convention_documented=True, coverage_adequate=True,
            provenance_acceptable=True, quality_acceptable=True,
        )
        result = consider_fallback(material_impact=True, candidate_evidence=evidence)
        assert result.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_ADEQUATE
        assert result.unresolved_dimensions == ()

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

    def test_no_candidate_evidence_lists_all_six_unresolved(self) -> None:
        result = consider_fallback(material_impact=True, candidate_evidence=None)
        assert result.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_INADEQUATE
        assert len(result.unresolved_dimensions) == 6

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
