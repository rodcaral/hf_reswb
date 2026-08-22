# Import & Status Presentation — Independent Read-Only Verification

**Date:** 2026-08-22
**From:** SDT Workbench
**To:** SE
**Status: read-only review of HistFinTS's own source (`histfints-v3`), not this project's code.
No UI, production data, or schema modified. Read-only queries only, against the live database
and the sibling repository's source files.**

**Scope note**: `import_status.html`, `import_status_view.py`, and `import_state.py` live in
`histfints-v3`, not `hf_reswb-v1` — HistFinTS's own application, not the Workbench. Per D-001
this project treats HistFinTS as read-only at the *database* level; reading its source code for
a review, without modifying anything, is consistent with that boundary and with this session's
prior practice of reading `histfints-v3/docs/` as reference material.

---

## 1. Is "105 = 65 failed + 32 stale + 8 never" backed by the actual definitions and logic?

**Partially — the formula's structure is correct and the FAILED/STALE counts reproduce
exactly; the NEVER count and therefore the 105 total do not match current live state.**

Independently re-implemented `classify_import_state()`'s exact logic (`histfints-v3/src/
histfints/domain/import_state.py`) against a fresh read-only query of the live database (not
copied from the app, not assumed from the docstrings) and computed every ACTIVE series' state
directly:

| State | Cited | Independently reproduced, live, now |
|---|---|---|
| FAILED | 65 | **65 — exact match** |
| STALE | 32 | **32 — exact match** |
| NEVER | 8 | **12 — does not match** |
| **Total "needs attention"** | **105** | **109** |

**The formula itself (`needs_attention = FAILED + STALE + NEVER`) is exactly what the code
does** — `ImportStatusView.summary()` (`import_status_view.py` lines 121-124) sums precisely
those three `ImportState` values, matching the domain enum and the template's attention-bar
(`import_status.html` line 31, iterating `by_state.items()` filtered to the same three names).
**No RUNNING or PARTIAL row is ever miscounted into "needs attention"** — confirmed by reading
both the summary code and the template.

**Why NEVER differs (12, not 8) — investigated, not merely flagged**: `NEVER` covers two
distinct populations, both correctly classified by the code, but the cited figure of 8 appears
to have been measured at an earlier point using only one of them:

- **6 series with zero `provider_assignment` at all** (`11344`, `11347`, `11356`, `11360`,
  `11367`, `11368`) — of these, `11344` and `11347` are the already-documented GLD/UBER Class-C
  orphan targets from this session's own prior work (`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`);
  the other four are unexamined by this review and outside its scope.
- **6 series with a provider assignment but zero `import_run` rows yet**
  (`11304`, `11306`–`11310`) — consecutive, low-density series ids, consistent with recently
  catalog-added series that have not yet had a first scheduled/manual run attempt.

`ImportStatusView`'s own docstring (`series_import_status.is_scheduled`, line 54) states "11,375
of 11,383 ACTIVE Series are scheduled; the eight that are not are exactly the assignment-less
ones" — an 8-series figure that **only covers the assignment-less half** of `NEVER`, not the
assigned-but-not-yet-run half. **This reads as ordinary data drift since that comment (and
whatever screenshot produced "105") was written — active series count has grown from 11,383 to
11,387 in the interim, and 6 new series entered the "not yet run" state — not as a defect in the
classification logic**, which reproduced FAILED and STALE exactly and treats both `NEVER`
populations correctly per its own documented rule (`import_state.py` lines 66-68: "NEVER...
distinguished from STALE... they need different actions").

**Recommendation, not a code change**: if a stable "8" figure is expected to persist over time,
it should not be — `NEVER`'s two constituent populations both grow with ordinary catalog
activity (new assignment-less orphans, newly added series pending their first run), so this
count should be expected to drift and be re-measured at point of use, not treated as a fixed
baseline.

---

## 2. Does the UI provide sufficient visibility into failure reason/history?

**Partially — full detail exists, but is not visible at the scale needed to triage 65 failures
efficiently. This is the one material visibility gap identified.**

**What exists and works correctly**:
- Every `ImportRun` row's failure detail (`ImportErrorRecord`: category — `NETWORK`/`API`/
  `VALIDATION`/`DATABASE`/`OTHER` — plus a free-text `message`, plus `occurred_at`) is fully
  retained and rendered on the per-series **History** page (`import_history.html` lines 17-23),
  most-recent-run-first, with no row limit (`import_service.list_import_history()` is a
  pass-through to `ImportRunRepository.list_for_series()`, unfiltered).
- The main table's `Result` badge (`import_status.html` lines 189-192) intentionally shows only
  the state label (`✕ Failed`) — **by explicit design**, documented in `LatestRun`'s own
  docstring (`repositories.py` lines 96-101): "hydrating the full aggregate... for 11,000+
  Series to render one badge per row would load a great deal of data no one displays." This is
  a deliberate, reasoned performance tradeoff, not an oversight.

**The material gap**: there is no way to see *why* the 65 failures failed without opening each
of the 65 series' History pages **individually, one at a time** — no failure-category column,
no aggregate breakdown (e.g. "40 NETWORK, 15 API, 10 OTHER"), no bulk/CSV export of recent error
messages, and no filter by error category (the filter bar offers only Status/Type/Provider/
Interval — confirmed by reading the filter options and query-param handling in `web.py` lines
700-725). An operator trying to triage a batch of 65 failures — e.g., to tell whether most are
one root cause (a single provider outage) versus 65 unrelated causes — has no way to see that
pattern without 65 separate page loads.

**Not flagged as gaps** (deliberately excluded, per instruction's "materially impede" bar):
- The badge-only main table is a reasoned tradeoff, not a gap — the detail is one click away,
  not missing.
- Minor cross-request staleness (the attention-bar's counts and a subsequently-clicked filtered
  view are each computed fresh per request; if state changes between two page loads, they could
  briefly disagree) is an inherent property of any live-queried dashboard across two separate
  requests, not a defect, and not material to diagnosing failures.

---

## 3. Discrepancies between displayed status and underlying acquisition state

**None found beyond the NEVER-count drift already reported in §1.** Specifically checked and
ruled out:
- **Stuck/orphaned in-flight runs**: exactly one `import_run` row has `ended_at IS NULL`
  (id 95860, `started_at` 2026-08-22T12:00:42Z) — its start time is current/recent relative to
  this review, consistent with a genuinely in-flight scheduled run, not a crashed process stuck
  showing `RUNNING` indefinitely. No evidence of a state/reality mismatch here today, but this
  was verified by query, not assumed — a stuck run of this kind, if it ever occurred, would be
  exactly the sort of thing this classifier could misrepresent (perpetually `RUNNING` instead of
  surfacing as needing attention), so it is worth re-checking periodically rather than assuming
  it can't happen.
- **Status vocabulary**: `import_run.status`'s actual stored values are `SUCCESS`/`FAILED`/
  `PARTIAL`/`IN_PROGRESS` (confirmed by query) — the domain's `ImportState.RUNNING` label is a
  *derived* presentation state (from `ended_at IS NULL`), never a stored value; `classify_
  import_state()` correctly checks `ended_at is None` before checking `last_status`, so an
  in-flight run's placeholder status can never be misread as its outcome (`import_state.py`
  lines 71-74, its own comment states this reasoning explicitly, and the code matches it).

---

## Summary

| Question | Answer |
|---|---|
| Is 105 = 65+32+8 backed by the definitions and logic? | FAILED (65) and STALE (32) reproduce exactly. NEVER is 12, not 8, live now — explained by ordinary catalog drift (new assignment-less and not-yet-run series), not a logic defect. Current total is 109, not 105. |
| Sufficient visibility into failure reason/history? | Full detail exists per-series via History, unlimited, most-recent-first. **Gap**: no bulk/aggregate view of failure reasons across the 65 — triage requires opening each series individually. |
| Discrepancies between displayed status and underlying state? | None found today. The one in-flight run is genuinely current, not stuck. Verified the RUNNING/status-vocabulary distinction is handled correctly by the code, not merely by convention. |

No UI or production state was modified in producing this review.
