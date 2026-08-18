"""Phase 2 tests for panel eligibility (D-046).

Tests for observation-suitability integration:
- Trade evidence filtering (NO_TRADE_REPORTED exclusion)
- Session status visibility (display-only, never gates)
- Suitability coverage validation
- Integration with Phase 1 parameters
- Upstream contract preservation
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest

from hf_reswb.application.panel_eligibility_service import compute_panel_eligibility
from hf_reswb.application.panel_integration import (
    get_session_status_for_date,
    get_trade_evidence_exclusions,
    get_trade_evidence_for_date,
    validate_suitability_coverage,
)
from hf_reswb.application.suitability_service import classify_series
from hf_reswb.domain.panel import (
    ExclusionReason,
    PanelEligibilityParameters,
    StalenessPolicy,
)
from hf_reswb.domain.suitability import TradeEvidence
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
    db_path: str, series_id: int, observed_at: str, value: float, volume: float = 100.0,
    open_val: float | None = None, high_val: float | None = None, low_val: float | None = None
) -> None:
    """Insert an observation with full OHLC."""
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

        # Default OHLC to close value if not specified
        if open_val is None:
            open_val = value
        if high_val is None:
            high_val = value
        if low_val is None:
            low_val = value

        conn.execute(
            "INSERT INTO observation (series_id, import_run_id, observed_at, open, high, low, value, volume, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (series_id, run_id, observed_at, open_val, high_val, low_val, value, volume, now, now),
        )
        conn.commit()
    finally:
        conn.close()


class TestTradeEvidenceFiltering:
    """Test trade evidence filtering integration (Phase 2)."""

    def test_no_trade_reported_excluded_by_default(self, histfints_copy, tmp_path):
        """Series with NO_TRADE_REPORTED on analysis_date are excluded by default."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        # Create two observations: one normal trade, one zero-volume carry-forward
        _insert_observation(histfints_copy, series_id, "2020-04-13", 100.0)
        # Zero volume, OHLC collapsed, equals prior close = NO_TRADE_REPORTED
        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0, volume=0.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            # Run suitability classification
            classify_series(connection, series_id, "2020-04-13", "2020-04-14")

            # Panel eligibility without validation bypass
            params = PanelEligibilityParameters()
            membership = compute_panel_eligibility(
                connection, [series_id], "2020-04-14", params, validate_suitability=False
            )

            # Series should be excluded due to NO_TRADE_REPORTED
            assert series_id not in membership.included_series_ids
            assert len(membership.excluded_records) == 1
            assert membership.excluded_records[0].reason == ExclusionReason.NO_TRADE_REPORTED
        finally:
            connection.close()

    def test_trade_observed_included(self, histfints_copy, tmp_path):
        """Series with volume > 0 (TRADE_OBSERVED) are included."""
        series_id = _seed_series(histfints_copy, "SERIES_B", "ACTIVE")

        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0, volume=1000.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, series_id, "2020-04-14", "2020-04-14")

            params = PanelEligibilityParameters()
            membership = compute_panel_eligibility(
                connection, [series_id], "2020-04-14", params, validate_suitability=False
            )

            # Series should be included
            assert series_id in membership.included_series_ids
        finally:
            connection.close()


class TestSessionStatusVisibility:
    """Test session status integration (display-only, never gates)."""

    def test_session_status_visible_for_inspection(self, histfints_copy, tmp_path):
        """Session status can be queried for display context."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0, volume=100.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, series_id, "2020-04-14", "2020-04-14")

            # Session status should be queryable (initially UNRESOLVED until apply_calendar)
            status = get_session_status_for_date(connection, series_id, "2020-04-14")

            assert status is not None
        finally:
            connection.close()


class TestTradeEvidenceQueries:
    """Test individual trade evidence query functions."""

    def test_get_trade_evidence_for_date(self, histfints_copy, tmp_path):
        """Query trade evidence for a Series/date."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0, volume=100.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, series_id, "2020-04-14", "2020-04-14")

            evidence = get_trade_evidence_for_date(connection, series_id, "2020-04-14")

            assert evidence == TradeEvidence.TRADE_OBSERVED
        finally:
            connection.close()

    def test_get_trade_evidence_for_missing_date(self, histfints_copy, tmp_path):
        """Query returns None for non-existent date."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            evidence = get_trade_evidence_for_date(connection, series_id, "2020-04-14")

            assert evidence is None
        finally:
            connection.close()


class TestSuitabilityCoverageValidation:
    """Test suitability coverage validation (Phase 2 gate)."""

    def test_coverage_validation_passes_when_classified(self, histfints_copy, tmp_path):
        """Coverage validation passes when suitability_run covers period."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0, volume=100.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, series_id, "2020-04-14", "2020-04-14")

            covered, missing = validate_suitability_coverage(
                connection, [series_id], "2020-04-14", "2020-04-14"
            )

            assert covered is True
            assert len(missing) == 0
        finally:
            connection.close()

    def test_coverage_validation_fails_when_not_classified(self, histfints_copy, tmp_path):
        """Coverage validation fails when suitability_run does not exist."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            covered, missing = validate_suitability_coverage(
                connection, [series_id], "2020-04-14", "2020-04-14"
            )

            assert covered is False
            assert len(missing) == 1
            assert missing[0][0] == series_id
        finally:
            connection.close()


class TestPhase2Integration:
    """Test Phase 2 integration with Phase 1 parameters."""

    def test_delisted_plus_trade_evidence_filtering(self, histfints_copy, tmp_path):
        """Delisted filter and trade evidence filter compose correctly."""
        active_id = _seed_series(histfints_copy, "ACTIVE", "ACTIVE")
        delisted_id = _seed_series(histfints_copy, "DELISTED", "DELISTED_OR_DISCONTINUED")

        _insert_observation(histfints_copy, active_id, "2020-04-14", 100.0, volume=100.0)
        _insert_observation(histfints_copy, delisted_id, "2020-04-14", 50.0, volume=0.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, active_id, "2020-04-14", "2020-04-14")
            classify_series(connection, delisted_id, "2020-04-14", "2020-04-14")

            params = PanelEligibilityParameters(include_delisted=False)
            membership = compute_panel_eligibility(
                connection, [active_id, delisted_id], "2020-04-14", params, validate_suitability=False
            )

            # Active should be included; delisted excluded for status + trade evidence
            assert active_id in membership.included_series_ids
            assert delisted_id not in membership.included_series_ids

            # Delisted exclusion should be from DELISTED reason (first filter)
            delisted_excl = [e for e in membership.excluded_records if e.series_id == delisted_id]
            assert len(delisted_excl) == 1
            assert delisted_excl[0].reason == ExclusionReason.DELISTED
        finally:
            connection.close()

    def test_staleness_plus_trade_evidence_filtering(self, histfints_copy, tmp_path):
        """Staleness and trade evidence filters compose correctly."""
        stale_id = _seed_series(histfints_copy, "STALE", "ACTIVE")
        notrade_id = _seed_series(histfints_copy, "NOTRADE", "ACTIVE")

        # Stale: observation ends before analysis date
        _insert_observation(histfints_copy, stale_id, "2020-04-10", 100.0, volume=100.0)
        # No trade: zero volume on analysis date
        _insert_observation(histfints_copy, notrade_id, "2020-04-13", 100.0, volume=100.0)
        _insert_observation(histfints_copy, notrade_id, "2020-04-14", 100.0, volume=0.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            classify_series(connection, stale_id, "2020-04-10", "2020-04-10")
            classify_series(connection, notrade_id, "2020-04-13", "2020-04-14")

            params = PanelEligibilityParameters(
                staleness_policy=StalenessPolicy(max_consecutive_no_trade_days=2)
            )
            membership = compute_panel_eligibility(
                connection, [stale_id, notrade_id], "2020-04-14", params, validate_suitability=False
            )

            # Both should be excluded: stale by staleness policy, notrade by trade evidence
            assert stale_id not in membership.included_series_ids
            assert notrade_id not in membership.included_series_ids

            reasons = {e.series_id: e.reason for e in membership.excluded_records}
            assert reasons[stale_id] == ExclusionReason.STALE
            assert reasons[notrade_id] == ExclusionReason.NO_TRADE_REPORTED
        finally:
            connection.close()


class TestUpstreamContractPreservation:
    """Verify frozen upstream contract (suitability_service) is not modified."""

    def test_classify_series_unchanged(self, histfints_copy, tmp_path):
        """classify_series contract unchanged (frozen)."""
        series_id = _seed_series(histfints_copy, "SERIES_A", "ACTIVE")
        _insert_observation(histfints_copy, series_id, "2020-04-14", 100.0, volume=100.0)

        connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
        try:
            # Call frozen function
            run, results = classify_series(connection, series_id, "2020-04-14", "2020-04-14")

            # Verify contract: returns (SuitabilityRun, list[ObservationSuitability])
            assert run.series_id == series_id
            assert len(results) == 1
            assert results[0].trade_evidence == TradeEvidence.TRADE_OBSERVED
        finally:
            connection.close()
