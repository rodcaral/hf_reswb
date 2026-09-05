"""The Workbench's own calculation and its verdict.

SPEC_F009_EVIDENCE_CONSUMPTION.md §2.2, §3, §4.3. Both types are P4 `Calculated` — never
`Asserted` (only a human writes a Research Conclusion, and the system never auto-promotes
a finding into one; D-033).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from hf_reswb.domain.evidence import EvidenceReference


class Verdict(str, Enum):
    EXPLAINED = "explained by captured evidence"
    NOT_EXPLAINED = "not explained by captured evidence"
    INSUFFICIENT_EVIDENCE = "insufficient evidence"


class ReasonCode(str, Enum):
    # insufficient evidence
    EVIDENCE_TABLE_ABSENT = "EVIDENCE_TABLE_ABSENT"
    NO_CAPTURE_RUN_FOR_SERIES = "NO_CAPTURE_RUN_FOR_SERIES"
    ALL_OBSERVATIONS_QUARANTINED = "ALL_OBSERVATIONS_QUARANTINED"  # F-033 quarantine integration
    PROVIDER_SUPPLIES_NO_REVISION_DATA = "PROVIDER_SUPPLIES_NO_REVISION_DATA"
    UPSTREAM_REFERENCE_UNRESOLVABLE = "UPSTREAM_REFERENCE_UNRESOLVABLE"
    # not explained
    NO_EVIDENCE_AT_DATE = "NO_EVIDENCE_AT_DATE"
    MAGNITUDE_MISMATCH = "MAGNITUDE_MISMATCH"
    PROVIDER_SPLICE_AT_BOUNDARY = "PROVIDER_SPLICE_AT_BOUNDARY"
    # explained
    EVENT_MAGNITUDE_RECONCILES = "EVENT_MAGNITUDE_RECONCILES"


@dataclass
class DiscontinuityCalculation:
    """Workbench-owned arithmetic. Carries its own inputs so a finding can restate its
    arithmetic even if the upstream row it cites is later mutated or archived (§2.2)."""

    series_id: int
    period_start: str
    period_end: str
    boundary_date: str
    value_before: float
    value_after: float
    step_factor: float
    persistence_horizons_days: tuple[int, int]
    persisted: bool
    step_threshold: float
    tolerance: float
    calendar_basis: str  # "calendar_days" until Q-027 (trading calendar) lands — SPEC §9
    code_version: str
    evidence_observation_before_id: int
    evidence_observation_after_id: int
    id: int | None = None


@dataclass
class AnalyticalFinding:
    """Exactly one verdict from §4.3, plus a reason code and every EvidenceReference
    consulted — including references that resolved to nothing, per §5's "consulted
    absences are part of the lineage"."""

    calculation: DiscontinuityCalculation
    verdict: Verdict
    reason_code: ReasonCode
    evidence_consulted: list[EvidenceReference] = field(default_factory=list)
    correlation_tolerance: float | None = None
    residual: float | None = None
    id: int | None = None
