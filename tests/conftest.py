"""Fixtures for testing the real read-only HistFinTS ATTACH boundary (D-001), never a
hand-built schema (SPEC-f009-evidence-consumption.md §6, D-009b: a fixture schema would
silently pass tests the real boundary fails).
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

PRODUCTION_DB_PATH = Path(
    os.environ.get(
        "HISTFINTS_DB_PATH",
        r"C:\Users\CarlonTinto\AppData\Local\histfints\histfints\histfints.db",
    )
)
HISTFINTS_PERSISTENCE_DIR = Path(
    os.environ.get(
        "HISTFINTS_PERSISTENCE_DIR",
        r"E:\Carlos\Documents\Mi Software\Proyectos\histfints-v3\src\histfints\persistence",
    )
)
SCHEMA_SQL_PATH = HISTFINTS_PERSISTENCE_DIR / "schema.sql"
MIGRATIONS_DIR = HISTFINTS_PERSISTENCE_DIR / "migrations"

# Production's PRAGMA user_version, verified live on 2026-08-17 (D-032). Building the test
# database up to exactly this point — from the real schema.sql plus the real migration
# files, never a hand-typed reconstruction (D-009b) — matches production's actual schema
# without needing to copy its 5+ GB data file.
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
