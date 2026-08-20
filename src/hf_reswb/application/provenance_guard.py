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


# ---------------------------------------------------------------------------
# Row-level write provenance (observation.origin_import_run_id)
#
# A second, distinct provenance axis from verify_fk_target() above. That function asks
# "does this series reference point somewhere independent"; this one asks "do we know,
# immutably, which import run first wrote this observation row." They answer different
# questions and are not substitutes for each other.
#
# `origin_import_run_id` was added to `observation` by HistFinTS on 2026-08-20 (schema
# now at PRAGMA user_version = 15) in response to the mutability issue in
# `PROVENANCE_INTEGRITY_import_run_id_mutability.md`: the existing `import_run_id` column
# is overwritten on `ON CONFLICT DO UPDATE`, so it names the *last* writer, not the
# original one. `origin_import_run_id` is intended to be set once and never overwritten.
#
# The epoch below (2026-08-20T12:08:12 UTC) is empirically observed against the live
# database at the time this module was written — the first `created_at` carrying a
# non-NULL `origin_import_run_id`, with a clean cutover (zero post-epoch NULLs, zero
# pre-epoch non-NULLs, verified at the time of writing). It is NOT sourced from an
# authoritative HistFinTS migration record or filing. See "Dependency on HistFinTS
# verification" in this module's accompanying documentation before relying on it as a
# stable constant — HistFinTS has not confirmed whether this cutover is guaranteed
# monotonic going forward, whether a historical backfill of `origin_import_run_id` is
# planned (which would silently invalidate any hardcoded epoch), or whether the value
# is authoritative rather than incidental to when the column was first observed. Callers
# should treat the epoch as a required, caller-supplied argument — never a module default.
# ---------------------------------------------------------------------------


class OriginProvenanceVerdict(str, Enum):
    ORIGIN_RECORDED = "ORIGIN_RECORDED"
    """`origin_import_run_id` is populated. Says nothing about whether the referenced
    import run itself is trustworthy — only that the immutable-origin field is present."""

    HISTORICAL_NULL_ORIGIN = "HISTORICAL_NULL_ORIGIN"
    """`origin_import_run_id` is NULL and the row's `created_at` predates the epoch at
    which the column started being populated. Expected, not anomalous — the column did
    not exist when this row was written. As of 2026-08-20, this is true for 27,949,974 of
    27,961,375 observations (99.96%) in the live database."""

    ORIGIN_MISSING_POST_EPOCH = "ORIGIN_MISSING_POST_EPOCH"
    """`origin_import_run_id` is NULL on a row created at or after the epoch — the column
    is expected to be populated for rows this recent. Distinct from HISTORICAL_NULL_ORIGIN:
    this is a candidate anomaly, not an expected historical gap. As of 2026-08-20, zero
    observations in the live database matched this case — it is currently a theoretical
    classification, not one with an observed instance."""


@dataclass(frozen=True)
class OriginProvenanceCheckResult:
    observation_id: int
    created_at: str
    epoch: str
    verdict: OriginProvenanceVerdict
    origin_import_run_id: int | None


def classify_origin_provenance(
    observation_id: int,
    created_at: str,
    origin_import_run_id: int | None,
    *,
    epoch: str,
) -> OriginProvenanceCheckResult:
    """Classify one observation's origin-tracking state.

    Args:
        observation_id: for traceability in the result only; not looked up.
        created_at: the observation's `created_at`, ISO 8601, lexicographically comparable
            to `epoch` (both must use the same format/timezone convention — this function
            does no timezone-aware parsing, only string comparison, matching how the epoch
            cutover was originally verified against the live database).
        origin_import_run_id: the observation's `origin_import_run_id`, or `None`.
        epoch: caller-supplied cutover timestamp. Required, no default — see module-level
            note on why this project's currently-known epoch should not be hardcoded here.

    Returns:
        OriginProvenanceCheckResult with a verdict distinguishing the three cases.
    """
    if origin_import_run_id is not None:
        verdict = OriginProvenanceVerdict.ORIGIN_RECORDED
    elif created_at < epoch:
        verdict = OriginProvenanceVerdict.HISTORICAL_NULL_ORIGIN
    else:
        verdict = OriginProvenanceVerdict.ORIGIN_MISSING_POST_EPOCH

    return OriginProvenanceCheckResult(
        observation_id=observation_id,
        created_at=created_at,
        epoch=epoch,
        verdict=verdict,
        origin_import_run_id=origin_import_run_id,
    )
