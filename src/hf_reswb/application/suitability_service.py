"""Observation suitability classification.

SPEC_OBSERVATION_SUITABILITY.md, D-038. Three ordered steps (§3.3), each its own function
here so the ordering can't collapse into a cycle:

    1. classify_series()   -- Axis A, row-local, no calendar input
    2. derive_calendar()   -- quorum over TRADE_OBSERVED dates only (a correction to D-037,
                               which quorumed over raw dates)
    3. apply_calendar()    -- Axis B, downstream of the calendar produced in step 2

F-030's guard (`is_classifiable`) refuses classification for any Series whose
`configured_interval` isn't daily or whose observations don't key uniquely by calendar
date -- date(observed_at) is not a valid session key otherwise (series 11311).

Governs suitability, not permission (D-036's principle, §4): there is no global gate here.
This module only classifies and records; a continuity-sensitive calculation is what
excludes NO_TRADE_REPORTED / TRADE_EVIDENCE_UNRESOLVED by default (§4, point 2/3) -- that
consuming logic lives with whatever builds on this (e.g. SPEC_PANEL_ELIGIBILITY.md), not
here.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from hf_reswb.domain.evidence import EvidenceReference, HistFintsObject, ResolutionState
from hf_reswb.domain.suitability import (
    CalendarConfidence,
    CalendarDerivation,
    NoTradeRun,
    ObservationSuitability,
    SessionStatus,
    SuitabilityRun,
    TradeEvidence,
)

RULE_VERSION = "observation-suitability-0.1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_classifiable(connection: sqlite3.Connection, series_id: int) -> tuple[bool, str]:
    """F-030 guard. A Series must be single-interval and key uniquely by calendar date."""
    row = connection.execute(
        "SELECT configured_interval FROM histfints.series WHERE id = ?", (series_id,)
    ).fetchone()
    if row is None:
        return False, "series not found in histfints.series"
    if row["configured_interval"] != "1d":
        return False, (
            f"configured_interval={row['configured_interval']!r}, not classifiable by "
            "calendar date (F-030)"
        )
    dup = connection.execute(
        """
        SELECT COUNT(*) AS c FROM (
            SELECT date(observed_at) AS d, COUNT(*) AS n
            FROM histfints.observation WHERE series_id = ? GROUP BY d HAVING n > 1
        )
        """,
        (series_id,),
    ).fetchone()
    if dup["c"] > 0:
        return False, "multiple observations share a calendar date (mixed granularity, F-030)"
    return True, ""


def classify_series(
    connection: sqlite3.Connection, series_id: int, period_start: str, period_end: str
) -> tuple[SuitabilityRun, list[ObservationSuitability]]:
    """Step 1 -- Axis A. Row-local; no calendar input (§3.3)."""
    classifiable, reason = is_classifiable(connection, series_id)
    if not classifiable:
        raise ValueError(f"series {series_id} is not classifiable: {reason}")

    prior_ctx = connection.execute(
        """
        SELECT id, observed_at, value FROM histfints.observation
        WHERE series_id = ? AND observed_at < ?
        ORDER BY observed_at DESC LIMIT 1
        """,
        (series_id, period_start),
    ).fetchone()

    rows = connection.execute(
        """
        SELECT id, observed_at, open, high, low, value, volume FROM histfints.observation
        WHERE series_id = ? AND observed_at BETWEEN ? AND ?
        ORDER BY observed_at
        """,
        (series_id, period_start, period_end),
    ).fetchall()

    run = SuitabilityRun(
        series_id=series_id, period_start=period_start, period_end=period_end,
        rule_version=RULE_VERSION, created_at=_now(),
    )
    run.id = _insert_suitability_run(connection, run)

    prior = prior_ctx
    prior_evidence_ref_id = (
        _insert_evidence_reference(
            connection,
            EvidenceReference(
                histfints_object=HistFintsObject.OBSERVATION,
                histfints_id=prior["id"],
                histfints_series_id=series_id,
                resolution_state=ResolutionState.RESOLVED,
                resolved_at=_now(),
                detail="prior-close context row, before period_start",
            ),
        )
        if prior is not None
        else None
    )

    results: list[ObservationSuitability] = []
    for row in rows:
        ohlc_collapsed = (
            row["open"] is not None and row["high"] is not None and row["low"] is not None
            and row["open"] == row["high"] == row["low"] == row["value"]
        )
        volume_zero = row["volume"] == 0
        equals_prior_close = prior is not None and prior["value"] == row["value"]

        basis = []
        if volume_zero:
            basis.append("VOLUME_ZERO")
        if ohlc_collapsed:
            basis.append("OHLC_COLLAPSED")
        if equals_prior_close:
            basis.append("EQUALS_PRIOR_CLOSE")

        volume_unreliable = False
        if volume_zero and ohlc_collapsed and equals_prior_close:
            trade_evidence = TradeEvidence.NO_TRADE_REPORTED
        elif volume_zero and ohlc_collapsed:
            # OHLC-collapsed + volume=0 but no prior-close match (or no prior context at
            # all): cannot be confirmed as a pure carry-forward. §2.1.
            trade_evidence = TradeEvidence.TRADE_EVIDENCE_UNRESOLVED
        else:
            trade_evidence = TradeEvidence.TRADE_OBSERVED
            volume_unreliable = volume_zero  # a genuine range reported with volume=0, §1.2

        evidence_ref_id = _insert_evidence_reference(
            connection,
            EvidenceReference(
                histfints_object=HistFintsObject.OBSERVATION,
                histfints_id=row["id"],
                histfints_series_id=series_id,
                resolution_state=ResolutionState.RESOLVED,
                resolved_at=_now(),
            ),
        )

        item = ObservationSuitability(
            evidence_reference_id=evidence_ref_id,
            prior_evidence_reference_id=prior_evidence_ref_id,
            histfints_series_id=series_id,
            observed_date=row["observed_at"][:10],
            trade_evidence=trade_evidence,
            volume_unreliable=volume_unreliable,
            session_status=SessionStatus.SESSION_UNRESOLVED,  # Axis B not yet applied
            basis=basis,
            calendar_derivation_id=None,
            rule_version=RULE_VERSION,
            classified_at=_now(),
        )
        item_id = _insert_observation_suitability(connection, run.id, item)
        results.append(_with_id(item, item_id))

        if trade_evidence == TradeEvidence.TRADE_OBSERVED:
            run.count_trade_observed += 1
        elif trade_evidence == TradeEvidence.NO_TRADE_REPORTED:
            run.count_no_trade_reported += 1
        else:
            run.count_trade_evidence_unresolved += 1

        prior = row
        prior_evidence_ref_id = evidence_ref_id

    _update_suitability_run_counts(connection, run)
    connection.commit()
    return run, results


def derive_calendar(
    connection: sqlite3.Connection,
    venue: str,
    contributing_series_ids: list[int],
    period_start: str,
    period_end: str,
    confidence_band: CalendarConfidence,
    quorum_threshold: float = 0.5,
) -> CalendarDerivation:
    """Step 2. Quorum over TRADE_OBSERVED dates only (§3.3) -- the correction to D-037,
    which quorumed over raw observation dates and was shown circular for this purpose
    (F-029). Requires classify_series() to have already run for every contributing
    Series over this period; refuses to guess over uncovered ranges (§6, suitability_run
    discipline)."""
    placeholders = ",".join("?" for _ in contributing_series_ids)
    rows = connection.execute(
        f"""
        SELECT histfints_series_id, observed_date, trade_evidence
        FROM observation_suitability
        WHERE histfints_series_id IN ({placeholders})
          AND observed_date BETWEEN ? AND ?
        """,
        (*contributing_series_ids, period_start, period_end),
    ).fetchall()

    covered_series = {r["histfints_series_id"] for r in rows}
    missing = set(contributing_series_ids) - covered_series
    if missing:
        raise ValueError(
            f"no suitability_run covers series {sorted(missing)} for this period -- "
            "run classify_series() for every contributing series first"
        )

    by_date: dict[str, list[str]] = {}
    for r in rows:
        by_date.setdefault(r["observed_date"], []).append(r["trade_evidence"])

    quorum_rule = f"TRADE_OBSERVED share >= {quorum_threshold} of series reporting that date"
    derivation = CalendarDerivation(
        venue=venue,
        contributing_series_ids=list(contributing_series_ids),
        quorum_rule=quorum_rule,
        period_start=period_start,
        period_end=period_end,
        confidence_band=confidence_band,
        derived_at=_now(),
    )
    derivation_id = _insert_calendar_derivation(connection, derivation)
    connection.commit()
    return _with_id(derivation, derivation_id)


def apply_calendar(
    connection: sqlite3.Connection, calendar_derivation: CalendarDerivation, series_id: int
) -> None:
    """Step 3 -- Axis B. Never gates anything (§4); display-only session context."""
    session_dates = getattr(calendar_derivation, "_session_dates", None)
    if session_dates is None:
        row = connection.execute(
            "SELECT contributing_series_ids, period_start, period_end, quorum_rule "
            "FROM calendar_derivation WHERE id = ?",
            (calendar_derivation.id,),
        ).fetchone()
        threshold = float(row["quorum_rule"].split(">=")[1].split(" ")[1])
        contributing = json.loads(row["contributing_series_ids"])
        rows = connection.execute(
            f"""
            SELECT observed_date, trade_evidence FROM observation_suitability
            WHERE histfints_series_id IN ({",".join("?" for _ in contributing)})
              AND observed_date BETWEEN ? AND ?
            """,
            (*contributing, row["period_start"], row["period_end"]),
        ).fetchall()
        by_date: dict[str, list[str]] = {}
        for r in rows:
            by_date.setdefault(r["observed_date"], []).append(r["trade_evidence"])
        session_dates = {
            date for date, ev in by_date.items()
            if ev.count(TradeEvidence.TRADE_OBSERVED.value) / len(ev) >= threshold
        }

    if calendar_derivation.confidence_band in (
        CalendarConfidence.AUTHORITATIVE, CalendarConfidence.RELIABLE,
    ):
        status_for = lambda date: (
            SessionStatus.SESSION_CONFIRMED if date in session_dates else SessionStatus.SESSION_ABSENT
        )
    else:
        status_for = lambda date: SessionStatus.SESSION_UNRESOLVED

    rows = connection.execute(
        "SELECT id, observed_date FROM observation_suitability WHERE histfints_series_id = ?"
        " AND observed_date BETWEEN ? AND ?",
        (series_id, calendar_derivation.period_start, calendar_derivation.period_end),
    ).fetchall()
    for r in rows:
        connection.execute(
            "UPDATE observation_suitability SET session_status = ?, calendar_derivation_id = ? WHERE id = ?",
            (status_for(r["observed_date"]).value, calendar_derivation.id, r["id"]),
        )
    connection.execute(
        "UPDATE suitability_run SET calendar_derivation_id = ? WHERE series_id = ? "
        "AND period_start = ? AND period_end = ?",
        (calendar_derivation.id, series_id, calendar_derivation.period_start, calendar_derivation.period_end),
    )
    connection.commit()


def compute_no_trade_runs(connection: sqlite3.Connection, suitability_run_id: int) -> list[NoTradeRun]:
    """Run length, not row count, is what a display must warn on (§5)."""
    rows = connection.execute(
        """
        SELECT id, histfints_series_id, observed_date, trade_evidence, evidence_reference_id
        FROM observation_suitability WHERE suitability_run_id = ? ORDER BY observed_date
        """,
        (suitability_run_id,),
    ).fetchall()

    runs: list[NoTradeRun] = []
    current: list[sqlite3.Row] = []
    for row in rows:
        if row["trade_evidence"] == TradeEvidence.NO_TRADE_REPORTED.value:
            current.append(row)
            continue
        if current:
            runs.append(_flush_run(connection, current, suitability_run_id))
            current = []
    if current:
        runs.append(_flush_run(connection, current, suitability_run_id))
    connection.commit()
    return runs


def _flush_run(connection, rows, suitability_run_id) -> NoTradeRun:
    run = NoTradeRun(
        histfints_series_id=rows[0]["histfints_series_id"],
        first_date=rows[0]["observed_date"],
        last_date=rows[-1]["observed_date"],
        length=len(rows),
        first_evidence_reference_id=rows[0]["evidence_reference_id"],
        last_evidence_reference_id=rows[-1]["evidence_reference_id"],
        suitability_run_id=suitability_run_id,
    )
    run_id = connection.execute(
        """
        INSERT INTO no_trade_run (
            histfints_series_id, first_date, last_date, length,
            first_evidence_reference_id, last_evidence_reference_id, suitability_run_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run.histfints_series_id, run.first_date, run.last_date, run.length,
            run.first_evidence_reference_id, run.last_evidence_reference_id,
            run.suitability_run_id, _now(),
        ),
    ).lastrowid
    return _with_id(run, run_id)


def _with_id(obj, new_id):
    obj.id = new_id
    return obj


def _insert_evidence_reference(connection: sqlite3.Connection, ref: EvidenceReference) -> int:
    return connection.execute(
        """
        INSERT INTO evidence_reference (
            calculation_id, histfints_object, histfints_id, histfints_series_id,
            resolution_state, resolved_at, detail
        ) VALUES (NULL, ?, ?, ?, ?, ?, ?)
        """,
        (
            ref.histfints_object.value, ref.histfints_id, ref.histfints_series_id,
            ref.resolution_state.value, ref.resolved_at, ref.detail,
        ),
    ).lastrowid


def _insert_suitability_run(connection: sqlite3.Connection, run: SuitabilityRun) -> int:
    return connection.execute(
        """
        INSERT INTO suitability_run (
            series_id, period_start, period_end, rule_version, calendar_derivation_id,
            count_trade_observed, count_no_trade_reported, count_trade_evidence_unresolved,
            created_at
        ) VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?)
        """,
        (run.series_id, run.period_start, run.period_end, run.rule_version,
         run.calendar_derivation_id, run.created_at),
    ).lastrowid


def _update_suitability_run_counts(connection: sqlite3.Connection, run: SuitabilityRun) -> None:
    connection.execute(
        """
        UPDATE suitability_run SET count_trade_observed = ?, count_no_trade_reported = ?,
            count_trade_evidence_unresolved = ? WHERE id = ?
        """,
        (run.count_trade_observed, run.count_no_trade_reported,
         run.count_trade_evidence_unresolved, run.id),
    )


def _insert_observation_suitability(
    connection: sqlite3.Connection, suitability_run_id: int, item: ObservationSuitability
) -> int:
    return connection.execute(
        """
        INSERT INTO observation_suitability (
            suitability_run_id, evidence_reference_id, prior_evidence_reference_id,
            histfints_series_id, observed_date, trade_evidence, volume_unreliable,
            session_status, basis, calendar_derivation_id, rule_version, classified_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            suitability_run_id, item.evidence_reference_id, item.prior_evidence_reference_id,
            item.histfints_series_id, item.observed_date, item.trade_evidence.value,
            int(item.volume_unreliable), item.session_status.value, ",".join(item.basis),
            item.calendar_derivation_id, item.rule_version, item.classified_at,
        ),
    ).lastrowid


def _insert_calendar_derivation(connection: sqlite3.Connection, derivation: CalendarDerivation) -> int:
    return connection.execute(
        """
        INSERT INTO calendar_derivation (
            venue, contributing_series_ids, quorum_rule, period_start, period_end,
            confidence_band, derived_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            derivation.venue, json.dumps(derivation.contributing_series_ids), derivation.quorum_rule,
            derivation.period_start, derivation.period_end, derivation.confidence_band.value,
            derivation.derived_at,
        ),
    ).lastrowid
