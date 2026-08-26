# `SUPERSEDED` — Workbench Implementation

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: Workbench-side implementation complete and tested. `histfints-v3` side NOT
implemented — per the standing sibling-repo rule, writing to `histfints-v3` requires PO
confirmation first. The exact planned edits are specified at the end of this document for that
confirmation, not yet applied.**

No production data or database schema modified anywhere. No change to
`class_e_identity_signal.py` — confirmed by new non-regression tests, not merely by omission.

---

## 1. What was implemented (Workbench: `panel.py`, `panel_eligibility_service.py`, `acquisition_quality_capability.py`)

### 1.1 Panel/analysis eligibility — default exclusion + opt-in + output qualification

- `domain/panel.py`: added `ExclusionReason.SUPERSEDED` (docstring cites the approved DFA
  definition verbatim); added `PanelEligibilityParameters.include_superseded: bool = False` —
  the shared semantic name for "include superseded/historical" across Workbench surfaces, per
  instruction; added `PanelMembershipSnapshot.superseded_included_series_ids: list[int]`;
  added `PanelResult.historical_evidence_qualification: str | None`.
- `application/panel_eligibility_service.py`: `compute_panel_eligibility()` gained a new
  branch mirroring the existing `DELISTED_OR_DISCONTINUED` pattern exactly — default-excludes
  `status = 'SUPERSEDED'` with `ExclusionReason.SUPERSEDED`; when `include_superseded=True`,
  tracks which of the *actually included* Series are SUPERSEDED (re-intersected against the
  final inclusion list after every later exclusion step, so the tracking reflects what really
  made it into the result, not just what step 1b alone saw). `compute_panel_result()` sets
  `historical_evidence_qualification` to a fixed message — the approved sentence verbatim, plus
  the specific Series ids — whenever any SUPERSEDED Series was opted in. This is the "visible
  superseded/historical-evidence qualification on opted-in output" SE required.

### 1.2 Acquisition-quality needs-attention aggregates — unconditional exclusion

- `application/acquisition_quality_capability.py`: added
  `NeverStateReason.SUPERSEDED_NOT_CURRENT_ATTRIBUTION` and
  `AcquisitionQualityPopulationMembership.EXCLUDED_SUPERSEDED`. Both are **non-heuristic** —
  unlike `NON_PRODUCTION_FIXTURE_CANDIDATE`/`CANDIDATE_UNCONFIRMED` (which require human
  confirmation and default to inclusion pending review), `Series.status` is already an
  authoritative fact, so SUPERSEDED is checked first and excludes unconditionally, with no
  pending-review state. `classify_never_state()` and `classify_population_membership()` both
  gained an `is_superseded` parameter, checked before the fixture-heuristic logic in each.
  `PopulationRow` gained `is_superseded: bool = False`, and
  `filter_for_acquisition_quality_metrics()` routes SUPERSEDED rows to `excluded`.

### 1.3 `class_e_identity_signal.py` — confirmed unchanged

No edit made. Confirmed by three new non-regression tests (not merely by omission): the
snapshot dataclass has no `status` field, `detect_identity_candidates()`'s signature is
unchanged, and a real 11345/11346-shaped pair still produces no candidate — this module has
never inspected `Series.status` and continues not to.

### 1.4 Test infrastructure finding, surfaced and worked around (not silently absorbed)

`tests/conftest.py`'s shared `PRODUCTION_USER_VERSION` constant was pinned at `10`, verified
live 2026-08-17 — but live production is now at `user_version=17` (migrations 0011-0017,
including 0017's SUPERSEDED support). **Bumping the shared constant to 17 broke multiple
unrelated existing tests** (`test_reconciliation_boundary.py`, panel-eligibility phase1/phase2
delisted and trade-evidence cases) — a real, separate schema-drift finding, not something to
fix as a side effect of this task. **Reverted** that bump; added an isolated
`histfints_copy_v17` fixture instead (mirroring the existing `histfints_copy_migrated`
precedent) so only the new SUPERSEDED-specific tests use the newer schema. The stale-constant
finding itself is flagged in `conftest.py`'s own comment for whoever picks up the broader
migration-currency question later — not resolved here.

---

## 2. Tests added

| File | New/updated tests | Covers |
|---|---|---|
| `tests/test_panel_eligibility_superseded.py` (new) | 5 | Default exclusion with correct `ExclusionRecord`; explicit opt-in inclusion; opted-in result carries the visible qualification (checks both approved-sentence fragments and the specific Series id); default result carries no qualification; qualification correctly narrows to only Series that survive later exclusion steps. |
| `tests/test_acquisition_quality_capability.py` | 6 new (`TestSupersededExclusionFromNeedsAttention`) | SUPERSEDED takes priority in `classify_never_state()`; overrides a coincidental fixture-candidate flag; falls through correctly when not SUPERSEDED; unconditional exclusion in population membership with no pending-review state even when a fixture flag is also set; a real 11344/11345/11346-shaped filter run excludes exactly the two SUPERSEDED ids. |
| `tests/test_class_e_identity_signal.py` | 3 new (`TestSupersededNonRegression`) | Snapshot type has no `status` field; `detect_identity_candidates()`'s signature is exactly `{series, venue_suffixes}`; a real 11345/11346-shaped pair still resolves to zero candidates. |

**Full suite: 167 passed, 1 skipped, 1 pre-existing unrelated failure (series 11312's live
`configured_interval`), zero regressions.**

---

## 3. `histfints-v3` — NOT implemented, awaiting PO confirmation to write

Per the standing rule (read sibling folders freely; ask PO before writing there), the following
is the **exact planned change set**, specified precisely so confirmation can be given without
another design round — nothing here has been applied:

1. **`series.py:115-134`** — add `"SUPERSEDED": "Superseded"` to `_SERIES_STATUS_LABEL`.
2. **`series_page()` (`web.py:537-566`)** — add a default filter excluding `status ==
   SUPERSEDED` from `all_series`, controlled by a new query parameter (e.g.
   `?include_superseded=1`), following the existing `technical=1` toggle idiom. The existing
   direct `?id=` hand-off path is left untouched (already bypasses `q`), preserving
   discoverability.
3. **`series.html`** — move the current ad-hoc inline SUPERSEDED caveat into the existing
   `field_help`/`field_help_floating` macro, carrying the approved sentence verbatim as the
   explanatory help; the row itself shows only the new compact label from item 1.
4. **`ImportStatusView.list_status()` (`import_status_view.py:86-109`)** — exclude
   `status == SUPERSEDED` from the default population, with the same explicit
   `include_superseded`-style filter access SE required (mirroring item 2's parameter name for
   the shared semantic, exposed as its own toggle on this page per instruction: "one shared
   semantic rule... while allowing individual surfaces to expose it differently").
5. Tests for items 1–4, in `tests/presentation/test_web.py`, mirroring the existing
   `_seeded_status_page`/`_row_by_label` conventions from the earlier UX-pilot test additions.

No other `histfints-v3` file needs a change for this directive — the bulk-scheduled path
(`run_scheduled_route`) already filters by `status != ACTIVE` and needs no SUPERSEDED-specific
addition.

**Requesting confirmation to proceed with items 1–5 above.**
