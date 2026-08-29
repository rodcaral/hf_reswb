"""Contract/integration tests for `acquisition_evidence_integration.py` -- the production caller
wiring HistFinTS's `AcquisitionEvidenceSnapshot` contract into the existing D1-D4 classifiers.

Fixture dicts below mirror the exact JSON shape `dataclasses.asdict(AcquisitionEvidenceSnapshot)`
produces (verified against `histfints/application/acquisition_evidence_view.py`, 2026-08-29) --
field names and nesting match the real contract, not a simplified stand-in.
"""
from datetime import timedelta
import json

import pytest

from hf_reswb.application.acquisition_evidence_integration import (
    AcquisitionQualityClassification,
    assemble_d1_successful_run_timestamps,
    assemble_d2_outcomes,
    assemble_d4_candidate_evidence,
    classify_acquisition_quality,
    classify_d1,
    classify_d2,
    classify_d3,
    classify_d4,
    load_snapshot,
)
from hf_reswb.application.acquisition_quality_capability import (
    AcquisitionQualityPopulationMembership,
    CadenceCapabilityVerdict,
    FallbackConsiderationVerdict,
    FixtureConfirmation,
    IdentifierCompatibilityVerdict,
    NeverStateReason,
    NonProductionFixtureStatus,
    RunOutcome,
)


def _assignment(**overrides) -> dict:
    defaults = dict(
        provider_assignment_id=1,
        provider_id=2,
        provider_name="Yahoo Finance",
        priority=1,
        provider_series_identifier="AAPL",
        adjustment_basis_provider_default="SPLIT_ADJUSTED",
        adjustment_basis_override=None,
        adjustment_basis_effective="SPLIT_ADJUSTED",
        adjustment_basis_source="provider_default",
        latest_import=None,
    )
    defaults.update(overrides)
    return defaults


def _latest_import(**overrides) -> dict:
    defaults = dict(
        import_run_id=99,
        status="SUCCESS",
        trigger_type="SCHEDULED",
        started_at="2026-08-20T17:00:00+00:00",
        ended_at="2026-08-20T17:00:05+00:00",
        errors=[],
    )
    defaults.update(overrides)
    return defaults


def _snapshot(**overrides) -> dict:
    defaults = dict(
        series_id=11323,
        series_label="Apple Inc.",
        series_status="ACTIVE",
        configured_interval="1d",
        assignments=[],
        provenance={
            "total_observations": 100,
            "origin_established_observations": 80,
            "note": "...",
        },
        identity={"evaluated": False, "note": "..."},
        non_production_status={"value": None, "note": "..."},
        coverage_quality={
            "first_available_date": None,
            "last_available_date": None,
            "note": "...",
            "integrity_audit_note": "...",
        },
        comparability={"computed": False, "note": "..."},
    )
    defaults.update(overrides)
    return defaults


# --- load_snapshot -------------------------------------------------------------------------


class TestLoadSnapshot:
    def test_accepts_a_dict_directly(self) -> None:
        assert load_snapshot(_snapshot())["series_id"] == 11323

    def test_accepts_a_raw_json_string(self) -> None:
        assert load_snapshot(json.dumps(_snapshot()))["series_id"] == 11323

    def test_accepts_a_file_path(self, tmp_path) -> None:
        p = tmp_path / "snapshot.json"
        p.write_text(json.dumps(_snapshot()), encoding="utf-8")
        assert load_snapshot(p)["series_id"] == 11323
        assert load_snapshot(str(p))["series_id"] == 11323

    def test_missing_required_key_raises_not_silently_proceeds(self) -> None:
        broken = _snapshot()
        del broken["coverage_quality"]
        with pytest.raises(ValueError, match="coverage_quality"):
            load_snapshot(broken)


# --- D3: fully operational -------------------------------------------------------------------


class TestD3:
    def test_no_assignments_not_superseded_not_fixture_like(self) -> None:
        result = classify_d3(_snapshot(series_label="Apple Inc.", assignments=[]))
        assert result.fixture_status == NonProductionFixtureStatus.NOT_A_FIXTURE
        assert result.population_membership == (
            AcquisitionQualityPopulationMembership.INCLUDED_ACQUISITION_CANDIDATE
        )
        assert result.never_state_reason == NeverStateReason.NO_PROVIDER_ASSIGNMENT

    def test_assigned_but_never_run(self) -> None:
        result = classify_d3(
            _snapshot(assignments=[_assignment(latest_import=None)])
        )
        assert result.never_state_reason == NeverStateReason.ASSIGNED_NOT_YET_RUN

    def test_has_run_clears_never_state(self) -> None:
        result = classify_d3(
            _snapshot(assignments=[_assignment(latest_import=_latest_import())])
        )
        assert result.never_state_reason is None

    def test_superseded_excludes_unconditionally_even_without_a_fixture_label(self) -> None:
        result = classify_d3(_snapshot(series_status="SUPERSEDED", series_label="Apple Inc."))
        assert result.population_membership == (
            AcquisitionQualityPopulationMembership.EXCLUDED_SUPERSEDED
        )
        assert result.never_state_reason == NeverStateReason.SUPERSEDED_NOT_CURRENT_ATTRIBUTION

    def test_superseded_with_a_run_on_record_still_excludes_but_never_state_is_none(self) -> None:
        result = classify_d3(
            _snapshot(
                series_status="SUPERSEDED",
                assignments=[_assignment(latest_import=_latest_import())],
            )
        )
        assert result.population_membership == (
            AcquisitionQualityPopulationMembership.EXCLUDED_SUPERSEDED
        )
        assert result.never_state_reason is None

    def test_fixture_like_label_stays_unconfirmed_by_default(self) -> None:
        result = classify_d3(_snapshot(series_label="GLD Smoke Test CEDEAR"))
        assert result.fixture_status == NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED
        assert result.population_membership == (
            AcquisitionQualityPopulationMembership.INCLUDED_PENDING_FIXTURE_REVIEW
        )

    def test_real_production_label_never_flagged_by_the_heuristic(self) -> None:
        """Regression guard matching the fixture heuristic's own known false-positive risk
        (this exact case -- 'DuPont de Nemours' matching a naive '%dup%' check -- is named in
        HistFinTS's own acquisition_evidence_view.py docstring)."""
        result = classify_d3(_snapshot(series_label="DuPont de Nemours"))
        assert result.fixture_status == NonProductionFixtureStatus.NOT_A_FIXTURE

    def test_explicit_confirmation_reaches_confirmed_exclusion(self) -> None:
        confirmation = FixtureConfirmation(
            confirmed_by="rgc", confirmed_at="2026-08-29", reason="known smoke-test series"
        )
        result = classify_d3(
            _snapshot(series_label="Duplicate Warning Test"), fixture_confirmation=confirmation
        )
        assert result.fixture_status == NonProductionFixtureStatus.CONFIRMED_FIXTURE
        assert result.population_membership == (
            AcquisitionQualityPopulationMembership.EXCLUDED_CONFIRMED_FIXTURE
        )

    def test_fixture_heuristic_reads_the_first_assignments_identifier(self) -> None:
        """Documents the current, deliberately narrow scope: only assignments[0]'s identifier is
        consulted (matching the label-plus-one-identifier shape `looks_like_non_production_
        fixture()` was designed for) -- not a claim that every assignment is checked."""
        result = classify_d3(
            _snapshot(
                series_label="Apple Inc.",
                assignments=[_assignment(provider_series_identifier="bulk-verify-tmp")],
            )
        )
        assert result.fixture_status == NonProductionFixtureStatus.CANDIDATE_UNCONFIRMED


# --- D2: operational, single-sample evidence only ---------------------------------------------


class TestD2:
    def test_no_run_yet_is_insufficient_evidence(self) -> None:
        assert assemble_d2_outcomes(_assignment(latest_import=None)) == []
        assert (
            classify_d2(_assignment(latest_import=None)).verdict
            == IdentifierCompatibilityVerdict.INSUFFICIENT_EVIDENCE
        )

    def test_single_success_resolves(self) -> None:
        a = _assignment(latest_import=_latest_import(status="SUCCESS"))
        assert assemble_d2_outcomes(a) == [RunOutcome.SUCCESS]
        assert classify_d2(a).verdict == IdentifierCompatibilityVerdict.RESOLVED

    def test_single_failure_is_consistently_unresolved_on_one_sample(self) -> None:
        a = _assignment(latest_import=_latest_import(status="FAILED"))
        assert classify_d2(a).verdict == IdentifierCompatibilityVerdict.CONSISTENTLY_UNRESOLVED
        assert classify_d2(a).attempt_count == 1

    @pytest.mark.parametrize("status", ["PARTIAL", "IN_PROGRESS"])
    def test_partial_and_in_progress_are_excluded_not_forced_into_a_binary_outcome(
        self, status
    ) -> None:
        a = _assignment(latest_import=_latest_import(status=status))
        assert assemble_d2_outcomes(a) == []
        assert classify_d2(a).verdict == IdentifierCompatibilityVerdict.INSUFFICIENT_EVIDENCE


# --- D1: wired but structurally not operational from this contract ----------------------------


class TestD1:
    def test_no_run_is_insufficient_evidence(self) -> None:
        result = classify_d1(_assignment(latest_import=None), tolerance=timedelta(days=3))
        assert result.verdict == CadenceCapabilityVerdict.INSUFFICIENT_EVIDENCE
        assert result.observed_gap_count == 0

    def test_single_successful_run_still_insufficient_evidence(self) -> None:
        """The structural limitation this contract has today: one timestamp cannot produce a
        gap, and even a genuine gap wouldn't clear the classifier's own min_samples=3 floor."""
        a = _assignment(latest_import=_latest_import(status="SUCCESS"))
        assert len(assemble_d1_successful_run_timestamps(a)) == 1
        result = classify_d1(a, tolerance=timedelta(days=3))
        assert result.verdict == CadenceCapabilityVerdict.INSUFFICIENT_EVIDENCE

    def test_failed_run_contributes_no_timestamp(self) -> None:
        a = _assignment(latest_import=_latest_import(status="FAILED"))
        assert assemble_d1_successful_run_timestamps(a) == []


# --- D4: operational, six of seven dimensions structurally unavailable ------------------------


class TestD4:
    def test_only_adjustment_convention_is_ever_populated(self) -> None:
        evidence = assemble_d4_candidate_evidence(
            _assignment(adjustment_basis_source="provider_default")
        )
        assert evidence.adjustment_convention_documented is True
        assert evidence.identity_compatible is None
        assert evidence.history_available is None
        assert evidence.coverage_adequate is None
        assert evidence.provenance_acceptable is None
        assert evidence.quality_acceptable is None
        assert evidence.comparability_acceptable is None

    def test_unavailable_adjustment_basis_source_maps_to_false_not_none(self) -> None:
        """`adjustment_basis_source == "unavailable"` is itself a real, observed fact -- distinct
        from "we don't know" -- so it must map to `False`, not `None`."""
        evidence = assemble_d4_candidate_evidence(
            _assignment(adjustment_basis_source="unavailable")
        )
        assert evidence.adjustment_convention_documented is False

    def test_materiality_unknown_by_default_regardless_of_candidate_evidence(self) -> None:
        result = classify_d4(_assignment(adjustment_basis_source="provider_default"))
        assert result.verdict == FallbackConsiderationVerdict.MATERIALITY_UNKNOWN

    def test_material_but_six_dimensions_unavailable_is_inadequate_not_adequate(self) -> None:
        result = classify_d4(
            _assignment(adjustment_basis_source="provider_default"), material_impact=True
        )
        assert result.verdict == FallbackConsiderationVerdict.WARRANTED_CANDIDATE_INADEQUATE
        assert "coverage_adequate" in result.unresolved_dimensions
        assert "adjustment_convention_documented" not in result.unresolved_dimensions


# --- Orchestration --------------------------------------------------------------------------


class TestClassifyAcquisitionQuality:
    def test_full_snapshot_wires_all_four_classifiers_per_assignment(self) -> None:
        snapshot = _snapshot(
            series_id=11323,
            assignments=[
                _assignment(
                    provider_assignment_id=1,
                    latest_import=_latest_import(status="SUCCESS"),
                ),
                _assignment(
                    provider_assignment_id=2,
                    provider_name="Alpha Vantage",
                    adjustment_basis_source="unavailable",
                    latest_import=_latest_import(status="FAILED"),
                ),
            ],
        )

        result = classify_acquisition_quality(snapshot, cadence_tolerance=timedelta(days=3))

        assert isinstance(result, AcquisitionQualityClassification)
        assert result.series_id == 11323
        assert result.d3.population_membership == (
            AcquisitionQualityPopulationMembership.INCLUDED_ACQUISITION_CANDIDATE
        )
        assert len(result.assignments) == 2
        assert result.assignments[0].d2.verdict == IdentifierCompatibilityVerdict.RESOLVED
        assert result.assignments[1].d2.verdict == (
            IdentifierCompatibilityVerdict.CONSISTENTLY_UNRESOLVED
        )
        assert result.assignments[0].d1.verdict == CadenceCapabilityVerdict.INSUFFICIENT_EVIDENCE
        assert result.assignments[1].d4.verdict == FallbackConsiderationVerdict.MATERIALITY_UNKNOWN

    def test_zero_assignments_still_returns_a_complete_result(self) -> None:
        result = classify_acquisition_quality(_snapshot(), cadence_tolerance=timedelta(days=3))
        assert result.assignments == ()
        assert result.d3.never_state_reason == NeverStateReason.NO_PROVIDER_ASSIGNMENT


# --- Structural guardrails, matching this module's own no-mutation/no-activation claims -------


class TestNoProductionMutationOrActivation:
    def test_module_never_references_the_activation_function(self) -> None:
        """`evaluate_fallback_activation()` -- the one function in acquisition_quality_
        capability.py capable of reaching an `ACTIVATED` verdict -- is never imported or called
        here. This module only ever reaches `consider_fallback()`, which cannot activate
        anything regardless of its inputs."""
        import hf_reswb.application.acquisition_evidence_integration as module

        assert "evaluate_fallback_activation" not in dir(module)

    def test_module_performs_no_database_or_network_access(self) -> None:
        """`load_snapshot()`'s only I/O is a local file read of an already-produced JSON
        artifact -- confirmed via the AST (docstring prose is excluded, so this checks actual
        code, not this module's own explanation of what it deliberately doesn't do)."""
        import ast
        import inspect

        import hf_reswb.application.acquisition_evidence_integration as module

        tree = ast.parse(inspect.getsource(module))
        imported_names = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        } | {
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert imported_names.isdisjoint({"sqlite3", "subprocess", "requests", "urllib", "socket"})
