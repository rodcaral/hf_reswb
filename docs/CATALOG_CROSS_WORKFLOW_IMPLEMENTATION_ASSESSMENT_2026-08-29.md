# Catalog Cross-Workflow — UX Implementation Assessment

**From:** SDT-WB
**Date:** 2026-08-29
**Against:** `041_Catalog_Workflow_Cross_Screen_UX_Specification.md` (`histfints_uiue`, commit
`d68f47c`, committed) and its predecessor `040_Catalog_Workflow_Cross_Screen_UX_Assessment.md`
**Status:** Read-only technical assessment. No code, template, or route was modified to produce
this document. No automatic resolution, scoring, or certainty signal is proposed or implied. All
findings below verified directly against `histfints` source at read time (commit `1ea33f2`,
committed — the Catalog Resolve implementation this workstream builds on has already landed,
`82f999d`), not taken from `040`/`041`'s own descriptions alone where independently checkable.

---

## 1. AC-XWF-01 through AC-XWF-15 — classification

| AC | Requirement | Classification | Basis |
|---|---|---|---|
| AC-XWF-01 | Nav Search link reads "Catalog: Search" | **Presentation/template change** | `base.html:16` confirmed: `<a href="...">Search</a>` — a one-line label edit, no route/URL change |
| AC-XWF-02 | Each unresolved Discover-side candidate gets its own clickable, candidate/subject-anchored Resolve link | **Presentation/read-model change** | `_relationship_state_suffix()` (`web.py:170-196`) already enumerates each unresolved candidate individually (`"; ".join(...)"`) — the per-candidate loop already exists; each iteration needs a link, not a new enumeration mechanism |
| AC-XWF-03 | Link reads as navigation, not disposition | **Presentation/template change** | A wording/accessible-name requirement on the same new links — no separate mechanism |
| AC-XWF-04 | Clicking the link doesn't change resolution state | **Already satisfied by construction** | The link is a plain `<a href>` GET navigation to `catalog_resolve_page` — no POST, no service call. Verifiable by construction the same way AC-RES-05/21 were: no code path exists for a GET request to reach any `resolve_*()`/`reverse_*()` method |
| AC-XWF-05 | Tracked result with unresolved Series-subject candidate shows both actions | **Presentation/read-model change** | `catalog_search.html`'s `is_tracked`/`provider_symbol_id` branching (lines 51-72, confirmed) has no third condition today; needs a new "has unresolved Series-subject candidate(s)" check, answerable from already-fetched data (§2.1 below) — no new repository method required |
| AC-XWF-06 | Tracked result with no unresolved candidate is unchanged | **Already satisfied** | Structurally the default/else branch of AC-XWF-05's new condition — nothing to build separately |
| AC-XWF-07 | The two actions are separate, independently labeled controls | **Presentation/template change** | Two sibling elements, not a combined control — a template-structure choice, not a new mechanism |
| AC-XWF-08 | Resolved ProviderSymbol echo gets a real, clickable Undo/Revert control | **Requires a new mechanism (bounded)** | See §2.2 — reuses `_undo_control()`'s existing `Markup`-return pattern, but requires restructuring `_relationship_state_suffix()` and its three call sites' flash construction from a bare f-string to Markup-safe composition |
| AC-XWF-09 | Control remains locatable after reload, from any of the three call-site pages | **Already satisfied by the chosen mechanism** | All three call sites (Create/Verify ProviderSymbol, Verify Scheduled) already independently re-derive `describe_relationship_state()` fresh on each request — re-visiting any of them (or re-submitting Verify, which is idempotent) reproduces the control; no new persistence needed |
| AC-XWF-10 | Reversal doesn't delete the underlying candidate/tier/rule (DFA-X04) | **Already satisfied** | Reuses `reverse_attach_route`/`reverse_group_route` (unchanged) — confirmed both call only `candidate.clear_resolution()` + a Series-side field clear, never `_match_candidate_repo` delete; same guarantee already established for Series-side Undo |
| AC-XWF-11 | Provenance echo states actual disposition + Candidate id | **Already satisfied (data); presentation rewrite bundled with AC-XWF-08** | `_relationship_state_suffix()`'s resolved branch (`web.py:180-185`) already includes `state.resolved_candidate.id` and `.resolution_operation.value` in its current text — the *data* requirement is met today. The exact wording needs a small rewrite anyway as part of AC-XWF-08 (separating the provenance clause from the plain-text "reversible via..." sentence that AC-XWF-08 replaces with a real control) |
| AC-XWF-12 | No wording/icon implies correctness beyond the factual record (DFA-X03) | **Presentation/template change** | A wording-review requirement on the same rewrite — no separate mechanism |
| AC-XWF-13 | No candidate auto-resolved/dismissed as a side effect of any new link/control (DFA-X01) | **Already satisfied by construction, verify by non-mutation** | Every new element in this assessment (§2) is either a GET link or a reuse of the existing, unchanged `reverse_*` routes — no new write path is introduced anywhere |
| AC-XWF-14 | No confidence/score/ranking signal introduced (DFA-X05) | **Already satisfied by construction** | Nothing proposed in §2 touches `evidence_tier` presentation or introduces a new field; verifiable by diff review (no new numeric/percentage field anywhere in the proposed changes) |
| AC-XWF-15 | Every new link/control is keyboard-operable with a distinct, candidate-specific accessible name | **Presentation/template change** | Same `aria-label`/accessible-name pattern already used throughout this app (`015`/`021`/`035`'s own established convention) — applied to the new elements, not a new pattern |

**Summary counts:** 6 already satisfied (2 by construction/verification only, no code); 7
presentation/template or presentation-read-model changes; 1 requiring a new (but bounded, reusing
an existing pattern) mechanism (AC-XWF-08, which AC-XWF-11/12 ride along with); 0 blocked by
missing information. **Zero genuine DFA/PO blockers** — independently re-checked, not merely
repeated from `041` §9: every one of the five settled changes (§3 below) has either already-
available data or an already-established implementation pattern to extend; nothing surfaced a new
domain/product question this pass.

---

## 2. The five settled changes — smallest implementation boundary

### 2.1 PO-XW01 — Nav rename

`base.html:16`: `Search` → `Catalog: Search`. No route, no URL, no other file.

### 2.2 PO-XW02 — Discover → Resolve candidate-specific links

`_relationship_state_suffix()`'s unresolved-candidate branch (`web.py:190-195`) already loops
over `state.unresolved_candidates`; extend each iteration to also emit a link (see §3's shared
helper) alongside the existing `"Series #{id} (tier {tier})"` text — `url_for('catalog_resolve_page',
subject_series_id=<the ProviderSymbol's own id, filtered via the existing provider_symbol_id
param>)` — i.e. **no new filter param needed for this direction**: the existing
`?provider_symbol_id=` filter already scopes correctly, since every candidate in this branch
shares the same `provider_symbol_id` (the subject). The link only needs to reuse the existing
filter, not add one.

### 2.3 PO-XW03 — Search dual-action

**New read-model step in `catalog_search_page`** (or wherever results are assembled): call
`context.catalog_resolution_service.list_unresolved_candidates()` once for the page (not
per-row), build `dict[int, list[MatchCandidate]]` keyed by `subject_series_id` (mirroring exactly
the `SubjectKey`-style grouping `catalog_resolve_page()` itself already does — same pattern,
smaller: only the Series-subject half is needed here), and pass it to the template. **No new
repository method required** — `MatchCandidateRepository.list_unresolved()` already exists and
is unscoped; a per-page grouping in Python is the same "smallest addition to an existing surface"
discipline this whole workstream family has used throughout (`026`/`029`/`035` §13.2).

**New filter param on `catalog_resolve_page`**: `?subject_series_id=` — symmetric to the existing
`?provider_symbol_id=` filter (`web.py:1400-1409`), same shape, same code pattern
(`[c for c in candidates if c.subject_series_id == focus_series_id_int]`).

`catalog_search.html`: add the new "Review in Resolve" link as a sibling to "Open Series" when the
per-row lookup finds unresolved candidates for that `series_id`.

### 2.4 PO-XW04 — Real ProviderSymbol-side Undo/Revert

**The materially larger of the five, but still bounded to existing patterns.** `_undo_control()`
(`web.py:1358-1377`) already exists, already returns `Markup`, already reuses the unchanged
`reverse_attach_route`/`reverse_group_route`. The gap is structural, not conceptual:
`_relationship_state_suffix()` currently returns a plain `str`, and all three call sites
(`web.py:1051-1053`, `1144-1149`, `1195-1200`) build their flash message via bare f-string
concatenation of that `str` with other plain-text segments (`ProviderSymbol id`, `raw_ticker`,
`verification_status`, lifecycle suffix). **Required change**: `_relationship_state_suffix()`
gains a resolved-branch path that returns `Markup` (composing `_undo_control()`'s output the same
way the Resolve-confirmation flashes already do — `Markup(f"...") + undo`), and each of the three
call sites' flash-message construction is restructured to build via `Markup`-safe composition
(explicitly `escape()`-ing each dynamic plain-text segment, exactly as `_undo_control()`'s own
docstring already requires of itself) rather than a bare f-string. **This is presentation/service
work reusing an established, already-proven technique — not a new page, and not "no HTML-safe
rendering path exists"; that finding (`029`/`036`) predates the Resolve implementation, which
already solved this exact problem for its own confirmation flashes.**

### 2.5 PO-XW05 — ATTACH/GROUP provenance wording

Rides along with §2.4's rewrite: the resolved-branch text becomes (roughly) `f"— linked to
tracked Series: {label} (Series #{id}) — resolved relationship (MatchCandidate {id}, resolution
{op})"` followed by the real Undo control (§2.4), replacing the current combined "resolved
relationship (MatchCandidate {id}, resolution {op} — reversible via Reverse Candidate on Catalog:
Resolve)" sentence. No new data — `state.resolved_candidate.id`/`.resolution_operation` are
already present in `ProviderSymbolRelationshipState` (confirmed, `catalog_resolution_service.py:435-437`
area).

---

## 3. §8 — SE/SDT implementation-assessment questions, answered

### §8.1 — Multi-candidate link behavior for Search's dual-action (PO-XW03)

**Recommend reusing the subject-filter mechanism (one link showing all), not one link per
candidate.** Consistent with how the ProviderSymbol side already works (`?provider_symbol_id=`
filters to all of that subject's candidates at once, not one URL per candidate) and with §2.2's
finding that Discover's own new links also reuse the subject filter rather than a
per-candidate-id filter. A single "Review in Resolve" link per Search result, filtered by the new
`?subject_series_id=` param, is simpler, requires no per-candidate link enumeration in
`catalog_search.html`, and matches `041` §5's own "reused... consistent with how the
ProviderSymbol-side filter already works" phrasing exactly.

### §8.2 — Does the Undo/Revert control fit the existing flash mechanism, or does it need to move?

**Fits, verified by direct inspection of `_undo_control()`'s own established pattern — does not
need to move to a different page surface.** See §2.4. The original `029`/`036` finding that
"Discover's flash mechanism has no HTML-safe rendering path" predates the Resolve
confirmation-flash work, which already built exactly this capability (`Markup`-returning helper,
`escape()`-composed surrounding text) for its own three success-flash sites. Reusing the identical
technique for `_relationship_state_suffix()`'s three call sites is the smallest implementation —
moving the ProviderSymbol echo to a new page (mirroring `series.html`'s approach) would be a
materially larger change than necessary, and nothing in `040`/`041` requires it once the flash
mechanism is confirmed capable.

### §8.3 — Does existing data already support §7's provenance text without new read-model work?

**Yes, confirmed directly, not assumed.** `ProviderSymbolRelationshipState.resolved_candidate`
already carries `.id` and `.resolution_operation` (`catalog_resolution_service.py`,
`describe_relationship_state()`) and `_relationship_state_suffix()`'s current text already
consumes both (`web.py:180-185`). No new field, no new query.

### §8.4 — Can Discover's and Search's candidate-specific Resolve links share one helper?

**Yes.** Both ultimately need the same thing: given a subject (a ProviderSymbol id or a Series
id), produce `url_for('catalog_resolve_page', provider_symbol_id=X)` or
`url_for('catalog_resolve_page', subject_series_id=Y)` depending on subject kind — exactly the
`SubjectKey`-shaped distinction `catalog_resolve_page()` itself already makes internally.
**Recommend a small helper** (e.g. `_resolve_link_for_subject(subject_key) -> str`, taking the
same `SubjectKey` type `web.py` already defines) usable from both `_relationship_state_suffix()`
(Discover-side) and `catalog_search_page`'s template context (Search-side) — avoiding duplicated
URL-construction logic in two places, per `041` §8.4's own framing.

---

## 4. Tests required

- **AC-XWF-01**: template/nav-text assertion (existing pattern, e.g. a page-text extraction check).
- **AC-XWF-02/03/04**: per-candidate link presence and href correctness in the unresolved-candidate
  flash; a structural test confirming the link is a GET anchor, never a form/POST (mirrors the
  existing "no tier-conditional branch" structural-test discipline this whole session's work has
  used repeatedly).
- **AC-XWF-05/06/07**: `catalog_search_page` tests for a tracked result with/without an unresolved
  Series-subject candidate — both actions present in one case, only "Open Series" in the other,
  each a separate labeled element.
- **AC-XWF-08/09**: flash-content tests confirming the resolved-ProviderSymbol echo contains a real
  `<form>`/Undo control (not the old plain-text sentence), re-derivable by re-visiting/re-verifying
  from all three call sites.
- **AC-XWF-10**: reuse/extend the existing `reverse_attach`/`reverse_group` tests confirming
  candidate/tier/rule survive reversal — already covered by existing Resolve tests, re-run as
  regression, not new logic to test.
- **AC-XWF-11/12**: flash-text assertions for exact disposition+id wording; a wording-review check
  (no "verified"/checkmark/percentage language) — text-content assertions, no new mechanism.
- **AC-XWF-13/14**: structural tests — no new code path reaches any `resolve_*`/`reverse_*` method
  from a GET request; no new numeric/score field introduced anywhere in the diff (a grep-based or
  AST-based structural test, matching this session's own established `acquisition_evidence_integration.py`-style
  discipline for exactly this kind of guarantee).
- **AC-XWF-15**: accessible-name assertions for every new link/control, each distinct and
  candidate/subject-specific — matching the existing `element.closest/aria-label` verification
  pattern already used for `032`/`038`.
- **Regression**: full `histfints` suite re-run before and after — the established practice this
  whole workstream family has followed at every implementation step.

---

## 5. Genuine DFA/PO blockers

**None identified.** Independently re-checked against `041` §2/§3, not merely repeated from its
own §9 claim: every one of DFA-X01–X05's constraints is satisfiable by the read-only/reuse-only
mechanisms in §2 (no new write path, no scoring, no automatic resolution anywhere in this
assessment's proposed boundary), and every one of PO-XW01–XW05's five decisions maps to an
already-available data shape or an already-established implementation pattern (§2, §3). If SDT-HF's
actual implementation surfaces a genuinely new question not covered by `041` §2/§3, it should route
back to DFA/PO per the standing rule — not inferred here.

---

## 6. Required HistFinTS-side changes — identified, not written

All changes named in §2 are in `histfints`, none in `workbench` or any other sibling repository.
Per the standing sibling-repository rule, this assessment identifies them for SDT-HF's own
implementation; SDT-WB has not written to `histfints` to produce this document.

| File | Change |
|---|---|
| `src/histfints/presentation/templates/base.html` | Nav label (§2.1) |
| `src/histfints/presentation/web.py` | `_relationship_state_suffix()` gains links (§2.2) and `Markup`-safe Undo composition (§2.4); `catalog_resolve_page()` gains `?subject_series_id=` filter (§2.3); `catalog_search_page` gains the per-page unresolved-candidates grouping (§2.3); new shared `_resolve_link_for_subject()` helper (§3.4) |
| `src/histfints/presentation/templates/catalog_search.html` | Dual-action rendering (§2.3) |
| `src/histfints/application/catalog_resolution_service.py` | No change identified — `describe_relationship_state()`'s existing return shape already suffices (§3.3) |
| `src/histfints/domain/repositories.py` | No new abstract method identified — `list_unresolved()` already sufficient (§2.3) |
| Tests | New/extended tests per §4, across `test_web_catalog.py` and `test_catalog_search.py`-equivalent files |

---

## What this assessment does not do

- Does not implement anything — no route, template, service method, or Help entry was changed.
- Does not introduce any automatic resolution, scoring, ranking, or certainty signal.
- Does not reopen or revise `030`/`031`/`033`/`039`'s own findings.
- Does not change which operations are valid for which subject kind.
- Does not modify `workbench` or any sibling repository.

## Gate

Per `041`'s expected transition — `041 specification → SE/SDT implementation assessment →
implementation → UI/UE validation` — this document is the assessment half. Hand-off: to SDT-HF
for implementation in `histfints`, per the standing sibling-repository rule (SDT-WB does not
implement). SDT-WB will perform a read-only conformance review against AC-XWF-01–15 and this
assessment after SDT-HF implements, matching the precedent set for INC-13.
