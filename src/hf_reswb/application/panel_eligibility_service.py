"""Panel eligibility orchestrator (D-046, Phase 1–3).

Orchestrates four inclusion-rule parameters per SPEC-panel-eligibility.md §8:
- include_delisted: Boolean, default TRUE (Phase 1)
- staleness_policy: Time-local exclusion (provisional parameter, Phase 1)
- dispersion_threshold: Aggregate suppression (provisional parameter, Phase 1)
- trade_evidence: Liquidity filter, excludes NO_TRADE_REPORTED by default (Phase 2)

Handles data constraints per Phase 3:
- Incomplete availability metadata (UNRESOLVED coverage status)
- Adjustment basis mismatches (mixed bases or required-basis violation)

Upstream contract (observation-suitability) is FROZEN — not modified here.
All numerical thresholds marked PROVISIONAL; no hard-coded arbitrary values.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from hf_reswb.application.data_constraints import (
    get_adjustment_basis_mismatch_exclusions,
    get_coverage_incomplete_exclusions,
)
from hf_reswb.application.dispersion_analyzer import (
    compute_dispersion_metrics,
    should_suppress_result,
)
from hf_reswb.application.panel_integration import (
    get_trade_evidence_exclusions,
    validate_suitability_coverage,
)
from hf_reswb.application.staleness_detector import get_staleness_exclusions
from hf_reswb.domain.panel import (
    DispersionThreshold,
    ExclusionReason,
    ExclusionRecord,
    PanelEligibilityParameters,
    PanelMembershipSnapshot,
    PanelResult,
    ResultStatus,
    StalenessPolicy,
)


def compute_panel_eligibility(
    connection: sqlite3.Connection,
    series_ids: list[int],
    analysis_date: str,
    parameters: PanelEligibilityParameters,
    validate_suitability: bool = True,
    check_coverage: bool = True,
    check_adjustment_basis: bool = True,
    required_adjustment_basis: str | None = None,
) -> PanelMembershipSnapshot:
    """
    Determine eligible Series for a panel date (D-046, Phase 1–3).

    Integration with observation-suitability (Phase 2):
    - Requires trade evidence classification (Axis A) to be present
    - Excludes NO_TRADE_REPORTED by default (liquidity criterion per SPEC §8.2)
    - Uses session status (Axis B) as display context only (D-036)

    Data constraints (Phase 3):
    - Detects incomplete availability metadata (UNRESOLVED status)
    - Detects adjustment basis mismatches (mixed bases or required-basis violation)

    Args:
        connection: HistFinTS read-only connection
        series_ids: Candidate Series
        analysis_date: Date in YYYY-MM-DD format
        parameters: include_delisted, staleness_policy, etc.
        validate_suitability: If True, require observation_suitability coverage (Phase 2)
        check_coverage: If True, exclude UNRESOLVED availability metadata (Phase 3)
        check_adjustment_basis: If True, exclude mixed adjustment bases (Phase 3)
        required_adjustment_basis: If set, exclude Series not matching this basis (Phase 3)

    Returns:
        PanelMembershipSnapshot with included and excluded Series
    """
    if not series_ids:
        return PanelMembershipSnapshot(
            date=analysis_date, included_series_ids=[], excluded_records=[]
        )

    # Phase 2: Validate observation-suitability coverage (optional, for safety)
    if validate_suitability:
        covered, missing = validate_suitability_coverage(
            connection, series_ids, analysis_date, analysis_date
        )
        if not covered:
            raise ValueError(
                f"observation-suitability classification missing for series {[m[0] for m in missing]}. "
                "Run classify_series() before computing panel eligibility."
            )

    excluded: list[ExclusionRecord] = []

    # 1. include_delisted: Check Series.status at this date
    if not parameters.include_delisted:
        placeholders = ",".join("?" for _ in series_ids)
        delisted = connection.execute(
            f"""
            SELECT id FROM histfints.series
            WHERE id IN ({placeholders})
              AND status = 'DELISTED_OR_DISCONTINUED'
            """,
            (*series_ids,),
        ).fetchall()

        for row in delisted:
            excluded.append(
                ExclusionRecord(
                    series_id=row["id"],
                    reason=ExclusionReason.DELISTED,
                    detail="status = DELISTED_OR_DISCONTINUED",
                )
            )

    # 2. staleness_policy: Time-local exclusion
    remaining_ids = [s for s in series_ids if not any(e.series_id == s for e in excluded)]
    if parameters.staleness_policy and remaining_ids:
        stale_exclusions = get_staleness_exclusions(
            connection,
            remaining_ids,
            analysis_date,
            parameters.staleness_policy,
        )
        excluded.extend(stale_exclusions)

    # 3. Phase 2: Trade evidence liquidity criterion (excludes NO_TRADE_REPORTED by default)
    remaining_ids = [s for s in series_ids if not any(e.series_id == s for e in excluded)]
    if remaining_ids:
        trade_exclusions = get_trade_evidence_exclusions(
            connection,
            remaining_ids,
            analysis_date,
        )
        excluded.extend(trade_exclusions)

    # 4. Phase 3: Coverage metadata constraints (incomplete availability)
    remaining_ids = [s for s in series_ids if not any(e.series_id == s for e in excluded)]
    if check_coverage and remaining_ids:
        coverage_exclusions = get_coverage_incomplete_exclusions(
            connection,
            remaining_ids,
        )
        excluded.extend(coverage_exclusions)

    # 5. Phase 3: Adjustment basis constraints (mixed bases or required-basis mismatch)
    remaining_ids = [s for s in series_ids if not any(e.series_id == s for e in excluded)]
    if check_adjustment_basis and remaining_ids:
        basis_exclusions = get_adjustment_basis_mismatch_exclusions(
            connection,
            remaining_ids,
            required_adjustment_basis,
        )
        excluded.extend(basis_exclusions)

    # 6. Final inclusion list
    excluded_ids = {e.series_id for e in excluded}
    included = [s for s in series_ids if s not in excluded_ids]

    return PanelMembershipSnapshot(
        date=analysis_date,
        included_series_ids=included,
        excluded_records=excluded,
    )


def compute_panel_result(
    connection: sqlite3.Connection,
    membership: PanelMembershipSnapshot,
    parameters: PanelEligibilityParameters,
    member_rates: list[float],
    member_residuals: list[float],
    adjustment_basis: str | None = None,
    coverage_status: str | None = None,
) -> PanelResult:
    """
    Compute panel result with dispersion-based suppression (D-046, Phase 1).

    Args:
        connection: HistFinTS connection (for metadata only)
        membership: Eligible Series snapshot
        parameters: Panel parameters (include_delisted, staleness_policy, dispersion_threshold)
        member_rates: Consensus rate computation (one per included member)
        member_residuals: Residuals for dispersion (one per included member)
        adjustment_basis: Adjustment basis used (SPLIT_ADJUSTED, UNADJUSTED, or None)
        coverage_status: Coverage metadata status (for reporting incomplete availability)

    Returns:
        PanelResult with full traceability
    """
    # Compute consensus rate
    consensus_rate = (
        sum(member_rates) / len(member_rates) if member_rates else None
    )

    # Compute dispersion metrics
    dispersion_metrics = compute_dispersion_metrics(member_residuals)
    dispersion_value = dispersion_metrics.coefficient_of_variation

    # Determine if suppressed (D-046, SPEC §8.3)
    is_suppressed = False
    if parameters.dispersion_threshold:
        is_suppressed = should_suppress_result(
            dispersion_value,
            parameters.dispersion_threshold.threshold_value,
        )

    result_status = ResultStatus.SUPPRESSED if is_suppressed else ResultStatus.PUBLISHED

    # Build result
    return PanelResult(
        date=membership.date,
        result_status=result_status,
        consensus_rate=consensus_rate if not is_suppressed else None,
        dispersion_metric=dispersion_value,
        member_count=membership.total_eligible,
        excluded_count=membership.total_excluded,
        exclusion_summary={
            reason.value: count
            for reason, count in membership.exclusion_summary().items()
        },
        member_rates=member_rates,
        member_residuals=member_residuals,
        parameters_used=parameters,
        membership=membership,
        adjustment_basis=adjustment_basis,
        coverage_status=coverage_status,
    )


def format_provisional_status(parameters: PanelEligibilityParameters) -> str:
    """
    Format provisional parameter status for display/logging.

    Returns:
        Human-readable summary of provisional parameters
    """
    lines = ["Panel Eligibility Parameters (provisional):"]

    lines.append(f"  include_delisted: {parameters.include_delisted}")

    if parameters.staleness_policy:
        lines.append(
            f"  staleness_policy.max_consecutive_no_trade_days: "
            f"{parameters.staleness_policy.max_consecutive_no_trade_days} (PROVISIONAL)"
        )

    if parameters.dispersion_threshold:
        lines.append(
            f"  dispersion_threshold: "
            f"{parameters.dispersion_threshold.threshold_value} "
            f"({parameters.dispersion_threshold.metric_name}, PROVISIONAL)"
        )

    return "\n".join(lines)
