"""A pointer into HistFinTS, never a copy of its data.

D-033 / SPEC-f009-evidence-consumption.md §2.2: the Workbench references upstream evidence
by key and re-resolves it at read time. `TABLE_ABSENT` is a first-class state, not an error
— it is the normal state for `PROVIDER_EVENT` and `OBSERVATION_CORRECTION` against today's
production database (D-032).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HistFintsObject(str, Enum):
    OBSERVATION = "OBSERVATION"
    CORRECTION = "CORRECTION"
    IMPORT_RUN = "IMPORT_RUN"
    PROVIDER_ASSIGNMENT = "PROVIDER_ASSIGNMENT"
    PROVIDER_EVENT = "PROVIDER_EVENT"
    OBSERVATION_CORRECTION = "OBSERVATION_CORRECTION"


class ResolutionState(str, Enum):
    RESOLVED = "RESOLVED"
    MISSING = "MISSING"
    TABLE_ABSENT = "TABLE_ABSENT"
    SERIES_ARCHIVED = "SERIES_ARCHIVED"


@dataclass(frozen=True)
class EvidenceReference:
    histfints_object: HistFintsObject
    histfints_id: int | None  # None whenever resolution_state is TABLE_ABSENT
    histfints_series_id: int
    resolution_state: ResolutionState
    resolved_at: str  # ISO 8601 UTC
    detail: str = ""
