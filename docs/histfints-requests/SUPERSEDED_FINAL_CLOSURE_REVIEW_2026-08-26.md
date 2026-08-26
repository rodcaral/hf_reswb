# `SUPERSEDED` — Final Read-Only Closure Review

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: read-only review only. No file modified in either repository. HistFinTS's "10 new
tests, 1328 passing" claim independently re-run and confirmed, not accepted on assertion.**

---

## Verdict: **NOT YET FULL PASS — one concrete residual divergence found**

Everything SE asked to verify passes except one item under check 2 (default exclusion vs.
explicit historical access convergence): Import & Status's own pagination controls silently
drop the `include_superseded` toggle, unlike every other surface. Detailed below, item by item.

---

## 1. Approved meaning implemented consistently — **PASS**

Both repos cite the identical DFA-approved definition. HistFinTS's help text
(`help_content.py:106-113`, key `series_status_superseded`) now reads, verbatim: *"Superseded —
retained for historical/provenance purposes; no longer the current attribution."* — not merely
equivalent to the approved wording, textually identical to it.

## 2. Default exclusion and explicit historical access converge — **PASS with one exception**

**Series page** (`web.py:540-571`): default excludes `SUPERSEDED`;
`?include_superseded=1` reveals it; the direct `?id=` hand-off takes precedence over *both* `q`
and the exclusion (confirmed by reading the route — `focus_id` branch runs before the
`else:` branch containing the exclusion), so discoverability is intact. Pagination
(`_pagination.html:18,21`) correctly threads `include_superseded` through Prev/Next.

**Import & Status** (`import_status_view.py:73-99`, `web.py:836-837,893`): default excludes
`SUPERSEDED` from both the row list and the summary counts; `?include_superseded=1` reveals it,
via its own toggle link (`import_status.html:97-101`).

**The exception**: Import & Status's *own* pagination macro (`import_status.html:112-118`,
the `pager()`/`plink()` used for First/Prev/page-numbers/Next/Last — a different, separately
maintained component from `_pagination.html`) builds its links as `url_for('import_status_page',
page=n, q=q, sort=sort, per_page=pagination.per_page, **selected)`. **`include_superseded` is
not in this argument list, and not in `selected`** (`selected={"state":..., "type":...,
"provider":..., "interval":...}`, `web.py:889-890` — no `include_superseded` key).

**Traced the concrete failure mode, not just the missing parameter**: `_IMPORT_VIEW_KEYS`
(`web.py:85-86`) does include `"include_superseded"`, and the route does try to remember view
state across navigations that omit all tracked keys — but a pager-generated URL *does* carry
several other tracked keys (`q`, `sort`, `per_page`, `page`), so the route's `if any(key in
request.args...)` branch fires and **overwrites** the session's remembered view with only what's
actually present in that URL — which excludes `include_superseded`. The visible result: a user
who toggles "Show superseded" and then clicks Next/Previous/a page number/First/Last on Import &
Status silently lands back on the default (excluded) view, on that same click, with no
indication anything changed.

This does not happen on the Series page (its simpler `_pagination.html`-based pager explicitly
threads the parameter). It is isolated to Import & Status's own pagination component.

## 3. Workbench analysis opt-in produces the required historical-evidence qualification — **PASS**

Unchanged since the 2026-08-26 Workbench implementation; re-confirmed by re-running
`tests/test_panel_eligibility_superseded.py` — 5/5 passing, including the two tests asserting
`historical_evidence_qualification` is set (containing both approved-sentence fragments and the
specific Series id) when opted in, and `None` when not.

## 4. HistFinTS help text semantically equivalent to the approved wording — **PASS, exceeds the bar**

As noted in §1, the `short` field is not merely a compact paraphrase that preserves meaning —
it is the approved sentence verbatim. The `format` field adds the negative-scope clarifications
(does not mean delisted/invalid/ceased-to-exist/should-be-deleted) drawn directly from
`SeriesStatus.SUPERSEDED`'s own docstring, not an invented addition.

## 5. Acquisition-quality exclusion and `class_e_identity_signal` remain as approved — **PASS**

Re-ran both test files: `tests/test_acquisition_quality_capability.py`'s
`TestSupersededExclusionFromNeedsAttention` (6/6 passing) and
`tests/test_class_e_identity_signal.py`'s `TestSupersededNonRegression` (3/3 passing,
confirming no `status` field on the snapshot type and an unchanged function signature).
`git status` on `class_e_identity_signal.py` shows no uncommitted changes — untouched since the
prior commit.

## 6. No residual divergence from approved product/domain behavior — **one found, above (§2)**

Backend write-guard enforcement (`Series.is_current_attribution`,
`enable_series()`/`add_provider_assignment()` rejection, `reactivate_series()`) confirmed
unchanged — same three call sites, same logic, as in the prior integration review. No reusable
application mechanism for *setting* `SUPERSEDED` was added — confirmed still absent by the same
exhaustive grep as before, and **kept out of this closure verdict**, per instruction, as a
separately tracked item.

---

## Independent verification performed (not accepted on assertion)

- Ran `histfints-v3`'s full suite directly: **1328 passed, 92 deselected** — matches SE's
  reported figure exactly.
- Ran Workbench's full suite: **167 passed, 1 skipped, 1 pre-existing unrelated failure**
  (series 11312's `configured_interval` — the same standing, unrelated failure noted in every
  prior test run this session), zero regressions.
- Read every code path named in this review directly; none of the findings above are restated
  from a prior document without re-checking the current source.

---

## What would make this a clean PASS

Threading `include_superseded` (and, while touching that macro, the pre-existing `technical`
omission — a separate, not-SUPERSEDED-related gap noticed in passing, not this review's
subject) through `import_status.html`'s `pager()`/`plink()` macro, the same way
`_pagination.html` already does for the Series page. A one-parameter addition to one macro's
`url_for()` call, not a design change — no new decision required.

**No file was modified in producing this review.**
