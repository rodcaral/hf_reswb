"""Phase 1 tests for panel eligibility (D-046).

Tests for:
- include_delisted parameter (boolean, default TRUE)
- staleness_policy (time-local exclusion, provisional max_consecutive_no_trade_days)
- dispersion_threshold (aggregate suppression, provisional configurable value)
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from hf_reswb.application.dispersion_analyzer import (
    compute_dispersion_metrics,
    should_suppress_result,
)
from hf_reswb.application.panel_eligibility_service import (
    compute_panel_eligibility,
    compute_panel_result,
    format_provisional_status,
)
from hf_reswb.application.staleness_detector import detect_stale_series
from hf_reswb.domain.panel import (
    DispersionThreshold,
    ExclusionReason,
    PanelEligibilityParameters,
    ResultStatus,
    StalenessPolicy,
)
from hf_reswb.persistence import connect


def _seed_series(db_path: str, label: str, status: str = "ACTIVE") -> int:
    """Create a test Series."""
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


def _insert_observation(
    db_path: str, series_id: int, observed_at: str, value: float, volume: float = 100.0
) -> None:
    """Insert an observation."""
    conn = sqlite3.connect(db_path)
    try:
        now = datetime.now(timezone.utc).isoformat()

        # Ensure provider and assignment exist
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
            "SELECT id FROM provider_assignment WHERE series_id=? LIMIT 1",
            (series_id,),
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
            "SELECT id FROM import_run WHERE provider_assignment_id=? LIMIT 1",
            (assignment_id,),
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


class TestIncludeDelisted:
    """Test include_delisted parameter."""

    def test_include_delisted_true_includes_discontinued_series(self, histfints_copy, tmp_path):
        """When include_delisted=TRUE, discontinued Series retain observations."""
        # Create two series: one ACTIVE, one DELISTED
        active_id = _seed_series(histfints_copy, "ACTIVE_SERIES", "ACTIVE")
        delisted_id = _seed_series(histfints_copy, "DELISTED_SERIES", "DELISTED_OR_DISCONTINUED")

        # Insert observations for both
        _insert_observation(histfints_copy, active_id, "2020-04-14", 100.0)
        _insert_observation(histfints_copy, delisted_id, "2020-04-14", 50.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters(include_delisted=True)
            # Phase 1 test: skip suitability validation (Phase 2 integration)
            membership = compute_panel_eligibility(
                connection, [active_id, delisted_id], "2020-04-14", params, validate_suitability=False
            )

            # Both should be included
            assert membership.total_eligible == 2
            assert active_id in membership.included_series_ids
            assert delisted_id in membership.included_series_ids
        finally:
            connection.close()

    def test_include_delisted_false_excludes_discontinued_series(self, histfints_copy, tmp_path):
        """When include_delisted=FALSE, discontinued Series are excluded."""
        active_id = _seed_series(histfints_copy, "ACTIVE", "ACTIVE")
        delisted_id = _seed_series(histfints_copy, "DELISTED", "DELISTED_OR_DISCONTINUED")

        _insert_observation(histfints_copy, active_id, "2020-04-14", 100.0)
        _insert_observation(histfints_copy, delisted_id, "2020-04-14", 50.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters(include_delisted=False)
            # Phase 1 test: skip suitability validation (Phase 2 integration)
            membership = compute_panel_eligibility(
                connection, [active_id, delisted_id], "2020-04-14", params, validate_suitability=False
            )

            # Only active should be included
            assert membership.total_eligible == 1
            assert active_id in membership.included_series_ids
            assert delisted_id not in membership.included_series_ids

            # Exclusion should have reason DELISTED
            exclusions = [e for e in membership.excluded_records if e.series_id == delisted_id]
            assert len(exclusions) == 1
            assert exclusions[0].reason == ExclusionReason.DELISTED
        finally:
            connection.close()


class TestStalenessPolicy:
    """Test staleness_policy parameter (time-local exclusion)."""

    def test_staleness_time_local_not_retroactive(self, histfints_copy, tmp_path):
        """Series excluded from stale date onward, not retroactively."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        # Observations: up to 2020-04-10
        _insert_observation(histfints_copy, series_id, "2020-04-08", 100.0)
        _insert_observation(histfints_copy, series_id, "2020-04-09", 101.0)
        _insert_observation(histfints_copy, series_id, "2020-04-10", 102.0)
        # Gap: 2020-04-11 to 2020-04-20 (10 days)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            policy = StalenessPolicy(max_consecutive_no_trade_days=5)
            params = PanelEligibilityParameters(staleness_policy=policy)

            # On 2020-04-14 (4 days since last obs), not stale yet
            # Phase 1 test: skip suitability validation (Phase 2 integration)
            membership_14 = compute_panel_eligibility(
                connection, [series_id], "2020-04-14", params, validate_suitability=False
            )
            assert series_id in membership_14.included_series_ids

            # On 2020-04-16 (6 days since last obs), now stale
            membership_16 = compute_panel_eligibility(
                connection, [series_id], "2020-04-16", params, validate_suitability=False
            )
            assert series_id not in membership_16.included_series_ids
            assert len(membership_16.excluded_records) == 1
            assert membership_16.excluded_records[0].reason == ExclusionReason.STALE
        finally:
            connection.close()

    def test_staleness_resume_when_trade_resumes(self, histfints_copy, tmp_path):
        """Series re-enters panel when trading resumes after staleness."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        # Observations: early data, then gap, then new observation
        _insert_observation(histfints_copy, series_id, "2020-04-08", 100.0)
        _insert_observation(histfints_copy, series_id, "2020-04-09", 101.0)
        _insert_observation(histfints_copy, series_id, "2020-04-10", 102.0)
        # Gap: 2020-04-11 to 2020-04-20 (10 days)
        _insert_observation(histfints_copy, series_id, "2020-04-21", 105.0)  # Trading resumes

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            policy = StalenessPolicy(max_consecutive_no_trade_days=5)
            params = PanelEligibilityParameters(staleness_policy=policy)

            # On 2020-04-16, stale (6 days since last obs on 04-10)
            membership_16 = compute_panel_eligibility(
                connection, [series_id], "2020-04-16", params, validate_suitability=False, check_coverage=False, check_adjustment_basis=False
            )
            assert series_id not in membership_16.included_series_ids

            # On 2020-04-21, trading has resumed (0 days since observation ON 04-21), should be included
            membership_21 = compute_panel_eligibility(
                connection, [series_id], "2020-04-21", params, validate_suitability=False, check_coverage=False, check_adjustment_basis=False
            )
            assert series_id in membership_21.included_series_ids
        finally:
            connection.close()


class TestDispersionThreshold:
    """Test dispersion_threshold parameter (aggregate suppression)."""

    def test_dispersion_suppression(self):
        """When dispersion exceeds threshold, result is SUPPRESSED."""
        member_residuals = [0.005, -0.002, 0.002, -0.001]

        # Compute dispersion
        metrics = compute_dispersion_metrics(member_residuals)
        cv = metrics.coefficient_of_variation

        # Verify suppression logic: if computed CV is high, any low threshold should suppress
        high_threshold = cv + 0.1  # threshold > cv: don't suppress
        low_threshold = cv - 0.1   # threshold < cv: suppress

        assert should_suppress_result(cv, threshold=high_threshold) is False
        assert should_suppress_result(cv, threshold=low_threshold) is True

    def test_suppression_preserves_diagnostics(self, histfints_copy, tmp_path):
        """Suppressed result preserves underlying observations and diagnostics."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")
        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            params = PanelEligibilityParameters(
                staleness_policy=StalenessPolicy(max_consecutive_no_trade_days=10),
                dispersion_threshold=DispersionThreshold(threshold_value=0.01),
            )

            # Phase 1 test: skip suitability validation (Phase 2 integration)
            membership = compute_panel_eligibility(
                connection, [series_id], "2020-04-14", params, validate_suitability=False
            )

            # High dispersion (simulated)
            member_rates = [100.0, 120.0]  # 20% spread
            member_residuals = [0.0909, -0.0909]

            result = compute_panel_result(
                connection, membership, params, member_rates, member_residuals
            )

            # Result should be suppressed
            assert result.is_suppressed
            assert result.consensus_rate is None  # Not published

            # But diagnostics are preserved
            assert result.member_rates == member_rates
            assert len(result.member_residuals) == 2
            assert result.dispersion_metric > 0
        finally:
            connection.close()


class TestProvisionalStatus:
    """Test that provisional parameters are clearly marked."""

    def test_provisional_status_visible_in_format(self):
        """Provisional parameters are marked in formatted output."""
        params = PanelEligibilityParameters(
            staleness_policy=StalenessPolicy(max_consecutive_no_trade_days=10),
            dispersion_threshold=DispersionThreshold(threshold_value=0.05),
        )

        status_str = format_provisional_status(params)

        assert "PROVISIONAL" in status_str
        assert "10" in status_str
        assert "0.05" in status_str


class TestPanelResultTraceability:
    """Test that panel results maintain full traceability."""

    def test_panel_result_includes_parameters(self, histfints_copy, tmp_path):
        """Panel result records the parameters that produced it."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")
        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            policy = StalenessPolicy(max_consecutive_no_trade_days=10)
            threshold = DispersionThreshold(threshold_value=0.05)
            params = PanelEligibilityParameters(
                include_delisted=True,
                staleness_policy=policy,
                dispersion_threshold=threshold,
            )

            # Phase 1 test: skip suitability validation (Phase 2 integration)
            membership = compute_panel_eligibility(
                connection, [series_id], "2020-04-14", params, validate_suitability=False
            )

            result = compute_panel_result(
                connection,
                membership,
                params,
                member_rates=[100.0],
                member_residuals=[0.0],
            )

            # Result should record parameters
            assert result.parameters_used == params
            assert result.membership == membership
        finally:
            connection.close()
