"""Panel eligibility models and result types.

D-046: include_delisted, staleness_policy, dispersion_threshold as analytical parameters.
All numerical thresholds marked PROVISIONAL — no hard-coded arbitrary values.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ResultStatus(str, Enum):
    """Panel result status: published or suppressed due to data quality."""
    PUBLISHED = "PUBLISHED"
    SUPPRESSED = "SUPPRESSED"


class ExclusionReason(str, Enum):
    """Why a Series was excluded from a panel date."""
    STALE = "STALE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    NO_TRADE_REPORTED = "NO_TRADE_REPORTED"
    NO_RATIO_KNOWN = "NO_RATIO_KNOWN"
    ADJUSTMENT_BASIS_MISMATCH = "ADJUSTMENT_BASIS_MISMATCH"
    COVERAGE_INCOMPLETE = "COVERAGE_INCOMPLETE"
    DELISTED = "DELISTED"


@dataclass(frozen=True)
class StalenessPolicy:
    """Time-local staleness exclusion parameter (D-046, SPEC §8.2)."""
    max_consecutive_no_trade_days: int

    @property
    def status(self) -> str:
        return "PROVISIONAL — awaiting calibration (D-042 §8.5)"


@dataclass(frozen=True)
class DispersionThreshold:
    """Aggregate suppression parameter (D-046, SPEC §8.3)."""
    threshold_value: float
    metric_name: str = "coefficient_of_variation"  # Placeholder pending calibration

    @property
    def status(self) -> str:
        return "PROVISIONAL — economically contextual, awaiting calibration (D-042 §8.5)"


@dataclass(frozen=True)
class PanelEligibilityParameters:
    """Three inclusion-rule parameters per D-046."""
    include_delisted: bool = True  # Default: inclusion for historical research
    staleness_policy: Optional[StalenessPolicy] = None  # Provisional; set before panel computation
    dispersion_threshold: Optional[DispersionThreshold] = None  # Provisional; set before result suppression

    @property
    def provisional_parameters(self) -> dict[str, str]:
        """Return all provisional parameters and their status."""
        result = {}
        if self.staleness_policy:
            result["staleness_policy.max_consecutive_no_trade_days"] = (
                f"{self.staleness_policy.max_consecutive_no_trade_days} days (PROVISIONAL)"
            )
        if self.dispersion_threshold:
            result["dispersion_threshold"] = (
                f"{self.dispersion_threshold.threshold_value} ({self.dispersion_threshold.metric_name}, PROVISIONAL)"
            )
        return result


@dataclass
class ExclusionRecord:
    """Why a Series was excluded on a particular date."""
    series_id: int
    reason: ExclusionReason
    detail: str = ""  # Optional context (e.g., "stale since 2020-04-10")


@dataclass
class PanelMembershipSnapshot:
    """Panel membership as-of-date, with full audit trail."""
    date: str
    included_series_ids: list[int]
    excluded_records: list[ExclusionRecord] = field(default_factory=list)

    @property
    def total_eligible(self) -> int:
        return len(self.included_series_ids)

    @property
    def total_excluded(self) -> int:
        return len(self.excluded_records)

    def exclusion_summary(self) -> dict[ExclusionReason, int]:
        """Count exclusions by reason."""
        summary = {}
        for record in self.excluded_records:
            summary[record.reason] = summary.get(record.reason, 0) + 1
        return summary


@dataclass
class PanelResult:
    """Complete panel result with full traceability (D-046, SPEC §4.2)."""
    date: str
    result_status: ResultStatus
    consensus_rate: Optional[float]  # None if SUPPRESSED
    dispersion_metric: float

    # Traceability
    member_count: int
    excluded_count: int
    exclusion_summary: dict[str, int]  # ExclusionReason -> count

    member_rates: list[float]
    member_residuals: list[float]

    # Metadata
    parameters_used: PanelEligibilityParameters
    membership: Optional[PanelMembershipSnapshot] = None

    adjustment_basis: Optional[str] = None  # Which basis was enforced (SPLIT_ADJUSTED, UNADJUSTED)
    coverage_status: Optional[str] = None  # Availability metadata status

    @property
    def is_suppressed(self) -> bool:
        return self.result_status == ResultStatus.SUPPRESSED

    @property
    def is_published(self) -> bool:
        return self.result_status == ResultStatus.PUBLISHED
