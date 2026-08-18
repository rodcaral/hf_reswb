"""Time-local staleness detection (D-046, SPEC §8.2).

Row-local detection: for each Series, compute days since last observation.
Governs eligibility as of each date, never retroactive.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

from hf_reswb.domain.panel import ExclusionReason, ExclusionRecord, StalenessPolicy


def detect_stale_series(
    connection: sqlite3.Connection,
    series_ids: list[int],
    analysis_date: str,
    staleness_policy: StalenessPolicy,
) -> dict[int, bool]:
    """
    Determine which Series are stale as of a specific date (time-local).

    Args:
        connection: HistFinTS read-only connection
        series_ids: Series to check
        analysis_date: Date in YYYY-MM-DD format
        staleness_policy: Policy with max_consecutive_no_trade_days

    Returns:
        Dict mapping series_id -> is_stale (bool)
    """
    if not series_ids:
        return {}

    analysis_dt = datetime.strptime(analysis_date, "%Y-%m-%d")
    max_days = staleness_policy.max_consecutive_no_trade_days

    placeholders = ",".join("?" for _ in series_ids)
    rows = connection.execute(
        f"""
        SELECT DISTINCT s.id,
          MAX(DATE(o.observed_at)) as last_observed_date
        FROM histfints.series s
        LEFT JOIN histfints.observation o ON s.id = o.series_id
        WHERE s.id IN ({placeholders})
          AND (o.observed_at IS NULL OR DATE(o.observed_at) < ?)
        GROUP BY s.id
        """,
        (*series_ids, analysis_date),
    ).fetchall()

    stale_map = {}
    for series_id in series_ids:
        stale_map[series_id] = False

    for row in rows:
        series_id = row["id"]
        last_observed = row["last_observed_date"]

        if last_observed is None:
            # No observations at all before this date
            stale_map[series_id] = True
        else:
            last_dt = datetime.strptime(last_observed, "%Y-%m-%d")
            days_since = (analysis_dt - last_dt).days
            stale_map[series_id] = days_since > max_days

    return stale_map


def get_staleness_exclusions(
    connection: sqlite3.Connection,
    series_ids: list[int],
    analysis_date: str,
    staleness_policy: StalenessPolicy,
) -> list[ExclusionRecord]:
    """
    Get staleness exclusion records for a date.

    Returns:
        List of ExclusionRecord with reason=STALE and detail showing last observed date
    """
    stale_map = detect_stale_series(
        connection, series_ids, analysis_date, staleness_policy
    )

    placeholders = ",".join("?" for _ in series_ids)
    rows = connection.execute(
        f"""
        SELECT DISTINCT s.id,
          MAX(DATE(o.observed_at)) as last_observed_date
        FROM histfints.series s
        LEFT JOIN histfints.observation o ON s.id = o.series_id
        WHERE s.id IN ({placeholders})
        GROUP BY s.id
        """,
        (*series_ids,),
    ).fetchall()

    last_obs_map = {row["id"]: row["last_observed_date"] for row in rows}

    exclusions = []
    for series_id, is_stale in stale_map.items():
        if is_stale:
            last_obs = last_obs_map.get(series_id)
            detail = f"stale since {analysis_date}" if last_obs else "no observations before this date"
            exclusions.append(
                ExclusionRecord(
                    series_id=series_id,
                    reason=ExclusionReason.STALE,
                    detail=detail,
                )
            )

    return exclusions
