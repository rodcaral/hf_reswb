# `SUPERSEDED` — Cross-Repository Integration/Semantic Consistency Review

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: read-only review only. No file modified in either repository. Confirms/denies
consistency between the completed Workbench implementation and the now-returned HistFinTS
implementation; makes no changes to either.**

---

## Summary

| Dimension | Workbench | HistFinTS UI | Consistent? |
|---|---|---|---|
| Approved meaning (definition text) | Cited verbatim | Cited verbatim | **Yes** |
| Default exclusion from ordinary listings | **Implemented** (panel eligibility, acquisition-quality aggregates) | **Not implemented** (Series page, Import & Status both still show SUPERSEDED unfiltered) | **No — real gap** |
| Explicit historical/opt-in access | `include_superseded=True` | N/A — nothing is excluded by default, so there's nothing to opt into | **Moot, not fulfilled by design** |
| Compact label ("Superseded") | N/A (no label rendering in Workbench) | **Not implemented** — `_SERIES_STATUS_LABEL` has no entry; the raw enum string `"SUPERSEDED"` renders | **No — deviates from the literal requirement** |
| Help text (approved sentence verbatim) | Used verbatim in `historical_evidence_qualification` | **Different text**: `"(historical record — see Domain Model docs)"` — a paraphrase, not the approved sentence, deferring to external docs | **No — wording differs** |
| Analysis-output qualification | **Implemented** (`PanelResult.historical_evidence_qualification`) | N/A — no analysis/panel feature exists in this UI | **Consistent by absence, not a gap** |
| `class_e_identity_signal` unchanged | Confirmed, tested | N/A (Workbench-only module) | **N/A** |

**Bottom line: the two implementations do not yet converge on the same behavior.** They agree
on *what SUPERSEDED means*; they diverge on *what a user sees by default* and on the *exact
label/help wording*. HistFinTS implemented a materially different, additional facet of the
ruling (see §3) that Workbench's design didn't anticipate and SE's original directive to
Workbench didn't request.

---

## 1. Meaning — consistent

Both `histfints-v3/src/histfints/domain/series.py:29-55` and
`workbench/src/hf_reswb/domain/panel.py`'s `ExclusionReason.SUPERSEDED` docstring cite the
identical DFA-approved definition. No divergence found.

## 2. Default exclusion — real gap, HistFinTS side

Checked directly, not assumed: `series_page()` (`web.py:537-566`) still builds `all_series`
from unfiltered `list_active()` with no status-based exclusion of any kind; `ImportStatusView.
list_status()` (`import_status_view.py`) has **zero** occurrences of `SUPERSEDED` anywhere
(confirmed by grep, no matches). Both surfaces render 11345/11346 exactly as they did before
this entire workstream began — unchanged.

Workbench, by contrast, excludes `status = 'SUPERSEDED'` by default in both
`compute_panel_eligibility()` and `acquisition_quality_capability`'s aggregate-membership
filter, per the 2026-08-26 implementation.

**Consequence**: the "normal/current Series listings exclude SUPERSEDED" requirement from SE's
directive is satisfied on the Workbench side and not satisfied on the HistFinTS UI side.

## 3. What HistFinTS implemented instead — a different, real facet of the ruling

Not requested by SE's directive to Workbench, and not anticipated by the Workbench-side design,
but a legitimate reading of the same DFA ruling: **write-action guarding.**

- `Series.is_current_attribution` (`series.py:181-188`): `True` for every status except
  SUPERSEDED.
- `SeriesService.enable_series()` now **rejects** a SUPERSEDED Series outright
  (`series_service.py:256-269`), forcing a separate, deliberate `reactivate_series()` call
  instead — so a SUPERSEDED Series can never leave that status as a side effect of the ordinary
  Enable action.
- `add_provider_assignment()` similarly rejects adding an assignment to a SUPERSEDED Series
  (`series_service.py:191-193`).
- `series.html` gained a conditional **Reactivate** button (line 102-104), shown only for
  SUPERSEDED rows, alongside the existing Enable/Disable/Archive/Unarchive actions.

This is a coherent, DFA-ruling-consistent addition — "no longer the current attribution"
plausibly implies ordinary write actions shouldn't silently apply to it — but it is **additive
to**, not a substitute for, the visibility/eligibility behavior SE's directive specified.
Flagging the scope difference rather than treating either side as wrong.

## 4. Label and help text — both deviate from the literal wording SE specified

- **Label**: `_SERIES_STATUS_LABEL` (`web.py:115-120`) has entries for `ACTIVE`,
  `USER_DISABLED`, `DELISTED_OR_DISCONTINUED`, `PROVIDER_UNAVAILABLE` — **no `SUPERSEDED`
  entry**. `_series_status_label()`'s fallback (`return _SERIES_STATUS_LABEL.get(status,
  status)`) means the raw enum string `"SUPERSEDED"` renders on the Series page, not the
  "Superseded" compact label SE specified.
- **Help text**: the Series page's inline caveat now reads `"(historical record — see Domain
  Model docs)"` (`series.html:28`) — different wording from the approved sentence ("Retained for
  historical/provenance purposes; no longer the current attribution.") SE specified as the
  required help meaning, and it defers to external documentation rather than surfacing the
  meaning inline.
- One relevant code comment, read carefully rather than taken as contradicting production data:
  `web.py:108-114` states *"no code path in this codebase ever sets [SUPERSEDED]... giving it a
  confident gloss here would be exactly the invented meaning [the spec] prohibits."*
  **Verified this is narrowly accurate**: exhaustive grep across `histfints-v3/src/` finds no
  application method that assigns `SeriesStatus.SUPERSEDED` — the two real instances (11345/
  11346) were produced by the one-off SDT-1 data operation, not a reusable code path. Not a
  factual error on HistFinTS's part, but it does mean **no general mechanism exists today for
  a future reattribution to reach SUPERSEDED except another bespoke, out-of-band operation** —
  a real gap worth naming, separate from the label question above.

## 5. Analysis-output qualification — not applicable on the HistFinTS side, not a gap

HistFinTS's UI has no comparison/panel/analysis feature (confirmed in the earlier
`SUPERSEDED_UI_CONSUMER_ASSESSMENT_2026-08-26.md` review, unchanged). There is nothing on that
side to carry an output-level qualification. This dimension is consistent by absence, not a
divergence to resolve.

---

## What this review does not do

- Makes no change to either repository.
- Does not decide which side's wording/behavior should change to converge — that's a
  cross-team product decision for SE/PO, not a Workbench call.
- Does not reopen the financial disposition of 11345/11346, used here only as the concrete,
  already-established test cases both sides' code paths were checked against.
