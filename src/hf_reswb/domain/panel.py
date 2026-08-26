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
    NON_INDEPENDENT_SOURCE = "NON_INDEPENDENT_SOURCE"
    """F-033 pattern: values or returns locked to another cohort member to within machine
    precision — a shared computed origin, not independent market observation. See
    `application.independence_detector`."""
    PROVENANCE_UNVERIFIED = "PROVENANCE_UNVERIFIED"
    """A referenced series (e.g. `underlying_series_id`) has not passed the duplicate-of-
    source / plausible-range check. See `application.provenance_guard.verify_fk_target`.
    Series-level reference provenance only — distinct from ORIGIN_PROVENANCE_MISSING below,
    which is row-level write provenance. Distinct from NON_INDEPENDENT_SOURCE: this flags an
    unverified reference, not a confirmed shared origin between panel members."""
    ORIGIN_PROVENANCE_MISSING = "ORIGIN_PROVENANCE_MISSING"
    """`observation.origin_import_run_id` is NULL on a row created at or after the epoch at
    which that column started being populated (2026-08-20, `PRAGMA user_version = 15`) — a
    candidate anomaly, not the expected historical gap that predates the column's existence.
    See `application.provenance_guard.classify_origin_provenance`. Deliberately does NOT
    cover the historical-NULL case (`OriginProvenanceVerdict.HISTORICAL_NULL_ORIGIN`), which
    is expected for 99.96% of the live database as of 2026-08-20 and is not a defect — no
    ExclusionReason is assigned for it. Proposed 2026-08-20; not yet assigned by any
    production code path."""
    SUPERSEDED = "SUPERSEDED"
    """`series.status = 'SUPERSEDED'` (DFA-approved general definition, 2026-08-26): "retained
    for historical/provenance purposes; no longer the current attribution." Excluded by default,
    mirroring `DELISTED`'s pattern, but opt-in via `PanelEligibilityParameters.include_superseded`
    rather than opt-out (default `False`, not `True`) — SUPERSEDED asserts the Series is not the
    current attribution for its history, a stronger default-exclusion signal than DELISTED's
    "the instrument stopped trading." Not a financial-validity claim by itself; see
    `SeriesStatus.SUPERSEDED`'s own docstring in `histfints-v3` for what it does and does not
    mean."""


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
    """Four inclusion-rule parameters (three per D-046, plus include_superseded 2026-08-26)."""
    include_delisted: bool = True  # Default: inclusion for historical research
    include_superseded: bool = False
    """Shared semantic name for the "include superseded/historical" rule across Workbench
    surfaces (SE directive 2026-08-26). Default `False` — excluded unless explicitly opted in,
    the reverse default of `include_delisted`. See `ExclusionReason.SUPERSEDED`."""
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
    superseded_included_series_ids: list[int] = field(default_factory=list)
    """Subset of `included_series_ids` that are `status = 'SUPERSEDED'` and were included only
    because `include_superseded=True` was explicitly set. Non-empty here is what drives
    `PanelResult.historical_evidence_qualification` — an opted-in analytical output must carry
    a visible qualification (SE directive 2026-08-26), not silently include historical/
    superseded data indistinguishably from current attribution."""

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

    historical_evidence_qualification: Optional[str] = None
    """Set (non-None) whenever `membership.superseded_included_series_ids` is non-empty — a
    visible qualification on this specific result, not merely at the selection step (SE
    directive 2026-08-26: "any explicitly opted-in analytical output must carry a visible
    superseded/historical-evidence qualification"). `None` when no SUPERSEDED Series was
    opted into this result."""

    @property
    def is_suppressed(self) -> bool:
        return self.result_status == ResultStatus.SUPPRESSED

    @property
    def is_published(self) -> bool:
        return self.result_status == ResultStatus.PUBLISHED
