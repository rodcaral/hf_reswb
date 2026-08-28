"""Acceptance tests for the F-009 evidence-consumption increment
(SPEC_F009_EVIDENCE_CONSUMPTION.md §6).

Every test here exercises the real read-only ATTACH boundary (D-001) against a disposable
copy of the actual production database file — never a hand-built fixture schema (D-009b).
"""
from __future__ import annotations

import sqlite3

import pytest

from hf_reswb.application import DetectorParams, reconcile
from hf_reswb.domain import HistFintsObject, ResolutionState, Verdict
from hf_reswb.persistence import connect

from tests.conftest import insert_fixture_series_with_step, insert_fixture_split_event

PARAMS = DetectorParams(step_threshold=0.20, persistence_horizons_days=(15, 60), persistence_tolerance=0.10)


def test_read_only_attach_against_actual_production_file(real_production_db_readonly_path, tmp_path):
    """Proves the boundary against the real thing, not just a same-schema stand-in — read
    only, never copied (the file is multi-gigabyte)."""
    connection = connect(
        tmp_path / "workbench.db", real_production_db_readonly_path, histfints_readonly=True
    )
    try:
        row = connection.execute("PRAGMA histfints.user_version").fetchone()
        assert row[0] >= 10
        with pytest.raises(sqlite3.OperationalError):
            connection.execute(
                "INSERT INTO histfints.provider (display_name, implementation_key, kind, "
                "created_at, updated_at) VALUES ('x', 'x', 'API', 't', 't')"
            )
    finally:
        connection.close()


def test_boundary_rejects_write_to_histfints(histfints_copy, tmp_path):
    """This is a boundary test, not a data test: the application must not be able to write
    to the attached HistFinTS database under any circumstances (D-001)."""
    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        with pytest.raises(sqlite3.OperationalError):
            connection.execute(
                "INSERT INTO histfints.provider (display_name, implementation_key, kind, "
                "created_at, updated_at) VALUES ('x', 'x', 'API', 't', 't')"
            )
    finally:
        connection.close()


def test_insufficient_evidence_when_no_observations_in_period(histfints_copy, tmp_path):
    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        findings = reconcile(connection, series_id=-1, period_start="2020-01-01", period_end="2020-12-31")
    finally:
        connection.close()

    assert len(findings) == 1
    assert findings[0].verdict == Verdict.INSUFFICIENT_EVIDENCE
    assert findings[0].id is not None


def test_not_explained_when_correction_table_has_nothing_and_event_tables_absent(histfints_copy, tmp_path):
    """The reachable case against today's actual production schema (D-033): a real
    discontinuity, checked against the one evidence source that exists (`correction`), and
    found to hold nothing at that date — while `provider_event` and `observation_correction`
    are correctly reported as TABLE_ABSENT rather than silently skipped."""
    fixture = insert_fixture_series_with_step(histfints_copy, label="FIXTURE-NOTEXPLAINED", step_factor=1 / 7)

    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        findings = reconcile(
            connection,
            series_id=fixture["series_id"],
            period_start=fixture["period_start"],
            period_end=fixture["period_end"],
            params=PARAMS,
        )
    finally:
        connection.close()

    assert len(findings) == 1
    finding = findings[0]
    assert finding.verdict == Verdict.NOT_EXPLAINED

    table_absent_objects = {
        ref.histfints_object
        for ref in finding.evidence_consulted
        if ref.resolution_state == ResolutionState.TABLE_ABSENT
    }
    assert HistFintsObject.PROVIDER_EVENT in table_absent_objects
    assert HistFintsObject.OBSERVATION_CORRECTION in table_absent_objects

    # Traceability: the finding must resolve back to the exact affected observations.
    observation_refs = {
        ref.histfints_id
        for ref in finding.evidence_consulted
        if ref.histfints_object == HistFintsObject.OBSERVATION
    }
    assert fixture["boundary_observation_id"] in observation_refs


def test_explained_when_migrated_and_captured_event_reconciles(histfints_copy_migrated, tmp_path):
    """`explained by captured evidence` can only be tested against a fixture with migrations
    0011-0013 applied (SPEC §6) — it is structurally unreachable against production today
    (D-032, D-033). If this ever returns EXPLAINED against an unmigrated copy, that is a
    reconciler defect, not a success."""
    fixture = insert_fixture_series_with_step(
        histfints_copy_migrated, label="FIXTURE-EXPLAINED", step_factor=1 / 7
    )
    insert_fixture_split_event(
        histfints_copy_migrated,
        series_id=fixture["series_id"],
        provider_id=fixture["provider_id"],
        event_date=fixture["boundary_date"],
        ratio=7.0,
    )

    connection = connect(tmp_path / "workbench.db", histfints_copy_migrated, histfints_readonly=True)
    try:
        findings = reconcile(
            connection,
            series_id=fixture["series_id"],
            period_start=fixture["period_start"],
            period_end=fixture["period_end"],
            params=PARAMS,
        )
    finally:
        connection.close()

    assert len(findings) == 1
    finding = findings[0]
    assert finding.verdict == Verdict.EXPLAINED
    assert finding.residual is not None and finding.residual <= PARAMS.persistence_tolerance

    event_refs = [
        ref for ref in finding.evidence_consulted if ref.histfints_object == HistFintsObject.PROVIDER_EVENT
    ]
    assert any(ref.resolution_state == ResolutionState.RESOLVED for ref in event_refs)
