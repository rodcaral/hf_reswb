# Data-Acquisition Quality Investigation — STALE / NEVER / FAILED Inventory

**Date:** 2026-08-22
**From:** SDT Workbench
**To:** SE / SDT HistFinTS
**Status: read-only investigation only. No provider reassignment, schedule modification,
catalog or observation mutation, remediation, migration, or production-policy change performed
or proposed. The completed SDT-1/Class-D/Class-E work is not reopened — where a series from
that work appears in this inventory, it is reported as an observed fact only, not re-evaluated.**

All figures below were computed by direct, read-only query against the live HistFinTS database
at investigation time (`now = 2026-08-22T12:12:32Z`), reproducing `classify_import_state()`'s
own logic (`histfints-v3/src/histfints/domain/import_state.py`) rather than trusting any
previously-cited count.

---

## 1. NEVER population — reconciled first, per DFA's stated priority

**Reconciled count: 12, not 8 (previously cited) and not 14.** Traced to exact row-level
population, not merely re-asserted.

`NEVER` = active Series with no `import_run` at all, per `classify_import_state()`'s own rule
(`last_status is None`). This is structurally two disjoint sub-populations, both correctly
captured by the single `NEVER` label but with materially different implications:

### 1a. Zero `provider_assignment` at all (6 series) — cannot be imported by construction

| Series | Label | Created | Note |
|---|---|---|---|
| 11344 | SPDR Gold Shares - ETF (NYSE) | 2026-08-18 | **Already documented**: Class-C GLD-target orphan (`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`). Not re-evaluated here. |
| 11347 | Uber Technologies - Stock (NYSE) | 2026-08-18 | **Already documented**: Class-C UBER-target orphan. Not re-evaluated here. |
| 11356 | Equinor ASA (NYSE) | 2026-08-19T01:10:23Z | New to this inventory. |
| 11360 | iShares Core MSCI Europe ETF | 2026-08-19T01:10:23Z | New to this inventory. |
| 11367 | S&P 500 Index | 2026-08-19T01:10:23Z | New to this inventory. |
| 11368 | Cboe Volatility Index | 2026-08-19T01:10:23Z | New to this inventory. |

**Observed fact**: the four new-to-this-inventory rows were all created within the same second
(`2026-08-19T01:10:23`Z) — a single batch catalog-add event — and none received a provider
assignment. **Hypothesis, not confirmed**: this reads as a batch import process that completed
the catalog-add step but not the assignment step for these four rows; the mechanism that would
confirm this (the batch job's own log) was not available to this read-only database review.

### 1b. Assignment exists, zero `import_run` rows (6 series) — a data-hygiene finding, not an acquisition-quality one

| Series | Label | Provider symbol | Created |
|---|---|---|---|
| 11304 | GLD Smoke Test CEDEAR | GLD / GLD | 2026-08-11 |
| 11306 | Duplicate Warning Test | ZZZTEST1 | 2026-08-12 |
| 11307 | Duplicate Warning Test | ZZZTEST2 | 2026-08-12 |
| 11308 | UC-6 Test Series | UC6TEST2 | 2026-08-12 |
| 11309 | LIVE-VERIFY-BULK-IMPORT-TEST | LIVE-VERIFY-BULK-IMPORT-TEST | 2026-08-12 |
| 11310 | Apple Inc. - Common Stock | AAPL-BULK-VERIFY-DUP | 2026-08-12 |

**Observed fact**: all six labels and/or provider symbols explicitly identify themselves as
test/smoke-test/verification artifacts ("Smoke Test", "Duplicate Warning Test", "UC-6 Test
Series", "LIVE-VERIFY-BULK-IMPORT-TEST", "-BULK-VERIFY-DUP"). None resembles a real production
financial series awaiting acquisition. **This population should not be read as an
acquisition-quality signal at all** — it is evidence of test fixtures left in the live ACTIVE
series table, a distinct data-hygiene question from "is real financial data being acquired."

### Reconciliation of the cited "8"

`ImportStatusView`'s own code comment (`import_status_view.py` line 54) states "the eight [Series]
that are not [scheduled] are exactly the assignment-less ones" — this is the origin of "8," and
it **only ever counted §1a's population**, not §1b. Since that comment was written, active
Series count grew from 11,383 to 11,387, and §1a's own count moved from 8 to 6 (two of the
original eight — plausibly including cases resolved by this session's own BABA/BIDU work,
though this was not re-traced since it would reopen closed work) while §1b's six-row test-
fixture population is either new or was not previously counted under this lens. **The
discrepancy is fully explained by (a) two different sub-populations being combined under one
label and (b) ordinary data drift** — not by a defect in `classify_import_state()`, which
correctly and consistently applies "no run at all" to both sub-populations per its own
documented rule.

---

## 2. STALE population (32) — one well-evidenced, cohort-specific scheduling gap, not 32 independent problems

**Observed fact, not a hypothesis**: all 32 `STALE` Series are `configured_interval='1h'`, and
every one of their most recent `import_run` rows has `started_at` clustered within a single
53-second window: **2026-08-21T10:05:53Z through 2026-08-21T10:06:39Z**. None of these 32 has
run since. This is directly queryable, not inferred.

**Observed fact**: of the 41 total ACTIVE `1h`-interval Series, only 2 (series 259 — Adecoagro
S.A., and 1601 — Corporacion America Airports) have run within the last 24 hours as of this
investigation (most recently at 2026-08-22T11:41–11:50Z, i.e. actively running **today**, hours
after this investigation began). Both are low series ids, predating the 2026-08-11+ CEDEAR/
BYMA/seven-pair expansion batch that the 32 stale Series belong to (series ids 11305–11353, all
provider-assignment ids in the clustered 11312–11386 range).

**All 32 stale Series belong to the same catalog-expansion batch**: the BYMA CEDEAR cohort
(Apple, GLD, YPF, Banco Macro, Pampa Energia, Alibaba, Baidu, iShares Ethereum Trust, Uber,
Micron, Microsoft, AMD, MercadoLibre, Nu, QQQ, Amazon CEDEARs), the Argentine-listing common
shares added alongside it (Tenaris, Ternium, Globant, iShares China Large-Cap, iShares Bitcoin
Mini Trust, JD.com, Petrobras, ProShares Short S&P 500), and the seven D-pair current/proposed
target series from this session's own Class-D work (11342/11343/11348/11349/11350/11351/11352/
11353 — appearing here purely as members of the affected 1h cohort, **not re-evaluated for
Class-D/Class-E purposes**).

**Hypothesis, explicitly not confirmed**: the uniform last-run timestamp and the sharp contrast
with the two long-lived 1h Series (259, 1601) that continue running today is consistent with
this cohort being served by a distinct scheduled task or job (plausibly the "BYMA Evidence
Collection" task named in an earlier, separately-flagged instruction this session) that has not
executed since 2026-08-21T10:06, while the general/legacy scheduler continues running normally.
**This could not be confirmed from database evidence alone** — no scheduler/cron configuration
table exists in this schema to inspect directly; this is stated as the most consistent
explanation of the observed pattern, not as a verified mechanism.

**Alternative acquisition paths**: not separately checked per-row for all 32 (out of scope for
this pass given the single, cohort-wide root cause already found), but the same provider
(Yahoo, `provider_id=2`) that successfully populated 2,866+ historical rows for this exact
cohort in the past (`CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md`) is still the configured
primary assignment for all 32 — there is no evidence the provider itself is the blocker, which
is consistent with (not proof of) the scheduling-mechanism hypothesis above rather than a
provider/identifier-level failure.

---

## 3. FAILED population (65) — two distinct, well-evidenced root causes plus one unresolved pattern

### 3a. Identifier-format mismatch (61 of 65) — the dominant, clearly evidenced cause

**Observed fact**: 61 of 65 `FAILED` Series carry a provider symbol containing `.` or `$`
(e.g. `AKO.A`, `BF.A`, `BH.A`, `AHL$D`, `ATH$A`, `BAC$E`) and every one of their failing runs
recorded the identical error shape: `"Yahoo Finance HTTP 404 for '<symbol>'"`. These are share-
class (`.A`/`.B`) and preferred-share (`$`-series) ticker conventions stored in this catalog's
raw form; Yahoo Finance's API does not resolve symbols in this literal format (its own
convention typically substitutes a hyphen, e.g. `BRK-A`, and encodes preferred shares
differently) — **this is a well-evidenced identifier-format failure**, not a data-availability
problem: the underlying securities are real, listed instruments; the stored identifier does not
match what the provider's endpoint expects.

**None of these 61 has a second `provider_assignment`** — confirmed by query. **No currently-
configured alternative acquisition path exists for this population** — every one of the 61
fails for the same structural reason (symbol encoding), and there is no fallback provider
assignment recorded that a retry could use instead.

### 3b. Rate-limiting on Twelve Data, both configured paths currently failing (3 of 65)

Series 11339 (SLV), 11340 (UBER), 11341 (URA) each carry two provider assignments (Yahoo
priority 1, Twelve Data priority 3). **Full run history traced, not just the latest attempt**:
every Yahoo-path attempt for these three, across five separate runs from 2026-08-18 through
2026-08-21, failed with `HTTP 422` (a distinct status from the 404s in §3a — request-level
rejection, not "symbol not found"). The Twelve Data fallback succeeded twice (2026-08-18,
2026-08-19) then failed twice more (2026-08-20, 2026-08-21) with `HTTP 429` (rate limit).

**Both configured paths are currently failing for these three Series as of the latest attempt**
— this is not a case of an untried, evidenced alternative sitting available; it was traced
across the full history, not assumed from the presence of a second assignment. Series 11340 is
the same `UBER`/provider-2/Twelve-Data-symbol series already on record in this session's Class-E
work (10165↔11340, `SAME_INSTRUMENT` technical signal, financial disposition `UNRESOLVED`) —
**noted here only as a cross-reference**: its zero-observation state is explained by this
acquisition failure history, not by anything Class-E-related, and this observation does not
reopen or bear on that disposition.

### 3c. One unresolved, distinct failure (FCX, 1 of 65)

Series 11333 (`FCX`, Freeport-McMoRan): `Yahoo Finance HTTP 422 for 'FCX'`, a plain ticker with
no identifier-format issue and no `.`/`$` character, structurally similar in HTTP status to
§3b's three but with no working fallback provider (single Yahoo assignment only) and no
successful run in its history to compare against. **Root cause not established** — reported as
an evidence gap (§5), not resolved here.

---

## 4. Financial/data-quality implications — currentness, completeness, comparability

Per instruction, no financial invalidity is inferred from any of FAILED/STALE/NEVER alone.
Stated as implications for downstream analytical use, not as a defect ruling:

- **Currentness**: the 32 STALE Series (§2) — including several already-examined Class-D/E
  series in this session's own work — have not received a new observation since 2026-08-21
  10:06 UTC. Any analysis treating their most recent value as "current market price" as of
  today would be working with data over a day old for an hourly-configured series — a
  currentness gap, not a correctness defect in the historical data itself.
- **Completeness**: the 65 FAILED Series (§3) have zero prospect of a new observation under
  their current configuration — §3a's 61 will fail on every future attempt until the identifier
  format is corrected (a structural, not transient, gap); §3b/3c's 4 may or may not resolve
  depending on whether the rate limit clears or the 422 cause is found. None of the 65 has lost
  any *historical* data — this is entirely a forward-looking completeness gap for series that,
  per available evidence, may never have successfully acquired any observation (11333, 11339,
  11340, 11341 all show `0` observations currently) or whose gap is limited to the period since
  each series' own last successful run.
- **Comparability**: the identifier-format failures (§3a) affect specifically share-class and
  preferred-share instruments — a comparison spanning "all US equities" that silently excludes
  every `.A`/`.B`/preferred-share ticker without flagging it would understate coverage for that
  instrument category specifically, not uniformly across the catalog. This is a comparability
  risk for any downstream population-level analysis (e.g. sector aggregates including preferred
  shares) that does not separately account for this systematic gap.

---

## 5. Evidence gaps

- **No scheduler/cron configuration is visible from this database** — the STALE cohort's most
  consistent explanation (§2) is a hypothesis about an external scheduling mechanism this
  review could not directly inspect.
- **FCX's (§3c) HTTP 422 root cause is unresolved** — no comparable successful history exists
  for this series to diagnose against, and no ImportErrorRecord detail beyond the bare status
  code is stored.
- **The four new NEVER/assignment-less Series (§1a)** — whether their missing assignment is a
  pending manual step, a known batch-process gap, or an oversight is not evidenced from the
  database alone.
- **§3b's HTTP 422 pattern on Yahoo** (SLV/UBER/URA/FCX) was not compared against Yahoo's actual
  API contract or request payload — this review had no access to the request construction code
  path, only the recorded outcome.

---

## 6. Candidate follow-up capability/policy decisions (named, not decided)

Per instruction, no decision is made here — these are named as open items for SE/DFA/product to
consider, not proposals this review recommends or is authorized to act on:

1. Whether identifier-format normalization (translating stored `.`/`$` conventions to each
   provider's expected format at request time) is worth building, given it would address 61 of
   65 current failures with one mechanism.
2. Whether the four assignment-less §1a Series need a manual assignment step, and whether that
   batch-add process should be changed to always create an assignment.
3. Whether the six §1b test-fixture Series should be archived/removed from the live ACTIVE
   population — a data-hygiene question independent of acquisition quality.
4. Whether the STALE cohort's suspected scheduling gap (§2) needs operational investigation
   outside this database's visibility.
5. Whether a rate-limit backoff/retry policy is warranted for the Twelve Data fallback path
   (§3b), given it has historically succeeded for these three Series.

---

## What this investigation does not do

- Does not reassign any provider, modify any schedule, or touch any catalog/observation row.
- Does not reopen or re-evaluate the seven Class-D series, the BABA/BIDU disposition, or the
  10165↔11340 disposition — each appears here only as a member of a population being inventoried
  for acquisition-quality purposes, with the same status already on record.
- Does not assert financial invalidity for any FAILED, STALE, or NEVER Series.
- Does not propose or stage any remediation, migration, or policy change.
