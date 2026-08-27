# Acquisition-Quality D1–D4 Status Assessment

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: read-only assessment. No schedule, provider assignment, Series, observation, schema,
migration, or production-policy state inspected beyond static code/test review and running the
existing DB-free test suite. No production data touched.**

Assesses `src/hf_reswb/application/acquisition_quality_capability.py` (as it exists today,
including the later SUPERSEDED-exclusion extension) against the four DFA-approved requirements
from `ACQUISITION_QUALITY_CAPABILITY_DESIGN_D1_D5_2026-08-22.md` and
`D3_D4_APPROVED_DESIGN_INCREMENT_2026-08-22.md`. **Verified directly, not assumed**: read the
current module source in full, cross-checked every type/function named in both design docs
against it, ran `tests/test_acquisition_quality_capability.py` (45 passed, 0 failed, 0 skipped —
39 from the original two design passes + 6 added for SUPERSEDED), and grepped the codebase for
production callers (none found outside the module's own re-export in
`application/__init__.py`, which imports names but invokes nothing).

---

## D1 — Cadence/currentness capability

**Status: IMPLEMENTED** (classifier only; policy use remains gated, as designed).

- `CadenceCapabilityVerdict` / `CadenceCapabilityAssessment` / `assess_cadence_capability()`
  present exactly as specified: gaps between consecutive successful-run timestamps, compared
  against a caller-supplied `tolerance`, with `margin` reported as evidence rather than judged.
  `min_samples` floor (default 3) still gates `INSUFFICIENT_EVIDENCE` correctly.
- Unaffected by the SUPERSEDED work — no reference to `Series.status` anywhere in this section.

**Evidence gates still unavailable:** a DFA-approved margin-sufficiency threshold. The module
still deliberately returns only SUFFICIENT/INSUFFICIENT_MARGIN based on sign of the margin, not
a "how much margin is enough" judgment — unchanged since 2026-08-22, no new blocker introduced.

**Smallest next technical increment:** none required to keep D1 at its current, complete
classifier scope. The only forward step is a live caller — a read-only reporting view that
pulls a Series' `staleness_tolerance` and successful-run history from `histfints-v3` (read-only,
per D-001) and passes them through `assess_cadence_capability()` — which is a wiring task, not a
classifier change, and still cannot use the output for any decision until DFA sets the margin
threshold.

---

## D2 — Identifier/provider acquisition-compatibility validation

**Status: IMPLEMENTED.**

- `RunOutcome` / `IdentifierCompatibilityVerdict` / `IdentifierCompatibilityAssessment` /
  `assess_identifier_compatibility()` present exactly as specified: outcome-history-only, no
  identifier string inspected (confirmed again by reading the function body — no string
  parameter exists at all, only a `list[RunOutcome]`), satisfying D2's prohibition on a
  universal `.`/`$` syntax rule.
- Unaffected by the SUPERSEDED work.

**Evidence gates still unavailable:** none for the classifier itself. D2 was never blocked;
this remains true. (Productive use still requires a caller assembling real per-`(provider,
identifier)` outcome history, but that is a wiring gap, not an evidence gate.)

**Smallest next technical increment:** a read-only query against `histfints-v3`'s
`import_run`/`import_error` tables to build the `list[RunOutcome]` for a real `(provider,
identifier)` pair, then call the existing function — no new classification logic needed.

---

## D3 — Separation/exclusion of test/non-production and assignment states

**Status: IMPLEMENTED**, and this is the item most changed since 2026-08-22 — two increments,
not one, both present in the current file.

1. **NEVER-state evidence model** (`NeverStateReason`, `looks_like_non_production_fixture()`,
   `classify_never_state()`): present as designed. `NO_PROVIDER_ASSIGNMENT` /
   `ASSIGNED_NOT_YET_RUN` / `NON_PRODUCTION_FIXTURE_CANDIDATE` all correctly distinguished; the
   Class-C orphan disposition (11344/11347) is confirmed still unreinterpreted by a dedicated
   test.
2. **Formal population semantics and exclusion mechanism** (SR-approved increment):
   `NonProductionFixtureStatus`, `FixtureConfirmation`, `determine_fixture_status()`,
   `AcquisitionQualityPopulationMembership`, `PopulationRow`, `PopulationFilterResult`,
   `filter_for_acquisition_quality_metrics()` — all present, all matching the three-state
   design (`NOT_A_FIXTURE` / `CANDIDATE_UNCONFIRMED` / `CONFIRMED_FIXTURE`) that requires an
   explicit, attributed `FixtureConfirmation` before anything is excluded — a heuristic match
   alone still only ever reaches `CANDIDATE_UNCONFIRMED` / `INCLUDED_PENDING_FIXTURE_REVIEW`.
3. **SUPERSEDED exclusion** (this session, 2026-08-26, SE directive on `SeriesStatus.SUPERSEDED`):
   `NeverStateReason.SUPERSEDED_NOT_CURRENT_ATTRIBUTION` and
   `AcquisitionQualityPopulationMembership.EXCLUDED_SUPERSEDED` added; `classify_never_state()`
   and `classify_population_membership()` both take a new `is_superseded` parameter checked
   **first**, ahead of the fixture heuristic — an authoritative `Series.status` fact requires no
   human confirmation, unlike the fixture candidate flag, and this priority ordering is
   explicit in both function docstrings and enforced by dedicated tests
   (`TestSupersededExclusionFromNeedsAttention`, 6 tests) plus non-regression tests confirming
   `class_e_identity_signal.py` remains status-blind throughout.

**Evidence gates still unavailable:** the storage/recording location for a real
`FixtureConfirmation` (who confirms, where it's persisted) is still an open product decision —
restated from 2026-08-22, not newly blocked. `SUPERSEDED` exclusion has no equivalent gap since
`Series.status` is already a stored, authoritative field — this is why it was implemented as an
unconditional exclusion rather than a pending-review state.

**Smallest next technical increment:** a read-only reporting view that (a) builds
`PopulationRow`s from `histfints-v3`'s `series.status` plus a fixture-candidate check on
`series.label`, and (b) calls `filter_for_acquisition_quality_metrics()` to get
included/pending/excluded id sets for a real acquisition-quality report. The classification
logic needs no further work; only a caller is missing.

---

## D4 — Evidence-gated conditional fallback

**Status: IMPLEMENTED** (classifier and activation gate; actual activation remains blocked by
design, not by an implementation gap).

- **Conditional fallback consideration** (`FallbackCandidateEvidence`, `FallbackConsiderationVerdict`,
  `FallbackConsiderationResult`, `consider_fallback()`): present, with materiality checked first
  (`material_impact is not True` → `MATERIALITY_UNKNOWN`), then all-dimension adequacy. Confirmed
  no Series-id parameter exists anywhere in this section — cannot be used to assert a universal
  coverage policy, matching D4's explicit prohibition.
- **Evidence-gated activation** (SR-approved increment): `FallbackActivationVerdict` (four
  members), `FallbackActivationResult`, `evaluate_fallback_activation()` — present exactly as
  designed, layering an explicit `fallback_activation_enabled` flag (default `False`) on top of
  `consider_fallback()`'s adequacy result. A seventh dimension, `comparability_acceptable`, is
  present on `FallbackCandidateEvidence` and correctly included in both `is_fully_adequate()`
  and `unresolved_dimensions()`.
- **Confirmed by direct grep, not assumed**: no caller anywhere in this codebase (including
  after the SUPERSEDED work, which did not touch this section) sets
  `fallback_activation_enabled=True`. `evaluate_fallback_activation` and `consider_fallback` are
  both re-exported from `application/__init__.py` but never invoked there or elsewhere.

**Evidence gates still unavailable — this is D4's real bottleneck, unchanged since 2026-08-22:**
most real `(candidate)` evaluations today would receive `None` on several of the seven
dimensions, because adjustment-basis, provenance, and comparability evidence is largely
unrecorded in HistFinTS (D-005/D-021, and the G1/G9 dimension-availability survey — restated,
not new). In practice this means real calls would land on `WARRANTED_CANDIDATE_INADEQUATE` /
`DISABLED_BY_DEFAULT` far more often than an adequate/activated result — an accurate reflection
of the evidence gap, not a defect in the classifier.

**Smallest next technical increment:** none on the classifier side — it is complete and tested
against every named dimension including comparability. The only forward step is upstream, in
HistFinTS: populating `adjustment_basis` and provenance metadata (the Tranche 2 migration, still
unconfirmed landed per `DECISIONS.md`'s Tranche table) would be what actually changes real-world
`consider_fallback()` outcomes from mostly-inadequate to sometimes-adequate. No Workbench-side
implementation step would change this outcome distribution.

---

## D0 designation

**No artifact in this codebase uses a "D0" designation.** Grepped `src/`, `tests/`, and `docs/`
for `\bD0\b` — zero matches. D1 is confirmed as the lowest-numbered item in both design documents
and the implementation; there is no gap in the numbering and no undocumented predecessor item.
Reported explicitly per instruction rather than creating one where none exists.

---

## Summary table

| Item | Status | Evidence gate still unavailable | Smallest next increment |
|---|---|---|---|
| D1 (cadence capability) | Implemented | DFA margin-sufficiency threshold (policy use only) | Wire a real caller against `histfints-v3` run history; no classifier change |
| D2 (identifier compatibility) | Implemented | None | Wire a real caller against `import_run`/`import_error`; no classifier change |
| D3 (NEVER/population semantics + SUPERSEDED) | Implemented | `FixtureConfirmation` storage/recording location (product decision) | Wire a real reporting view calling `filter_for_acquisition_quality_metrics()` against live `series.status`/labels; no classifier change |
| D4 (evidence-gated fallback) | Implemented | Adjustment-basis/provenance/comparability evidence in HistFinTS (Tranche 2, unconfirmed landed) | None Workbench-side; upstream HistFinTS metadata population is the actual unblock |
| D0 | Not applicable | — | No artifact uses this designation; none created |

**Net assessment:** all four DFA-approved capabilities are fully implemented as pure,
DB-free evidence classifiers with complete test coverage (45/45 passing) and zero production
callers — no automatic fallback, exclusion, or remediation is active anywhere in this codebase.
What remains for each is not classifier work but (a) wiring real callers against live
`histfints-v3` data (D1–D3, a read-only integration task) and (b) upstream evidence that only
HistFinTS's own schema/data can supply (D4, and D1's policy-use case pending a DFA threshold).
Nothing here was implemented, mutated, or activated by this assessment.
