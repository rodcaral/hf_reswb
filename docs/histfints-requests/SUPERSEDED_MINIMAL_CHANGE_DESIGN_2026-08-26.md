# `SUPERSEDED` — Minimal UI/Consumer Change Design

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: read-only design only. No code or production data modified. This document proposes
changes; it implements none.**

**Baseline (approved, not reinterpreted)**: *"Superseded — retained for historical/provenance
purposes; no longer the current attribution."* No additional financial semantics are invented
anywhere below — every label/help text is either this sentence verbatim or a compact paraphrase
of it, never a new claim.

**Governing distinction throughout**: **visibility** (can a person find/see the record) and
**analysis eligibility** (does it participate in panels/metrics by default) are different
questions with different defaults. Visibility should stay open (discoverable); eligibility
should default closed (excluded, opt-in).

---

## 1. Impact matrix

| Surface | Current behavior (from the prior assessment) | Visibility target | Eligibility target |
|---|---|---|---|
| Series/search presentation (`series_page`) | Shown in default list, unfiltered; direct `?id=` lookup works; status labelled with an ad-hoc caveat, no dict entry | **Stays visible** via direct lookup and an explicit "include superseded" toggle; **excluded from the default list** | N/A — pure presentation surface |
| Import & Status | Shown as ordinary `NEVER`, status not even fetched into the row model | **Excluded by default** — this is an operational acquisition-monitoring view, not the discoverability surface; there is nothing to acquire for a Series that is no longer the current attribution | Not applicable to this surface at all — it's already an eligibility-adjacent view (what needs *acquisition* attention), and SUPERSEDED belongs outside that population entirely |
| Panel/analysis eligibility (`compute_panel_eligibility`) | No check exists — SUPERSEDED passes through untouched | N/A — not a discoverability surface | **Excluded by default**, opt-in only, mirroring the existing `include_delisted` pattern |
| Selectors/candidate lists (any future picker for building an analysis) | Don't exist yet (confirmed by search) | Same principle as the Series page: visible in an explicit "show historical" mode, excluded from the default pick list | Excluded from anything that would auto-populate a panel |
| Acquisition-quality capability (`acquisition_quality_capability.py`) | `classify_never_state()` has no SUPERSEDED-aware branch; a SUPERSEDED Series with no assignment would be classified `NO_PROVIDER_ASSIGNMENT`, identical to a genuine gap | N/A | **Excluded from "needs attention"-style aggregate counts** via a new, explicit reason — not the heuristic fixture-candidate path, since `Series.status` is an authoritative fact, not a guess |
| `class_e_identity_signal.py` | No `status` field consumed anywhere | No change needed — this module reasons over provider/label evidence, not lifecycle status | No change needed |
| History page | No `Series.status` shown for any status, not just SUPERSEDED | Out of scope for this pass — not status-specific behavior; flag only if SE wants status added there too | N/A |

---

## 2. Minimal proposed UI/consumer boundary

Stated as the **smallest** change per surface — not a redesign.

### 2.1 Series/search presentation
- Add one filter clause to `series_page()`'s default query path: exclude
  `status == SUPERSEDED` unless an explicit query parameter (e.g. `?include_superseded=1`) is
  present — same pattern already used for `technical=1` on Import & Status, so no new UX idiom
  is introduced.
- The existing direct `?id=` hand-off path is **left untouched** — it already bypasses the `q`
  filter today (per its own comment, "takes precedence... rather than combining"), and must
  continue to return a SUPERSEDED Series when looked up directly. This is the concrete
  mechanism that keeps the record discoverable without adding a new one.
- Add `"SUPERSEDED": "Superseded"` to `_SERIES_STATUS_LABEL` (the one missing entry found in the
  prior assessment) — a **compact label**, consistent with every other status.
- Move the explanatory sentence (the approved baseline, verbatim) out of the ad-hoc inline
  caveat and into the existing `field_help`/`field_help_floating` macro system already used for
  column headers — reuses an established pattern rather than inventing a new one, and is where
  **explanatory help** belongs per the instruction's own visibility/help distinction.

### 2.2 Import & Status
- Smallest correct fix: filter `SUPERSEDED` out of `ImportStatusView.list_status()`'s source
  rows (or add the same downstream check `run_scheduled_route()` already uses) — one
  status-comparison, not a new query shape.
- No compact label is needed on this surface if the row is excluded entirely — nothing to
  render.

### 2.3 Panel/analysis eligibility
- Add one branch to `compute_panel_eligibility()`, structurally identical to the existing
  `DELISTED_OR_DISCONTINUED` block: default-exclude `status == SUPERSEDED`, controlled by a new
  `include_superseded: bool = False` parameter (mirrors `include_delisted` exactly — no new
  parameter shape invented). Exclusion reason/detail follows the same `ExclusionRecord` pattern
  already in place (`ExclusionReason.<new member>`, `detail="status = SUPERSEDED"`).

### 2.4 Selectors/candidate lists
- No code exists to change today. Forward-looking requirement only: any future picker must
  default-exclude SUPERSEDED and offer the same "include historical" opt-in used on the Series
  page — stated as a requirement for whoever builds it, not a change to make now.

### 2.5 Acquisition-quality capability
- Add one new `NeverStateReason`-equivalent value (or a sibling classification path) —
  `SUPERSEDED` treated as its own, non-heuristic exclusion reason, distinct from
  `NON_PRODUCTION_FIXTURE_CANDIDATE` (which requires human confirmation) since `Series.status`
  is already an authoritative fact requiring no confirmation step. Always excluded from
  "needs attention"-style aggregate counts, the same way a `CONFIRMED_FIXTURE` already is.

---

## 3. Tests required (design only — not written)

- **Series page**: default list excludes a SUPERSEDED fixture; `?id=<superseded>` still returns
  it; `?include_superseded=1` includes it in the list; the compact label renders `"Superseded"`,
  not the raw enum string; the help text matches the approved sentence exactly.
- **Import & Status**: a SUPERSEDED fixture is absent from both the row list and the summary
  counts (`needs_attention`, `by_state`).
- **Panel eligibility**: SUPERSEDED excluded by default with the correct `ExclusionRecord`
  reason/detail; included when `include_superseded=True`; a non-SUPERSEDED Series in the same
  call is unaffected (no cross-contamination).
- **Acquisition-quality capability**: a SUPERSEDED-status input is classified via the new
  reason, not folded into `NO_PROVIDER_ASSIGNMENT`/`ASSIGNED_NOT_YET_RUN`; confirmed excluded
  from any aggregate "needs attention" count built on top of it.
- **Regression fixtures**: 11345/11346 (real, already-established SUPERSEDED cases) used
  directly in at least the Series-page and panel-eligibility tests, so the test suite is
  grounded in the actual case that motivated this work, not only a synthetic one.
- **Negative check**: confirm `class_e_identity_signal.py` requires no change (assert it has no
  `status`-typed parameter anywhere, protecting against silent scope creep into that module).

---

## 4. Product ambiguity — genuine open choices not derivable from the ruling

The DFA ruling defines the *meaning* of the status; it does not, and isn't expected to, decide
UI/product placement questions. These four need SE/PO, not another DFA round, since none of
them is a financial-semantics question:

1. **Does SUPERSEDED belong on Import & Status at all, even filtered/badged, for audit-trail
   visibility of "this used to need attention and no longer does"?** This design proposes full
   exclusion (§2.2) as the minimal, natural read of "no longer the current attribution" — but
   that's a product judgment about where discoverability is satisfied (Series page vs. every
   surface), not something the ruling states directly.
2. **Exact compact-label wording** — "Superseded" alone, vs. something like "Superseded (see
   history)" inline in list views. Cosmetic, but user-facing text should get an explicit
   sign-off rather than being decided by this document.
3. **Whether opting a SUPERSEDED Series into an analysis (`include_superseded=True`) should
   surface a caveat in the analysis *output* itself**, not just at the selection step — the
   ruling's own point 5 (evidentiary sufficiency for the disposition) doesn't speak to whether
   downstream consumers of an opted-in analysis need their own visible flag. Genuinely open.
4. **Whether "include historical/superseded" should be one consistent, shared preference across
   surfaces, or independently toggled per page** — a UX-consistency question with no basis in
   the ruling either way.

Everything else in this design (the visibility/eligibility split, the exclusion mechanics, the
label/help placement) is a direct, mechanical consequence of the approved meaning and does not,
in this assessment's judgment, require a further DFA round.

---

## 5. What this document does not do

- Does not modify any file in `histfints-v3` or `workbench`.
- Does not implement any of the proposed changes, tests, or label text.
- Does not decide the four open product questions in §4 — named for SE/PO routing only.
