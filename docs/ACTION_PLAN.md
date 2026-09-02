# WORKBENCH ACTION PLAN

**Plan revision:** v7 — **Last updated:** 2026-09-01 — **Supersedes:** v6
**Owner:** PO — **Domain authority:** DFA — **Technical authority:** SE / SDT — **UIUX authority:** UIUX
**Purpose:** Dependency-ordered master plan for the Financial Research Workbench (`hf_reswb`).

> This document coordinates work. It does not replace authoritative financial decisions, analytical specifications, technical specifications, defect records, or UIUX specifications. Where a governing source conflicts with this plan, the governing source prevails, and the discrepancy must be surfaced to the owning authority and corrected here.

*v7 incorporates the reviewed v6 consolidation plus DFA corrections available as of 2026-08-29. Items whose governing evidence is still unavailable remain explicit GAPs; this plan does not manufacture closure.*

*"Workbench V0" below refers to **product** scope. Plan revisions appear only in this header.*

## 1. Parties, sequences, vocabulary

### Parties and settled authority

| Acronym | Party | Settles |
|---|---|---|
| PO | Project Owner | product scope, priorities, sequencing, closure and release |
| DFA | Domain Financial Advisor | financial meaning, terminology meaning, methodology, evidence interpretation, analytical eligibility, conclusion boundaries |
| SE | Software Engineer | architecture, technical validation, provider/adaptor investigation, engineering constraints |
| SDT1/SDT2/n | Software Development Team (agents) | implementation under SE direction |
| UIUX | UIUX authority | interaction, information architecture, terminology *presentation*, discoverability, accessibility, warning and uncertainty display, usability validation |

UIUX is an **independent authority**, not a specialism coordinated by SE — it settles its own
questions (§4's boundary table) without SE approval. That independence is about decision
authority, not routing: UIUX-to-DFA communication still routes through SE, per PO's
2026-08-29 settlement (`ACTOR_MODEL.md`'s "Confirmed relationships"; `ACTOR_AND_MODEL_INTERACTION_RULES.md`
§2.3, "DFA does not interact directly with either SDT" — extended here to read "with any
implementation-side actor," UIUX included, not only the two SDTs). Routing chain:

**SDT1/SDT2/n, UIUX ↔ SE ↔ DFA ↔ PO**

This is a routing model, not a requirement that every issue pass through every party.

- Technical constraints must not silently determine financial meaning.
- A UI decision that could change interpretation routes to DFA.
- A DFA ruling does not authorize implementation.
- A PO scope decision does not establish financial validity.

**Two boundaries that previously collided** (both parties may raise; one settles):

| Question | Raised by | Settled by |
|---|---|---|
| Can the user understand the screen and complete the task? (comprehension, discoverability, accessibility) | anyone | UIUX |
| Would a user reading the screen correctly still draw a materially misleading **financial** conclusion? | anyone | DFA |
| What does this term mean, and is this label financially accurate? | anyone | DFA |
| Where does the term appear, how prominent is it, is it used consistently? | anyone | UIUX |

### The three named sequences

Each has a distinct job. Do not merge them or invent a fourth.

**Research sequence** (what the product must preserve, DFA-governed):
**Evidence → Calculation → Analytical Finding → Research Conclusion**

**Analytical sequence** (how a research capability is built):
**Financial question → Evidence needs → Methodology → Diagnostics → Finding → Research conclusion**

**Delivery sequence** (how any increment moves to closure):
**Evidence availability → Domain sufficiency → Product scope → UIUX specification → Technical implementation → Four-gate validation**

### Shared vocabulary

- **Series** — the HistFinTS/Workbench time-series/catalog object with metadata. **Instrument/security** — the financial object a Series may represent; use these terms only for that financial object, not as synonyms for Series. **Observations** — time-indexed values. **series_master_list** — the reference table.
- Where "status" appears, its domain must be qualified: *acquisition*, *Series/lifecycle*, *ProviderSymbol/catalog*, *financial-identity*, or *analytical/result* (UP-2).

### Open references (GAP — expand or cite a governing source)

| Identifier | Used in | Action |
|---|---|---|
| "remaining P0 dependencies" | INC-1 history | enumerate, or cite the record listing them |
| D1–D4 | INC-3, INC-4, §7 | cite the decision record defining D1–D4 |
| Tier 0/1/2 | INC-4 | RESOLVED (2026-09-01) — governing reference: `TIER_0_1_2_3_FINANCIAL_IDENTITY_EVIDENCE_METHODOLOGY_REFERENCE_2026-09-01.md`, adopted per DFA's rulings (relayed by SE/PO); the reference's own §1 preserves the unrecoverable historical `docs/28` provenance limitation rather than claiming it away. **Tier 3 remains deferred/out of scope**, not resolved by this row. |
| BR-29 | INC-11 | cite the rule record; state what "history-preserving removal" guarantees |
| `SUPERSEDED` (unresolved) | INC-11 | DFA to define the state's meaning and permitted display |
| "non-production / fixture" | §7 | RESOLVED — authority comes from an explicit persisted catalog/configuration designation established through an authorized auditable project/system process; MatchCandidate dispositions are independent |

## 2. Product objective and boundaries

The Workbench is a financial research and analytical product built over HistFinTS.

V0 may support research and general research conclusions. It must not silently promote results into investor-specific recommendations, trade/execution decisions, fair-value, mispricing, arbitrage, or predictive claims without an explicitly established methodology and evidence base (SP-11).

Architectural boundary: **`hf_reswb` reads HistFinTS read-only** (SP-7). Workbench diagnostics and analytical results do not themselves authorize mutation of HistFinTS.

## 3. Standing rules

One ID space. Cite by ID from increments; do not restate.

### Standing prohibitions (SP)

| ID | The Workbench must not |
|---|---|
| SP-1 | automatically resolve financial identity |
| SP-2 | synthesize a global financial-data quality, acquisition-quality, comparability, or identity verdict, score, or confidence percentage — in computation **or** in presentation |
| SP-3 | convert provider/technical signals — compatibility, search ranking, symbol similarity, normalization — into proof of financial identity |
| SP-4 | infer financial invalidity from acquisition status or gaps alone, or infer provider failure solely from the absence of a successful run |
| SP-5 | invent universal staleness, dispersion, cadence, tolerance, margin, or quality thresholds — including PASS/FAIL, "missed expected observation", or SLA framing |
| SP-6 | activate fallback providers merely because a primary acquisition failed |
| SP-7 | mutate HistFinTS from Workbench analysis, or present UI behavior implying such mutation |
| SP-8 | silently delete or reattribute observations |
| SP-9 | treat provider-reported corporate actions or events as reconciled financial facts, or as automatic economic explanation |
| SP-10 | suppress material uncertainty for presentation convenience |
| SP-11 | promote research findings into investor-specific recommendations, trade/execution decisions, or fair-value / mispricing / arbitrage / predictive claims |

### Standing UIUX defaults (UP)

| ID | Default |
|---|---|
| UP-1 | User interpretation is part of correctness. A technically correct result is insufficient if a reasonable user is likely to interpret it incorrectly. |
| UP-2 | Status domains are explicit. Never a single generic `Status` where several domains coexist. |
| UP-3 | Unknown is not negative. `UNKNOWN`, missing, unavailable, unresolved, not-yet-tracked, stale, or absent evidence must not be displayed as invalid, failed, nonexistent, low-quality, or incompatible. *(Display counterpart of SP-4; SP-4 governs inference, UP-3 governs labelling.)* |
| UP-4 | Progressive disclosure. The primary surface may be concise, but provenance, assumptions, evidence quality, dates, units, and limitations remain reachable. |
| UP-5 | *Withdrawn — folded into SP-2 and SP-5. ID retained so existing references resolve.* |
| UP-6 | Help is part of the product. Each screen increment compares **actual behavior → current Help → intended meaning**, and classifies each discrepancy as UIUX, documentation, DFA/domain, PO/spec, or implementation. |
| UP-7 | Actions communicate consequence. A label and its feedback must make clear whether the action records evidence, creates a candidate, changes configuration, changes lifecycle, adjudicates identity, or only navigates. |
| UP-8 | The four levels of the research sequence (§1) stay visually and linguistically distinct. |

## 4. Validation — four gates

"Dual validation" is retired. Every increment closes through four gates.

| Gate | Owner | Establishes |
|---|---|---|
| A — Technical correctness | SE/SDT | implementation behavior, invariants, migrations, data integrity, failure handling, automated regression coverage |
| B — UX / accessibility correctness | UIUX | task completion, hierarchy, labels, keyboard, focus, screen-reader behavior where material, empty/error/recovery states, warning and uncertainty display, comprehension |
| C — Financial-interpretation correctness | DFA | terminology, evidence meaning, units/currency/date/period clarity, uncertainty, analytical eligibility, conclusion level, absence of materially misleading financial interpretation |
| D — Product acceptance | PO | agreed scope, priority, closure and release |

A passing test suite does not establish UX correctness. Passing UX validation does not establish financial correctness. **If a gate is N/A for an increment, the owning authority records why** — silence does not close a gate.

## 5. Master sequence

**State vocabulary (closed set).** `CLOSED` — validated and accepted through all four gates. `ACTIVE` — in progress. `NEXT` — cleared to start. `BLOCKED` — waiting on a named gate. `DEFERRED` — postponed pending evidence. `CONTINUOUS` — runs across increments.

**IDs are permanent.** New increments append; nothing is renumbered. The table is grouped by state for readability, not by execution order — execution order follows *Blocked by*.

States marked **†** are carried from the v5 UIUX review and must be confirmed against the project index before this revision is treated as authoritative (§17).

| ID | Increment | State | Primary owner | Blocked by | Governing material |
|---|---|---|---|---|---|
| INC-1 | Import & Status UX pilot | CLOSED † | UIUX + SE | — | UIUX pilot specification |
| INC-2 | Search decision gate and UX | CLOSED † | DFA + PO + UIUX | — | Search decision-gate material |
| INC-11 | Series / Provider Assignment | CLOSED † | SE/SDT + DFA + UIUX | — | BR-29 record; provider-assignment decisions |
| INC-12 | Catalog: Discover | CLOSED | UIUX + SE/SDT + DFA | — | `024_Catalog_Discover_UX_Specification.md` (histfints_uiue); §8/§9 baseline |
| INC-4 | Financial identity/evidence prerequisites | ACTIVE (bounded `EvidenceSignal` capability CLOSED, see §12) | DFA + SE/SDT | — | identity decisions; evidence pipeline; §8/§12 baseline for the closed sub-capability |
| INC-5 | Corporate-action / economic-event evidence | live capture capability CLOSED (see §13) | SE/SDT + DFA | — (scope set by INC-6/INC-7 needs) | `REQUEST-event-capture.md`; §8/§13 baseline |
| INC-6 | Adjustment-basis and coverage evidence | CLOSED | SE/SDT + DFA | — | `REQUEST-tranche2-migration.md`; §8/§14 baseline (provider-level `adjustment_basis` field only — see §14's closure-scope note) |
| INC-13 | Catalog: Resolve | CLOSED | UIUX + SE/SDT + DFA | — | `035_Catalog_Resolve_UX_Specification.md`, `039_Catalog_Resolve_Workstream_Closure.md` (histfints_uiue); §8/§10 baseline |
| INC-3 | Publication-aware acquisition-history diagnostic | CLOSED | DFA → SE/SDT | — | D1–D4 rulings; DFA BYMA calendar rulings; §8/§11 baseline |
| INC-14 | Application-wide dynamic feedback / live regions | CLOSED | UIUX + SE/SDT + PO | — | `043_Application_Wide_Dynamic_Feedback_UX_Specification.md`, `052_Application_Wide_Dynamic_Feedback_AC_DFB_08_Final_Validation_Evidence.md` (histfints_uiue); §8/§16 baseline |
| INC-16 | `USER_DISABLED` manual-Run prohibition | CLOSED | UIUX + SE/SDT + PO | — | `047_USER_DISABLED_Manual_Run_UX_Specification.md`, `053_USER_DISABLED_Manual_Run_UIUX_Validation_Evidence.md` (histfints_uiue); §8/§16a baseline |
| INC-17 | `IdentityAdjudication` corrective increment (authoritative-contradiction resolution + case-specific materiality persistence) | NEXT — DFA §7 ruling and SDT-HF design finalization (`2f1da5a`) both COMPLETE; UIUX contract + DFA trigger-map confirmation open in parallel | DFA (§7 ruling ✓) → SDT-HF (design finalization ✓) → [UIUX (contract) \|\| DFA (trigger-map confirmation)] → SDT-HF (implementation) → validation | — | `TIER_0_1_2_3_FINANCIAL_IDENTITY_EVIDENCE_METHODOLOGY_REFERENCE_2026-09-01.md` §6b/§7b/§7c; `histfints/docs/future_designs/INC17_CORRECTIVE_INCREMENT_DESIGN.md`; §12a/§12b/§12c detail |
| INC-15 | Catalog: Cross-Workflow (Search/Discover/Resolve hand-offs) | CLOSED | UIUX + SE/SDT + DFA | — | `040_Catalog_Workflow_Cross_Screen_UX_Assessment.md`, `041_Catalog_Workflow_Cross_Screen_UX_Specification.md`, `045_Catalog_Workflow_AC_XWF_11_Revalidation_Evidence.md` (histfints_uiue); §8/§10a baseline |
| INC-7 | Core Workbench research capability | BLOCKED | DFA → SE/SDT + UIUX | per-analysis evidence prerequisites | `SPEC-panel-eligibility.md`; `DECISIONS.md` |
| INC-8 | Screen-by-screen UIUX expansion | CONTINUOUS | UIUX + SE + DFA | per-screen decision gates | UIUX audits and specifications |
| INC-9 | Workbench-wide information architecture | DEFERRED | PO, informed by UIUX + DFA + SE | several validated workflows delivered | future PO decision |
| INC-10 | Four-gate validation | CONTINUOUS | SE + UIUX + DFA + PO | — | §4 |

**Blocking is per-analysis, not global.** INC-7 waits on the evidence its *specific* question needs — not on global completeness of INC-4/5/6.

## 6. Increment template

The template is **proportional**. Ceremony on an increment with no user-facing surface is a failure mode, not diligence.

**Core fields — every increment:**

1. User/product goal and financial/product question
2. Required evidence
3. Methodology or governing decision
4. Legitimate conclusion level
5. Prohibited — cite SP/UP IDs, then any increment-specific rule
6. Owner and dependencies
7. Gate A/B/C/D closure criteria, or a recorded reason a gate is N/A
8. Open questions, each with a named GAP owner

**Conditional fields — only where the increment has a user-facing surface:**

9. User-visible states
10. Material uncertainty and warnings to display
11. Available actions and the consequence each communicates (UP-7)
12. Accessibility requirements
13. Help dependencies — the UP-6 behavior ↔ Help ↔ intended-meaning comparison

INC-4, INC-5 and INC-6 are pipeline/evidence work; fields 9–13 apply to them only at the point their evidence reaches a screen.

## 7. D1–D4 evidence capabilities — presentation rules

Referenced by INC-3, INC-4 and INC-12. Safe order of work:

1. persisted, auditable non-production classification;
2. structured identifier compatibility;
3. identity evidence pipeline;
4. descriptive cadence/coverage;
5. *later* — analysis-specific comparability;
6. *later* — fitness-for-use assessment.

**Non-production / fixture.** Authoritative classification requires an explicit persisted catalog/configuration designation established through an authorized, auditable project/system process, or an auditable decision that establishes that designation. Authority comes from the classification process and evidence, not merely from operator access. Naming patterns, inactivity, unusual values and other heuristics remain non-authoritative candidate evidence. This authority is independent from MatchCandidate ATTACH/GROUP/MERGE dispositions: neither decision authorizes or proves the other. Distinguish authoritative classification, heuristic/unconfirmed candidate and unknown; preserve authority/source, confirming actor/process, timestamp, reason/evidence and audit history.

**Identifier compatibility.** `COMPATIBLE`, `INCOMPATIBLE_FORMAT`, `NOT_FOUND`, `PROVIDER_ERROR` and `UNKNOWN` must always be qualified as **identifier compatibility**. `COMPATIBLE` must never read as identity confirmation (SP-3).

**Identity evidence pipeline.** Show required dimensions, which are supported and which unmet, provenance, and the unresolved state. No global identity-confidence score (SP-2). `automatic_resolution_enabled=False` remains binding (SP-1).

**Cadence / coverage.** Permitted evidence: observed coverage span, successful-run dates, observed gaps, observation counts. Not permitted until methodology exists: PASS/FAIL cadence, cadence margin, "missed expected observation", SLA compliance (SP-5).

## 8. Closed increments — reusable baselines

Their remaining value is the pattern they establish. Do not reopen; cite them.

**INC-1 — Import & Status.** Baseline for acquisition-state presentation and for the pilot pattern itself: specification → implementation → four-gate validation. Acquisition states (`FAILED`, `STALE`, `NEVER`) are operational/evidence states (SP-4, UP-3).

**INC-2 — Search.** Baseline for **find → understand → continue**: Series hand-off, contextual Resolve hand-off, Search/Discover/Resolve kept distinct, and no Search-derived `AMBIGUOUS` or `DUPLICATE` state (SP-3).

**INC-11 — Series / Provider Assignment.** Baseline for object, lifecycle and provider presentation: lifecycle vs acquisition vs archive separated; provider priority and fallback; configured-primary distinguished from successful provider; BR-29 history-preserving removal; no provider-replacement workflow. `SUPERSEDED` remains unresolved — GAP, DFA.

**INC-3 — Publication-aware acquisition-history diagnostic.** Baseline for session-aware acquisition diagnostics generally, not only BYMA today: raw elapsed time reported alongside a session-aware count computed only from authoritative curated calendar evidence, `UNKNOWN`/incomplete coverage left unavailable rather than inferred, and acquisition-process gaps kept structurally distinct from missing-observation gaps. Accepted 2026-08-29 (Gate A/C/D — SDT/DFA/PO; Gate B N/A, no UI introduced). Full detail, prohibitions and the validated result: §11. Do not broaden venue coverage, add a threshold/margin/quality-verdict, or build UI from this acceptance without a new decision.

**INC-12 — Catalog: Discover.** Baseline for the evidence/candidate-generation vs. adjudication boundary generally, not only Catalog today: discovery records provider/catalog evidence and, at most, an unresolved `MatchCandidate` — never an automatic identity resolution, at any evidence tier including Tier 0 (exact match); a candidate and a resolved relationship never share wording and are structurally mutually exclusive at the data layer; no confidence/percentage score is ever shown alongside evidence-tier classification. Accepted 2026-08-29 (Gate A — SDT; Gate B — UIUX; Gate C — DFA; Gate D — PO). Full detail, the Gate C evidence package, and the validated result: §9. **Does not extend to Resolve (INC-13)** — Resolve's own gates are unaffected and settle on their own evidence — **and does not authorize automatic financial-identity resolution at any tier**; do not extend this closure to another increment without a new decision.

**INC-14 — Application-wide dynamic feedback.** Baseline for live-region/announcement behavior generally, not only this workstream today: a server-rendered `aria-live` region with no subsequent DOM mutation (this app ships zero JavaScript) cannot rely on `aria-live`'s own change-detection to announce on first paint — moving keyboard focus to the region on load (`tabindex="-1"`/native `autofocus`, no script required) is the reliable substitute; a region needing first-occurrence-only behavior across repeated same-URL polling needs an explicit server-side flag, not an unconditional attribute; and an unconditional focus-management change must be checked against every existing URL-fragment landing pattern in the app, not assumed safe by default — the one existing case (`#series-{id}`) genuinely regressed before being fixed. Accepted 2026-08-31 (Gate A — SDT-WB; Gate B — UIUX, `052`, with two named, not-glossed-over evidence-scope qualifications; Gate C — N/A, no financial content; Gate D — PO). Full detail and the five-document validation chain: §16. **Does not extend to INC-12, INC-13, or INC-15** — each remains closed on its own, separately-settled evidence; do not reopen or silently extend without a new decision.

**INC-4 (`MatchCandidate → EvidenceSignal` capability scope only) — Financial identity and evidence prerequisites.** Baseline for retaining individually-inspectable technical evidence alongside a single-winner decision field generally, not only Tier 0/1/2 today: a legacy single-value field (`evidence_tier`/`rule_reference`) can gain a genuine 1:N evidence record without being rewritten or treated as superseded, as long as the new record is additive and the old field stays exactly as it was; first-hit short-circuiting silently discards every evidence source that didn't win — retaining all of them (as SUPPORTS/CONTRADICTS/INFORMS relative to the winner) is what makes a later contradiction or corroboration inspectable at all; a live capability with genuinely zero real-world occurrences yet (an empty table) is not itself a defect or an incomplete implementation, provided the reason (no eligible input has occurred) is independently traceable, not merely asserted; and a bounded, deliberately narrow closure of one sub-capability inside a larger, still-open increment must state its own boundary explicitly rather than let the increment's overall `ACTIVE` state imply nothing was ever settled. Accepted 2026-09-01 (Gate A — SDT-WB, `613638a`; Gate C — DFA; Gate D — PO). Full detail: §12. **Closes only the `MatchCandidate → EvidenceSignal` retention/gathering capability** — does **not** close INC-4 as a whole, validate or expand Tier 3, change Resolve/adjudication semantics, or authorize any automatic identity resolution; do not reopen or silently extend without a new decision.

**INC-5 (live Yahoo/FRED provider-event capture capability) — Corporate-action and economic-event evidence.** Baseline for evidence-capture wiring and its own limits generally, not only Yahoo/FRED today: a decorator/wrapper class that implements only the base interface (here, `fetch()`) silently strips access to any wrapped implementation's extra methods — a real, previously-invisible defect class since a broad except-and-log-empty pattern in the caller made a masked `AttributeError` indistinguishable from a genuine empty result; a composition-boundary test using the real factory/registry, not a fake standing in for either, is what actually catches this class of gap; captured evidence needs row-level, per-event traceability (source, subject, date, capture time, provider's own id, raw representation, provenance) but does not necessarily need a dedicated run-tracking entity if a shared per-call timestamp already reconstructs the grouping — a real but weaker provenance mechanism than an explicit FK, and must be described as such, not overstated as equivalent. Accepted 2026-09-01 (Gate A — SDT-WB; Gate C — DFA; Gate D — PO; Gate B deferred to first user-facing surface, unchanged). Full detail: §13. **Closes only the live capture capability** — does not establish adjustment correctness, cross-provider comparability, causal explanation of price discontinuities, historical price repair, or automatic corporate-action adjudication, and does not extend to any other increment; do not reopen or silently extend without a new decision.

**INC-4 (manual financial-identity adjudication, `IdentityAdjudication`, capability scope only) — Financial identity and evidence prerequisites.** Baseline for a human-adjudication layer sitting over a technical-evidence-retention layer, preserving `EvidenceSignals → human adjudication disposition → separately authorized catalog action` as three genuinely separate, separately-authorized steps: a disposition vocabulary that traces to the same DFA framework as an existing, structurally unrelated evaluator must still be its own distinct type, never cast to or from the other, so that "who is allowed to produce this value" (a human, an automated evaluator) stays enforced by the type system, not by convention; every DFA validity gate (missing material evidence, authoritative contradiction, temporal incompatibility, an absent adjudication period) must share one code path between the read-only preview and the actual recording, so the two can never silently disagree; and an accessibility "freeze" observed during validation is not necessarily an application defect — a capture-tooling artifact and a genuine missing-focus-target defect can both be real at once, and distinguishing them requires checking the tool as rigorously as the application under test. Accepted 2026-09-01 (Gate A — SDT-WB, `7248ffe`; Gate B — UIUX, fully discharged via the `061`–`067` chain, including a genuinely distinct application defect found and fixed — `40eae9e`, confirm-page focus target — and a genuinely distinct capture-tooling defect found and fixed — `0a8377a`, Speech Viewer length-cap; Gate C — DFA; Gate D — PO). Full detail: §12. **Closes only the `IdentityAdjudication` capability** — does **not** close INC-4 as a whole, authorize automated adjudication, authorize Tier 3 processing, or extend to the separate, on-hold G1/G9 capability; do not reopen or silently extend without a new decision.

**INC-6 (provider-level `adjustment_basis` scope only) — Adjustment basis and historical coverage.** Baseline for evidence-bar discipline on a per-provider assertion field generally, not only these seven providers today: an unevidenced value already stored is not self-justifying and must be downgraded once no traceable evidence can be found for it (BYMA's `RAW→UNKNOWN` correction); a real, registered, observation-producing path with a negative evidence-review result is `UNKNOWN`, never left at `NULL` (`NULL` is reserved for a path that has never produced an observation at all, i.e. never yet reached the point where evidence review even applies); a "0 attributable observations" signal can be a dedup artifact of a lower-priority provider being routinely suppressed, not proof the provider is silently failing — the correct signal is the run-outcome count (`SUCCESS`/`FAILED`), not an attributed-observation count (the Twelve Data finding); and a `NULL`-conforming state tied to a live-data condition (Finnhub's "zero successful observations so far") must be recorded as a standing, self-expiring rule for future review, not a one-time classification. Accepted 2026-09-01 (Gate A — SDT-WB, twice, catching one real inventory drift — `Twelve Data` — between passes rather than restating a stale value; Gate C — DFA; Gate D — PO). Full detail, the finalized 7-provider inventory, and the Finnhub boundary condition: §14. **Closes only the provider-level `adjustment_basis` field classification** — does **not** extend to cross-provider comparability, historical splicing, corporate-action correctness, UI implementation, or any other increment; do not reopen or silently extend without a new decision.

**INC-16 — `USER_DISABLED` manual-Run prohibition.** Baseline for bringing a manual-action path into alignment with an existing, already-correct automated/scheduled path, not only Run today: an eligibility rule enforced on one path (scheduled Run's `status == ACTIVE` filter) is not automatically enforced on a manually-triggered equivalent unless independently checked at that path's own choke point; a rejection message surfaced verbatim to a user (a flash, an error string) must be reviewed for leaked internal rationale/spec-reference text even when the underlying behavior it describes is already correct — a defect in wording is not a defect in logic and does not need to reopen or re-validate the logic, only the string. Accepted 2026-09-01 (Gate A — SDT-WB; Gate B — UIUX, `053`, full AC-UD-01–12 PASS plus a narrower, appropriately-scoped follow-up for the adjacent wording cleanup, not re-run in full; Gate C — N/A, no financial content; Gate D — PO). Full detail and the two-stage validation record: §16a. **Does not extend to `SUPERSEDED`, `DELISTED_OR_DISCONTINUED`, or `PROVIDER_UNAVAILABLE`**, and **does not extend to any other increment**; do not reopen or silently extend without a new decision.

**INC-13 — Catalog: Resolve.** Baseline for a confirmation-and-reversibility layer over an already-adjudication-owning workflow, not only this page today: every disposition (ATTACH/GROUP/SET_UNDERLYING/MERGE) requires an explicit, uniform, tier-independent confirmation step restating operation/subject/candidate/evidence-tier (MERGE additionally discloses absorbed-data consequence); competing candidates for the same subject are grouped and labeled as ambiguity, never silently resolved by resolving a sibling; every disposition remains directly, visibly reversible after reload via the pre-existing reversal mechanism; evidence tier is informational context only, never authorization, at every tier including Tier 0. Accepted 2026-08-29 (Gate A — SDT-WB conformance review; Gate B — UIUX, PASS with two named validation-coverage qualifications, not rounded up; Gate C — DFA; Gate D — PO). Full detail, the SDT-WB implementation-assessment hand-off, and the conformance review: §10. **Does not authorize automatic identity resolution at any evidence tier — the confirmation step accepted here is uniform and unremovable, not a gate that acceptance loosens** — **each future disposition through this mechanism remains subject to its own evidence and adjudication requirements**, and this closure does not extend to another increment without a new decision.

**INC-15 — Catalog: Cross-Workflow.** Baseline for cross-screen hand-offs over an already-adjudication-owning workflow, not only Catalog today: a navigation link between screens (Discover→Resolve, Search→Resolve) is never itself a disposition — reachable only via `GET`, never a route capable of changing resolution state; disposition provenance shown at any echo point states operation + Candidate id as fact, never styled or worded to imply verification; a persistent Undo/Revert control, once offered for an operation, must resolve its target from the one authoritative persisted fact for that operation, never a resolution-time pointer that a later operation type can leave stale (the GROUP-specific lesson this increment's own correction cycle produced — see §10a); reversal preserves the underlying candidate/tier/rule, never erasing evidence history. Accepted 2026-08-31 (Gate A — SDT-WB conformance review, twice — see §10a for why the first pass's PASS did not catch what live runtime validation did; Gate B — UIUX, `044`→`045`, PASS after one concrete defect was found, root-caused, fixed, and re-validated against the identical scenario; Gate C — DFA; Gate D — PO). Full detail: §10a. **Does not authorize automatic identity resolution at any tier** and **does not extend to another increment** without a new decision.

## 9. INC-12 — Catalog: Discover

**State:** CLOSED/ACCEPTED — **Owner:** UIUX + SE/SDT + DFA — **Gate disposition:** A — PASS (SDT technical, 2026-08-29, below). B — PASS (UIUX, 2026-08-29, below). C — PASS (DFA). D — ACCEPT (PO).

**Gate status update (2026-08-29).** `histfints_uiue` commit `f7d3ca3` ("Catalog Discover: close workstream — UIUX runtime validation PASS (032/033)"), verified directly — `033_Catalog_Discover_Workstream_Closure.md`: AC-DIS-01–22 all satisfied (AC-DIS-09/10 N/A by design, reconfirmed), zero discrepancies against `024`'s specification, no sibling repository modified (validation ran against a disposable, seeded, now-deleted test instance). **Gate A** (candidate generation reproducible/provenance-bearing): satisfied — independently reconfirmed by `032`'s live-reproduced and source-verified evidence, on top of `027`/`029`'s implementation evidence. **Gate B** (a user can tell a candidate from a decision, UP-7): satisfied — this is precisely what UIUX's completed runtime validation closes. `PROJECT_INDEX.yaml`'s `current_gate` field confirms: `'None open'` from UIUX's own side. **Gates C and D remain open** — `033`'s own record states this itself: *"DFA/PO gate | Not self-certified; none found open"* — UIUX reports finding no open DFA/PO question, which is not the same as DFA or PO having actually confirmed one. Neither gate is closed by this commit.

**Boundary:** Discover owns **evidence and candidate generation**. Resolve (INC-13) owns **adjudication and disposition**. The UI must not blur them.

**Prohibited:** SP-1, SP-2, SP-3. Increment-specific: Tier-based auto-resolution that is not supported by established methodology must not be normalized by the interface.

**Gates:** A — PASS. B — PASS. C — PASS (DFA, on the Gate C evidence package: AC-DIS financial-interpretation criteria, verbatim runtime wording, `VERIFIED`/`FAILED` meanings, unresolved/ambiguity presentation, absence of confidence scoring, action consequences, the Tier-0 zero-`ProviderAssignment` case). D — ACCEPT (PO).

**Open:** governing Discover specification cited — `024_Catalog_Discover_UX_Specification.md` (`histfints_uiue`), AC-DIS-01–22. GAP resolved.

**Closure scope — stated explicitly, not implied.** This closes **only** the Discover workstream as specified in `024`/validated in `027`/`029`/`032`/`033`. It does **not**: extend to or close INC-13 (Resolve) — Resolve's own gates are unaffected and remain to be settled on its own evidence; authorize automatic financial-identity resolution at any evidence tier — AC-DIS-08's boundary (no Tier 0–2 auto-resolution) is part of what was accepted, not lifted by acceptance; or extend to any other increment. The Boundary and Prohibited lines below are preserved unchanged as the accepted, binding scope — not loosened by this closure.

## 10. INC-13 — Catalog: Resolve

**State:** CLOSED/ACCEPTED — **Owner:** UIUX + SE/SDT + DFA — **Gate disposition:** A — PASS (SDT-WB read-only conformance review, 2026-08-29, below). B — PASS (UIUX, `039`, including the two recorded NVDA validation-coverage qualifications — not silently rounded up). C — PASS (DFA). D — ACCEPT (PO).

**Closure record (2026-08-29).** Specification `035` (settled DFA-R01–R03/PO-R01–R05, later gained §6a's AC-RES-08 mechanism and the approved `confirm_column`/BR-19 wording) → SDT-WB implementation assessment (`CATALOG_RESOLVE_UX_IMPLEMENTATION_ASSESSMENT_2026-08-29.md`, hand-off to SDT-HF, SDT-WB did not implement) → SDT-HF implementation in `histfints` (uncommitted, in-progress at review time) → UIUX runtime + real-NVDA validation (`036` initial, 2 discrepancies found; `037` both fixed and reconfirmed; `038` mandatory real-NVDA pass; `039` closure, **PASS with two named validation-coverage qualifications**: the MERGE-only consequence sentence and BR-19's exact wording were each "attempted, not confirmed" by real-NVDA output specifically — both independently supported by direct DOM/HTTP and source-level evidence instead, recorded as such rather than rounded up to a full NVDA PASS).

**SDT-WB's own promised read-only conformance review, performed against the real implementation, not assumed from `039` alone**: full `histfints` suite re-run, **1412 passed, 0 failed**; `confirm_column`/BR-19 wording confirmed byte-for-byte against `035`'s approved text; all four `/catalog/resolve/{op}/confirm` routes confirmed present; zero tier-conditional branching found anywhere in `web.py`/`catalog_resolution_service.py` (AC-RES-05/21's structural guarantee holds); grouping implemented via a typed `SubjectKey` (provider_symbol vs. series kind + id) rather than a bare int — exceeds this assessment's own suggested approach, avoiding a cross-kind id-collision risk a bare int would carry; Undo/Revert reuses all four pre-existing `reverse_*` routes exactly as handed off, plus one new, narrowly-scoped `find_terminal_merge_for_series()` method for MERGE's Series-side echo (a real edge case UIUX found in `036`, fixed in `037`); **`catalog_discovery_service.py`/`catalog_discover.html` show zero diff** — Discover untouched, AC-RES-22 and the Discover→Resolve boundary confirmed intact by non-touch, not by claim.

**Preserved boundary, stated explicitly, not implied.** This closes only what `035`/`039` specify: a confirmation-and-reversibility mechanism layered onto the *existing* four disposition operations. It does **not**: authorize automatic identity resolution at any evidence tier — DFA-R01's "tier is never adjudication authority" and AC-RES-05/21's uniform, unremovable confirmation step are part of what was accepted, not lifted by acceptance; change which operations are valid for which subject kind; or extend to any other increment. **Each future human disposition through this mechanism remains subject to its own evidence and adjudication requirements** — this closure accepts the *mechanism* (confirm, disclose, reverse), not any specific past or future disposition decision on its merits; DFA-D07's "candidate creation is not resolution" and the whole evidence/adjudication boundary this workstream itself enforces (`024` §1, unchanged) continue to apply to every individual ATTACH/GROUP/SET_UNDERLYING/MERGE going forward, exactly as before.

**Prior audit-stage record, preserved below as history — not the current state:**

**Audit status (2026-08-29) — verified against `histfints_uiue` commit `261d2ba` / `034_Catalog_Resolve_Current_State_UX_Audit.md` directly, not taken on the relayed summary alone.** **Audit COMPLETE** — confirmed, the document's own gate line: *"Catalog Resolve current-state UX audit: COMPLETE — ready for DFA/PO decisions on §8/§9 before a UX specification can be approved."* **DFA semantics and PO product decisions are not confirmed settled by this artifact — the opposite is stated directly in it.** `034` §8 lists three explicit, still-open DFA financial-methodology gates (resolution friction vs. evidence tier; raw internal rule-identifier exposure in error messages; competing-candidate presentation) and §9 lists five open PO product-decision gates (confirmation/review step before disposition; reversibility communication; competing-candidate grouping; MERGE consequence communication; NVDA-validation scope) — none marked resolved in this document, and its own commit message reads *"DECISION-GATE PENDING."* This plan is not recording "DFA semantics settled" or "PO product decisions settled" as fact on the strength of an instruction alone when the one available artifact states the opposite — flagged for SE/PO to clarify (a since-relayed settlement not yet reflected in `histfints_uiue`, or a premature characterization) rather than silently absorbed either way.

**Not implementation-ready regardless of how that question resolves** — Owner is UIUX + DFA at this step, not SE/SDT; `034` itself is a current-state audit, not a specification, and states a specification only follows once §8/§9 are actually settled. SE/SDT ownership begins only after UIUX delivers the Resolve UX specification with testable acceptance criteria.

**Question:** how is an identity adjudication recorded, by whom, on what evidence, and how is it shown as a decision rather than a computation?

**Prohibited:** SP-1, SP-2, SP-3.

**Open:** required evidence, user-visible states, and the disposition vocabulary — GAP, DFA. (UIUX's read-only audit may inform, not settle, this — the vocabulary itself remains DFA's to decide.)

## 10a. INC-15 — Catalog: Cross-Workflow

**State:** CLOSED/ACCEPTED — **Owner:** UIUX + SE/SDT + DFA — **Gate disposition:** A — PASS (SDT-WB read-only conformance review, below). B — PASS (UIUX, `044`→`045`, below). C — PASS (DFA). D — ACCEPT (PO).

**Closure record (2026-08-31).** `040` (cross-screen assessment, 5 findings, PO-XW01–05) → `041` (specification: DFA-X01–05, PO-XW01–05, AC-XWF-01–15, §8's four open technical questions) → SDT-WB implementation assessment (`CATALOG_CROSS_WORKFLOW_IMPLEMENTATION_ASSESSMENT_2026-08-29.md`, all four §8 questions answered, hand-off to SDT-HF, SDT-WB did not implement) → SDT-HF implementation in `histfints` (`5ab086e`, then `9b277cc` self-correcting AC-XWF-08's GROUP-target bug before any external review) → **SDT-WB's first conformance review (2026-08-29): PASS** — full suite 1435/1435, every diffed file read, structural/content tests for AC-XWF-13/14 confirmed, the AC-XWF-08 GROUP-target fix verified end-to-end. → **UIUX's live runtime validation (`044`, 2026-08-31): FAIL** — AC-XWF-01–10/13–15 confirmed live-PASS, but AC-XWF-11 concretely violated for GROUP specifically: the *displayed* provenance text still named the pre-existing matched-against Series (via `describe_relationship_state()`'s own `terminal.candidate_series_id` read), not the Series `resolve_group()` actually created — even though `9b277cc` had already fixed the Undo *control's* target via `find_group_created_series()`. Root cause: two docstrings in the same file (`describe_relationship_state()` and `find_group_created_series()`) directly contradicted each other, and the display code followed the wrong one. → SDT-HF fix (`b759a85`): `describe_relationship_state()` now calls `find_group_created_series()` itself, so the displayed text and the Undo control share one source of truth instead of two independently-computed answers that could disagree. → **UIUX revalidation (`045`, 2026-08-31): PASS** — the identical `044` scenario reproduced exactly, now showing the correct Series; ATTACH spot-checked as a regression sanity check, not re-run in full (nothing in `b759a85` touches its code path beyond the shared function, itself spot-checked). → **SDT-WB's second conformance review (this record)**: verified `b759a85` directly — `HEAD`, working tree clean, full suite **1436 passed, 0 failed** (up from 1435); read the actual diff (`catalog_resolution_service.py`, `web.py`) confirming `describe_relationship_state()` now branches on `ResolutionOperation.GROUP` and calls the same `find_group_created_series()` already proven correct for the Undo control, removing the second, independently-wrong lookup entirely rather than patching its output; confirmed the new regression tests reproduce `044`'s exact failing scenario at both the application layer and end-to-end, including the displayed label, not only the Undo control.

**Named, not glossed over: SDT-WB's own first conformance review reported PASS on a defect UIUX's live runtime pass then caught.** The first review was source/diff/test-level (reading the implementation, running the existing suite, verifying the tests that existed) and correctly confirmed everything those methods can confirm — the bug was a contradiction between two docstrings' *claims* about what `candidate_series_id` means for GROUP, with the actually-shipped test suite not asserting the *displayed label's* Series identity for the GROUP case specifically (only the Undo control's `series_id` field, which was already correct). Only comparing the rendered page against independently-established ground truth (a live browser session, a second `GET /series?id=N` call) surfaces that class of defect — exactly the reason this project's four-gate model keeps SDT's technical conformance and UIUX's runtime validation as two separate, non-substitutable gates rather than treating either as sufficient alone. Recorded here as a real limitation of source-level conformance review, not smoothed over.

**Preserved boundaries, stated explicitly, not implied — per PO's instruction, verbatim scope:**

- **Navigation ≠ adjudication.** Every new cross-screen link (Discover→Resolve, Search→Resolve) is a plain `GET <a href>`, structurally unable to reach any `resolve_*`/`reverse_*` route (all `@app.post`-only) — confirmed both by direct source/route inspection and by UIUX's live click-through. Clicking a link changes no candidate's resolution state.
- **Disposition provenance ≠ proof of identity.** Every provenance sentence states only the factual disposition (operation + Candidate id, now correctly identifying the linked Series for GROUP as well as ATTACH) — no wording, badge, or styling anywhere implies verification or correctness beyond what was actually resolved (AC-XWF-11/12, DFA-X03).
- **Reversal changes the disposition without erasing evidence history.** Every Undo/Revert control reuses the pre-existing, unmodified `reverse_attach_route`/`reverse_group_route` — the same mechanism INC-13 already confirmed never deletes the underlying candidate/tier/rule (AC-XWF-10, DFA-X04).
- **No automatic resolution, scoring, or certainty.** No new code path reaches a `resolve_*` method from a GET request; no confidence/percentage/ranking field was introduced anywhere in this increment's diff — confirmed structurally (AC-XWF-13/14, DFA-X01/X05), not only by inspection.

**Prohibited:** SP-1, SP-2, SP-3. Increment-specific: a persistent Undo/Revert control must never be rendered from a resolution-time pointer whose meaning varies by operation type (the specific defect this increment's own correction cycle both produced and closed) — any future echo point added to this workflow must resolve its target from the one authoritative persisted fact for that operation, not re-derive it independently in more than one place.

**Gates:** A — PASS (SDT-WB, twice — see above for why the first pass alone was insufficient). B — PASS (UIUX, `044`→`045`). C — PASS (DFA). D — ACCEPT (PO).

**Closure scope — stated explicitly, not implied.** This closes only the cross-screen hand-off/provenance/Undo mechanism specified in `041` and validated in `044`/`045`. It does **not**: extend to or reopen INC-12 (Discover) or INC-13 (Resolve) — both remain closed on their own, unaffected, separately-settled evidence; authorize automatic financial-identity resolution at any evidence tier; or extend to any other increment, including INC-14 (a distinct, not-yet-specified live-region workstream that happens to be adjacent in scope). No sibling repository was modified by either SDT-WB conformance review — read-only throughout, per the standing sibling-repository rule.

## 11. INC-3 — Publication-aware acquisition-history diagnostic

**State:** CLOSED/ACCEPTED — **Owner:** DFA → SE/SDT — **Gate disposition:** A — PASS (SDT technical, 2026-08-29, baseline below). B — N/A (no UI was introduced; nothing to validate). C — PASS (DFA). D — ACCEPT (PO).

**Validated, accepted baseline (2026-08-29).** `hf_reswb/application/publication_aware_acquisition_diagnostic.py` produced a live, fully-traceable `AVAILABLE` result for all 6 series in the first bounded population's real-data test (11323–11327, 11329; the 7th CEDEAR series, 11328, correctly excluded as `ETF`, not `STOCK`): `sessions_elapsed=1`, `coverage_complete=True` against the one curated authoritative 2026-08-18 `TRADING` record (BYMA 2026 Trading Calendar, `TRADING_CALENDAR` tier), with raw elapsed acquisition time reported alongside it throughout, and confirmed byte-for-byte traceable back to an independent `byma-trading-sessions` query. Full result detail: `docs/DECISIONS.md`, 2026-08-29 entries. **This behavior is the reference baseline going forward — do not alter it without a new decision**, per this increment's own standing prohibitions (unchanged, restated for emphasis on acceptance): do not broaden venue coverage beyond BYMA, do not add a threshold, margin, or quality/comparability verdict of any kind, and do not build a UI surface from this acceptance alone (Gate B remains N/A until a UIUX specification exists). One residual named, not closed: `UNKNOWN`-status session propagation is validated only by unit test — no live authoritative `UNKNOWN`-status record exists yet to confirm the same behavior on real data.

**Original scope, unchanged below:**

**Financial question:** for a Series whose acquisition history shows gaps or apparent lateness, are those gaps inconsistent with financially relevant BYMA trading opportunities, or explained by the historically applicable BYMA market schedule?

**First bounded population:** `STOCK` Series for which applicability to the relevant BYMA trading venue/market can be established independently for the historical period analyzed. MERVAL membership is **not required** and does not define eligibility; where available it is optional corroborating/descriptive evidence only.

**Required evidence** (kept separate): observed successful acquisition timestamps and raw elapsed-time gaps; independently established BYMA venue applicability for the Series-period; historically applicable BYMA session evidence; configured acquisition cadence where relevant; provider/acquisition provenance.

**Governing calendar evidence:** authoritative BYMA calendars and dated BYMA circulars/communications applicable to the historical date concerned. Controlled manual curation is acceptable for the first increment when every accepted session/date record is traceable to its BYMA source. Historical calendar PDFs may be manually acquired and used when available; systematic PDF coverage is not required before sufficiently evidenced dates can be used.

**Methodology:** raw elapsed time remains descriptive operational evidence. Session-aware calculation may count or exclude dates only where the historical session state is sufficiently established. A date that cannot be established confidently remains `UNKNOWN`; any session-aware result materially dependent on it is unavailable or explicitly qualified, never inferred. Current calendars must not be projected backward merely because historical evidence is absent.

**Legitimate conclusion:** descriptive only — e.g. a gap spans a stated number of established BYMA trading sessions; or an interval contains no established eligible session and therefore does not by itself evidence a missed market-day acquisition. Raw elapsed-time evidence remains usable when session interpretation is unresolved.

**Prohibited:** SP-2, SP-4, SP-5, SP-6, SP-7. Increment-specific: do not infer sessions from weekdays, public holidays alone, observed acquisitions, observed prices, neighboring dates, MERVAL membership or behavioral patterns; do not construct a calendar from the observations under assessment and then treat it as independent evidence; do not alter `STALE`/`OK` semantics automatically; do not extrapolate the BYMA methodology to other venues or publication regimes without separate methodology; no remediation, fallback, exclusion, identity resolution or mutation is triggered.

**Gates:** A — source traceability, historical-date applicability and `UNKNOWN` behavior are technically validated. B — any user-facing population boundary and unresolved-calendar state are understandable. C — DFA confirms calendar-evidence semantics, diagnostic wording and conclusion level. D — PO accepts bounded scope.

## 12. INC-4 — Financial identity and evidence prerequisites

**State:** ACTIVE overall (broader financial-identity-adjudication question, unchanged). Two bounded capabilities closed within it: **`MatchCandidate → EvidenceSignal` (2026-09-01)** — A/C/D PASS-ACCEPT — and **manual financial-identity adjudication (`IdentityAdjudication`, 2026-09-01)** — A/B/C/D PASS-ACCEPT, below. — **Owner:** DFA + SE/SDT

**Established domain rule:** financial identity requires authoritative, temporally valid evidence sufficient for the identity question. Technical/provider signals may discover candidates and support evidence collection but cannot independently establish identity (SP-3). Missing, stale, contradictory or insufficient evidence produces `UNRESOLVED`.

**Constraints:** `automatic_resolution_enabled=False` is binding (SP-1); the compatibility states retain narrow provider/technical meaning (§7); current evidence cannot automatically establish historical identity; source count is not a substitute for authority, independence, or effective-date validity.

**Governing Tier 0/1/2 methodology (2026-09-01):** `TIER_0_1_2_3_FINANCIAL_IDENTITY_EVIDENCE_METHODOLOGY_REFERENCE_2026-09-01.md`, adopted per DFA's rulings (relayed by SE/PO) — resolves §1's own Tier 0/1/2 GAP row. Preserves the unrecoverable `docs/28` historical-provenance limitation rather than claiming it away; explicitly does **not** claim the shipped implementation already conforms to its own newly-incorporated authoritative-contradiction-resolution and disposition-specific-materiality rulings (each section names its own real gap). Tier 3 remains deferred/out of scope, unaffected.

**Gate C:** evidence may populate the identity pipeline only where doing so does not silently redefine Tier 0/1/2/3 methodology. Where the tiers cannot express a required evidence condition, record a specification gap for DFA/PO rather than stretching a tier.

### Gates A/C — `EvidenceSignal` capability: 1:N technical-evidence retention (2026-09-01)

**Scope of what passed, stated precisely — not the whole of INC-4, only this capability.** `MatchCandidate → EvidenceSignal`, the 1:N technical-signal-retention child, is implemented, independently conformance-reviewed, live-activated, and now DFA-confirmed to conform to the approved Tier 0/1/2 methodology. This does **not** mean INC-4 as a whole (identity adjudication, the broader "financial identity requires authoritative, temporally valid evidence" question above) is resolved — only that the evidence-retention *mechanism* conforms.

**Gate A — SDT-WB independent conformance review, cited as evidence: `613638a`.** Full detail there (twelve verified properties, five demonstration cases located and confirmed, full suite 1506/1506 at `histfints@a113456`). Not re-derived here.

**Gate C — DFA's ruling (2026-09-01), attributed to its actual owning authority.** Independently re-verified before recording, not taken on the relayed summary alone:

- **1:N capability implemented and verified**: unchanged from Gate A's own finding — re-confirmed still true at the current `histfints` HEAD.
- **Tier 0/1/2 evidence remains informational and non-adjudicative**: re-confirmed — zero `resolve_attach`/`resolve_group`/`resolve_merge`/`resolve_set_underlying` calls anywhere in `a113456` or the new `0a4893d` commit (grepped directly); `gather_evidence_for_candidate()`'s own docstring and its four dedicated tests confirm it never creates a candidate, never touches `evidence_tier`/`rule_reference`, never resolves.
- **Independence/derivative-lineage/contradiction/temporal-applicability/provenance semantics conform to DFA methodology**: re-confirmed against Gate A's own twelve-property and five-demonstration-case findings — unchanged, since neither `histfints` commit since Gate A touches `domain/evidence_signal.py`'s own rules.
- **Migration `0022` successfully activated live**: independently confirmed by direct query — live `histfints.db`'s `PRAGMA user_version=22` (was `21` at Gate A's own review), `evidence_signal` table now exists.
- **Bounded live gatherer run produced zero Tier 0/1/2 signals**: independently confirmed — `evidence_signal` table has **0 rows** live. Traced to why, not merely accepted: all 9 currently-unresolved `MatchCandidate` rows in the live database carry `evidence_tier=3` (originally Tier-3-only matches — their subject genuinely had no Tier 0/1/2 evidence when first discovered), and `gather_evidence_for_candidate()`'s own re-check against the same underlying data honestly finds the same nothing again — exactly the behavior `test_gather_evidence_for_candidate_never_creates_a_new_signal_when_tiers_0_1_2_all_still_miss` asserts. **This zero-signal result is methodologically correct, not a failure** — the alternative (fabricating a signal to show something happened) is precisely what this capability's own "never fabricates" guarantee (independently verified at Gate A) exists to prevent.
- **No real production Tier 0/1/2 signal has yet occurred**: confirmed by the same query — `evidence_signal` is empty. Preserved here as a standing note, not a defect: a future naturally-occurring Tier 0/1/2 case (a new Discover run against a subject with real identifier/normalized-identity evidence) will provide the first genuine real-data validation this capability has not yet had; nothing about this closure record should be read as substituting for that.
- **Tier 3 not validated or expanded**: re-confirmed — `0a4893d`'s diff touches only `catalog_discovery_service.py`/`cli.py`/tests; Tier 3's own matching logic is untouched, and `gather_evidence_for_candidate()` produces zero signals for a Tier-3-only candidate by design (the same test cited above).
- **Resolve/adjudication semantics unchanged**: re-confirmed live — the 4 already-resolved `MatchCandidate` rows in the live database are unchanged (same `resolution_operation`/`evidence_tier` values as before this work began); `entity_change_log` contains zero `MatchCandidate`-type entries, ever.

**Full suite re-confirmed at the current HEAD**: **1512 passed, 0 failed** (up from 1506 at Gate A's own review — 6 new tests for `gather_evidence_for_candidate()`).

**UIUX `055`, independently verified — confirmation only, not a manufactured gate.** Read in full: a bounded, read-only readiness assessment finding the existing Discover/Resolve UI contracts (`024`/`035`/`040`/`041`) already sufficient for a one-`MatchCandidate`-per-tier gatherer shape, no new UX specification needed for what `a113456`/`0a4893d` actually ship. **Independently confirmed no UI code was touched by either commit** (both diffs confined to `application`/`domain`/`persistence`/`composition_root.py`/`cli.py` — zero `presentation/templates/*.html` or `web.py` changes) — `055` is treated exactly as instructed: confirmation that no UI specification/runtime gate is currently required, not manufactured evidence of a validation that didn't need to happen.

### Gate D — PO acceptance (2026-09-01) — closure of this bounded capability only

Per PO's own direct instruction ("PO has ACCEPTED the bounded INC-4 `MatchCandidate → EvidenceSignal` capability"), attributed to its actual owning authority. Re-verified live before recording, no drift since Gate C: `histfints` `HEAD` still `0a4893d`, working tree clean except unrelated same-day BYMA evidence-collection output.

**Closure scope — stated explicitly, precisely as instructed, not implied.** This closes **only**:

- The Tier 0/1/2 `MatchCandidate → EvidenceSignal` retention/gathering capability itself (implementation, conformance, live activation) — not INC-4 as a whole.
- Individual supporting/contradictory/informative signals and the DFA-approved independence semantics (distinct upstream lineage + materially relevant assertion + compatible effective period; derivative/Tier-2 quantity exclusion) — all re-confirmed unchanged since Gate C, since no commit since then touches `domain/evidence_signal.py`.
- Migration `0022`'s live activation — re-confirmed unchanged (`PRAGMA user_version=22`, `evidence_signal` table present).

**It does not close, and this closure does not imply**:

- **Tier 3** — outside this closure entirely; unchanged, unvalidated, unexpanded by any part of this work.
- **Resolve/adjudication semantics** — unchanged; re-confirmed no `resolve_*` call exists anywhere in the closed capability's own code, and the 4 pre-existing resolved `MatchCandidate` rows remain byte-identical.
- **INC-4's broader financial-identity-adjudication question** — the "Established domain rule"/"Constraints" text above this section remains fully binding and unresolved; this closure narrows to the evidence-retention mechanism only, exactly as Gate C's own record already scoped it.
- **INC-12, INC-13, or INC-15** — none reopened; none of their own AC-* criteria concern this capability.
- **Any form of automatic identity resolution** — `automatic_resolution_enabled=False` (SP-1) remains fully binding; nothing in this closure loosens it.

**The "no real production signal yet" condition, preserved exactly as a standing note, not a reopening trigger.** `evidence_signal` remains empty in the live database (0 rows, re-confirmed) — no real production Tier 0/1/2 signal has naturally occurred yet. Per explicit instruction, **a future naturally-occurring case is additional real-data validation, not a condition whose absence blocks or whose future arrival reopens this closure by itself.** This closure accepts the *capability* (correctly implemented, correctly inert on today's data), not a claim that real-world evidence has already exercised it.

**No HistFinTS or `histfints_uiue` file modified by this closure record.**

### Gates A/B/C — manual financial-identity adjudication capability (2026-09-01)

**Scope of what this covers, stated precisely — a second, separate bounded capability inside INC-4, distinct from the `EvidenceSignal` capability closed above.** `IdentityAdjudication` (migration `0023`) is the human-adjudication layer sitting over `EvidenceSignal`, preserving the DFA methodological boundary exactly:

> `EvidenceSignals → human adjudication disposition → separately authorized catalog action`

**Gate A — technical: PASS.** SDT-WB independent conformance review, cited as evidence — full detail there, not re-derived here. Verified `histfints@103de84` (five-commit chain: backend → DFA temporal-applicability ruling + preview hook → Resolve UI integration → two runtime-defect fixes → AC-FID-04 disclosure fix) directly: own distinct `AdjudicatedDisposition` type (`SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT`/`UNRESOLVED` only, never cast to/from `FinancialIdentityConclusion`); append-only (frozen dataclass, no UPDATE/DELETE path anywhere in migration `0023`'s schema); every required field (relied/contradictory `EvidenceSignal` ids, reviewer, rationale, effective period, qualifications, `human_reviewer_attested`) enforced; missing material dimensions, authoritative contradiction, `UNKNOWN` applicability, incompatible periods, and an absent adjudication period all confirmed to block stronger dispositions, read directly in the shared `_validation_failures()` gate logic; `UNRESOLVED` exempt from every gate, never preselected (no `checked` attribute on any disposition radio); `preview_adjudication()` confirmed read-only (never calls `.save()`); zero `resolve_*`/`reverse_*`/`MatchCandidate.save()` calls anywhere in the adjudication code. Migration `0023` confirmed live (`PRAGMA user_version=23`), zero historical rows rewritten (unrelated live growth in `observation`/`import_run` independently traced and confirmed purely additive, not a rewrite, and structurally impossible for this capability to cause). Full suite **1609 passed, 0 failed**.

**Gate B — UIUX: application-level PASS, not fully discharged as of the prior record (2026-09-01, superseded below).** `056`–`060` read in full. All application-level defects found during validation are resolved: `057`'s two live-reproduced, root-caused defects (missing CSRF field blocking the confirm step entirely; `required_dimensions` never wired through from the web layer, silently disabling the missing-dimension/`UNKNOWN`-applicability/incompatible-period gates in production) both confirmed fixed and re-validated in `058`, via direct database query rather than UI text. `059`'s AC-FID-04 gap (the temporal-incompatibility disclosure existed at the domain layer but was never called from the web route) confirmed fixed and re-validated PASS in `060`, with an explicit regression check. AC-FID-17 (keyboard) confirmed PASS via real OS/UIA focus tracking. AC-FID-18 (screen-reader-legible grouping/state) confirmed PASS for every control captured before a genuine, disclosed NVDA/environment malfunction interrupted the pass — not glossed over, not rounded up. AC-FID-19/20 and one radio-announcement sub-check were, at that point, genuinely attempted, not confirmed.

### Gate B discharge — the NVDA/Speech Viewer investigation, and its resolution (2026-09-01, same day)

**Preserved as historical validation evidence, not rewritten**, per explicit instruction: the full investigation chain `061`–`067` (`histfints_uiue`), each read in full and independently cross-checked against real source/git state, not taken on summary.

- **`061`**: a real, genuine application defect found and reported — the confirm-page transition had no author-specified focus target, the one step in the flow missing it, freezing Speech Viewer 3/3 times under a confirmed exclusive, uncontended desktop (ruling out simple resource contention as the sole cause). The radio-announcement sub-check separately confirmed PASS this same pass.
- **`062`**: a narrow tooling diagnostic (not an INC-4 revalidation) — NVDA's own process/log showed no exception at the freeze point; a Speech Viewer display/output-window failure was the best-supported reading at the time, independent of the app.
- **`063`**: AC-FID-19 confirmed PASS with real fresh NVDA capture. AC-FID-20 (the confirm-step transition specifically) reproduced the freeze three times, including across two full recovery cycles — a real, reproducible pattern, root-cause not yet identified.
- **`064`**: RGC's focus-target fix (`histfints@40eae9e`, verified independently — real diff, confirmed by direct `git show`: wraps the confirm page's own `<h1>` and context paragraphs in `tabindex="-1" autofocus`, the same established mechanism `base.html`'s flash region already uses, applied directly since this success path emits no flash; five new regression tests confirm zero change to adjudication/catalog semantics; full suite grew to 1613 passed) was applied and tested — **the fix did not resolve the freeze**, reproduced identically three more times. Significant negative evidence: a well-reasoned, correctly-applied, evidence-backed fix made no observable difference, weighing toward a capture-tooling cause rather than an application one.
- **`065`**: the decisive diagnostic. The ad hoc capture method used throughout `057`–`064` (`AutomationElement.Current.Name`, never previously committed to the shared toolkit) was found to plateau at ~4096 characters against Speech Viewer's real `RICHEDIT50W`-backed control — the real underlying buffer, read directly via `WM_GETTEXTLENGTH`/`WM_GETTEXT`, was **demonstrably current and complete** (4280 real characters vs. 4096 reported) at the exact moment the old method reported a "freeze." **The Speech Viewer content was never actually frozen — the capture method used to observe it had a length ceiling.** Independently re-confirmed: `histfints@0a8377a` (the corresponding toolkit fix, `Get-SpeechViewerText`, committed to `.claude/skills/at-validation/` in the `histfints` repo — a tooling-only change, zero `src/` files touched, confirmed by direct `git show --stat`) matches this diagnostic's own root cause and corrected mechanism exactly.
- **`066`**: AC-FID-19/20 and the radio-announcement sub-check all re-confirmed **PASS** using the corrected capture tool — real, fresh NVDA output captured well past the old 4096-character boundary (growing to 9349 characters, no plateau), containing the complete confirm-step announcement (disposition, candidate, subject, and the explicit non-mutation guarantee). **One genuine documentation error in this same document, caught and independently re-confirmed here, not silently accepted**: `066` itself misstated `AC-FID-04` as "remains open, unaddressed by any fix to date" — independently checked against real source (current `histfints` HEAD) and found **false**: `_temporally_incompatible_ids()` and its "Temporal note" template output are present and wired exactly as `103de84`/`060` established: `git log 103de84..HEAD` touches zero files relevant to that fix.
- **`067`**: UIUX's own reconciliation, matching this record's independent finding exactly — acknowledges `066`'s AC-FID-04 error as a reporting oversight, confirms `060`'s PASS remains authoritative and current (same git-log check, independently reproduced here), and records Gate B as fully discharged.

**Gate B — now PASS, fully discharged, independently re-confirmed, not taken on `067`'s own claim alone.** Every `AC-FID-*` criterion: PASS. Full suite at current `histfints` HEAD (`0a8377a`): **1613 passed, 0 failed**. Migration `0023` unchanged (`PRAGMA user_version=23`); `identity_adjudication` table still 0 rows (no live adjudication has yet been recorded through the real UI — the recording tested in `058`/`066` used a disposable, seeded, now-deleted database, per every one of these documents' own explicit statement). The application-level focus-target defect (`061`, fixed `40eae9e`) and the capture-tooling defect (`065`, fixed `0a8377a`) are two genuinely distinct, both-real findings — neither cancels the other; both are preserved here as what they actually were, not retroactively merged into one story.

**Gate C — DFA: PASS.** Per SE relaying DFA's ruling, attributed to its actual owning authority. The methodological boundary — `EvidenceSignals → human adjudication disposition → separately authorized catalog action` — is confirmed structurally enforced, not merely asserted: `IdentityAdjudicationService` holds `MatchCandidateRepository` read-only, never calls any `ResolutionOperation`, and no catalog-mutation code path reads or writes an `IdentityAdjudication` row (independently re-confirmed as part of Gate A above, not re-derived separately here).

**Gate D — PO: PASS / ACCEPT (2026-09-01).** Per PO's own direct instruction, attributed to its actual owning authority.

**Overall: the manual-adjudication capability is CLOSED / ACCEPTED.** All four gates disposed (A/B/C/D). **Closure scope, stated explicitly, not implied**: this closes the bounded `IdentityAdjudication` capability — its DFA-approved gates, its append-only history mechanism, its UI, and its accessibility record. It does **not**: close INC-4 overall — the "Established domain rule"/"Constraints" text at the top of this section remains fully binding, and the broader financial-identity-adjudication question this increment names is not resolved by this closure; authorize automated adjudication of any kind — every recorded disposition to date has been, and every future one must be, a human's, per `human_reviewer_attested`'s own non-defaultable enforcement; authorize Tier 3 processing — Tier 3 remains completely outside every part of this capability, confirmed unchanged and unexpanded throughout; extend to the separate, on-hold G1/G9 `IdentityEvidenceEvaluator` capability — `057`'s own §0 boundary stands, unaffected; or reopen INC-12, INC-13, INC-15, or the already-closed `EvidenceSignal` sub-capability above.

**Evidence referenced, not rewritten**, per explicit instruction: the prior Gate A/C record above, the prior conformance review (`7248ffe`), and the full `061`–`067` chain all stand exactly as originally written — this closure adds only the discharge finding and the Gate D disposition.

**No HistFinTS or `histfints_uiue` file modified by this record.**

## 12a. INC-17 — `IdentityAdjudication` corrective increment — persisted plan/dependency state (2026-09-01, NEXT — not implemented, not accepted)

**Correction to a stale statement recorded at `8bcab60`, superseded and consolidated here.**
§20's own current-focus line for INC-4 previously stated "no SDT-HF task is currently justified."
That was accurate when written but became stale once DFA's subsequent ruling landed; corrected in
place there, and the full plan/dependency state is persisted here as the current record of record
for INC-17.

**The state, in dependency order, exactly as it stands:**

1. **The governing Tier 0/1/2 methodology is established.**
   `TIER_0_1_2_3_FINANCIAL_IDENTITY_EVIDENCE_METHODOLOGY_REFERENCE_2026-09-01.md`, adopted
   `8bcab60`, resolves §1's own Tier 0/1/2 GAP row (Tier 3 remains deferred, unaffected).
2. **DFA subsequently identified canonical persisted semantics for two areas** — case-specific
   materiality and authoritative-contradiction resolution — that the adopted methodology names but
   the shipped mechanism does not yet record as its own persisted fact. Ruled by DFA, relayed by
   SE/PO; incorporated into the governing reference at §6b (authoritative-contradiction
   resolution: the four evidentiary acts, the explicit non-resolving mechanisms, required
   preservation) and §7b/§7c (the case-specific material identity dimension rule;
   disposition-specific `SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT` conditions).
3. **A read-only HistFinTS assessment confirmed both as real implementation gaps** — not
   theoretical, not newly invented here. Performed while adopting the governing reference (`8bcab60`):
   the shipped `web.py`'s `_adjudication_form_state()` derives `required_dimensions` fresh, per
   request, from whatever the candidate's evidence happens to touch — it does not persist, as its
   own recorded fact, *which* dimensions were determined material for a *specific* recorded
   adjudication, and does not yet distinguish a `SAME_INSTRUMENT`-shaped materiality question from
   a `RELATED_BUT_DISTINCT`-shaped one (gap 1, reference §7b/§7c). The shipped
   `diagnose()`/`_validation_failures()` code detects an authoritative contradiction as a flat
   boolean and blocks on it, with no mechanism to record which of the four DFA-ruled resolution
   acts applies, no record type for a correction/supersession assertion distinct from an ordinary
   signal, and no authority-precedence table anywhere in the codebase (gap 2, reference §6b). Both
   confirmed by direct source reading, read-only — no HistFinTS file modified to reach this
   finding.
4. **The previously accepted manual-adjudication capability remains historically CLOSED/
   ACCEPTED.** §12's own closure record above (Gates A/B/C/D, all PASS-ACCEPT) is unedited by this
   section — not silently reopened. This increment is a *new*, separate, corrective piece of work
   responding to a *later* DFA ruling, the same posture INC-6's Finnhub boundary condition and
   INC-4's own `EvidenceSignal`-then-`IdentityAdjudication` sequencing already established: a
   closure records what was true and accepted at that time; a subsequent ruling can justify new,
   separately-gated work without retroactively undoing the earlier acceptance.
5. **A new bounded corrective increment (INC-17) is now in technical-design stage.** Not
   implemented; not accepted. Scope is exactly the two gaps named in item 3, nothing broader.
6. **SDT-HF is currently tasked with producing that design before implementation** — per SE/PO's
   own direct instruction, recorded here as the current task assignment, not decided or assigned
   by SDT-WB. SDT-WB does not produce the technical design (SDT-HF's own repository and
   ownership); this record establishes and preserves the justification and the two gaps the design
   must address, nothing more.
7. **Real production adjudication remains separately blocked by the absence of naturally-occurring
   Tier 0/1/2 `EvidenceSignal`s.** `evidence_signal`: 0 rows, live-confirmed at closure and
   unchanged since. This is a **separate** block, unrelated to and not itself blocking INC-17's
   design/implementation — the two named gaps exist in the mechanism itself, checkable and fixable
   independent of whether any real candidate has yet exercised it.

**Dependency order, preserved exactly as instructed:**

> Governing methodology (1) → DFA's canonical-semantics ruling (2) → read-only gap confirmation
> (3) → SDT-HF technical design (5–6, current stage) → PO/DFA domain-ambiguity check → UIUX
> contract → implementation.

Items 4 and 7 sit outside this dependency chain, stated as standing, unaffected facts — the prior
closure (4) is not a step this chain revisits, and the production-evidence block (7) does not gate
any step in it.

**State: NEXT.** Not implemented; not accepted. No HistFinTS or `histfints_uiue` file modified by
this record.

## 12b. DFA's ruling on INC-17's §7 boundary question — the candidate-context completeness rule (2026-09-01)

**Context, verified directly before recording.** SDT-HF's own technical design
(`histfints@cf5463a`, `docs/future_designs/INC17_CORRECTIVE_INCREMENT_DESIGN.md`, read in full)
named one concrete, unresolved boundary question at its own §7: for an identity dimension no
Tier 0/1/2 gatherer has ever produced evidence for on a given candidate, does materiality review
require (a) an explicit determination against a fixed, DFA-defined taxonomy regardless of gathered
evidence, or (b) stay strictly scoped to gathered evidence, with an ungathered dimension simply out
of scope? The design explicitly declined to choose, stating engineering cannot resolve it without
inventing financial-methodology taxonomy.

**DFA's ruling, relayed by SE/PO, settles this — as a synthesis, not a literal pick of (a) or
(b):**

- **Case-specific relevant-dimension inventory.** The set of dimensions requiring an explicit
  materiality determination for a given adjudication is derived from **governing identity
  taxonomy plus financially typed candidate context** together — neither a single fixed list
  applied uniformly to every candidate (pure option (a)) nor a set limited to whatever a gatherer
  happened to produce (pure option (b)). A CEDEAR-vs-underlying candidate's own financially typed
  context pulls in dimensions (e.g. settlement) the governing taxonomy names as relevant to that
  candidate *type*, whether or not a Tier 0/1/2 gatherer has produced evidence for them yet.
- **Candidate context discovers, it does not establish.** The financially typed candidate context
  that expands the relevant-dimension inventory beyond gathered evidence is itself only a
  discovery mechanism — it identifies which dimensions are *potentially* relevant for a candidate
  of that type. It does **not** itself constitute authoritative evidence for or against any
  dimension; it only says which dimensions must be explicitly ruled on.
- **Every relevant dimension must be explicitly `MATERIAL` or `NON_MATERIAL`.** No relevant
  dimension may be left un-ruled-on — silence is not a valid third state.
- **`NON_MATERIAL` requires reviewer rationale.** Matches the design's own already-specified
  `DimensionMateriality.__post_init__` requirement (`cf5463a` §1) — confirmed consistent, not a
  new constraint the design lacked.
- **Every `MATERIAL` dimension must satisfy evidence, temporal-applicability, and contradiction
  rules** — the existing gates (§7a/§8/§6 of the governing reference) apply to every dimension
  ruled `MATERIAL`, regardless of whether that dimension came from gathered evidence or from the
  taxonomy-plus-context inventory.
- **Evidence presence/absence alone cannot define the inventory or materiality.** Directly settles
  the design's own §7 framing: gathered-evidence presence is not sufficient to define the full
  relevant-dimension set (rules out pure option (b) as the complete answer), and evidence *absence*
  does not itself make a dimension `NON_MATERIAL` either — a taxonomy-identified dimension with no
  gathered evidence must still be explicitly ruled on, most likely blocking a stronger disposition
  until it is (consistent with, and extending, DFA-D03's own "not a substitute for authority"
  framing already compiled in the governing reference).
- **Inability to establish relevant-set completeness forces `UNRESOLVED`.** If the governing
  taxonomy or the candidate's financial typing cannot be established with enough confidence to
  determine the full relevant-dimension inventory for a given candidate, the honest outcome is
  `UNRESOLVED` — the same "missing evidence cannot be worked around" discipline already governing
  every other gate in this methodology, applied here to inventory-completeness itself rather than
  to any one dimension's own evidence.

**DFA could not inspect the literal §7 option labels — recorded explicitly, not glossed over.**
DFA does not read `histfints` source directly (per this project's own actor-model routing); the
ruling above answers the underlying methodological question DFA was actually asked, not a literal
selection between SDT-HF's own internally-labeled options (a)/(b). **SDT-HF is now mapping this
ruling against the actual persisted design (`cf5463a`) before UIUX work begins** — determining
precisely how "governing identity taxonomy plus financially typed candidate context" cashes out
against the design's own `candidate_context_dimensions` completeness check (§3.1) and
`materiality_determinations` structure (§1), which is engineering/design work this record does not
do or anticipate on SDT-HF's behalf.

**Dependency order — corrected 2026-09-01 (was recorded too strongly at `a3ebe70`: a second
DFA/PO review was stated as an unconditional next step; it is conditional, not mandatory).**

> DFA §7 ruling (this record) → SDT-HF design mapping/finalization (current step, not yet done) →
> **conditional** DFA/PO clarification, **only if** SDT-HF's mapping identifies a remaining
> domain/product ambiguity the ruling does not settle → UIUX contract → implementation →
> validation.

If SDT-HF reports that the ruling fully settles the design boundary, the conditional step does
not occur — the sequence proceeds directly from SDT-HF's design finalization to the UIUX contract,
with no second DFA/PO review implied as mandatory.

**State: the boundary question is DFA-ruled; the design mapping against it is not yet done.** Not
implemented; not accepted; does not itself change the persisted design document, which remains
SDT-HF's to update. No HistFinTS or `histfints_uiue` file modified by this record.

**Preserved as history, not rewritten**: the paragraph above accurately describes the state as of
`a3ebe70`/`f23bcbe`. §12c below records the current, later stage — it does not edit this section.

## 12c. SDT-HF design finalization complete (`histfints@2f1da5a`) — UIUX contract stage now open (2026-09-02)

**Verified directly before recording, not taken on the relayed summary.** `histfints@2f1da5a`
("INC-17: apply DFA's §7 ruling to the corrective-increment design"), read in full: `HEAD` matches
(one later commit, `b661058`, is an unrelated operational checkpoint about Daily Import timing, not
INC-17 substance). `docs/future_designs/INC17_CORRECTIVE_INCREMENT_DESIGN.md`'s own header now
reads: *"§7's boundary question has been ruled on by DFA and this revision applies that ruling
directly... the boundary question itself is closed."* No production code changed; `histfints_uiue`
untouched.

- **DFA §7 methodology ruling — COMPLETE.** Unchanged from §12b, restated here as the first
  fixed point in the now-current chain.
- **SDT-HF design mapping/finalization — COMPLETE at `2f1da5a`.** §7 was **rewritten**, not
  approximated to either of the design's own original alternatives — confirmed directly: the
  design's own text states neither (a) fixed-taxonomy-always-material nor (b) scoped-strictly-to-
  gathered-evidence matches DFA's ruling, so the section states the actual third rule directly
  rather than forcing it into either label.
- **The mechanism is now settled, verified against the design's own §7/§1a**: the relevant-
  dimension inventory for a candidate is the **union** of (i) every dimension the candidate's
  gathered `EvidenceSignal`s touch and (ii) every dimension mechanically discoverable from the
  candidate's own financially-typed context fields (a new `CONTEXT_DIMENSION_TRIGGERS` table,
  §1a) — regardless of whether evidence was ever gathered for it. **Context discovers questions,
  never supplies evidence**: confirmed structurally, not merely stated — the design's own
  `discover_candidate_context_dimensions()` returns `frozenset[str]` (dimension *names* only),
  never an `EvidenceSignal`, with no code path by which its output could be passed as
  `relied_upon_signal_ids` or otherwise satisfy a dimension. The design's own table (§7) draws the
  line precisely: deterministic discovery reads only whether a typed field **is populated**, never
  its *value* — a field's actual value is never read to infer materiality, only its presence, to
  decide whether a dimension needs asking about at all.
- **One narrow DFA confirmation remains open — confirmed genuinely narrow, not a re-litigation
  of the mechanism**: whether the proposed finite `CONTEXT_DIMENSION_TRIGGERS` field→dimension
  table (built from this project's own already-existing typed fields — `Series.currency`/
  `country`/`instrument_subtype`/`settlement_mechanism`/`underlying_series_id`,
  `ProviderSymbol.currency`/`settlement_mechanism`/`venue`/`share_class`/`security_type`) is
  complete against DFA's own understanding of the governing financial taxonomy. The design's own
  text states this explicitly: a confirm-or-amend question against a concrete, finite table, not
  an open design question.
- **UIUX contract drafting is now authorized and may proceed independently, in parallel** — the
  design's own §9 states "ready for the UIUX contract stage," with the trigger-table confirmation
  named as proceeding in parallel, not gating it, "since it changes only the *contents* of a
  lookup table, not the mechanism, persistence shape, or service API documented here."
- **Production implementation is not yet authorized** — the design's own §9, verbatim: "Nothing in
  this document authorizes starting implementation yet." Depends on **both** the completed UIUX
  contract **and** the DFA trigger-map confirmation.
- **Real production adjudication remains separately blocked by the absence of naturally-occurring
  Tier 0/1/2 `EvidenceSignal`s** — unchanged from every prior record in this chain; live row
  counts re-verified by the design document itself at `2f1da5a`'s own writing (still 0/0/0),
  unrelated to and not blocking any step above.

**Dependency line, updated:**

> DFA §7 ruling ✓ → SDT-HF design finalization ✓ → **[UIUX contract || DFA trigger-map
> confirmation]** → implementation → validation.

The two bracketed items are independent and run in parallel, not sequentially — neither blocks the
other, and both must complete before implementation is authorized.

**For the other actors, no new instruction is needed yet, per explicit note**: SDT-HF should
return the extracted trigger table; UIUX should return the INC-17 contract.

**State: NEXT — design finalized, two parallel tracks open, neither complete.** Not implemented;
not accepted. No HistFinTS or `histfints_uiue` file modified by this record.

## 13. INC-5 — Corporate-action and economic-event evidence

**State:** the live Yahoo/FRED provider-event capture capability: **CLOSED/ACCEPTED (2026-09-01).** Gate disposition: A — PASS. C — PASS (DFA). D — ACCEPT (PO, below). Gate B remains deferred to first user-facing surface (unchanged). — **Owner:** SE/SDT + DFA — **Source:** `REQUEST-event-capture.md`

**Financial question:** what externally reported event evidence exists, for which Series and effective period, and how far may it support reconciliation of observed time-series behavior?

**Required evidence:** provider/run provenance; the reported event as distinct from any reconciled fact; effective dates and historical applicability.

**Legitimate conclusion:** "an event was reported by provider X, effective date Y, captured in run Z." Nothing stronger.

**Prohibited:** SP-7, SP-9.

**Gates:** A — provenance is queryable for every captured event. C — DFA confirms stored fields and any wording keep reported evidence distinct from reconciled fact. B/D — on first user-facing surface.

### Gates A/C — wiring fix + live event capture (2026-09-01)

**Gate A — SDT-WB independent conformance review of `histfints@5eafe66` and the live database.** Verified directly, not taken on the relayed summary. `HEAD` matches, working tree clean except unrelated same-day BYMA evidence-collection output. Full suite **1518 passed, 0 failed**, matching the reported count exactly.

**Wiring fix confirmed delegation-only.** The diff is exactly one production file, `providers/retry.py`: a single `__getattr__` method delegating any attribute `RetryingProviderClient` doesn't itself define straight to the wrapped client. Read the method and its docstring in full — `fetch()` (the only retry-wrapped method) is unaffected, since `__getattr__` is only ever consulted after normal attribute lookup fails; a dedicated test (`test_getattr_delegation_does_not_retry_a_retryable_error`) independently proves a delegated method's own error is **not** retried (`sleeps == []`), confirming retry policy is genuinely unchanged, not merely claimed. **Zero other production files touched** by this commit (confirmed by `git show --stat`: `retry.py` plus two test files only) — structurally confirms event semantics, provider selection, Series identity, and historical-observation code are all untouched by construction, not merely by inspection.

**The original failed zero-event attempt correctly diagnosed as an execution failure, not evidence.** Confirmed: the pre-fix `AttributeError` was raised and caught *before* either capture service's own event-construction/save loop ever ran (read both `yahoo_event_capture_service.py` and `fred_event_capture_service.py` in full — the `try/except` wraps only the provider-client call itself, returning `[]` immediately on any exception) — no spurious `ProviderEvent` row was ever created from the failed attempt, and no workbench record (`DECISIONS.md`/`ACTION_PLAN.md`, checked directly) ever characterized that prior silent-empty result as genuine capture evidence. The commit's own message states this correctly ("silently reported as 'no events found,' indistinguishable from a genuine empty result... Confirmed live") — a defect diagnosis, not evidence.

**Live capture results independently confirmed via direct SQL against `histfints.db`**: `provider_event` totals **859 rows exactly** — `4` `SPLIT` + `57` `DIVIDEND` (both `series_id=33`, "Apple Inc. — Common Stock," provider Yahoo Finance) + `798` `REVISION` (`series_id=1`, "US Unemployment Rate," provider FRED). Types explicitly distinguishable at the schema level (`event_type` column, `CHECK`-documented as `SPLIT, DIVIDEND, REVISION, CORPORATE_ACTION, OTHER`) and by provider (`provider_id`), never conflated.

**Row-level traceability, checked field by field on real sample rows**: `provider_id` (provider/source), `series_id` (relevant Series), `event_date` (real-world effective date), `acquired_at` (capture timestamp), `provider_source_id` (the provider's own identifier for the event), `structured_data` (the retained provider representation as JSON, e.g. `{"numerator": 2.0, "denominator": 1.0, "source": "Yahoo Finance chart API", "symbol": "AAPL"}`), and `provenance_note` (human-readable source description). **One nuance worth naming precisely, not glossed over**: there is no dedicated capture-run entity/FK (`provider_event` has no `import_run_id`-equivalent column) — "captured in run Z" (this section's own "Legitimate conclusion" wording) is reconstructible via `acquired_at`, since every event from one `capture_events_for_series()` call shares the exact same timestamp (confirmed: all AAPL split/dividend rows share one `acquired_at`; all FRED revision rows share a distinct, later one) — a real, working traceability mechanism, but an implicit one via shared timestamp rather than an explicit run-id relationship. Not treated as a blocking gap, since row-level traceability is genuinely complete without it, but stated precisely rather than claimed as identical to `ImportRun`'s own explicit FK pattern.

**No historical observations/import runs rewritten — confirmed structurally and by exact figures.** `observation` (28,062,084 rows) and `import_run` (222,654 rows) both show the **identical** counts and `max(updated_at)` (13:23:51/13:24:05, both 2026-09-01) as every prior check this session — both timestamps **predate** this event-capture work (18:13) entirely. `entity_change_log` unchanged (`Provider` 12, `ProviderAssignment` 1, `ProviderSymbol` 2 — no new rows of any type).

**Evidence-only boundary confirmed by reading both capture services in full**: neither `yahoo_event_capture_service.py` nor `fred_event_capture_service.py` references `Observation`, performs reconciliation, historical price repair, causal attribution, comparability judgment, or any corporate-action adjudication anywhere (grepped directly — zero matches) — each does exactly three things: fetch, de-duplicate against already-captured events for the same series/date/type, and save a new, immutable `ProviderEvent` row.

**Gate C — DFA's confirmation (2026-09-01), attributed to its actual owning authority.** Re-verified before recording, not taken on the relayed ruling alone: the stored fields (`event_type`, `structured_data`, `provenance_note`) and this section's own "Legitimate conclusion" wording ("an event was reported by provider X... Nothing stronger") are structurally incapable of asserting anything beyond a reported fact — no adjustment-correctness field, no comparability field, no causal-attribution field, no adjudication field exists anywhere in `provider_event`'s schema (confirmed by reading the full `CREATE TABLE` statement).

**Methodological boundary, preserved exactly, per instruction:** provider event capture establishes reported external evidence; it does not establish adjustment correctness, cross-provider comparability, causal explanation of price discontinuities, historical price repair, or automatic corporate-action adjudication. Confirmed true of the actual implementation, not merely restated as policy.

### Gate D — PO acceptance (2026-09-01) — closure of the bounded capture capability

Per PO's own direct instruction ("PO has ACCEPTED INC-5 — provider-reported event capture for the bounded evidence-capture scope"), attributed to its actual owning authority. Re-verified live before recording, no drift since Gate C: `histfints` `HEAD` still `5eafe66`, working tree clean except unrelated same-day BYMA evidence-collection output; `provider_event` still exactly **859 rows**.

**Closure scope — stated explicitly, precisely as instructed, not implied.** This closes the live Yahoo/FRED provider-event capture capability itself (the wiring fix, its delegation-only mechanism, and the resulting real captured evidence). It preserves, unchanged from Gates A/C's own findings, not restated more strongly:

- **859 real captured events preserved as operational evidence** — 4 `SPLIT` + 57 `DIVIDEND` (Apple Inc.) + 798 `REVISION` (US Unemployment Rate), re-confirmed unchanged at closure.
- **Provider events remain evidence-only** — does **not** establish adjustment correctness, cross-provider comparability, causal explanation of price discontinuities, historical price repair, or automatic corporate-action adjudication. Confirmed true of `provider_event`'s own schema (Gate A), not merely asserted as policy.
- **The capture-run provenance limitation preserved exactly, not smoothed over**: capture-run identity is reconstructible through the shared `acquired_at` timestamp per capture call, **not** a dedicated capture-run FK/entity — this remains explicitly **not equivalent** to `ImportRun`'s own explicit-FK provenance pattern, stated as precisely at closure as it was at Gate A.
- **The original zero-event attempt preserved as a failed execution caused by the wiring defect, not as evidence** — the pre-fix `AttributeError` was caught before either capture service's save loop ever ran; no spurious row was ever created from it.
- **The wiring fix's delegation-only nature and unchanged retry semantics preserved exactly** — `fetch()` remains the only retry-wrapped method; a delegated method's own error is not retried, independently proven by its own dedicated test.

**It does not**: broaden into cross-provider comparability, causal attribution, historical price repair, or any adjudication capability; extend to any other increment; or reopen INC-12, INC-13, INC-15, or INC-4's own bounded `EvidenceSignal` closure.

**Gate A's and Gate C's own records above are unedited by this closure** — this section only adds the Gate D disposition and this closure-scope statement.

**No HistFinTS or `histfints_uiue` file modified by this closure record.**

## 14. INC-6 — Adjustment basis and historical coverage

**State:** CLOSED/ACCEPTED — **Gate disposition:** A — PASS. C — PASS (DFA). D — ACCEPT (PO, 2026-09-01, below). **Owner:** SE/SDT + DFA — **Source:** `REQUEST-tranche2-migration.md`

**Financial question:** is the stored history sufficiently complete and comparable for the intended analysis, or does apparent absence reflect Series existence, provider assignment, provider availability, incomplete acquisition, or another unresolved cause?

**Required evidence** (where applicable): provider-assignment effective periods; provider availability/coverage; stored observation coverage; adjustment basis; corporate-action context; provenance and missing-data state.

**Domain constraint:** existence is not analytical eligibility; incomplete coverage is not automatically invalid data; absence of an observation is not proof of non-existence.

**Prohibited:** SP-4, SP-8.

**Gate C:** for each consuming analysis, DFA confirms the coverage evidence answers that analysis's comparability question; unresolved causes remain visibly unresolved (UP-3).

### Gate A — SDT-WB independent conformance review (2026-09-01)

Verified `histfints@fe17b39` and the live database directly, not taken on the relayed summary. `HEAD` matches; working tree clean except unrelated same-day BYMA evidence-collection output. Full suite **1485 passed, 0 failed** — matching the reported count exactly. Three commits reviewed in sequence: `f8d273b` (new `Provider.adjustment_basis_evidence` column, migration `0021`; `set_adjustment_basis()`/`correct_provider_series_identifier()`-style narrow write; applied live once), `01af3b6` (regression coverage for the write path and the three-state invariant), `fe17b39` (doc-only correction of `DATABASE_SCHEMA.md`'s inventory after a live corrective write moved BYMA from an initially-recorded `UNKNOWN` to `NOT_APPLICABLE`).

**1. Technical/model conformance — PASS.** Live database (`provider` table, all 7 rows) confirmed directly by SQL query: `FRED=NOT_APPLICABLE`, `Yahoo Finance=SPLIT_ADJUSTED`, `BYMA=NOT_APPLICABLE`, `Finnhub=NULL`, `Twelve Data=NULL`, `MERVAL=UNKNOWN`, `BYMA EOD=UNKNOWN` — the complete 7-provider inventory, every value matching the task's stated targets exactly. The `AdjustmentBasis` enum (`provider.py`) keeps `RAW`/`SPLIT_ADJUSTED`/`SPLIT_AND_DIVIDEND_ADJUSTED`/`NOT_APPLICABLE`/`UNKNOWN` as five distinct real values, with Python `None`/SQL `NULL` as a sixth, structurally separate "no assertion" state — confirmed the three DFA-relevant states (`NULL`/`UNKNOWN`/`NOT_APPLICABLE`) never collapse, both in source (a domain-level test added in `01af3b6` asserts this) and in the live data (Finnhub/Twelve Data genuinely `NULL`, not a string "UNKNOWN"; MERVAL/BYMA EOD genuinely the enum value `UNKNOWN`, not `NULL`; BYMA/FRED genuinely `NOT_APPLICABLE`).

**2. Evidence provenance — PASS.** `entity_change_log` (`entity_type='Provider'`, 10 rows, `id` 4–13) is fully auditable: FRED/Yahoo each got one `adjustment_basis_evidence`-only write (no value change — an established value gaining its supporting citation, not being altered); BYMA shows a genuine two-step corrective history preserved in full (`RAW→UNKNOWN` with its own evidence text, then `UNKNOWN→NOT_APPLICABLE` with a second evidence text explicitly stating it "supersedes the 2026-09-01 UNKNOWN write" — neither step overwritten or deleted, both reconstructible); MERVAL and BYMA EOD each show one `NULL→UNKNOWN` write with a citation of the real code review performed and its negative result. Every `adjustment_basis_evidence` value read live is substantive, checkable text (specific files checked, specific reasoning, specific observation/run counts as of the review date), not a placeholder. `docs/DATABASE_SCHEMA.md`'s own inventory (`fe17b39`) matches the live data exactly, corrected once to remove a transient mismatch rather than left stale.

**3. No historical rows rewritten — PASS, confirmed structurally, not by claim.** `entity_change_log` contains zero `Observation`- or `ImportRun`-type entries, ever (grouped-count query across the full table: `Provider` 10, `ProviderAssignment` 1 — the unrelated, separately-verified `BF.A→BF-A` fix — `ProviderSymbol` 2, nothing else). `observation`'s and `import_run`'s own `max(updated_at)` (13:23:51 and 13:24:05 respectively) both **predate** the INC-6 corrective writes (15:20:03–15:35:38) — neither table has been touched since before this work began. `provider_assignment.adjustment_basis_override`: 0 of 11,467 rows non-`NULL`, matching `f8d273b`'s own claim exactly.

**4. Financial-domain correctness — NOT evaluated here, explicitly deferred to DFA.** Whether `NOT_APPLICABLE` is the financially correct classification for BYMA (vs. e.g. treating a never-successfully-invoked adapter differently), whether `UNKNOWN` is the correct disposition for MERVAL/BYMA EOD rather than a specific basis being derivable from further review, and whether the underlying evidence texts themselves meet DFA's own bar for "established" are financial-methodology questions this review does not adjudicate — Gate C's own question, unchanged. This review confirms the *model and mechanism* conform to the DFA `NULL`/`UNKNOWN`/`NOT_APPLICABLE` semantics as already encoded in the domain layer; it does not confirm the specific classifications are the financially correct ones.

**UIUX state (`histfints_uiue` `054`/`2dbb923`), independently verified**: `054` read in full — a read-only, state-generic UX assessment (AC-INC6-01–05) against no live surface; HistFinTS's web UI has no adjustment-basis column anywhere (`series.html`, `import_history.html` both confirmed not to render it), and Workbench has no HTML templates at all. `2dbb923` re-confirms `054` covers the finalized inventory without needing a rewrite (its criteria are state-generic, not tied to provider names) and explicitly records that no live UI/NVDA gate exists or applies yet — matching this review's own independent check exactly. `054` remains a future presentation contract only.

**Scope discipline, confirmed not exceeded**: this review and the underlying implementation do not touch cross-provider comparability, do not rewrite or reinterpret any Observation, and do not perform or claim any corporate-action analysis — none of `f8d273b`/`01af3b6`/`fe17b39` touches `data_constraints.py`, `panel.py`, or any comparability/reconciliation logic (confirmed by their own diffs, all confined to `Provider`/`AdjustmentBasis` and its evidence field).

### Gate C — DFA re-evaluation of the finalized inventory (2026-09-01)

Per SE relaying DFA's own re-evaluation, attributed to its actual owning authority, consistent with this project's standing practice. **Finalized, DFA-confirmed 7-provider inventory**: `FRED=NOT_APPLICABLE`, `Yahoo Finance=SPLIT_ADJUSTED`, `BYMA=NOT_APPLICABLE`, `Finnhub=NULL`, `Twelve Data=UNKNOWN`, `MERVAL=UNKNOWN`, `BYMA EOD=UNKNOWN`. **Independently re-verified against the live database before recording**, not taken on the relayed inventory alone — one value had changed since Gate A's own review (`Twelve Data`: `NULL` → `UNKNOWN`, a new live write, `histfints@5619399`/`8a77de6`, full suite now **1486 passed, 0 failed**): live query confirms all seven values exactly as stated above; `entity_change_log` (`entity_type='Provider'`, now 12 rows) gained one new, substantive `NULL→UNKNOWN` write for Twelve Data, citing its 161 `SUCCESS` import runs and `import_service.py`'s own FR-11 dedup rule as the reason 0 observations are directly attributable to those runs despite genuine successful fetches (priority 2–3, suppressed by an already-current identical value from a higher-priority provider — a real, reviewed, observation-producing path, correctly `UNKNOWN` not `NULL`, per the same evidence bar already applied to MERVAL/BYMA EOD). No historical row rewritten by this additional write either — `entity_change_log` still contains zero `Observation`/`ImportRun` entries ever, and `adjustment_basis_override` remains 0-of-11,467.

**Finnhub's `NULL` boundary condition — preserved exactly, not weakened.** `NULL` is DFA-conforming for Finnhub only because, and only while, it has zero successful stored observations — independently confirmed live: 23 `FAILED` import runs, 0 `SUCCESS`, all-time. This is a **live-data condition, not a permanent classification**: the first time Finnhub produces a real `SUCCESS` run with a stored `Observation`, it moves into the same observation-producing/evidence-review class Twelve Data was just placed in, and its `adjustment_basis` must then be resolved to an established value or `UNKNOWN` — it may no longer sit at `NULL` at that point. No code enforces this transition automatically (confirmed: `docs/DATABASE_SCHEMA.md`'s own `5619399` text states this explicitly) — it is a documented rule for whoever next reviews Finnhub's state, not a pre-emptive live-data write against its current, unchanged, all-failure history. This boundary condition is recorded here as a standing note for any future review of Finnhub's provider row, not merely restated once and forgotten.

**UIUX state, re-confirmed unchanged.** `histfints_uiue` `054`/`2dbb923` still describe a state-generic contract (AC-INC6-01–05) that covers the finalized inventory, including Twelve Data's new value, without needing a rewrite — neither document names specific providers in its acceptance criteria. No live UI surface exists in either application; no NVDA/runtime validation gate applies at this data-model-only stage. `054` remains the future presentation contract only.

**Scope discipline, re-confirmed at this pass.** Neither `5619399` (docs-only) nor `8a77de6` (test-only) touches comparability, splicing, corporate-action logic, or any UI code — confirmed by their own diffs.

### Gate D — PO acceptance (2026-09-01) — final closure

Per PO's own direct instruction ("PO has ACCEPTED INC-6"), attributed to its actual owning authority. Re-verified live before recording (no drift since Gate C): `histfints` `HEAD` still `5619399`, working tree clean except unrelated same-day BYMA evidence-collection output. **Finalized inventory, preserved exactly, re-confirmed live one final time**: `FRED=NOT_APPLICABLE`, `Yahoo Finance=SPLIT_ADJUSTED`, `BYMA=NOT_APPLICABLE`, `Finnhub=NULL`, `Twelve Data=UNKNOWN`, `MERVAL=UNKNOWN`, `BYMA EOD=UNKNOWN`.

**Closure scope — stated explicitly, not implied.** This closes only the technical/model conformance and DFA-confirmed classification of the provider-level `adjustment_basis` field for these seven providers, per Gates A/C's own findings above. It does **not**: reopen or extend into cross-provider comparability, historical splicing, corporate-action correctness, or any UI implementation — none of those was in scope for either gate and none is authorized by this closure; extend to any other increment; or retroactively validate any Series/analysis that consumes this field — each consuming analysis still requires its own DFA confirmation that the coverage evidence answers *that* analysis's comparability question, per this section's own pre-existing Gate C rule (unchanged, still binding).

**Finnhub's `NULL` boundary condition — preserved as a standing, binding note, surviving this closure unchanged.** `NULL` remains DFA-conforming for Finnhub only while it has zero successful stored observations (23 `FAILED`, 0 `SUCCESS`, all-time, as last confirmed). The first real `SUCCESS` run with a stored `Observation` moves Finnhub into the same observation-producing/evidence-review class as Twelve Data/MERVAL/BYMA EOD, requiring its `adjustment_basis` to be resolved to an established value or `UNKNOWN` — never a continued `NULL` at that point. This condition is **not** closed or discharged by INC-6's acceptance; it remains open and applicable for whoever next reviews Finnhub's provider row, for as long as Finnhub's own observation history stays empty.

**Evidence chain preserved exactly, not altered**: Gate A's and Gate C's own records above (including the Twelve Data re-verification and the full `entity_change_log` audit trail) are unedited by this closure — this section only adds the Gate D disposition and the closure-scope statement.

**No HistFinTS or `histfints_uiue` file modified by this closure record.**

## 15. INC-7 — Core Workbench research capability

**State:** BLOCKED per-analysis — **Owner:** DFA → SE/SDT + UIUX — **Source:** `SPEC-panel-eligibility.md`

**Scope:** the primary analytical workflows, each unblocked by its own evidence prerequisites. Current directions: CEDEAR / foreign-underlying implied-FX panel; ordinary Series comparison and diagnostics. Each follows the analytical sequence (§1).

**Panel constraints** (summary only — `SPEC-panel-eligibility.md` governs): staleness is analysis-specific for contemporaneous comparisons; a local quality problem need not invalidate an entire Series; affected spans may be quarantined where the governing methodology establishes that treatment; aggregate suppression withholds the aggregate while retaining useful diagnostics; dispersion uses an economically meaningful normalized measure, not raw price-level CV; calibration populations require verified identity, representativeness, independence considerations, and sufficient temporal/regime diversity.

**Calibration boundary:** the current CEDEAR calibration population is **not** established while shared-driver / non-independence or insufficient temporal/regime diversity remains unresolved.

**Conclusion boundary:** a calculation is not a research conclusion; a research conclusion is not investor-specific advice or a trade decision (SP-11).

## 16. INC-8, INC-9, INC-14 — UIUX programme

**INC-8 — Screen-by-screen expansion. CONTINUOUS**, dependency-driven, no longer globally deferred. Per screen: **audit → DFA/PO decision gate where needed → UX specification → implementation → four-gate validation**. Prioritize by product value and dependency readiness.

**Screen-level IA is continuous.** Each screen increment validates page purpose, relationship to neighboring workflows, object terminology, hand-offs, and whether navigation labels express task boundaries accurately.

**INC-9 — Workbench-wide IA. DEFERRED.** Synthesizes the validated screen-level findings once several workflows are delivered. Do not redesign navigation merely because the current structure looks technically oriented. PO decision, recorded in `DECISIONS.md`.

**INC-14 — Application-wide dynamic feedback / live regions. CLOSED/ACCEPTED.** Cross-cutting accessibility work item; **does not reopen validated screen workstreams**. Owner UIUX + SE/SDT + PO. **Gate disposition:** A — PASS (SDT-WB). B — PASS (UIUX, `052`). C — N/A (no financial content). D — ACCEPT (PO, 2026-08-31, below).

**State (2026-08-31).** `042` (current-state audit) → `043` (specification: PO-DFB01/02, AC-DFB-01–10) → SDT-WB implementation assessment (`APPLICATION_WIDE_DYNAMIC_FEEDBACK_IMPLEMENTATION_ASSESSMENT_2026-08-31.md`, commit `8ac90a8`; proposed a zero-JavaScript `tabindex="-1"`/`autofocus` fix for both `base.html`'s flash mechanism and `job_running.html`'s status region, and flagged one residual interaction not covered by the four representative surfaces: a `#series-{id}` fragment-anchored cross-workflow link landing on a page also carrying a flashed message) → SDT-HF implementation, four iterations (`ea754dd` initial; `4802615` fixed the flagged fragment/autofocus interaction's focus half but left scroll wrong; `9311cd2` regressed focus entirely while investigating the scroll half; `5bad881` reverted to `4802615`'s structure once real-click investigation — `histfints_uiue 051` — showed the "scroll defect" that motivated the split never reproduced via a real click, only via scripted/automated navigation) → UIUX real-NVDA validation, five documents (`048` FAIL on the flagged interaction, exactly as SDT-WB anticipated; `049` partial fix; `050` regression; `051` reconciliation — scroll: navigation-method artifact, not a real defect; focus/announcement: confirmed real, unresolved on `9311cd2`; `052` **PASS**, current authoritative result, against `5bad881`, using a real UI-Automation click on the actual production "Open Series" link as the trigger).

**Gate A (SDT-WB technical conformance, this record).** Verified `histfints@5bad881` directly: `HEAD` matches, working tree clean except unrelated same-day BYMA evidence-collection output; full suite **1450 passed, 0 failed** (up from 1436 pre-implementation); read `base.html`/`job_running.html`/`series.html`/`web.py`'s current diff against the assessment's own proposed mechanism — confirmed to match (`suppress_flash_autofocus` context flag, set by `series_page()` only for a fragment-target landing; `announced` flag on the in-memory `jobs` dict, gating `job_running.html`'s `autofocus` to first arrival only) — and confirmed the implementation's own template comments cite the assessment (`8ac90a8`) directly. **PASS.**

**Gate B (UIUX, `052`).** **PASS.** AC-DFB-01–10 confirmed: shared flash mechanism (AC-DFB-01–04/07) and `job_running.html` first-arrival announcement (AC-DFB-05) both independently captured via real NVDA on `5bad881`, using the real Search → "Open Series" link as the trigger (not scripted navigation, per `051`'s own finding that scripted navigation had been producing an artifact). **Two qualifications, preserved exactly as `052` recorded them, neither treated as a defect**: (1) DOM `document.activeElement` was not independently captured this pass — the isolated Chrome process used has no JS/CDP access by the validation toolkit's own design; OS/UIA `HasKeyboardFocus` (a real, unambiguous signal, confirmed exactly one match: the target fieldset) stands in its place, explicitly named as a different measurement, not approximated as equivalent. (2) `job_running.html` was not freshly re-captured with NVDA in this specific pass — `5bad881`'s diff does not touch it, and `049`'s own real-NVDA PASS for that surface (against `4802615`, structurally identical on this point) stands as the most recent direct evidence. AC-DFB-06 does not trigger (no JavaScript was introduced). AC-DFB-09/10 satisfied by construction — no closed workstream's own AC-* criteria concerned this interaction (independently re-confirmed by SDT-WB in the original assessment, §6, and re-stated unchanged by every one of `048`–`052`).

**Evidence chain preserved, not rewritten.** `048` (original FAIL against `ea754dd`), `049` (partial fix against `4802615`), `050` (regression against `9311cd2`), and `051` (reconciliation, narrowing `050`'s combined finding to scroll-resolved/focus-still-broken) all remain exactly as originally written — each is accurate, dated evidence about the specific commit it tested, not superseded content. `052` supersedes them only for the current authoritative AC-DFB-08/INC-14 verdict (PASS, against `5bad881`), not by editing or retracting any of the four.

**Gate C (DFA): N/A.** No financial meaning, methodology, or evidence-interpretation question is raised by any part of this workstream — confirmed directly (`042` §7: "None... this is purely an accessibility-mechanism question"), independently re-confirmed by re-reading `043` end to end, which raises no DFA gate either.

**Gate D (PO): ACCEPT (2026-08-31).** Per PO's own direct instruction ("PO has ACCEPTED INC-14"), attributed to its actual owning authority, consistent with this project's standing practice of recording a gate decision only when relayed from the party who actually holds it. This is the final closure event for INC-14 — Gates A/B/C/D are now all disposed.

**Closure scope — stated explicitly, not implied.** This closes only the mechanism specified in `043` and validated in `048`–`052`: the shared `base.html` flash region and `job_running.html`'s status region are now reliably announced on full navigation/first arrival, via the zero-JavaScript `tabindex="-1"`/`autofocus` technique, with the `#series-{id}` fragment interaction resolved. It does **not**: extend to or reopen INC-12, INC-13, or INC-15 — none of their own AC-* criteria concern focus management or announcement timing (independently re-confirmed here, consistent with every one of `048`–`052`'s own repeated check); authorize any further UI/live-region mechanism change without its own specification; or extend to any other increment. **The evidence chain is preserved exactly as recorded** — `048`/`049`/`050`/`051` remain unedited as accurate, dated evidence about the specific commits they each tested, and `052`'s own two qualifications (DOM `document.activeElement` not independently captured; `job_running.html` not freshly re-captured with NVDA in that pass) stand as recorded, neither treated as a defect nor as blocking this closure. Does not touch `histfints_uiue 60d12dd`'s own repository — **noted explicitly: that commit was, as of the prior record, local-only/unpushed** in `histfints_uiue`, a fact about that repository's own state, not something this closure changes or depends on beyond citing it accurately; if its push status has since changed, that is a fact for a future record to confirm, not inferred here.

## 16a. INC-16 — `USER_DISABLED` Manual Run Prohibition

**State:** CLOSED/ACCEPTED — **Owner:** UIUX + SE/SDT + PO — **Gate disposition:** A — PASS (SDT-WB, below). B — PASS (UIUX, `053`). C — N/A (no financial content). D — ACCEPT (PO, 2026-09-01, below).

**Background.** A pre-existing, already-flagged backlog item (`005` §9, 2026-08-25 — not a new workstream), explicitly carved out as unaffected by the Provider Assignment Removal closure (`010` §5, "continues on its own track") and never answered by any subsequent document through `030`'s own Series UX closure. `046` re-verified the asymmetry live in the current codebase (unchanged from `005`): a `USER_DISABLED` Series with a provider assignment rendered an enabled, clickable Run button in Import & Status, identical to an `ACTIVE` Series — scheduled bulk Run already correctly excluded non-`ACTIVE` Series, but manual per-row Run did not.

**Closure record so far (2026-09-01).** `046` (current-state re-verification, one PO gate restated from `005` §9) → `047` (specification, settled 2026-08-31: PO-UD01 — manual Run prohibited for `USER_DISABLED`, both paths brought into alignment with scheduled Run's existing exclusion; AC-UD-01–12; amended in place at `836fb2e` to settle AC-UD-07's exact bulk-confirm dialog wording, §4a) → SDT-HF implementation (`c3e2cf6`, full suite 1460/1460 at the time, up from 1450) → **adjacent, non-AC finding during UIUX's own validation**: the `USER_DISABLED` rejection message leaked internal specification/AC references (`"(histfints_uiue 047, AC-UD-02)"` plus a rationale paragraph) into user-visible flash text — not a FAIL of any AC-UD criterion (`047` never specified this exception's exact wording), flagged rather than treated as a defect → bounded cleanup (`3023a84`, the exception string only, rationale moved to a code comment, matching the sibling `SUPERSEDED` guard's own established style) → UIUX narrow follow-up validation (spot-check only, not a full AC-UD-01–12 re-run — none needed, the diff touched one string) — **PASS**, both recorded together in `053`.

**Gate A (SDT-WB technical conformance, this record).** Verified both commits directly in `histfints`: `HEAD` is `3023a84`, working tree clean except unrelated same-day BYMA evidence-collection output; full suite **1460 passed, 0 failed** (unchanged count from `c3e2cf6` — `3023a84` added assertions to existing tests, no new test functions, matching its own commit message exactly). Read `c3e2cf6`'s full diff (`import_service.py`, `import_status_view.py`, `import_status.html`, plus three test files, 323 lines) — confirms `SeriesImportStatus.is_disabled` is deliberately independent of `is_scheduled` (047 §9 Q1, answered), the disabled-reason precedence rule (AC-UD-03), the shared-choke-point `ImportService.run_import()` rejection (AC-UD-02, closing the previously-open direct-call bypass), the two independent non-overlapping bulk-dialog counts (§4a), and the first-ever `Series.status` indicator on this page (`046`'s own finding, now addressed) — all matching `047`'s specification, not a paraphrase. Read `3023a84`'s full diff — confirms it is exactly the exception string, nothing else: no routing, status-behavior, template-wording, or bulk-confirm-wording change, per its own commit message, independently verified rather than trusted. **PASS.**

**Gate B (UIUX, `053`).** **PASS.** Full AC-UD-01–12 validated live against `c3e2cf6` — all twelve PASS, including a real-NVDA capture for AC-UD-10 (verbatim: `"...an import. Series is disabled — re-enable it first to run an import."`). The message-leak finding (§3 above) was recorded as history, not as an AC-UD FAIL, and the narrow follow-up against `3023a84` (spot-check, not a full re-run — the diff didn't warrant one) confirmed the corrected wording and zero regression in the adjacent per-row reason (AC-UD-05) or bulk-dialog wording (AC-UD-07), both found byte-identical to the `c3e2cf6` validation.

**Distinction preserved, per instruction, independently re-confirmed**: the original AC-UD-01–12 validation (against `c3e2cf6`) and the later non-AC cleanup validation (against `3023a84`) are two distinct events in `053`'s own record, not conflated into one pass — `053` itself states this explicitly (§1's five-step sequence) and this record does not compress them further.

**Gate C (DFA): N/A.** No financial meaning, methodology, or evidence-interpretation question is raised — confirmed directly (`046` §3/`047`'s own framing: "a product-behavior question... not a financial-methodology one — no DFA gate identified"), independently re-confirmed by reading both documents end to end.

**Gate D (PO): ACCEPT (2026-09-01).** Per PO's own direct instruction ("PO has ACCEPTED INC-16"), attributed to its actual owning authority, consistent with this project's standing practice of recording a gate decision only when relayed from the party who actually holds it. This is the final closure event for INC-16 — Gates A/B/C/D are now all disposed.

**Closure scope — stated explicitly, not implied.** This closes only the mechanism specified in `047` and validated in `053`: manual Run is prohibited for a `USER_DISABLED` Series on both the presentation path (disabled button, correct precedence over the assignment-gap reason) and the service path (the shared choke point, closing the previously-open direct-call bypass), with accurate, non-leaking explanatory and bulk-confirm wording. It does **not**: reopen `030` (Series UX) — this item was never part of what `030` closed, confirmed directly by both `046` and `047`; extend to any other Series-status value (`DELISTED_OR_DISCONTINUED`, `PROVIDER_UNAVAILABLE`, `SUPERSEDED`) — `047` §3 explicitly named these out of scope, and this closure does not widen that; or extend to any other increment. **The evidence chain is preserved exactly as recorded, and the distinction between the two validation events is preserved, per instruction**: `053`'s full AC-UD-01–12 validation (against `c3e2cf6`) and its later, narrower follow-up validation of the adjacent, non-AC message-leak cleanup (against `3023a84`) remain two distinct, dated events in `053`'s own record — not conflated into one pass by this closure, exactly as `053` itself states them. `046` remains unchanged as the historical pre-decision record; `047` remains unchanged as the settled specification (its one amendment, `836fb2e`, predates this closure and is already reflected in the wording independently verified in Gate A above, not a further change made here).

## 17. Remaining verification gaps

The cross-actor consolidation is complete to the extent supported by available governing evidence. The following items remain explicit because this plan must not manufacture authority or closure:

1. **Closure/state verification.** States marked **†** (INC-1, INC-2, INC-11) came from the UIUX consolidation and still require confirmation against the authoritative project index. Until confirmed, the dagger is part of the state assertion. (INC-12 confirmed against the live project index 2026-08-29 and has since closed — no longer daggered; see §9.)
2. **Increment-ID provenance.** Confirm that INC-11 through INC-14 do not collide with IDs already assigned in an unavailable prior project index. Existing IDs must never be renumbered silently.
3. **`SUPERSEDED`.** DFA general semantics remain unresolved because the current docstring and evidence for the existing rows have not been supplied. Do not infer a general lifecycle meaning from the historical reattribution case.
4. **BR-29.** Cite the governing rule and state exactly what history-preserving removal guarantees.
5. **Discover / Resolve.** Cite their governing specifications.
6. **D1–D4 (still open) and Tier 0/1/2/3 (Tier 0/1/2 RESOLVED 2026-09-01, see §1's row; Tier 3 remains deferred).** Replace remaining shorthand with governing citations when the authoritative records are available.

These are documentation/evidence gaps unless a governing source reveals a substantive contradiction. They do not authorize reinterpretation by convenience.

## 18. Documentation map

This plan stays concise; detail belongs in governing documents.

- `Workbench_UIUX_decisions_&_constraints.md` — UIUX domain and architectural constraints.
- `SPEC-panel-eligibility.md` — panel eligibility methodology.
- `DECISIONS.md` — authoritative project decisions and rulings.
- `REQUEST-event-capture.md` — event-capture evidence capability. *(The available project source is titled `REQUEST-event-capture.md`; SE should still verify repository canonical naming if duplicate physical files exist.)*
- `REQUEST-tranche2-migration.md` — historical/provider-assignment evidence migration.
- `DEFECT-F009.md` — defect evidence where applicable.
- *GAP:* Discover specification, Resolve specification, BR-29 record, INC-14 specification.

UIUX audits and screen specifications remain governing for their screens.

## 19. Maintenance rule

Update this plan when an increment changes state, a dependency resolves, or PO changes sequencing. Update **Last updated** in the same edit.

Do not copy detailed methodology here; reference the authoritative source. Where a summary is unavoidable, mark it as a summary and name the source.

Every increment states the core fields of §6, plus the conditional fields where it has a user-facing surface. Where a field is not yet answerable, write `GAP —` and the party who must answer it. Silent omission is not permitted.

Standing rules live in §3 and are cited by ID. Do not restate an SP or UP inside an increment; if an increment needs a different rule, it is a new rule and belongs in §3.

## 20. Current focus

*As of 2026-09-01. Pointer only — states live in §5.*

- **INC-12** — **CLOSED/ACCEPTED 2026-08-29 (§8/§9).** All four gates disposed (A/B/C/D PASS-ACCEPT). Reusable baseline only from here — does not extend to Resolve (INC-13) or authorize automatic identity resolution; do not reopen or silently extend without a new decision.
- **INC-13** — **CLOSED/ACCEPTED 2026-08-29 (§8/§10).** All four gates disposed (A/B/C/D PASS-ACCEPT; Gate B carries two named, not-rounded-up NVDA validation-coverage qualifications). Reusable baseline only from here — does not authorize automatic identity resolution at any tier, and each future disposition remains subject to its own evidence/adjudication requirements; do not reopen or silently extend without a new decision.
- **INC-15** — **CLOSED/ACCEPTED 2026-08-31 (§8/§10a).** All four gates disposed (A/B/C/D PASS-ACCEPT; Gate B carries a named defect-and-correction cycle, `044` FAIL → `045` PASS — not glossed over). Reusable baseline only from here — does not extend to INC-12/INC-13/INC-14 or authorize automatic identity resolution; do not reopen or silently extend without a new decision.
- **INC-4** — ACTIVE overall; two bounded capabilities **CLOSED/ACCEPTED 2026-09-01 (§8/§12)**: `MatchCandidate → EvidenceSignal` (A/C/D PASS-ACCEPT; the empty `evidence_signal` table — no real production signal yet — is not a reopening condition, a future occurrence is additional validation only) and manual financial-identity adjudication (`IdentityAdjudication`, A/B/C/D PASS-ACCEPT; Gate B fully discharged only after a genuine capture-tooling defect, distinct from a genuine application defect, was separately found and fixed — see §12). Reusable baselines only for those bounded capabilities — neither closes INC-4 as a whole, validates/expands Tier 3, changes Resolve/adjudication semantics, or authorizes automatic/automated identity resolution; do not reopen or silently extend without a new decision. **Tier 0/1/2 methodology GAP RESOLVED 2026-09-01** (§1/§12) — governing reference adopted, `docs/28` provenance limitation preserved; shipped implementation not yet claimed conformant to the newly-incorporated authoritative-contradiction-resolution/disposition-materiality rulings. **Correction (2026-09-01): stale as of `8bcab60`.** DFA's subsequent canonical adjudication-record ruling establishes two real, forward-looking implementation gaps (case-specific materiality persistence; affirmative authoritative-contradiction resolution) — a bounded corrective increment, **INC-17**, is now justified for SDT-HF technical design (§12a). The previously-closed `IdentityAdjudication` capability remains historically CLOSED/ACCEPTED, not reopened. Real production adjudication still waits on a genuinely eligible Tier 0/1/2 `EvidenceSignal` occurring naturally — that remains true and unrelated, and does not itself block INC-17's design/implementation.
- **INC-5** — live Yahoo/FRED capture capability **CLOSED/ACCEPTED 2026-09-01 (§8/§13)**, all applicable gates disposed (A/C/D PASS-ACCEPT; B deferred to first user-facing surface, unchanged). 859 real captured events preserved as operational evidence, evidence-only; capture-run provenance via shared `acquired_at` explicitly not equivalent to `ImportRun`'s FK pattern. Reusable baseline only — does not extend to comparability/causal-attribution/adjudication or any other increment; continue only the further prerequisite work defined financial questions require beyond this capability.
- **INC-6** — **CLOSED/ACCEPTED 2026-09-01 (§8/§14), provider-level `adjustment_basis` field scope only.** All three applicable gates disposed (A/C/D PASS-ACCEPT). Reusable baseline only from here — does not extend to cross-provider comparability, historical splicing, corporate-action correctness, or UI implementation; Finnhub's `NULL` boundary condition stands as a permanent, self-expiring standing note, not discharged by this closure; do not reopen or silently extend without a new decision.
- **INC-3** — **CLOSED/ACCEPTED 2026-08-29 (§8/§11).** All four gates disposed (A/C/D PASS-ACCEPT, B N/A). Reusable baseline only from here — do not reopen or silently extend without a new decision.
- **INC-14** — **CLOSED/ACCEPTED 2026-08-31 (§8/§16).** All four gates disposed (A/B/D PASS-ACCEPT; C N/A, no financial content; Gate B carries two named, not-glossed-over evidence-scope qualifications). Reusable baseline only from here — distinct from INC-15, not touched or advanced by its closure; do not reopen or silently extend without a new decision.
- **INC-16** — **CLOSED/ACCEPTED 2026-09-01 (§8/§16a).** All four gates disposed (A/B/D PASS-ACCEPT; C N/A, no financial content). Reusable baseline only from here — does not extend to `SUPERSEDED`/`DELISTED_OR_DISCONTINUED`/`PROVIDER_UNAVAILABLE` or any other increment; do not reopen or silently extend without a new decision. `046` remains unchanged as historical pre-decision evidence; `047` remains unchanged as the settled specification.
- **INC-7** — advance each analytical workflow when its own evidence and methodology gates are satisfied.
- **§17** — close the remaining evidence/documentation gaps without inferring missing semantics.

**Next SDT increment: SE/PO sequencing decision, not started here.** INC-4/5 are not selected or begun by this plan on its own authority — per §1, sequencing is PO's to settle. (INC-6/INC-12/INC-13/INC-14/INC-15/INC-16, all previously named or newly closed here, are now closed — see above, not candidates for "next.")
