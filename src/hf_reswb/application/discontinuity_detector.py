"""Minimal boundary detector (SPEC_F009_EVIDENCE_CONSUMPTION.md §4.2 step 1).

Deliberately simple: a single-step move beyond `step_threshold` that persists through both
horizons without reverting. Trading-calendar-aware persistence is blocked on Q-027 (open) —
this counts calendar days and every calculation records that basis explicitly (SPEC §9), so
it is never mistaken for a trading-day count.

`step_threshold` is a candidate-generation filter, not a financial definition of a
discontinuity (D-036). Move size alone is not the discriminator — the project's own
evidence rules that out (a +19.1% move that was a market-wide FX shift, a -18.3% move that
reverted, a -49.4% move that persisted and was confirmed real). Persistence is what the
project has actually validated; do not present the threshold as calibrated on its own.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DetectorParams:
    step_threshold: float = 0.20
    persistence_horizons_days: tuple[int, int] = (15, 60)
    persistence_tolerance: float = 0.10


@dataclass(frozen=True)
class Boundary:
    index: int  # position, within the input arrays, of the first post-boundary observation
    value_before: float
    value_after: float
    step_factor: float  # value_after / value_before


def detect_boundaries(
    values: list[float], params: DetectorParams
) -> list[Boundary]:
    boundaries: list[Boundary] = []
    for i in range(1, len(values)):
        before, after = values[i - 1], values[i]
        if before == 0:
            continue
        step_factor = after / before
        if abs(1.0 - step_factor) < params.step_threshold:
            continue
        if not _persists(values, i, params):
            continue
        boundaries.append(
            Boundary(index=i, value_before=before, value_after=after, step_factor=step_factor)
        )
    return boundaries


def _persists(values: list[float], boundary_index: int, params: DetectorParams) -> bool:
    level = values[boundary_index]
    if level == 0:
        return False
    last_index = len(values) - 1
    for horizon in params.persistence_horizons_days:
        check_index = min(boundary_index + horizon, last_index)
        if abs(1.0 - values[check_index] / level) > params.persistence_tolerance:
            return False
    return True
