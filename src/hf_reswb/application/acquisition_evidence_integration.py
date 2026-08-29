"""Production caller for `acquisition_quality_capability.py`, driven by HistFinTS's read-only
`AcquisitionEvidenceSnapshot` contract (`python -m histfints acquisition-evidence <series_id>`,
`histfints/application/acquisition_evidence_view.py`).

**Boundary, stated once**: this module accepts the snapshot as already-fetched JSON (a path, a
raw JSON string, or a parsed dict) -- it does not invoke HistFinTS's CLI or know its Python
environment/venv/install path. HistFinTS is read-only from Workbench (D-001); the two projects
already run in separate virtualenvs, and inventing a subprocess-invocation convention here would
be a new, unflagged cross-repo coupling this module has no mandate to create. Producing the JSON
(`python -m histfints acquisition-evidence <id> > snapshot.json`) is the caller's own step.

**What this module does and does not do**, restated per SE's integration directive:
- Maps HistFinTS's evidence fields onto the *existing* D1-D4 classifiers in
  `acquisition_quality_capability.py` -- it does not modify, extend, or duplicate their logic.
- Never derives, infers, or substitutes a value for evidence the snapshot reports as
  unavailable. `coverage_quality.first_available_date`/`last_available_date` are always `None`
  in the current contract (unwired on the HistFinTS side) and are propagated as `None` into D4's
  `coverage_adequate`, never guessed at or backfilled from another field.
- Keeps D3's structural ceiling explicit: `non_production_status.value` is always `None` (no
  authoritative test/non-production column exists anywhere in HistFinTS's schema); this module
  still runs Workbench's own `looks_like_non_production_fixture()` heuristic against the raw
  `series_label`/`provider_series_identifier` facts the snapshot *does* carry, and that heuristic
  result is -- exactly as before -- a `CANDIDATE_UNCONFIRMED` flag, never an authoritative
  exclusion. Nothing here upgrades the heuristic past that ceiling.
- Introduces no synthesized quality score, financial-identity verdict, automatic identity
  resolution, exclusion/remediation action, fallback activation, provider reassignment, or
  production mutation. Every function here is pure and read-only; nothing calls
  `evaluate_fallback_activation(..., fallback_activation_enabled=True)`, and nothing writes to
  either project's database.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from hf_reswb.application.acquisition_quality_capability import (
    AcquisitionQualityPopulationMembership,
    CadenceCapabilityAssessment,
    FallbackCandidateEvidence,
    FallbackConsiderationResult,
    FixtureConfirmation,
    IdentifierCompatibilityAssessment,
    NeverStateReason,
    NonProductionFixtureStatus,
    RunOutcome,
    assess_cadence_capability,
    assess_identifier_compatibility,
    classify_never_state,
    classify_population_membership,
    consider_fallback,
    determine_fixture_status,
    looks_like_non_production_fixture,
)

# ---------------------------------------------------------------------------------------------
# Snapshot loading -- read-only, no HistFinTS process/env coupling
# ---------------------------------------------------------------------------------------------


def load_snapshot(source: str | Path | dict) -> dict:
    """Accepts a JSON file path, a raw JSON string, or an already-parsed dict -- and returns the
    raw dict as produced by `histfints acquisition-evidence <series_id>`. Validates the presence
    of the top-level keys every downstream mapper depends on, so a contract break surfaces here
    as a clear error rather than a confusing `KeyError` three functions deep."""
    if isinstance(source, dict):
        raw = source
    elif isinstance(source, Path) or (isinstance(source, str) and Path(source).is_file()):
        raw = json.loads(Path(source).read_text(encoding="utf-8"))
    else:
        raw = json.loads(source)

    required = {
        "series_id", "series_label", "series_status", "configured_interval", "assignments",
        "provenance", "identity", "non_production_status", "coverage_quality", "comparability",
    }
    missing = required - raw.keys()
    if missing:
        raise ValueError(
            f"acquisition-evidence snapshot missing required key(s): {sorted(missing)} -- "
            "contract mismatch, not a data gap; do not proceed with a partial snapshot."
        )
    return raw


# ---------------------------------------------------------------------------------------------
# D3 -- NEVER-state / population membership. Fully operational: every input this classifier
# needs is a RAW FACT the snapshot actually carries.
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class D3Result:
    fixture_status: NonProductionFixtureStatus
    population_membership: AcquisitionQualityPopulationMembership
    never_state_reason: NeverStateReason | None
    """`None` when the series has at least one assignment with a recorded (non-`None`)
    `latest_import` -- i.e. it is not in a NEVER state at all, so this classifier does not
    apply. Never guessed at; computed from whether every assignment's `latest_import` is
    `None`, which is exactly what "no import_run has ever been attempted" means."""


def classify_d3(
    snapshot: dict, *, fixture_confirmation: FixtureConfirmation | None = None
) -> D3Result:
    """Wires the existing D3 classifiers (`looks_like_non_production_fixture`,
    `determine_fixture_status`, `classify_population_membership`, and -- when the series has
    never had a run -- `classify_never_state`) against real per-series evidence.

    `fixture_confirmation` stays `None` unless the caller supplies a real, attributed
    `FixtureConfirmation` -- this module never manufactures one. Per D3's own design, an
    unconfirmed heuristic match can only ever reach `CANDIDATE_UNCONFIRMED`/
    `INCLUDED_PENDING_FIXTURE_REVIEW`, exactly as it did before this integration existed.
    """
    has_provider_assignment = len(snapshot["assignments"]) > 0
    is_superseded = snapshot["series_status"] == "SUPERSEDED"

    fixture_candidate = looks_like_non_production_fixture(
        snapshot["series_label"],
        snapshot["assignments"][0]["provider_series_identifier"]
        if snapshot["assignments"]
        else None,
    )
    fixture_status = determine_fixture_status(
        candidate_flag=fixture_candidate, confirmation=fixture_confirmation
    )
    population_membership = classify_population_membership(
        fixture_status, is_superseded=is_superseded
    )

    has_ever_run = any(a["latest_import"] is not None for a in snapshot["assignments"])
    never_state_reason = (
        None
        if has_ever_run
        else classify_never_state(
            has_provider_assignment=has_provider_assignment,
            fixture_candidate=fixture_candidate,
            is_superseded=is_superseded,
        )
    )

    return D3Result(
        fixture_status=fixture_status,
        population_membership=population_membership,
        never_state_reason=never_state_reason,
    )


# ---------------------------------------------------------------------------------------------
# D2 -- identifier/provider acquisition compatibility. Operational, but evidence-limited: the
# snapshot exposes only the LATEST run per assignment, not full outcome history, so
# CONSISTENTLY_UNRESOLVED here means "the one recorded attempt failed", not "every attempt ever
# made failed". This limitation is structural to the current contract, not a mapping choice.
# ---------------------------------------------------------------------------------------------


def assemble_d2_outcomes(assignment: dict) -> list[RunOutcome]:
    """Single-sample outcome history for one assignment. `PARTIAL` and `IN_PROGRESS` runs are
    deliberately excluded rather than forced into SUCCESS/FAILED -- `RunOutcome` is a binary
    completed-outcome type and neither status is one; excluding them yields an honest, smaller
    sample rather than a fabricated binary read on an ambiguous or unfinished run."""
    latest = assignment["latest_import"]
    if latest is None or latest["status"] not in ("SUCCESS", "FAILED"):
        return []
    return [RunOutcome.SUCCESS if latest["status"] == "SUCCESS" else RunOutcome.FAILED]


def classify_d2(assignment: dict) -> IdentifierCompatibilityAssessment:
    return assess_identifier_compatibility(assemble_d2_outcomes(assignment))


# ---------------------------------------------------------------------------------------------
# D1 -- cadence capability. Now operational: HistFinTS's contract exposes `run_history`, the
# full, authoritative, most-recent-first `ImportRun` list per assignment (previously only the
# single latest run was exposed, which structurally could never clear
# `assess_cadence_capability()`'s own gap-based evidence floor). Only `SUCCESS` runs contribute a
# timestamp -- matching HistFinTS's own `RunHistoryEntry` docstring ("the minimum evidence a D1
# cadence classifier needs to compute its own observed successful-run gaps") and this project's
# established rule that `PARTIAL`/`IN_PROGRESS` runs are not forced into a binary read. Verdict
# and margin-sufficiency judgment stay entirely the existing classifier's: this module supplies
# evidence only, never a tolerance, a margin threshold, or a STALE/OK-shaped conclusion.
# ---------------------------------------------------------------------------------------------


def assemble_d1_successful_run_timestamps(assignment: dict) -> list[datetime]:
    """Every `SUCCESS`-status entry in `run_history`, as real `datetime`s -- not sampled, not
    capped, and not limited to the latest run. An assignment with an empty or all-non-SUCCESS
    `run_history` correctly yields `[]`, which `assess_cadence_capability()` already turns into
    `INSUFFICIENT_EVIDENCE` on its own; this function does not special-case that outcome."""
    return [
        datetime.fromisoformat(run["started_at"])
        for run in assignment["run_history"]
        if run["status"] == "SUCCESS"
    ]


def classify_d1(assignment: dict, *, tolerance: timedelta) -> CadenceCapabilityAssessment:
    """`tolerance` must be supplied by the caller (the Series' own `staleness_tolerance`, per
    D1's original design) -- this module does not invent, select, or default one, and never will:
    that is a DFA-approved policy boundary this module has no authority to cross. With HistFinTS's
    `run_history` now available, a series with enough recorded `SUCCESS` runs (>= `min_samples`
    consecutive-run gaps, per the classifier's own floor) produces a real `SUFFICIENT_MARGIN`/
    `INSUFFICIENT_MARGIN` verdict; a series with too few still honestly reports
    `INSUFFICIENT_EVIDENCE`, exactly as before -- the missing-evidence state is preserved, not
    papered over now that richer evidence exists for series that have it."""
    return assess_cadence_capability(
        tolerance=tolerance,
        successful_run_started_at=assemble_d1_successful_run_timestamps(assignment),
    )


# ---------------------------------------------------------------------------------------------
# D4 -- evidence-gated conditional fallback. Operational, severely evidence-limited: of the
# seven named dimensions, only `adjustment_convention_documented` maps to a real fact in the
# current contract. The other six are propagated as `None` (unavailable), never derived --
# `coverage_adequate` in particular must stay `None` because `coverage_quality.
# first_available_date`/`last_available_date` are always `None` on the HistFinTS side today
# (unwired, per that module's own docstring), matching SE's explicit instruction not to derive
# or substitute for the unwired coverage-span dates.
# ---------------------------------------------------------------------------------------------


def assemble_d4_candidate_evidence(assignment: dict) -> FallbackCandidateEvidence:
    return FallbackCandidateEvidence(
        identity_compatible=None,  # identity.evaluated is always False -- never guessed here
        history_available=None,  # no per-assignment observation history in this contract
        adjustment_convention_documented=assignment["adjustment_basis_source"] != "unavailable",
        coverage_adequate=None,  # coverage_quality dates are unwired -- propagated, not derived
        provenance_acceptable=None,  # "acceptable" is a judgment this module never makes
        quality_acceptable=None,  # HistFinTS reports this via a separate, unembedded capability
        comparability_acceptable=None,  # comparability.computed is always False
    )


def classify_d4(assignment: dict, *, material_impact: bool | None = None) -> FallbackConsiderationResult:
    """`material_impact` defaults to `None` (unknown) -- this contract carries no signal that
    could ever supply it; materiality is an analysis-context judgment, not evidence about a
    Series. A real caller with an actual materiality determination should pass it explicitly."""
    return consider_fallback(
        material_impact=material_impact,
        candidate_evidence=assemble_d4_candidate_evidence(assignment),
    )


# ---------------------------------------------------------------------------------------------
# Orchestration -- one call per snapshot, all four classifiers, nothing hidden
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class AssignmentClassification:
    provider_assignment_id: int
    provider_name: str
    d1: CadenceCapabilityAssessment
    d2: IdentifierCompatibilityAssessment
    d4: FallbackConsiderationResult


@dataclass(frozen=True)
class AcquisitionQualityClassification:
    series_id: int
    d3: D3Result
    assignments: tuple[AssignmentClassification, ...] = field(default_factory=tuple)


def classify_acquisition_quality(
    snapshot: dict,
    *,
    cadence_tolerance: timedelta,
    fixture_confirmation: FixtureConfirmation | None = None,
    material_impact: bool | None = None,
) -> AcquisitionQualityClassification:
    """The production caller: assembles evidence from one `AcquisitionEvidenceSnapshot` dict and
    runs it through D1-D4 exactly as designed -- D3 population-level, D1/D2/D4 per assignment.
    Performs no action and mutates nothing; returns a classification only."""
    d3 = classify_d3(snapshot, fixture_confirmation=fixture_confirmation)
    assignments = tuple(
        AssignmentClassification(
            provider_assignment_id=a["provider_assignment_id"],
            provider_name=a["provider_name"],
            d1=classify_d1(a, tolerance=cadence_tolerance),
            d2=classify_d2(a),
            d4=classify_d4(a, material_impact=material_impact),
        )
        for a in snapshot["assignments"]
    )
    return AcquisitionQualityClassification(
        series_id=snapshot["series_id"], d3=d3, assignments=assignments
    )
