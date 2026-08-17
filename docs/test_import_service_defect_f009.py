"""
Regression tests for DEFECT-F009: incremental import scale breaks.

Constructed-reproduction harness running against real persistence (disposable SQLite,
real schema/migrations, real ImportService/_determine_range()) with a scripted
FakeProviderClient. The only way to force a before/after-a-restating-event boundary,
since no live provider exposes vintage data.

Case (a): split — Yahoo-style price adjustment at a known date.
Case (b): FRED-style revision — provider re-publishes with historical corrections.

Both cases run through the real ImportService.run_import() -> _determine_range() ->
fetch -> _store_records() path, confirming the defect and the incremental-import
mechanism that causes it.

See docs/DEFECT-F009.md for full analysis and impact.
"""
import os
import tempfile
from datetime import date, datetime, timezone

from pathlib import Path

from histfints.application import ImportService, ProviderRecord
from histfints.domain import Provider, ProviderKind, Series, SeriesType, TriggerType
from histfints.persistence import (
    SqliteImportRunRepository,
    SqliteObservationRepository,
    SqliteProviderRepository,
    SqliteSeriesRepository,
    connect,
)
from histfints.application import ProviderClient
from tests.fakes.import_lock import FakeImportLock
from tests.fakes.provider_client_factory import FakeProviderClientFactory


class ScriptedRecordingClient(ProviderClient):
    """Like FakeProviderClient but also records (identifier, interval, start, end) per call."""

    def __init__(self, outcomes):
        self._outcomes = iter(outcomes)
        self.calls = []

    def fetch(self, identifier, interval, start, end):
        self.calls.append((identifier, interval, start, end))
        return next(self._outcomes)

def fresh_conn(tmp_path):
    """Create a fresh in-memory or temp-file SQLite connection with full schema."""
    db_path = tmp_path / "a009_test.db"
    return connect(str(db_path))


def test_defect_f009_case_a_split(tmp_path):
    """DEFECT-F009 case (a): split scale break on incremental import.

    Yahoo-style: provider reports price adjustments; when a split occurs,
    subsequent fetches report post-split-adjusted prices for all dates.
    _determine_range() fetches only from latest-stored forward, missing the
    opportunity to fix pre-split prices to post-split scale. Result: permanent
    scale break with no correction row.
    """
    conn = fresh_conn(tmp_path)
    series_repo = SqliteSeriesRepository(conn)
    provider_repo = SqliteProviderRepository(conn)
    import_run_repo = SqliteImportRunRepository(conn)
    observation_repo = SqliteObservationRepository(conn)

    provider = provider_repo.save(
        Provider(display_name="Yahoo Finance", implementation_key="yahoo_finance", kind=ProviderKind.API)
    )
    series = Series(
        label="FIXTURE-SPLIT-CO",
        series_type=SeriesType.STOCK,
        configured_interval="1d",
        backfill_start_date=date(2020, 1, 2),
    )
    series.add_provider_assignment(provider, priority=1, provider_series_identifier="FIXCO")
    series = series_repo.save(series)

    # Call 1 (first backfill, ending BEFORE the fixture split): real pre-split-scale values,
    # e.g. a $600-ish stock about to do a 7:1 split -- exactly AAPL's own real 2014 numbers.
    pre_split = [
        ProviderRecord(observed_at=datetime(2020, 8, 27, tzinfo=timezone.utc), value=630.00),
        ProviderRecord(observed_at=datetime(2020, 8, 28, tzinfo=timezone.utc), value=632.50),
    ]
    # Call 2 (incremental, forward from latest stored date): the SAME provider now reporting on
    # the POST-split scale for genuinely new dates -- exactly what Yahoo would return for any
    # live call made after a real split, since it always serves current-basis values.
    post_split = [
        ProviderRecord(observed_at=datetime(2020, 8, 31, tzinfo=timezone.utc), value=129.04),
        ProviderRecord(observed_at=datetime(2020, 9, 1, tzinfo=timezone.utc), value=134.18),
    ]
    factory = FakeProviderClientFactory({"yahoo_finance": ScriptedRecordingClient([pre_split, post_split])})
    service = ImportService(
        series_repo=series_repo, provider_repo=provider_repo, import_run_repo=import_run_repo,
        observation_repo=observation_repo, import_lock=FakeImportLock(), provider_client_factory=factory,
    )

    run1 = service.run_import(series.id, TriggerType.MANUAL)
    assert run1.status.value in ("SUCCESS", "PARTIAL"), f"Import 1 failed: {run1.status.value}"

    run2 = service.run_import(series.id, TriggerType.MANUAL)
    assert run2.status.value in ("SUCCESS", "PARTIAL"), f"Import 2 failed: {run2.status.value}"

    rows = conn.execute(
        "SELECT observed_at, value FROM observation WHERE series_id=? ORDER BY observed_at", (series.id,)
    ).fetchall()
    assert len(rows) == 4, f"Expected 4 observations, got {len(rows)}"

    corrections = conn.execute(
        "SELECT c.* FROM correction c JOIN observation o ON o.id=c.observation_id WHERE o.series_id=?",
        (series.id,),
    ).fetchall()

    # DEFECT-F009 REPRODUCED: no correction rows fired despite scale break
    ratio = rows[1]["value"] / rows[2]["value"]
    assert len(corrections) == 0, f"Expected 0 corrections, got {len(corrections)}: {corrections}"
    assert ratio > 2, f"Expected discontinuity ratio > 2, got {ratio:.4f}"

    conn.close()


def test_defect_f009_case_b_fred_revision(tmp_path):
    """DEFECT-F009 case (b): FRED-style revision blindness on incremental import.

    FRED publishes economic indicators with provisional values that get revised
    in later releases (standard for BLS-reported data: prior two months provisional).
    _determine_range() fetches only from latest-stored forward. If June's value is
    revised on the next release, the revised value is never fetched because the fetch
    was asked to start at August (latest stored). Result: stale June value persists,
    never revised, no correction row.
    """
    conn = fresh_conn(tmp_path)
    series_repo = SqliteSeriesRepository(conn)
    provider_repo = SqliteProviderRepository(conn)
    import_run_repo = SqliteImportRunRepository(conn)
    observation_repo = SqliteObservationRepository(conn)

    # Real production default_revalidation_window_days for FRED is NULL (zero look-back) --
    # confirmed live. Reproduce that exact configuration.
    provider = provider_repo.save(
        Provider(display_name="FRED", implementation_key="fred", kind=ProviderKind.API,
                 default_revalidation_window_days=None)
    )
    series = Series(
        label="FIXTURE-REVISED-INDICATOR",
        series_type=SeriesType.ECONOMIC_INDICATOR,
        configured_interval="1mo",
        backfill_start_date=date(2020, 1, 1),
    )
    series.add_provider_assignment(provider, priority=1, provider_series_identifier="FIXIND")
    series = series_repo.save(series)

    # Import 1: three months already published, June through August -- "latest stored" becomes
    # 2020-08-01. Real BLS-style behaviour: the prior two months are provisional and get revised
    # on the next release.
    first_publication = [
        ProviderRecord(observed_at=datetime(2020, 6, 1, tzinfo=timezone.utc), value=100.0),
        ProviderRecord(observed_at=datetime(2020, 7, 1, tzinfo=timezone.utc), value=101.2),
        ProviderRecord(observed_at=datetime(2020, 8, 1, tzinfo=timezone.utc), value=102.5),
    ]
    # Import 2: the provider has genuinely revised June (100.0 -> 97.4) and published a new
    # September figure -- but a real live fetch only ever returns records inside the range it was
    # actually asked for. _determine_range() requests start=latest(2020-08-01) forward, so June
    # is outside the requested window and the revised value is never in this response at all --
    # exactly what a real provider would return for that exact request, not a contrivance.
    revised_publication = [
        ProviderRecord(observed_at=datetime(2020, 8, 1, tzinfo=timezone.utc), value=102.5),
        ProviderRecord(observed_at=datetime(2020, 9, 1, tzinfo=timezone.utc), value=103.9),
    ]
    factory = FakeProviderClientFactory({"fred": ScriptedRecordingClient([first_publication, revised_publication])})
    service = ImportService(
        series_repo=series_repo, provider_repo=provider_repo, import_run_repo=import_run_repo,
        observation_repo=observation_repo, import_lock=FakeImportLock(), provider_client_factory=factory,
    )

    run1 = service.run_import(series.id, TriggerType.MANUAL)
    assert run1.status.value in ("SUCCESS", "PARTIAL"), f"Import 1 failed: {run1.status.value}"

    client = factory.create_client(provider)
    run2 = service.run_import(series.id, TriggerType.MANUAL)
    assert run2.status.value in ("SUCCESS", "PARTIAL"), f"Import 2 failed: {run2.status.value}"

    # Confirm _determine_range() only fetched from latest stored (2020-08-01) forward,
    # not from June (which was revised)
    start_call_2 = client.calls[1][2]
    assert start_call_2 >= datetime(2020, 8, 1, tzinfo=timezone.utc), \
        f"Expected fetch to start at or after 2020-08-01, got {start_call_2}"

    rows = conn.execute(
        "SELECT observed_at, value FROM observation WHERE series_id=? ORDER BY observed_at", (series.id,)
    ).fetchall()
    assert len(rows) == 4, f"Expected 4 observations, got {len(rows)}"

    corrections = conn.execute(
        "SELECT c.* FROM correction c JOIN observation o ON o.id=c.observation_id WHERE o.series_id=?",
        (series.id,),
    ).fetchall()

    # DEFECT-F009 REPRODUCED: June's revision was never fetched, no correction row
    stored_june = next(r["value"] for r in rows if r["observed_at"].startswith("2020-06"))
    has_september = any(r["observed_at"].startswith("2020-09") for r in rows)

    assert stored_june == 100.0, \
        f"June value frozen at first-publication (100.0), not revised (97.4): {stored_june}"
    assert len(corrections) == 0, \
        f"No correction for June revision because fetch started at 2020-08-01: {corrections}"
    assert has_september, "September (new date) was picked up in incremental fetch"

    conn.close()
