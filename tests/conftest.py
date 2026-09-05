"""Fixtures for testing the real read-only HistFinTS ATTACH boundary (D-001), never a
hand-built schema (SPEC_F009_EVIDENCE_CONSUMPTION.md §6, D-009b: a fixture schema would
silently pass tests the real boundary fails).
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

def _require_env(name: str) -> Path:
    """No fallback, by design (restructure Decision 5b): a wrong silent default is worse
    than a loud failure naming exactly what's missing and how to set it."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set. This test suite reads HistFinTS's real database and "
            f"source tree directly (D-001) and has no hardcoded fallback path -- set "
            f"{name} explicitly, e.g.:\n"
            f'  $env:{name} = "C:\\path\\to\\target"   (PowerShell)\n'
            f"  export {name}=/path/to/target           (bash)"
        )
    return Path(value)


PRODUCTION_DB_PATH = _require_env("HISTFINTS_DB_PATH")
HISTFINTS_PERSISTENCE_DIR = _require_env("HISTFINTS_PERSISTENCE_DIR")
SCHEMA_SQL_PATH = HISTFINTS_PERSISTENCE_DIR / "schema.sql"
MIGRATIONS_DIR = HISTFINTS_PERSISTENCE_DIR / "migrations"

# Production's PRAGMA user_version, verified live on 2026-08-17 (D-032). Building the test
# database up to exactly this point — from the real schema.sql plus the real migration
# files, never a hand-typed reconstruction (D-009b) — matches production's actual schema
# without needing to copy its 5+ GB data file.
#
# Re-verified live 2026-08-26: production has since advanced to user_version=17 (migrations
# 0011-0017, including 0017's SUPERSEDED status support) — deliberately NOT bumped here, since
# doing so broke multiple unrelated existing tests (test_reconciliation_boundary.py,
# panel-eligibility phase1/phase2 delisted/trade-evidence cases) that assume the v10 schema
# shape. Bumping this shared constant is a separate, cross-cutting infrastructure decision with
# its own blast radius — out of scope for one feature's tests. SUPERSEDED-specific tests use
# their own isolated, explicitly-versioned fixture instead (see
# tests/test_panel_eligibility_superseded.py's `_histfints_copy_v17`).
PRODUCTION_USER_VERSION = 10


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_histfints_source() -> None:
    if not SCHEMA_SQL_PATH.exists():
        pytest.skip(
            f"histfints-v3 schema not found at {SCHEMA_SQL_PATH}; "
            "set HISTFINTS_PERSISTENCE_DIR to the histfints-v3 persistence directory"
        )


def _build_histfints_db(target: Path, *, up_to_version: int) -> Path:
    _require_histfints_source()
    conn = sqlite3.connect(target)
    try:
        conn.executescript(SCHEMA_SQL_PATH.read_text())
        for migration_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = int(migration_file.stem.split("_", 1)[0])
            if version > up_to_version:
                continue
            conn.executescript(migration_file.read_text())
        conn.execute(f"PRAGMA user_version = {up_to_version}")
        conn.commit()
    finally:
        conn.close()
    return target


@pytest.fixture
def histfints_copy(tmp_path) -> Path:
    """A database built from HistFinTS's own real `schema.sql` plus its real migration
    files, taken up to production's actual current version (`user_version = 10`, D-032) —
    the real schema, not a reconstruction of it, without copying the multi-gigabyte
    production data file wholesale."""
    return _build_histfints_db(tmp_path / "histfints_copy.db", up_to_version=PRODUCTION_USER_VERSION)


@pytest.fixture
def histfints_copy_migrated(tmp_path) -> Path:
    """The same real schema, with migrations 0011-0013 additionally applied — for testing
    the `explained` verdict, which SPEC §6 states can only be tested against a migrated
    fixture, never against production as it stands today."""
    return _build_histfints_db(tmp_path / "histfints_copy_migrated.db", up_to_version=13)


@pytest.fixture
def histfints_copy_v17(tmp_path) -> Path:
    """The real schema through migration 0017 (`series.status = 'SUPERSEDED'` support,
    2026-08-26) — isolated from the shared `PRODUCTION_USER_VERSION`/`histfints_copy` fixture
    deliberately, since bumping that shared constant to 17 broke multiple unrelated existing
    tests that assume the v10 schema shape. Use this fixture only for tests that specifically
    need SUPERSEDED (or another 0011-0017 migration) support; everything else should keep using
    `histfints_copy`."""
    return _build_histfints_db(tmp_path / "histfints_copy_v17.db", up_to_version=17)


@pytest.fixture
def histfints_copy_v27(tmp_path) -> Path:
    """The real schema through migration 0027 (`observation_quarantine_case`/
    `observation_quarantine_member` + the `observation_quarantine_active` view, F-033
    quarantine integration) -- isolated from the shared `PRODUCTION_USER_VERSION`/
    `histfints_copy` fixture for the same reason as `histfints_copy_v17`: bumping the shared
    constant has its own blast radius, out of scope for one feature's tests. Use this fixture
    only for tests that specifically need quarantine support."""
    return _build_histfints_db(tmp_path / "histfints_copy_v27.db", up_to_version=27)


def insert_fixture_quarantine(
    db_path: Path,
    *,
    series_id: int,
    provider_assignment_id: int,
    observation_ids: list[int],
    provenance_mode: str = "BACKFILL_LABELED",
) -> int:
    """Quarantines the given observation ids under one new `observation_quarantine_case`/
    `observation_quarantine_member` pair, built directly against HistFinTS's own migration-0027
    schema -- a test fixture, not a reimplementation of F-033 curation logic (which stays
    entirely HistFinTS-side; Workbench only ever reads `observation_quarantine_active`)."""
    conn = sqlite3.connect(db_path)
    try:
        now = _now()
        run_id = conn.execute(
            "INSERT INTO import_run (provider_assignment_id, trigger_type, status, started_at, "
            "ended_at, created_at, updated_at) VALUES (?, 'MANUAL', 'SUCCESS', ?, ?, ?, ?)",
            (provider_assignment_id, now, now, now, now),
        ).lastrowid
        case_id = conn.execute(
            "INSERT INTO observation_quarantine_case (series_id, provenance_mode, disposition, "
            "originating_import_run_id, rationale, adjudication_reference, recorded_at, created_at) "
            "VALUES (?, ?, 'CONFIRMED_SYNTHETIC', ?, ?, ?, ?, ?)",
            (series_id, provenance_mode, run_id, "test fixture", "TEST-FIXTURE", now, now),
        ).lastrowid
        for obs_id in observation_ids:
            row = conn.execute(
                "SELECT value, open, high, low, volume, import_run_id FROM observation WHERE id = ?",
                (obs_id,),
            ).fetchone()
            conn.execute(
                "INSERT INTO observation_quarantine_member (case_id, observation_id, snapshot_value, "
                "snapshot_open, snapshot_high, snapshot_low, snapshot_volume, snapshot_import_run_id, "
                "created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (case_id, obs_id, row[0], row[1], row[2], row[3], row[4], row[5], now),
            )
        conn.commit()
        return case_id
    finally:
        conn.close()


@pytest.fixture
def real_production_db_readonly_path() -> Path:
    """The actual production file, used read-only and never copied or written to — for the
    one test that must prove the boundary holds against the real thing, not a
    same-schema stand-in."""
    if not PRODUCTION_DB_PATH.exists():
        pytest.skip(f"real HistFinTS database not found at {PRODUCTION_DB_PATH}")
    return PRODUCTION_DB_PATH


def insert_fixture_series_with_step(
    db_path: Path, *, label: str, step_factor: float, tail_days: int = 70
) -> dict:
    """Constructs a Series with a known, deliberate discontinuity. Per D-009, no real Series
    in this database has lived through a triggering event, so the boundary must be built,
    not searched for."""
    conn = sqlite3.connect(db_path)
    try:
        provider_row = conn.execute(
            "SELECT id, display_name FROM provider WHERE implementation_key='yahoo_finance' LIMIT 1"
        ).fetchone()
        now = _now()
        if provider_row is None:
            provider_id = conn.execute(
                "INSERT INTO provider (display_name, implementation_key, kind, created_at, updated_at) "
                "VALUES (?, 'yahoo_finance', 'API', ?, ?)",
                (f"Yahoo Finance", now, now),
            ).lastrowid
        else:
            provider_id = provider_row[0]

        series_id = conn.execute(
            "INSERT INTO series (label, series_type, configured_interval, backfill_start_date, "
            "status, created_at, updated_at) VALUES (?, 'STOCK', '1d', '2020-01-01', 'ACTIVE', ?, ?)",
            (label, now, now),
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

        boundary_day = datetime(2020, 8, 31, tzinfo=timezone.utc)
        before_days = [boundary_day - timedelta(days=d) for d in range(4, 0, -1)]
        after_days = [boundary_day + timedelta(days=d) for d in range(0, tail_days)]

        value_before = 630.0
        value_after = round(value_before * step_factor, 4)

        def insert_observation(observed_at: datetime, value: float) -> int:
            return conn.execute(
                "INSERT INTO observation (series_id, import_run_id, observed_at, value, "
                "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (series_id, run_id, observed_at.isoformat(), value, now, now),
            ).lastrowid

        for day in before_days:
            insert_observation(day, value_before)
        boundary_observation_id = None
        for i, day in enumerate(after_days):
            obs_id = insert_observation(day, value_after)
            if i == 0:
                boundary_observation_id = obs_id

        conn.commit()
        return {
            "series_id": series_id,
            "provider_id": provider_id,
            "provider_display_name": provider_row[1] if provider_row else "Yahoo Finance",
            "assignment_id": assignment_id,
            "import_run_id": run_id,
            "boundary_date": after_days[0].isoformat(),
            "boundary_observation_id": boundary_observation_id,
            "period_start": before_days[0].isoformat(),
            "period_end": after_days[-1].isoformat(),
        }
    finally:
        conn.close()


def insert_fixture_split_event(
    db_path: Path, *, series_id: int, provider_id: int, event_date: str, ratio: float
) -> int:
    """Inserts a `provider_event` SPLIT row matching a constructed discontinuity, for
    testing the `explained` verdict (SPEC §6). Requires migrations 0011-0013 applied."""
    conn = sqlite3.connect(db_path)
    try:
        event_id = conn.execute(
            "INSERT INTO provider_event (series_id, provider_id, event_type, event_date, "
            "acquired_at, provider_source_id, structured_data, provenance_note, created_at) "
            "VALUES (?, ?, 'SPLIT', ?, ?, ?, ?, ?, ?)",
            (
                series_id, provider_id, event_date, _now(), f"fixture-split-{series_id}",
                json.dumps({"ratio": ratio}), "constructed test fixture", _now(),
            ),
        ).lastrowid
        conn.commit()
        return event_id
    finally:
        conn.close()
