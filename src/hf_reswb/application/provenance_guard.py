"""Foreign-key provenance verification for underlying/reference series.

Codifies, as reusable infrastructure, the check that has repeatedly caught corrupted
`series.underlying_series_id` links during the F-032/F-033 investigation: a stored FK is a
convention-level pointer, not a verified fact (D-003 — `series_id` is never enforced). Every
instance found so far shared one signature — the FK target's values are a near-duplicate of
the *source* series' own values, not an independent market series — and every instance was
found by manual label search plus a price-plausibility check, repeated by hand across two
separate investigations (Workbench's original F-033 finding, and HistFinTS's own initial
audit walking into the same corrupted pointer on 2026-08-19 before self-correcting; see
`docs/histfints-requests/RECONCILIATION-F033-2026-08-19.md`).

This module does not decide whether any specific FK is correct for production use — it flags
candidates for the same manual check this project has now performed several times, so a
future calibration attempt does not have to rediscover the pattern from scratch.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from hf_reswb.application.independence_detector import (
    MACHINE_EPSILON_RELATIVE_TOLERANCE,
    relative_range,
)


class ProvenanceVerdict(str, Enum):
    TRUSTED = "TRUSTED"
    """FK target's values differ from the source series' own values by more than machine
    precision on every common date, and (if provided) fall within an expected price range.
    Not a claim that the FK is *correct* — only that it is not the specific, already-observed
    failure mode of pointing back at (a near-copy of) the source itself."""

    SUSPECT_DUPLICATE_OF_SOURCE = "SUSPECT_DUPLICATE_OF_SOURCE"
    """FK target's values are indistinguishable (within MACHINE_EPSILON_RELATIVE_TOLERANCE)
    from the source series' own values on every common date — the exact signature found for
    `series.underlying_series_id` on the F-033-affected CEDEAR series, where the FK pointed
    to a duplicate series carrying the CEDEAR's own values under a different id and a
    mislabeled currency."""

    IMPLAUSIBLE_RANGE = "IMPLAUSIBLE_RANGE"
    """FK target's values are distinct from the source (not SUSPECT_DUPLICATE_OF_SOURCE) but
    fall outside a caller-supplied expected range — e.g. a series labeled as a USD common
    stock whose values are in the thousands, when the real instrument trades in the tens to
    low hundreds. Distinctness from the source alone is not sufficient verification."""

    NO_COMMON_DATES = "NO_COMMON_DATES"
    """Source and FK target share no observation dates — cannot be checked by this method."""


@dataclass(frozen=True)
class ProvenanceCheckResult:
    source_series_id: int
    fk_target_series_id: int
    verdict: ProvenanceVerdict
    max_relative_range_vs_source: float | None
    dates_checked: int
    detail: str = ""


def verify_fk_target(
    source_series_id: int,
    fk_target_series_id: int,
    source_values: dict[str, float],
    fk_target_values: dict[str, float],
    *,
    expected_min: float | None = None,
    expected_max: float | None = None,
) -> ProvenanceCheckResult:
    """Check whether an FK target is plausibly independent of the series it's attached to.

    Args:
        source_series_id: the series carrying the FK (e.g. a CEDEAR).
        fk_target_series_id: the id `source`'s FK points to (e.g. `underlying_series_id`).
        source_values: {date -> value} for the source series.
        fk_target_values: {date -> value} for the FK target.
        expected_min/expected_max: optional plausible price range for the FK target (e.g.
            from a known real-world quote range). If omitted, only the duplicate-of-source
            check runs.

    Returns:
        ProvenanceCheckResult with a verdict and the evidence behind it.
    """
    common_dates = sorted(set(source_values) & set(fk_target_values))
    if not common_dates:
        return ProvenanceCheckResult(
            source_series_id=source_series_id,
            fk_target_series_id=fk_target_series_id,
            verdict=ProvenanceVerdict.NO_COMMON_DATES,
            max_relative_range_vs_source=None,
            dates_checked=0,
            detail="source and FK target share no observation dates",
        )

    ranges = [
        relative_range([source_values[d], fk_target_values[d]])
        for d in common_dates
    ]
    max_range = max(ranges)

    if max_range < MACHINE_EPSILON_RELATIVE_TOLERANCE:
        return ProvenanceCheckResult(
            source_series_id=source_series_id,
            fk_target_series_id=fk_target_series_id,
            verdict=ProvenanceVerdict.SUSPECT_DUPLICATE_OF_SOURCE,
            max_relative_range_vs_source=max_range,
            dates_checked=len(common_dates),
            detail=(
                f"FK target matches source to within machine precision on all "
                f"{len(common_dates)} common dates — consistent with the F-033 corrupted-FK "
                f"pattern, not an independent underlying series"
            ),
        )

    if expected_min is not None and expected_max is not None:
        out_of_range = [
            v for v in fk_target_values.values() if not (expected_min <= v <= expected_max)
        ]
        if out_of_range:
            return ProvenanceCheckResult(
                source_series_id=source_series_id,
                fk_target_series_id=fk_target_series_id,
                verdict=ProvenanceVerdict.IMPLAUSIBLE_RANGE,
                max_relative_range_vs_source=max_range,
                dates_checked=len(common_dates),
                detail=(
                    f"{len(out_of_range)} of {len(fk_target_values)} values fall outside "
                    f"the expected [{expected_min}, {expected_max}] range"
                ),
            )

    return ProvenanceCheckResult(
        source_series_id=source_series_id,
        fk_target_series_id=fk_target_series_id,
        verdict=ProvenanceVerdict.TRUSTED,
        max_relative_range_vs_source=max_range,
        dates_checked=len(common_dates),
        detail=f"distinct from source on all {len(common_dates)} common dates checked",
    )
