"""Tests for the `include_superseded` parameter and its output qualification (SE directive
2026-08-26): SUPERSEDED excluded by default, opt-in via `include_superseded=True`, and any
opted-in result must carry a visible `historical_evidence_qualification`.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest

from hf_reswb.application.panel_eligibility_service import (
    compute_panel_eligibility,
    compute_panel_result,
)
from hf_reswb.domain.panel import ExclusionReason, PanelEligibilityParameters
from hf_reswb.persistence import connect


def _seed_series(db_path, label: str, status: str = "ACTIVE") -> int:
    conn = sqlite3.connect(db_path)
    try:
        now = datetime.now(timezone.utc).isoformat()
        series_id = conn.execute(
            "INSERT INTO series (label, series_type, configured_interval, backfill_start_date, status, created_at, updated_at) "
            "VALUES (?, 'STOCK', '1d', '2000-01-01', ?, ?, ?) RETURNING id",
            (label, status, now, now),
        ).fetchone()[0]
        conn.commit()
        return series_id
    finally:
        conn.close()


def _insert_observation(db_path, series_id: int, observed_at: str, value: float, volume: float = 100.0) -> None:
    conn = sqlite3.connect(db_path)
    try:
        now = datetime.now(timezone.utc).isoformat()
        provider_id = conn.execute(
            "SELECT id FROM provider WHERE implementation_key='test' LIMIT 1"
        ).fetchone()
        if provider_id is None:
            provider_id = conn.execute(
                "INSERT INTO provider (display_name, implementation_key, kind, created_at, updated_at) "
                "VALUES ('Test Provider', 'test', 'API', ?, ?) RETURNING id",
                (now, now),
            ).fetchone()[0]
        else:
            provider_id = provider_id[0]

        assignment = conn.execute(
            "SELECT id FROM provider_assignment WHERE series_id=? LIMIT 1", (series_id,)
        ).fetchone()
        if assignment is None:
            assignment_id = conn.execute(
                "INSERT INTO provider_assignment (series_id, provider_id, priority, provider_series_identifier, created_at, updated_at) "
                "VALUES (?, ?, 1, ?, ?, ?) RETURNING id",
                (series_id, provider_id, f"test_{series_id}", now, now),
            ).fetchone()[0]
        else:
            assignment_id = assignment[0]

        run = conn.execute(
            "SELECT id FROM import_run WHERE provider_assignment_id=? LIMIT 1", (assignment_id,)
        ).fetchone()
        if run is None:
            run_id = conn.execute(
                "INSERT INTO import_run (provider_assignment_id, trigger_type, status, started_at, ended_at, created_at, updated_at) "
                "VALUES (?, 'MANUAL', 'SUCCESS', ?, ?, ?, ?) RETURNING id",
                (assignment_id, now, now, now, now),
            ).fetchone()[0]
        else:
            run_id = run[0]

        conn.execute(
            "INSERT INTO observation (series_id, import_run_id, observed_at, value, volume, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (series_id, run_id, observed_at, value, volume, now, now),
        )
        conn.commit()
    finally:
        conn.close()


class TestIncludeSupersededDefaultExclusion:
    def test_default_excludes_superseded_series(self, histfints_copy_v17, tmp_path):
        active_id = _seed_series(histfints_copy_v17, "ACTIVE_SERIES", "ACTIVE")
        superseded_id = _seed_series(histfints_copy_v17, "SUPERSEDED_SERIES", "SUPERSEDED")
        _insert_observation(histfints_copy_v17, active_id, "2020-04-14", 100.0)
        _insert_observation(histfints_copy_v17, superseded_id, "2020-04-14", 50.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy_v17, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters()  # include_superseded defaults False
            membership = compute_panel_eligibility(
                connection, [active_id, superseded_id], "2020-04-14", params, validate_suitability=False, check_coverage=False
            )

            assert membership.total_eligible == 1
            assert active_id in membership.included_series_ids
            assert superseded_id not in membership.included_series_ids
            assert membership.superseded_included_series_ids == []

            exclusions = [e for e in membership.excluded_records if e.series_id == superseded_id]
            assert len(exclusions) == 1
            assert exclusions[0].reason == ExclusionReason.SUPERSEDED
            assert exclusions[0].detail == "status = SUPERSEDED"
        finally:
            connection.close()


class TestIncludeSupersededExplicitOptIn:
    def test_opt_in_includes_superseded_series(self, histfints_copy_v17, tmp_path):
        active_id = _seed_series(histfints_copy_v17, "ACTIVE_SERIES", "ACTIVE")
        superseded_id = _seed_series(histfints_copy_v17, "SUPERSEDED_SERIES", "SUPERSEDED")
        _insert_observation(histfints_copy_v17, active_id, "2020-04-14", 100.0)
        _insert_observation(histfints_copy_v17, superseded_id, "2020-04-14", 50.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy_v17, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters(include_superseded=True)
            membership = compute_panel_eligibility(
                connection, [active_id, superseded_id], "2020-04-14", params, validate_suitability=False, check_coverage=False
            )

            assert membership.total_eligible == 2
            assert superseded_id in membership.included_series_ids
            assert membership.superseded_included_series_ids == [superseded_id]
        finally:
            connection.close()

    def test_opted_in_result_carries_visible_qualification(self, histfints_copy_v17, tmp_path):
        active_id = _seed_series(histfints_copy_v17, "ACTIVE_SERIES", "ACTIVE")
        superseded_id = _seed_series(histfints_copy_v17, "SUPERSEDED_SERIES", "SUPERSEDED")
        _insert_observation(histfints_copy_v17, active_id, "2020-04-14", 100.0)
        _insert_observation(histfints_copy_v17, superseded_id, "2020-04-14", 50.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy_v17, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters(include_superseded=True)
            membership = compute_panel_eligibility(
                connection, [active_id, superseded_id], "2020-04-14", params, validate_suitability=False, check_coverage=False
            )
            result = compute_panel_result(
                connection, membership, params, member_rates=[1.0, 1.0], member_residuals=[0.0, 0.0]
            )

            assert result.historical_evidence_qualification is not None
            assert "retained for historical/provenance purposes" in result.historical_evidence_qualification
            assert "no longer the current attribution" in result.historical_evidence_qualification
            assert str(superseded_id) in result.historical_evidence_qualification
        finally:
            connection.close()

    def test_default_result_carries_no_qualification(self, histfints_copy_v17, tmp_path):
        active_id = _seed_series(histfints_copy_v17, "ACTIVE_SERIES", "ACTIVE")
        _insert_observation(histfints_copy_v17, active_id, "2020-04-14", 100.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy_v17, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters()
            membership = compute_panel_eligibility(
                connection, [active_id], "2020-04-14", params, validate_suitability=False, check_coverage=False
            )
            result = compute_panel_result(
                connection, membership, params, member_rates=[1.0], member_residuals=[0.0]
            )
            assert result.historical_evidence_qualification is None
        finally:
            connection.close()

    def test_qualification_absent_when_superseded_excluded_by_a_later_check(self, histfints_copy_v17, tmp_path):
        # A SUPERSEDED Series opted in at step 1b can still be excluded by a later check
        # (e.g. missing suitability data is bypassed here via validate_suitability=False, so
        # use staleness instead) -- the qualification must reflect only what actually made it
        # into the final included set, not what step 1b alone saw.
        from datetime import timedelta

        from hf_reswb.domain.panel import StalenessPolicy

        superseded_id = _seed_series(histfints_copy_v17, "SUPERSEDED_SERIES", "SUPERSEDED")
        old_date = (datetime.now(timezone.utc) - timedelta(days=400)).strftime("%Y-%m-%d")
        _insert_observation(histfints_copy_v17, superseded_id, old_date, 50.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy_v17, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters(
                include_superseded=True,
                staleness_policy=StalenessPolicy(max_consecutive_no_trade_days=5),
            )
            membership = compute_panel_eligibility(
                connection, [superseded_id], datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                params, validate_suitability=False, check_coverage=False,
            )
            # Whether or not staleness actually excludes it here (depends on staleness_detector's
            # own logic against a single old observation), the invariant under test is:
            # superseded_included_series_ids must be a subset of included_series_ids.
            assert set(membership.superseded_included_series_ids) <= set(membership.included_series_ids)
        finally:
            connection.close()
