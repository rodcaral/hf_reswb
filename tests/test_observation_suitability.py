"""Tests for SPEC_OBSERVATION_SUITABILITY.md / D-038.

Constructed fixtures against HistFinTS's real schema (via the `histfints_copy` fixture,
built from the actual schema.sql + migrations, not a hand-rolled one) -- matching this
project's standing discipline that a reproduction must be built, not searched for (D-009),
and that the schema under test must be the real one (D-009b).
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from hf_reswb.application import apply_calendar, classify_series, compute_no_trade_runs, derive_calendar
from hf_reswb.domain import CalendarConfidence, SessionStatus, TradeEvidence
from hf_reswb.persistence import connect


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed_series(db_path, *, label: str, configured_interval: str = "1d") -> dict:
    conn = sqlite3.connect(db_path)
    try:
        now = _now()
        provider_row = conn.execute(
            "SELECT id FROM provider WHERE implementation_key='yahoo_finance' LIMIT 1"
        ).fetchone()
        if provider_row is None:
            provider_id = conn.execute(
                "INSERT INTO provider (display_name, implementation_key, kind, created_at, updated_at) "
                "VALUES ('Yahoo Finance', 'yahoo_finance', 'API', ?, ?)", (now, now),
            ).lastrowid
        else:
            provider_id = provider_row[0]

        series_id = conn.execute(
            "INSERT INTO series (label, series_type, configured_interval, backfill_start_date, "
            "status, created_at, updated_at) VALUES (?, 'STOCK', ?, '2000-01-01', 'ACTIVE', ?, ?)",
            (label, configured_interval, now, now),
        ).lastrowid
        assignment_id = conn.execute(
            "INSERT INTO provider_assignment (series_id, provider_id, priority, "
            "provider_series_identifier, created_at, updated_at) VALUES (?, ?, 1, ?, ?, ?)",
            (series_id, provider_id, label, now, now),
        ).lastrowid
        run_id = conn.execute(
            "INSERT INTO import_run (provider_assignment_id, trigger_type, status, started_at, "
            "ended_at, created_at, updated_at) VALUES (?, 'MANUAL', 'SUCCESS', ?, ?, ?, ?)",
            (assignment_id, now, now, now, now),
        ).lastrowid
        conn.commit()
        return {"series_id": series_id, "provider_id": provider_id, "import_run_id": run_id}
    finally:
        conn.close()


def _insert_bar(db_path, *, series_id, import_run_id, day: datetime, value, open_=None, high=None, low=None, volume=None):
    conn = sqlite3.connect(db_path)
    try:
        now = _now()
        conn.execute(
            "INSERT INTO observation (series_id, import_run_id, observed_at, value, open, "
            "high, low, volume, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (series_id, import_run_id, day.isoformat(), value, open_, high, low, volume, now, now),
        )
        conn.commit()
    finally:
        conn.close()


def _weekdays(start: datetime, n: int) -> list[datetime]:
    days = []
    d = start
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    return days


def test_no_trade_reported_for_conjunctive_carried_forward_bar(histfints_copy, tmp_path):
    """The adopted rule (SPEC §2.1): volume=0 AND OHLC collapsed AND value equals the prior
    stored close, at exact equality."""
    fixture = _seed_series(histfints_copy, label="FIXTURE-CARRY-FORWARD")
    days = _weekdays(datetime(2020, 12, 21, tzinfo=timezone.utc), 5)
    close = 29.3999996185303
    _insert_bar(histfints_copy, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[0], value=close, open_=close, high=close, low=close, volume=1000)
    for day in days[1:4]:
        # A carried-forward fill: OHLC collapsed to the same bit-identical close, volume 0.
        _insert_bar(histfints_copy, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                    day=day, value=close, open_=close, high=close, low=close, volume=0)

    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        run, results = classify_series(connection, fixture["series_id"], days[0].isoformat(), days[3].isoformat())
    finally:
        connection.close()

    assert results[0].trade_evidence == TradeEvidence.TRADE_OBSERVED  # the real trading day
    for item in results[1:]:
        assert item.trade_evidence == TradeEvidence.NO_TRADE_REPORTED
        assert "VOLUME_ZERO" in item.basis and "OHLC_COLLAPSED" in item.basis and "EQUALS_PRIOR_CLOSE" in item.basis
    assert run.count_no_trade_reported == 3
    assert run.count_trade_observed == 1


def test_trade_evidence_unresolved_when_price_moved_on_zero_volume(histfints_copy, tmp_path):
    """SPEC §2.1: volume=0 AND OHLC collapsed AND value != prior close -> unresolved, not
    a confirmed no-trade (it cannot be a pure carry-forward if the price moved)."""
    fixture = _seed_series(histfints_copy, label="FIXTURE-UNRESOLVED")
    days = _weekdays(datetime(2021, 3, 1, tzinfo=timezone.utc), 2)
    _insert_bar(histfints_copy, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[0], value=50.0, open_=50.0, high=50.0, low=50.0, volume=500)
    _insert_bar(histfints_copy, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[1], value=51.5, open_=51.5, high=51.5, low=51.5, volume=0)

    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        run, results = classify_series(connection, fixture["series_id"], days[0].isoformat(), days[1].isoformat())
    finally:
        connection.close()

    assert results[1].trade_evidence == TradeEvidence.TRADE_EVIDENCE_UNRESOLVED
    assert run.count_trade_evidence_unresolved == 1


def test_trade_observed_with_volume_unreliable_for_genuine_range_at_zero_volume(histfints_copy, tmp_path):
    """§1.2: a genuine intraday range reported with volume=0 is real evidence of a trade --
    not a carried-forward fill -- but flagged volume_unreliable."""
    fixture = _seed_series(histfints_copy, label="FIXTURE-RANGE")
    days = _weekdays(datetime(2023, 11, 22, tzinfo=timezone.utc), 2)
    _insert_bar(histfints_copy, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[0], value=1.0, open_=1.0, high=1.0, low=1.0, volume=100)
    _insert_bar(histfints_copy, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[1], value=1.05, open_=0.95, high=1.10, low=0.92, volume=0)

    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        run, results = classify_series(connection, fixture["series_id"], days[0].isoformat(), days[1].isoformat())
    finally:
        connection.close()

    assert results[1].trade_evidence == TradeEvidence.TRADE_OBSERVED
    assert results[1].volume_unreliable is True


def test_f030_guard_refuses_non_daily_series(histfints_copy, tmp_path):
    fixture = _seed_series(histfints_copy, label="FIXTURE-5M", configured_interval="5m")
    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        with pytest.raises(ValueError, match="F-030"):
            classify_series(connection, fixture["series_id"], "2020-01-01", "2020-12-31")
    finally:
        connection.close()


def test_ground_truth_against_real_production_series_11312(real_production_db_readonly_path, tmp_path):
    """Same ground truth SPEC_OBSERVATION_SUITABILITY.md §1.3 validated against: series
    11312 (YPF CEDEAR), Argentina's *feriados inamovibles* 2000-12-25 and 2001-01-01.
    Read-only against the real production file -- no copy, no fixture."""
    connection = connect(tmp_path / "workbench.db", real_production_db_readonly_path, histfints_readonly=True)
    try:
        _, results = classify_series(connection, 11312, "2000-12-20T00:00:00+00:00", "2001-01-02T00:00:00+00:00")
    finally:
        connection.close()

    by_date = {item.observed_date: item.trade_evidence for item in results}
    assert by_date["2000-12-25"] == TradeEvidence.NO_TRADE_REPORTED  # Christmas
    assert by_date["2001-01-01"] == TradeEvidence.NO_TRADE_REPORTED  # New Year's Day
    assert by_date["2000-12-21"] == TradeEvidence.TRADE_OBSERVED
    assert by_date["2000-12-26"] == TradeEvidence.TRADE_OBSERVED
    assert by_date["2000-12-27"] == TradeEvidence.TRADE_OBSERVED


def test_calendar_derivation_ordering_and_no_trade_run(histfints_copy, tmp_path):
    """§3.3's ordering: Axis A first (no calendar input), then a calendar derived from
    TRADE_OBSERVED dates only, then Axis B applied back onto the classified rows. Mirrors
    the 2026-07-06 case (D-038 §1.4): most of the venue trades while one Series carries a
    fill -- quorum must still confirm the session, not call it absent."""
    days = _weekdays(datetime(2024, 6, 3, tzinfo=timezone.utc), 6)

    a = _seed_series(histfints_copy, label="FIXTURE-VENUE-A")
    b = _seed_series(histfints_copy, label="FIXTURE-VENUE-B")
    c = _seed_series(histfints_copy, label="FIXTURE-VENUE-C")

    # A real holiday: all three carry a fill on day[2].
    # An idiosyncratic non-trade for Series A only on day[4]: B and C trade normally.
    close_a, close_b, close_c = 10.0, 20.0, 30.0
    for i, day in enumerate(days):
        if i == 2:
            _insert_bar(histfints_copy, series_id=a["series_id"], import_run_id=a["import_run_id"],
                        day=day, value=close_a, open_=close_a, high=close_a, low=close_a, volume=0)
            _insert_bar(histfints_copy, series_id=b["series_id"], import_run_id=b["import_run_id"],
                        day=day, value=close_b, open_=close_b, high=close_b, low=close_b, volume=0)
            _insert_bar(histfints_copy, series_id=c["series_id"], import_run_id=c["import_run_id"],
                        day=day, value=close_c, open_=close_c, high=close_c, low=close_c, volume=0)
            continue
        bump_a = close_a if i == 4 else close_a + i
        _insert_bar(histfints_copy, series_id=a["series_id"], import_run_id=a["import_run_id"],
                    day=day, value=bump_a, open_=bump_a, high=bump_a, low=bump_a,
                    volume=(0 if i == 4 else 100))
        close_b_i, close_c_i = close_b + i, close_c + i
        _insert_bar(histfints_copy, series_id=b["series_id"], import_run_id=b["import_run_id"],
                    day=day, value=close_b_i, open_=close_b_i, high=close_b_i, low=close_b_i, volume=150)
        _insert_bar(histfints_copy, series_id=c["series_id"], import_run_id=c["import_run_id"],
                    day=day, value=close_c_i, open_=close_c_i, high=close_c_i, low=close_c_i, volume=200)
        close_a = bump_a

    period_start, period_end = days[0].isoformat(), days[-1].isoformat()
    connection = connect(tmp_path / "workbench.db", histfints_copy, histfints_readonly=True)
    try:
        run_a, results_a = classify_series(connection, a["series_id"], period_start, period_end)
        classify_series(connection, b["series_id"], period_start, period_end)
        classify_series(connection, c["series_id"], period_start, period_end)

        derivation = derive_calendar(
            connection, venue="XBUE",
            contributing_series_ids=[a["series_id"], b["series_id"], c["series_id"]],
            period_start=period_start, period_end=period_end,
            confidence_band=CalendarConfidence.RELIABLE, quorum_threshold=0.5,
        )
        apply_calendar(connection, derivation, a["series_id"])

        rows = connection.execute(
            "SELECT observed_date, trade_evidence, session_status FROM observation_suitability "
            "WHERE histfints_series_id = ? ORDER BY observed_date", (a["series_id"],),
        ).fetchall()

        # day[2]: real holiday -- all three fill -> SESSION_ABSENT (quorum has no TRADE_OBSERVED).
        assert rows[2]["trade_evidence"] == TradeEvidence.NO_TRADE_REPORTED.value
        assert rows[2]["session_status"] == SessionStatus.SESSION_ABSENT.value

        # day[4]: only A fills; B and C trade -> quorum confirms the session for A too.
        assert rows[4]["trade_evidence"] == TradeEvidence.NO_TRADE_REPORTED.value
        assert rows[4]["session_status"] == SessionStatus.SESSION_CONFIRMED.value

        no_trade_runs = compute_no_trade_runs(connection, run_a.id)
        assert {r.first_date for r in no_trade_runs} == {days[2].isoformat()[:10], days[4].isoformat()[:10]}
        assert all(r.length == 1 for r in no_trade_runs)
    finally:
        connection.close()
