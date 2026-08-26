# `SUPERSEDED` — Read-Only UI/Consumer Assessment

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: read-only assessment only. No code or production change. 11345/11346 used as concrete,
already-established test cases — their financial disposition is not reopened or re-evaluated
here; only how the *interface layer* currently presents/consumes their `SUPERSEDED` status.**

Format per surface: **current user-visible behavior → ambiguity/risk → evidence/code path.**
Every row below was verified against the current source and, where noted, the live database —
not assumed from a prior turn's memory.

---

## 0. Ground truth used throughout

Re-verified directly: `series` rows 11345/11346 currently have `status='SUPERSEDED'` and
`archived_at IS NULL` (both). This single fact — **`SUPERSEDED` is not `archived`** — turns out
to be the load-bearing detail behind nearly every finding below.

---

## 1. Workbench (`workbench` repo)

**Workbench has no UI of its own** — confirmed by a full search of `src/`: zero presentation/
template files exist. Every "surface" here is a library function, invoked programmatically
(scripts, this session's own ad-hoc queries), not a page a person browses.

| Surface | Current behavior | Ambiguity/risk | Evidence |
|---|---|---|---|
| Panel eligibility (`compute_panel_eligibility()`) | Given a caller-supplied `series_ids` list, explicitly excludes only `status = 'DELISTED_OR_DISCONTINUED'`. **No check for `SUPERSEDED` exists anywhere in this function.** | If a caller passes a `SUPERSEDED` series id into a panel, nothing in this function flags, excludes, or even logs it — it would be silently treated identically to an `ACTIVE` series for eligibility purposes. | `src/hf_reswb/application/panel_eligibility_service.py:99-118` — the only `status`-aware branch in the file. |
| Series selection/search | No entry point exists — no function anywhere in Workbench queries `series` for a general browsable list. | N/A — there is nothing to assess because the surface doesn't exist. | Confirmed by search: no `SELECT ... FROM series` outside the one DELISTED check above. |
| Charts/history, comparison/panel picker, exports | Not implemented as UI in Workbench at all — these exist only as domain/application-layer building blocks (e.g. `evaluate_fallback_activation`, `class_e_identity_signal`), never as something a person clicks through. | Not applicable to *current* behavior; worth naming as a gap if any future Workbench UI is built without SUPERSEDED-awareness baked in from the start. | Confirmed by search across `src/`. |

---

## 2. HistFinTS web UI (`histfints-v3`)

`SeriesStatus.SUPERSEDED` (with the DFA-approved general definition, `series.py:23-55`) is fully
defined in the domain layer. What varies sharply is whether each *consuming* surface actually
reads and displays it.

### 2.1 The root cause behind most findings below: `list_active()` doesn't filter by status

`SqliteSeriesRepository.list_active()` filters **only** on `WHERE s.archived_at IS NULL`
(`sqlite_series_repository.py:43-49`) — **it does not check `status` at all**, despite its name.
Since `SUPERSEDED` series are archived-null by design (the whole point of the status is
"retained, not archived" — `series.py:30`), **every consumer that calls `list_active()` and
does not apply its own status filter downstream will include `SUPERSEDED` series.**

Two consumers apply their own downstream filter; two do not:

| Consumer | Downstream status filter? | Evidence |
|---|---|---|
| `run_scheduled_route()` (bulk scheduled import) | **Yes** — `if series.status != SeriesStatus.ACTIVE: continue` | `web.py:887` |
| `series_page()` (Series listing) | **No** | `web.py:539` |
| `ImportStatusView.list_status()` (Import & Status) | **No** — iterates `self._series_repo.list_active()` directly | `import_status_view.py:86` |

### 2.2 Surface-by-surface

| Surface | Current user-visible behavior | Ambiguity/risk | Evidence/code path |
|---|---|---|---|
| **Search/listing visibility** (`/series`, `series_page()`) | 11345/11346 **do appear** in the Series listing (confirmed: no status filter applied at this layer) — including under a plain-text search (`q` matches label) or a direct `?id=` lookup. | A user browsing or searching Series has no reason to expect a SUPERSEDED row to be hidden, and it isn't — but see the next row for whether it's at least *labelled* clearly once found. | `web.py:537-566`, confirmed no status exclusion in the route. |
| **Status labels** (on the same Series page) | Each row shows `Series status: {{ series_status_label(series.status.value) }}`, and specifically for `SUPERSEDED` an added caveat: `(meaning not yet established)`. **However**, `_SERIES_STATUS_LABEL` (the friendly-name dict) has **no entry for `SUPERSEDED`** — `ACTIVE`→"Active", `USER_DISABLED`→"Disabled (paused by user)", etc. all get friendly text, but `SUPERSEDED` falls through to the raw enum string `"SUPERSEDED"` verbatim. | Minor, but real: every other status gets a human-readable label; `SUPERSEDED` alone doesn't — the caveat sentence is bolted onto the template separately from the label dict, not integrated with it. | `web.py:115-134` (label dict + fallback), `series.html:27-28` (caveat markup). |
| **Charts/history access** | The per-Series History page (`/series/<id>/import-history`) shows only run-level data (Run ID, Trigger, Status, Started, Ended, Errors) — **no `Series.status` is shown on History at all**, for any status value, not just SUPERSEDED. | A user who lands on History for 11345/11346 (e.g. via the Series page's link, or directly) sees a plain run list with no indication the Series itself is SUPERSEDED — that context exists only on the page they came from. | `import_history.html` (full file reviewed — no status field present). |
| **Comparison/panel selection** | No such feature exists in `histfints-v3`'s own UI (no compare/chart route found). Workbench's `panel_eligibility_service` is the only place this concept exists, and (per §1) it does not check for `SUPERSEDED`. | If/when a comparison feature is built (in either repo), it would need to explicitly add SUPERSEDED-awareness — nothing today provides it by default. | Confirmed by search: no compare/chart route in `web.py`. |
| **Exports** | No export route exists in `histfints-v3` (only bulk CSV *import*, `parse_bulk_series_csv`, unrelated). Workbench has no export UI either. | Not currently assessable — the surface doesn't exist yet. | Confirmed by search across both repos. |
| **Acquisition/status views** (Import & Status) | **11345/11346 currently appear on Import & Status**, classified `NEVER` (zero provider assignment, zero import runs — both facts independently re-verifiable, not reopened here). The row shows ticker (`—`, no assignment), label, type, schedule, and the `○ Never imported` badge — **`Series.status` is never rendered anywhere on this page**, for any Series. | This is the sharpest ambiguity found: an operator scanning Import & Status for "what needs attention" sees 11345/11346 exactly as they would see a genuinely new, never-yet-acquired Series — nothing on this page distinguishes "we haven't gotten to this one yet" from "this one was deliberately retired and its data lives elsewhere now." The Series page next door *does* disclose SUPERSEDED; Import & Status does not, and it's the page framed around "what needs attention." | `import_status.html` (full file reviewed — no `series.status` field anywhere in the row markup); `import_status_view.py:86-109` (the read model itself carries no `SeriesStatus` field on `SeriesImportStatus` at all — it isn't merely unrendered, it isn't even fetched into the row object). |
| **Do consumers distinguish `SUPERSEDED` from `ACTIVE`?** | **Inconsistent across the app.** The Series page: yes, explicitly (status label + caveat). Catalog search results (when a result links to an existing Series): yes, shows the raw `series_status.value` (`catalog_search.html:63`) — no friendly wording, but visibly distinct. Import & Status: **no** — the distinction isn't even loaded into the view model, let alone rendered. Bulk scheduled import: **yes** — explicitly skips non-ACTIVE. Panel eligibility (Workbench): **no** — only checks for `DELISTED_OR_DISCONTINUED`. | The inconsistency itself is the finding: the same two Series (11345/11346) are labelled on one page and unlabelled on another, with no single place a user could go to reliably learn "is this SUPERSEDED" across every surface they might encounter it from. | Table above, consolidated. |

---

## 3. Consolidated risk summary (no product semantics proposed, per instruction)

The single mechanical root cause is `list_active()`'s name-vs-behavior mismatch
(`archived_at IS NULL`, not `status = 'ACTIVE'`), which two of four checked UI/service
consumers do not compensate for downstream. The consequence, concretely demonstrated by
11345/11346: a SUPERSEDED Series is fully visible and searchable on the Series page (where it
*is* labelled) and on Import & Status (where it is *not* labelled, and reads identically to a
genuinely unacquired Series) — while Workbench's only status-aware exclusion logic
(`panel_eligibility_service`) has no branch for this status at all.

**No proposal is made here for what the correct behavior should be** (hide it, label it
differently, exclude it from "needs attention," etc.) — per instruction, this assessment only
identifies where the current implementation does and does not distinguish the state.
