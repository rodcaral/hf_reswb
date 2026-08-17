# SPEC — F-009 Evidence Consumption and Reconciliation

**Status:** design note for review · **Version:** 0.1 · **Date:** 2026-08-17
**Governing decisions:** D-001 (read-only ATTACH) · D-032 (what upstream actually holds) ·
D-033 (reference-not-duplicate; four layers; three verdicts)
**Findings it must respect:** F-009 · F-012 · F-017 · F-023 · F-024 · F-025

> **Implementation is not authorised by this note alone.** §8 names what must be true before
> code starts, and one item in it is not yet true.

---

## 0. The requirement, in one sentence

> For a selected Series and period, identify a historical discontinuity in its observations,
> resolve whatever evidence HistFinTS has actually captured for that Series and period, and
> record an **Analytical Finding** that classifies the discontinuity as *explained by captured
> evidence*, *not explained by captured evidence*, or *insufficient evidence* — where every
> element of the finding is traceable back through the Workbench's own calculation to named
> upstream rows, and where **no finding is ever promoted to a research conclusion by the
> system**.

The final clause is the one worth defending. The purpose of this increment is not to explain
discontinuities; it is to prove the Workbench can hold the line between *what a provider
recorded* and *what that means*.

---

## 1. What is actually readable upstream today

This section is the reason the note exists, and it is the part that must not be paraphrased
from memory later. Everything here is verified — see D-032 for the queries and citations.

### 1.1 Present in the live database (`PRAGMA user_version = 10`)

| Object | Shape relevant to us | Notes |
|---|---|---|
| `observation` | `id, series_id, import_run_id NOT NULL, observed_at, value, open, high, low, volume, created_at, updated_at` | `import_run_id` is a real FK and has been since the v1 baseline (F-001 retracted). **Values are mutable in place** — that is F-009. |
| `import_run` | `id, provider_assignment_id NOT NULL, trigger_type, status, started_at, ended_at` | `status = SUCCESS` does **not** imply a complete range (F-017). |
| `provider_assignment` | `id, series_id, provider_id, priority, provider_series_identifier` | Priority is the fallback order — the splice risk. Oldest row is 2026-08-04. |
| `provider` | `id, display_name, implementation_key, default_revalidation_window_days, ...` | `adjustment_basis` **absent**. `default_revalidation_window_days` **NULL for all three** live providers. |
| `correction` | `id, observation_id, import_run_id NOT NULL, field_name ∈ {value,open,high,low,volume}, previous_value, new_value, detected_at` | **13,304 rows.** The only populated change evidence in existence. Per-field, fully provenanced, and bounded by the re-fetch window (D-006). |
| `series` | `..., currency, instrument_subtype, underlying_series_id, ratio, settlement_mechanism` | `ratio` populated for **1 of 11,319** Series, undated (F-021). |

**The full provenance path exists and works:**

```
observation.import_run_id  ->  import_run.provider_assignment_id
                           ->  provider_assignment.provider_id  ->  provider
correction.observation_id  ->  observation          (subject)
correction.import_run_id   ->  import_run           (detecting run)
```

Two anchors, not one. On a correction the upsert writes the *existing* Observation back, so
`observation.import_run_id` remains the run that **first inserted** the row while
`correction.import_run_id` is the run that **overwrote** it (verified in D-032). A finding can
therefore name both the origin and the mutation.

### 1.2 Implemented in HistFinTS code, **not in the live database**

`provider_event`, `observation_correction`, `revalidation_run`,
`provider.adjustment_basis`, `provider_assignment.adjustment_basis_override`,
`provider_assignment.last_revalidated_at`. Migrations 0011–0013 exist on disk and have not
been applied. `SELECT * FROM histfints.provider_event` against today's file raises
`no such table`.

### 1.3 Not implemented at all

- **Adjustment basis is nowhere in the data**, only in a migration. Yahoo remains
  split-adjusted/dividend-unadjusted and Alpha Vantage raw, by external knowledge only
  (D-005, D-021).
- **BYMA conversion ratios.** `underlying_ratio` reaches HistFinTS only through a
  hand-authored JSON catalog snapshot; the BYMA reader never supplies it. There is no dated
  ratio anywhere, which is F-021 and is *not* in scope here.
- **FRED vintage values.** Only vintage *dates* are captured (F-024).

---

## 2. The Workbench-side representation

### 2.1 The rule

**The Workbench stores upstream keys and its own numbers. It stores no upstream observation
values.** (D-033.)

The reason is not disk space. HistFinTS observations are mutable in place, so a local copy is
not a snapshot with integrity — it is a second version of the truth with nothing to say which
one is stale. Duplication would also make the Workbench a second time-series store, which
D-001 exists to prevent.

The accepted cost: a finding can become **unresolvable** when the upstream row it names is
archived (D-003) or overwritten. That is a state the UI renders honestly. It is strictly
better information than a stale local copy that looks fresh.

### 2.2 The minimum object set

Three Workbench-owned records. Names are indicative; the shape is what matters.

**`evidence_reference`** — a pointer across the boundary, never a copy.

| Field | Purpose |
|---|---|
| `histfints_object` | Which upstream table: `OBSERVATION`, `CORRECTION`, `IMPORT_RUN`, `PROVIDER_ASSIGNMENT`, `PROVIDER_EVENT`, `OBSERVATION_CORRECTION` |
| `histfints_id` | The upstream primary key. Convention-level, unenforced (D-003). |
| `histfints_series_id` | Denormalised for query, and for detecting a stale reference. |
| `resolved_at` | When the Workbench last successfully read the row. |
| `resolution_state` | `RESOLVED` · `MISSING` · `TABLE_ABSENT` · `SERIES_ARCHIVED` |

`TABLE_ABSENT` is a first-class state, not an error, and it is the *normal* state today for
`PROVIDER_EVENT` and `OBSERVATION_CORRECTION` (§1.2). A schema-presence probe against
`histfints.sqlite_master` runs once per session and drives it.

**`discontinuity_calculation`** — the Workbench's own arithmetic, P4 `Calculated`.

Carries the Series, the period examined, the boundary date, the two values either side, the
step factor, the persistence-test results (per Q-052: 15 and 60–75 trading days), the
tolerance parameters used, and the code/spec version that produced it. It cites
`evidence_reference` rows for the observations it read. This is the one place where upstream
numbers are recorded, and they are recorded as *inputs to a stated calculation*, not as a
mirror of the store — a finding that cannot restate its own arithmetic is not traceable.

**`analytical_finding`** — the verdict, P4 `Calculated` plus a named classification.

Carries exactly one `discontinuity_calculation`, one verdict from §4, one reason code, the
set of `evidence_reference` rows consulted (including those that resolved to nothing — an
absence consulted is part of the lineage), and the correlation tolerance applied.

**Research conclusions are deliberately not in this increment's object set.** A conclusion is
`Asserted` and human-authored (§3). Specifying its storage now would invite the system to
write one. The only thing this increment owes the conclusion layer is that a finding is
citable.

---

## 3. The four layers, with epistemic status

Existing P4 vocabulary throughout — Observed / Calculated / Asserted. No new terms.

| Layer | P4 status | Owned by | Example |
|---|---|---|---|
| **Provider evidence** | `Observed` | HistFinTS | a `correction` row; an `import_run` and its `provider_assignment`; later, a `provider_event` SPLIT with numerator/denominator |
| **Workbench calculation** | `Calculated` | Workbench | the −49.4% step at 2024-01-24; the persistence test at 15 and 60 days; the ratio implied by the step |
| **Analytical finding** | `Calculated` + verdict | Workbench | "persistent step of 0.506× at 2024-01-24; no captured evidence at or within 5 days of that date; verdict *not explained by captured evidence*" |
| **Research conclusion** | `Asserted` | **a person** | "pre-2024-01-24 history for this Series is unusable for return calculations" |

Three rules make the layering real rather than decorative:

1. **No auto-promotion.** The system never writes an `Asserted` row. A conclusion is created
   by a human action and must cite the finding it rests on. A finding with no conclusion is a
   normal, permanent state.
2. **A verdict is a statement about HistFinTS, not about the world.** "Explained by captured
   evidence" means *HistFinTS recorded something consistent with this step*. It does not mean
   a split occurred. Rendering it as the latter is the fabricated-lineage failure P3 exists to
   prevent, so the UI string must carry the qualifier, not just the label.
3. **`UNKNOWN` beats a guess.** Where the provider behind an observation cannot be determined
   — an archived assignment, a missing `import_run` — the finding records `UNKNOWN`, not the
   Series' current top-priority provider.

---

## 4. The reconciliation capability

One capability, narrow on purpose.

### 4.1 Input

A `series_id`, a period, and the tolerance parameters (step threshold, persistence horizons,
event-date proximity window). Not a ticker — P1. The ticker never appears in a cache key, a
URL parameter or a stored reference; `provider_assignment.provider_series_identifier` is
displayed as *provenance*, never used as identity.

### 4.2 Steps

1. **Detect.** Run the Q-052 three-stage detector over `histfints.observation` for the
   period: candidate single-day moves, persistence at 15 and 60–75 trading days, and (for
   CEDEAR pairs only) residual against panel consensus. Output: zero or more boundary dates.
   Writes a `discontinuity_calculation` per boundary.
2. **Resolve evidence.** For each boundary, gather, and record as `evidence_reference` rows:
   - the observations either side, and their `import_run` → `provider_assignment` → `provider`
     chain — including **whether the two sides came from different providers**, which is the
     splice case and is visible today without any migration;
   - any `correction` rows on those observations, with `previous_value`/`new_value`/`detected_at`
     and the detecting run;
   - `provider_event` rows for the Series within the proximity window — **if the table
     exists**; otherwise a `TABLE_ABSENT` reference;
   - `observation_correction` / `revalidation_run` rows, same conditional.
3. **Classify.** §4.3.
4. **Record.** One `analytical_finding`. Stop. Do not repair, do not quarantine the Series, do
   not write anything to HistFinTS.

### 4.3 The verdict, and only these three values

| Verdict | Condition |
|---|---|
| **explained by captured evidence** | Captured evidence exists at or within the proximity window of the boundary **and** its magnitude reconciles with the computed step within the stated tolerance. Example: a `SPLIT` event with numerator/denominator 4:1 beside a step factor of 0.251. |
| **not explained by captured evidence** | The evidence tables were readable and held nothing at that date, **or** held something whose magnitude does not reconcile. |
| **insufficient evidence** | The question could not be put to the data. |

No fourth value. "Partially explained" and "explained with residual" were both considered and
rejected: each encodes a magnitude judgement the Workbench cannot make from event metadata,
and each would let a real mismatch pass as half-explained (D-033). The residual **is**
reported — as a `Calculated` number beside the verdict — but it does not get a verdict of its
own.

**Reason codes accompany the verdict; they do not extend it.** For `insufficient evidence`:
`EVIDENCE_TABLE_ABSENT` (§1.2 — the live case today) · `NO_CAPTURE_RUN_FOR_SERIES` ·
`PROVIDER_SUPPLIES_NO_REVISION_DATA` (ECB, per HistFinTS `docs/KNOWN_LIMITATIONS.md:79–81`) ·
`UPSTREAM_REFERENCE_UNRESOLVABLE`. For `not explained`: `NO_EVIDENCE_AT_DATE` ·
`MAGNITUDE_MISMATCH` · `PROVIDER_SPLICE_AT_BOUNDARY`.

### 4.4 Two rules that stop the verdict from being vacuous

**A bare FRED `REVISION` event is not explanatory.** Per F-024, a vintage date is captured for
essentially every FRED release, so accepting one as explanation would return *explained* for
almost every macro discontinuity, defects included. A FRED boundary resolves to
`insufficient evidence` with reason `PROVIDER_SUPPLIES_NO_REVISION_DATA` unless and until
vintage *values* are captured via `get_observations_at_vintage()`
(`providers/fred.py:87–106`, currently called from nowhere in `src/`).

**Event correlation is `Calculated`, not `Observed`.** `provider_event` carries no FK to any
observation or correction (F-023), so the join is by `series_id` plus date proximity plus a
tolerance. The tolerance is a parameter and must appear in the finding's provenance. And
because `acquired_at` is capture time rather than fetch time (F-025), any before/after timing
claim is labelled a proxy.

---

## 5. Traceability requirement

For any displayed finding, a reader must be able to walk, in one direction, without leaving
the UI:

```
Series (series_id, label, currency, instrument_subtype)
  -> period examined, and the detector parameters used
  -> affected observations (observation.id, observed_at, value)
       -> import_run (id, status, started_at)     [status ≠ complete range — F-017]
       -> provider_assignment (provider_series_identifier)   [provenance, not identity]
       -> provider (display_name, implementation_key)
  -> HistFinTS evidence consulted, including what resolved to nothing
       -> correction rows (field, previous_value, new_value, detected_at, detecting run)
       -> provider_event rows, or TABLE_ABSENT
  -> Workbench calculation (step factor, persistence results, tolerances, code version)
  -> Analytical Finding (verdict + reason code)
  -> Research Conclusion, if a human wrote one — otherwise visibly absent
```

Two acceptance points follow, and both are testable:

- **An opaque status is a failure, not a simplification.** A finding rendered as a badge with
  no expandable lineage does not satisfy P3, however clean it looks.
- **Consulted absences are part of the lineage.** "No `provider_event` table in the attached
  database" must be *visible in the finding*, not inferred from a missing section. This is
  what separates an honest gap from fabricated lineage.

---

## 6. Test boundary

The test exercises the **real read-only ATTACH boundary** (D-001), not a duplicated dataset:

```sql
ATTACH DATABASE 'file:.../histfints.db?mode=ro' AS histfints;
```

Concretely:

- Queries run against a **read-only handle on a copy of the real production file**, so the
  schema under test is the real schema — including `user_version = 10` and the genuinely
  absent tables. A hand-built fixture schema would silently pass tests that the real boundary
  fails, which is precisely the class of error D-009b names.
- **A write attempt to `histfints.*` must be asserted to fail.** This is a boundary test, not
  a data test.
- **The `TABLE_ABSENT` path is a first-class test case**, not an error case.
- **The discontinuity must be constructed, not found.** Every `provider_assignment` in the
  live store was created between 2026-08-04 and 2026-08-15; no tracked Series has lived
  through a split under HistFinTS's observation. A test that finds no discontinuity in real
  data has proved nothing about the detector (D-009). Construct a Workbench-side fixture
  Series with a known step and assert the detector finds it, the reason code, and the
  full traceability chain.
- **`explained by captured evidence` can only be tested against a fixture with migrations
  0011–0013 applied to a copy.** Test it there; do not let a green fixture test be reported as
  the capability working against production.

---

## 7. Out of scope for this increment

Explicitly, and each for a reason:

- **R3 (integrity detection gate).** A gate acts on a verdict; this increment is establishing
  whether the verdict is trustworthy. Gating on an untested classifier is worse than not
  gating.
- **Any HistFinTS repair mechanism.** HistFinTS is read-only from here (D-001). Repair is
  upstream work and has been deliberately halted.
- **Observation replication.** §2.1.
- **Natural-language question answering.** Nothing in the requirement needs it.
- **A generalised event-analysis framework.** One capability, one Series, one period, three
  verdicts. Generalising before the narrow case is proven is how the vocabulary grows to
  fifteen values.
- **Mispricing, arbitrage or any investment inference.** A research conclusion is `Asserted`
  by a human (§3); an investment inference is a further step the system does not take at all.
- **Dated CEDEAR ratios (F-021), adjustment-basis normalisation (F-010), panel eligibility
  (`SPEC-panel-eligibility.md`).** All real, all separately tracked, none of them this
  increment.
- **Any scope beyond proving the evidence-consumption pattern.**

---

## 8. The call on upstream incompleteness

The directive that opened this increment referred to "the completed HistFinTS F-009 evidence
chain." **It is not completed in any sense the Workbench can read.** R1, R2a, R2b-FRED and
R2b-Yahoo are implemented in code; migrations 0011–0013 are unapplied, the three evidence
tables do not exist in the production database, and no capture command has ever been run
against it (D-032).

**The call: proceed, and do not treat F-012 or vintage capture as a blocker for this
increment.** The reasoning, stated so it can be disagreed with:

The increment's purpose is to prove the Workbench can consume evidence *without confusing
evidence with interpretation*. The hard half of that proof is **declining to explain** —
correctly reporting `insufficient evidence` when the evidence is absent, and
`not explained by captured evidence` when it is present but silent. Today's database exercises
both, honestly and immediately. A consumer built and tested only against a populated evidence
chain is a consumer never tested on the case that actually occurs in production.

The alternative — declaring the increment blocked until the migration lands and capture runs —
is defensible, and it has one genuine advantage: `explained by captured evidence` would be
reachable end to end against real data rather than a fixture. It is rejected because it makes
the Workbench's readiness a function of upstream scheduling, on a workstream that has just
been deliberately halted, in exchange for exercising the *easiest* of the three verdicts.

**What proceeding obliges, and these are not optional:**

1. **`explained by captured evidence` is documented as structurally unreachable against
   production today**, and the acceptance criteria say so. If it ever appears against the live
   database before the migration is applied, that is a bug in the reconciler, not a success.
2. **Every evidence query is written behind a schema-presence probe from the start.** Not
   retrofitted. The absent-table path is the primary path today and must be the one that is
   best tested.
3. **The reachable-verdict set is stated in the UI**, so a user reading "insufficient
   evidence" across an entire Series understands they are seeing an upstream capture gap
   rather than a clean bill of health. This is the D-009 failure mode expressed as an
   interface risk: a screen full of benign-looking verdicts that means only "nobody has looked
   yet."
4. **Applying migrations 0011–0013 and running the capture commands once against a copy is
   filed as the immediate next upstream ask** — cheap, mechanical, and it converts a fixture
   test into a real one.

---

## 9. Open dependencies

| Item | Status |
|---|---|
| Q-027 (trading calendar) | Open. The persistence test counts **trading** days at 15 and 60–75; without a venue calendar it degrades to calendar days, which is acceptable for this increment provided the finding records which was used. |
| Migrations 0011–0013 applied upstream | **Not applied.** Gates the `explained` verdict only (§8.1). |
| FRED vintage-value capture | Not implemented (F-024). Gates any `explained` verdict for macro Series. |
| A-014 (correct `HISTFINTS-BRIEF-v2.md`) | Queued. The brief is stale on FRED vintages and Yahoo events. |
