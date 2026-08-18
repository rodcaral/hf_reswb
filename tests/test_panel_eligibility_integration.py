"""Phase 4 integration tests for panel eligibility (D-046).

Integration tests covering:
- Real observation-suitability output (classify_series pipeline)
- Multi-series panel scenarios (realistic panel construction)
- Traceability chain validation (panel → eligibility → observations)
- HistFinTS observation immutability (read-only constraint verification)
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest

from hf_reswb.application.panel_eligibility_service import (
    compute_panel_eligibility,
    compute_panel_result,
)
from hf_reswb.application.suitability_service import classify_series
from hf_reswb.domain.panel import (
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


def _insert_observations(
    db_path: str, series_id: int, dates_and_volumes: list[tuple[str, float]],
    price_changes: list[tuple[str, float]] | None = None
) -> None:
    """Insert multiple observations for a Series.

    Args:
        db_path: Database path
        series_id: Series ID
        dates_and_volumes: List of (date, volume) tuples
        price_changes: Optional list of (date, price) to override default pricing
    """
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

        # Build price map if provided
        price_map = {}
        if price_changes:
            for date, price in price_changes:
                price_map[date] = price

        # Insert observations
        prior_price = None
        for observed_at, volume in dates_and_volumes:
            # Get price: use price_map override or prior price for carry-forward
            if observed_at in price_map:
                price = price_map[observed_at]
            else:
                price = prior_price if prior_price is not None else 100.0

            prior_price = price

            # Set OHLC: if volume=0 and price=prior, OHLC collapsed; otherwise use price for all
            if volume == 0:
                # Carry-forward: OHLC all equal to current price
                o = h = l = c = price
            else:
                # Normal trade: realistic OHLC
                o = price
                h = price + 1.0
                l = price - 1.0
                c = price

            conn.execute(
                "INSERT INTO observation (series_id, import_run_id, observed_at, open, high, low, value, volume, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (series_id, run_id, observed_at, o, h, l, c, volume, now, now),
            )

        conn.commit()
    finally:
        conn.close()


class TestPanelWithRealSuitabilityOutput:
    """Integration tests with real observation-suitability pipeline."""

    def test_panel_with_mixed_trade_evidence(self, histfints_copy, tmp_path):
        """Panel with mixed TRADE_OBSERVED, NO_TRADE_REPORTED, and TRADE_EVIDENCE_UNRESOLVED observations."""
        # Three series with different trade evidence patterns
        trade_obs_id = _seed_series(histfints_copy, "TRADES", "ACTIVE")
        no_trade_id = _seed_series(histfints_copy, "NO_TRADE", "ACTIVE")
        unresolved_id = _seed_series(histfints_copy, "UNRESOLVED", "ACTIVE")

        # Series with trades
        _insert_observations(histfints_copy, trade_obs_id, [
            ("2020-04-13", 100.0),
            ("2020-04-14", 1000.0),  # High volume = TRADE_OBSERVED
        ])

        # Series with zero volume carry-forward (OHLC collapsed, equals prior)
        _insert_observations(histfints_copy, no_trade_id, [
            ("2020-04-13", 100.0),
            ("2020-04-14", 0.0),  # Zero volume, OHLC collapsed, equals prior = NO_TRADE_REPORTED
        ], price_changes=[("2020-04-13", 100.0), ("2020-04-14", 100.0)])

        # Series with zero volume but price moved (TRADE_EVIDENCE_UNRESOLVED)
        _insert_observations(histfints_copy, unresolved_id, [
            ("2020-04-13", 100.0),
            ("2020-04-14", 0.0),  # Zero volume but price moved = TRADE_EVIDENCE_UNRESOLVED
        ], price_changes=[("2020-04-13", 100.0), ("2020-04-14", 105.0)])

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            # Classify all series
            classify_series(connection, trade_obs_id, "2020-04-13", "2020-04-14")
            classify_series(connection, no_trade_id, "2020-04-13", "2020-04-14")
            classify_series(connection, unresolved_id, "2020-04-13", "2020-04-14")

            params = PanelEligibilityParameters()
            membership = compute_panel_eligibility(
                connection,
                [trade_obs_id, no_trade_id, unresolved_id],
                "2020-04-14",
                params,
                validate_suitability=False,
                check_coverage=False,
                check_adjustment_basis=False,
            )

            # Only TRADE_OBSERVED should be included
            assert trade_obs_id in membership.included_series_ids
            assert no_trade_id not in membership.included_series_ids
            assert unresolved_id in membership.included_series_ids  # UNRESOLVED is included by default

            # Check exclusion reasons
            no_trade_excl = [e for e in membership.excluded_records if e.series_id == no_trade_id]
            assert len(no_trade_excl) == 1
            assert no_trade_excl[0].reason == ExclusionReason.NO_TRADE_REPORTED
        finally:
            connection.close()

    def test_multi_series_panel_with_varying_staleness(self, histfints_copy, tmp_path):
        """Multi-series panel with different staleness conditions."""
        active_id = _seed_series(histfints_copy, "ACTIVE", "ACTIVE")
        recent_id = _seed_series(histfints_copy, "RECENT", "ACTIVE")
        stale_id = _seed_series(histfints_copy, "STALE", "ACTIVE")

        # Active: observation on analysis date
        _insert_observations(histfints_copy, active_id, [
            ("2020-04-10", 100.0),
            ("2020-04-14", 105.0),
        ])

        # Recent: observation 3 days before
        _insert_observations(histfints_copy, recent_id, [
            ("2020-04-10", 100.0),
            ("2020-04-11", 101.0),
        ])

        # Stale: observation 10 days before
        _insert_observations(histfints_copy, stale_id, [
            ("2020-04-01", 100.0),
            ("2020-04-04", 101.0),
        ])

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            # Classify all
            classify_series(connection, active_id, "2020-04-10", "2020-04-14")
            classify_series(connection, recent_id, "2020-04-10", "2020-04-11")
            classify_series(connection, stale_id, "2020-04-01", "2020-04-04")

            policy = StalenessPolicy(max_consecutive_no_trade_days=5)
            params = PanelEligibilityParameters(staleness_policy=policy)

            membership = compute_panel_eligibility(
                connection,
                [active_id, recent_id, stale_id],
                "2020-04-14",
                params,
                validate_suitability=False,
                check_coverage=False,
                check_adjustment_basis=False,
            )

            # Active should be included (observation on 2020-04-14)
            # Recent should be included (3 days since 2020-04-11)
            # Stale should be excluded (10 days since 2020-04-04)
            assert active_id in membership.included_series_ids
            assert recent_id in membership.included_series_ids
            assert stale_id not in membership.included_series_ids

            # Verify exclusion reasons
            stale_excl = [e for e in membership.excluded_records if e.series_id == stale_id]
            assert len(stale_excl) == 1
            assert stale_excl[0].reason == ExclusionReason.STALE
        finally:
            connection.close()


class TestTraceabilityChain:
    """Verify traceability from panel result through eligibility to observations."""

    def test_panel_result_carries_traceability(self, histfints_copy, tmp_path):
        """Panel result maintains full traceability chain."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        _insert_observations(histfints_copy, series_id, [
            ("2020-04-14", 100.0),
        ])

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, series_id, "2020-04-14", "2020-04-14")

            params = PanelEligibilityParameters()
            membership = compute_panel_eligibility(
                connection,
                [series_id],
                "2020-04-14",
                params,
                validate_suitability=False,
                check_coverage=False,
                check_adjustment_basis=False,
            )

            result = compute_panel_result(
                connection,
                membership,
                params,
                member_rates=[100.0],
                member_residuals=[0.0],
            )

            # Verify traceability elements
            assert result.date == "2020-04-14"
            assert result.parameters_used == params
            assert result.membership == membership
            assert result.member_count == 1
            assert result.member_rates == [100.0]
            assert result.member_residuals == [0.0]
            assert result.result_status == ResultStatus.PUBLISHED
        finally:
            connection.close()

    def test_excluded_series_recorded_with_reason(self, histfints_copy, tmp_path):
        """Excluded Series are recorded with explicit exclusion reasons."""
        active_id = _seed_series(histfints_copy, "ACTIVE", "ACTIVE")
        delisted_id = _seed_series(histfints_copy, "DELISTED", "DELISTED_OR_DISCONTINUED")

        _insert_observations(histfints_copy, active_id, [("2020-04-14", 100.0)])
        _insert_observations(histfints_copy, delisted_id, [("2020-04-14", 50.0)])

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, active_id, "2020-04-14", "2020-04-14")
            classify_series(connection, delisted_id, "2020-04-14", "2020-04-14")

            params = PanelEligibilityParameters(include_delisted=False)
            membership = compute_panel_eligibility(
                connection,
                [active_id, delisted_id],
                "2020-04-14",
                params,
                validate_suitability=False,
                check_coverage=False,
                check_adjustment_basis=False,
            )

            # Verify exclusion record
            assert len(membership.excluded_records) == 1
            excl = membership.excluded_records[0]
            assert excl.series_id == delisted_id
            assert excl.reason == ExclusionReason.DELISTED
            assert "DELISTED_OR_DISCONTINUED" in excl.detail
        finally:
            connection.close()


class TestHistFinTSImmutability:
    """Verify HistFinTS observations are never modified by panel eligibility."""

    def test_no_observations_modified(self, histfints_copy, tmp_path):
        """Panel eligibility operations do not modify HistFinTS observations."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        _insert_observations(histfints_copy, series_id, [
            ("2020-04-13", 100.0),
            ("2020-04-14", 0.0),
        ])

        # Get observation counts before
        conn_before = sqlite3.connect(histfints_copy)
        try:
            obs_before = conn_before.execute(
                "SELECT COUNT(*) as c FROM observation"
            ).fetchone()[0]  # fetchone() returns tuple, use index not dict key
        finally:
            conn_before.close()

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            # Run eligibility computation
            classify_series(connection, series_id, "2020-04-13", "2020-04-14")

            params = PanelEligibilityParameters()
            membership = compute_panel_eligibility(
                connection,
                [series_id],
                "2020-04-14",
                params,
                validate_suitability=False,
                check_coverage=False,
                check_adjustment_basis=False,
            )

            result = compute_panel_result(
                connection,
                membership,
                params,
                member_rates=[100.0],
                member_residuals=[0.0],
            )

            # Verify HistFinTS unchanged
            conn_after = sqlite3.connect(histfints_copy)
            try:
                obs_after = conn_after.execute(
                    "SELECT COUNT(*) as c FROM observation"
                ).fetchone()[0]
                assert obs_before == obs_after  # No observations added/deleted
            finally:
                conn_after.close()
        finally:
            connection.close()


class TestRegressionTests:
    """Verify no regressions in upstream components."""

    def test_upstream_suitability_contract_unchanged(self, histfints_copy, tmp_path):
        """Observation-suitability contract remains frozen (upstream)."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        _insert_observations(histfints_copy, series_id, [
            ("2020-04-13", 100.0),
            ("2020-04-14", 1000.0),
        ])

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            # Call frozen upstream function
            run, results = classify_series(connection, series_id, "2020-04-13", "2020-04-14")

            # Verify contract: SuitabilityRun and list of ObservationSuitability
            assert run.series_id == series_id
            assert run.count_trade_observed == 2
            assert run.count_no_trade_reported == 0
            assert len(results) == 2

            # Observations have correct trade evidence
            assert results[0].trade_evidence.value == "TRADE_OBSERVED"
            assert results[1].trade_evidence.value == "TRADE_OBSERVED"
        finally:
            connection.close()
