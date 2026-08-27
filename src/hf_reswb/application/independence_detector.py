"""Cross-sectional independence detection for calibration inputs.

Codifies, as reusable infrastructure, the diagnostic method developed and repeatedly
re-verified during the F-033 investigation (2026-08-18/19): a candidate calibration
cohort's members must be independently-sourced observations, not values sharing one
computed origin. Six of seven new-CEDEAR pairs were found to carry an identical implied-FX
value to IEEE double-precision machine epsilon (relative range 2.25e-16) — not "highly
correlated," but the same floating-point number. Genuinely independent instruments under a
shared macro factor (the pattern this project separately verified for BABA/BIDU/UBER/GLD and
for the SECONDARY cohort's YPF/Banco Macro/Pampa Energía) show real, non-zero dispersion
even while correlated.

`MACHINE_EPSILON_RELATIVE_TOLERANCE` below is a numerical-precision bound, not a financial
or statistical threshold. It distinguishes "the same computed number" from "a different
number that happens to be close" and is not calibrated to, or tunable per, any asset class,
market, or panel-eligibility parameter. Do not treat it as a dispersion_threshold candidate
(D-046) — it answers a different question (is this data point independent at all?), upstream
of any calibration question (how much should independent members be allowed to disagree?).

This module draws no calibration conclusion. It classifies inputs so a calibration attempt
can refuse to proceed on non-independent members, the same judgment call this project made
by hand for F-033 before any calibration statistic was computed on the affected cohort.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from enum import Enum

MACHINE_EPSILON_RELATIVE_TOLERANCE = 1e-8
"""Relative range below this is indistinguishable from IEEE 754 double-precision rounding
noise (true epsilon ~2.22e-16; this tolerance is set two orders of magnitude looser to absorb
ordinary floating-point arithmetic drift across different computation paths, while remaining
many orders of magnitude tighter than any real bid/ask spread, quote-timing difference, or
market microstructure effect). See DEFECT-F033.md and RATIO_DIAGNOSIS_2026-08-19.md (docs/evidence/) for the
empirical basis: real independent CEDEARs showed relative ranges of 1-91%; the circular ones
showed 2.25e-16."""


class IndependenceFlag(str, Enum):
    """Classification of one series relative to a comparison group, on a shared date/return
    basis. Not a calibration parameter — a data-quality gate upstream of calibration."""

    EXACT_IDENTITY = "EXACT_IDENTITY"
    """Values (or returns) match the group to within MACHINE_EPSILON_RELATIVE_TOLERANCE on
    every checked date. Consistent with a shared computed origin (F-033 signature)."""

    RETURNS_LOCKED = "RETURNS_LOCKED"
    """Levels differ (no EXACT_IDENTITY on values), but day-over-day percent changes match
    the group to within MACHINE_EPSILON_RELATIVE_TOLERANCE on every checked transition. A
    ratio/scale correction cannot resolve this — correlation of returns is scale-invariant by
    construction, so this indicates the same shared-origin problem at one remove (observed
    2026-08-19, when F-033's exact-level signature resolved but return-lockstep did not)."""

    INDEPENDENT = "INDEPENDENT"
    """Neither values nor returns are locked to the comparison group beyond
    MACHINE_EPSILON_RELATIVE_TOLERANCE. May still be highly correlated (a real, expected
    property of instruments sharing a macro factor) — high correlation alone is not flagged."""


@dataclass(frozen=True)
class PairwiseIdentityResult:
    series_key: str
    compared_against: str
    relative_range_levels: float
    relative_range_returns: float | None
    flag: IndependenceFlag


@dataclass(frozen=True)
class IndependenceReport:
    """Per-series classification against the rest of a candidate cohort, plus the
    cohort's effective independent width — the number of members that remain after
    collapsing every EXACT_IDENTITY/RETURNS_LOCKED group to one representative."""

    results: list[PairwiseIdentityResult]
    effective_independent_width: int
    groups: list[list[str]] = field(default_factory=list)
    """Each inner list is a set of series_keys classified as sharing one origin (including
    singleton groups for independent series)."""


def relative_range(values: list[float]) -> float:
    """(max - min) / |median|, the cross-sectional dispersion primitive this module and
    `provenance_guard` both build on. 0.0 for empty input or a zero median."""
    if not values:
        return 0.0
    median = statistics.median(values)
    if median == 0:
        return 0.0
    return (max(values) - min(values)) / abs(median)


def day_over_day_returns(values_by_date: dict[str, float]) -> dict[str, float]:
    """Percent change from the previous date, in ascending date order. The first date has
    no return and is omitted."""
    dates = sorted(values_by_date)
    out: dict[str, float] = {}
    for prior, current in zip(dates, dates[1:]):
        v0, v1 = values_by_date[prior], values_by_date[current]
        if v0 == 0:
            continue
        out[current] = (v1 - v0) / v0
    return out


def classify_cohort_independence(
    values_by_series: dict[str, dict[str, float]],
) -> IndependenceReport:
    """Classify every series in a candidate cohort against the group's per-date median.

    Args:
        values_by_series: series_key -> {date -> value}. Values should already be on a
            comparable basis (e.g. implied FX, not raw price levels of heterogeneously-scaled
            instruments — that is a units problem this function does not solve).

    Returns:
        IndependenceReport with a flag per series and the cohort's effective independent
        width (the number of series remaining after collapsing shared-origin groups).

    Note on method: each series is compared against the **per-date median of the whole
    cohort**, not a pairwise range across all members — this isolates one outlier (e.g. a
    QQQ-like exception) from being averaged into every other series' statistic, matching
    how this project actually diagnosed F-033 by hand (residual against panel median, not a
    group-wide spread).
    """
    keys = list(values_by_series)
    common_dates = sorted(
        set.intersection(*[set(v) for v in values_by_series.values()])
    ) if keys else []

    returns_by_series = {
        k: day_over_day_returns(values_by_series[k]) for k in keys
    }
    common_return_dates = sorted(
        set.intersection(*[set(v) for v in returns_by_series.values()])
    ) if keys else []

    def _residual(value: float, group_values: list[float]) -> float:
        median = statistics.median(group_values)
        if median == 0:
            return 0.0
        return abs(value - median) / abs(median)

    results: list[PairwiseIdentityResult] = []
    for k in keys:
        level_residuals = [
            _residual(values_by_series[k][d], [values_by_series[other][d] for other in keys])
            for d in common_dates
        ]
        max_level_range = max(level_residuals) if level_residuals else 0.0

        if common_return_dates:
            return_residuals = [
                _residual(
                    returns_by_series[k][d],
                    [returns_by_series[other][d] for other in keys if d in returns_by_series[other]],
                )
                for d in common_return_dates
                if d in returns_by_series[k]
            ]
            max_return_range = max(return_residuals) if return_residuals else None
        else:
            max_return_range = None

        if max_level_range < MACHINE_EPSILON_RELATIVE_TOLERANCE:
            flag = IndependenceFlag.EXACT_IDENTITY
        elif max_return_range is not None and max_return_range < MACHINE_EPSILON_RELATIVE_TOLERANCE:
            flag = IndependenceFlag.RETURNS_LOCKED
        else:
            flag = IndependenceFlag.INDEPENDENT

        results.append(
            PairwiseIdentityResult(
                series_key=k,
                compared_against="cohort median",
                relative_range_levels=max_level_range,
                relative_range_returns=max_return_range,
                flag=flag,
            )
        )

    groups = _collapse_shared_origin_groups(results)
    return IndependenceReport(
        results=results,
        effective_independent_width=len(groups),
        groups=groups,
    )


def _collapse_shared_origin_groups(results: list[PairwiseIdentityResult]) -> list[list[str]]:
    """All EXACT_IDENTITY/RETURNS_LOCKED members collapse into one group (they share an
    origin with each other, by construction of the check above); every INDEPENDENT member is
    its own group."""
    locked = [r.series_key for r in results if r.flag in (IndependenceFlag.EXACT_IDENTITY, IndependenceFlag.RETURNS_LOCKED)]
    independent = [r.series_key for r in results if r.flag == IndependenceFlag.INDEPENDENT]

    groups: list[list[str]] = []
    if locked:
        groups.append(locked)
    groups.extend([k] for k in independent)
    return groups
