"""Dispersion analysis for aggregate suppression (D-046, SPEC §8.3).

Computes dispersion metric across panel members.
When metric exceeds threshold, aggregate result is SUPPRESSED (not published).
Underlying observations and diagnostics remain available for inspection.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class DispersionMetrics:
    """Dispersion measures for a panel."""
    coefficient_of_variation: float  # std / mean of residuals
    interquartile_range: float  # IQR of residuals
    max_absolute_residual: float


def compute_dispersion_metrics(member_residuals: list[float]) -> DispersionMetrics:
    """
    Compute dispersion metrics from member residuals.

    Args:
        member_residuals: List of (member_rate - consensus_rate) / consensus_rate values

    Returns:
        DispersionMetrics with multiple measures
    """
    if not member_residuals:
        return DispersionMetrics(
            coefficient_of_variation=0.0,
            interquartile_range=0.0,
            max_absolute_residual=0.0,
        )

    # Coefficient of variation (std / mean absolute value)
    mean_abs = statistics.mean(abs(r) for r in member_residuals)
    if mean_abs > 0:
        try:
            std = statistics.stdev(member_residuals)
            cv = std / mean_abs
        except (ValueError, statistics.StatisticsError):
            cv = 0.0
    else:
        cv = 0.0

    # Interquartile range
    sorted_residuals = sorted(member_residuals)
    n = len(sorted_residuals)
    if n >= 4:
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        iqr = sorted_residuals[q3_idx] - sorted_residuals[q1_idx]
    else:
        iqr = 0.0

    # Max absolute residual
    max_abs = max(abs(r) for r in member_residuals) if member_residuals else 0.0

    return DispersionMetrics(
        coefficient_of_variation=cv,
        interquartile_range=iqr,
        max_absolute_residual=max_abs,
    )


def should_suppress_result(
    dispersion_value: float,
    threshold: float,
) -> bool:
    """
    Determine if result should be suppressed based on dispersion.

    Args:
        dispersion_value: Computed dispersion metric (e.g., coefficient of variation)
        threshold: Maximum acceptable dispersion (provisional)

    Returns:
        True if dispersion > threshold (suppress result)
    """
    return dispersion_value > threshold
