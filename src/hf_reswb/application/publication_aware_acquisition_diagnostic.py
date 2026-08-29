"""INC-3 -- Publication-aware acquisition-history diagnostic (first bounded increment).

Governing material: `docs/ACTION_PLAN.md` §11 (INC-3), citing D1-D4 rulings (§7) and DFA BYMA
calendar rulings. Consumes HistFinTS's `AcquisitionEvidenceSnapshot` contract exactly as
`acquisition_evidence_integration.py` does for D1-D4 -- same JSON, same read-only boundary (this
module accepts already-fetched evidence; it does not invoke HistFinTS's CLI or process).

**Financial question** (§11): for a Series whose acquisition history shows gaps or apparent
lateness, are those gaps inconsistent with financially relevant BYMA trading opportunities, or
explained by the historically applicable BYMA market schedule?

**First bounded population** (§11): `STOCK` Series for which BYMA venue applicability is
established. `series_type` is **not** part of the acquisition-evidence contract -- the caller
must supply it explicitly (e.g. from `histfints list-series`); this module never infers it from
a label, ticker, or any other proxy. BYMA venue applicability is read directly from the
contract's own `byma_applicable` flag on each assignment (HistFinTS's own determination from
provider identity), never re-derived here.

**Methodology** (§11): raw elapsed time remains descriptive operational evidence, always
reported when a successful run exists. A session-aware count may use only authoritative curated
BYMA session evidence (`byma_session_coverage`, already filtered to independently-authoritative
records by HistFinTS's own view) -- and only when that coverage is complete over the exact date
range being examined. A date that cannot be established confidently leaves the session-aware
result `UNAVAILABLE`, never inferred, never defaulted from a weekday/holiday heuristic, never
projected from a current calendar backward.

**Kept distinct, deliberately** (per instruction): this module reports an *acquisition-process*
gap only (successful-run timing) -- never a claim about missing financial *observations*. Every
dataclass here carries no observation-count field; `ProvenanceEvidence`/`total_observations` are
a different question this module does not touch, so the two cannot be conflated by a caller
reading only this module's output.

**Prohibited** (§11, SP-2/4/5/6/7, all enforced structurally, not only documented):
- No synthesized acquisition-quality/comparability score or confidence percentage (SP-2).
- No inference of provider failure from an unsuccessful or absent run alone (SP-4).
- No invented staleness/cadence/tolerance/margin threshold, and no PASS/FAIL or SLA framing
  (SP-5) -- this module reports counts and explicit unavailable states only.
- No fallback-provider activation of any kind (SP-6).
- No write path, no HistFinTS mutation (SP-7) -- pure functions over already-fetched evidence.
- `STALE`/`OK` semantics (owned by `import_state.py` on the HistFinTS side, and by nothing in
  this Workbench codebase) are never read or written here.
- No generalization beyond the approved BYMA/STOCK population -- `diagnose_inc3_acquisition_gap`
  returns `None`, not a degraded result, for anything outside it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class SessionsElapsedStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    """Every date the session-aware count depends on (HistFinTS's own reported coverage range)
    has authoritative curated evidence -- `sessions_elapsed` is a real count of established
    `TRADING`-status sessions in that range."""

    UNAVAILABLE_INSUFFICIENT_SESSION_EVIDENCE = "UNAVAILABLE_INSUFFICIENT_SESSION_EVIDENCE"
    """At least one date in the range has no authoritative record -- never curated, or curated
    but still awaiting independent review. Per ACTION_PLAN.md §11 this stays unavailable/
    qualified; it is never filled in from a weekday/holiday assumption or a current calendar."""

    UNAVAILABLE_NO_SUCCESSFUL_RUN = "UNAVAILABLE_NO_SUCCESSFUL_RUN"
    """No successful acquisition run is on record for this assignment. There is no acquisition
    gap to measure yet -- distinct from a real gap that cannot be measured in sessions."""

    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    """This assignment is outside INC-3's first bounded population (not BYMA-applicable, or the
    Series is not a STOCK). Returned only by `diagnose_inc3_acquisition_gap` as a filtering
    signal to a caller iterating a whole snapshot -- never surfaced as a `None`-shaped result
    with a fabricated reason."""


@dataclass(frozen=True)
class PublicationAwareAcquisitionDiagnostic:
    """One BYMA-applicable assignment's INC-3 diagnostic for a STOCK Series. Descriptive only --
    see this module's own docstring for the full prohibition list this dataclass's shape is
    designed to make structurally hard to violate (no score field, no STALE/OK field, no
    observation-count field)."""

    provider_assignment_id: int

    raw_elapsed_since_last_success_seconds: float | None
    """Descriptive operational evidence, pass-through from HistFinTS's own
    `elapsed_since_last_success_seconds` -- always reported when a successful run exists,
    independent of session-aware availability (ACTION_PLAN.md §11: "raw elapsed-time evidence
    remains usable when session interpretation is unresolved")."""

    sessions_elapsed_status: SessionsElapsedStatus
    sessions_elapsed: int | None
    """Count of established `TRADING`-status sessions in HistFinTS's own reported coverage
    range. `None` unless `sessions_elapsed_status == AVAILABLE`. Deliberately excludes
    `SPECIAL_LIMITED` sessions -- see `special_limited_sessions_elapsed` -- so a limited/
    abbreviated session is never silently folded into an ordinary-trading-session count."""

    special_limited_sessions_elapsed: int | None
    """Count of established `SPECIAL_LIMITED`-status sessions in the same range, reported
    separately from `sessions_elapsed` rather than blended into it. `None` under the same
    condition as `sessions_elapsed`."""

    session_evidence_range: tuple[date, date] | None
    session_evidence_known_days: int | None
    session_evidence_total_days: int | None
    note: str


def diagnose_inc3_acquisition_gap(
    assignment: dict, *, series_type: str
) -> PublicationAwareAcquisitionDiagnostic | None:
    """Returns `None` -- not a degraded diagnostic -- when this assignment is outside INC-3's
    first bounded population: `series_type != "STOCK"`, or the assignment's own
    `byma_applicable` is `False`. `series_type` must be supplied by the caller; the acquisition-
    evidence contract carries no such field, and this function never infers one.

    A non-`None` result is always returned once the population test passes -- eligibility never
    collapses into an `UNAVAILABLE` status; those two concerns stay separate (`None` = out of
    scope for this diagnostic entirely; `UNAVAILABLE_*` = in scope, evidence insufficient).
    """
    if series_type != "STOCK" or not assignment["byma_applicable"]:
        return None

    raw_elapsed = assignment["elapsed_since_last_success_seconds"]
    coverage = assignment["byma_session_coverage"]

    if raw_elapsed is None:
        return PublicationAwareAcquisitionDiagnostic(
            provider_assignment_id=assignment["provider_assignment_id"],
            raw_elapsed_since_last_success_seconds=None,
            sessions_elapsed_status=SessionsElapsedStatus.UNAVAILABLE_NO_SUCCESSFUL_RUN,
            sessions_elapsed=None,
            special_limited_sessions_elapsed=None,
            session_evidence_range=None,
            session_evidence_known_days=None,
            session_evidence_total_days=None,
            note=(
                "No successful acquisition run is on record for this assignment -- there is no "
                "acquisition gap to measure yet."
            ),
        )

    if coverage is None or not coverage["coverage_complete"]:
        return PublicationAwareAcquisitionDiagnostic(
            provider_assignment_id=assignment["provider_assignment_id"],
            raw_elapsed_since_last_success_seconds=raw_elapsed,
            sessions_elapsed_status=(
                SessionsElapsedStatus.UNAVAILABLE_INSUFFICIENT_SESSION_EVIDENCE
            ),
            sessions_elapsed=None,
            special_limited_sessions_elapsed=None,
            session_evidence_range=(
                (date.fromisoformat(coverage["range_start"]), date.fromisoformat(coverage["range_end"]))
                if coverage is not None
                else None
            ),
            session_evidence_known_days=coverage["known_days"] if coverage is not None else 0,
            session_evidence_total_days=coverage["total_days"] if coverage is not None else None,
            note=(
                "Raw elapsed acquisition time is available; a session-aware count is not. "
                + (
                    coverage["note"]
                    if coverage is not None
                    else "No authoritative BYMA session evidence exists for any date this "
                    "assignment's run history spans."
                )
            ),
        )

    trading = [s for s in coverage["sessions"] if s["session_status"] == "TRADING"]
    special_limited = [s for s in coverage["sessions"] if s["session_status"] == "SPECIAL_LIMITED"]
    return PublicationAwareAcquisitionDiagnostic(
        provider_assignment_id=assignment["provider_assignment_id"],
        raw_elapsed_since_last_success_seconds=raw_elapsed,
        sessions_elapsed_status=SessionsElapsedStatus.AVAILABLE,
        sessions_elapsed=len(trading),
        special_limited_sessions_elapsed=len(special_limited),
        session_evidence_range=(
            date.fromisoformat(coverage["range_start"]), date.fromisoformat(coverage["range_end"])
        ),
        session_evidence_known_days=coverage["known_days"],
        session_evidence_total_days=coverage["total_days"],
        note=(
            "Every date in this assignment's run-history span has authoritative curated BYMA "
            "session evidence. sessions_elapsed counts only TRADING-status sessions in that "
            "span -- this describes the acquisition-history span, not a claim that any specific "
            "gap within it was a missed market-day acquisition."
        ),
    )


def diagnose_inc3_for_snapshot(
    snapshot: dict, *, series_type: str
) -> tuple[PublicationAwareAcquisitionDiagnostic, ...]:
    """The production entry point: one diagnostic per BYMA-applicable assignment on a STOCK
    Series' snapshot. Returns `()` -- not a diagnostic carrying a `NOT_ELIGIBLE` status -- for a
    Series entirely outside the first bounded population, matching
    `diagnose_inc3_acquisition_gap`'s own `None`-for-out-of-scope contract."""
    return tuple(
        d
        for a in snapshot["assignments"]
        if (d := diagnose_inc3_acquisition_gap(a, series_type=series_type)) is not None
    )
