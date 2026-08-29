# INC-12 (Catalog: Discover) — Gate C Evidence Package for DFA

**From:** SDT-WB
**Date:** 2026-08-29
**Status:** Read-only compilation from already-validated evidence. No code, UI, or specification
was created, changed, or redesigned to produce this package. No financial judgment is made
here — that is exactly what this package hands to DFA to make.

**Sources** (all `histfints_uiue`, verified directly against `histfints` source before
inclusion, not taken on a document's word alone): `024_Catalog_Discover_UX_Specification.md`
(governing spec + AC-DIS-01–22), `027_Catalog_Discover_Implementation_Evidence.md`,
`029_Catalog_Discover_Relationship_Presentation_Completion_Evidence.md`,
`032_Catalog_Discover_UIUX_Runtime_Validation_Evidence.md` (independent UIUX reproduction),
`033_Catalog_Discover_Workstream_Closure.md`. Cross-repo anchor: `histfints_uiue` @ `f7d3ca3`
("Catalog Discover: close workstream — UIUX runtime validation PASS (032/033)"), and
`histfints` source as checked out at read time, 2026-08-29.

---

## 1. Governing AC-DIS criteria relevant to financial interpretation

The full spec defines AC-DIS-01–22; the subset that bears directly on financial-interpretation
correctness (Gate C's actual question — "does any candidate presentation read as identity?") is:

| AC | Requirement |
|---|---|
| AC-DIS-01 | ProviderSymbol is presented as provider/catalog evidence, **not** financial identity |
| AC-DIS-02 | Discovery is not described as establishing financial identity, tracked status, equivalence, or resolved relationship |
| AC-DIS-03/04 | Evidence-tier labels are explained as strength/authority classifications — never confidence percentage, financial conclusion, or automatic correctness |
| AC-DIS-05 | Tracked-Series relationship is clearly distinguishable from not-yet-tracked |
| AC-DIS-06 | Candidate/suggested relationship is clearly distinguishable from resolved relationship |
| AC-DIS-07 | Candidate creation is not presented as resolution |
| AC-DIS-08 | Run Discovery does not silently perform automatic financial-identity adjudication from Tier 0–2 evidence alone |
| AC-DIS-11/12 | Manual actions (Add/Verify ProviderSymbol, overrides, candidate creation) use consequence-oriented wording, never implying resolution where none occurred |
| AC-DIS-14 | No direct Attach/Group/Set-underlying adjudication control is exposed on Discover |

Governing DFA rulings already folded into the spec (`024` §2, DFA-D01–D07) and PO decisions
(§3, PO-D01–D06) are cited in full in `024` — not restated here; §2/§3 of that document define
what "identity," "candidate," and "resolved" are permitted to mean throughout.

---

## 2. Exact runtime candidate/identity labels and explanatory wording (verbatim)

All strings below were re-confirmed directly against `histfints` source at read time — not
copied from a document's paraphrase.

**Help text** (`help_content.py`):

- `provider_symbol_column`: *"A raw ticker as one specific data provider reports it — discovered automatically, not yet necessarily linked to anything you track."*
- `evidence_tier`: label "Evidence tier" — *"How strong the evidence is that this ProviderSymbol and Series are the same real-world security."* Format: *"0-3 — 0 is strongest (an exact identifier match), 3 is weakest (name similarity only)."*
- `match_candidate`: *"A proposed relationship between a discovered ProviderSymbol (or an already-tracked Series) and a candidate Series — created as evidence for a human to review, never a resolved relationship by itself."*
- `resolved_relationship`: *"An authorized disposition (ATTACH, GROUP, MERGE, or SET_UNDERLYING) applied to a MatchCandidate through Resolve. Discover never applies one of these itself — it only ever records candidate evidence."*
- `provider_symbol_lifecycle` (label "Closed / excluded"): *"A provider symbol can be closed (its own identity's validity window has ended) or excluded from a discovery run (out of that run's scope). Both describe the ProviderSymbol/catalog record itself only — never that the underlying security is delisted, that a Series is invalid, or that anything stopped existing."*
- `run_discovery`: *"Reads a Provider's snapshot, records/updates ProviderSymbols, and records any matching evidence as an unresolved MatchCandidate for Resolve. It never automatically attaches, groups, merges, or sets an underlying relationship — every disposition is a human decision made through Resolve."*
- `candidate-vs-resolved` topic body (full): *"Discovering a ProviderSymbol, and even finding matching evidence for it, are not the same thing as resolving anything... A MatchCandidate is a proposal... It carries no authority of its own — it exists purely for a human to review... A relationship only becomes resolved when a human applies ATTACH, GROUP, MERGE, or SET_UNDERLYING to that candidate through Resolve... Run Discovery can leave many candidates unresolved in a single pass, and that is the normal, expected outcome, not a failure."*

**Runtime flash text**, all four relationship states (`web.py`'s `_relationship_state_suffix()`,
confirmed live in `029`/`032`):

| State | Exact wording |
|---|---|
| Linked to a tracked, resolved Series | `"...linked to tracked Series: Apple Inc (Series #1) — resolved relationship"` |
| Not linked to any tracked Series | `"...not currently linked to a tracked Series"` |
| Unresolved candidate relationship exists | `"...candidate relationship exists, review required in Resolve: Series #2 (tier 0)"` |
| Provider symbol closed (lifecycle, orthogonal axis) | `"...provider symbol closed as of 2024-06-01 (catalog lifecycle state only)"` — composes with the above, e.g. `"...provider symbol closed as of 2024-06-01 (catalog lifecycle state only) — not currently linked to a tracked Series"` |

Verified no wording overlap between the "candidate" and "resolved" strings (test-enforced per
`029`, independently re-confirmed per `032`).

---

## 3. Provider/identifier compatibility wording — "COMPATIBLE" does not exist in this codebase

**Checked directly, not assumed**: grepped `catalog_discover.html`, `web.py`, and
`help_content.py` for the literal string `COMPATIBLE` — zero matches anywhere in this codebase.

What actually exists and is live is a **three-value** `ProviderSymbol.VerificationStatus` enum
(`UNVERIFIED` / `VERIFIED` / `FAILED`, `domain/provider_symbol.py`), surfaced via the Verify
ProviderSymbol flash message exactly as its raw enum value:

> `"ProviderSymbol {id} ({raw_ticker!r}): {VERIFIED or FAILED}{lifecycle suffix}{relationship suffix}"`

e.g. `"ProviderSymbol 2 ('CANDIDATE'): VERIFIED — linked to tracked Series: Apple Inc (Series #1) — resolved relationship"`.

This reports whether the provider's endpoint accepts/returns data for the literal identifier
string — a technical probe result, not a claim about financial identity, and it carries no
adjacent identity-confirming language (confirmed: the string is a bare `VERIFIED`/`FAILED`, not
embedded in any sentence claiming resolution).

A separate, more granular five-state identifier-compatibility vocabulary
(`COMPATIBLE`/`INCOMPATIBLE_FORMAT`/`NOT_FOUND`/`PROVIDER_ERROR`/`UNKNOWN`) was proposed in
`CAPABILITY_A_D_IMPLEMENTATION_ASSESSMENT_2026-08-26.md`'s Capability B — that assessment states
directly *"no schema support exists for any of the five today"* and it remains unimplemented,
confirmed unchanged by this pass's grep. **Reported because it is the only "COMPATIBLE"-shaped
wording anywhere in this project's history — it does not exist in the running system.**

---

## 4. Unresolved / ambiguity states

- **`MatchCandidate` with `resolution_operation=None`** — the unresolved-candidate state. Every
  `MatchCandidate` Discovery produces defaults to this; nothing in Discover ever sets it to
  anything else (`027` §1 item 2, independently re-verified by `032` at the source level).
- **`describe_relationship_state()`'s own structure** is XOR by construction:
  `linked_series` populated, or a (possibly-empty) `unresolved_candidates` tuple — never both. No
  fifth, blended, or partial state exists.
- **Empty-lookup states** (four surfaces: discovery-run history, raw snapshots, change log, field
  overrides) each carry explicit, distinct text (e.g. `"No discovery runs found for Provider
  9999"`) — none reads as invalid/nonexistent, all confirmed live against a real nonexistent id.
- **AC-DIS-09/10 are `N/A`, not silently dropped**: after `027` removed both automatic-resolution
  call sites, there is no automatic action left for any trace/report mechanism to describe — this
  is recorded explicitly in three separate documents (`027`, `029`, `032`) as a deliberate `N/A`,
  not an unaddressed gap.

---

## 5. Confidence/score display — none found

**No numeric confidence, percentage, or score of any kind is shown anywhere in Discover.**
Checked specifically: the evidence-tier field is `0`–`3`, explicitly documented as *"strength...
classification"* with an explicit anti-pattern warning in the governing spec itself (`024` §10,
"Avoid: '90% confidence', 'high-confidence identity', 'verified instrument' unless those
meanings are separately established") — confirmed the live help text matches this ("How
strong... 0 is strongest..., 3 is weakest...") with no percentage anywhere. No other numeric
quality/confidence value exists on this page.

---

## 6. Available user actions and what each actually does

| Action | What it actually does | What it does *not* do |
|---|---|---|
| **Run Discovery** | Reads a Provider's snapshot; creates/updates `ProviderSymbol` rows; on a match, saves one unresolved `MatchCandidate` (`resolution_operation=None`) | Never calls `resolve_attach`/`resolve_group`/`resolve_set_underlying` — confirmed by grep (`027`) and independently by source inspection (`032`); zero remaining call sites |
| **Add ProviderSymbol** | Creates a `ProviderSymbol` row | Does not create or imply a relationship to any Series |
| **Verify ProviderSymbol** | Calls `verify_provider_symbol()`, reports `VERIFIED`/`FAILED` plus lifecycle and relationship state | Does not adjudicate identity — a pure probe-and-report action |
| **Field overrides (set/remove)** | Overrides/clears provider/catalog metadata on a `ProviderSymbol` | Does not imply financial identity resolution |
| **Suggest / Create MatchCandidate** | Saves a `MatchCandidate` proposal | Never resolves it — `resolution_operation` stays `None`; flash text is literally `"Created MatchCandidate {id}"`, no resolution language |
| **(No Attach/Group/Set-underlying control exists on this page)** | — | Confirmed: `catalog_discover.html` contains no form posting to `/catalog/resolve/*` (grep, `032`) |

The only route off this page toward an actual identity decision is the existing, separate
**Resolve** page (INC-13) — Discover performs no adjudication action of its own.

---

## 7. Representative validated runtime evidence: candidate discovery ≠ identity adjudication

Real, end-to-end (not mocked) run cited in `027` §1 item 1, independently reproduced in `032`:

- Seeded a Series (`AAPL`, USD/CABLE) with an `OBSERVED` ISIN identifier.
- Ran `POST /catalog/discovery` against a snapshot carrying the **exact same**
  ticker/currency/settlement/ISIN — Tier 0, the strongest evidence tier the system can produce
  (this exact input previously auto-ATTACHed unconditionally, before removal).
- Result: `provider_assignments after run: 0` (was `1` before this change). Exactly one
  unresolved `MatchCandidate` (`evidence_tier=0`, `resolution_operation=None`). **No
  `ProviderAssignment` was created; no financial identity was established, at the strongest
  possible evidence tier.**
- The same candidate was then independently confirmed resolvable by a human through the
  existing, unchanged `CatalogResolutionService.resolve_attach()` path (`027` §1 item 4) —
  demonstrating the full discovery → candidate → (separate, human) resolution chain works
  end-to-end, with discovery alone never crossing into resolution at any point.
- `032` re-confirmed this boundary independently, by direct source inspection against the
  currently-checked-out code (not `027`'s word): *"zero calls to
  resolve_attach/resolve_group/resolve_set_underlying/_auto_resolve/_attempt_relationship_match
  remain — only a docstring warning against reintroducing them."*

---

## What this package does not do

- Does not judge whether this wording is financially accurate or sufficient — that is Gate C's
  own question, for DFA.
- Does not modify any code, template, help content, or specification.
- Does not self-certify Gate C or Gate D. `033`'s own record already states this explicitly:
  *"DFA/PO gate | Not self-certified; none found open"* — a report that no new question was
  found, not a DFA confirmation.
