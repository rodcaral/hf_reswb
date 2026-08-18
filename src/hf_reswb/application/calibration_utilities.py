"""Calibration utility functions for panel eligibility parameters (D-046, Phase 5).

Provides helper functions to analyze historical panel data and compute statistics
for staleness and dispersion calibration. These utilities are used by the calibration
study to generate empirical evidence for parameter tuning.
"""
from __future__ import annotations

import sqlite3
import statistics
from datetime import datetime


def compute_staleness_lengths(
    connection: sqlite3.Connection,
    series_ids: list[int],
    period_start: str,
    period_end: str,
) -> dict[int, list[int]]:
    """
    Compute staleness lengths (days between consecutive observations) for each Series.

    Args:
        connection: Read-only HistFinTS connection
        series_ids: Series to analyze
        period_start: Analysis period start (YYYY-MM-DD)
        period_end: Analysis period end (YYYY-MM-DD)

    Returns:
        Dict mapping series_id -> list of staleness lengths in days
    """
    staleness_by_series: dict[int, list[int]] = {s: [] for s in series_ids}

    placeholders = ",".join("?" for _ in series_ids)
    rows = connection.execute(
        f"""
        SELECT series_id, observed_at
        FROM histfints.observation
        WHERE series_id IN ({placeholders})
          AND DATE(observed_at) BETWEEN ? AND ?
        ORDER BY series_id, observed_at
        """,
        (*series_ids, period_start, period_end),
    ).fetchall()

    # Group by series and compute gaps
    current_series = None
    prior_date = None

    for row in rows:
        series_id = row["series_id"]
        observed_date = row["observed_at"][:10]  # Extract date part

        if series_id != current_series:
            current_series = series_id
            prior_date = None

        if prior_date is not None:
            obs_dt = datetime.strptime(observed_date, "%Y-%m-%d")
            prior_dt = datetime.strptime(prior_date, "%Y-%m-%d")
            days_gap = (obs_dt - prior_dt).days
            if days_gap > 0:
                staleness_by_series[series_id].append(days_gap)

        prior_date = observed_date

    return staleness_by_series


def compute_staleness_statistics(
    staleness_by_series: dict[int, list[int]]
) -> dict[str, float | int]:
    """
    Compute summary statistics on staleness lengths.

    Args:
        staleness_by_series: Dict from compute_staleness_lengths

    Returns:
        Dict with keys: min, max, median, mean, p25, p75, p95, count_series, count_gaps
    """
    all_lengths = []
    for lengths in staleness_by_series.values():
        all_lengths.extend(lengths)

    if not all_lengths:
        return {
            "min": 0, "max": 0, "median": 0, "mean": 0.0,
            "p25": 0, "p75": 0, "p95": 0,
            "count_series": 0, "count_gaps": 0,
        }

    sorted_lengths = sorted(all_lengths)
    count = len(sorted_lengths)

    def percentile(p: int) -> int:
        idx = int(count * p / 100)
        return sorted_lengths[min(idx, count - 1)]

    return {
        "min": min(sorted_lengths),
        "max": max(sorted_lengths),
        "median": statistics.median(sorted_lengths),
        "mean": statistics.mean(sorted_lengths),
        "p25": percentile(25),
        "p75": percentile(75),
        "p95": percentile(95),
        "count_series": len(staleness_by_series),
        "count_gaps": count,
    }


def compute_panel_depth_by_date(
    connection: sqlite3.Connection,
    series_ids: list[int],
    period_start: str,
    period_end: str,
) -> dict[str, int]:
    """
    Compute panel member count (depth) for each date in the period.

    Panel depth on a date = count of Series with at least one observation on or before that date.

    Args:
        connection: Read-only HistFinTS connection
        series_ids: Series to analyze
        period_start: Analysis period start (YYYY-MM-DD)
        period_end: Analysis period end (YYYY-MM-DD)

    Returns:
        Dict mapping date (YYYY-MM-DD) -> member count
    """
    depth_by_date: dict[str, int] = {}

    placeholders = ",".join("?" for _ in series_ids)
    rows = connection.execute(
        f"""
        SELECT DISTINCT DATE(o.observed_at) as obs_date, s.id
        FROM histfints.series s
        LEFT JOIN histfints.observation o ON s.id = o.series_id
        WHERE s.id IN ({placeholders})
          AND (o.observed_at IS NULL OR DATE(o.observed_at) <= ?)
        ORDER BY obs_date
        """,
        (*series_ids, period_end),
    ).fetchall()

    # Count unique series per date
    series_by_date: dict[str, set[int]] = {}
    for row in rows:
        obs_date = row["obs_date"]
        if obs_date is None:
            continue
        if obs_date not in series_by_date:
            series_by_date[obs_date] = set()
        series_by_date[obs_date].add(row["id"])

    # Convert to depth counts
    for date, series_set in series_by_date.items():
        depth_by_date[date] = len(series_set)

    return depth_by_date


def estimate_threshold_impact(
    staleness_statistics: dict[str, float | int],
    candidate_threshold: int,
) -> dict[str, float | int]:
    """
    Estimate impact of a staleness threshold on panel membership.

    Rough estimate: how many staleness gaps exceed the threshold?

    Args:
        staleness_statistics: Dict from compute_staleness_statistics
        candidate_threshold: Candidate max_consecutive_no_trade_days value

    Returns:
        Dict with impact metrics: affected_proportion, specificity, false_positive_estimate
    """
    # Simplified estimate based on distribution
    # Real calibration would need full gap analysis
    median = staleness_statistics.get("median", 0)
    p95 = staleness_statistics.get("p95", 0)

    if p95 == 0:
        return {"affected_proportion": 0.0, "specificity": 1.0}

    # Rough heuristic: gaps > threshold affect ~(p95-threshold)/(p95-median) proportion
    if p95 > median:
        affected_proportion = max(0.0, 1.0 - (candidate_threshold - median) / (p95 - median))
    else:
        affected_proportion = 0.0

    return {
        "affected_proportion": affected_proportion,
        "specificity": 1.0 - affected_proportion,
    }
