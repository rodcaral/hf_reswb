"""Row-local trade evidence and calendar-derived session status.

SPEC_OBSERVATION_SUITABILITY.md, D-038. Two orthogonal axes: `TradeEvidence` is decided
from a row and its predecessor alone, no calendar input, and governs suitability for
continuity-sensitive calculations. `SessionStatus` is downstream of a derived venue
calendar and governs nothing — display only (§2.1, §4).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TradeEvidence(str, Enum):
    TRADE_OBSERVED = "TRADE_OBSERVED"
    NO_TRADE_REPORTED = "NO_TRADE_REPORTED"
    TRADE_EVIDENCE_UNRESOLVED = "TRADE_EVIDENCE_UNRESOLVED"


class SessionStatus(str, Enum):
    SESSION_CONFIRMED = "SESSION_CONFIRMED"
    SESSION_ABSENT = "SESSION_ABSENT"
    SESSION_UNRESOLVED = "SESSION_UNRESOLVED"


class CalendarConfidence(str, Enum):
    AUTHORITATIVE = "AUTHORITATIVE"
    RELIABLE = "RELIABLE"
    USABLE_WITH_CAVEAT = "USABLE_WITH_CAVEAT"
    UNRESOLVED = "UNRESOLVED"


@dataclass
class ObservationSuitability:
    evidence_reference_id: int
    prior_evidence_reference_id: int | None
    histfints_series_id: int
    observed_date: str
    trade_evidence: TradeEvidence
    volume_unreliable: bool
    session_status: SessionStatus
    basis: list[str]
    calendar_derivation_id: int | None
    rule_version: str
    classified_at: str
    id: int | None = None


@dataclass
class CalendarDerivation:
    venue: str
    contributing_series_ids: list[int]
    quorum_rule: str
    period_start: str
    period_end: str
    confidence_band: CalendarConfidence
    derived_at: str
    id: int | None = None


@dataclass
class SuitabilityRun:
    series_id: int
    period_start: str
    period_end: str
    rule_version: str
    calendar_derivation_id: int | None = None
    count_trade_observed: int = 0
    count_no_trade_reported: int = 0
    count_trade_evidence_unresolved: int = 0
    created_at: str = ""
    id: int | None = None


@dataclass
class NoTradeRun:
    histfints_series_id: int
    first_date: str
    last_date: str
    length: int
    first_evidence_reference_id: int
    last_evidence_reference_id: int
    suitability_run_id: int
    id: int | None = None
