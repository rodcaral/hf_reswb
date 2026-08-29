# Catalog Resolve — UX Implementation Assessment

**From:** SDT-WB
**Date:** 2026-08-29
**Against:** `035_Catalog_Resolve_UX_Specification.md` (`histfints_uiue`, untracked/uncommitted at
read time — read directly, noted since it affects reproducibility until committed)
**Status:** Read-only technical assessment. No code, template, or route was modified to produce
this document. No automatic resolution, tier-based confirmation bypass, Discover/Resolve
boundary change, or subject-kind operation change is proposed or implied.

**Method:** direct source inspection of `web.py`'s four resolve routes and four reverse routes,
`catalog_resolution_service.py`'s eight resolution/reversal methods, `catalog_resolve.html`,
`help_content.py`'s `confirm_column`/`evidence_tier` entries, and `import_status.html` (for
existing confirmation-pattern precedent) — no code run, no database touched, no live server
started. Every claim below was checked against this source directly, including re-verifying (not
assuming) two of `034`'s own characterizations where the actual text told a more precise story
(§5, §6.4 below).

---

## 1. AC-RES-01 through AC-RES-22 — classification

| AC | Requirement | Classification | Basis |
|---|---|---|---|
| AC-RES-01 | ATTACH interposes confirmation | **New confirmation-flow mechanism** | `resolve_attach_route` (`web.py:1311`) calls `resolve_attach()` directly on POST — no intermediate state exists |
| AC-RES-02 | GROUP interposes confirmation | **New confirmation-flow mechanism** | `resolve_group_route` (`web.py:1329`) — same shape, plus new-Series attributes must also survive into the confirmation step |
| AC-RES-03 | SET_UNDERLYING interposes confirmation | **New confirmation-flow mechanism** | `resolve_set_underlying_route` (`web.py:1365`) — same shape |
| AC-RES-04 | MERGE interposes confirmation with full §9 disclosure | **New confirmation-flow mechanism** | `resolve_merge_route` (`web.py:1383`) — same shape, plus MERGE-specific consequence text is net-new content, not just a gate |
| AC-RES-05 | No tier-based bypass of confirmation | **New confirmation-flow mechanism (structural), verifiable by construction** | Satisfied automatically if the chosen mechanism (§2 below) has no tier-conditional branch — the same "no new field, no new condition" discipline `027` already used for Discover's auto-resolution removal |
| AC-RES-06 | Success feedback states reversibility | **Presentation/template change** | Extend the four success `flash()` strings (`web.py:1325,1358,1379,1404`) with a reversibility statement |
| AC-RES-07 | Success feedback provides a direct, candidate-scoped Undo/Revert control | **New confirmation-flow mechanism** (a real link/control, not bare text) | The four `reverse_*_route`s already exist and take exactly `candidate_id` (plus `series_id` for GROUP) — the control is new UI, not new reversal logic (§13.3) |
| AC-RES-08 | Undo/Revert remains locatable after reload | **Presentation/template change** | The existing candidate table already lists resolved-but-reversible candidates nowhere today — `list_unresolved_candidates()` only returns unresolved ones (see §6.2, a genuine open question) |
| AC-RES-09 | Competing candidates grouped and labeled | **Presentation/read-model change** | `catalog_resolve_page()` (`web.py:1267`) already builds `subject_labels`/`candidate_labels` from the flat `candidates` list in Python — grouping by `provider_symbol_id or subject_series_id` is an addition to that same loop, no new query (§13.2) |
| AC-RES-10 | Resolving one candidate in a group doesn't dismiss others | **Already satisfied** | Structurally true today: each `resolve_*()` call only mutates the one `MatchCandidate` it's given; nothing removes or alters sibling rows. Confirmed by reading all four `resolve_*` methods — none queries or touches any other candidate |
| AC-RES-11 | A single-candidate subject is not presented as ambiguous | **Presentation/read-model change** | A direct consequence of AC-RES-09's own grouping logic (group size 1 → no ambiguity banner) — no separate mechanism needed |
| AC-RES-12 | Evidence tier shown at row and confirmation-step level | **Presentation/template change** (row) + **New confirmation-flow mechanism** (confirmation step, since that step doesn't exist yet) | Row-level tier is already shown (`034` §2, confirmed); confirmation-step display is new by definition |
| AC-RES-13 | No tier presentation implies authorization | **Presentation/template change — and a real, newly-found gap** | `help_content.py`'s `confirm_column` entry currently reads *"Confirms the strongest candidate as fact"* (line 86) — this phrasing itself reads as tier-authorizes-confirmation, in direct tension with DFA-R01/AC-RES-13. **Not flagged in `034`** (which didn't quote this string) — found by this assessment's own direct source check. Must be reworded alongside the confirmation-step work, not left as-is |
| AC-RES-14 | Domain/business-rule errors lead with plain language | **Partially already satisfied — narrower gap than `034`'s framing suggests** | See §5 below: every current `ValueError` message already leads with a plain-language clause and already places the `BR-##` reference parenthetically, i.e. already secondary, not leading. What's actually missing against DFA-R02's stricter reading: (a) no explicit "reference:" label (a bare parenthetical isn't unambiguously *labeled* as a reference), and (b) one message (`BR-19`, shared-provider rejection) states *what* failed without *why* it's disallowed. Classified **presentation/template change** — a wording pass, not a restructuring |
| AC-RES-15 | Malformed-input errors unaffected | **Already satisfied** | Confirmed unchanged in every route above — `"Priority must be an integer"` etc. never carries a rule id and needs no rewording |
| AC-RES-16 | Placeholder-only inputs gain persistent labels | **Presentation/template change** | Same fix pattern `024`'s AC-DIS-18 already established and validated elsewhere in this app; `034` §7 already enumerated every affected input by name, not re-enumerated here |
| AC-RES-17 | Candidate/subject-specific accessible names on repeated actions | **Presentation/template change** | Same naming pattern already established for Series/Search (`015`/`021`) — applies to existing Confirm buttons and to every new confirmation-step/Undo control |
| AC-RES-18 | Confirmation step, feedback, grouping, errors all programmatically perceivable | **New confirmation-flow mechanism** (confirmation step) + **presentation/template change** (the rest) | Split because the confirmation step doesn't exist yet; the other three build on already-established, already-accessible mechanisms (flash `role="status"`, existing table semantics) |
| AC-RES-19 | Grouped ambiguity not color-only | **Presentation/template change** | A text heading/banner naming the shared subject satisfies this by construction — no color dependency needs to be introduced in the first place |
| AC-RES-20 | Mandatory real NVDA pass before runtime validation closes | **Blocked by missing information — not a code classification** | This is a validation-gate requirement, not an implementation task; it blocks *closure*, not implementation start. No code change makes this "satisfied" — it requires an actual NVDA session against the built confirmation/grouping/Undo mechanisms once they exist |
| AC-RES-21 | No disposition becomes automatic at any tier; confirmation never configurably removable | **New confirmation-flow mechanism (structural)** | Same discipline as AC-RES-05 — verifiable by construction: the chosen mechanism must have no configuration flag, environment variable, or tier branch capable of skipping it |
| AC-RES-22 | Discover unmodified; boundary unchanged | **Already satisfied — verify by non-touch, not by test** | Nothing in this specification's scope (§3) or this assessment's own proposed changes touches `catalog_discover.html`, `catalog_discovery_service.py`, or any Discover route. Verifiable the same way `029`/`032` verified it for Discover's own boundary: confirm the file list of an eventual implementation pass contains zero Discover files |

**Summary counts:** 1 already satisfied outright (AC-RES-10); 2 already satisfied with a caveat/no
further action needed (AC-RES-15, AC-RES-22 pending non-touch verification); 9
presentation/template changes; 8 requiring the new confirmation-flow mechanism (some jointly with
a presentation change); 1 blocked-by-missing-information (AC-RES-20, a validation gate, not a
code gap). Zero criteria are blocked by a missing domain/product decision — `035` §14's own claim
("§2's rulings settle every gate `034` raised") holds on this pass's own re-check; nothing here
surfaced a new domain/product question.

---

## 2. §13 — SE/SDT implementation-assessment questions, answered

### §13.1 — Confirmation-step mechanism

**A genuine two-step server-rendered mechanism, not a client-side `confirm()` gate.** A precedent
for a client-side gate already exists in this codebase —
`import_status.html:22`'s `onsubmit="return confirm('Run scheduled imports now?...')"` for the
scheduled-import action — but it is a single interpolated string in a native browser dialog, not
the multi-field structured content §5 requires (operation name; subject and candidate **by
label**; evidence tier and rule reference; MERGE's §9 consequence text). A browser `confirm()`
cannot render that shape, and `035` §11's own Validation section already treats Resolve's
confirmation step as a genuinely new pattern requiring a fresh NVDA pass — implicitly ruling out
"just reuse `confirm()`" as satisfying the reuse-of-already-validated-mechanism exception Discover
used. **Recommend**: each of the four POST routes gains a required intermediate GET/POST pair —
POST from the row/standalone form to a new `/catalog/resolve/{op}/confirm` action that
re-validates the same inputs and renders a confirmation template (reusing the existing
`candidate_id`/operation-specific fields as hidden inputs for the second, real POST) rather than
executing immediately. This is a two-step POST/confirm pattern, not a new intermediate *page*
requiring its own navigation — closer in shape to a same-page state change than a route change,
kept deliberately unspecified beyond this at the assessment stage per `035` §5's own "does not
mandate a mechanism."

### §13.2 — Grouping `list_unresolved_candidates()`'s flat result without a new query

**No new query mechanism needed.** `catalog_resolve_page()` (`web.py:1267`) already iterates the
full candidate list in Python to build `subject_labels`/`candidate_labels`. Grouping by
`candidate.provider_symbol_id or candidate.subject_series_id` (exactly one is ever set, by
`MatchCandidate`'s own BR-13 constructor guard) in that same loop — e.g. via
`itertools.groupby` on a pre-sorted list, or a plain `dict[int, list[MatchCandidate]]` — produces
the grouping AC-RES-09 needs entirely in the presentation/read-model layer. `list_unresolved_candidates()`
itself needs no change.

### §13.3 — Undo/Revert control placement/route

**Reuse the four existing `reverse_*_route`s as-is; the only new work is UI, not routing.** Each
already takes exactly the inputs available at the point of success feedback: `candidate_id` for
ATTACH/SET_UNDERLYING/MERGE, plus `series_id` for GROUP (`reverse_group_route`, `web.py:1443`,
needs the *new* Series' own id — already returned by `resolve_group()`, already available to the
success-feedback code path that would render the Undo control). No new reversal logic, no new
route needed — the AC-RES-07 "direct path" requirement is satisfiable by rendering a real
`<form>`/link to the existing route, pre-filled, at the point of success feedback, rather than
requiring the user to navigate to the separate "Reverse Candidate" section.

### §13.4 — Which error sites need rewriting for DFA-R02

**Re-verified directly against source, not taken from `034`'s enumeration.** Every
`ValueError`/`InvalidAssignmentError` site across all four `resolve_*` methods and `reverse_attach`
already leads with a plain-language clause and already places any `BR-##` reference
parenthetically (§5 below has the full list). **None require a full rewrite.** What's needed,
narrowly: (a) a consistent, explicit "reference:" label replacing the bare parenthetical, across
all sites, for uniformity — a wording/formatting pass; (b) one message
(`"survivor and absorbed Series share Provider(s) {ids} (BR-19)"`) states the *what* without the
*why* — needs one added clause explaining why a shared provider blocks MERGE, which requires
domain wording SDT should draft and route back to UIUX for confirmation (per `035` §10's own
"where the existing rule text already explains why, restate that reason" — for BR-19, the
existing text does not yet explain why, so this is new wording, not a restatement). Every
plain-language SUPERSEDED-rejection message already fully satisfies DFA-R02 as written and needs
no change.

### §13.5 — MERGE consequence text from existing service-layer data, without new read-model work

**Yes, without new read-model work.** `resolve_merge()`'s own inputs already carry everything §9
requires before execution: `survivor_series_id`/`absorbed_series_id` (caller-supplied, already
resolvable to labels via the same `series_service.get()` pattern `catalog_resolve_page()` already
uses for every other label lookup on this page) and the fixed, already-true fact that absorbed
history reassigns via `SeriesMerge` rather than deleting (`resolve_merge()`'s own body: identifiers
and provider assignments are `reassign`ed, `absorbed.archive()`s, nothing is deleted). The
confirmation step's MERGE-specific text is static/templated content plus two label lookups — no
new service method, no new field.

### §13.6 — Accessible-naming pattern for repeated per-candidate actions in a grouped layout

**Extend the existing `"Open Series {label}"`-style pattern with the group's own subject label,
not the row's position.** Since AC-RES-09 groups candidates under a named subject heading, the
per-row action's accessible name should read e.g. `"ATTACH MatchCandidate {id} to {candidate
Series label}"` — candidate-and-target-specific, matching `015`/`021`'s established
`"Open Series Duplicate Label Corp"` shape — rather than relying on the group heading alone to
disambiguate (a screen-reader user tabbing directly to a button, without having read the
preceding heading, must still get a fully-specific name).

---

## 3. Route-to-confirmation-mechanism mapping

| Current route (executes immediately) | Proposed confirmation step | New route (executes) |
|---|---|---|
| `POST /catalog/resolve/attach` (`resolve_attach_route`) | Re-validates `candidate_id`/`priority`, renders confirmation content: operation, subject (label), candidate Series (label), evidence tier/rule | `POST /catalog/resolve/attach/confirm` → calls `resolve_attach()` |
| `POST /catalog/resolve/group` (`resolve_group_route`) | Same, plus the entered new-Series attributes (label/type/interval/backfill/currency/country/subtype) restated | `POST /catalog/resolve/group/confirm` → calls `resolve_group()` |
| `POST /catalog/resolve/set-underlying` (`resolve_set_underlying_route`) | Same, plus the entered ratio | `POST /catalog/resolve/set-underlying/confirm` → calls `resolve_set_underlying()` |
| `POST /catalog/resolve/merge` (`resolve_merge_route`) | Same, plus survivor/absorbed labels and the full §9 consequence statement | `POST /catalog/resolve/merge/confirm` → calls `resolve_merge()` |

All four `reverse_*_route`s are unaffected by this mapping — `035` does not require a
confirmation step on *reversal*, only on the original disposition (§5, §12 AC-RES-01–04 name only
ATTACH/GROUP/SET_UNDERLYING/MERGE, never the reverse operations) — re-confirmed by reading `035`
in full; no AC references confirming a reversal.

---

## 4. Explicit preservation confirmation

| Requirement | Preserved how |
|---|---|
| **Uniform confirmation across tiers** | AC-RES-05/21's classification (§1) is structural, not a per-tier code path — the recommended mechanism (§2.1) has no tier input anywhere in its control flow |
| **Grouped competing candidates** | §1 AC-RES-09/10/11, §2.2 |
| **Direct Undo/Revert** | §1 AC-RES-07/08, §2.3 — reuses existing reversal routes, adds only the UI control |
| **Stronger MERGE disclosure** | §1 AC-RES-04, §2.5 — MERGE's confirmation step carries the additional §9 content the other three don't |
| **Plain-language errors** | §1 AC-RES-14, §2.4 — re-verified narrower in scope than `034`'s framing suggested, not narrower in requirement |
| **Accessibility requirements** | §1 AC-RES-16–19, §2.6 |
| **Discover → Resolve boundary** | §1 AC-RES-22 — zero Discover files touched by anything proposed in this assessment |

---

## 5. Full current error-message inventory (re-verified directly, not from `034`)

| Site | Message | Leads with plain language? | Rule id secondary? |
|---|---|---|---|
| `resolve_attach` | `"cannot ATTACH to an archived Series (BR-25)"` | Yes | Yes |
| `resolve_attach` | `"cannot ATTACH to a superseded Series — it is no longer the current attribution target for this history (DFA ruling, Series.status = SUPERSEDED)"` | Yes, with "why" | N/A (no BR-id) |
| `resolve_group` | `"cannot GROUP against an archived Series (BR-25)"` | Yes | Yes |
| `resolve_group` | `"cannot GROUP against a superseded Series..."` (same shape as above) | Yes, with "why" | N/A |
| `resolve_set_underlying` | `"cannot SET_UNDERLYING on a superseded Series..."` / `"...to a superseded Series..."` (×2) | Yes, with "why" | N/A |
| `resolve_merge` | `"MERGE survivor and absorbed Series must be different (BR-16)"` | Yes | Yes |
| `resolve_merge` | `"cannot MERGE into a superseded survivor Series..."` | Yes, with "why" | N/A |
| `resolve_merge` | `"survivor and absorbed Series share Provider(s) {ids} (BR-19)"` | **Yes, but no "why"** | Yes |
| `resolve_merge` | `"a confirmed CEDEAR and its underlying Series can never be MERGEd (BR-28)"` | Yes | Yes |
| `reverse_attach` | `"cannot reverse ATTACH: its ProviderAssignment has real ImportRun history (BR-29)"` | Yes, with "why" | Yes |

Every site already satisfies DFA-R02's core requirement (plain language leads, rule id is
already parenthetical/secondary). The only genuine gap is the BR-19 message's missing "why," and
the formatting question of whether a bare parenthetical counts as a "clearly-labeled" reference
under `035` §10's stricter reading — a wording decision, not a structural one.

---

## 6. Open items for UIUX, named rather than guessed at

1. **BR-19's "why" wording** (§2.4) — needs domain phrasing UIUX should confirm, not SDT-authored
   unilaterally, given DFA-R02 is a DFA-flavored ruling.
2. **`confirm_column` Help text** (AC-RES-13, §1) — "Confirms the strongest candidate as fact" is
   a real, newly-found tension with DFA-R01; needs rewording UIUX should own, not SDT.
3. **Reversed-candidate history visibility** (AC-RES-08) — `list_unresolved_candidates()` only
   returns unresolved ones, so nothing on the page today shows an already-resolved (and thus
   potentially-reversible) candidate after the success flash disappears. Making Undo "locatable
   after reload" needs either a new resolved-candidates listing or a different mechanism (e.g. a
   short-lived, id-addressable confirmation record) — **flagged as needing UIUX's own
   scope decision**, not resolved here, since it is plausibly larger than "the smallest safe
   addition" `035` otherwise stays within.

---

## What this assessment does not do

- Does not implement anything — no route, template, service method, or Help entry was changed.
- Does not introduce any automatic resolution or tier-based confirmation bypass.
- Does not redesign Discover or touch the Discover/Resolve boundary.
- Does not change which operations are valid for which subject kind.
- Does not settle the two open items in §6 — named for UIUX, not decided here.

## Gate

Per `035`'s expected transition — `035 specification → SE/SDT implementation assessment →
implementation → UI/UE validation` — this document is the assessment half. Returning to UIUX/SE
for disposition on §6's open items before implementation begins.
