# Import & Status UX Pilot — Implementation & Validation Report

**Date:** 2026-08-24
**From:** SDT Workbench
**To:** SE/SDT, UI/UE, PO
**Contract:** `histfints_uiue/003_Import_and_Status_UX_Pilot_Implementation_and_Validation.md`
(depends on `002_Import_&_status UX_pilot_specification.md`)
**Repository:** `histfints-v3` (has no version control — no commit exists; changes are plain
filesystem edits, verified by a full local test run, 1257 passed / 92 deselected, zero
regressions).

---

## 1. What was implemented

| Contract item | Change | File(s) |
|---|---|---|
| Run availability/explanation, keyboard discoverability (§4.1, V-01, A-02) | Disabled Run's reason is now rendered as **static, always-visible text** (`.run-unavailable-reason`) next to the button, not only inside a hover-only `title` attribute — a disabled `<button>` cannot receive keyboard focus, so `title` alone was undiscoverable without a mouse. | `import_status.html` |
| Series-specific accessible names (§10, A-03) | `aria-label="Run import for [Series]"` / `aria-label="View import history for [Series]"` on both actions, including the disabled Run (labelled "— unavailable"). | `import_status.html` |
| Dynamic status feedback (§10, A-04) | Flash-message container now carries `role="status"/aria-live="polite"` (or `role="alert"/aria-live="assertive"` when any message is an error) so completion/failure feedback is exposed to assistive technology. The "Working…" job page's decorative progress bar is marked `aria-hidden="true"` (it conveyed nothing text didn't already say and would have been visually clipped by its own `overflow:hidden`); a new visible status line ("Import is running…") carries `role="status"/aria-live="polite"` instead. | `base.html`, `job_running.html` |
| User-facing terminology, no raw enums (§5, §9, V-04, V-09) | New `describe_run_outcome(run, series_label)` translates `run_import()`'s result into acquisition-qualified feedback: no-assignment → explanation; unfinished run returned (concurrent case, `ended_at is None`) → *"an import is already running; no second import was started"*; `SUCCESS`/`PARTIAL`/`FAILED` → acquisition-qualified sentences, `PARTIAL`/`FAILED` pointing to History. **Never emits a raw `ImportRunStatus` value.** | `import_status_view.py` (new function), `web.py` (`run_import_route` now calls it) |

---

## 2. What was deliberately not changed, and why

- **Concurrent-Run semantics** (`ImportService.run_import()`'s lock/resume logic): untouched.
  `describe_run_outcome()` only *interprets* the already-returned `ImportRun` (via `ended_at is
  None`) — it calls nothing new and changes no service-layer behavior. Per contract §4.2 and
  the "Do not" list, this was correctly left to PO if a *behavioral* change is ever wanted.
- **`USER_DISABLED` per-row Run asymmetry** (§4.3): untouched. Not silently normalized.
- **`Needs attention` aggregation rule** (§7): untouched — no new canonical state introduced,
  no candidate set presented as final. This increment did not touch the summary/aggregation
  code at all.
- **Bulk "Run Scheduled Imports" messaging** (`run_scheduled_route`): still emits raw
  `run.status.value` per Series in its flash summary, **unlike** the per-Series Run path just
  fixed. Scoping decision, not an oversight: every V-01–V-12 scenario in the contract describes
  a single-Series interaction; the bulk path is a distinct, multi-Series summary the contract's
  non-goals ("Aggregate failure triage... remain out of scope") point away from. Flagged here
  explicitly rather than left as a silent inconsistency — if UI/UE or PO wants the same
  treatment applied there, that is a follow-up, not something this increment silently decided.
- **Job-polling transport** (`<meta http-equiv="refresh" content="1">` in `job_running.html`):
  left in place. Only its *announcement semantics* were added (the new status line). Replacing
  full-page meta-refresh with non-disruptive JS polling was considered and not done — it would
  be a materially larger, higher-risk change with no test harness in this session to verify
  actual browser polling/redirect-following behavior end to end, and the contract's own §10
  "Verification boundary" explicitly warns against claiming validation that hasn't occurred.

---

## 3. Validation performed

**Real, executable tests** (`histfints-v3`'s own pytest suite — a Flask test client, not a
browser), not merely a description:

- `tests/application/test_import_status_view.py` (new, 6 tests): every `describe_run_outcome()`
  branch, including the concurrent-run case built directly on `ImportRun.ended_at is None` (the
  same signal a real lock-contention return value carries) — asserts the raw enum text never
  appears and the Series identity is present in every message.
- `tests/presentation/test_web.py` (4 new tests, 2 existing tests updated):
  - Disabled-Run reason renders as real visible content, not only a `title` attribute (V-01/A-02).
  - A NEVER Series *with* a provider assignment gets a live Run control (V-02) — the assignment,
    not the state label, gates availability.
  - A RUNNING row keeps Run enabled (V-03/§4.2's verified behavior) — a regression test
    protecting this specific "do not disable merely because RUNNING" guarantee going forward.
  - Run/History both carry Series-specific `aria-label`s, including on the disabled Run (A-03).
  - The two pre-existing Run-outcome tests were updated from asserting the old raw
    `"ImportRun {id}: {status}"` text to the new acquisition-qualified wording.
- **Full suite**: 1257 passed, 92 deselected (pre-existing marker exclusions, e.g. tkinter/GUI
  tests needing a display), zero failures, zero regressions.

**Not performed, explicitly** (per contract §10's own verification boundary): a real
screen-reader session. Nothing in this report or its tests claims that validation occurred —
the `aria-live`/`role`/`aria-label` additions are markup-level, verified present in rendered
HTML by the test suite, not verified as correctly announced by any specific assistive
technology.

---

## 4. Validation-scenario coverage, stated precisely

| Scenario | Addressed by this increment | How |
|---|---|---|
| V-01 NEVER without provider | Yes | Static visible reason text + `aria-label`, tested. |
| V-02 NEVER with provider | Yes | Run enabled, tested. |
| V-03 Running | Yes | Run stays enabled (pre-existing, now regression-tested); no implication a second import is useful (unaffected by this pilot's messaging change until actually clicked). |
| V-04 Concurrent Run | Yes | `describe_run_outcome()`'s "already running" branch, unit-tested against the exact `ended_at is None` signal the real concurrent path produces. |
| V-05 Failed | Yes | Acquisition-qualified wording, points to History, tested. |
| V-06 Stale | Not touched by this increment | Existing `⚠ Stale` badge already avoided a financial-invalidity implication before this pilot; no code change was needed here. |
| V-07 Partial | Yes (feedback wording) | `describe_run_outcome()`'s `PARTIAL` branch, tested. Row rendering (`◐ Partial`, distinct from Failed/Stale) pre-existing, unchanged. |
| V-08 OK | Not touched | Pre-existing `✓ OK` rendering; no misleading "certification" language exists there and none was added. |
| V-09 Run completion | Yes | Fresh-query redirect flow confirmed unchanged/correct by reading `job_status_page`; terminology now agrees with the resulting row via `describe_run_outcome()`. |
| V-10 History | Not touched | Contract §6 explicitly scopes History's contents as already-correct; no change proposed or made. |
| V-11 Needs attention | **Deliberately not touched** | §7's aggregation rule remains PO-pending; nothing here converts the candidate set into a final rule. |
| V-12 Status-domain separation | Not touched | No new status domain introduced by this increment. |
| A-01 Keyboard-only workflow | Partially | Individual controls verified keyboard-operable/discoverable (native `<button>`/`<a>`/`<form>`, no custom widgets); a full end-to-end keyboard walkthrough was not performed (no browser session available this session). |
| A-02 Discover unavailable-Run reason without mouse | Yes | Tested directly (static text now present regardless of hover). |
| A-03 Accessible names identify the Series | Yes | Tested directly. |
| A-04 Outcome feedback via programmatic mechanism | Yes, markup-level | `role`/`aria-live` added and present in rendered HTML (tested); not verified against a real screen reader. |
| A-05 State without relying on color | Not touched | Pre-existing icon+text badges already satisfied this before the pilot. |
| A-06 Predictable focus after filtering/Run/job-page return | **Not implemented** | This is a traditional multi-page Flask app (no SPA) — every transition here is a full page navigation, which is the standard, generally-accepted way this concern is satisfied by default (focus resets to the top of a newly-loaded document). No explicit focus-management code (e.g. `autofocus`, scripted `.focus()`) was added or verified. Flagged as unaddressed, not silently assumed adequate. |

---

## 5. Not implemented / explicitly deferred

- A-01 (full keyboard walkthrough) and A-06 (focus-predictability verification): markup supports
  them by construction (native elements, full-page navigation) but neither was walked through
  end to end in a real browser this session.
- Screen-reader validation (§10's own stated boundary): not performed, not claimed.
- Bulk "Run Scheduled Imports" messaging: still raw-enum, a scoping decision stated in §2, not
  a gap in the per-Series contract.
- Meta-refresh polling transport: unchanged, only its announcement semantics were added.

---

## 6. Escalations

**None required.** No previously-unresolved financial/domain semantic was exposed by this
implementation pass — every acquisition-state label and piece of terminology added
(`describe_run_outcome()`'s messages, the `aria-label`s) uses the exact acquisition-qualified
vocabulary contract §9 already specifies, and none of it touches `Needs attention`,
`USER_DISABLED` behavior, or concurrent-Run semantics.

---

## 7. Definition-of-done checklist (contract §14), current status

| Item | Status |
|---|---|
| All required user-visible states represented | Unchanged, already true pre-pilot |
| Provider assignment visibly distinct from acquisition state | Unchanged, already true (ticker column vs. Result column) |
| Run behavior matches the verified contract, deviations routed | Matches; no deviation proposed |
| Background execution and fresh post-run state observable | Confirmed by reading `job_status_page`'s redirect flow |
| History exposes the specified information | Unchanged, already true |
| Terminology does not conflate acquisition with financial validity | `describe_run_outcome()` uses only acquisition-qualified language |
| Disabled Run explanation keyboard accessible | **Done, tested** |
| Run/History accessible names identify the Series | **Done, tested** |
| Dynamic outcome feedback addressed or documented | **Addressed** (live-region markup); screen-reader confirmation explicitly not claimed |
| User-visible validation scenarios executable | V-01 through V-09 directly exercised by new/updated tests; V-06/V-08/V-10/V-11/V-12 unaffected/pre-existing, not re-verified here |
| No unresolved domain question silently converted into UI meaning | Confirmed — `Needs attention`, `USER_DISABLED`, concurrent-Run semantics all left exactly as contracted |

**Ready for UI/UE validation**, with the explicit caveats in §5 carried forward, not hidden.
