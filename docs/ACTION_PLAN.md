# WORKBENCH ACTION PLAN

**Plan revision:** v7 — **Last updated:** 2026-08-29 — **Supersedes:** v6
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

UIUX is an **independent authority**, not a specialism coordinated by SE. Routing chain:

**SDT1/SDT2/n ↔ SE ↔ UIUX ↔ DFA ↔ PO**

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
| INC-12 | Catalog: Discover | BLOCKED | UIUX + SE/SDT + DFA | Gate C (DFA) and Gate D (PO) — Gates A/B PASS 2026-08-29 (§9) | `024_Catalog_Discover_UX_Specification.md` (histfints_uiue) |
| INC-4 | Financial identity/evidence prerequisites | ACTIVE | DFA + SE/SDT | — | identity decisions; evidence pipeline |
| INC-5 | Corporate-action / economic-event evidence | ACTIVE | SE/SDT + DFA | — (scope set by INC-6/INC-7 needs) | `REQUEST-event-capture.md` |
| INC-6 | Adjustment-basis and coverage evidence | ACTIVE | SE/SDT + DFA | — (scope set by INC-7 needs) | `REQUEST-tranche2-migration.md` |
| INC-13 | Catalog: Resolve | NEXT | UIUX + DFA | INC-12 evidence/candidate boundary validated | Resolve specification (GAP: cite) |
| INC-3 | Publication-aware acquisition-history diagnostic | CLOSED | DFA → SE/SDT | — | D1–D4 rulings; DFA BYMA calendar rulings; §8/§11 baseline |
| INC-14 | Application-wide dynamic feedback / live regions | NEXT | UIUX + SE | — | new; specification required |
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

## 9. INC-12 — Catalog: Discover

**State:** BLOCKED — **Owner:** UIUX + SE/SDT + DFA — **Blocked by:** Gate C (DFA) and Gate D (PO). Gates A and B are satisfied; UIUX's own record does not, and cannot, certify either remaining gate.

**Gate status update (2026-08-29).** `histfints_uiue` commit `f7d3ca3` ("Catalog Discover: close workstream — UIUX runtime validation PASS (032/033)"), verified directly — `033_Catalog_Discover_Workstream_Closure.md`: AC-DIS-01–22 all satisfied (AC-DIS-09/10 N/A by design, reconfirmed), zero discrepancies against `024`'s specification, no sibling repository modified (validation ran against a disposable, seeded, now-deleted test instance). **Gate A** (candidate generation reproducible/provenance-bearing): satisfied — independently reconfirmed by `032`'s live-reproduced and source-verified evidence, on top of `027`/`029`'s implementation evidence. **Gate B** (a user can tell a candidate from a decision, UP-7): satisfied — this is precisely what UIUX's completed runtime validation closes. `PROJECT_INDEX.yaml`'s `current_gate` field confirms: `'None open'` from UIUX's own side. **Gates C and D remain open** — `033`'s own record states this itself: *"DFA/PO gate | Not self-certified; none found open"* — UIUX reports finding no open DFA/PO question, which is not the same as DFA or PO having actually confirmed one. Neither gate is closed by this commit.

**Boundary:** Discover owns **evidence and candidate generation**. Resolve (INC-13) owns **adjudication and disposition**. The UI must not blur them.

**Prohibited:** SP-1, SP-2, SP-3. Increment-specific: Tier-based auto-resolution that is not supported by established methodology must not be normalized by the interface.

**Gates:** A — PASS (2026-08-29, above). B — PASS (2026-08-29, above). C — DFA confirms no candidate presentation reads as identity — **open**. D — PO accepts scope — **open**.

**Open:** governing Discover specification now cited — `024_Catalog_Discover_UX_Specification.md` (`histfints_uiue`), AC-DIS-01–22. GAP resolved.

## 10. INC-13 — Catalog: Resolve

**State:** NEXT — **Owner:** UIUX + DFA — **Blocked by:** INC-12 boundary validated

**Question:** how is an identity adjudication recorded, by whom, on what evidence, and how is it shown as a decision rather than a computation?

**Prohibited:** SP-1, SP-2, SP-3.

**Open:** required evidence, user-visible states, and the disposition vocabulary — GAP, DFA.

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

1. **Closure/state verification.** States marked **†** (INC-1, INC-2, INC-11, INC-12) came from the UIUX consolidation and still require confirmation against the authoritative project index. Until confirmed, the dagger is part of the state assertion.
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

*As of 2026-08-29. Pointer only — states live in §5.*

- **INC-12** — Discover: hold the evidence/candidate versus adjudication boundary.
- **INC-4/5/6** — continue only the prerequisite work defined financial questions require; preserve unresolved states and provenance.
- **INC-3** — **CLOSED/ACCEPTED 2026-08-29 (§8/§11).** All four gates disposed (A/C/D PASS-ACCEPT, B N/A). Reusable baseline only from here — do not reopen or silently extend without a new decision.
- **INC-14** — specify the live-region behavior before more screens ship.
- **INC-7** — advance each analytical workflow when its own evidence and methodology gates are satisfied.
- **§17** — close the remaining evidence/documentation gaps without inferring missing semantics.

**Next SDT increment: SE/PO sequencing decision, not started here.** INC-4/5/6/12 are not selected or begun by this plan on its own authority — per §1, sequencing is PO's to settle.
