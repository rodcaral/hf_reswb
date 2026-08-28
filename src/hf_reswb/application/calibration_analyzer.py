"""Panel eligibility calibration analysis framework (D-046, Phase 5).

Empirical analysis of staleness and dispersion parameters against historical panel data.
Provides calibration utilities for:
- Staleness threshold calibration (days between last observation)
- Dispersion threshold calibration (coefficient of variation, IQR, etc.)
- Sensitivity analysis (panel depth, membership, suppression rates)
- Candidate parameter recommendation

Per SPEC_PANEL_ELIGIBILITY.md §8.5 and D-046, all calibration results are recommendations
only. Final values require domain review and financial advisor approval before production.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StalenessDistribution:
    """Distribution statistics for staleness (days between observations)."""
    min_days: int
    max_days: int
    median_days: int
    mean_days: float
    p25_days: int
    p75_days: int
    p95_days: int
    count_series: int
    count_observations: int

    @property
    def description(self) -> str:
        """Human-readable summary."""
        return (
            f"Staleness distribution: min={self.min_days}d, max={self.max_days}d, "
            f"median={self.median_days}d, mean={self.mean_days:.1f}d, "
            f"p25={self.p25_days}d, p75={self.p75_days}d, p95={self.p95_days}d"
        )


@dataclass(frozen=True)
class DispersionDistribution:
    """Distribution statistics for dispersion metrics (CV, IQR, etc.)."""
    metric_name: str  # "coefficient_of_variation", "interquartile_range", etc.

    min_value: float
    max_value: float
    median_value: float
    mean_value: float
    p25_value: float
    p75_value: float
    p95_value: float

    count_panel_dates: int
    suppression_rate_at_p95: float  # What % of dates would be suppressed at p95 threshold

    @property
    def description(self) -> str:
        """Human-readable summary."""
        return (
            f"{self.metric_name} distribution: min={self.min_value:.4f}, "
            f"max={self.max_value:.4f}, median={self.median_value:.4f}, "
            f"mean={self.mean_value:.4f}, p95={self.p95_value:.4f}, "
            f"suppression_rate_at_p95={self.suppression_rate_at_p95:.1%}"
        )


@dataclass(frozen=True)
class ThresholdImpact:
    """Impact of a single threshold candidate on panel eligibility."""
    parameter_name: str  # "staleness_policy" or "dispersion_threshold"
    threshold_value: float | int
    description: str  # e.g., "max_consecutive_no_trade_days=10"

    affected_dates: int  # How many dates have at least one exclusion
    affected_series_count: int  # Unique series affected
    avg_panel_depth_change: float  # Change in average member count per date (% or absolute)
    min_panel_depth: int  # Minimum member count on any affected date

    @property
    def summary(self) -> str:
        """One-line summary of impact."""
        return (
            f"{self.description}: affects {self.affected_dates} dates, "
            f"{self.affected_series_count} series, depth change {self.avg_panel_depth_change:+.1%}"
        )


@dataclass(frozen=True)
class CalibrationReport:
    """Complete calibration study report per Phase 5."""
    title: str = "Panel Eligibility Calibration Study"
    date_generated: str = ""  # ISO format timestamp
    period_start: str = ""  # "2000-01-01"
    period_end: str = ""  # "2026-08-18"

    staleness_distribution: Optional[StalenessDistribution] = None
    dispersion_distribution_cv: Optional[DispersionDistribution] = None
    dispersion_distribution_iqr: Optional[DispersionDistribution] = None

    staleness_threshold_impacts: list[ThresholdImpact] = None  # Test: 5, 10, 15, 20 days
    dispersion_threshold_impacts_cv: list[ThresholdImpact] = None  # Test: p50, p75, p90, p95
    dispersion_threshold_impacts_iqr: list[ThresholdImpact] = None

    staleness_recommendation: Optional[str] = None  # Recommended threshold with rationale
    dispersion_recommendation: Optional[str] = None

    caveats: list[str] = None  # Regime dependencies, limitations, etc.

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.staleness_threshold_impacts is None:
            object.__setattr__(self, 'staleness_threshold_impacts', [])
        if self.dispersion_threshold_impacts_cv is None:
            object.__setattr__(self, 'dispersion_threshold_impacts_cv', [])
        if self.dispersion_threshold_impacts_iqr is None:
            object.__setattr__(self, 'dispersion_threshold_impacts_iqr', [])
        if self.caveats is None:
            object.__setattr__(self, 'caveats', [])

    @property
    def is_complete(self) -> bool:
        """Whether all analysis components are present."""
        return (
            self.staleness_distribution is not None
            and self.dispersion_distribution_cv is not None
            and len(self.staleness_threshold_impacts) > 0
            and len(self.dispersion_threshold_impacts_cv) > 0
            and self.staleness_recommendation is not None
            and self.dispersion_recommendation is not None
        )

    def format_markdown(self) -> str:
        """Format report as Markdown for documentation."""
        lines = [
            f"# {self.title}",
            "",
            f"**Generated:** {self.date_generated}  ",
            f"**Period:** {self.period_start} to {self.period_end}  ",
            "",
        ]

        if self.staleness_distribution:
            lines.extend([
                "## Staleness Distribution",
                "",
                self.staleness_distribution.description,
                "",
            ])

        if self.dispersion_distribution_cv:
            lines.extend([
                "## Dispersion Distribution (Coefficient of Variation)",
                "",
                self.dispersion_distribution_cv.description,
                "",
            ])

        if self.staleness_recommendation:
            lines.extend([
                "## Staleness Threshold Recommendation",
                "",
                self.staleness_recommendation,
                "",
            ])

        if self.dispersion_recommendation:
            lines.extend([
                "## Dispersion Threshold Recommendation",
                "",
                self.dispersion_recommendation,
                "",
            ])

        if self.caveats:
            lines.extend([
                "## Caveats and Limitations",
                "",
            ])
            for caveat in self.caveats:
                lines.append(f"- {caveat}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "**Status:** PROVISIONAL — awaiting domain review and financial advisor approval",
            "",
        ])

        return "\n".join(lines)


@dataclass(frozen=True)
class CalibrationRequest:
    """Request parameters for a calibration study."""
    period_start: str  # "2000-01-01"
    period_end: str  # "2026-08-18"
    panel_pairs: list[tuple[int, int]] | None = None  # [(series_id_a, series_id_b), ...]

    staleness_threshold_candidates: list[int] = None  # Days: [5, 10, 15, 20, 25]
    dispersion_metric_names: list[str] = None  # ["coefficient_of_variation", "interquartile_range"]
    dispersion_percentile_candidates: list[int] = None  # [50, 75, 90, 95]

    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.staleness_threshold_candidates is None:
            object.__setattr__(self, 'staleness_threshold_candidates', [5, 10, 15, 20, 25])
        if self.dispersion_metric_names is None:
            object.__setattr__(self, 'dispersion_metric_names', ["coefficient_of_variation"])
        if self.dispersion_percentile_candidates is None:
            object.__setattr__(self, 'dispersion_percentile_candidates', [50, 75, 90, 95])
