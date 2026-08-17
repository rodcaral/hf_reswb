# HistFinTS Research Workbench — Decision Log

**Status:** living document · **Owner:** Carlos · **Last updated:** 2026-08-15

This log is the authoritative record of *what has been decided and why* for the
Research Workbench. The specification document describes the target product; this
log describes the constraints the product must actually be built inside.

Where the two disagree, **this log wins** and the spec gets amended (see §4).

---

## 0. How to use this document

**For humans.** Read §1 (decided) and §3 (findings) before proposing anything.
Check §2 before asking a question — it may already be queued.

**For the review agent** (`.claude/agents/spec-interrogator.md`):

1. Never treat an open question in §2 as settled by inference. Only a `D-###`
   entry in §1 is settled.
2. When a decision is reached, write the `D-###` entry **before** moving to the
   next question. An unlogged decision does not exist.
3. When an answer is empirical (something about the database, the pipeline, the
   provider data), verify it against the artefact before logging it. Record the
   command or query used under *Evidence*.
4. Questions are asked **one at a time**, chosen by what the last answer changed.

### Conventions

| Prefix | Meaning |
|---|---|
| `D-###` | Decided. Binding. |
| `Q-###` | Open question. Numbering follows the original review sequence; gaps are questions closed or absorbed. |
| `F-###` | Finding — a defect or gap in the current spec or data, not yet a decision. |
| `A-###` | Spec amendment queued as a consequence of a decision. |

Status values for open questions: `blocking` · `open` · `partially answered` ·
`deferred to V2+`

---

## 1. Decided

### D-001 — Workbench data live in a separate SQLite database

*Decided 2026-08-15. Supersedes options (a) shared file and (c) extend HistFinTS.*

Workbench-owned domains — Series relationships, corporate actions, fundamentals,
watchlists, peer sets, benchmark assignments — live in a **Workbench-owned SQLite
database**. HistFinTS is reached by `ATTACH DATABASE ... AS histfints` opened
**read-only** (`file:...?mode=ro`) from the Workbench connection.

**Rationale**

- HistFinTS `schema.sql` is frozen and its migrations are a single numbered
  sequence (`persistence/migrations/0001`–`0010`) keyed off one
  `PRAGMA user_version`. A second, independently-owned migration track cannot
  coexist in that file. Option (a) was in practice *"both teams ship schema
  changes through one coordinated pipeline"* — a far larger commitment than it
  appeared.
- The connection layer assumes a single writing application. WAL is already on
  (`persistence/connection.py`), so Workbench reads never block on HistFinTS
  imports — but WAL still serialises writers, and HistFinTS's own locking
  (`CatalogDiscoveryLock`, single shared `ApplicationContext` connection) is not
  built to arbitrate an external second writer. Write-heavy Workbench tables
  (watchlists, peer sets) would contend.

**Consequences**

- Cross-database `JOIN`s are real SQL, not application-level stitching. Cost is
  low.
- Read-only attach makes *"Workbench never writes to HistFinTS"* a mechanical
  guarantee rather than a discipline.
- **No DB-enforced referential integrity across the boundary.** `series_id` is a
  convention-level foreign key. See D-003.
- Workbench owns its own migration track, versioned independently.

### D-002 — HistFinTS scope boundary is fixed

*Decided 2026-08-15.*

HistFinTS's scope is time-series history plus provider/ticker deduplication
(per its `docs/ARCHITECTURE.md`). Corporate actions, fundamentals, watchlists and
peer sets are **not** folded into it. Doing so would couple two release cadences
to one codebase for no technical gain over D-001.

### D-003 — `series_id` is a stable reference by convention

*Decided 2026-08-15.*

HistFinTS never hard-deletes a Series. MERGE (deduplicating two Series found to
be the same instrument) **archives** the absorbed row (`archived_at` set) rather
than removing it. A `series_id` stored by Workbench today will therefore never
dangle.

**Consequence — the defensive check is the wrong one by default.** Workbench must
not check for *id existence*; it must check `series.status` and `archived_at` for
staleness. See Q-050 for the unresolved half of this.

### D-004 — Review protocol: one question at a time, decisions logged before moving on

*Decided 2026-08-15. Extended 2026-08-15 with the closing-footnote requirement.*

Batched questions cannot use the previous answer to sharpen the next one, and
several early questions were already answered by documents Carlos had written.
Reviews proceed serially. Each resolved question produces a `D-###` entry before
the next question is asked.

**Closing footnote.** Every response ends with a short, explicit footnote covering
exactly three points: (1) whether any important question must still be answered
before concrete HistFinTS changes can be requested; (2) if so, **only** the single
most important next question; (3) if not, precisely which changes are being requested
and why. Where the state is mixed — some asks unblocked, others gated — both are
stated rather than collapsed. Written into `spec-interrogator.md` so it survives the
conversation.

### D-005 — `observation.value` is provider-adjusted; the basis is split-only for Yahoo and differs by provider

*Decided 2026-08-15. Closes Q-041.*

**Evidence.** Production database, series 33 (AAPL, Yahoo Finance, 6694 daily bars,
2000–2026). Stored value for 2014-06-06 is `23.06`; the published raw close that day
was ~`645.57`. `23.06 × 7 × 4 ≈ 645.7` — the stored value reconciles only after
backing out *both* the 2014 7:1 and the 2020 4:1 split, and no discontinuity is
visible at either date.

**The values are split-adjusted — and, provable from the same arithmetic,
dividend-*un*adjusted.** `23.06 × 28 = 645.68` against a published `645.57` is a
0.017% gap, i.e. rounding. AAPL has paid dividends continuously since 2012; a
dividend-adjusted series would sit roughly 10–15% lower, near `20`, not `23.06`.
The basis is therefore **split-adjusted, dividend-unadjusted** — consistent with
Yahoo's plain `close` field, which `providers/yahoo_finance.py` reads deliberately
in preference to `adjclose`.

Narrowly, this is good news: split-adjusted/dividend-unadjusted is the correct
basis for a *price* series and the cleanest possible input to price-return
calculations. It is **not** a total-return series and must never be presented as
one (see Q-030).

**Cross-provider.** Code-confirmed mismatch, not empirically comparable — no Alpha
Vantage data exists in this database. Yahoo adapter reads
`indicators.quote[0].close` (split-adjusted server-side); Alpha Vantage adapter
calls `TIME_SERIES_DAILY`, the deliberately unadjusted function.

**Consequences**

- Adjustment basis is a **per-provider** property and is recorded nowhere. See F-010.
- A Series fallback-spliced across providers jumps at the handover with nothing
  marking it.
- AC-06 remains unbuildable until basis is recorded somewhere queryable.
- The apparent cleanliness of `correction` is survivorship, not health. See F-009.

### D-006 — The `correction` log measures the re-fetch window, not provider behaviour

*Decided 2026-08-15. Partially closes Q-039.*

**Evidence.** All 13,302 `correction` rows ever recorded, every Series, every
provider. Age of the corrected observation (`detected_at − observed_at`):
0 days → 7,114 · 1 day → 5,851 · 2 days → 325 · 3 days → 12 · 4+ days → **0**.
Oldest `observed_at` ever corrected anywhere: 2026-08-04, 11 days ago.

**Refinement, 2026-08-15 — the window is per-provider and may be zero.** Confirmed at the
line level: `ImportService._determine_range()`
(`application/import_service.py:183–200`) starts an incremental import from the latest
stored Observation **minus that provider's `default_revalidation_window_days`**, with
**zero look-back where the field is unset**; with no Observations, it starts from
`backfill_start_date` instead.

So the 0–3 day distribution reflects the providers that happen to have a window
configured. **For any provider with the field unset, no stored date is ever revisited and
`correction` can never fire at all.** The blind spot is not a uniform three days — it is
per-provider, and for some providers it is total.

**The key inference.** This distribution is *not* a measurement of how providers
revise data. It is a measurement of how far back HistFinTS ever looks. Incremental
import fetches only a trailing window from the latest stored date forward, so a
correction is structurally impossible outside that window. The hard cliff at 4 days
is the window's edge, not a property of the data.

**Therefore `correction` cannot serve as a detection mechanism.** Its coverage is
exactly the re-fetch window and nothing beyond it. Any provider revision, rescaling
or adjustment older than ~3 days is not merely unrecoverable (F-003) — it is
**undetected**. Nothing in HistFinTS will ever notice it.

**Consequence for F-009.** Detection must therefore live in Workbench or nowhere.
This promotes Q-052 (discontinuity detector) from a cheap convenience to the only
detection mechanism that exists anywhere in the stack.

**Narrowing, in the project's favour.** Because D-005 established Yahoo's `close`
is dividend-*un*adjusted, ex-dividend dates do not trigger a rescale. Only **splits**
do. That drops the trigger rate for US equities from ~4×/year/Series to a rare
event. For this project's actual universe the relief is smaller than it looks:
**CEDEAR conversion-ratio changes** (Q-018) and BYMA corporate actions fire far more
often than US splits.

**Still open from Q-039.** Whether `correction` records *which* `import_run`
performed the overwrite is unanswered, and it bears directly on F-001. Volume and
close are known to be logged; the full field coverage is unconfirmed.

**Validation route (endorsed, not yet run).** The mechanism is unfalsifiable from
observation of this database because no tracked Series has yet lived through a split.
It must be tested by construction: backfill a Series to a date *before* a known real
split, run an incremental import for a date *after* it, and check whether the
pre-split rows are left on the old scale. See A-009 — this belongs in the HistFinTS
regression suite permanently, not as a one-off.

### D-007 — Adjustment: HistFinTS captures provider events, Workbench owns the derivation

*Decided 2026-08-15. Closes Q-051. Resolves an apparent conflict with D-002 — see below.*

**Evidence.** The codebase's only reference to corporate actions is
`providers/yahoo_finance.py:63`, `"events": "div,splits"`. Grepping
`events|dividend|adjclose|splits` across `src/` returns no other hit. `_to_records()`
parses only `timestamp` and `indicators.quote[0].{open,high,low,close,volume}`; it
never reads `chart.result[0].events`. HistFinTS requests the split/dividend payload
on **every fetch** and discards it. No `splits`/`dividends`/`corporate_action` table
exists among the eleven tables in `DATABASE_SCHEMA.md`.

**The asymmetry.** Nobody owns adjustment today, but the two sides are not equally
placed. HistFinTS is one small change from owning real, provider-observed event
dates and ratios — handed over directly, not inferred. Workbench has no path to that
data except reverse-engineering it from price discontinuities, which is precisely
the guessed-scale-factor that P3 forbids.

**The split.**

| Layer | Owner | Status of the data |
|---|---|---|
| Raw provider-reported events — one record per `(provider_assignment, event)` | **HistFinTS** | Observed. Same epistemic status as an observation: recorded, not interpreted. |
| Reconciled corporate-actions model; adjustment derivation | **Workbench** | Calculated. Provenance-bearing under P3. |

**Why this does not override D-002.** D-002 says HistFinTS does not own *domains* —
fundamentals, watchlists, peer sets. Persisting an event payload a provider already
handed you is not a scope expansion; it is **faithful recording**, which is the
existing scope. Discarding it is a recording defect. D-002 stands unamended.

**Why the second row is not negotiable.** Yahoo's `events` payload covers
Yahoo-sourced Series only. **CEDEAR conversion-ratio changes come from BYMA.**
FRED/ECB Series have no corporate actions at all. Adjustment logic living inside
HistFinTS would leave the Argentine half of the universe — the differentiating
half — unadjusted. Only Workbench spans providers and asset classes.

**V0/V1: detect and quarantine.** Repair requires a trustworthy event table; nobody
has one; the ingredient is being discarded three lines from where it arrives. A
repair attempt today would necessarily infer a split ratio from a price ratio —
fragile in any week combining a split with ordinary volatility. Deferred until the
gap closes on one side or the other.

**F-009 and basis labeling stay separate.** F-009 is a defect and stands regardless
of who ends up owning adjustment: a store whose `observation.value` silently changes
scale, with no correction row and nothing recorded, is broken as a store. Basis
labeling is a feature — needs schema, a value per provider, and a backfill-vs-
go-forward decision. Bundled, they get deprioritised together.

### D-008 — HistFinTS asks are tranched by migration cost, not by review completeness

*Decided 2026-08-15.*

D-001 established that HistFinTS migrations are a **single numbered sequence** keyed
off one `PRAGMA user_version`. Every schema change is therefore a coordination event.
Three sequential migrations cost roughly three times one batched migration, so the
governing question for timing is not *"do we know enough yet"* but **"does this ask
require schema?"**

> **STATUS 2026-08-15 — nothing in Tranche 1 has been sent.** This has now persisted
> across several rounds. The consequence is worse than a delay: **Q-039 sits inside
> Tranche 1 and is the sole remaining gate on Tranche 2.** The entire HistFinTS
> workstream is therefore blocked on a message that has not gone out. Earlier footnotes
> describing Tranche 2 as "gated on Q-039" were imprecise — Q-039 was not awaiting an
> answer, it was awaiting *being asked*.

| Tranche | Contents | Gate |
|---|---|---|
| **1** | ~~fact sheet~~ **completed internally (D-021)** · ~~Q-039/Q-050/Q-057~~ **answered (D-018)** · F-009 defect report — **held pending the §3.1 reproduction (D-020)** | Only the defect report remains, and only on the reproduction. |
| **2 — one batched migration** | Corporate-action/event table (D-007, F-012) · `import_run_id` on `observation` (F-001) · adjustment-basis field (F-010) · `firstTradeDate` capture (D-014, F-017) | **UNBLOCKED 2026-08-15** by D-018(a). Specified in `REQUEST-tranche2-migration.md`. |
| **3 — later, separable** | **First defined item: asserted-identity evidence record (D-026)** · settlement dimension if D-010 resolves that way · dated conversion ratios · adapter-version on `import_run` if the adapter layer is touched | Judged on their own merits, never bundled with Tranche 2. |

**Amendment, 2026-08-15 — batch by coherence of concern, not by migration count.**
The original rule ("does this ask require schema?") was too crude, and D-010 exposed
why. Tranche 2's three changes share one justification: `observation` is not currently
trustworthy. A speculative catalog-modeling change bolted onto that migration would
make it two stories, and by the same logic already applied to F-009 versus basis
labeling, the weaker story sets the priority for both. **A second migration is cheaper
than a mixed one.** Migration count is a cost to weigh, not the criterion.

**Why Tranche 1 does not wait.** F-009's justification cannot be changed by any open
question — a store whose values silently change scale is broken regardless of how a
Series is individuated or which FX basis wins. Its fuse is lit by the next split of a
tracked Series, so the cost of delay is low-probability but unbounded, and the fix is
cheapest now while no corrupt history exists to clean up. The evidence is also at peak
quality today, while the diagnostics are fresh and reproducible.

**Why the fact sheet is Tranche 1 despite feeding a Tranche 2 column.** Determining
each provider's adjustment convention is *investigation*, not schema. Yahoo and Alpha
Vantage are settled (D-005); Stooq, BYMA and FRED are unconfirmed. Starting that work
now parallelises it against the remaining review and removes it from the migration's
critical path.

**Framing discipline, carried from D-007.** The defect and the feature requests go
separately. A single bundled wish-list gets prioritised as one item, at the priority of
its weakest member.

### D-009 — A clean empirical result from this database is not evidence

*Decided 2026-08-15. Standing methodological rule, applies to every subsequent check.*

Three independent diagnostics have now come back clean, and the same root cause
explains all three: **everything in this database was backfilled within the last two
weeks.**

| Diagnostic | Apparent result | Actual explanation |
|---|---|---|
| Splits — no discontinuity in AAPL | history is consistent | assignment created 2026-08-11, after both splits |
| Corrections — none older than 3 days | provider revisions are rare | the re-fetch window never looks further back (D-006) |
| FRED — UNRATE matches current publication | revisions are being captured | assignment created 2026-08-04, 11 days ago |

None of these observed the mechanism working. Each observed a system too young to have
been tested.

**The rule.** For any defect whose trigger is an *elapsed event* — a split, a revision,
a provider substitution, a ticker recycle — a negative result from this database is
**uninformative**, not reassuring. Such defects can only be settled by:

1. **construction** — force the trigger against the real import path; or
2. **external evidence** about the provider, where provider behaviour rather than
   HistFinTS behaviour is the thing in doubt.

Waiting for the database to age is not a third option; it converts an unproven risk
into a discovered corruption.

**Consequence for the review.** Empirical answers are still worth gathering — they have
repeatedly sharpened the picture — but a clean one must be recorded as *"not yet
triggered"*, never as *"mechanism sound"*. This rule is written into
`spec-interrogator.md` so it survives the current conversation.

### D-010 — Settlement modelling is a Catalog-resolution question, needs no schema today, and is not bundled

*Decided 2026-08-15. Reframes Q-046, which was posed as a false dichotomy.*

**Evidence.** `series WHERE label LIKE '%GGAL%'` → **0 rows**. Four raw
`provider_symbol` rows exist, discovered from BYMA and never resolved:

| id | raw_ticker | currency | settlement_mechanism |
|---|---|---|---|
| 1284 | GGAL | ARS | LOCAL |
| 1395 | GGALB | ARS | LOCAL |
| 1396 | GGALC | USD | CABLE |
| 1397 | GGALD | USD | MEP |

`match_candidate` for any of them → **0 rows**. Discovery has run; matching has not
even proposed an answer.

**So "one Series or three" is not answerable from this database.** The honest status is
*presently unresolved, with nothing in the catalog pipeline having proposed a
resolution*.

**What is settled.** `currency` and `settlement_mechanism` are already real, populated,
discriminating fields at the **ProviderSymbol** level. BYMA reports these as genuinely
distinct instruments, not as views of one raw ticker. The open question sits entirely
on the Series side.

**Both answers are structurally available today, without a migration.**
`series.settlement_mechanism` already exists as a nullable column (migration `0004`),
so "settlement as an attribute of one Series" needs no schema at all. And
`underlying_series_id`/`ratio` with `SET_UNDERLYING` already models a typed
relationship, so "three Series related to one another" has precedent.

Schema would only be needed to make HistFinTS **enforce** the dimension — a uniqueness
constraint scoped by settlement, or a first-class relationship type between the three.
Recording it descriptively is free.

**Not bundled with Tranche 2.** Observation-integrity changes concern whether stored
numbers are trustworthy. This concerns how the catalog resolves identity. Different
concerns, different certainty, and this one is speculative — there is not yet a single
resolved instance to generalise from. Bundled, it would inherit Tranche 2's priority
rather than being judged on its own, exactly as would have happened had F-009 been
filed together with basis labeling.

**Note in passing — the schema leans toward three.** A nullable
`series.settlement_mechanism` is only meaningful if a Series *has* a settlement
mechanism. Under the one-Series reading, that column would be permanently NULL or
arbitrary for every multi-settlement instrument. Suggestive of original intent, not
decisive.

### D-011 — V0 runs on US equities/ETFs plus macro; the Argentine side is a throughput problem, not a modelling one

*Decided 2026-08-15. Closes Q-007. Confirms Q-049's V0 proposal.*

**Census (11,311 `series` rows, joined through `provider_assignment`):**

| Provider | series_type | count |
|---|---|---|
| Yahoo Finance | STOCK | 5,725 |
| Yahoo Finance | ETF | 5,583 |
| BYMA | STOCK | 2 |
| FRED | ECONOMIC_INDICATOR | 1 |
| FRED | STOCK | 1 *(test fixture)* |

The two BYMA-backed Series are **CEDEAR wrappers of US underlyings** — 11305 Apple Inc.
CEDEAR (`underlying_series_id=33`, `ratio=20.0`) and 11311 GLD CEDEAR. **Zero Series
exist for any BYMA-domestic instrument.**

**The backlog.** 1,491 open BYMA ProviderSymbols discovered; 11 have ever produced a
`MatchCandidate`; **0** resolved. GGAL's unresolved state is not an edge case, it is the
default state of the entire BYMA universe.

**Consequences**

- V0 is confirmed as US equities/ETFs plus macro. Not a prudent narrowing — the only
  thing this database currently supports.
- The identity cluster (settlement dimension, BYMA suffix semantics, domestic-equity
  typing) has **no resolved instance to design against**. Designing it now would be
  speculation. Deferred until catalog resolution produces real cases. This retroactively
  vindicates D-010's refusal to bundle it.
- The gap is Catalog throughput, not schema and not modelling.

**But the two CEDEARs are worth more than their count suggests — see A-012.**

---

**Amendment, 2026-08-15 — corrected, not merely refined.** Eight further Series now
carry real multi-year Argentine price history: YPF, Banco Macro, Comercial del Plata,
Pampa Energía, and CEDEARs for Alibaba, Baidu and Uber (plus iShares Ethereum Trust
CEDEAR, incomplete — see F-017).

**Corrected statement:** V0 can be built on US equities, macro, **and a
manually-verified subset of BYMA-linked names**, but not the BYMA-discovered universe
in bulk.

**Crucial provider detail: these arrive via Yahoo's `.BA` cross-listing feed, not via
the BYMA provider.** The BYMA adapter path remains unexercised, so BYMA-specific
conventions — suffix parsing, `denominationCcy`, truncated symbols, the certificate
chain — are still untested. Everything above inherits Yahoo's basis (D-005) and Yahoo's
blind spots (F-009, F-013, F-017), not BYMA's.

**The "in bulk" caveat is load-bearing.** Two of ten hand-picked, well-known names were
rejected before creation: `FXI.BA` resolves to a different company entirely, and
`PBR.BA` has exactly one bar of history. A ~20% rejection rate on an easy sample implies
the 1,491-symbol backlog needs per-name verification at scale, not a bulk run. See
F-018.

### D-012 — The one-Series settlement outcome is a tooling-forced default, **not** a modelling decision

*Recorded 2026-08-15. Does not close the settlement question.*

`BMA`, `COME` and `PAMP` each presented 4–6 BYMA settlement-suffixed variants (e.g.
`BMA`, `BMA.C`, `BMA.D`, `BMADB`) — structurally identical to GGAL's
`GGAL`/`GGALB`/`GGALC`/`GGALD`. Each family was resolved into **one** Series, backed by
Yahoo's single ARS-denominated `.BA` feed, with the other settlement variants left
untouched.

**This is recorded specifically so it is not later misread as precedent.** The
one-Series shape was forced by what Yahoo offers — one feed per company, not one per
settlement mechanism. It is not an answer to the modelling question in D-010. Nobody
decided "one row"; the only working data source made three rows impossible.

**Two consequences worth watching.**

1. **A default becomes a decision by silence.** If these Series accumulate history and
   downstream code assumes one-Series-per-company, the modelling question will have been
   settled by inertia rather than judgement.
2. **A latent inconsistency exists now.** The unresolved settlement variants still sit in
   `provider_symbol`. If they are later resolved, they must either merge into these
   Series or create siblings — and the existing rows' `settlement_mechanism` value
   (whatever it currently holds) will have to be reconciled against a decision not yet
   made.

The question stays open, and is properly answerable only when a source supplying
per-settlement prices is connected — which is the BYMA adapter, still unexercised.

### D-013 — CEDEAR is a wrapper, not a type; the regulation defines subtypes, a variable ratio, and three distinct relationship kinds

*Decided 2026-08-15. Source: CNV Normas, Título II, Capítulo VIII, as substituted by
RG 1142/2026 (B.O. 01/06/2026) and RG 1095/2025. Answers Q-018 and the remainder of
Q-017; reshapes Q-045.*

**1. CEDEAR subtypes are a regulatory requirement, not a modelling nicety.** The
prospectus must state whether the CEDEAR represents *acciones, ADR, ETF or bono
corporativo*, and whether it is *patrocinado* or *no patrocinado*. CEDEARs over ETFs
tracking equities, virtual assets or commodities are separately provided for.

Consequence for P2/AC-04: **the metrics that apply to a CEDEAR are determined by its
underlying asset class, not by "CEDEAR".** A CEDEAR over an ETF needs NAV, tracking
error and expense ratio; over a corporate bond, coupon and maturity; over shares,
EPS and dividends. The current data already contains two subtypes — Apple CEDEAR
(shares) and GLD/ETHA CEDEARs (ETFs, over a commodity and a virtual asset). A single
`instrument_subtype = CEDEAR` is therefore already insufficient today.

**2. The conversion ratio is explicitly variable, and ratio changes are formal events.**
Issuers must report the underlying quantity and conversion ratio **quarterly** to the
CNV and the market, and a change in the exchange ratio requires a Prospectus Supplement
— named alongside a split or extraordinary dividend of the underlying as a triggering
event.

**This settles Q-018 by regulation rather than inference: `ratio` as a single scalar is
insufficient.** It must be dated. Ratio changes have an announcement, an effective date
and a published value.

**3. Three distinct relationship kinds, legally and economically different** — so
Q-017's remaining sub-question is answered **yes**, they need separate edges:

| Relationship | Direction | Distinguishing features |
|---|---|---|
| **CEDEAR** | local certificate over *foreign* underlying | conversion ratio, custodian, issuer fees, sponsored/unsponsored |
| **ADR** | foreign certificate over *local* underlying | depositary and custodian banks, divergent-voting rules |
| **Doble Listado** | same shares listed in both venues | no ratio, no custodian, no wrapper |

The YPF and Banco Macro pairs in the current data are **not** the same relationship as
the Apple CEDEAR pair, and modelling them with one edge type would be wrong.

**4. CEVA is a new instrument class** — a local vehicle for creating passively-managed
ETPs, introduced by RG 1142/2026 and distinct from both CEDEAR and FCI. It carries its
own requirements: daily basket publication, indicative NAV, tracking-error disclosure,
securities-lending limits. Not V1, but it belongs in the taxonomy now rather than being
discovered later.

**5. CEDEAR total return ≠ underlying total return.** The issuer exercises the
underlying's rights and charges a fee on dividend payments. Any comparison of a CEDEAR
against its underlying that ignores issuer fees will overstate the CEDEAR.

**6. An authoritative non-Yahoo source exists.** The CNV's AIF disclosure system carries
prospectuses, supplements and material events; quarterly issuer reports carry ratio and
outstanding quantities. **Ratio history is publicly obtainable rather than something to
reverse-engineer from prices** — which matters, because reverse-engineering it is
exactly what P3 forbids.

### D-014 — Coverage is strong; the completeness reference I asked for was the wrong one

*Decided 2026-08-15. Closes Q-056. Substantially downgrades F-015.*

**Coverage census.** 11,319 Series; 74 with zero observations; 11,245 with ≥1; 9,418
with ≥250; 6,308 with ≥1,250. Overall range 2000-01-03 → 2026-08-14.

**F-015's stronger claim is wrong.** 99.3% of Series carry data. Search returning
thousands of dead ends is not a real risk — only 74 cases exist. The bulk load fetched
history, it did not create shells.

**F-015's weaker claim survives and is now quantified.** Sufficiency, not existence:

| Cannot support | Series | Share |
|---|---|---|
| any chart (0 observations) | 74 | 0.7% |
| a 1-year return (<250 bars) | ~1,827 | 16% |
| a 5-year CAGR (<1,250 bars) | ~4,937 | 44% |

So the gate is real but narrow: it suppresses *specific metrics* on a minority of Series,
rather than gutting the search experience. AC-04's type-based suppression needs a
sufficiency-based sibling, sized accordingly.

**The comparison I requested was confounded.** `backfill_start_date` was blanket-set to
`2000-01-01` during bulk import regardless of an instrument's real listing date, so
"requested vs received" measures the blanket setting, not provider behaviour. The 9,544
Series in the >365-day bucket are dominated by instruments that genuinely did not exist
in 2000 — five of the worst offenders were verified live and **all five matched Yahoo's
own `firstTradeDate` exactly**. Sampled, not exhaustive, so a real truncation case could
still hide in that population.

**The right completeness reference is `firstTradeDate`, which the provider already
supplies.** This refines the Tranche 2 ask: rather than a generic requested-vs-received
range, capture the provider's own first-trade date. Completeness then becomes exact
rather than inferential, and splits cleanly into two checks:

1. **Start completeness** — `MIN(observed_at)` against `firstTradeDate`. Catches ETHA-style
   truncation at the head of the range.
2. **Density** — actual bar count against expected trading days between min and max.
   Catches interior gaps, which the first check cannot see.

### D-015 — F-019 fails clean: dated ratios are mandatory. The architecture validated; one field's data model did not

*Decided 2026-08-15. Closes F-019 and Q-058. Escalates F-021 from unsourced to provably wrong.*

**Result.** implied_FX(t) = CEDEAR_ARS(t) × 20 ÷ AAPL_USD(t), computed over 1,575
overlapping trading days (2020-01-02 → 2026-08-14).

| Date | CEDEAR (ARS) | AAPL (USD) | Move |
|---|---|---|---|
| 2024-01-23 | 25,100.0 | 195.18 | — |
| 2024-01-24 | 12,697.5 | 194.50 | CEDEAR −49.4%, AAPL −0.35% |

A single, non-reverting step confined to the CEDEAR leg. Ten-day mean implied FX: 2,467
before, 1,273 after — a persistent level shift, not a glitch.

**The other 1,574 points validate the architecture.** Day-to-day changes average 1.18%
(median 0.77%), with the largest legitimate moves clustering on dateable Argentine macro
events — the August 2023 PASO, the October/November 2023 elections, the December 2023
devaluation. **The series genuinely tracks something CCL-like.** Identity model,
relationship edge, adjustment basis and provenance chain are all confirmed working end to
end. The failure is isolated to one field's temporality.

That distinction matters and should not be lost: **this is not "the approach is broken."
It is "the approach works and one field is modelled wrong."**

**Sharpening the estimate — for verification, not for use.** The single-day factor is
25,100 ÷ 12,697.5 = 1.9768; correcting for AAPL's own −0.35% move gives 1.9699. The
residual ~1.5% from a clean 2:1 is well within a single day's genuine CCL movement in
January 2024, weeks after the December 2023 devaluation. So the likely change is **exactly
2:1, ratio 10 → 20**, with real FX drift on top.

**That remains an inference and must not be displayed.** Published ratios are clean
values; a reverse-engineered 1.97 is not one. The hypothesis is worth carrying to the
authoritative record — an exact effective date of **2024-01-24** and an expected factor of
2 make that lookup cheap — but P3 forbids using it until confirmed.

**Correction to an earlier inference (F-019 update, same day).** Smoothness through AAPL's
2020 4:1 split was read as evidence that Yahoo's `.BA` feed rebases history. That was one
of two explanations, and the 2024 step now favours the other: since Yahoo demonstrably
does *not* rebase a ratio change, the 2020 smoothness is better explained by **the issuer
changing the ratio by exactly the split factor**, leaving the peso price continuous. The
provider is likely not adjusting the CEDEAR series at all — the issuer is absorbing
underlying corporate actions into the ratio.

**A generalisation that no non-Argentine source would surface.** Ratio changes have two
distinct causes:

1. **Underlying corporate actions** — split, extraordinary dividend, merger. Visible in a
   US corporate-actions feed.
2. **Local tradability adjustments** — when peso price levels rise, issuers halve the unit
   price by doubling the ratio. **Invisible to every non-Argentine source.**

The January 2024 event has no underlying corporate action behind it and follows the
December 2023 devaluation, which roughly doubled CEDEAR peso prices. It is very likely a
case of the second kind. **A US corporate-actions feed would never have caught it**, which
is precisely why the CNV AIF / BYMA ratio record is the authoritative source and not a
convenience.

**Consequences**

- **A-012 respecified.** No implied-FX figure may be displayed as fact until dated ratios
  exist. Per D-007's V0/V1 decision, the correct behaviour is **detect and quarantine**:
  flag the span, mark the boundary, refuse the calculation across it. This is the
  anticipated case, now instantiated.
- **F-021 escalates** from "undated and unsourced" to "demonstrably wrong for at least one
  historical span in live data."
- **Q-052 is validated and should be adopted.** The detector as specified — a large
  single-day move whose ratio sits near a simple integer or fraction — would have caught
  this automatically. 1.97 is near 2.
- **The authoritative source is connected to nothing.** Neither HistFinTS nor Workbench
  has any path to CNV AIF or BYMA ratio-change records. This is a new provider
  requirement, not a change to an existing one.

### D-016 — Detector run across the tracked CEDEAR universe; the implied-FX rate should be panel-derived, not pair-derived

*Decided 2026-08-15. Closes Q-059. Supersedes Q-052's original specification.*

**Results across all six tracked pairs.** Method: raw CEDEAR/US price ratios (a constant
scaling factor cannot affect day-over-day change, so real ratios were not needed), with
each top mover tested for **persistence** — 15-day mean before, immediately after, and
60–75 trading days later.

| Pair | Verdict | Evidence |
|---|---|---|
| AAPL | **Confirmed ratio artifact** | 2024-01-24, −49.4% vs US −0.35%, no reversion, ~1.94–1.98× |
| GLD | Clean | Largest move −12.1% barely shifts the trailing mean (1.025× / 1.058×) |
| ETHA | **Untestable** | Only 19 days of overlap — F-017 truncation. Unknown, *not* passing |
| BABA | Clean | −18.3% fully reverts by 60–75 days (1.003×) |
| BIDU | **Ambiguous** | 2020-04-14, +19.1% vs US +2.6%; sustained (1.27× / 1.34×) but not a clean rational factor |
| UBER | Clean | −8.9% is continuing drift (0.965× → 0.870×), a trend not a step |

**Detector specification updated.** Persistence is the discriminator. A large single-day
move is only a *candidate*; what separates a ratio change from a real FX swing is whether
the level shift survives 60–75 trading days. Move size alone flags all three of GLD, BABA
and BIDU without separating them.

**The panel principle — the significant conclusion.** An implied-FX series derived from a
**single pair** conflates two signals: the actual exchange rate, and everything specific
to that instrument. Derived from a **panel** of pairs, the two separate cleanly:

- **movement common to all pairs** = the real rate;
- **one pair's residual against panel consensus** = instrument-specific — ratio change,
  liquidity, corporate action, stale price.

This is a better design than A-012 as specified, and it does two jobs with one mechanism:
the consensus is the rate, and the residual *is* the ratio-change detector — more
sensitive than per-pair persistence testing, because it does not need a level shift to
survive months before it becomes visible.

**Immediate application to BIDU.** A CCL regime shift moves **every** pair at once; a
ratio change moves **one**. April 2020 sits in the COVID crash and a tightening of
Argentine capital controls, so the cross-pair check is likely decisive and costs nothing —
the series are already held.

**Scope, and why the rate is not projectable.** Of six tracked pairs: 1 confirmed wrong,
1 ambiguous, 1 untestable, 3 clean. This measures what is live today rather than
projecting onto the 1,491-symbol backlog — correctly stated. Worth adding that the sample
skews toward long-history, high-liquidity names, and that **tradability-driven ratio
changes accumulate with time listed and peso price level** (D-015). Exposure is therefore
estimable per name from listing age and unit price, rather than assumable as a flat rate.

**ETHA demonstrates that F-017 has analytical consequences, not merely cosmetic ones.**
The truncation does not just produce a short chart; it makes a validation impossible to
run at all.

### D-017 — BIDU is clean; the panel mechanism now serves three purposes, and its membership is time-varying

*Decided 2026-08-15. Closes Q-060 and the BIDU ambiguity. AIF worklist drops to one item.*

**Cross-pair coherence at 2020-04-14.** GLD (data from Dec 2024) and UBER (Jul 2022) are
*structurally absent* at that date rather than silent on it. AAPL and BABA both cover it:

| Pair | 15d before | 15d after | ratio | ~60–75d later | vs before |
|---|---|---|---|---|---|
| AAPL | 8.98 | 11.15 | 1.241× | 11.89 | 1.323× |
| BABA | 10.00 | 12.39 | 1.239× | 13.19 | 1.319× |
| BIDU | 8.09 | 10.27 | 1.270× | 10.80 | 1.335× |

All three converge on 1.32–1.34×. **A market-wide CCL widening, not an instrument-specific
ratio change.** An independent ratio change would not coincidentally land within 1.5% of
two unrelated instruments' organic drift.

The widening is also externally checkable: April–June 2020 covers the COVID crash and
Argentina's sovereign-default negotiations, a period of real and well-documented CCL
widening. **The panel is measuring something that happened.**

**The path difference is a second finding, not a footnote.** AAPL and BABA drift to the new
level over ~15 trading days (5.8% and 4.5% on the day itself). BIDU jumps +19.1% in a
single print, reaching in one day what the others took three weeks to reach. Same
destination, different path — the signature of **a thin instrument catching up to an
already-shifted level in one lumpy trade.**

**Consequences for illiquidity (Q-028, open since the first round, now with evidence).**
BIDU's series has stale-price characteristics, and the effects are not confined to this
date: volatility is understated between prints and overstated at them, correlation with
anything is attenuated, and a "single-day return" may be several days of movement
compressed into one print. Risk metrics computed naively on such a series are wrong in a
direction that looks like low volatility — the flattering direction, which is worse.

**The panel mechanism does three jobs, distinguished by residual behaviour:**

| Signal | Diagnostic |
|---|---|
| Movement common to all pairs | the real exchange rate |
| **Persistent** single-pair residual | instrument-specific level change — ratio change |
| **Transient** single-pair residual that closes | staleness / illiquidity |

One mechanism, three outputs, with the residual's *time signature* separating the last two.

**A new design constraint: the panel is time-varying.** Membership on 2020-04-14 is three
pairs, one of which is illiquid — an effective depth of two. Today it is six. So:

- consensus reliability varies across history and is thinnest exactly where history is
  longest;
- under P3 the displayed rate must carry its own derivation — **"derived from N pairs on
  this date"** is provenance, not decoration;
- a stale member corrupts consensus, so panel membership needs a liquidity criterion, not
  merely a data-availability one.

**AIF worklist: one item.** AAPL only, for the 2024-01-24 step.

### D-018 — Tranche 1 questions answered: `correction` is fully provenanced, MERGE repair is possible, and `ratio` is hand-entered with no "as of" concept anywhere

*Decided 2026-08-15. Closes Q-039, Q-050 and Q-057. **Unblocks Tranche 2.***

#### (a) `correction` — better provenanced than `observation` itself

`import_run_id` is a `NOT NULL` FK, present since the v1 baseline, and all five
observation fields are covered by the `CHECK` constraint. Verified live: **0 of 13,302
rows carry a null `import_run_id`**. Field distribution — volume 4,966 · value 3,026 ·
low 2,287 · high 2,183 · open 840.

**Consequences**

- **F-001's migration scopes cleanly to `observation` alone.** Nothing per-field is
  missing on the correction side.
- **An odd but useful asymmetry:** the audit log is better provenanced than the primary
  data. Where an observation *has* been corrected, the correcting run is recoverable via
  `correction.observation_id → import_run_id`. That is partial provenance for corrected
  rows only, and it identifies the *correcting* run, never the *originating* one — so it
  narrows F-001 without closing it.
- **Q-053's denominator partly resolves.** The 13,302 figure is **field-level**, not
  observation-level. Volume alone accounts for 4,966, so at least that many distinct
  observations were corrected in an 11-day window. Against a rough ~90,000 fresh
  observations in that period, the provisional rate is on the order of 5% — enough to
  justify F-011's provisional display state, and an order of magnitude rather than a
  measurement.

#### (b) MERGE repair is possible, one hop away

No `merged_into_series_id` on `series`; the pointer lives on `series_merge`
(`survivor_series_id`, `absorbed_series_id`, `match_candidate_id UNIQUE`, `merged_at`).
Repair path: `SELECT survivor_series_id FROM series_merge WHERE absorbed_series_id = ?`.

**Two cautions not to lose.**

1. **Resolution must be recursive, not a single lookup.** Nothing prevents a survivor
   from later being absorbed itself. A reference to A where A→B and B→C needs to follow
   both hops. The repair is a `WHILE`, not a `SELECT`, and should carry a cycle guard
   even though a cycle ought to be impossible.
2. **`series_merge` is empty in production.** Per D-009 this is a schema- and
   trigger-level answer, not a demonstrated one — "not yet exercised", not "works".

A-002 can now be written concretely against this path.

#### (c) `ratio` is hand-entered, and no "as of" concept exists anywhere

Both code paths traced. The auto-resolve path sources from `record.underlying_ratio`,
which `BymaSnapshotReader` **never populates** — it is always `None` from a real BYMA
fetch, and the guard leaves BYMA relationship matches pending for a human. The only
remaining path is `resolve_set_underlying(candidate, ratio)` called with a
human-supplied float via CLI, GUI or web.

**So: hand-typed. Not carried from a provider field, not scraped, not inferred.**

And the gap is categorical, not per-row. There is no effective-date field, no history
table, and no audit trail: `entity_change_log` only ever writes `ProviderSymbol` rows,
confirmed by zero rows of any other `entity_type` in the live database. **"As of when" is
not a question this system can answer for any Series.**

**Consequences**

- **F-021 escalates to confirmed at the design level.** D-015 proved the value is wrong
  for at least one historical span; this proves the column cannot be right in principle.
- **Dated ratios do not belong in Tranche 2.** Per D-008's amended criterion, Tranche 2's
  concern is whether `observation` is trustworthy. Ratio temporality is relationship
  modelling — a different concern, on its own timeline, exactly as D-010 held for
  settlement.
- **Ownership follows D-007.** Ratio history is not a Yahoo provider event; it comes from
  the CNV AIF. Until a provider path exists, **Workbench owns the effective-dated ratio
  model**, sourced manually. If BYMA is ever made to populate `underlying_ratio`, the
  raw-capture layer becomes HistFinTS's under the same rule that governs corporate-action
  events.
- **The current scalar is untrusted input, not authoritative data**, and should be treated
  as a hypothesis pending the AIF lookup.

---

### F-022 · M — P4 has no data class for manually-asserted values

P4 distinguishes **Observed**, **Calculated** and **Reported/Estimated**. A hand-typed
conversion ratio is none of these: nobody observed it, nothing derived it, and no external
organisation reported it. It is a fourth thing — **Asserted**.

These values exist today, are load-bearing (the entire CEDEAR relationship rests on one),
and are indistinguishable in the UI from provider-supplied facts. Under P3 an asserted
value needs the most conspicuous provenance of all, since it has the least behind it.

### D-019 — Tranche 2 reduces to one migration item; two of three were already in the schema

*Decided 2026-08-15. Supersedes the first draft of `REQUEST-tranche2-migration.md`.*

| Proposed item | Actual status |
|---|---|
| `observation.import_run_id` | **Already exists** since v1, `NOT NULL` FK. Withdrawn — see F-001 retraction. |
| Provider first-trade date | **Column exists** — `provider_symbol.first_available_date`/`last_available_date`, migration `0004`, fully wired through domain model and repository — but **never written by any code path**. 0 of 1,493 rows populated. Not a migration; an application-logic gap. |
| Adjustment basis | **Genuinely missing.** The only real schema change of the three. |

**Reachability is the open part of item 2.** The existing column sits on `provider_symbol`,
which belongs to the Catalog subsystem. Workbench references `series_id` across the
boundary and does not otherwise touch that table. So populating it may not help unless it
is reachable from the series side — and if it isn't, *that* is the actual gap, not the
column's absence.

**Framing that survives review unchanged:** additive-only as a constraint, and the
exclusion of dated ratios, settlement modelling and corporate-action reconciliation. Tying
this migration to the CEDEAR-ratio work — still one open item on the AIF worklist — would
bind it to a far less certain resolution timeline.

---

### D-009b — The mirror of D-009: absence in documentation is not absence in the system

*Recorded 2026-08-15, extending D-009 after the F-001 retraction.*

D-009 established that a clean empirical result is not evidence of safety. The F-001
retraction exposes the symmetric error, and this review has now made it three times in the
same direction:

| Finding | Claimed | Actual |
|---|---|---|
| F-013 | live defect | dormant — no time had elapsed |
| F-015 | thousands of empty Series | 74 |
| **F-001** | **no provenance link exists** | **existed since v1** |

All three inferred a defect from incomplete evidence. **Inferring absence from silence is
the same error as inferring safety from a clean result** — both read nothing as though it
were something.

**The rule.** Before asserting that a field, table, constraint or code path does not exist,
read the schema or the code. A prose summary, a brief, or a description of columns is a
*summary*; its silence carries no information. Cite the file and line, or state explicitly
that the claim rests on documentation and has not been verified.

**Extension, 2026-08-15 — the rule governs proposals, not only claims.** A third instance
occurred: `REQUEST-event-capture.md` specified an `amount / currency` pair for dividend
events. A real Yahoo dividend event is `{ "amount": ..., "date": ... }` and carries **no
currency at all** — that lives on `chart.result[0].meta.currency`, elsewhere in the response.

This is the inverse of the first two failures. F-001 asserted a schema field's *absence*; the
dropped Tranche 2 item asserted a filing's *contents*; this asserted a provider payload's
*presence*. Same root — a reasonable-sounding model trusted over the artifact — in the
opposite direction.

**So: before specifying any field sourced from a provider response, verify the provider
actually sends it.** A proposal is a claim about the world and carries the same burden. Note
also that D-009b was already written when instances two and three occurred, which suggests
the rule needs applying at *drafting* time, not only when reviewing someone else's assertion.

**Instance three had a second lesson.** The proposed field would have been filled from
`meta.currency` at capture time — which is *interpretation*, in a filing whose entire
argument is that interpretation is out of scope. **A shape that quietly violates its own
document's principle is a signal the shape is wrong, not that the principle needs an
exception.**

### D-020 — `DEFECT-F009.md` ships **with** a constructed reproduction, not as a procedure

*Decided 2026-08-15.*

Both options were available: send the report now with §3.1 as a procedure for maintainers
to run, or hold it until the reproduction has actually been executed.

**Ship with results.** The argument is not general rigour — it is specific to this filing's
position in this body of work.

1. **The defect is unfalsifiable by observation (D-009).** Nothing in this database is old
   enough to have triggered it. Construction is not a nice-to-have confirmation; it is the
   *only* route to establishing the claim at all. A procedure without results ships an
   unestablished assertion.
2. **F-001 was retracted the same day, from the same body of work.** It rested on analysis
   plus code reading without checking the artefact — precisely the method behind F-009's
   current evidence. Asking a maintainer to trust that method again, immediately after it
   produced a wrong answer, is asking too much. **The next filing has to be airtight.**
3. **Marginal cost is lowest now.** Tooling is in hand, live provider access is working,
   context is loaded. Later this is a re-setup.
4. **It is not extra work.** A-009 already queues a permanent regression harness covering
   the split and revision cases. Running §3.1 is that harness's first execution, not a
   detour.

**Decoupling, so this does not stall the rest.** `REQUEST-basis-factsheet.md` is
independent of the reproduction and should go **now**. Only the defect report waits.

**On the report's construction** — the scope note, the pre-emptive "why production looks
clean today" section, remedies offered as options rather than a directive, and the
explicit out-of-scope list are all load-bearing. They exist to answer a skeptical
maintainer's first three objections before they are raised. Preserve that shape in future
filings.

### D-021 — Basis fact sheet complete. Three separate gaps are one systematic characteristic

*Decided 2026-08-15. Fulfils `REQUEST-basis-factsheet.md` internally — it no longer needs
sending. Removes the last dependency from the adjustment-basis migration.*

| Provider | Price basis | Revision behaviour | Confidence |
|---|---|---|---|
| Yahoo Finance | split-adjusted, dividend-unadjusted | rebases history to current split basis at query time | **code + data confirmed** |
| Alpha Vantage | raw/unadjusted (`TIME_SERIES_DAILY`) | unknown | code-confirmed only, no data present |
| FRED | n/a — value-only | revises retroactively; adapter passes **no vintage parameters**, so values freeze at first-fetch vintage | **code-confirmed** |
| BYMA | n/a — **supplies no observations at all** | n/a | **code-confirmed** (excluded from `PROVIDER_REGISTRY`) |
| ECB / World Bank | n/a — value-only | assumed to revise; **not verified** | assumed |
| Stooq | **UNKNOWN** | **UNKNOWN** | attempted; blocked by bot detection |

#### The pattern — three instances, one characteristic

| Provider | Data offered | Adapter behaviour |
|---|---|---|
| Yahoo | `events` (splits, dividends) — **requested on every fetch** | never parsed (F-012) |
| FRED | vintage access via realtime parameters (ALFRED) | never requested |
| BYMA | reference data incl. `underlying_ratio` | reader exists, field never populated (D-018c) |

**These are not three bugs. They are one design characteristic: adapters capture prices
and discard everything else the provider offers.** Every gap this review has spent rounds
on — corporate actions, vintages, conversion ratios — has an available source that is
already reachable and simply not taken.

That reframes the asks. F-012 is not "add a corporate-actions feature"; it is "stop
discarding what already arrives." The same sentence covers all three.

#### BYMA is a reference provider, not a price provider

Every BYMA-linked Series draws its prices from a Yahoo `.BA` cross-listing. This explains
F-020 (series 11305 with a BYMA-only assignment and zero observations) and confirms
D-011's amendment: **the BYMA adapter path remains entirely unexercised for observations.**

**The schema does not model provider *role*.** `provider` conflates sources of identity
and reference data with sources of observations. Consequences: the adjustment-basis field
is meaningless for BYMA; a `provider_assignment` can exist with no possible price path;
and — the sharp one — **BYMA is exactly where conversion ratios should come from, and it
is the one provider that supplies no observations.** The ratio problem and the price
problem need different provider paths.

#### F-013 upgraded — mechanism confirmed, occurrence still not demonstrated

`providers/fred.py` calls plain `series/observations` with no vintage parameters, so it
always fetches current vintage. Combined with `_determine_range()` never revisiting a
stored date, each value freezes at whatever vintage was current on its first-fetch day.

F-013 now sits at exactly F-009's epistemic level: **mechanism proven at code level,
occurrence not yet demonstrated** (D-009 — nothing here is old enough). Case (b) of the
A-009 harness settles both.

#### Stooq — a guard, not a blocker

The basis is unknown and the empirical check was blocked by client-side proof-of-work bot
detection. Correctly recorded as attempted-and-blocked rather than guessed from
reputation.

**It does not block the migration**, because no Stooq data exists in the database today.
It does require a rule: **a provider whose basis is UNKNOWN must not serve as a fallback
until its basis is established.** That converts an unbounded risk into a controlled one
without waiting on anything.

*Cheaper route than scraping:* try the fetch through Stooq's own adapter rather than curl.
If the adapter has a working path, use it to run the same split check. If it does not,
Stooq is non-functional as a provider today and the question is moot either way.

### D-022 — F-009 and F-013 confirmed by construction; the mechanism is narrower and sharper than described

*Decided 2026-08-15. Closes Q-063. `DEFECT-F009.md` is complete and sendable.*

**Case (a) — split.** Stored values across the boundary: `630.00 → 632.50 → 129.04 →
134.18`, a ratio of 4.90 (a 5:1 split with ~2% genuine movement on top). **Zero
`correction` rows. Both `ImportRun`s recorded `SUCCESS`.**

That last sentence is the report's strongest single line: *the system reports complete
success while holding internally inconsistent data.*

**Case (b) — FRED revision — confirmed, via a negative result that was worth more than the
positive one.** The first attempt targeted a revision at the most-recently-stored date and
**failed to reproduce**. That failure pinned the real boundary.

**Mechanism refinement.** `_determine_range()`'s `start = latest` is **inclusive**, so the
single most-recent stored date is re-requested on every import and a revision landing there
*is* caught. The blind spot is narrower than previously described: **only dates strictly
older than the current latest are never seen again.**

Retargeting two months back — matching BLS's real prior-two-months payroll pattern —
reproduced cleanly: June froze at its original value while September was picked up normally
in the same call, with zero corrections.

**Why the refinement does not soften either defect.** A split rescales *all* historical
dates, every one of which is strictly older than the latest — hence case (a) reproducing
cleanly. Macro revisions land months back by construction. **The narrowing removes only the
case neither defect depends on.**

**All three configured providers have `default_revalidation_window_days = NULL`** — FRED,
Yahoo Finance and BYMA, confirmed live, no exceptions. Combined with the inclusive start,
the effective re-fetch window across the entire system is **exactly one date**.

**Coherence check against D-006, which now closes cleanly.** A one-date window predicts
corrections concentrated at ages 0 and 1, with a small tail at 2–3 from weekend and holiday
gaps where the latest stored date stays latest across several calendar days. Observed:
12,965 of 13,302 (97.5%) at ages 0–1, 337 (2.5%) at ages 2–3, **zero beyond**. The
distribution is what a one-date window predicts and is *not* consistent with any multi-day
look-back. D-006's inference is confirmed by an independent route.

---

### D-023 — CEDEARs are probably immune to F-009, and exposed to a different defect instead

*Recorded 2026-08-15. Answers the case (c) proposal.*

A CEDEAR ratio change is economically a split of the CEDEAR, so case (c) looks like a
natural extension. It would most likely return a **null result**, for a reason worth
recording rather than discovering by running it.

F-009 requires the *provider* to rebase history while HistFinTS holds unrebased rows.
D-015 established that Yahoo's `.BA` feed does **not** rebase for either CEDEAR cause: the
2024-01-24 ratio change appears as a visible step in the stored data, and the 2020
underlying split is continuous because the *issuer* absorbed it into the ratio. **No rebase
means nothing for the import to miss.**

**So the CEDEAR discontinuity is a provider-data characteristic, not an F-009 instance.**
The exposure is F-021 — an undated ratio applied across a boundary where it did not hold —
which is a modelling defect on the Workbench side, not an import defect upstream.

**A more valuable case (c): provider substitution.** The unmarked splice between a
split-adjusted provider and a raw one (D-005: Yahoo vs Alpha Vantage) has been asserted
since the earliest rounds and **never demonstrated**. Under D-009b that makes it an
unverified claim in a document about to be sent. The harness already has the right shape:
back a fixture Series with one provider, force fallback to the other, and observe whether
the handover produces a scale discontinuity with no marker and no correction row.

If it reproduces, the adjustment-basis migration gains a demonstrated justification rather
than a code-reading one.

### D-024 — Panel eligibility becomes an explicit, versioned object; eligibility must be evaluated **as of each date**

*Decided 2026-08-15. Closes Q-061 in principle; drafted in `SPEC-panel-eligibility.md`.*

**Accepted.** Making eligibility an explicit parameter set, and requiring every result to
report its own panel diagnostics, is right and directly serves P3: a panel-derived figure
carries its own derivation rather than presenting as a bare number.

**The long-history warning is the strongest element** and generalises beyond panels — *any*
metric computed over a window should report the cross-section it was computed on.

#### The structural correction: as-of-date eligibility

The proposal evaluates eligibility once. Evaluated as of today, a 20-year panel contains
only Series that **survived to today** — which is survivorship bias, reintroduced by the
mechanism built to warn about it. The warning would report *"18 of 137 have sufficient
history"* while silently omitting the ones that died before acquiring it.

**Eligibility must be evaluated as of each observation date.** Membership then varies
through the series — confirmed empirically by D-017, where the panel on 2020-04-14 has three
members and today has six — and the count becomes part of the output rather than a fixed
property of the run.

`series.status` makes this concrete: `DELISTED_OR_DISCONTINUED` Series retain valid history.
Whether they enter the panel is a survivorship decision, and it must be an explicit
parameter rather than an accident of which rows happen to be `ACTIVE` at query time.

#### Two different panels are being conflated

| | **Pair panel** (V0) | **Cross-section panel** (later) |
|---|---|---|
| Unit | a *pair* — CEDEAR ↔ underlying | a single Series |
| Eligibility | both legs present, relationship typed, ratio known **as of date** | screening criteria |
| Purpose | derive implied FX; residual detects ratio change and staleness (D-016) | studies, screeners, benchmarks |

The proposed parameters are cross-section screening criteria and contain **no notion of
pair-level eligibility** — which is what V0 actually needs.

#### Additions to the parameter set

- **`include_delisted`** — the survivorship switch, currently implicit.
- **`staleness_policy`, separate from `liquidity_requirement`.** D-017 showed BIDU is *clean
  but stale*: it passes any reasonable volume bar while its prints lag, and a stale member
  drags consensus toward its own lagged level. Tradability and price freshness are
  different properties.
- **`dispersion_threshold`, not merely reported dispersion.** Per D-016 a member's residual
  against consensus *is* the ratio-change detector, so dispersion is an alarm, not only a
  statistic. Above threshold, the result should be suppressed rather than displayed with a
  caveat.

#### Additions to diagnostics

- **Exclusion reasons, not just counts.** *"Excluded: 12 insufficient history, 4 stale, 2
  currency"* tells you whether the criteria are doing what you think; a bare `N excluded`
  does not.
- **The resolved membership list, stored with the result.** Re-running the same parameters
  in six months yields a different panel, because more Series will have crossed the history
  threshold. **A result is only reproducible if it carries both its spec and its resolved
  membership** — P3 applied to an aggregate, and a partial answer to F-003.

#### Two refinements

- **`minimum_coverage` needs a definition and has an upstream dependency.** Per F-017,
  coverage cannot currently distinguish *"the provider has little data"* from *"our fetch was
  truncated"* until `firstTradeDate` is populated.
- **Show the cross-section always; warn on threshold.** `N(20Y) << N(1Y)` is not
  implementable as written, and a conditional warning teaches users that its absence means
  no problem. Always display the count; escalate to a warning past a stated ratio.

#### Sequencing

`minimum_coverage` and `adjustment_policy` are **not implementable until Tranche 2 lands** —
they consume `firstTradeDate` and the adjustment-basis field respectively. The spec can be
written now; those two parameters activate later.

### D-025 — `first_available_date` is unreachable by design, not by a missing join; and the Catalog has produced none of the working data

*Decided 2026-08-15. Closes Q-062 and the adapter-version question. Re-scopes the Tranche 2
completeness item.*

#### (a) `import_run` records no adapter version or endpoint variant

Confirmed against the schema: `import_run` holds exactly `id, provider_assignment_id,
trigger_type, status, started_at, ended_at, created_at, updated_at`. If the adapter layer
changes what it requests — a different Yahoo endpoint, a changed interval mapping — nothing
distinguishes rows written before the change from those written after.

**Real but narrow today. It becomes material at a specific moment.** D-021 established that
adapters discard what providers offer (Yahoo events, FRED vintages, BYMA
`underlying_ratio`). The moment any of those is fixed, rows on either side of the fix carry
different provenance characteristics and nothing records which side a row falls on. **The
cost is dormant and lands retroactively** — the same shape as F-009.

Kept as a note, not a request. But if the adapter layer is being touched for any D-021 item,
adding the column in that same migration is nearly free and retroactively valuable, whereas
adding it afterwards is not.

#### (b) `provider_symbol` is structurally disconnected from most Series

`provider_symbol_id` appears **only** on `match_candidate` and `identifier` — never on
`provider_assignment` or `series`. The sole path from a `series_id` to a `provider_symbol`
runs through a resolved `match_candidate`.

Two consequences, the second sharper than the first:

1. **Series created via `add-series` have no path to any `provider_symbol` at all** — they
   never entered Catalog discovery. That includes **all eight CEDEAR pilot Series** and the
   A-009 harness fixtures.
2. **Even for a properly resolved Series, the reachable `provider_symbol` is the
   discovery-side one, which may not be the provider supplying observations.** GLD CEDEAR
   (11311) is the concrete case: discovered via BYMA, priced via a Yahoo `.BA` assignment
   that has no `ProviderSymbol` row at all, since Yahoo is never discovery-scanned. A
   populated `first_available_date` there would describe **BYMA's listing depth, not
   Yahoo's** — the wrong provider for the truncation question entirely.

**Re-scope confirmed.** The completeness marker must live on `provider_assignment`, the row
that actually determines who supplies observations. The existing `provider_symbol` columns
are not wrong; they answer a different question — discovery-side listing depth — and can
stay.

#### (c) The finding underneath both: two disjoint populations of Series

Series enter the database by two routes that share almost nothing:

| Route | Identity provenance | Currently holds |
|---|---|---|
| Catalog discovery → `match_candidate` → resolution | `ProviderSymbol` lineage, reproducible | **none of the working data** |
| `add-series` direct entry | hand-typed, no lineage | all 8 CEDEAR pilot Series, all fixtures |

Combined with D-011 (1,491 BYMA symbols discovered, 11 candidates, 0 resolved):
**the Catalog pipeline has produced none of the data the Workbench would actually use.**
Every currently-usable Series was created by direct entry.

**This substantially expands F-022.** The **Asserted** data class is not one ratio field.
For the direct-entry population, the *Series identity itself* is asserted — label, type,
currency, and the provider's raw ticker are all typed in by a human, with no discovery
lineage and no `entity_change_log` trail (D-018c confirms that log only ever writes
`ProviderSymbol` rows).

So the V0 demo rests on asserted identity, an asserted relationship, and an asserted ratio.
Hand-curation is legitimate — 2 of 10 hand-picked names were correctly rejected (F-018), so
human judgement is doing real work. **But under P3 and P4 it must be labelled, and the
labelling surface is much larger than a single field.**

### D-026 — Direct entry is permanent by design; asserted identity becomes the first Tranche 3 item

*Decided 2026-08-15. Closes Q-065. Completes the shape of F-022.*

**Direct entry is foundational, not provisional.** On `master`, `SeriesService.add_series`
(UC-1) was the *only* creation path and no Catalog subsystem existed. Catalog was built
**alongside** it to solve a different problem — *"here are 1,491 unknown tickers, work out
what they are"* — while direct entry serves *"I already know exactly what this is."*
Nothing marks `add_series` deprecated or provisional.

**Nothing to unwind for the eight pilot Series.** Re-creating them through Catalog
resolution would produce *worse*-founded identity, not better: each `.BA` ticker was
verified live against the provider before creation, with two of ten rejected on that basis.
That is stronger evidence than an automated Tier 2/3 match. The path was right; it simply
has nowhere to record what was done.

#### The inversion — the sharper form of the gap

A Catalog-resolved Series carries a `MatchCandidate` with `evidence_tier` and
`rule_reference` recording *why* a mapping was believed. A directly-added Series carries
nothing: `add_series` and `add-provider-assignment` persist the assignment and no rationale.

So **evidence quality and evidence recording are inversely correlated.** The path producing
the strongest evidence — a human checking a live source and rejecting two candidates —
leaves the weakest record, while the weaker automated path leaves a full trail. For any
`ProviderAssignment`, *"a human verified this against a live source"* and *"someone
guessed"* are indistinguishable in the schema.

#### The rejections are evidence, and they are lost entirely

`FXI.BA` resolves to a different company; `PBR.BA` has one bar of history. That is
**negative evidence of real value** — it records that a plausible ticker was checked and
found wrong.

The Catalog path can hold a rejected candidate. **The direct-entry path has no rejection
concept at all**: a Series is either created or it isn't, and the "isn't" leaves no trace.
At F-018's observed ~20% rejection rate on hand-picked names, **a fifth of all curation
work produces knowledge that is discarded the moment it is produced** — and the next person
to consider `FXI.BA` will find no sign it was ever examined.

#### Assertions decay

A verified mapping is not verified forever. Ticker recycling is real (Q-019) and F-018
confirms collisions occur in this universe. So an assertion record needs `verified_at` and
ideally a re-verification cadence — otherwise a mapping checked once in 2026 is treated as
permanently sound.

#### Proposed record shape

More than an audit log, and closer to a `MatchCandidate` for manual work:

```
asserted_by / asserted_at
verified_against        # "live Yahoo fetch", "BYMA panel", "prospectus"
evidence_observed       # "3,637 bars from 2011-09-26; issuer name matches"
evidence_tier           # comparable to the Catalog's own scale
rejected_alternatives   # candidate + reason — the currently-discarded half
verified_at / reverify_after
```

#### Placement and timing

**Tranche 3, not Tranche 2.** This is identity provenance; Tranche 2's concern is
observation trustworthiness. Bundling would repeat the error D-010 and D-019 both caught.

Not a defect — nothing is wrong, only unrecorded — but with a **cheap-now, expensive-later**
profile, since evidence not captured at assertion time cannot be reconstructed. Practical
step available immediately, independent of any schema: **record the eight pilot Series'
verification evidence and the two rejections in a document now**, before it exists only in
one person's memory and this transcript.

#### F-022 completed

The **Asserted** class covers Series identity, provider assignments, the CEDEAR
relationship and the ratio. And unlike Observed, Calculated or Reported, **Asserted carries
an internal quality dimension** — verified-against-a-live-source and guessed are both
assertions. That variation is precisely what the record above exists to capture, and why a
single "manually entered" flag would not be sufficient.

### D-027 — Event capture filed; capture-vs-reconciliation generalised from corporate actions to all provider data

*Decided 2026-08-15. Filed as `REQUEST-event-capture.md`.*

**The design fork resolved: dedicated table, not an extension of `entity_change_log`.**

D-007 already settles it, in its own words: raw provider events have *"the same epistemic
status as an observation: recorded, not interpreted."* `entity_change_log` records **changes
to entities inside this system**. A split or dividend is not that — it is an observed fact
about the outside world. **Observations do not live in the change log, and events should not
either.** The category argument is decisive; query pattern, typed structure, coupling and
provenance chain all point the same way, and the reuse argument is weak anyway since the log
is hardcoded to `entity_type='ProviderSymbol'` and needs changing either route.

**Naming note carried into the filing.** `provider_event` over `corporate_action` — the
former says *"this is what a provider told us"*, the latter implies a reconciled domain fact.
Since reconciliation is explicitly a different job with a different owner, a name marking
this as the raw-capture layer is worth having.

**A free backfill exists, and it is already on the table.** A parse-only fix captures events
going forward and leaves history empty. Yahoo returns events for whatever range is requested,
so a full-range re-fetch recovers them — **the same operation as remedy R1 in
`DEFECT-F009.md`.** One full-range re-fetch would simultaneously repair the scale
discontinuities, surface them as correction rows, and backfill the entire event history.
Three jobs, one operation.

---

### D-028 — The capture / reconciliation split applies to *all* provider data, not just corporate actions

*Recorded 2026-08-15. Generalises D-007.*

D-007 drew the line for corporate actions: HistFinTS captures what a provider reports;
Workbench reconciles and derives. That distinction recurs for every item in the D-021 family
and should be applied by default rather than re-argued each time.

| Provider data | **Capture** — HistFinTS | **Reconciliation** — Workbench, separate decision |
|---|---|---|
| Yahoo `events` | persist splits/dividends as reported | apply them to adjust or rebase a series |
| FRED vintages | record which vintage a value came from | decide which vintage a given analysis should use |
| BYMA `underlying_ratio` | persist the reported ratio and its date | apply the ratio in force at each observation date |

**Why this matters procedurally.** Tranche 2's exclusion note collapsed both halves into the
phrase *"corporate-action reconciliation"* and thereby dropped a capture item that had
already been decided. The two halves have different owners, different justifications and
different timelines — **a filing that excludes one must say which one.**

**Standing rule.** When a provider offers data the adapter discards, the default position is:
*capture is upstream and cheap; reconciliation is downstream and its own decision.* File them
separately, and never let an exclusion note cover both without naming them.

### D-029 — Completeness metadata belongs on the operational path; "unresolved" becomes a first-class third state

*Decided 2026-08-15. Sharpens D-025(b) and re-scopes the Tranche 2 completeness item.*

#### The placement principle, generalised

The schema carries **two distinct concept graphs** that meet only at `Series`:

```
Catalog identity / discovery          Operational data acquisition
    ProviderSymbol                        Series
        ↓                                     ↓
    match_candidate                       ProviderAssignment
        ↓                                     ↓
    Series                                ImportRun
                                              ↓
                                          Observation
```

They answer different questions. *"When did BYMA discover this ticker?"* is a Catalog
question. *"According to the assignment actually supplying these observations, when did this
listing become available?"* is an operational one. **They are not interchangeable facts.**

**Standing placement rule:** any metadata consumed by the analytical layer belongs on the
**operational** path, because the analytical layer consumes observations. This generalises
beyond the completeness marker and should be applied by default.

#### The hedge resolved: `provider_assignment`, definitively

Availability is a property of *"this provider's listing for this instrument"*. Not
`import_run` — it is stable across fetches, not per-fetch. Not `series` — a Series may carry
several assignments with genuinely different availability. `provider_assignment` is the only
row with the right cardinality, and it is reachable from every Series regardless of creation
path, which `provider_symbol` is not.

#### The third state — and it is permanent, not transitional

```
no trustworthy availability metadata
            ↓
   cannot distinguish
            ↓
"insufficient history"  vs  "incomplete coverage"
            ↓
       report UNRESOLVED
```

Reporting *unresolved* rather than guessing is the epistemically honest rule, and it slots
into the exclusion diagnostic as **its own category**, not a subdivision of coverage.

**It does not disappear once the marker ships.** Some providers cannot report availability at
all. Where an adapter has no such metadata to surface, `UNRESOLVED` is the permanent, correct
answer — which makes it a modelled state rather than a transitional convenience.

#### The fix is larger than a column, and the filing should say so

Not *"populate an existing column"*, and not merely *"add a column"*. To be reachable from
every Series **and** describe the actual observation source, the value must be populated
per-assignment at import time from each adapter's own metadata — Yahoo's `meta.firstTradeDate`,
FRED's observation range, and so on. **That is an adapter-interface change:** every adapter
must either surface availability metadata or explicitly declare that it cannot.

The honest characterisation belongs in the filing rather than being discovered during
implementation.

#### A new eligibility parameter falls out

`unresolved_coverage_policy: exclude | include_flagged`

Fail-closed is the principled long-run answer, but **zero rows carry availability metadata
today**, so applying it now yields an empty panel. The policy must therefore be a parameter
that tightens as coverage improves — not a fixed rule written once.

*Minor design note:* availability metadata is itself provider-reported and can change — a
provider may extend history backwards. Refresh it on each import rather than storing it once.

### D-030 — Availability and coverage are two levels, not three states; density detection depends on trading calendars

*Decided 2026-08-15. Adopts and corrects the availability/coverage vocabulary.*

#### The standing rule, adopted

> **Known availability → measurable coverage → diagnosable incompleteness.
> Unknown availability → explicitly unresolved, never silently inferred.**

The vocabulary distinction holds all the way into the UI. *"This source has data from 2018"*
and *"HistFinTS holds data from 2020"* are different statements, and keeping them separate is
what lets the diagnostic say **coverage incomplete** rather than the false **insufficient
history**.

Also adopted: **provider-reported availability is observed metadata, not immutable Series
metadata, and MUST be refreshed when the assignment is imported.** And the eligibility policy
is part of the panel definition — two panels differing only in `unresolved_coverage_policy`
are different panels, which follows from D-024's requirement that a result store its spec.

#### Correction: this is two levels, not a three-value enum

`KNOWN` / `UNRESOLVED` / `INCOMPLETE` are not parallel. The first two are states of
**availability metadata**; the third is a state of **coverage**, derived from availability
plus stored observations.

```
Availability   (stored)     KNOWN | UNRESOLVED
                   ↓
Coverage       (derived, only when availability is KNOWN)     COMPLETE | INCOMPLETE
```

This matters for implementation: availability is persisted, coverage is computed at query
time. A single enum would force a stored value to be recomputed whenever observations change.

#### Provider availability is not instrument availability

*"The source says data should exist from 2018"* overstates what the provider reported. Yahoo's
`firstTradeDate` says when **Yahoo's coverage** begins, which for a `.BA` cross-listing may
well postdate the actual BYMA listing.

Honest phrasing: **"this source has data from 2018."** The stronger claim is an instrument
fact, and providers do not report instrument facts — they report their own coverage. Same
discipline as P1: provider statements are not identity statements.

#### `INCOMPLETE` is not atomic

Two distinguishable failures with different causes:

| | Detection | Typical cause |
|---|---|---|
| **Head truncation** | `MIN(observed_at)` later than availability start | fetch truncation (confirmed live at 19 of ~408 bars) |
| **Interior gaps** | bar count below expected trading days in range | halts, holidays, or fetch failure |

A series can start correctly and still be full of holes. The diagnostic should say which.

#### The unnamed dependency: density detection needs a trading calendar

*"Stored observations don't **adequately** cover that period"* has the same defect as
*"substantially reduces"* — it needs a number. Worse, the underlying quantity is not currently
computable: **expected trading days requires the venue's trading calendar**, and BYMA and
NYSE holiday sets differ. No calendar table exists, and no provider supplies one.

**This links directly to Q-027, open since the first round and never addressed.** Calendar
alignment was raised for correlation and beta; it turns out density detection needs it too.

Until a calendar exists, density is a **heuristic, not a measure** — a ~252-day annual
approximation is adequate to flag a series 10%+ below expectation for review, and inadequate
to assert a precise gap count. It should be labelled as a screen rather than presented as a
figure.

### D-031 — Availability/coverage model converged; density screen boundary made explicit and load-bearing

*Decided 2026-08-15. Finalises D-029/D-030's three-layer model. No corrections — refinements
only, to prevent drift at implementation time.*

**Converged model, adopted as final:**

```
ProviderAssignment
      │
      └── availability_status: KNOWN | UNRESOLVED     (stored)
                  │
              [KNOWN]
                  │
                  ▼
          coverage: HEAD_TRUNCATED | INTERIOR_GAPS | ADEQUATE     (derived, not stored)
                  │
                  ├── head truncation:  MIN(observed_at) > provider_coverage_start
                  ├── density screen:   observed ≈ expected(~252/yr)   — heuristic
                  └── interior gaps:    requires venue trading calendar → Q-027
```

**Governing sentence, to appear verbatim in the eventual spec:**

> Coverage density is a screening diagnostic until an appropriate trading-calendar
> capability exists. It MUST NOT be presented as an authoritative count of missing
> observations or trading-day gaps without a calendar defining the expected observation
> dates.

**Three points worth locking down now, before implementation, so they cannot drift:**

1. **`coverage` is computed, never persisted.** Storing it would let it go stale the moment new
   observations arrive or a correction lands. Every prior round has said this; stating it once
   more as a hard implementation constraint, since a cached "coverage" column is exactly the
   kind of convenience shortcut that reintroduces the staleness this model was built to avoid.
2. **`ADEQUATE` needs the same discipline as the other two states.** A series can pass the
   density screen and still contain interior gaps too small for a ~252-day approximation to
   surface. `ADEQUATE` therefore means *"the screen found nothing,"* not *"coverage is
   confirmed complete."* The UI must not imply verification the screen cannot provide — the
   same asymmetry already established for `UNRESOLVED` applies here in the positive direction.
3. **Density and interior-gap detection are himself two different confidence levels, not two
   names for the same check.** Density is available now, heuristic, and appropriately labelled
   a screen. Interior-gap analysis is exact but blocked entirely on Q-027. A UI that shows both
   under one "coverage" heading without distinguishing confidence would quietly launder a
   heuristic into an authoritative-looking result — precisely what the governing sentence
   above exists to prevent.

**Status: this branch of the review is complete.** The model is layered correctly, the
epistemic boundary is explicit, and the one real dependency (Q-027) is named and already
logged. No further design work needed here — implementation is now gated on Q-027 (interior
gaps) and Tranche 2 (availability metadata itself), not on further specification.

---

### D-032 — The F-009 evidence chain is code-complete upstream and **absent from the live database**

*Decided 2026-08-17. Supersedes the stale parts of D-019 and D-021. Prerequisite for
`SPEC-f009-evidence-consumption.md`.*

**Context.** The directive that opened this increment was to build "the minimum Workbench
capability needed to consume the **completed** HistFinTS F-009 evidence chain." Before
designing against it, the chain was inspected in the live `histfints-v3` checkout
(`E:\Carlos\Documents\Mi Software\Proyectos\histfints-v3`) and in the production database.

**What has landed in code since 2026-08-15.** Materially more than D-019/D-021 record, and
those two entries are now partly stale:

| Item | D-019/D-021 said | Current fact | Citation |
|---|---|---|---|
| Adjustment basis | requested, not landed | migration written; `provider.adjustment_basis` + `provider_assignment.adjustment_basis_override`, 5-value CHECK, **no DEFAULT, backfill deferred to application logic** | `persistence/migrations/0011_add_adjustment_basis.sql:22–33` |
| Retroactive-change detection (R1) | detection "must live in Workbench or nowhere" (D-006) | `RevalidationService` exists — provider risk tiers, per-provider windows (Yahoo 730d, FRED 365d), 0.1% tolerance | `application/revalidation_service.py:23–63` |
| Correction audit trail | only the v1 `correction` table | new `observation_correction` + `revalidation_run` tables | `migrations/0012_add_revalidation_tracking.sql:5–49` |
| Yahoo events (F-012) | "requested on every fetch, `_to_records()` never reads it" | **partly remedied**: a new `get_splits_and_dividends()` parses `events.splits`/`events.dividends`; `_to_records()` still ignores them and the method issues its **own second chart request** | `providers/yahoo_finance.py:70–92`, `95–126`; `_to_records` at `128` |
| FRED vintages | "never requested" | **landed**: `get_vintage_dates()` hits `/fred/series/vintagedates`; `get_observations_at_vintage()` exists with `realtime_start`/`realtime_end` | `providers/fred.py:9`, `67–85`, `87–106` |
| Provider-event storage | requested (`REQUEST-event-capture.md`) | `provider_event` table + `ProviderEvent` domain entity + repository, with mandatory `acquired_at`, `provider_source_id`, `provenance_note` | `migrations/0013_add_provider_event.sql:5–23`; `domain/provider_event.py:20–52` |
| BYMA `underlying_ratio` | reader exists, field never populated | **unchanged.** `underlying_ratio` exists only on the `RawCatalogRecord` port (`application/ports.py:236`) and is populated **only** by the hand-authored JSON reader (`infrastructure/json_snapshot_reader.py:58`). `byma_snapshot_reader.py` never sets it. | as cited |

HistFinTS's own status doc agrees: R1, R2a, R2b-FRED and R2b-Yahoo are marked
**Implemented**, R2b-ECB **Not viable** (ECB publishes no revision data), R3 **out of
scope** — `histfints-v3/docs/KNOWN_LIMITATIONS.md:71–82`.

**The decisive fact, which the directive's phrasing conceals.** None of it is in the
database the Workbench would ATTACH to.

```
sqlite3 -readonly "C:/Users/CarlonTinto/AppData/Local/histfints/histfints/histfints.db" \
  "PRAGMA user_version;"                                   -->  10
  "SELECT COUNT(*) FROM sqlite_master WHERE name='provider_event';"        -->  0
  "SELECT COUNT(*) FROM sqlite_master WHERE name='observation_correction';"-->  0
  "SELECT COUNT(*) FROM sqlite_master WHERE name='revalidation_run';"      -->  0
  "PRAGMA table_info(provider_assignment);"  --> no adjustment_basis_override,
                                                 no last_revalidated_at
  "PRAGMA table_info(provider);"             --> no adjustment_basis
```

`user_version = 10` with migrations 0011, 0012 and 0013 present on disk means
`apply_pending_migrations()` (`persistence/migrations.py:20–29`) has not been run since they
were written. Corroborated independently by the backup trail in the data directory, which
stops at `histfints_backup_before_migration0010_20260812_182934.db` — and HistFinTS's own
convention is to back the file up before applying a migration for real
(`histfints-v3/CLAUDE.md:63–70`).

**Decision.** The F-009 evidence chain is **implemented but unexercised, and invisible
across the boundary.** Three consequences are binding on this increment:

1. **The Workbench cannot be designed against `provider_event`, `observation_correction` or
   `revalidation_run` as present data.** A read-only ATTACH against today's file fails on
   `no such table`. Any query touching them must be behind a schema-presence probe, and
   their absence must resolve to **`insufficient evidence`**, never to "not explained."
2. **The evidence that *does* exist today is the v1 chain**, and it is real and populated:
   `observation.import_run_id` → `import_run.provider_assignment_id` →
   `provider_assignment.provider_id` → `provider`, plus 13,304 rows in the legacy
   `correction` table. Verified end to end:
   ```sql
   SELECT o.id, o.observed_at, ir.status, pa.provider_series_identifier, p.implementation_key
   FROM correction c JOIN observation o ON o.id=c.observation_id
     JOIN import_run ir ON ir.id=c.import_run_id
     JOIN provider_assignment pa ON pa.id=ir.provider_assignment_id
     JOIN provider p ON p.id=pa.provider_id LIMIT 5;
   -- 5597 | 2026-08-04T13:30:00+00:00 | SUCCESS | GLD | yahoo_finance
   ```
   A **new** and useful property, verified both ways: on a correction the upsert preserves
   the *original inserting* run, because `_reconcile()` returns the loaded `existing`
   Observation and never rewrites its `import_run_id`
   (`application/import_service.py:240–264`; `ON CONFLICT ... DO UPDATE SET import_run_id =
   excluded.import_run_id` at `persistence/sqlite_observation_repository.py:61–66` therefore
   writes the old value back). Confirmed in data: observation 5597 retains
   `import_run_id = 2` while its corrections were detected by run 4; observation 5598
   retains 6 against detecting run 8. So the Workbench gets **two** provenance anchors per
   corrected observation — who first wrote it, and who overwrote it.
3. **D-006 is not superseded.** `_determine_range()` still starts at
   `latest − default_revalidation_window_days`, with **zero** look-back when the field is
   unset (`application/import_service.py:183–200`, now at lines 183–201 verbatim), and
   `default_revalidation_window_days` remains **NULL for all three live providers**
   (`SELECT id, display_name, implementation_key, default_revalidation_window_days FROM
   provider;` → FRED, Yahoo Finance, BYMA, all empty). The 730/365-day windows in
   `RevalidationService.REVALIDATION_WINDOWS` are a *separate*, manually-invoked code path,
   not a change to import behaviour.

**Rationale for not waiting.** The tempting alternative was to declare the increment blocked
until migrations 0011–0013 are applied. Rejected: the increment's stated purpose is to prove
the Workbench can *consume* an evidence chain without confusing evidence with
interpretation, and the harder half of that proof — declining to explain a discontinuity
when the evidence is absent — is exercised **better** by today's database than by a
populated one. A consumer that only works once the evidence exists is a consumer that has
never been tested on the case that actually occurs. The migration is a prerequisite for the
*"explained"* verdict, not for the capability.

**Consequence — D-009 applies with unusual force.** Every `provider_assignment` in the live
database was created between 2026-08-04 and 2026-08-15
(`SELECT MIN(created_at), MAX(created_at) FROM provider_assignment;`), i.e. the oldest
provenance in the store is **13 days old** as of today. No tracked Series has lived through a
split under HistFinTS's own observation. A reconciliation run that returns "no discontinuity
found" therefore proves nothing about the detector; the acceptance test must construct the
discontinuity, not look for one.

---

### D-033 — Workbench references upstream evidence by key; four epistemic layers stay separate and the verdict vocabulary stays at three values

*Decided 2026-08-17. Governs `SPEC-f009-evidence-consumption.md`. Depends on D-032.*

**Context.** Having established what is actually readable (D-032), the question was what the
Workbench should *store*. Two shapes were available.

**(a) Materialise upstream evidence into Workbench tables** — copy the relevant
observations, corrections and (eventually) events into local tables at analysis time, so a
finding is self-contained and reproducible even if HistFinTS changes underneath.

**(b) Reference by upstream key, resolve at read time** — store only the identifiers
(`series_id`, the observation id range, the `import_run_id`s, and later
`observation_correction.id` / `provider_event.id`) plus the Workbench's own calculated
quantities, and re-resolve the evidence through the ATTACH on every display.

**Decision: (b), with one narrow exception.** The Workbench stores no upstream observation
values. It stores upstream *keys*, its own *calculated* quantities, and its own *findings*.
The exception: the specific numbers a finding asserts about (the values either side of a
discontinuity, and the computed step factor) are recorded as Workbench **Calculated** values
with their inputs named — because a finding that cannot restate its own arithmetic is not
traceable, and re-deriving it later against mutated upstream data would silently change what
the finding said.

**Rationale.** Shape (a) is the more obvious answer and it is wrong here for a specific
reason: HistFinTS observations are **mutable in place** — the whole content of F-009 — so a
Workbench copy is not a snapshot with integrity, it is a second version of the truth with no
way to tell which is stale. Duplication would also make the Workbench a de facto second
time-series store, which D-001 exists to prevent, and it directly violates the standing
instruction not to replicate historical observations. The cost of (b) is honest and
acceptable: a finding can become *unresolvable* if the upstream row it points at is archived
or overwritten. That is a state the UI must be able to render, and it is strictly better
information than a stale local copy that looks fresh.

**The four layers, in existing P4 vocabulary — no new terms.**

| Layer | P4 status | Owner | Example |
|---|---|---|---|
| **Provider evidence** | `Observed` | HistFinTS | a `correction` row; a `provider_event` SPLIT with ratio 4:1; an `import_run` and its `provider_assignment` |
| **Workbench calculation** | `Calculated` | Workbench | the step factor across 2024-01-24; the persistence test at 15 and 60 trading days |
| **Analytical finding** | `Calculated`, plus a named verdict | Workbench | "a −49.4% single-day step at 2024-01-24, persistent, not matched by any captured event" |
| **Research conclusion** | `Asserted` | the human | "this Series' pre-2024-01-24 history is unusable for return series" |

The load-bearing rule: **a finding may never be promoted to a conclusion by the system.**
Only a person writes an `Asserted` row, and it must cite the finding it rests on. The reason
is P4 itself — "explained by captured evidence" is a statement about *what HistFinTS
recorded*, not a statement about what happened in the world, and collapsing the two is
exactly the fabricated-lineage failure P3 exists to prevent.

**Why the verdict vocabulary stays at exactly three values.** `explained by captured
evidence` / `not explained by captured evidence` / `insufficient evidence`. Every richer
vocabulary that suggested itself — "partially explained", "explained with residual",
"probably a ratio change" — turned out to encode a *magnitude judgement* the Workbench is
not entitled to make from event metadata alone. A 4:1 split beside a 3.9× step is either
consistent within a stated tolerance or it is not; "partially" would let a mismatch pass as
half-explained and thereby launder an unexplained break. The residual magnitude is still
reported — as a `Calculated` number beside the verdict, where it belongs — but it does not
get its own verdict value.

**The third value is the important one.** `insufficient evidence` covers three distinct real
situations, and all three are live today per D-032: the evidence tables do not exist in the
attached database; they exist but hold nothing for this Series/period; or the provider is one
that supplies no revision data at all (ECB, per HistFinTS
`docs/KNOWN_LIMITATIONS.md:79–81`). Collapsing any of these into "not explained" would report
a HistFinTS gap as a data defect. The three underlying reasons are carried as a *reason
code* beside the verdict, not as extra verdict values.

**Consequence.** Against today's database (`user_version = 10`), the only verdicts reachable
for a price Series are `not explained by captured evidence` — when a discontinuity is found
and the legacy `correction` table has nothing at that date — and `insufficient evidence`.
`explained by captured evidence` is **structurally unreachable until migrations 0011–0013
are applied and the capture commands are actually run.** The increment must therefore be
accepted on the two reachable verdicts, with the third exercised against a constructed
fixture. Stated plainly so it is not later mistaken for a bug in the reconciler.

---

### D-034 — Proceed with `hf_reswb` evidence consumption against the currently deployed schema; migration application filed as a separate mechanical ask

*Decided 2026-08-17. Ratifies §8 of `SPEC-f009-evidence-consumption.md`. Depends on D-032, D-033.*

**The call.** Proceed with the `hf_reswb` reconciliation implementation now, against
`histfints.db` as it actually stands (`user_version = 10`, migrations 0011–0013 unapplied).
Do not wait for those migrations to land. `explained by captured evidence` is **structurally
unreachable** against the live database today; if the reconciler ever returns it against
production before the migration is applied, that is a reconciler defect, not a success — this
must be stated in the increment's acceptance criteria, not left implicit.

**Why proceeding is stronger than waiting.** An empty evidence store forces the first
implementation to demonstrate its two hardest behaviours immediately: `not explained by
captured evidence` (evidence tables readable, hold nothing at the boundary) and `insufficient
evidence` (tables absent, per D-032). A reconciler built and first tested against a
populated fixture would prove the *easy* verdict works and defer the two that actually occur
in production.

**Two-stage validation sequence, adopted as the plan going forward:**

```
Now:            empty/legacy evidence  -> not-explained / insufficient verdicts, full traceability
After upstream: migrated + captured evidence -> explained verdict, validated positive path
```

Stage 2 is not blocking on stage 1 shipping — it is the acceptance test for a *second,
later* increment, run once the migration below has landed.

**Separate mechanical ask, filed to HistFinTS.** Request application of migrations
0011–0013 to a **copy** of the production database, plus one run of the existing capture
commands, plus a report of what was actually captured. This is **deployment of code that
already exists**, not new HistFinTS development, and does not reopen the workstream halted
earlier this session. The production file itself stays untouched until the copy is
validated. Filed as `REQUEST-apply-migrations-0011-0013.md`.

**F-023, F-024, F-025 are binding on the implementation, not just noted.** Restated here so
they cannot be designed around by accident:
- **F-023** — `provider_event` carries no FK to any observation or correction. Event
  correlation is a `Calculated` join by `series_id` + date proximity + a stated tolerance,
  never treated as an `Observed` link.
- **F-024** — a FRED `REVISION` event records a vintage *date*, not a vintage *value*. A bare
  vintage date must not, by itself, produce `explained by captured evidence` — per D-033
  §4.4, it resolves to `insufficient evidence` / `PROVIDER_SUPPLIES_NO_REVISION_DATA` unless
  `get_observations_at_vintage()` values are actually fetched and compared.
- **F-025** — `provider_event.acquired_at` is capture time, not fetch time. Any
  before/after-import timing claim built on it must be labelled a proxy, not treated as
  exact.

All three converge on one rule, restated because it is the point of the increment: **evidence
presence is not evidence of explanation.** A row existing in `provider_event` is necessary but
not sufficient for the `explained` verdict; magnitude reconciliation within a stated tolerance
is what makes it sufficient.

**Documentation, not blocking.** `SPEC-f009-evidence-consumption.md` gets a row in
`CLAUDE.md`'s "Where things are" table (done alongside this entry). A-014 (correct
`HISTFINTS-BRIEF-v2.md`'s now-stale FRED-vintage and Yahoo-events claims) stays queued,
explicitly not folded into this implementation increment.

**Immediate actions.** (1) Development starts on the `hf_reswb` reconciliation
implementation against the current schema. (2) `REQUEST-apply-migrations-0011-0013.md` goes
to HistFinTS as a separate, mechanical, non-blocking ask.

---

### Inherited principles (ratified, not re-decided)

These come from the specification and are treated as binding constraints on all
subsequent decisions. Listed so the reviewer can test proposals against them.

| Ref | Principle | Spec |
|---|---|---|
| P1 | Series is the primary identity. A ticker is a provider-specific symbol and must never be the identity of an instrument. | §2 |
| P2 | The application must be instrument-aware: metrics meaningless for a type are suppressed, not blanked. | §2 |
| P3 | Every displayed externally-sourced or calculated value must have machine-accessible provenance. | §2 |
| P4 | Observed / Calculated / Reported-Estimated must never be silently conflated. | §2 |
| P5 | Yahoo Finance is a UX benchmark, not the domain model. | §2 |
| P43 | The UI is a *projection* of the domain. The domain must never be reshaped to mirror the UI. | §43 |

---

## 2. Open questions

Ordered by what unblocks the most downstream work. `blocking` means the answer
changes the architecture, not just the content.

### 2.1 Live

| ID | Status | Question |
|---|---|---|
| ~~Q-056~~ | closed | → D-014. |
| **Q-045** | **blocking · awaiting answer** | **The capability matrix.** D-013 gave the three axes — wrapper (direct/CEDEAR/CEVA/ADR) × underlying asset class (shares/ETF/bond/commodity/virtual asset/index) × venue+currency+settlement. What is missing is the matrix itself: which metrics are permitted, suppressed or replaced for each combination. Without it **AC-04 is untestable** and V0's Statistics section (Q-048) cannot be scoped. Open since the first round, and now fully equipped to be answered. |
| ~~Q-065~~ | closed | → D-026. |
| Q-064 | open · Workbench-side, no upstream impact | **Which panel is being specified for V0 — the pair panel only, or both?** V0 needs only the pair panel (implied FX, plus residual as ratio-change and staleness detector). The cross-section panel serves screeners and studies, which sit in V5. Specifying both now is scope creep; specifying only the pair panel risks a parameter set that will not generalise. My view: **pair panel only for V0**, with the cross-section spec written but explicitly deferred. |
| ~~Q-061~~ | closed in principle | → D-024. |
| ~~Q-063~~ | closed | → D-022. **Run the §3.1 constructed reproduction** before `DEFECT-F009.md` goes out: backfill a fixture Series to before a known split, run an incremental import past it, record the values either side. Decision recorded in D-020. Also worth capturing per-provider `default_revalidation_window_days` values while in there — the window may be zero for some, which would make their blind spot total. |
| Q-062 | open · gates the first-trade-date item only | **Is `provider_symbol.first_available_date` reachable from a `series_id`?** If Workbench can traverse series → provider_assignment → provider_symbol, then item 2 is purely an application-logic fix: populate the existing column from Yahoo's `meta.firstTradeDate`. If it is not reachable, the real gap is a completeness marker on the series/observation side, and the ask changes shape entirely. |
| Q-061 | open · Workbench-side, blocks nothing upstream | **What are the panel's inclusion rules?** Three parts, all now blocking implementation: (a) **minimum depth** — below how many members is a consensus rate not published at all? (b) **liquidity criterion** — BIDU is clean but stale, and a stale member drags consensus toward its own lagged level; is it included, weighted down, or excluded? (c) **confidence reporting** — how is panel depth and dispersion surfaced under P3, given depth is thinnest where history is longest? |
| ~~Q-060~~ | closed | → D-017. **Cross-pair coherence test on 2020-04-14.** Do GLD, BABA, UBER and AAPL show a comparable sustained level shift around that date? All pairs moving together → real CCL widening, BIDU is clean, and only AAPL needs the AIF lookup. BIDU alone moving → instrument-specific, and it joins the worklist. Free — the series are already held. |
| ~~Q-059~~ | closed | → D-016. **Run the same detector across every CEDEAR pair.** The method is proven and cheap. GLD, ETHA, BABA, BIDU and UBER CEDEARs all carry ratios that may have changed, and any of them may contain the same seam. The output is an inventory of suspected ratio-change dates with estimated factors — the worklist for the authoritative AIF/BYMA lookup, and the scope estimate for how much of the CEDEAR universe is currently unquarantined and wrong. |
| ~~Q-058~~ | closed | → D-015. **Run the F-019 validation.** Every prerequisite is now in place: 11305 has ~9 years of CEDEAR history, the US AAPL Series is populated, and the relationship and ratio are set. Compute the implied-FX series across full history and compare against known historical CCL. Smooth and tracking → constant current ratio is correct for the adjusted data. Step discontinuities at ratio-change dates → dated ratios are mandatory before any FX figure is displayed. |
| Q-057 | **moved to Tranche 1 — unsent** | **Where did `ratio = 20.0` on series 11305 come from?** Hand-entered, scraped, inferred, or carried from a provider field? Is it dated, and is it current as of today or as of some past moment? D-013 makes ratios temporal and authoritatively published; F-021 makes this the provenance of the demo's headline number. |
| ~~Q-056-old~~ | superseded | **Coverage *and* completeness — the two cannot be separated by counting alone.** Requested: (a) count of Series with ≥1 observation, with ≥250 (one year of daily bars), with ≥1,250 (five years); (b) earliest and latest `observed_at` across the store; and (c) for a sample, the **requested date range on the import versus the span actually received**. Part (c) is what F-017 makes necessary: ETHA showed 19 bars for a ~408-bar range, so a low count cannot be read as "the provider has little data" rather than "we failed to fetch what exists." 11,311 Series is a catalogue number; this is the capability number. |
| ~~Q-007~~ | closed | **What is actually in `series` today?** A census: count by `provider` and by `series_type`, and specifically — **is any BYMA-sourced ProviderSymbol resolved into a Series at all?** D-010 showed GGAL's four symbols are discovered but unresolved. If that holds across BYMA, the Argentine half of the universe does not yet exist as Series, and every decision taken so far about CEDEARs, settlement, FX and ratio changes concerns data the Workbench cannot currently read. This defines V0's real scope. |
| Q-055 | closed · inconclusive by construction | The UNRATE comparison returned no discrepancy, but the assignment is 11 days old, so a match was guaranteed either way. Superseded by A-009's constructed harness. See D-009. |
| Q-054 | open · candidate remedy for F-009 **and** F-013 | A **periodic full-range re-fetch** is simultaneously detector and repair, with no schema change: a healthy Series generates ~zero corrections, a drifted one generates a burst dated the same day. Cost is bandwidth and rate limits; side effect is that history becomes mutable *by design* — but logged mutation beats silent drift. Does not help provider-splice breaks. *Note: promoting this to "the fix that covers both" was premature — it rests on F-013 sharing F-009's root cause, which is argued but not yet demonstrated.* |
| ~~Q-051~~ | closed | → D-007. |
| ~~Q-041~~ | closed | → D-005. |

### 2.2 Data integrity and provenance

| ID | Status | Question |
|---|---|---|
| ~~Q-038~~ | **moot** | Premised on F-001, which is retracted. No migration was ever needed — the column has existed since v1. |
| Q-039 | partially answered by D-006 | Resolved: corrections never touch historical rows, and that is an artifact of the re-fetch window rather than evidence of clean data. **Still open:** does `correction` record which `import_run` performed the overwrite, and does it cover every field or only `value`/`volume`/`close`? Bears directly on F-001. |
| Q-042 | absorbed into Q-051 | Original option (b) — "store raw prices" — is **not available for Yahoo**: the endpoint returns split-adjusted values and there is no raw close to store. The live option space is now (c) Workbench normalises onto a declared basis at read time, or (d) Workbench detects and quarantines without repairing. Both pull corporate actions toward V1, contradicting spec §35. |
| Q-052 | **respecified by D-016 — adopt** | Discontinuity detector, now in three stages: (1) flag large single-day moves as *candidates*; (2) test **persistence** at 15 and 60–75 trading days to separate reverting swings from permanent steps; (3) test **residual against panel consensus** to separate instrument-specific steps from market-wide FX moves. Still the only detection mechanism anywhere in the stack (D-006). |
| Q-053 | open · quick | What is the denominator behind 13,302 corrections in an 11-day window? Corrections per observation-day tells us how provisional a freshly-imported bar really is, and therefore whether F-011 needs UI treatment or just a footnote. |
| Q-050 | open | After a MERGE, does the archived Series row carry a pointer to the surviving `series_id`? Without it Workbench can *detect* a stale reference but cannot repair it, and watchlists/peer sets silently rot. |
| Q-040 | open | Does the pipeline ever write while Workbench reads? WAL says this is safe; confirm whether a snapshot copy is nonetheless wanted for reproducibility. |

### 2.3 Series identity and typing

| ID | Status | Question |
|---|---|---|
| Q-046 | reframed → **D-010** | Posed as a false dichotomy — the rows do not exist. Now a Catalog-resolution question: separable, schema-free today, and reopened only once discovery actually resolves a multi-settlement BYMA instrument. |
| Q-045 | blocking · **reshaped by D-013** | The taxonomy needs at least three orthogonal axes, not one: **wrapper** (direct / CEDEAR / CEVA / ADR), **underlying asset class** (shares / ETF / bond / commodity / virtual asset / index), and **venue+currency**. `CEDEAR` alone cannot drive the capability matrix, since a CEDEAR over an ETF and one over a bond need different metrics. Sponsored vs unsponsored is a further regulatory attribute. |
| Q-021 | open | Commit to a closed instrument taxonomy **plus a capability matrix** (type → permitted metrics). Without it AC-04 is untestable. |
| Q-020 | open | The spec says "instrument" and "instrument-aware" throughout while project vocabulary is **Series**. Unify on one term. Is instrument type a property of a Series or a separate classification object? |
| Q-017 | **answered** | `underlying_series_id` + `ratio` via `SET_UNDERLYING` models CEDEAR↔underlying, and D-011 confirms two *working* instances (11305→33 at ratio 20.0; 11311→GLD). Remaining sub-question only: whether dual-listing and index-tracking reuse this edge or need their own. |
| Q-018 | **answered by D-013** | Settled by regulation: the ratio is variable, reported quarterly, and changes require a Prospectus Supplement with an effective date. A scalar `ratio` is insufficient — it must be dated. Ratio history is publicly available via the CNV's AIF rather than needing reverse-engineering. |
| Q-019 | open | How are ProviderSymbol → Series mappings created — manual, automatic via ISIN/FIGI, or hybrid with a review queue? What happens on ticker recycling? |
| Q-047 | open | A Series may have several ranked providers. Which ProviderSymbol does the §7 header display — primary, all, or the one that produced the displayed value (which per F-001 may be unknowable)? |

### 2.4 Currency, FX and inflation *(the real differentiator — largely unaddressed by the spec)*

| ID | Status | Question |
|---|---|---|
| Q-011 | **blocking · now concretely testable** (D-011) | Comparing a CEDEAR to its underlying: in which currency is the return expressed, and using **which** FX rate — implicit CCL derived from the pair, official, MEP? Each is defensible; each gives a different answer. |
| Q-012 | open | Is the implicit exchange rate a **Series** in its own right (derived, stored, provenance-tracked), or a read-time calculation? |
| Q-013 | open | Are **real (inflation-adjusted)** returns required? Nominal ARS returns over 1Y+ are close to meaningless. If yes: INDEC IPC or CER, and from which provider? |
| Q-014 | open | What is the risk-free rate for a Sharpe ratio on an ARS-denominated Series? Without an answer, spec §11 Sharpe/Sortino are unimplementable for half the universe. |
| Q-015 | open | Global user-selectable display currency that re-expresses every chart and metric, or currency fixed per Series? |

### 2.5 Analytics correctness

| ID | Status | Question |
|---|---|---|
| Q-027 | open · **now blocking a second consumer** (D-030) | How are Series with different trading calendars (BYMA vs NYSE holidays) aligned for correlation, beta and comparison — intersection of common dates, or forward-fill? Raised for analytics; **density-based coverage detection needs the same calendar** to compute expected trading days. No calendar table exists and no provider supplies one, so density stays a heuristic until this is answered. |
| Q-028 | open · **now with evidence and a measurable signature** (D-017) | BIDU demonstrates the effect concretely: a single print compressing three weeks of movement. Naive volatility understates between prints and spikes at them — wrong in the flattering direction. The panel residual's *transience* gives a detection signature, so the policy question is now what to do once detected: suppress, adjust the estimator, or flag and display. |
| Q-029 | open | Default benchmark per type: ARS equity, CEDEAR, ETF, index. Merval ARS, Merval USD, S&P 500? |
| Q-030 | partially answered by D-005 | Yahoo values are dividend-*un*adjusted, so today only **price return** is computable and it is computed correctly. Total return requires the dividends table (Workbench-owned, V2). Remaining question: is the basis visible in the UI at all times, or only on inspection? |

### 2.6 Scope, universe and delivery

| ID | Status | Question |
|---|---|---|
| Q-048 | open · recommendation on the table | V1 Statistics: since no fundamentals exist, restrict V1 to price-derived statistics (52w high/low, 50/200-day MA, average volume, realised volatility, beta vs chosen benchmark) and move market cap, P/E, EPS, yield to V2. Resolves the §34/§35 contradiction. |
| Q-049 | open · recommendation on the table | Accept a **V0** below V1: search, identity, EOD chart, historical table with provenance-carrying export, one comparison — nothing else. Demoable in weeks; exercises every architectural principle before any money is spent on data. |
| Q-043 | open | Which `configured_interval` values are actually in use? If everything is daily, 1D and 5D must come out of the V1 chart — §9.2 forbids fabricating intervals. |
| Q-044 | open · recommendation on the table | Is a live-quote path in scope at all, or does V1 honestly display *"Last close · 2026-08-14 · Stooq"*? Recommendation: the latter. Cheaper, truthful, and what a provenance-first tool should look like. |
| Q-007 | **promoted to §2.1 Live** | See above. |
| Q-008 | open | Are Argentine bonds and ONs in scope, and in which version? Clean/dirty price, accrued interest, amortisation, CER adjustment form a separate domain, not an equity variant. |
| Q-010 | open | Must the app work when BYMA is unreachable from outside Argentina? Must it run offline? |
| Q-031 | open | Team size, stack, hours per week. Is there a web server, or is this single-user desktop like HistFinTS? |
| Q-032 | open | Expected store size in a year. SQLite is fine for EOD across thousands of Series; questionable with broad intraday coverage. |
| Q-033 | open | Is there any **write** path in the app — editing mappings, correcting an observation, tagging peers — or is it strictly read-only over the pipeline? |
| Q-034 | open | Is CSV export meant to reproduce Yahoo's download, or to be a provenance-carrying export (value + source + as-of)? |
| Q-026 | open | AC-09 says "every displayed value." Replace with an enumerated list of V1 metrics and their required provenance fields, or it cannot be tested or signed off. |
| Q-006 | open | Team-internal only, or ever shared/published? See F-007. |

---

## 3. Findings against the current spec and data

Severity: **H** breaks a stated acceptance criterion · **M** requires a spec
rewrite · **L** worth recording.

### F-001 · ~~H~~ **RETRACTED 2026-08-15 — the finding was wrong**

`observation` carries `series_id`, `observed_at`, `value`, OHLC — and **no
foreign key** to `import_run` or `provider_assignment`. Joining "through" those
tables means correlating by timestamp, which is inference, not provenance. Because
a Series can be served by different providers over time via fallback, the
inference is wrong precisely in the cases that matter.

Renders spec §12.1 (per-row Provider / ProviderSymbol / import run) and **AC-09
unbuildable** — awkward, since provenance is the stated differentiator (§44).

**RETRACTION.** `observation.import_run_id` **already exists** — `NOT NULL`, a real FK, in
`schema.sql` itself since the v1 baseline. Every observation already traces to the exact
import run that wrote it, and from there through `provider_assignment` to the provider and
its raw ticker. The provenance chain was complete the whole time.

**Cause of the error.** The finding was built on the prose brief's column summary, which
listed `series_id`, `observed_at`, `value` and optional OHLC. I read that list as
exhaustive. It was a summary. The brief even said to *"join through
`provider_assignment`/`import_run`"* — which presupposed the very join path I concluded
was missing.

**I never read the schema.** `spec-interrogator.md` requires verifying empirical claims
against the artefact rather than accepting stated intent; on the single most load-bearing
finding of the review, that was not done.

**Blast radius.** F-001 was raised in the first round of findings and cited across roughly
ten. It drove Q-038 (schema-change governance), part of D-018, and Item 1 of the Tranche 2
request — a migration to add a column that has existed since v1.

**The correction is good news.** **AC-09 was buildable all along.** The provenance
differentiator rests on firmer foundations than this review has been claiming.

*Possible residual gap, unverified:* `import_run` may not record which adapter version or
endpoint variant served a fetch. That is a real question, but it is downstream of the FK
and much narrower than what F-001 asserted.

### F-002 · H — Raw vs adjusted is unrepresentable *(confirmed by D-005)*

`UNIQUE(series_id, observed_at)` plus a single `value` column permits exactly one
number per instant, and D-005 confirms that number is provider-adjusted with a
provider-dependent convention. **AC-06 requires the chart to state its adjustment
basis; that remains unknowable from the schema.** Now split into F-009 (the
mechanism that corrupts) and F-010 (the missing label). Live as Q-051.

### F-003 · M — The store is not bitemporal

Corrections overwrite in place. Correct for a pipeline; a problem for a
provenance-first research tool. §32 promises to answer *"where did this number come
from"* — but not *"what did this chart look like when I made that decision in
March."* Recoverability depends entirely on Q-039.

### F-004 · H — No quote, no session, no current price

Spec §7 (live price, change, market status), §7.1 (seven session states) and
**AC-03** (regular vs extended hours never silently mixed) have no backing data.
`observation` has a UTC timestamp and nothing tagging a session. Live as Q-044.

### F-005 · M — No relationships and no corporate actions

CEDEAR ↔ underlying (§6), dual listings, index membership, benchmark assignment
(§11.1): nowhere to store any of it. Dividends, splits, CEDEAR ratio changes
(§20): same. This is the largest genuinely **new** domain the Workbench must own,
and it is what forced D-001.

### F-006 · M — Value-only Series are a first-class case

FRED/ECB series have `value` and NULL OHLC, as does any computed ratio. P2's
instrument-awareness table has no row for *"no OHLC → no candlestick, no volume,
no intraday."* For this universe that is a large slice, not an exception.

### F-009 · H (dormant) — Incremental import will silently break scale at future splits

**The most serious finding so far.** From `application/import_service.py`: the first
import backfills full history; every subsequent import fetches only a trailing
window from the latest stored date forward. Historical rows are never re-fetched.

A Series backfilled *before* a split and tracked incrementally *through* it therefore
keeps its pre-split rows at the old scale while post-split rows arrive already
adjusted — a permanent, unmarked discontinuity of exactly the split factor.
`correction` never fires, because it only compares a re-fetched value against a
stored value for the *same date*, and those dates are never re-fetched.

**Why the database looks clean today: survivorship, not health.** AAPL's
`provider_assignment.created_at` is 2026-08-11 — long after both its splits — so
26 years of history arrived internally consistent in one shot. Every long-history
Series in the store was backfilled after its splits already happened. The defect is
not absent; it is **dormant**, and starts producing corrupt data the first time a
tracked Series splits.

Blast radius is far wider than display. A 7:1 split injects a −85.7% single-day
return, poisoning realised volatility, maximum drawdown, CAGR, beta, correlation
and every comparison chart crossing the boundary — silently, with no correction-log
trace and no visual cue beyond the jump itself.

*Owner:* HistFinTS. This is an import-integrity defect independent of anything
Workbench decides.

### F-010 · M — Adjustment basis has nowhere to live

Neither `observation`, `series` nor `provider` records which adjustment basis
applies. Basis is a per-provider property (D-005), and `provider_assignment`
permits a Series to be served by several providers over time. Fallback splicing
across conventions produces an unmarked scale jump, and AC-06 cannot be satisfied
from the schema regardless of what Workbench does.

### F-011 · M — The most recent observations are provisional, and the UI would present them as settled

D-006 shows corrections concentrate at 0–1 days old (12,965 of 13,302). Whatever the
denominator turns out to be (Q-053), the newest one or two bars of any Series are
routinely revised after they are first stored.

The spec's §7 header and §40 V1 screen display the latest value as a settled fact.
Under P4 (Observed / Calculated / Reported must not be conflated) a provisional
observation is arguably a fourth class, or at minimum needs a freshness marker.
Concrete rule to consider: any observation younger than the re-fetch window is
displayed as **provisional**, and is excluded from — or flagged within — derived
statistics.

### F-020 · ~~H~~ **RESOLVED 2026-08-15** — Series 11305 (Apple CEDEAR) had zero observations

The centrepiece of A-012 has no price history at all. Its only `provider_assignment` is
BYMA, which has no working price-fetch path, so the Series exists with a populated
`underlying_series_id` and `ratio` and nothing to plot.

**A verified fix exists and was deliberately not applied.** Adding a Yahoo `AAPL.BA`
assignment — the same pattern used for the eight-name pilot — yields **3,637 real bars
back to 2011-09-26**. That is nine years of history spanning AAPL's 2020 4:1 split, which
is exactly what F-019's validation needs.

*Recommendation: apply it.* This is the single highest-leverage action available — it
converts the V0 demo from theoretical to runnable and makes F-019 testable, at the cost
of one assignment.

**Applied 2026-08-15.** Series 11305 is now a working CEDEAR with history spanning a
known split, sitting alongside the US-listed AAPL Series. **A-012 is runnable and F-019
is testable.** Every prerequisite for the V0 headline acceptance test is in place.

**Note the shape of the failure.** A Series can hold a complete, plausible identity
record — name, type, underlying, ratio — and zero data. Identity resolution and data
availability are independent, and neither implies the other.

### F-019 · H — The V0 implied-FX demo is unsound as specified: the ratio must be dated

A-012 proposes computing implied FX from Apple CEDEAR (ARS) against AAPL (USD) using
`ratio = 20.0`. D-013 establishes that the ratio is variable and that changes are formal,
dated, published events.

Applying today's ratio across all history is therefore wrong **unless** the provider has
already rebased the CEDEAR price series for past ratio changes — economically, a ratio
change is a split of the CEDEAR, so Yahoo plausibly treats it as one. Plausibly is not
good enough for the calculation this product is built to defend.

**A validating test that D-009's freshness problem does not block.** Compute the implied
FX series across the full history and compare it against known historical CCL rates. The
history spans years even though the rows are days old, so this tests the chain rather
than the calendar:

- Series smooth and tracking known CCL → the provider rebases ratio changes as splits,
  and a constant current ratio is correct for the adjusted series.
- Step discontinuities at ratio-change dates → the provider does not rebase, dated ratios
  are mandatory before any FX figure is displayed.

Either outcome is worth having, and it validates identity, relationship, ratio and
adjustment basis in one calculation. **This should be V0's headline acceptance test.**

**Update, 2026-08-15 — prior strengthened, question not closed.** `AAPL.BA` shows no
discontinuity through AAPL's 2020 4:1 split (1574→1582→1679→1705→1651), so Yahoo's `.BA`
feed *is* adjusted. That makes a constant current ratio plausibly correct: both sides sit
on current basis and the two adjustments cancel.

Plausibly, still not demonstrated. Smoothness proves Yahoo adjusts; it does not prove
Yahoo's adjustment factor matches the actual ratio change the issuer applied, nor what
ratio was in force in 2015. **Only the end-to-end comparison against known historical CCL
tests the whole chain.** Two consequences either way: the nominal historical ARS prices
are not what traded, which is a labelling requirement under P3; and see F-021.

### F-021 · H — `ratio = 20.0` is undated and unsourced, in the one field the demo depends on

D-013 established that conversion ratios are temporal, change by formal dated event, and
are authoritatively published through the CNV's AIF. Series 11305 carries a bare scalar
`20.0` with no effective date, no announcement reference and no recorded provenance.

We do not currently know whether that value is current, historical, hand-entered, or
inferred. **A provenance-first product would be computing its headline differentiator
from an unsourced number** — the precise failure P3 exists to prevent, in the first
calculation the product performs.

### F-017 · H — **LIVE** — `import_run.status = SUCCESS` does not mean the range is complete

**The first defect in this review confirmed to have already corrupted stored data.**

The ETHA CEDEAR Series received **19 of its ~408 real observations**. Yahoo silently
truncated a single wide-date-range request and returned a partial slice; the import was
recorded as successful. This is a live, reproducible instance of a gap already documented
in `KNOWN_LIMITATIONS.md` (a wide-range request can return a truncated slice; a real
backfill needs date-chunked requests).

**Distinct from F-009 and F-013.** No split, no revision, no elapsed time. A Series
backfilled *today*, from a healthy provider, in a run marked `SUCCESS`, is simply
incomplete on arrival.

**Why this is worse than it looks.**

- Any completeness assumption in Workbench — *"if `import_run.status = SUCCESS`, the
  requested range is populated"* — is **false, confirmed**. That assumption is the
  natural one to make and would have been made silently.
- Unlike F-009's scale break, which announces itself as a visible jump, missing bars can
  be invisible. A truncated series looks like a short or thin one.
- **It confounds the coverage census (Q-056).** A low observation count cannot be read as
  "the provider has little data" — it may mean "we failed to fetch what exists." The two
  need distinguishing.

**The ask is not "fix truncation"** — the limitation is already documented and the fix
(date-chunked requests) is known. The ask is to **expose completeness**: record the
requested range against the received range on `import_run`, so a consumer can tell a thin
Series from a truncated one. That is an `observation`-trustworthiness concern and belongs
in the Tranche 2 migration.

### F-018 · M — Ticker collision is real, not hypothetical: `FXI.BA` resolves to a different company

P1 exists to prevent exactly this, and this is its first confirmed instance in live data.
`FXI.BA` — a plausible, well-known ticker — points at a different company than the string
suggests.

The base rate is the alarming part: **2 rejections in 10 hand-picked, familiar names.**
Whatever failure rate the 1,491-symbol BYMA backlog carries, it is unlikely to be better
than a curated sample, and `match_candidate` plus human confirmation is therefore
load-bearing rather than ceremonial.

Two distinct failure modes, needing different handling: `FXI.BA` is **wrong identity**
(dangerous — produces confident nonsense), `PBR.BA` is **insufficient data** (harmless if
detected, per F-015's sufficiency gate).

### F-015 · H — Series *existence* and Series *coverage* are different things, and the spec conflates them

11,308 Yahoo Series were bulk-loaded from a listing source. How many carry any
`observation` rows is unknown and, given that the database is two weeks old, probably a
small fraction.

The spec's core flow — §5 Search → §6 Series Selection → §7 Research Header → §9 Chart —
assumes that selecting a Series yields data. Under bulk loading, search returns thousands
of names that resolve to an empty Research View. **The spec has no state for "Series
exists, no observations."**

Nor for the intermediate states that matter to specific features: a Series with 40 bars
cannot support a 1Y return; one with 300 cannot support a 5Y CAGR. AC-05 and AC-08 are
silent on what happens when the data is insufficient rather than absent.

*Related:* AC-04's instrument-awareness suppresses metrics by *type*. Coverage requires
suppression by *sufficiency*, which is a second, independent gate.

### F-016 · L — Test fixtures share the production table with no flag distinguishing them

`Duplicate Warning Test` ×2, `LIVE-VERIFY-BULK-IMPORT-TEST`, `UC-6 Test Series`, an
archived `GLD Smoke Test CEDEAR`, and a FRED/STOCK row are development artefacts sitting
in `series` alongside real rows. `series.status` offers no value that cleanly separates
them.

Workbench needs an exclusion rule and currently has no reliable basis for one. Naming
conventions are fragile. Options: a status value, a boolean column, or a Workbench-side
denylist — the last being ugly but requiring no upstream change.

### F-014 · M — `currency` + `settlement_mechanism` do not individuate

GGAL (1284) and GGALB (1395) share **both** values: `ARS` / `LOCAL`. Whatever the
trailing `B` denotes, it is a third discriminating dimension captured by neither field.

Two readings, and they lead to opposite models:

1. **`B` is a real dimension** — settlement period (*contado inmediato* vs 24/48hs),
   share class, or market segment — in which case a field is missing and the
   individuation key is incomplete.
2. **GGAL and GGALB are the same Series** with two ProviderSymbols. This would be the
   **first genuine many-symbols-to-one-Series instance in the data**, and would make
   the likely overall answer *mixed*: GGAL+GGALB collapse into one Series, GGALC and
   GGALD stand separately.

Reading 2 is the more probable and the more interesting: it would exercise P1 for
real, rather than as an architectural aspiration.

This connects to the project's existing standing question about the meaning of a
trailing `B` on BYMA tickers, which is now concrete and locally testable rather than
abstract — the two rows sit side by side with identical currency and settlement.

### F-013 · H (dormant, short fuse) — Retroactive provider revisions will be silently missed

*Filed 2026-08-15 as "live"; **downgraded the same day**. The original claim inferred
present divergence from an established mechanism without checking that any time had
elapsed for divergence to occur. See D-009.*

Sibling of F-009, same root cause, different trigger.

FRED restates macro series retroactively — some monthly (payroll employment revises
the prior two months), some annually (seasonally adjusted household-survey data at the
January benchmark), some on a published schedule (GDP second and third estimates).
Because incremental import re-fetches only a trailing window (D-006), a revision older
than that window is never seen, and the stored series freezes at the vintage current
at first backfill.

**Status: unproven in either direction.** `provider_assignment.created_at` for UNRATE
is 2026-08-04. The whole series was fetched fresh 11 days ago, so a match against
FRED's current publication was guaranteed regardless of whether the mechanism is sound.
The test cannot distinguish "FRED doesn't revise this series" from "FRED does, but
nothing has had time to drift."

**Why the fuse is shorter than F-009's.** F-009 waits on a split — rare, per-Series,
possibly years away. F-013 waits on the next scheduled revision, which for some series
is weeks. Choosing a series with a frequent published revision schedule would give a
faster natural trigger than UNRATE.

**Resolution route.** Not the ALFRED comparison — FRED's revision behaviour is
documented and not seriously in doubt; proving it externally spends effort on the
half of the claim that isn't load-bearing. The mechanism is what matters, and it is
the *same* mechanism as F-009. Both should be settled by one constructed test. See
A-009.

### F-012 · M — Corporate-action events are requested on every fetch and thrown away

`providers/yahoo_finance.py:63` sends `"events": "div,splits"`; `_to_records()` never
reads `chart.result[0].events`. Every fetch since inception has paid for this payload
and discarded it.

**Recoverable, not lost.** Yahoo returns events for whatever range is requested, so a
full-range re-fetch would recover the complete event history for any Yahoo-sourced
Series. Nothing is permanently gone. But because incremental import covers only a
trailing window (D-006), a parse-only fix captures events **go-forward** and leaves
history empty until a deliberate backfill pass runs.

**Update 2026-08-17 — partly remedied in code, still unremedied on the import path.**
`YahooFinanceClient.get_splits_and_dividends()` now parses both event blocks
(`providers/yahoo_finance.py:70–92`, `_parse_splits` at `95`, `_parse_dividends` at `112`),
and `YahooEventCaptureService` persists them as `ProviderEvent` rows
(`application/yahoo_event_capture_service.py:76–164`). **But `_to_records()` at
`yahoo_finance.py:128` still ignores `events` entirely**, and
`get_splits_and_dividends()` issues its own second `_request_chart()` call
(`yahoo_finance.py:80`, duplicating the one at `:52`). So every price import still pays for the events payload and
discards it, and capturing events costs a duplicate HTTP request against an API with no
supported systematic-use terms. The finding stands, narrowed: the waste is now
architectural rather than a missing parser.

### F-023 · M — `provider_event` has no link to the observations or corrections it would explain

Verified against `migrations/0013_add_provider_event.sql:5–18`. The table carries
`series_id`, `provider_id`, `event_type`, `event_date`, `acquired_at`,
`provider_source_id`, `structured_data`, `provenance_note`, `created_at` — and **no
`observation_id`, no `observation_correction_id`, no `import_run_id`**. The reciprocal is
also true: `observation_correction`
(`migrations/0012_add_revalidation_tracking.sql:5–26`) links to `observation` and to
`revalidation_run`, and carries no reference to any event.

**What it breaks.** Nothing upstream — this is arguably the correct shape, since asserting
that an event *caused* a change is interpretation and HistFinTS is right to stay out of it
(D-028, and `domain/provider_event.py:22–34` says so explicitly). But it means the
correlation is entirely the **Workbench's** to compute, by `series_id` plus date proximity
plus a tolerance, with no upstream key to lean on. Consequently the join is a
`Calculated` step with a stated tolerance, not an `Observed` fact, and the tolerance is a
parameter that must appear in the finding's provenance. Recorded so that a later
implementer does not go looking for the FK and conclude it was overlooked.

### F-024 · M — FRED `REVISION` events record the vintage *date* only, with no changed values, making "explained by captured evidence" near-vacuous for macro Series

`FredEventCaptureService.capture_events_for_series()` calls `get_vintage_dates()` and emits
one `ProviderEvent(REVISION)` per vintage date, with
`structured_data = {"source": ..., "series_id": ...}` — no value, no changed range, no
before/after (`application/fred_event_capture_service.py:58`, `96–108`). The client
*does* have `get_observations_at_vintage()` with `realtime_start`/`realtime_end`
(`providers/fred.py:87–106`) and it is **called from nowhere in `src/`** — only from
`tests/providers/test_fred.py`.

**What it breaks.** FRED publishes a vintage date on essentially every release, so for a
monthly series the captured event set approximates "one event per month, forever." Any
reconciliation rule of the form *"a REVISION event exists within N days of the
discontinuity → explained"* will return `explained by captured evidence` for almost every
macro discontinuity, including genuine defects. That is a fabricated-lineage outcome and it
invalidates the verdict for FRED Series specifically. Mitigation for this increment: the
reconciler must **not** accept a bare `REVISION` event as explanatory; a vintage date is
evidence that a revision *window* was open, not evidence of what changed. Either the
verdict for FRED stays at `insufficient evidence`, or a vintage-value comparison via
`get_observations_at_vintage()` becomes a prerequisite. This increment takes the former.

### F-025 · L — `provider_event.acquired_at` is capture time, not fetch time, so the event table cannot say what the provider reported *at the moment of an import*

`acquired_at = datetime.now(timezone.utc)` at the point the capture service runs
(`application/yahoo_event_capture_service.py:73`,
`application/fred_event_capture_service.py:70`), and capture is a **separate operator
action** — CLI `capture-yahoo-events` / `capture-fred-events`
(`presentation/cli.py:173`, `183`), not part of `run_import`. There is no
`import_run_id` on the row (F-023).

**What it breaks.** The bitemporal question "did the provider tell us about this split
before or after the import that broke the scale?" is unanswerable from the event table
alone; the best available proxy is comparing `provider_event.created_at` against
`import_run.started_at`, which conflates *when HistFinTS asked* with *when the provider
knew*. Low severity because the proxy is usable and the ordering is usually obvious, but it
must be labelled as a proxy in any provenance display rather than presented as the
provider's own timing.

### F-007 · L — The database is proprietary; the data is not

Yahoo, Stooq and Alpha Vantage terms bind on redistribution. Irrelevant while this
stays on team machines; decisive the moment anyone discusses sharing. Tracked as
Q-006.

### F-008 · H — §34 contradicts §35

V1 requires Key Statistics (market cap, P/E, EPS, yield, beta) while V1 excludes
fundamentals and corporate actions. One of the two must give. Live as Q-048.

---

## 4. Spec amendments queued

Written once the governing decision lands; do not edit the spec ahead of them.

| ID | Trigger | Amendment |
|---|---|---|
| A-001 | D-001 | §30 architecture diagram gains a second store. State the rule: boundary crossed read-only, `series_id` is a convention-level reference. |
| A-002 | D-001, D-003 | New acceptance criterion — **stale reference handling**. If HistFinTS merges two Series, a watchlist or peer set pointing at the absorbed row must *follow* the merge, not silently display an archived Series. Depends on Q-050 for whether repair is even possible. |
| A-003 | Q-041/Q-042 | Rewrite AC-06 to state the actual adjustment basis, and §12 to expose it per row. |
| A-004 | Q-044 | Rewrite §7, §7.1 and AC-03 to describe last-observation display rather than a live quote, or else specify a quote provider. |
| A-005 | Q-048 | Rewrite §13 and the §34/§35 boundary. |
| A-006 | Q-026 | Replace AC-09's universal claim with an enumerated V1 metric/provenance table. |
| A-007 | Q-020, Q-045 | Unify vocabulary on **Series**; add the closed type taxonomy and capability matrix as a numbered spec section. |
| A-009 | D-006, D-009 | Add **one constructed regression harness** to the HistFinTS suite covering F-009 and F-013 together — they share a root cause, so they should share a test. (a) Split case: backfill a fixture Series to before a known split, import past it, assert both sides are on one scale. (b) Revision case: set `backfill_start_date` back, delete a chunk of recent observations, re-run `run_import` across the boundary, assert an already-stored value is actually revisited. Both defects are unfalsifiable by observation and must be held down by construction. |
| A-012 | D-011 | Make the **implied-FX pair the V0 demo**, not a generic quote page. Three instances now exist in real data, in increasing order of cleanliness: (a) **YPF (NYSE, USD) + YPF.BA (BYMA, ARS)** — a genuine dual listing; adjusted for the ADR ratio, the quotient *is* the implied rate, with no CEDEAR ratio to carry. (b) **Series 33 (AAPL) + 11305 (Apple CEDEAR, ratio 20.0)** — exercises the `underlying_series_id`/`ratio` edge as well. (c) Banco Macro and Pampa, which also carry US listings. Each exercises P1 identity, P3 provenance, P4 Observed-vs-Calculated and the currency question on one screen, using data that exists today and needing nothing from the 1,491-symbol backlog. |
| A-013 | D-032, D-033 | Add an **evidence-consumption** section to the spec, per `SPEC-f009-evidence-consumption.md`: the four epistemic layers (provider evidence / Workbench calculation / analytical finding / research conclusion) with their P4 statuses, the three-value reconciliation verdict with its reason codes, and the rule that no finding is ever auto-promoted to a conclusion. Must state that `explained by captured evidence` is unreachable until HistFinTS migrations 0011–0013 are applied and the capture commands have been run. |
| A-014 | D-032 | **Correct the stale rows in `HISTFINTS-BRIEF-v2.md`.** The brief predates HistFinTS's R1/R2a/R2b work and currently reads as though FRED vintages were never requested and Yahoo events never parsed. Both are now false in code and both are still true in the live database — the brief must carry that distinction explicitly (`code-complete / not migrated`), because a reader who trusts either half alone will design wrongly. |
| A-011 | D-007 | Add a two-layer corporate-actions section to the spec: HistFinTS-side raw provider events (Observed, P4) vs Workbench-side reconciled model and derivation (Calculated, P4). State explicitly that Yahoo events cover Yahoo Series only and that BYMA/CEDEAR ratio changes need a separate source. |

---

## 5. Vocabulary

Binding across spec, code and conversation.

| Term | Meaning | Not |
|---|---|---|
| **Series** | An identified entity with metadata; the primary financial-data identity. | "instrument", "security", "ticker" |
| **series_master_list** | The reference table of Series. | "instrument universe", "instrument master list" |
| **Observation** | A time-indexed value for a Series. | "price row", "data point" |
| **Provider** | An external source of data. Never a source of identity. | |
| **ProviderSymbol** | A provider's own raw ticker string for a Series. | the Series' identity |
| **HistFinTS** | The read-only upstream time-series store. | the Workbench |
| **Workbench** | This application, and its own database. | |

---

## 6. Changelog

| Date | Change |
|---|---|
| 2026-08-17 | §8 of `SPEC-f009-evidence-consumption.md` accepted → **D-034**: proceed with the `hf_reswb` reconciliation implementation against the current schema (migrations 0011–0013 unapplied); `explained by captured evidence` remains structurally unreachable against production until they land, and must be stated as such in acceptance criteria, not left implicit. Two-stage validation adopted (now: not-explained/insufficient against legacy evidence; later: explained, once migrated). Migration application filed as a **separate, non-blocking, mechanical** ask (`REQUEST-apply-migrations-0011-0013.md`) — deployment of already-built code, not reopened HistFinTS development. F-023/F-024/F-025 restated as binding on the implementation: event correlation is `Calculated` not `Observed` (no FK); a bare FRED vintage date is not explanatory; `acquired_at` is capture time, not fetch time. `CLAUDE.md` gains a row for the new spec; A-014 stays queued, not folded into this increment. |
| 2026-08-17 | F-009 remediation halted in HistFinTS; focus moved to proving Workbench evidence *consumption*. Upstream inspected before designing → **D-032**: the evidence chain is **code-complete and absent from the live database**. R1 (`RevalidationService`), R2a (`provider_event`), R2b-FRED (vintage dates) and R2b-Yahoo (splits/dividends) are all implemented, and **FRED vintages and Yahoo event parsing have landed since D-021**, which is now partly stale. But the production DB is at `PRAGMA user_version = 10` with migrations 0011–0013 unapplied, so `provider_event`, `observation_correction` and `revalidation_run` **do not exist across the ATTACH boundary** — corroborated by a backup trail stopping at migration 0010. BYMA `underlying_ratio` unchanged (hand-authored JSON reader only). D-006 **not** superseded: `default_revalidation_window_days` is still NULL for all three live providers. New verified provenance property: a corrected observation **retains its original inserting `import_run_id`**, giving two anchors per correction. **D-033** settles the Workbench-side model — reference upstream evidence by key, never duplicate observations (they are mutable in place, so a copy is a second truth, not a snapshot); four epistemic layers in existing P4 vocabulary, with **no auto-promotion of a finding to a conclusion**; verdict vocabulary fixed at three values because every richer option encodes a magnitude judgement the Workbench cannot make from event metadata. **F-012 updated** (parser landed; `_to_records()` still discards events and capture costs a duplicate request). **F-023** raised (`provider_event` has no FK to observations or corrections — correlation is the Workbench's `Calculated` step with a stated tolerance). **F-024** raised (FRED REVISION events carry vintage *dates only*; a bare vintage date must not count as explanatory or the verdict is vacuous for macro). **F-025** raised (`acquired_at` is capture time, not fetch time). Design note written: `SPEC-f009-evidence-consumption.md`. A-013, A-014 queued. |
| 2026-08-15 | Log created. D-001…D-004 recorded; F-001…F-008 raised; open questions Q-006…Q-050 migrated in from the review sequence. |
| 2026-08-15 | Codebase grep confirms the `events` payload is requested and discarded → **D-007** closes Q-051: HistFinTS captures raw provider events (faithful recording, inside D-002), Workbench owns reconciliation and derivation (spans providers; BYMA/CEDEAR unreachable from Yahoo events). V0/V1 = detect and quarantine. **F-012** raised (events discarded, recoverable). **Q-054** added (periodic full-range re-fetch as combined detector/repair). A-011 queued. Adjustment thread closed; **Q-046 (Series individuation) promoted to live** after five rounds on data integrity. |
| 2026-08-15 | Review paused to assess ask timing → **D-008**: asks tranched by migration cost rather than review completeness. Tranche 1 (F-009 defect, basis fact sheet, Q-039/Q-050) sent now; Tranche 2 batched into one migration gated on Q-039 and Q-046. |
| 2026-08-15 | Availability/coverage model **converged** → **D-031**. Three-layer structure finalised (availability stored, coverage derived, interior gaps gated on a calendar); governing sentence on density-as-screening adopted verbatim for the eventual spec. Three implementation guards locked in: coverage must never be persisted, `ADEQUATE` must not imply verified-complete, and density/interior-gap results must carry visibly different confidence levels in any UI. **This design branch is closed** — remaining work is implementation, gated on Q-027 and Tranche 2, not further specification. |
| 2026-08-15 | Availability/coverage vocabulary adopted → **D-030**, with the standing rule *known availability → measurable coverage → diagnosable incompleteness; unknown availability → explicitly unresolved*. **Corrected to two levels, not a three-value enum** — availability is stored, coverage is derived. Three refinements: **provider availability ≠ instrument availability** (Yahoo's `.BA` `firstTradeDate` reports Yahoo's coverage, not the BYMA listing date); **`INCOMPLETE` is not atomic** (head truncation vs interior gaps have different causes); and *"adequately cover"* needs a number that **is not currently computable — expected trading days requires a venue calendar**, linking this to **Q-027**, open since round one and now blocking a second consumer. Density is a screen, not a measure, until then. |
| 2026-08-15 | Completeness placement sharpened → **D-029**. Two concept graphs named — Catalog identity vs operational acquisition, meeting only at `Series` — yielding a **standing placement rule**: analytical-layer metadata belongs on the operational path. Hedge resolved: `provider_assignment` definitively (right cardinality, reachable from every Series). **`UNRESOLVED` adopted as a first-class third state** and, crucially, a **permanent** one — some adapters can never report availability. Filing re-scoped and honestly characterised: this is an **adapter-interface change**, not a column. New parameter `unresolved_coverage_policy`, which must tighten over time since zero rows carry the metadata today. |
| 2026-08-15 | Panel requirement reformulated into one testable sentence — adopted into `SPEC-panel-eligibility.md` §0, **with the as-of-date clause restored**: the rewrite had dropped it, and without it a developer implements a single query-time filter that restricts a 20Y panel to survivors, reintroducing precisely the bias the sentence's final clause exists to surface. Exclusion-diagnostic display adopted with three added implementation rules: **overlapping criteria need a stated counting rule** (first-failure-wins and reconciling, or multi-count and say so); `Universe` not `Eligible` for the pre-filter line; and `Instrument type` is **not computable until Q-045's capability matrix exists**. Confirmed that three of four exclusion reasons are computable against the current schema today — coverage is the exception, blocked on Tranche 2. |
| 2026-08-15 | `REQUEST-event-capture.md` reviewed pre-send: proposed `currency` on dividend events **does not exist in the payload** (Yahoo sends `{amount, date}` only; currency lives on `meta.currency`). Field dropped, with an explanatory note so it is not re-added as an oversight. **D-009b extended** — the rule governs *proposals*, not only claims; this was the third instance and the first in the presence direction. Separately noted: `meta.currency` is provider-reported and discarded while `series.currency` is hand-entered — a **free cross-check against mis-entered Series**, filed as a note rather than bundled. |
| 2026-08-15 | Yahoo `events` capture — decided in D-007, never filed — **now filed** as `REQUEST-event-capture.md` → **D-027**. Design fork resolved in favour of a **dedicated `provider_event` table**: D-007 already classes these as Observed, and observations do not belong in a change log. Free backfill identified — a full-range re-fetch is *the same operation* as defect remedy R1, doing three jobs at once. **D-028** generalises the capture/reconciliation split from corporate actions to **all** provider data (Yahoo events, FRED vintages, BYMA ratio), with a standing rule that a filing excluding one half must name which half. |
| 2026-08-15 | Direct entry confirmed **permanent by design** (`master` had it as the only path; Catalog was built alongside for a different problem) → **D-026**. Nothing to unwind for the 8 pilot Series — live verification with 2 rejections beats an automated Tier 2/3 match. **The inversion named**: evidence quality and evidence recording are inversely correlated. **Rejections identified as lost evidence** — ~20% of curation output discarded at the moment of production. **Assertions decay** — `verified_at` and re-verification needed against ticker recycling. Record shape proposed; placed in **Tranche 3**, not bundled. Immediate no-schema step: capture the pilot verification evidence in a document now. **F-022 completed** — Asserted uniquely carries an internal quality dimension. **Q-045 (capability matrix) promoted to live.** |
| 2026-08-15 | Both embedded questions in the Tranche 2 filing closed → **D-025**. (a) `import_run` records no adapter version — narrow now, **material the moment any D-021 adapter fix ships**, and retroactive. (b) `first_available_date` is **structurally unreachable**: `provider_symbol_id` exists only on `match_candidate`/`identifier`, so direct-entry Series have no path at all and resolved ones reach the *discovery-side* provider, not the pricing one. Completeness marker **re-scoped onto `provider_assignment`**. (c) Underlying finding: **two disjoint Series populations**, and the Catalog pipeline has produced **none** of the working data. **F-022 substantially expanded** — asserted identity, not just an asserted ratio. **Q-065 promoted to live.** |
| 2026-08-15 | Panel eligibility proposal reviewed → **D-024**: accepted in direction, with one structural correction — **eligibility must be evaluated as of each date**, or a 20-year panel silently contains only survivors, reintroducing the bias the long-history warning exists to surface. Two panels distinguished (**pair** for V0, **cross-section** later); proposed parameters are cross-section criteria with no pair-level notion. Added `include_delisted`, `staleness_policy` (separate from liquidity, per BIDU), `dispersion_threshold` as an alarm not a statistic; diagnostics gain **exclusion reasons** and a **stored resolved membership list** for reproducibility. `minimum_coverage` and `adjustment_policy` flagged as **not implementable until Tranche 2 lands**. Drafted in `SPEC-panel-eligibility.md`. **Q-064 promoted to live.** |
| 2026-08-15 | Constructed reproduction run → **D-022**. Case (a) split confirmed (630.00→632.50→129.04→134.18, ratio 4.90, **zero corrections, both runs SUCCESS**); case (b) FRED revision confirmed after an informative negative result. **Mechanism refined: `start = latest` is inclusive**, so the newest stored date *is* revisited — the blind spot is dates strictly older than the latest, which is where both defects live anyway. `default_revalidation_window_days` is **NULL for all three providers**, making the system-wide re-fetch window exactly one date; the D-006 correction-age distribution is confirmed as exactly what that predicts. **D-023**: CEDEARs are probably immune to F-009 (no provider rebase to miss) and exposed to F-021 instead; **provider substitution proposed as a more valuable case (c)** since the splice claim remains undemonstrated. **`DEFECT-F009.md` complete and sendable.** |
| 2026-08-15 | Basis fact sheet completed internally → **D-021**. FRED and BYMA newly code-confirmed; Stooq attempted and blocked, handled by a **fallback guard** rather than a blocker; ECB/World Bank marked assumed rather than guessed. **Principal finding: Yahoo events, FRED vintages and BYMA `underlying_ratio` are one characteristic, not three bugs — adapters capture prices and discard everything else the provider offers.** BYMA identified as a **reference provider that supplies no observations**, exposing that the schema does not model provider *role*. **F-013 upgraded to mechanism-confirmed.** The fact sheet no longer needs sending, and the adjustment-basis migration now has **no remaining dependency**. |
| 2026-08-15 | `DEFECT-F009.md` reviewed → **D-020**: ships **with** a constructed reproduction, not as a procedure — the defect is unfalsifiable by observation, and F-001's same-day retraction means analysis-plus-code-reading cannot carry this filing alone. `REQUEST-basis-factsheet.md` **decoupled and sent now**. §2.2 closed at the line level (`ImportService._determine_range()`, `import_service.py:183–200`); §4 frequency claim now cites the CNV quarterly-reporting requirement and the confirmed 2024-01-24 instance. **D-006 refined: the look-back is per-provider and may be zero**, making the correction blind spot total for any provider with `default_revalidation_window_days` unset. **Q-063 promoted to live.** |
| 2026-08-15 | Tranche 2 draft reviewed against the real schema → **F-001 RETRACTED**: `observation.import_run_id` has existed since the v1 baseline; the finding rested on reading a prose summary as exhaustive and was never checked against `schema.sql`. Cited across ~10 rounds; Q-038 now moot; **AC-09 was buildable all along**. **D-019**: Tranche 2 reduces to **one** genuine migration item (adjustment basis); first-trade-date is an *unpopulated existing column* (0/1,493) and therefore an application-logic gap, pending reachability. **D-009b** recorded — third over-claim from incomplete evidence; absence in documentation is not absence in the system. **Q-062 promoted to live.** |
| 2026-08-15 | Tranche 1 questions answered → **D-018**. (a) `correction` carries a `NOT NULL import_run_id` across all five fields since v1 — **F-001 scopes to `observation` alone and Tranche 2 is unblocked**; the 13,302 figure is field-level, partly resolving Q-053. (b) MERGE repair exists via `series_merge`, but must be **recursive** and is **untested** (empty table, D-009). (c) `ratio` is **hand-typed** with no effective date, no history and no audit — the gap is categorical, so **F-021 confirmed at design level** and dated ratios stay out of Tranche 2 per D-008. **F-022** raised: P4 has no class for **Asserted** values. |
| 2026-08-15 | Cross-pair coherence run → **D-017**: AAPL, BABA and BIDU all converge on 1.32–1.34× at 2020-04-14, confirming **market-wide CCL widening**; BIDU is clean and the AIF worklist drops to **one item (AAPL)**. Path-versus-destination difference identified as a **staleness signature**, giving Q-028 its first concrete evidence. Panel mechanism now serves three purposes — rate, ratio-change detection, staleness detection — separated by the residual's time signature. **New constraint: the panel is time-varying**, thinnest where history is longest, so depth becomes a P3 provenance field. **Q-061 promoted to live.** |
| 2026-08-15 | Detector run across all six tracked CEDEAR pairs → **D-016**: 1 confirmed (AAPL), 1 ambiguous (BIDU, 2020-04-14), 1 untestable (ETHA, F-017 truncation), 3 clean. **Persistence testing** adopted as the discriminator, superseding the original Q-052 spec. Principal conclusion: **the implied-FX rate should be panel-derived, not pair-derived** — panel consensus is the rate, per-pair residual is the ratio-change detector, one mechanism doing both jobs. **Q-060 promoted to live:** cross-pair coherence at 2020-04-14 may close BIDU for free. |
| 2026-08-15 | **F-019 validation run → D-015.** Step discontinuity confirmed at 2024-01-24: CEDEAR −49.4% against AAPL −0.35%, persistent ~2:1 level shift. **Dated ratios are mandatory**; A-012 respecified to detect-and-quarantine; **F-021 escalates** to demonstrably wrong. The other 1,574 points track real Argentine macro events, **validating identity, relationship, basis and provenance end to end** — the failure is isolated to one field's temporality. Earlier inference that Yahoo rebases `.BA` history **corrected**: the issuer absorbs corporate actions into the ratio instead. New generalisation: ratio changes have two causes, and the local-tradability kind is invisible to every non-Argentine source. Q-052 detector validated. **Q-059 promoted to live.** |
| 2026-08-15 | **F-020 resolved** — 11305 fixed and now carries history spanning a known split; A-012 runnable and F-019 testable. Q-057 reclassified from a question to Carlos into a **Tranche 1 question to the HistFinTS team**, joining Q-039 and Q-050. **Process finding recorded: nothing in Tranche 1 has been sent, and Q-039 — the sole Tranche 2 gate — is inside it**, so the HistFinTS workstream is stalled on an unsent message rather than an unanswered one. **Q-058 promoted to live: run the F-019 validation.** |
| 2026-08-15 | Coverage census delivered → **D-014**: 99.3% of Series carry data (74 empty), so F-015's search-dead-ends claim is **downgraded**; the sufficiency gate survives, quantified at 16% below 1Y and 44% below 5Y. `backfill_start_date` was blanket-set to 2000-01-01, so the requested-vs-received comparison was confounded — **`firstTradeDate` is the correct reference**, refining the Tranche 2 ask into start-completeness plus density checks. **F-020** raised: series 11305 has zero observations and blocks A-012; a verified fix (Yahoo `AAPL.BA`, 3,637 bars from 2011-09-26) is recommended. **F-021** raised: `ratio = 20.0` is undated and unsourced. F-019 prior strengthened — `.BA` is adjusted — but not closed. Q-056 closed; **Q-057 promoted to live.** |
| 2026-08-15 | CNV Título II Cap. VIII reviewed (as rewritten by **RG 1142/2026**, B.O. 01/06/2026) → **D-013**: CEDEAR subtypes are regulatorily mandated (shares/ADR/ETF/corporate bond; sponsored or not); the conversion ratio is **variable, quarterly-reported and changed by formal dated event**, settling Q-018; CEDEAR, ADR and Doble Listado are three distinct relationship kinds, answering the rest of Q-017; **CEVA** added as a new instrument class; CEDEAR total return is net of issuer fees; the CNV **AIF** is an authoritative non-Yahoo source for ratio history. Q-045 reshaped into three orthogonal axes. **F-019** raised — the A-012 implied-FX demo is unsound with a constant ratio, and its validation against historical CCL is proposed as V0's headline acceptance test. |
| 2026-08-15 | HistFinTS team update: 8 new Argentine/CEDEAR Series with real multi-year history via Yahoo `.BA`. **D-011 corrected** — V0 includes a manually-verified BYMA-linked subset, but the BYMA *adapter* remains unexercised, so all new data inherits Yahoo's basis and blind spots. **D-012** records the one-Series settlement outcome explicitly as a tooling-forced default, **not** a modelling decision, so it is not later misread as precedent. **F-017** raised — first defect confirmed **live**: `import_run.status = SUCCESS` does not imply a complete range (ETHA: 19 of ~408 bars); confounds the coverage census and adds a requested-vs-received range column to Tranche 2. **F-018** raised — `FXI.BA` is the first live ticker-collision instance, at a 20% rejection rate on hand-picked names. A-012 upgraded with the YPF dual-listing pair. Q-056 revised to cover completeness alongside coverage. |
| 2026-08-15 | Census delivered → **D-011**: 11,308 US Series, 1 macro, 2 BYMA CEDEARs of US underlyings, 0 BYMA-domestic. 1,491 BYMA symbols discovered / 11 candidates / 0 resolved — a Catalog-throughput gap, not a modelling one. V0 confirmed as US + macro. **F-015** raised (existence ≠ coverage; spec has no empty-Series state) and **F-016** (test fixtures unflagged in `series`). Q-017 answered. **A-012** queued: AAPL + Apple CEDEAR demonstrate the implied-FX differentiator with data that exists today. Q-007 closed; **Q-056 (coverage census) promoted to live.** |
| 2026-08-15 | GGAL query returns **zero `series` rows** — four unresolved ProviderSymbols, no `match_candidate`. Q-046 dissolved as a false dichotomy → **D-010**: settlement modelling is Catalog-side, needs no schema today (`series.settlement_mechanism` exists from migration `0004`), and is **not** bundled with Tranche 2. D-008's batching criterion amended to *coherence of concern*, not migration count. **F-014** raised (GGAL/GGALB collide on currency+settlement, so those fields do not individuate). Q-017 mostly answered — `underlying_series_id`/`ratio`/`SET_UNDERLYING` already exist; Q-018 sharpened to `ratio` temporality. **Q-007 promoted to live.** |
| 2026-08-15 | FRED check returned no discrepancy but is **inconclusive** — UNRATE's assignment is 11 days old. F-013 **downgraded from live to dormant**; the promotion of R1 to "the fix that covers both" withdrawn as premature. Third clean-but-uninformative diagnostic in a row → **D-009** raised as a standing methodological rule and written into the agent definition. A-009 merged into a single constructed harness covering F-009 and F-013. Q-055 closed inconclusive. **Tranche 1 unaffected — F-009 never depended on F-013.** |
