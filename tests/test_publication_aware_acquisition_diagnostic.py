"""Focused end-to-end tests for the INC-3 publication-aware acquisition-history diagnostic.

`_REAL_2020_03_30_SESSIONS` is captured verbatim from the live, authoritative HistFinTS
evidence: `python -m histfints byma-trading-sessions --from 2020-03-25 --to 2020-04-05`
(2026-08-29) -- BYMA Comunicado N. 17581, both records `is_authoritative: true`
(2020-03-30 independently ACCEPTED; 2020-03-31 NOT_REQUIRED, no qualification/conflict).
`AcquisitionEvidenceView` exposes these to a caller as `BymaSessionRecordEvidence` (session_date,
session_status, evidence_tier, source_reference) -- the shape mirrored below.
"""
from datetime import date

import pytest

from hf_reswb.application.publication_aware_acquisition_diagnostic import (
    PublicationAwareAcquisitionDiagnostic,
    SessionsElapsedStatus,
    diagnose_inc3_acquisition_gap,
    diagnose_inc3_for_snapshot,
)

_REAL_2020_03_30_SESSIONS = [
    {
        "session_date": "2020-03-30",
        "session_status": "TRADING",
        "evidence_tier": "CIRCULAR_NOTICE",
        "source_reference": "BYMA Comunicado N. 17581",
    },
    {
        "session_date": "2020-03-31",
        "session_status": "NON_TRADING",
        "evidence_tier": "CIRCULAR_NOTICE",
        "source_reference": (
            "BYMA Comunicado N. 17581 (Ref.: 30/03 actividad habitual - 31/03 feriado bursatil)"
        ),
    },
]


def _byma_assignment(**overrides) -> dict:
    defaults = dict(
        provider_assignment_id=11369,
        provider_id=99,
        provider_name="BYMA",
        priority=2,
        provider_series_identifier="MU",
        adjustment_basis_provider_default="RAW",
        adjustment_basis_override=None,
        adjustment_basis_effective="RAW",
        adjustment_basis_source="provider_default",
        latest_import={
            "import_run_id": 500,
            "status": "SUCCESS",
            "trigger_type": "SCHEDULED",
            "started_at": "2020-03-30T20:45:00+00:00",
            "ended_at": "2020-03-30T20:45:10+00:00",
            "errors": [],
        },
        run_history=[],
        elapsed_since_last_success_seconds=200_000_000.0,
        byma_applicable=True,
        byma_session_coverage=None,
    )
    defaults.update(overrides)
    return defaults


def _coverage(**overrides) -> dict:
    defaults = dict(
        range_start="2020-03-30",
        range_end="2020-03-31",
        total_days=2,
        known_days=2,
        coverage_complete=True,
        sessions=_REAL_2020_03_30_SESSIONS,
        note="Only independently-authoritative curated records are included.",
    )
    defaults.update(overrides)
    return defaults


def _snapshot(**overrides) -> dict:
    defaults = dict(
        series_id=11323,
        series_label="Micron Technology, Inc. CEDEAR (BYMA)",
        series_status="ACTIVE",
        configured_interval="1h",
        assignments=[],
        provenance={"total_observations": 0, "origin_established_observations": 0, "note": ""},
        identity={"evaluated": False, "note": ""},
        non_production_status={"value": None, "note": ""},
        coverage_quality={
            "first_available_date": None, "last_available_date": None, "note": "", "integrity_audit_note": "",
        },
        comparability={"computed": False, "note": ""},
        merval_assignment_present=False,
        merval_note="",
    )
    defaults.update(overrides)
    return defaults


# --- Population boundary: None for anything outside INC-3's first bounded scope --------------


class TestPopulationBoundary:
    def test_non_stock_series_returns_none_even_when_byma_applicable(self) -> None:
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(byma_applicable=True), series_type="ETF"
        )
        assert result is None

    def test_non_byma_assignment_returns_none_even_for_a_stock_series(self) -> None:
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(byma_applicable=False), series_type="STOCK"
        )
        assert result is None

    def test_neither_stock_nor_byma_returns_none(self) -> None:
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(byma_applicable=False), series_type="ETF"
        )
        assert result is None


# --- No successful run: distinct from an unmeasurable-but-real gap ---------------------------


class TestNoSuccessfulRun:
    def test_none_elapsed_yields_no_successful_run_status(self) -> None:
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(elapsed_since_last_success_seconds=None, latest_import=None),
            series_type="STOCK",
        )
        assert result.sessions_elapsed_status == SessionsElapsedStatus.UNAVAILABLE_NO_SUCCESSFUL_RUN
        assert result.raw_elapsed_since_last_success_seconds is None
        assert result.sessions_elapsed is None
        assert result.session_evidence_range is None


# --- Insufficient session evidence: the honest default given today's sparse curation ----------


class TestInsufficientSessionEvidence:
    def test_no_coverage_object_at_all(self) -> None:
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(byma_session_coverage=None), series_type="STOCK"
        )
        assert result.sessions_elapsed_status == (
            SessionsElapsedStatus.UNAVAILABLE_INSUFFICIENT_SESSION_EVIDENCE
        )
        assert result.raw_elapsed_since_last_success_seconds == 200_000_000.0
        assert result.sessions_elapsed is None
        assert result.session_evidence_range is None

    def test_coverage_present_but_incomplete(self) -> None:
        """The realistic case for almost any real series today: a run-history span that only
        partially overlaps the two curated 2020 dates."""
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(
                byma_session_coverage=_coverage(
                    range_start="2020-03-28",
                    range_end="2020-04-02",
                    total_days=6,
                    known_days=2,
                    coverage_complete=False,
                )
            ),
            series_type="STOCK",
        )
        assert result.sessions_elapsed_status == (
            SessionsElapsedStatus.UNAVAILABLE_INSUFFICIENT_SESSION_EVIDENCE
        )
        assert result.sessions_elapsed is None
        assert result.session_evidence_known_days == 2
        assert result.session_evidence_total_days == 6
        # raw evidence stays available even though the session-aware count does not
        assert result.raw_elapsed_since_last_success_seconds == 200_000_000.0


# --- Available: the real, accepted 2020-03-30/31 evidence, end to end -------------------------


class TestAvailableWithRealEvidence:
    def test_complete_coverage_over_the_real_accepted_evidence(self) -> None:
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(byma_session_coverage=_coverage()), series_type="STOCK"
        )
        assert result.sessions_elapsed_status == SessionsElapsedStatus.AVAILABLE
        assert result.sessions_elapsed == 1  # only 2020-03-30 is TRADING
        assert result.special_limited_sessions_elapsed == 0
        assert result.session_evidence_range == (date(2020, 3, 30), date(2020, 3, 31))
        assert result.session_evidence_known_days == 2
        assert result.session_evidence_total_days == 2
        assert result.raw_elapsed_since_last_success_seconds == 200_000_000.0

    def test_special_limited_sessions_counted_separately_not_blended(self) -> None:
        sessions_with_special = _REAL_2020_03_30_SESSIONS + [
            {
                "session_date": "2020-04-01",
                "session_status": "SPECIAL_LIMITED",
                "evidence_tier": "CIRCULAR_NOTICE",
                "source_reference": "synthetic -- no real SPECIAL_LIMITED record exists yet",
            }
        ]
        result = diagnose_inc3_acquisition_gap(
            _byma_assignment(
                byma_session_coverage=_coverage(
                    range_end="2020-04-01", total_days=3, known_days=3, sessions=sessions_with_special
                )
            ),
            series_type="STOCK",
        )
        assert result.sessions_elapsed == 1
        assert result.special_limited_sessions_elapsed == 1


# --- Distinctness: acquisition gap vs. missing observation, enforced structurally -------------


class TestKeepsAcquisitionGapDistinctFromObservationGap:
    def test_dataclass_carries_no_observation_or_provenance_field(self) -> None:
        field_names = {f for f in PublicationAwareAcquisitionDiagnostic.__dataclass_fields__}
        assert not any("observation" in f or "provenance" in f for f in field_names)

    def test_diagnostic_functions_never_read_the_provenance_key(self) -> None:
        """AST-based, not a grep claim: neither function subscripts `"provenance"` on its input."""
        import ast
        import inspect

        import hf_reswb.application.publication_aware_acquisition_diagnostic as module

        tree = ast.parse(inspect.getsource(module))
        string_constants = {
            node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        assert "provenance" not in string_constants


# --- Orchestration -----------------------------------------------------------------------------


class TestDiagnoseForSnapshot:
    def test_filters_to_only_byma_applicable_assignments_on_a_stock_series(self) -> None:
        snapshot = _snapshot(
            assignments=[
                _byma_assignment(
                    provider_assignment_id=1, byma_applicable=True, byma_session_coverage=_coverage()
                ),
                _byma_assignment(
                    provider_assignment_id=2, provider_name="Yahoo Finance", byma_applicable=False
                ),
            ]
        )
        result = diagnose_inc3_for_snapshot(snapshot, series_type="STOCK")
        assert len(result) == 1
        assert result[0].provider_assignment_id == 1
        assert result[0].sessions_elapsed_status == SessionsElapsedStatus.AVAILABLE

    def test_non_stock_series_yields_no_diagnostics_at_all(self) -> None:
        snapshot = _snapshot(
            assignments=[_byma_assignment(byma_applicable=True, byma_session_coverage=_coverage())]
        )
        result = diagnose_inc3_for_snapshot(snapshot, series_type="ETF")
        assert result == ()

    def test_zero_assignments_yields_empty_tuple(self) -> None:
        assert diagnose_inc3_for_snapshot(_snapshot(), series_type="STOCK") == ()


# --- Structural guardrails: no threshold, no mutation, no fallback ----------------------------


class TestNoProhibitedBehavior:
    def test_no_write_or_mutation_primitive_imported(self) -> None:
        import ast
        import inspect

        import hf_reswb.application.publication_aware_acquisition_diagnostic as module

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

    def test_no_stale_or_ok_verdict_type_referenced(self) -> None:
        """This module must never read or write import_state.py's STALE/OK vocabulary --
        checked via the AST so this module's own docstring (which names STALE/OK only to
        disclaim them) doesn't trip the assertion."""
        import ast
        import inspect

        import hf_reswb.application.publication_aware_acquisition_diagnostic as module

        tree = ast.parse(inspect.getsource(module))
        names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        string_constants = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        assert "ImportState" not in names
        assert not any(c in ("STALE", "OK") for c in string_constants)

    def test_no_numeric_threshold_constant_defined_at_module_level(self) -> None:
        """No margin/tolerance/threshold value is invented anywhere in this module -- every
        number it produces is a count read directly off supplied evidence."""
        import ast
        import inspect

        import hf_reswb.application.publication_aware_acquisition_diagnostic as module

        tree = ast.parse(inspect.getsource(module))
        module_level_assignments = [
            node for node in tree.body if isinstance(node, ast.Assign)
        ]
        assert module_level_assignments == []
