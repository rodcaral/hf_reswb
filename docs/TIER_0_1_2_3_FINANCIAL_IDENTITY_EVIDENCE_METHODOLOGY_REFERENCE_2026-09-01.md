# Tier 0/1/2/3 Financial-Identity Evidence Methodology — Consolidated Reference (DRAFT)

**Prepared by:** SDT-WB
**Date:** 2026-09-01
**Status:** **DRAFT — documentation compilation only. Not yet reviewed or approved by DFA. `docs/28` upstream-source verification complete (§1) — one citation found unrecoverable, not a defect in this compilation but a genuine gap in the historical record; nothing it might have said is assumed.**
**Purpose:** Answers `ACTION_PLAN.md` §1's open-reference row ("Tier 0/1/2/3 | INC-4 | cite the
identity-methodology document") and §17 item 6, by compiling — not creating — the methodology
already settled and implemented across the closed `EvidenceSignal` and `IdentityAdjudication`
capabilities. Every rule below is cited to a specific, checkable source: implemented and tested
domain code, a commit, or a UIUX validation document. Where no such source exists, the item is
marked **OPEN** rather than completed by inference, per explicit instruction.

**This document does not itself settle anything.** It is a citation map. Where DFA review surfaces
a disagreement with how a rule is stated here, the *source* (code, ruling, ADR) governs, not this
compilation.

---

## 0. Scope boundary — two distinct tier vocabularies, not one

This reference concerns **`Tier 0/1/2/3`**, the vocabulary used by `CatalogMatcher`'s
candidate-generation cascade and by `EvidenceSignal`/`IdentityAdjudication` (INC-4's closed
technical-retention and human-adjudication capabilities). It does **not** concern, and must not be
conflated with, the separately-numbered **`Tier 1–4`** evidence hierarchy defined in
`docs/evidence/G1_G9_Final_Domain_Ruling.md` §2 for the distinct, on-hold, automated
`IdentityEvidenceEvaluator` (G1/G9) capability. Both trace conceptually to "the same DFA
disposition framework" (per `domain/evidence_signal.py`'s own `AuthorityClass` docstring), but they
are two different numbering schemes for two structurally separate, non-interoperating capabilities.
`056` §0 (`histfints_uiue`) states this boundary explicitly for the human-adjudication capability
this reference documents; nothing here activates, wires, or reinterprets G1/G9.

**Source-of-record boundary, restated exactly, preserved verbatim throughout this document:**

> `EvidenceSignals → human adjudication disposition → separately authorized catalog action`

— confirmed structurally enforced (not merely stated) by SDT-WB's independent conformance reviews
(`workbench/docs/DECISIONS.md`, 2026-09-01 entries citing `histfints@a113456`, `103de84`,
`40eae9e`/`0a8377a`): `IdentityAdjudicationService` holds `MatchCandidateRepository` read-only,
never calls any `ResolutionOperation`, and no catalog-mutation code path reads or writes an
`IdentityAdjudication` row.

---

## 1. Tier 0, Tier 1, Tier 2, and Tier 3's out-of-scope/deferred status

**Source:** `domain/evidence_signal.py`, `EvidenceType` enum (verbatim):

```
IDENTIFIER_OBSERVED = "IDENTIFIER_OBSERVED"  # Tier 0
IDENTIFIER_BRIDGED = "IDENTIFIER_BRIDGED"    # Tier 1
NORMALIZED_IDENTITY = "NORMALIZED_IDENTITY"  # Tier 2
```

Cross-confirmed by `application/catalog_matcher.py`'s own cascade methods (`_match_tier`,
`_match_tier2`, `_match_tier3`) and by `domain/evidence_signal.py`'s `AuthorityClass` docstring:

- **Tier 0 — direct, provider-observed identifier match.** `AuthorityClass.DIRECT_AUTHORITATIVE`:
  "one direct authoritative chain — an exact, provider-observed identifier match. Sufficient
  alone; does not require independent corroboration." Verbatim DFA citation embedded in source:
  *"Tier 0 requires one direct authoritative chain, not multiple independent sources."*
- **Tier 1 — identifier via bridge lookup** (e.g. OpenFIGI). `AuthorityClass.INDEPENDENT_PRIMARY`
  when eligible for independence per §4 below.
- **Tier 2 — deterministic, non-fuzzy structural pattern** (normalized `base_symbol`/`venue`/
  `currency` agreement). `AuthorityClass.TECHNICAL_PATTERN`: "real evidence, never itself
  Tier 0/1-strength."
- **Tier 3 — fuzzy label similarity.** **Explicitly, permanently out of scope for the
  `EvidenceSignal`/`IdentityAdjudication` capability.** `EvidenceSignal.__post_init__` enforces
  `0 <= tier <= 2` and raises if `tier == 3` is supplied — a structural, not merely documented,
  exclusion. Confirmed by `catalog_matcher.py`: `_match_tier3()` is unchanged by every INC-4
  commit to date and produces zero `EvidenceSignal` rows by construction
  (`test_tier_3_matches_a_close_fuzzy_label...`: `assert result.signals == ()`). No fix or
  extension to date has touched Tier 3's own matching logic (independently re-verified,
  `workbench/docs/DECISIONS.md`, multiple 2026-09-01 entries).

**`docs/28` verification — completed. Result: the citation does not resolve to any Tier 0–3
content; the original source is not recoverable.** `catalog_matcher.py`'s inline comments cite
`docs/28 §4-6/§7/§9/§11/§14` as the founding source for these tier mechanics, and the commit that
first implemented Tier 0/1 (`histfints@891a40d`, 2026-08-10) states explicitly in its own message:
*"docs/26 -> v8, docs/28 -> v4. Both confirm the algorithm as originally designed was
implementable exactly as written."* — i.e., at that date, "docs/28 v4" genuinely was the matching-
cascade design document.

**The document currently at that number is a different document.**
`histfints_uiue/028_Catalog_Discover_Relationship_Presentation_Disposition.md`, read in full for
this verification pass, is dated 2026-08-26 — sixteen days after the citing commit — and its
entire content (§1–§7) is a small, unrelated UX completion-scope disposition for Discover's
tracked/candidate/resolved relationship-state presentation (AC-DIS-05/06). It contains **no Tier
0/1/2/3 definitions, no matching-cascade rules, no evidence-authority hierarchy, and no section
numbered past §7** — nothing in it corresponds to the cited §4-6/§7/§9/§11/§14 content. Confirmed
against `PROJECT_INDEX.yaml`'s own `catalog_discover` sequence: `028` has only ever been this one
document in the tracked project record (immediately after `027`, immediately before `029`, dated
consistently) — not a renamed or overwritten file.

**Why the original is unrecoverable, checked rather than assumed:** `histfints_uiue`'s git history
begins at a single `43abedb` "Initial commit — git init per P3-5" — the repository was not
git-tracked at all on 2026-08-10, when the citing commit was written, so no earlier version of any
file (under this number or another) is retrievable from git. Whatever "docs/28 v4" actually
contained at that date — very likely under a different numbering scheme, from before this
project's 2026-08-27/28 path restructure (per `workbench`'s own `AGENTS.md` history) — is not
locatable in any location checked this pass (`histfints_uiue`'s current tree, `histfints`'s own
`docs/`, `PROJECT_INDEX.yaml`).

**One genuine, additional, directly relevant citation found while checking this** — not present in
the original draft, added here rather than left out: `024_Catalog_Discover_UX_Specification.md`
(`histfints_uiue`), **DFA-D03 — Evidence tiers** (verbatim): *"Tier 0 / Tier 1 / Tier 2 classify:
strength, quality, or authority of evidence under the established evidence model. They are not:
confidence percentages; financial conclusions; universal guarantees that a relationship is
correct."* and **DFA-D04 — Auto-resolution**: *"Automatic financial-identity adjudication from
Tier 0–2 alone is not established as financially legitimate."* This is a real, named,
independently-checkable DFA ruling (not domain-code docstring paraphrase) directly supporting §9
below — added there as a second, independent citation.

**Net effect on this compilation's own reliability**: every assertion in §1–§11 that traces to
`catalog_matcher.py`/`evidence_signal.py`/`identity_adjudication.py`'s own implemented, tested code
remains independently verified and unaffected — none of those citations depended on `docs/28`'s
content, only its own inline comments did. What is **not** independently confirmed against a named
DFA source is the *specific mechanical shape* of Tier 0/1/2 (exact-identifier / bridged-identifier
/ normalized-pattern) as a deliberate methodology choice, as opposed to an engineering
implementation of a methodology stated only more generally (as DFA-D03/D04 do) elsewhere. The
mechanical shape is real, shipped, tested, and has not been contradicted by any DFA ruling found —
but its own specific rationale citation is genuinely lost, not merely unread. **Marked OPEN, more
precisely than before**: whether DFA re-affirms the specific Tier 0/1/2 mechanical definitions in
§1 as still-current methodology, now that their original citation cannot be produced.

---

## 2. Quantity of Tier 2 evidence does not promote it to Tier 1

**Source:** `domain/evidence_signal.py`, `signals_are_independent()` docstring, verbatim DFA
citation: *"multiple Tier-2 signals never become Tier 1 by quantity."* Implemented as a hard
authority-class exclusion, not a threshold: `TECHNICAL_PATTERN`-authority evidence is excluded
from `signals_are_independent()`'s independence check "on the same footing as
`DERIVATIVE_PROVIDER`, however many Tier-2 signals exist, and however different their lineage
keys." Independently tested: `test_multiple_tier_2_signals_never_become_tier_1_by_quantity`
(two Tier-2 signals, genuinely different `upstream_lineage_key` values, still `assert not
signals_are_independent(a, b)`).

Reinforced at the adjudication-validity layer: `identity_adjudication_service.py`'s
`_validation_failures()`: *"Tier 2 alone cannot support `SAME_INSTRUMENT` or
`RELATED_BUT_DISTINCT`"* — blocks a disposition outright when every relied-upon signal is
`tier == 2`, regardless of count.

---

## 3. Evidence stance semantics: support / contradict / inform

**Source:** `domain/evidence_signal.py`, `EvidenceStance` enum:

- `SUPPORTS` — signal agrees with the winning/relied-upon hypothesis **and** its own temporal
  validity is `KNOWN`.
- `CONTRADICTS` — signal names a different subject/candidate than the hypothesis it is being
  compared against, "regardless of temporal validity — a genuine disagreement that must stay
  visible, never silently dropped."
- `INFORMS` — signal agrees with the hypothesis, but its own applicability is `UNKNOWN` — "agrees,
  but its own applicability is unestablished, the 'historically unresolved' case."

**Never a score or a combined verdict**, per the enum's own docstring: "A candidate's evidence set
is a collection of these, not a single verdict." Implemented in `catalog_matcher.py`'s
`_stance_for()`, and — because no temporal field exists yet on `Identifier`/`ProviderSymbol`
(confirmed directly, `catalog_matcher.py`'s own `_build_evidence_signals()` docstring) — every
signal this specific implementation currently builds is honestly `INFORMS` (never `SUPPORTS`) when
it agrees, which the source itself calls "the conservative, missing-evidence-respecting outcome,"
not a defect.

---

## 4. The independence rule: distinct upstream primary lineage + materially relevant assertion + compatible effective period

**Source:** `domain/evidence_signal.py`, `signals_are_independent()`, implemented as exactly three
conjunctive conditions (all three quoted verbatim from the function's own docstring, each tracing
to a DFA citation):

1. **Distinct upstream primary lineage** — *"different providers wrapping the same upstream source
   are not independent"* — enforced by comparing `upstream_lineage_key`; equal keys are never
   independent, "however many providers reported it."
2. **Materially relevant assertion** — implemented as `identity_dimension` equality; two signals
   about different dimensions are not independent evidence of the same fact.
3. **Compatible effective period** — via `_effective_periods_compatible()`; see §7/§8 below for the
   `UNKNOWN`/incompatible-period rules that feed this clause.

**Also excludes**, per §2/§5 of this document: `DERIVATIVE_PROVIDER`- and `TECHNICAL_PATTERN`-
authority signals, unconditionally, regardless of lineage/dimension/period.

Pure and deterministic, "never a score, never fed back into `MatchCandidate.evidence_tier`
automatically" (function docstring). Symmetric (`a, b == b, a`), tested directly.

---

## 5. Treatment of derivative evidence

**Source:** `domain/evidence_signal.py`, `AuthorityClass.DERIVATIVE_PROVIDER`: *"A provider's own
republication of someone else's primary fact... Never increases the independent-evidence count,
regardless of how many such derivative signals exist"* — verbatim DFA citation: *"derivative
provider metadata does not increase the independent-evidence count."* Implemented identically to
Tier 2's own exclusion (§2 above) — both authority classes are excluded from
`signals_are_independent()` on the same footing, and `identity_adjudication.py`'s `diagnose()`
separately surfaces every such signal (plus every signal sharing a lineage key with another) as
`derivative_or_common_upstream_signal_ids`, "informational evidence context only" for a human
reviewer — never itself blocking or promoting anything on its own (distinct from the authoritative-
contradiction gate, §6).

---

## 6. Authoritative contradiction handling

**Source:** `domain/identity_adjudication.py`, `diagnose()`'s `authoritative_contradiction_signal_
ids`: every `CONTRADICTS`-stance signal whose `authority_class` is `DIRECT_AUTHORITATIVE` or
`INDEPENDENT_PRIMARY` — explicitly **not** triggered by a `TECHNICAL_PATTERN`/`DERIVATIVE_PROVIDER`
disagreement, per the function's own docstring: *"a `TECHNICAL_PATTERN`/`DERIVATIVE_PROVIDER`
disagreement is real evidence but not an *authoritative* contradiction"* — verbatim DFA citation:
*"authoritative contradiction on a material dimension... forces `UNRESOLVED`."*

Enforced at the recording layer (`identity_adjudication_service.py`'s `_validation_failures()`):
when present among the relied-upon/considered evidence for a candidate disposition, this **blocks**
`SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT` outright — `UNRESOLVED` is not itself blocked by this
condition (§10 below).

**Separately, at the disclosure layer** (`056` AC-FID-06, `histfints_uiue`): every present
`CONTRADICTS`-stance signal must be individually marked "considered" by the reviewer before any
disposition can be recorded — a reviewer cannot rely on other evidence while ignoring a
contradiction that exists. UIUX-specified presentation requirement, layered on top of the
domain-level blocking rule; both independently confirmed live (`057`/`058`, `histfints_uiue`).

---

## 7. Required temporal applicability for relied-upon material identity dimensions

**Source:** `domain/identity_adjudication.py`, `signal_covers_period()`, docstring verbatim:
*"does this `EvidenceSignal` actually establish coverage for the period a human is about to assert
a disposition over?"* A signal only "covers" an adjudicated period if its own effective period
(when `KNOWN`) overlaps the adjudicated `effective_from`/`effective_to`. Enforced at
`identity_adjudication_service.py`'s `_validation_failures()`: for each `required_dimensions`
entry, if no relied-upon signal for that dimension covers the adjudicated period, the dimension
counts as unsatisfied and blocks a stronger disposition.

**Which dimensions are "material" for which disposition — OPEN, not completed by inference.**
`identity_adjudication_service.py`'s own `BLOCKING_REQUIRED_DIMENSIONS` constant is
`frozenset()` (empty) by explicit design, with its own docstring stating: *"Which dimension(s) are
actually material for a given disposition is a DFA methodology question this service does not
answer on its own."* The current production wiring (`histfints@b2a0ef5`, `web.py`'s
`_adjudication_form_state()`) derives `required_dimensions` per candidate as *every* dimension
that candidate's own real `EvidenceSignal` set touches (any stance) — a defensible, tested,
conservative default that closes a real production gap (`057`/`058`), but this is an
**implementation choice filling an explicitly-acknowledged DFA gap, not itself a DFA ruling** on
which dimensions are inherently material to `SAME_INSTRUMENT` vs. `RELATED_BUT_DISTINCT`. Marked
**OPEN**.

---

## 8. `UNKNOWN` applicability and incompatible-period treatment

**Source:** `domain/evidence_signal.py`, `EffectiveApplicability` enum, docstring verbatim:
*"`UNKNOWN` is not a weaker version of `KNOWN` — it is the explicit 'missing evidence' state...
Two `UNKNOWN`-applicability signals can never be treated as compatible with each other; unknown
never defaults to fresh or to matching."* Enforced in `_effective_periods_compatible()`: either
signal being `UNKNOWN` makes the pair incompatible, unconditionally — verified by
`test_unknown_applicability_is_never_compatible_even_with_another_unknown`.

At the adjudication-validity layer, `signal_covers_period()`: *"`UNKNOWN` effective applicability
can never satisfy a period, however retained/informative the signal otherwise is"* — verbatim DFA
citation: *"`UNKNOWN` effective applicability cannot satisfy that dimension."* A `KNOWN` but
non-overlapping period is treated identically for this purpose — verbatim DFA citation: *"known but
incompatible evidence cannot satisfy that dimension."* Both may still be retained and displayed as
informative/supporting evidence (`domain/identity_adjudication.py`'s `diagnose()`,
`temporally_incompatible_signal_ids`) — the exclusion is from *satisfying a material dimension for
a specific adjudicated period*, not from the evidence record itself.

**Distinguished from a genuine `KNOWN`-vs-`KNOWN` conflict** among the relied-upon set itself:
`known_periods_conflict()`, a narrower check than `diagnose()`'s own informational
`temporally_incompatible_signal_ids` — per its own docstring, an `UNKNOWN` signal "may be retained
alongside a compatible one without that combination itself being treated as a conflict."

---

## 9. Distinction between evidence strength and adjudication/confidence/probability

**Source, structural, not merely stated — including one named DFA ruling, found and added during
the `docs/28` verification pass (see §1):**

- **DFA-D03 (Evidence tiers) and DFA-D04 (Auto-resolution)** —
  `024_Catalog_Discover_UX_Specification.md` (`histfints_uiue`), verbatim: *"Tier 0 / Tier 1 /
  Tier 2 classify: strength, quality, or authority of evidence under the established evidence
  model. They are not: confidence percentages; financial conclusions; universal guarantees that a
  relationship is correct."* and *"Automatic financial-identity adjudication from Tier 0–2 alone
  is not established as financially legitimate."* This is the earliest, most directly-named DFA
  source for this distinction found in this compilation — independently checkable, not a
  paraphrase.
- `identity_adjudication.py`'s `AdjudicationDiagnostics` docstring: *"never a score, rank,
  recommendation, preselection, or synthesized disposition. Every field is a plain fact... or a
  boolean derived directly from `EvidenceSignal`'s own fields, nothing weighted or combined into a
  single verdict."* The type itself carries only tuples of signal ids and booleans — no numeric
  field exists to hold a score even if one were computed.
- `AdjudicationValidation` docstring: *"Never a score: a disposition is either currently valid or
  it names every reason it isn't; there is no partial or weighted state between those two."*
- `independent_supporting_pairs()` docstring: *"inspectable evidence for a human reviewer, never a
  count, score, or automatic tier promotion... this returns pairs of signals for a reviewer to
  read, not a number that could be mistaken for a strength measure."*
- UIUX's own framing (`056` §5, `histfints_uiue`, revision note): explicitly distinguishes
  **validity enforcement** (an evidentiary sufficiency threshold — an option becomes genuinely
  unrecordable) from **recommendation** (implying which enabled option is correct) — the former is
  required by DFA's settled methodology, the latter is prohibited. `AC-FID-08`: a blocking warning
  states which condition triggered it, "never states or implies that `UNRESOLVED` is the
  recommended, correct, or suggested outcome."
- Independently re-confirmed live (`058`, `061`/`063`/`066`, `histfints_uiue`): no disposition
  radio is ever pre-checked; `UNRESOLVED` is never highlighted or defaulted to as a consequence of
  a blocking condition.

---

## 10. Explicit adjudication effective period required for a stronger disposition

**Source:** `identity_adjudication_service.py`'s `_validation_failures()`, verbatim: *"a stronger
disposition requires an explicit adjudication `effective_from` — its absence is never interpreted
as current, all-time, or irrelevant."* Enforced structurally: `effective_from is None` is checked
before any per-dimension evaluation and blocks `SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT`
unconditionally when absent.

**`UNRESOLVED` is exempt from this and every other gate in this document** — `_validation_failures()`
returns `()` immediately when `disposition is UNRESOLVED`, per its own comment: *"per the DFA
ruling... `UNRESOLVED` remains recordable"* when these requirements are not met. `UNRESOLVED` does
still require its own non-evidentiary requirements (`unresolved_qualifications` non-empty, per
`IdentityAdjudication.__post_init__`) — a substantive-basis requirement, not an evidentiary gate.

---

## 11. The boundary: `EvidenceSignals → human adjudication disposition → separately authorized catalog action`

Already stated in full at §0 above, restated here for completeness of the requested list. Sources:

- `domain/identity_adjudication.py`'s module-level `IdentityAdjudication` docstring states the
  three-step chain verbatim and states: *"Recording an adjudication never calls, and this type has
  no path to call, any `ResolutionOperation`."*
- `application/identity_adjudication_service.py`'s class docstring: *"deliberately the only
  connection point between `EvidenceSignal`... and `IdentityAdjudication`. Never touches
  `MatchCandidateRepository.save()`, never calls `resolve_attach()`/`resolve_group()`/
  `resolve_merge()`/`resolve_set_underlying()` or any `reverse_*()` counterpart."*
- Migration `0023`'s own SQL comment: *"identity_adjudication is never written to by, and never
  writes to, `match_candidate`'s own `resolution_operation`, or any ATTACH/GROUP/MERGE/
  SET_UNDERLYING code path."*
- `human_reviewer_attested` is a mandatory, non-defaultable field (`IdentityAdjudication.
  __post_init__` raises if not `True`) — *"financial-identity adjudication must be a human's,
  never an AI's; an AI cross-check may inform the rationale but is never itself the reviewer."*
- Independently structurally verified (not merely read), `workbench/docs/DECISIONS.md`, 2026-09-01
  entries: zero `resolve_*`/`reverse_*`/`MatchCandidate.save()` calls anywhere in the adjudication
  code path, confirmed by direct grep across every commit in the chain (`503aa91` through
  `0a8377a`); live database confirmed 0 `MatchCandidate`-type `entity_change_log` entries ever.

---

## 12. Finalized list of questions that actually require DFA judgment

**Verification against `docs/28` is complete (§1). It resolved one uncertainty (confirmed: the
`docs/28` citation cannot be checked against its original content, which is genuinely lost, not
merely unread) without resolving — and without attempting to resolve by inference — the two
substantive open questions below. A third, narrower item from the original draft is retired as
subsumed by the first.**

1. **Whether DFA re-affirms the specific Tier 0/1/2 mechanical definitions (§1) as still-current
   methodology, now that their original citation (`docs/28 v4`, pre-dating this repository's git
   history and 2026-08-27/28 path restructure) cannot be produced.** Nothing found this pass
   contradicts the shipped definitions — `024`'s DFA-D03/D04 (§9) describe evidence tiers at a more
   general level fully consistent with them — but the specific mechanical mapping (Tier 0 =
   exact provider-observed identifier, Tier 1 = bridged identifier, Tier 2 = normalized structural
   pattern) has no independently-checkable DFA source remaining, only the shipped, tested code
   itself. **This subsumes the original draft's item 1** (the "not yet re-read" placeholder is now
   replaced by this more precise, actually-verified finding).

2. **Which `identity_dimension` values are materially required for `SAME_INSTRUMENT` versus
   `RELATED_BUT_DISTINCT` specifically, and whether the shipped `BLOCKING_REQUIRED_DIMENSIONS`
   default has financial-methodological authority or is only an implementation default.** §7.
   `identity_adjudication_service.py`'s own docstring states plainly this is "a DFA methodology
   question this service does not answer on its own." The current production behavior (every
   dimension the candidate's own real evidence touches becomes required) is a tested, defensible,
   conservative engineering default — not itself a DFA ruling on per-disposition materiality. Kept
   OPEN, not resolved technically, per explicit instruction.

3. **What evidence is required to establish that an authoritative contradiction has itself been
   resolved.** §6. No source found in this compilation — code, commit, or UIUX document — defines
   this. `identity_adjudication_service.py`'s own comment states only that the current mechanism
   "re-evaluates the same deterministic condition against whatever is currently relied-upon,"
   without defining what evidentiary act constitutes a genuine resolution (a new superseding
   signal, an explicit reviewer override with its own justification, or something else). Kept
   OPEN, not resolved technically, per explicit instruction.

**Both #2 and #3 remain exactly as stated in the prior draft** — this verification pass did not
touch either, consistent with the instruction to keep them open for DFA rather than resolve them
technically.

---

## What this document does not do

Does not create, alter, or approve any methodology — every rule above is cited to an already-
implemented, already-tested, already-independently-verified source. Does not ask DFA to approve
this compilation. Does not reopen `EvidenceSignal` or `IdentityAdjudication` (both remain
CLOSED/ACCEPTED, unaffected). Does not resolve `ACTION_PLAN.md` §1's GAP row — that row should be
updated to cite this document only once DFA has reviewed it and confirmed nothing here
misrepresents a ruling; until then this remains a draft citation map, not the answer to the GAP.
Does not modify HistFinTS or `histfints_uiue`.
