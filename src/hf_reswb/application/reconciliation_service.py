"""The one reconciliation capability this increment builds.

Detect -> resolve evidence -> classify -> record. Nothing else: no repair, no HistFinTS
writes, no vocabulary beyond the three verdicts in SPEC-f009-evidence-consumption.md §4.3.

Governing decisions: D-032 (what upstream actually holds today), D-033 (reference-by-key,
three verdicts), D-034 (proceed against the current, unmigrated schema). Findings F-023
(no FK from provider_event to observations — correlation is Calculated, never Observed),
F-024 (a bare FRED vintage date is not explanatory) and F-025 (`acquired_at` is capture
time, not fetch time) are binding on the classification logic below, not just noted.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from hf_reswb.application.discontinuity_detector import Boundary, DetectorParams, detect_boundaries
from hf_reswb.domain.evidence import EvidenceReference, HistFintsObject, ResolutionState
from hf_reswb.domain.finding import AnalyticalFinding, DiscontinuityCalculation, ReasonCode, Verdict

CODE_VERSION = "f009-evidence-consumption-0.1"
CALENDAR_BASIS = "calendar_days"  # Q-027 (trading calendar) is open — SPEC §9

# Providers HistFinTS's own docs confirm supply no revision data at all (D-033, citing
# HistFinTS docs/KNOWN_LIMITATIONS.md:79-81). Not exhaustive; extend only on the same
# standard of evidence, never by inference.
_NO_REVISION_DATA_PROVIDERS = {"ECB"}

_OPTIONAL_EVIDENCE_TABLES: dict[HistFintsObject, str] = {
    HistFintsObject.PROVIDER_EVENT: "provider_event",
    HistFintsObject.OBSERVATION_CORRECTION: "observation_correction",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT name FROM histfints.sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def reconcile(
    connection: sqlite3.Connection,
    series_id: int,
    period_start: str,
    period_end: str,
    params: DetectorParams | None = None,
) -> list[AnalyticalFinding]:
    """Runs the full increment for one Series and period. Reads `histfints.*`; writes
    only to the Workbench's own tables (`discontinuity_calculation`, `evidence_reference`,
    `analytical_finding`)."""
    params = params or DetectorParams()

    rows = connection.execute(
        """
        SELECT id, observed_at, value
        FROM histfints.observation
        WHERE series_id = ? AND observed_at BETWEEN ? AND ?
        ORDER BY observed_at
        """,
        (series_id, period_start, period_end),
    ).fetchall()

    if not rows:
        return [
            _record_no_calculation_finding(
                connection,
                series_id,
                period_start,
                period_end,
                reason=ReasonCode.NO_CAPTURE_RUN_FOR_SERIES,
            )
        ]

    values = [r["value"] for r in rows]
    ids = [r["id"] for r in rows]
    dates = [r["observed_at"] for r in rows]

    boundaries = detect_boundaries(values, params)
    findings: list[AnalyticalFinding] = []
    for boundary in boundaries:
        findings.append(
            _reconcile_one_boundary(
                connection, series_id, period_start, period_end, dates, ids, boundary, params
            )
        )
    connection.commit()
    return findings


def _reconcile_one_boundary(
    connection: sqlite3.Connection,
    series_id: int,
    period_start: str,
    period_end: str,
    dates: list[str],
    ids: list[int],
    boundary: Boundary,
    params: DetectorParams,
) -> AnalyticalFinding:
    obs_before_id = ids[boundary.index - 1]
    obs_after_id = ids[boundary.index]
    boundary_date = dates[boundary.index]

    calculation = DiscontinuityCalculation(
        series_id=series_id,
        period_start=period_start,
        period_end=period_end,
        boundary_date=boundary_date,
        value_before=boundary.value_before,
        value_after=boundary.value_after,
        step_factor=boundary.step_factor,
        persistence_horizons_days=params.persistence_horizons_days,
        persisted=True,  # detect_boundaries only ever returns persisted boundaries
        step_threshold=params.step_threshold,
        tolerance=params.persistence_tolerance,
        calendar_basis=CALENDAR_BASIS,
        code_version=CODE_VERSION,
        evidence_observation_before_id=obs_before_id,
        evidence_observation_after_id=obs_after_id,
    )
    calculation.id = _insert_calculation(connection, calculation)

    evidence: list[EvidenceReference] = []
    evidence += _reference_observation_chain(connection, calculation.id, series_id, obs_before_id)
    evidence += _reference_observation_chain(connection, calculation.id, series_id, obs_after_id)

    correction_candidates = _resolve_corrections(
        connection, calculation.id, series_id, [obs_before_id, obs_after_id]
    )
    evidence += correction_candidates["refs"]

    provider_id = _provider_id_for_series(connection, series_id)
    provider_display_name = _provider_display_name(connection, provider_id) if provider_id else None

    event_candidates, event_refs = _resolve_provider_events(
        connection, calculation.id, series_id, boundary_date
    )
    evidence += event_refs

    obscorr_refs = _probe_optional_table(
        connection, calculation.id, series_id, HistFintsObject.OBSERVATION_CORRECTION
    )
    evidence += obscorr_refs

    verdict, reason, residual = _classify(
        provider_display_name,
        correction_candidates["magnitude_candidates"],
        event_candidates,
        boundary.step_factor,
        params.persistence_tolerance,
    )

    finding = AnalyticalFinding(
        calculation=calculation,
        verdict=verdict,
        reason_code=reason,
        evidence_consulted=evidence,
        correlation_tolerance=params.persistence_tolerance,
        residual=residual,
    )
    finding.id = _insert_finding(connection, finding)
    return finding


def _classify(
    provider_display_name: str | None,
    correction_magnitude_candidates: list[tuple[str, float]],
    event_magnitude_candidates: list[tuple[str, float]],
    step_factor: float,
    tolerance: float,
) -> tuple[Verdict, ReasonCode, float | None]:
    if provider_display_name in _NO_REVISION_DATA_PROVIDERS:
        return Verdict.INSUFFICIENT_EVIDENCE, ReasonCode.PROVIDER_SUPPLIES_NO_REVISION_DATA, None

    candidates = correction_magnitude_candidates + event_magnitude_candidates
    for _source, factor in candidates:
        residual = abs(step_factor - factor)
        if residual <= tolerance:
            return Verdict.EXPLAINED, ReasonCode.EVENT_MAGNITUDE_RECONCILES, residual

    if candidates:
        best_residual = min(abs(step_factor - factor) for _source, factor in candidates)
        return Verdict.NOT_EXPLAINED, ReasonCode.MAGNITUDE_MISMATCH, best_residual

    # `correction` (v1 baseline) is always queryable, so reaching here means at least one
    # real evidence source was checked and held nothing — D-033's reachable NOT_EXPLAINED
    # case, not an absence of any evidence source to check.
    return Verdict.NOT_EXPLAINED, ReasonCode.NO_EVIDENCE_AT_DATE, None


def _resolve_corrections(
    connection: sqlite3.Connection, calculation_id: int, series_id: int, observation_ids: list[int]
) -> dict:
    placeholders = ",".join("?" for _ in observation_ids)
    rows = connection.execute(
        f"""
        SELECT id, observation_id, field_name, previous_value, new_value, detected_at
        FROM histfints.correction
        WHERE observation_id IN ({placeholders})
        """,
        observation_ids,
    ).fetchall()

    refs: list[EvidenceReference] = []
    candidates: list[tuple[str, float]] = []
    for row in rows:
        refs.append(
            EvidenceReference(
                histfints_object=HistFintsObject.CORRECTION,
                histfints_id=row["id"],
                histfints_series_id=series_id,
                resolution_state=ResolutionState.RESOLVED,
                resolved_at=_now(),
                detail=f"{row['field_name']}: {row['previous_value']} -> {row['new_value']} at {row['detected_at']}",
            )
        )
        if row["field_name"] == "value" and row["previous_value"]:
            candidates.append(("correction", row["new_value"] / row["previous_value"]))
        _insert_evidence_reference(connection, calculation_id, refs[-1])

    return {"refs": refs, "magnitude_candidates": candidates}


def _resolve_provider_events(
    connection: sqlite3.Connection, calculation_id: int, series_id: int, boundary_date: str
) -> tuple[list[tuple[str, float]], list[EvidenceReference]]:
    if not _table_exists(connection, "provider_event"):
        ref = EvidenceReference(
            histfints_object=HistFintsObject.PROVIDER_EVENT,
            histfints_id=None,
            histfints_series_id=series_id,
            resolution_state=ResolutionState.TABLE_ABSENT,
            resolved_at=_now(),
            detail="provider_event does not exist in the attached database (D-032)",
        )
        _insert_evidence_reference(connection, calculation_id, ref)
        return [], [ref]

    proximity_window_days = 5
    boundary_dt = datetime.fromisoformat(boundary_date)
    window_start = boundary_dt.replace(hour=0, minute=0, second=0)
    window_end = boundary_dt.replace(hour=23, minute=59, second=59)

    rows = connection.execute(
        """
        SELECT id, event_type, event_date, structured_data
        FROM histfints.provider_event
        WHERE series_id = ? AND date(event_date) BETWEEN date(?, ?) AND date(?, ?)
        """,
        (
            series_id,
            window_start.isoformat(),
            f"-{proximity_window_days} days",
            window_end.isoformat(),
            f"+{proximity_window_days} days",
        ),
    ).fetchall()

    candidates: list[tuple[str, float]] = []
    refs: list[EvidenceReference] = []
    for row in rows:
        refs.append(
            EvidenceReference(
                histfints_object=HistFintsObject.PROVIDER_EVENT,
                histfints_id=row["id"],
                histfints_series_id=series_id,
                resolution_state=ResolutionState.RESOLVED,
                resolved_at=_now(),
                detail=f"{row['event_type']} at {row['event_date']}",
            )
        )
        _insert_evidence_reference(connection, calculation_id, refs[-1])

        if row["event_type"] == "REVISION":
            # F-024: a bare vintage date, never a value. Not explanatory on its own — do
            # not let it contribute a magnitude candidate.
            continue
        factor = _event_implied_factor(row["event_type"], row["structured_data"])
        if factor is not None:
            candidates.append(("provider_event", factor))

    if not rows:
        ref = EvidenceReference(
            histfints_object=HistFintsObject.PROVIDER_EVENT,
            histfints_id=None,
            histfints_series_id=series_id,
            resolution_state=ResolutionState.MISSING,
            resolved_at=_now(),
            detail=f"no provider_event within +/-{proximity_window_days}d of {boundary_date}",
        )
        _insert_evidence_reference(connection, calculation_id, ref)
        refs.append(ref)

    return candidates, refs


def _event_implied_factor(event_type: str, structured_data_json: str) -> float | None:
    # F-023: provider_event carries no FK to any observation/correction. This join is by
    # series_id + date proximity + a stated tolerance — Calculated, never Observed.
    try:
        data = json.loads(structured_data_json)
    except (TypeError, ValueError):
        return None
    if event_type == "SPLIT":
        ratio = data.get("ratio")
        if ratio:
            return 1.0 / float(ratio)
    return None


def _probe_optional_table(
    connection: sqlite3.Connection,
    calculation_id: int,
    series_id: int,
    histfints_object: HistFintsObject,
) -> list[EvidenceReference]:
    table_name = _OPTIONAL_EVIDENCE_TABLES[histfints_object]
    exists = _table_exists(connection, table_name)
    ref = EvidenceReference(
        histfints_object=histfints_object,
        histfints_id=None,
        histfints_series_id=series_id,
        resolution_state=ResolutionState.TABLE_ABSENT if not exists else ResolutionState.MISSING,
        resolved_at=_now(),
        detail=f"{table_name} {'absent (D-032)' if not exists else 'present, not queried by this increment'}",
    )
    _insert_evidence_reference(connection, calculation_id, ref)
    return [ref]


def _reference_observation_chain(
    connection: sqlite3.Connection, calculation_id: int, series_id: int, observation_id: int
) -> list[EvidenceReference]:
    row = connection.execute(
        """
        SELECT ir.id AS import_run_id, pa.id AS provider_assignment_id
        FROM histfints.observation o
        JOIN histfints.import_run ir ON ir.id = o.import_run_id
        JOIN histfints.provider_assignment pa ON pa.id = ir.provider_assignment_id
        WHERE o.id = ?
        """,
        (observation_id,),
    ).fetchone()

    refs = [
        EvidenceReference(
            histfints_object=HistFintsObject.OBSERVATION,
            histfints_id=observation_id,
            histfints_series_id=series_id,
            resolution_state=ResolutionState.RESOLVED,
            resolved_at=_now(),
        )
    ]
    if row is not None:
        refs.append(
            EvidenceReference(
                histfints_object=HistFintsObject.IMPORT_RUN,
                histfints_id=row["import_run_id"],
                histfints_series_id=series_id,
                resolution_state=ResolutionState.RESOLVED,
                resolved_at=_now(),
            )
        )
        refs.append(
            EvidenceReference(
                histfints_object=HistFintsObject.PROVIDER_ASSIGNMENT,
                histfints_id=row["provider_assignment_id"],
                histfints_series_id=series_id,
                resolution_state=ResolutionState.RESOLVED,
                resolved_at=_now(),
            )
        )
    for ref in refs:
        _insert_evidence_reference(connection, calculation_id, ref)
    return refs


def _provider_id_for_series(connection: sqlite3.Connection, series_id: int) -> int | None:
    row = connection.execute(
        "SELECT provider_id FROM histfints.provider_assignment WHERE series_id = ? ORDER BY priority LIMIT 1",
        (series_id,),
    ).fetchone()
    return row["provider_id"] if row else None


def _provider_display_name(connection: sqlite3.Connection, provider_id: int) -> str | None:
    row = connection.execute(
        "SELECT display_name FROM histfints.provider WHERE id = ?", (provider_id,)
    ).fetchone()
    return row["display_name"] if row else None


def _insert_calculation(connection: sqlite3.Connection, calc: DiscontinuityCalculation) -> int:
    horizon_1, horizon_2 = calc.persistence_horizons_days
    cursor = connection.execute(
        """
        INSERT INTO discontinuity_calculation (
            series_id, period_start, period_end, boundary_date, value_before, value_after,
            step_factor, persistence_horizon_days_1, persistence_horizon_days_2, persisted,
            step_threshold, tolerance, calendar_basis, code_version,
            evidence_observation_before_id, evidence_observation_after_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            calc.series_id, calc.period_start, calc.period_end, calc.boundary_date,
            calc.value_before, calc.value_after, calc.step_factor, horizon_1, horizon_2,
            int(calc.persisted), calc.step_threshold, calc.tolerance, calc.calendar_basis,
            calc.code_version, calc.evidence_observation_before_id,
            calc.evidence_observation_after_id, _now(),
        ),
    )
    return cursor.lastrowid


def _insert_evidence_reference(
    connection: sqlite3.Connection, calculation_id: int, ref: EvidenceReference
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO evidence_reference (
            calculation_id, histfints_object, histfints_id, histfints_series_id,
            resolution_state, resolved_at, detail
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            calculation_id, ref.histfints_object.value, ref.histfints_id,
            ref.histfints_series_id, ref.resolution_state.value, ref.resolved_at, ref.detail,
        ),
    )
    return cursor.lastrowid


def _insert_finding(connection: sqlite3.Connection, finding: AnalyticalFinding) -> int:
    cursor = connection.execute(
        """
        INSERT INTO analytical_finding (
            calculation_id, verdict, reason_code, correlation_tolerance, residual, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            finding.calculation.id, finding.verdict.value, finding.reason_code.value,
            finding.correlation_tolerance, finding.residual, _now(),
        ),
    )
    return cursor.lastrowid


def _record_no_calculation_finding(
    connection: sqlite3.Connection,
    series_id: int,
    period_start: str,
    period_end: str,
    reason: ReasonCode,
) -> AnalyticalFinding:
    """No observations at all in the period — there is no boundary to name, so this finding
    carries a calculation with before == after == None-equivalent markers rather than
    fabricating one. Recorded so 'nothing was found' is a traceable finding, not silence."""
    calculation = DiscontinuityCalculation(
        series_id=series_id,
        period_start=period_start,
        period_end=period_end,
        boundary_date=period_start,
        value_before=0.0,
        value_after=0.0,
        step_factor=1.0,
        persistence_horizons_days=(0, 0),
        persisted=False,
        step_threshold=0.0,
        tolerance=0.0,
        calendar_basis=CALENDAR_BASIS,
        code_version=CODE_VERSION,
        evidence_observation_before_id=-1,
        evidence_observation_after_id=-1,
    )
    calculation.id = _insert_calculation(connection, calculation)
    finding = AnalyticalFinding(
        calculation=calculation,
        verdict=Verdict.INSUFFICIENT_EVIDENCE,
        reason_code=reason,
        evidence_consulted=[],
    )
    finding.id = _insert_finding(connection, finding)
    connection.commit()
    return finding
