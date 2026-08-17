"""Workbench-side persistence: the Workbench's own SQLite file, plus a read-only ATTACH to
HistFinTS alongside it (D-001).

`histfints_readonly=False` exists only for test setup that must write a constructed
discontinuity into a disposable copy of the production file before the code under test
attaches it for real. Production code must never pass it.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def _to_sqlite_uri(path: str | Path, *, mode: str) -> str:
    return f"{Path(path).resolve().as_uri()}?mode={mode}"


def connect(
    workbench_db_path: str | Path,
    histfints_db_path: str | Path,
    *,
    histfints_readonly: bool = True,
) -> sqlite3.Connection:
    connection = sqlite3.connect(_to_sqlite_uri(workbench_db_path, mode="rwc"), uri=True)
    connection.row_factory = sqlite3.Row
    connection.executescript(_SCHEMA_PATH.read_text())

    mode = "ro" if histfints_readonly else "rw"
    connection.execute(
        f"ATTACH DATABASE '{_to_sqlite_uri(histfints_db_path, mode=mode)}' AS histfints"
    )
    return connection


def table_exists(connection: sqlite3.Connection, schema: str, table_name: str) -> bool:
    row = connection.execute(
        f"SELECT name FROM {schema}.sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None
