# WORKBENCH ACTION PLAN

**Plan revision:** v7 — **Last updated:** 2026-08-31 — **Supersedes:** v6
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
| Tier 0/1/2/3 | INC-4 | cite the identity-methodology document |
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
| INC-4 | Financial identity/evidence prerequisites | ACTIVE | DFA + SE/SDT | — | identity decisions; evidence pipeline |
| INC-5 | Corporate-action / economic-event evidence | ACTIVE | SE/SDT + DFA | — (scope set by INC-6/INC-7 needs) | `REQUEST-event-capture.md` |
| INC-6 | Adjustment-basis and coverage evidence | ACTIVE | SE/SDT + DFA | — (scope set by INC-7 needs) | `REQUEST-tranche2-migration.md` |
| INC-13 | Catalog: Resolve | CLOSED | UIUX + SE/SDT + DFA | — | `035_Catalog_Resolve_UX_Specification.md`, `039_Catalog_Resolve_Workstream_Closure.md` (histfints_uiue); §8/§10 baseline |
| INC-3 | Publication-aware acquisition-history diagnostic | CLOSED | DFA → SE/SDT | — | D1–D4 rulings; DFA BYMA calendar rulings; §8/§11 baseline |
| INC-14 | Application-wide dynamic feedback / live regions | NEXT | UIUX + SE | — | new; specification required |
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

**State:** ACTIVE — **Owner:** DFA + SE/SDT

**Established domain rule:** financial identity requires authoritative, temporally valid evidence sufficient for the identity question. Technical/provider signals may discover candidates and support evidence collection but cannot independently establish identity (SP-3). Missing, stale, contradictory or insufficient evidence produces `UNRESOLVED`.

**Constraints:** `automatic_resolution_enabled=False` is binding (SP-1); the compatibility states retain narrow provider/technical meaning (§7); current evidence cannot automatically establish historical identity; source count is not a substitute for authority, independence, or effective-date validity.

**Gate C:** evidence may populate the identity pipeline only where doing so does not silently redefine Tier 0/1/2/3 methodology. Where the tiers cannot express a required evidence condition, record a specification gap for DFA/PO rather than stretching a tier.

## 13. INC-5 — Corporate-action and economic-event evidence

**State:** ACTIVE — **Owner:** SE/SDT + DFA — **Source:** `REQUEST-event-capture.md`

**Financial question:** what externally reported event evidence exists, for which Series and effective period, and how far may it support reconciliation of observed time-series behavior?

**Required evidence:** provider/run provenance; the reported event as distinct from any reconciled fact; effective dates and historical applicability.

**Legitimate conclusion:** "an event was reported by provider X, effective date Y, captured in run Z." Nothing stronger.

**Prohibited:** SP-7, SP-9.

**Gates:** A — provenance is queryable for every captured event. C — DFA confirms stored fields and any wording keep reported evidence distinct from reconciled fact. B/D — on first user-facing surface.

## 14. INC-6 — Adjustment basis and historical coverage

**State:** ACTIVE — **Owner:** SE/SDT + DFA — **Source:** `REQUEST-tranche2-migration.md`

**Financial question:** is the stored history sufficiently complete and comparable for the intended analysis, or does apparent absence reflect Series existence, provider assignment, provider availability, incomplete acquisition, or another unresolved cause?

**Required evidence** (where applicable): provider-assignment effective periods; provider availability/coverage; stored observation coverage; adjustment basis; corporate-action context; provenance and missing-data state.

**Domain constraint:** existence is not analytical eligibility; incomplete coverage is not automatically invalid data; absence of an observation is not proof of non-existence.

**Prohibited:** SP-4, SP-8.

**Gate C:** for each consuming analysis, DFA confirms the coverage evidence answers that analysis's comparability question; unresolved causes remain visibly unresolved (UP-3).

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

**INC-14 — Application-wide dynamic feedback / live regions. NEXT.** Cross-cutting accessibility work item; **does not reopen validated screen workstreams**. Evaluates `role="status"` after full-page navigation or reload, `role="alert"`, focus restoration, success/error/no-op announcements, and cross-screen consistency. Owner UIUX + SE. Specification required — GAP, UIUX.

## 17. Remaining verification gaps

The cross-actor consolidation is complete to the extent supported by available governing evidence. The following items remain explicit because this plan must not manufacture authority or closure:

1. **Closure/state verification.** States marked **†** (INC-1, INC-2, INC-11) came from the UIUX consolidation and still require confirmation against the authoritative project index. Until confirmed, the dagger is part of the state assertion. (INC-12 confirmed against the live project index 2026-08-29 and has since closed — no longer daggered; see §9.)
2. **Increment-ID provenance.** Confirm that INC-11 through INC-14 do not collide with IDs already assigned in an unavailable prior project index. Existing IDs must never be renumbered silently.
3. **`SUPERSEDED`.** DFA general semantics remain unresolved because the current docstring and evidence for the existing rows have not been supplied. Do not infer a general lifecycle meaning from the historical reattribution case.
4. **BR-29.** Cite the governing rule and state exactly what history-preserving removal guarantees.
5. **Discover / Resolve.** Cite their governing specifications.
6. **D1–D4 and Tier 0/1/2/3.** Replace shorthand with governing citations when the authoritative records are available.

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

*As of 2026-08-31. Pointer only — states live in §5.*

- **INC-12** — **CLOSED/ACCEPTED 2026-08-29 (§8/§9).** All four gates disposed (A/B/C/D PASS-ACCEPT). Reusable baseline only from here — does not extend to Resolve (INC-13) or authorize automatic identity resolution; do not reopen or silently extend without a new decision.
- **INC-13** — **CLOSED/ACCEPTED 2026-08-29 (§8/§10).** All four gates disposed (A/B/C/D PASS-ACCEPT; Gate B carries two named, not-rounded-up NVDA validation-coverage qualifications). Reusable baseline only from here — does not authorize automatic identity resolution at any tier, and each future disposition remains subject to its own evidence/adjudication requirements; do not reopen or silently extend without a new decision.
- **INC-15** — **CLOSED/ACCEPTED 2026-08-31 (§8/§10a).** All four gates disposed (A/B/C/D PASS-ACCEPT; Gate B carries a named defect-and-correction cycle, `044` FAIL → `045` PASS — not glossed over). Reusable baseline only from here — does not extend to INC-12/INC-13/INC-14 or authorize automatic identity resolution; do not reopen or silently extend without a new decision.
- **INC-4/5/6** — continue only the prerequisite work defined financial questions require; preserve unresolved states and provenance.
- **INC-3** — **CLOSED/ACCEPTED 2026-08-29 (§8/§11).** All four gates disposed (A/C/D PASS-ACCEPT, B N/A). Reusable baseline only from here — do not reopen or silently extend without a new decision.
- **INC-14** — specify the live-region behavior before more screens ship. Distinct from INC-15 — not touched or advanced by INC-15's closure.
- **INC-7** — advance each analytical workflow when its own evidence and methodology gates are satisfied.
- **§17** — close the remaining evidence/documentation gaps without inferring missing semantics.

**Next SDT increment: SE/PO sequencing decision, not started here.** INC-4/5/6 are not selected or begun by this plan on its own authority — per §1, sequencing is PO's to settle. (INC-12/INC-13/INC-15, all previously named or newly closed here, are now closed — see above, not candidates for "next.")
