"""F-033 quarantine integration (DOM-2 ordering, item 1 of 3).

`histfints.observation_quarantine_active(observation_id)` is HistFinTS's own canonical,
read-only view (migration 0027) over `observation_quarantine_case` /
`observation_quarantine_member`. Presence of an `observation.id` in that view is the
*complete* Workbench predicate that the stored observation is CONFIRMED_SYNTHETIC and must
not serve as genuine observed-market-price evidence.

This module holds nothing beyond that single query. It does not reproduce case selection,
provenance modes, `import_run_id`/run-inventory logic, or any F-033 date range — all of that
stays HistFinTS-side. Consumers call `quarantined_observation_ids()` against the exact set of
observation ids they are about to treat as evidence, then decide for themselves what
"excluded" means for their own calculation (row-local exclusion, panel/dispersion/calibration
input exclusion, or — for a continuity-sensitive calculation — refusing to treat the
observations on either side of an excluded row as newly adjacent).
"""
from __future__ import annotations

import sqlite3
from collections.abc import Sequence


def quarantine_view_exists(connection: sqlite3.Connection) -> bool:
    row = connection.execute(
        "SELECT name FROM histfints.sqlite_master WHERE type='view' "
        "AND name='observation_quarantine_active'"
    ).fetchone()
    return row is not None


def quarantined_observation_ids(
    connection: sqlite3.Connection, observation_ids: Sequence[int]
) -> set[int]:
    """Returns the subset of `observation_ids` that are CONFIRMED_SYNTHETIC per HistFinTS's
    `observation_quarantine_active` view. Read-only; queries HistFinTS's own view verbatim.

    Against a HistFinTS copy older than migration 0027 (the view does not exist yet -- e.g. an
    unmigrated test fixture predating F-033 quarantine, never today's actual production
    schema, which is already at 0027) this returns an empty set rather than raising: no
    quarantine data exists to consult, so nothing can be classified as CONFIRMED_SYNTHETIC yet
    -- the same "table/view absent" treatment this codebase already gives
    `provider_event`/`observation_correction` (reconciliation_service.py), not a silent
    reinterpretation of the predicate."""
    if not observation_ids:
        return set()
    if not quarantine_view_exists(connection):
        return set()
    placeholders = ",".join("?" for _ in observation_ids)
    rows = connection.execute(
        f"""
        SELECT observation_id FROM histfints.observation_quarantine_active
        WHERE observation_id IN ({placeholders})
        """,
        list(observation_ids),
    ).fetchall()
    return {r["observation_id"] for r in rows}
