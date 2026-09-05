"""F-033 quarantine integration (DOM-2 ordering, item 1 of 3).

Proves `histfints.observation_quarantine_active` is consumed as the complete Workbench
predicate for CONFIRMED_SYNTHETIC exclusion, per the required ordering
`quarantine/provenance -> observation suitability -> calendar/alignment -> calculation`,
across the three consumers that actually read `histfints.observation` for a financial/
continuity calculation: `suitability_service.classify_series`, `reconciliation_service.reconcile`
(F-009), and `calibration_utilities.py`'s two direct-query functions.

Built against `histfints_copy_v27` (real schema.sql + real migrations through 0027, D-009b) --
never a hand-rolled quarantine table -- per this project's standing discipline that a
reproduction must be built against the real schema, not searched for or approximated.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from hf_reswb.application import DetectorParams, reconcile
from hf_reswb.application.calibration_utilities import (
    compute_panel_depth_by_date,
    compute_staleness_lengths,
)
from hf_reswb.application.quarantine import quarantined_observation_ids
from hf_reswb.domain import TradeEvidence, Verdict
from hf_reswb.persistence import connect

from tests.conftest import insert_fixture_quarantine, insert_fixture_series_with_step

PARAMS = DetectorParams(step_threshold=0.20, persistence_horizons_days=(15, 60), persistence_tolerance=0.10)


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
        return {
            "series_id": series_id, "provider_id": provider_id,
            "assignment_id": assignment_id, "import_run_id": run_id,
        }
    finally:
        conn.close()


def _insert_bar(db_path, *, series_id, import_run_id, day: datetime, value,
                 open_=None, high=None, low=None, volume=None) -> int:
    conn = sqlite3.connect(db_path)
    try:
        now = _now()
        obs_id = conn.execute(
            "INSERT INTO observation (series_id, import_run_id, observed_at, value, open, "
            "high, low, volume, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (series_id, import_run_id, day.isoformat(), value, open_, high, low, volume, now, now),
        ).lastrowid
        conn.commit()
        return obs_id
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


def test_quarantined_observed_looking_row_excluded_from_classification(histfints_copy_v27, tmp_path):
    """Property 1: a row that would otherwise classify TRADE_OBSERVED (real volume, real
    price move) is analytically excluded outright once quarantined -- no ObservationSuitability
    row at all, not merely a different TradeEvidence value."""
    from hf_reswb.application import classify_series

    fixture = _seed_series(histfints_copy_v27, label="FIXTURE-Q-EXCLUDED")
    days = _weekdays(datetime(2024, 4, 1, tzinfo=timezone.utc), 2)
    _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[0], value=100.0, open_=99.0, high=101.0, low=98.5, volume=1000)
    quarantined_id = _insert_bar(
        histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
        day=days[1], value=110.0, open_=108.0, high=111.0, low=107.0, volume=2000,
    )
    insert_fixture_quarantine(
        histfints_copy_v27, series_id=fixture["series_id"],
        provider_assignment_id=fixture["assignment_id"], observation_ids=[quarantined_id],
    )

    connection = connect(tmp_path / "workbench.db", histfints_copy_v27, histfints_readonly=True)
    try:
        run, results = classify_series(connection, fixture["series_id"], days[0].isoformat(), days[1].isoformat())
    finally:
        connection.close()

    assert len(results) == 1
    assert results[0].trade_evidence == TradeEvidence.TRADE_OBSERVED  # day[0], never quarantined
    assert run.count_trade_observed == 1
    assert run.count_no_trade_reported == 0
    assert run.count_trade_evidence_unresolved == 0


def test_quarantined_gap_does_not_bridge_continuity_for_equals_prior_close(histfints_copy_v27, tmp_path):
    """The conservative default (module docstring, suitability_service.py): `prior` resets
    across a quarantined row rather than silently comparing the row after the gap against the
    genuine row before it. Constructed so the naive/bridging behavior and the correct
    behavior would disagree: day 3 bit-for-bit equals day 1's close, volume 0, OHLC collapsed.
    If continuity had silently bridged across day 2 (quarantined), day 3 would classify
    NO_TRADE_REPORTED (EQUALS_PRIOR_CLOSE against day 1). It must not."""
    from hf_reswb.application import classify_series

    fixture = _seed_series(histfints_copy_v27, label="FIXTURE-Q-NOBRIDGE")
    days = _weekdays(datetime(2024, 5, 6, tzinfo=timezone.utc), 3)
    close_day1 = 42.5
    _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[0], value=close_day1, open_=close_day1, high=close_day1, low=close_day1, volume=500)
    quarantined_id = _insert_bar(
        histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
        day=days[1], value=999.0, open_=999.0, high=999.0, low=999.0, volume=700,
    )
    insert_fixture_quarantine(
        histfints_copy_v27, series_id=fixture["series_id"],
        provider_assignment_id=fixture["assignment_id"], observation_ids=[quarantined_id],
    )
    # Bit-identical to day 1's close, volume 0, OHLC collapsed -- would be NO_TRADE_REPORTED
    # only if compared against a "prior" that survived across the quarantined gap.
    _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[2], value=close_day1, open_=close_day1, high=close_day1, low=close_day1, volume=0)

    connection = connect(tmp_path / "workbench.db", histfints_copy_v27, histfints_readonly=True)
    try:
        run, results = classify_series(connection, fixture["series_id"], days[0].isoformat(), days[2].isoformat())
    finally:
        connection.close()

    assert len(results) == 2  # day 1 and day 3 only -- day 2 fully excluded
    assert results[0].observed_date == days[0].isoformat()[:10]
    assert results[1].observed_date == days[2].isoformat()[:10]
    # day 3's "prior" reset to None across the quarantined gap: OHLC collapsed + volume zero
    # but no resolvable prior-close comparison -- unresolved, not a confirmed carry-forward.
    assert results[1].trade_evidence == TradeEvidence.TRADE_EVIDENCE_UNRESOLVED
    assert "EQUALS_PRIOR_CLOSE" not in results[1].basis


def test_clean_observations_in_partially_quarantined_series_remain_eligible(histfints_copy_v27, tmp_path):
    """Property 5: quarantine binds to `observation.id`, never to `series_id` membership --
    a Series with some quarantined history still classifies its later, clean observations
    normally rather than being rejected wholesale merely for appearing in a quarantine case."""
    from hf_reswb.application import classify_series

    fixture = _seed_series(histfints_copy_v27, label="FIXTURE-Q-PARTIAL-SERIES")
    contaminated_days = _weekdays(datetime(2024, 1, 8, tzinfo=timezone.utc), 3)
    clean_days = _weekdays(datetime(2024, 6, 3, tzinfo=timezone.utc), 2)

    contaminated_ids = [
        _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                    day=day, value=50.0, open_=50.0, high=50.0, low=50.0, volume=100)
        for day in contaminated_days
    ]
    insert_fixture_quarantine(
        histfints_copy_v27, series_id=fixture["series_id"],
        provider_assignment_id=fixture["assignment_id"], observation_ids=contaminated_ids,
    )
    _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=clean_days[0], value=61.0, open_=60.0, high=62.0, low=59.5, volume=900)
    _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=clean_days[1], value=63.5, open_=61.5, high=64.0, low=61.0, volume=950)

    connection = connect(tmp_path / "workbench.db", histfints_copy_v27, histfints_readonly=True)
    try:
        run, results = classify_series(
            connection, fixture["series_id"], contaminated_days[0].isoformat(), clean_days[-1].isoformat()
        )
    finally:
        connection.close()

    assert len(results) == 2  # only the two clean days -- three contaminated days fully excluded
    assert all(item.trade_evidence == TradeEvidence.TRADE_OBSERVED for item in results)
    assert run.count_trade_observed == 2


def test_quarantined_observations_excluded_from_staleness_and_panel_depth(histfints_copy_v27, tmp_path):
    """Property 2: a CONFIRMED_SYNTHETIC row cannot enter calibration inputs -- it counts
    neither toward panel depth on its date nor as closing a staleness gap early."""
    fixture = _seed_series(histfints_copy_v27, label="FIXTURE-Q-CALIBRATION")
    days = _weekdays(datetime(2024, 2, 5, tzinfo=timezone.utc), 3)
    _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[0], value=10.0, volume=100)
    quarantined_id = _insert_bar(
        histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
        day=days[1], value=10.1, volume=100,
    )
    insert_fixture_quarantine(
        histfints_copy_v27, series_id=fixture["series_id"],
        provider_assignment_id=fixture["assignment_id"], observation_ids=[quarantined_id],
    )
    _insert_bar(histfints_copy_v27, series_id=fixture["series_id"], import_run_id=fixture["import_run_id"],
                day=days[2], value=10.2, volume=100)

    connection = connect(tmp_path / "workbench.db", histfints_copy_v27, histfints_readonly=True)
    try:
        staleness = compute_staleness_lengths(
            connection, [fixture["series_id"]], days[0].isoformat()[:10], days[2].isoformat()[:10]
        )
        depth = compute_panel_depth_by_date(
            connection, [fixture["series_id"]], days[0].isoformat()[:10], days[2].isoformat()[:10]
        )
    finally:
        connection.close()

    # The gap spans day 0 -> day 2 directly (day 1 excluded), not two 1-day gaps.
    gap_days = (days[2].date() - days[0].date()).days
    assert staleness[fixture["series_id"]] == [gap_days]
    assert days[1].isoformat()[:10] not in depth


def test_f009_does_not_treat_confirmed_synthetic_as_genuine_price_evidence(histfints_copy_v27, tmp_path):
    """Property 3: a quarantined row sitting exactly at the true step boundary is excluded
    from `detect_boundaries()`'s input outright, and the genuine flat segments on either side
    of it are never compared against each other as though newly adjacent -- no finding is
    fabricated from data no consumer may treat as genuine."""
    fixture = insert_fixture_series_with_step(histfints_copy_v27, label="FIXTURE-Q-F009", step_factor=1 / 7)

    # The one observation actually carrying evidence of the 630 -> 90 transition is the first
    # "after" row inserted by the fixture -- quarantine exactly that one.
    connection_probe = sqlite3.connect(histfints_copy_v27)
    boundary_row = connection_probe.execute(
        "SELECT id FROM observation WHERE id = ?", (fixture["boundary_observation_id"],)
    ).fetchone()
    connection_probe.close()
    assert boundary_row is not None

    insert_fixture_quarantine(
        histfints_copy_v27, series_id=fixture["series_id"],
        provider_assignment_id=fixture["assignment_id"],
        observation_ids=[fixture["boundary_observation_id"]],
    )

    connection = connect(tmp_path / "workbench.db", histfints_copy_v27, histfints_readonly=True)
    try:
        ids = [
            r["id"] for r in connection.execute(
                "SELECT id FROM histfints.observation WHERE series_id = ? AND observed_at BETWEEN ? AND ?",
                (fixture["series_id"], fixture["period_start"], fixture["period_end"]),
            ).fetchall()
        ]
        assert fixture["boundary_observation_id"] in quarantined_observation_ids(connection, ids)

        findings = reconcile(
            connection, series_id=fixture["series_id"], period_start=fixture["period_start"],
            period_end=fixture["period_end"], params=PARAMS,
        )
    finally:
        connection.close()

    for finding in findings:
        assert finding.calculation.evidence_observation_before_id != fixture["boundary_observation_id"]
        assert finding.calculation.evidence_observation_after_id != fixture["boundary_observation_id"]


def test_reconcile_unchanged_for_non_quarantined_series(histfints_copy_v27, tmp_path):
    """Property 4: with nothing quarantined, `reconcile()` against the v27 schema still finds
    and classifies the same real discontinuity as it does against the shared v10 fixture
    (test_reconciliation_boundary.py::test_not_explained_when_...) -- the quarantine
    integration changes nothing for a clean series."""
    fixture = insert_fixture_series_with_step(histfints_copy_v27, label="FIXTURE-Q-UNCHANGED", step_factor=1 / 7)

    connection = connect(tmp_path / "workbench.db", histfints_copy_v27, histfints_readonly=True)
    try:
        findings = reconcile(
            connection, series_id=fixture["series_id"], period_start=fixture["period_start"],
            period_end=fixture["period_end"], params=PARAMS,
        )
    finally:
        connection.close()

    assert len(findings) == 1
    assert findings[0].verdict == Verdict.NOT_EXPLAINED
    assert findings[0].calculation.evidence_observation_after_id == fixture["boundary_observation_id"]


def test_panel_eligibility_service_and_data_constraints_have_no_direct_observation_reads():
    """`panel_eligibility_service.py` and `data_constraints.py` were re-reviewed for this
    increment and confirmed to never read `histfints.observation` directly (only
    `provider_assignment`/`provider`/`series`) -- explicit "no quarantine integration needed"
    determination, not a silent omission. This asserts the source fact so the determination
    cannot silently go stale."""
    import inspect

    from hf_reswb.application import data_constraints, panel_eligibility_service

    for module in (panel_eligibility_service, data_constraints):
        source = inspect.getsource(module)
        assert "FROM histfints.observation" not in source
        assert "histfints.observation " not in source
        assert "histfints.observation\n" not in source
