"""Panel eligibility integration with observation-suitability (D-046, Phase 2).

Bridges frozen observation-suitability layer (classify_series → derive_calendar → apply_calendar)
to panel eligibility decisions. Operates downstream per SPEC-panel-eligibility.md §2.3.

Integration points:
- Trade evidence: Exclude NO_TRADE_REPORTED by default (liquidity criterion per SPEC §8.2)
- Session status: Display-only context, never gates (D-036 principle)
- Calendar: Align panel dates to confirmed trading sessions (informational)
"""
from __future__ import annotations

import sqlite3
from datetime import datetime

from hf_reswb.domain.panel import (
    ExclusionReason,
    ExclusionRecord,
    PanelEligibilityParameters,
)
from hf_reswb.domain.suitability import TradeEvidence


def get_trade_evidence_exclusions(
    connection: sqlite3.Connection,
    series_ids: list[int],
    analysis_date: str,
) -> list[ExclusionRecord]:
    """
    Identify Series with NO_TRADE_REPORTED on analysis_date.

    Observation-suitability classification (Axis A, D-035) marks rows as NO_TRADE_REPORTED
    when they meet all conjunctive conditions: volume=0 AND OHLC-collapsed AND
    equals-prior-close. Per SPEC §8.2, these are excluded by default (liquidity criterion).

    Args:
        connection: HistFinTS read-only connection
        series_ids: Candidate Series
        analysis_date: Date in YYYY-MM-DD format

    Returns:
        List of ExclusionRecord with reason=NO_TRADE_REPORTED for series without
        TRADE_OBSERVED on this date
    """
    if not series_ids:
        return []

    placeholders = ",".join("?" for _ in series_ids)
    rows = connection.execute(
        f"""
        SELECT DISTINCT histfints_series_id
        FROM observation_suitability
        WHERE histfints_series_id IN ({placeholders})
          AND observed_date = ?
          AND trade_evidence = ?
        """,
        (*series_ids, analysis_date, TradeEvidence.NO_TRADE_REPORTED.value),
    ).fetchall()

    excluded_ids = {row["histfints_series_id"] for row in rows}
    exclusions = []
    for series_id in excluded_ids:
        exclusions.append(
            ExclusionRecord(
                series_id=series_id,
                reason=ExclusionReason.NO_TRADE_REPORTED,
                detail=f"observation marked NO_TRADE_REPORTED on {analysis_date}",
            )
        )

    return exclusions


def get_trade_evidence_for_date(
    connection: sqlite3.Connection,
    series_id: int,
    analysis_date: str,
) -> TradeEvidence | None:
    """
    Query observation-suitability trade evidence classification for a Series/date.

    Returns:
        TradeEvidence enum value (TRADE_OBSERVED, NO_TRADE_REPORTED, TRADE_EVIDENCE_UNRESOLVED)
        or None if no observation exists for that date
    """
    row = connection.execute(
        """
        SELECT trade_evidence FROM observation_suitability
        WHERE histfints_series_id = ? AND observed_date = ?
        LIMIT 1
        """,
        (series_id, analysis_date),
    ).fetchone()

    if row is None:
        return None

    return TradeEvidence(row["trade_evidence"])


def get_session_status_for_date(
    connection: sqlite3.Connection,
    series_id: int,
    analysis_date: str,
):
    """
    Query observation-suitability session status (Axis B, informational only).

    Per D-036 §4, session status is display context, never a gating criterion.
    Serves to explain to the user why a date was included or excluded on other grounds.

    Returns:
        SessionStatus enum value or None if no classification exists
    """
    row = connection.execute(
        """
        SELECT session_status FROM observation_suitability
        WHERE histfints_series_id = ? AND observed_date = ?
        LIMIT 1
        """,
        (series_id, analysis_date),
    ).fetchone()

    if row is None:
        return None

    from hf_reswb.domain.suitability import SessionStatus
    return SessionStatus(row["session_status"])


def validate_suitability_coverage(
    connection: sqlite3.Connection,
    series_ids: list[int],
    period_start: str,
    period_end: str,
) -> tuple[bool, list[tuple[int, str]]]:
    """
    Verify that observation-suitability classification exists for all Series in period.

    Per SPEC §6 (suitability_run discipline), classify_series() must have been run
    for every contributing Series over the requested period before panel eligibility
    can be computed. This validates that assumption.

    Args:
        connection: HistFinTS connection
        series_ids: Series to check
        period_start: Period start (YYYY-MM-DD)
        period_end: Period end (YYYY-MM-DD)

    Returns:
        (all_covered, missing_list) where missing_list contains (series_id, reason) tuples
    """
    missing = []

    for series_id in series_ids:
        # Check if any suitability_run covers this series and period
        row = connection.execute(
            """
            SELECT COUNT(*) AS c FROM suitability_run
            WHERE series_id = ? AND period_start <= ? AND period_end >= ?
            """,
            (series_id, period_start, period_end),
        ).fetchone()

        if row["c"] == 0:
            missing.append((series_id, f"no suitability_run covering period [{period_start}, {period_end}]"))

    return len(missing) == 0, missing
