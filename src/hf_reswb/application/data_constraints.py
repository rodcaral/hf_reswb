"""Data constraint handling for panel eligibility (D-046, Phase 3).

Handles incomplete availability metadata and adjustment basis constraints
per SPEC_PANEL_ELIGIBILITY.md §5A and §7.

Constraints:
- Availability status: KNOWN | UNRESOLVED (for NULL availability_date assignments)
- Adjustment basis: Match required basis (SPLIT_ADJUSTED, UNADJUSTED, or mixed)
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from hf_reswb.domain.panel import (
    ExclusionReason,
    ExclusionRecord,
)


@dataclass(frozen=True)
class AvailabilityStatus:
    """Coverage availability for a Series on a date."""
    series_id: int
    status: str  # "KNOWN" | "UNRESOLVED"
    detail: str = ""  # e.g., "NULL first/last_available_date"


def get_availability_status(
    connection: sqlite3.Connection,
    series_id: int,
) -> AvailabilityStatus:
    """
    Determine availability_status for a Series.

    Per SPEC §5A: assignment with NULL first/last_available_date is UNRESOLVED.
    Assignment with both dates populated is KNOWN.

    Args:
        connection: HistFinTS read-only connection
        series_id: Series ID

    Returns:
        AvailabilityStatus (KNOWN or UNRESOLVED)
    """
    row = connection.execute(
        """
        SELECT first_available_date, last_available_date FROM histfints.provider_assignment
        WHERE series_id = ?
        """,
        (series_id,),
    ).fetchone()

    if row is None:
        # No assignment (shouldn't happen in practice)
        return AvailabilityStatus(
            series_id=series_id,
            status="UNRESOLVED",
            detail="no provider_assignment found",
        )

    if row["first_available_date"] is None or row["last_available_date"] is None:
        return AvailabilityStatus(
            series_id=series_id,
            status="UNRESOLVED",
            detail="NULL first_available_date or last_available_date",
        )

    return AvailabilityStatus(
        series_id=series_id,
        status="KNOWN",
        detail=f"available {row['first_available_date']} to {row['last_available_date']}",
    )


def get_coverage_incomplete_exclusions(
    connection: sqlite3.Connection,
    series_ids: list[int],
) -> list[ExclusionRecord]:
    """
    Identify Series with UNRESOLVED availability status.

    Per SPEC §7: assignments with NULL availability metadata are marked UNRESOLVED
    and reported separately from other coverage issues.

    Note: Requires Tranche 2 schema (migrations 0011–0013) with
    provider_assignment.first_available_date / last_available_date columns.
    If schema doesn't have these columns, returns empty list (Tranche 2 not deployed yet).

    Args:
        connection: HistFinTS read-only connection
        series_ids: Candidate Series

    Returns:
        List of ExclusionRecord with reason=COVERAGE_INCOMPLETE
    """
    if not series_ids:
        return []

    # Check if Tranche 2 schema is present
    try:
        connection.execute(
            "SELECT first_available_date FROM histfints.provider_assignment LIMIT 1"
        )
    except sqlite3.OperationalError:
        # Tranche 2 schema not yet deployed; skip this check
        return []

    placeholders = ",".join("?" for _ in series_ids)
    rows = connection.execute(
        f"""
        SELECT DISTINCT pa.series_id
        FROM histfints.provider_assignment pa
        WHERE pa.series_id IN ({placeholders})
          AND (pa.first_available_date IS NULL OR pa.last_available_date IS NULL)
        """,
        (*series_ids,),
    ).fetchall()

    exclusions = []
    for row in rows:
        exclusions.append(
            ExclusionRecord(
                series_id=row["series_id"],
                reason=ExclusionReason.COVERAGE_INCOMPLETE,
                detail="NULL availability metadata (0.64% edge case per D-046)",
            )
        )

    return exclusions


def get_adjustment_basis(
    connection: sqlite3.Connection,
    series_id: int,
) -> str | None:
    """
    Query adjustment basis for a Series.

    Per SPEC §7: `provider.adjustment_basis` is required for adjustment_policy enforcement.
    Tranche 2 provides this field (D-044, D-045).

    Note: If Tranche 2 schema (adjustment_basis column) is not present, returns None.

    Args:
        connection: HistFinTS read-only connection
        series_id: Series ID

    Returns:
        Adjustment basis string (SPLIT_ADJUSTED, UNADJUSTED) or None if unknown or Tranche 2 not deployed
    """
    try:
        row = connection.execute(
            """
            SELECT DISTINCT p.adjustment_basis FROM histfints.provider p
            JOIN histfints.provider_assignment pa ON p.id = pa.provider_id
            WHERE pa.series_id = ?
            """,
            (series_id,),
        ).fetchone()

        if row is None:
            return None

        return row["adjustment_basis"]
    except sqlite3.OperationalError:
        # Tranche 2 schema not yet deployed
        return None


def detect_mixed_adjustment_bases(
    connection: sqlite3.Connection,
    series_ids: list[int],
) -> dict[int, list[str]]:
    """
    Detect Series whose providers have different adjustment bases.

    If a Series can be reached through multiple provider_assignments with different bases,
    this returns a mapping of series_id -> [base1, base2, ...].

    Note: Requires Tranche 2 schema (provider.adjustment_basis column).
    If schema doesn't have it, returns empty dict (Tranche 2 not deployed yet).

    Args:
        connection: HistFinTS read-only connection
        series_ids: Candidate Series

    Returns:
        Dict mapping series_id -> list of distinct adjustment_basis values found
    """
    if not series_ids:
        return {}

    # Check if Tranche 2 schema is present
    try:
        connection.execute("SELECT adjustment_basis FROM histfints.provider LIMIT 1")
    except sqlite3.OperationalError:
        # Tranche 2 schema not yet deployed; skip this check
        return {}

    placeholders = ",".join("?" for _ in series_ids)
    rows = connection.execute(
        f"""
        SELECT DISTINCT pa.series_id, p.adjustment_basis
        FROM histfints.provider_assignment pa
        JOIN histfints.provider p ON pa.provider_id = p.id
        WHERE pa.series_id IN ({placeholders})
          AND p.adjustment_basis IS NOT NULL
        """,
        (*series_ids,),
    ).fetchall()

    bases_by_series: dict[int, set[str]] = {}
    for row in rows:
        series_id = row["series_id"]
        if series_id not in bases_by_series:
            bases_by_series[series_id] = set()
        bases_by_series[series_id].add(row["adjustment_basis"])

    # Return only those with mixed bases (more than one value)
    mixed = {}
    for series_id, bases in bases_by_series.items():
        if len(bases) > 1:
            mixed[series_id] = sorted(bases)

    return mixed


def get_adjustment_basis_mismatch_exclusions(
    connection: sqlite3.Connection,
    series_ids: list[int],
    required_basis: str | None = None,
) -> list[ExclusionRecord]:
    """
    Identify Series with mismatched adjustment bases.

    Per SPEC §7: if `adjustment_policy` requires a specific basis (e.g., all must be
    SPLIT_ADJUSTED), exclude Series that don't match. If no required_basis specified,
    exclude only those with mixed bases within themselves.

    Note: Requires Tranche 2 schema (provider.adjustment_basis column).
    If schema doesn't have it, returns empty list (Tranche 2 not deployed yet).

    Args:
        connection: HistFinTS read-only connection
        series_ids: Candidate Series
        required_basis: Required adjustment basis (e.g., "SPLIT_ADJUSTED"), or None to skip

    Returns:
        List of ExclusionRecord with reason=ADJUSTMENT_BASIS_MISMATCH
    """
    if not series_ids:
        return []

    # Check if Tranche 2 schema is present
    try:
        connection.execute("SELECT adjustment_basis FROM histfints.provider LIMIT 1")
    except sqlite3.OperationalError:
        # Tranche 2 schema not yet deployed; skip this check
        return []

    exclusions = []

    # First, detect series with mixed bases
    mixed = detect_mixed_adjustment_bases(connection, series_ids)
    for series_id, bases in mixed.items():
        exclusions.append(
            ExclusionRecord(
                series_id=series_id,
                reason=ExclusionReason.ADJUSTMENT_BASIS_MISMATCH,
                detail=f"mixed bases: {', '.join(bases)}",
            )
        )

    # If a required basis is specified, exclude mismatches
    if required_basis:
        placeholders = ",".join("?" for _ in series_ids)
        rows = connection.execute(
            f"""
            SELECT DISTINCT pa.series_id, p.adjustment_basis
            FROM histfints.provider_assignment pa
            JOIN histfints.provider p ON pa.provider_id = p.id
            WHERE pa.series_id IN ({placeholders})
              AND p.adjustment_basis IS NOT NULL
              AND p.adjustment_basis != ?
            """,
            (*series_ids, required_basis),
        ).fetchall()

        mismatched_ids = {row["series_id"] for row in rows}
        already_excluded = {e.series_id for e in exclusions}

        for series_id in mismatched_ids:
            if series_id not in already_excluded:
                basis = get_adjustment_basis(connection, series_id)
                exclusions.append(
                    ExclusionRecord(
                        series_id=series_id,
                        reason=ExclusionReason.ADJUSTMENT_BASIS_MISMATCH,
                        detail=f"basis={basis}, required={required_basis}",
                    )
                )

    return exclusions
