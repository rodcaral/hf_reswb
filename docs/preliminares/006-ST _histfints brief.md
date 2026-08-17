# HistFinTS — brief for the Research Workbench team (v2)

**Supersedes:** the original consuming-team brief (2026-08, reproduced in full reasoning at
`docs/DECISIONS.md`). **Status:** current as of 2026-08-15, pending three unconfirmed
HistFinTS filings (§8).

> **Why this document exists.** The original brief was accurate as a summary and was twice
> misread as exhaustive during review — once causing a retracted finding (`observation`
> *does* carry `import_run_id`; see D-019 in `DECISIONS.md`). This version states what is
> **confirmed against schema and code**, distinguishes that from what is still **inferred or
> pending**, and is the fast-start reference. `docs/DECISIONS.md` is the full reasoning and
> evidence trail behind every claim here — consult it before relying on anything not stated
> plainly in this file.

---

## 1. What it is

Local, single-user desktop application (Python, SQLite) maintaining a deduplicated,
incrementally-updated historical database of financial/economic time series ("Series")
pulled from multiple providers: Yahoo Finance, Alpha Vantage, FRED, ECB, Stooq, BYMA.

A separate **Series Catalog** subsystem discovers and deduplicates raw provider tickers
before they become a Series. As of this writing it is **not producing the data you will
use** — see §5.

**Where the data lives:** one SQLite 3.37+ file (`foreign_keys = ON`). No server, no
concurrent-writer model. **Treat it as read-only** — this is architectural, not just a
convention (`docs/DECISIONS.md` D-001): attach it via `ATTACH DATABASE ... AS histfints
(mode=ro)`, never write to it directly.

---

## 2. Core tables — corrected

### `series`
One row per tracked instrument: `label`, `series_type` (STOCK/ETF/BOND/CURRENCY_PAIR/…),
`configured_interval`, `status` (ACTIVE/DISABLED/DELISTED_OR_DISCONTINUED/…), optional
`currency`/`country`/`instrument_subtype`, nullable `settlement_mechanism` (present since
migration `0004`, currently unused by any resolved multi-settlement instrument), optional
`underlying_series_id` + `ratio` (for CEDEAR/wrapper relationships — see §6).

`DELISTED_OR_DISCONTINUED`/`USER_DISABLED` Series retain valid historical `observation`
rows; they are simply no longer actively imported.

### `provider` / `provider_assignment`
A Series can be backed by several providers, ranked by `priority` (1 = primary, used first;
others fallback). `provider_assignment` links `series_id` ↔ `provider_id` with the
provider's raw ticker.

**Correction to the original brief:** this is the row that determines *who actually supplies
observations for a Series*, and is the correct anchor for any per-provider metadata you need
(adjustment basis, availability — both pending, §8). It is **not** the same graph as
`provider_symbol` (§5) — do not confuse the two when reasoning about a Series' data source.

### `import_run`
One row per fetch attempt against a `provider_assignment` (`SUCCESS`/`PARTIAL`/`FAILED`,
timestamps). **Does not record adapter version or endpoint variant** — if the adapter layer
changes what it requests, nothing distinguishes rows from before vs. after.

**`SUCCESS` does not imply the requested range was fully populated.** Confirmed live: a
Series received 19 of ~408 real observations from one wide-range request marked `SUCCESS`
(Yahoo's own silent truncation on wide date ranges, documented in HistFinTS's own
`KNOWN_LIMITATIONS.md`). Build no completeness assumption on `status` alone.

### `observation`
`series_id`, `import_run_id` (**exists, `NOT NULL`, since the v1 baseline** — the original
brief's column list was not exhaustive and earlier review notes wrongly treated it as
missing observation-level provenance; it does not), `observed_at` (UTC), `value`, optional
`open`/`high`/`low`/`volume` (NULL for value-only sources). `UNIQUE(series_id, observed_at)`.

**What `value` means is provider-dependent and currently unrecorded in the schema** (§7).
This is the single most important operational fact about this table.

### `correction`
**Better provenanced than `observation` itself.** `import_run_id NOT NULL` FK to the
correcting run, `field_name CHECK IN ('value','open','high','low','volume')` — all five
fields covered, confirmed live (0 of 13,302 rows null). This identifies the *correcting* run
only, never the *originating* one.

**`correction` cannot detect anything older than the system's re-fetch window — confirmed
at the line level to be effectively one date.** `ImportService._determine_range()`
(`application/import_service.py:183–200`) starts from the latest stored observation minus
`default_revalidation_window_days`, **which is `NULL` (zero look-back) for all three
currently-configured providers** — FRED, Yahoo, BYMA. `start = latest` is inclusive, so the
single most-recent stored date is re-examined every import; **every older date is never
requested again.** A provider revision or a rescale on any date but the latest will never
produce a `correction` row and will never be flagged. See §7 for the confirmed consequence.

### `series_merge`
`survivor_series_id`, `absorbed_series_id`, `match_candidate_id UNIQUE`, `merged_at`. The
MERGE repair path: `SELECT survivor_series_id FROM series_merge WHERE absorbed_series_id =
?`. **Must be applied recursively** — nothing prevents a survivor from later being absorbed
itself. **Empty in production** — schema/trigger-confirmed, not yet exercised by a real
MERGE.

---

## 3. Full schema reference

`docs/DATABASE_SCHEMA.md` in the HistFinTS repo — current, all migrations merged. **Not**
`schema.sql`, which is deliberately frozen at an old baseline. Verify against the live
schema for anything load-bearing; several errors in this review's early rounds came from
trusting a summary over the artifact (`docs/DECISIONS.md` D-009b).

---

## 4. Adjustment basis — confirmed per provider

No schema field records this today (§8 requests one). Confirmed values, to hold in code
until the field lands:

| Provider | Basis | Confidence |
|---|---|---|
| **Yahoo Finance** | **Split-adjusted, dividend-unadjusted.** Reads `indicators.quote[0].close`, not `adjclose`. Verified against AAPL across both its splits — dividend-unadjustment separately confirmed by cross-checking the cumulative split factor against the published raw close (0.017% residual, consistent with rounding, not the 10–15% a dividend adjustment would produce). | code + data |
| **Alpha Vantage** | Raw/unadjusted. Calls `TIME_SERIES_DAILY`, not the `_ADJUSTED` variant. | code only, no data in this DB to check |
| **FRED** | N/A — value-only. **Adapter passes no vintage parameters**, so it always fetches current vintage; combined with the re-fetch window above, a value freezes at whatever vintage was current on first fetch. | code |
| **BYMA** | N/A — **supplies no `observation.value` at all.** Excluded from `PROVIDER_REGISTRY`. Every currently BYMA-linked Series gets its actual prices from a Yahoo `.BA` cross-listing — the real basis is Yahoo's, and the BYMA price-fetch path is entirely unexercised. | code |
| **ECB / World Bank** | N/A — value-only. Revision behaviour **assumed to occur, not verified.** | assumed |
| **Stooq** | **Unknown.** Empirical check attempted and blocked by client-side bot detection on the public endpoint. If Stooq is ever used as a fallback, treat as unknown-basis until established — do not assume it matches any other provider. | unconfirmed |

**A Series fallback-spliced across two providers with different bases carries an unmarked
scale change at the handover, undetectable by any consumer today.**

---

## 5. Series Catalog — the part you don't need, plus one thing you do

The Catalog subsystem is a separate identity graph from the one that actually produces data:

```
Catalog (identity/discovery)          Operational (data acquisition)
   ProviderSymbol                        Series
       ↓                                    ↓
   match_candidate                      ProviderAssignment
       ↓                                    ↓
   Series                               ImportRun → Observation
```

They meet only at `Series`. **`provider_symbol_id` appears only on `match_candidate` and
`identifier` — never on `provider_assignment` or `series`.** A Series created via
`add_series` (direct entry) has **no path at all** to any `provider_symbol` row.

**Direct entry (`add_series`) is a permanent, first-class creation path, not a bypass.** On
the original `master` branch it was the *only* way to create a Series; Catalog was added
alongside it later, specifically for bulk automated discovery of tickers nobody has looked
at. Confirmed in HistFinTS's own `docs/README.md` branch history.

**As of this review, Catalog discovery has produced none of the working data.** 1,491 BYMA
`ProviderSymbol`s discovered; 11 ever produced a `match_candidate`; **zero resolved into a
Series.** Every currently-usable Series — all US equities, macro, and all 8 CEDEAR pilot
Series — was created by direct entry.

**Consequence for provenance:** direct-entry Series carry no evidence trail. `add_series` and
`add-provider-assignment` persist the assignment and nothing else — no rationale, no rejected
alternatives, no re-verification date. `entity_change_log` only ever writes
`entity_type='ProviderSymbol'` rows (confirmed: zero rows of any other type exist).
**Treat direct-entry Series identity as `Asserted`, not `Observed`** — a fourth data class
alongside Observed/Calculated/Reported, one with its own internal quality gradient (a human
checking a live source and rejecting bad candidates is much stronger than a guess, but both
currently look identical in the schema).

---

## 6. CEDEAR / relationship structure

`series.underlying_series_id` + `series.ratio`, set via `SET_UNDERLYING` — models CEDEAR ↔
underlying (and by extension ADR-type relationships, though see below).

**`ratio` is a bare, undated scalar with no effective-date field, no history, and no audit
trail anywhere in the system** — confirmed by tracing both code paths that can set it
(auto-resolve, which requires a BYMA `underlying_ratio` field that the real BYMA reader
**never populates**; and direct human entry via CLI/GUI/web, the only path actually used).
**This is confirmed wrong in live data**, not just theoretically incomplete: the Apple
CEDEAR pair shows a clean ~2:1 step on 2024-01-24 with no change on the US-listed
underlying, consistent with the Argentine issuer doubling the ratio after the December 2023
devaluation — a purely local event with no trace in any international corporate-actions
feed. **Never apply a Series' current `ratio` across a historical date without checking
whether it held on that date.**

**Regulatory context** (CNV Normas, Título II, Cap. VIII, as substituted by RG 1142/2026):
conversion ratios are reported quarterly and change by formal dated Prospectus Supplement.
Three distinct relationship kinds exist — CEDEAR, ADR, Doble Listado — with different
mechanics; `SET_UNDERLYING` currently models only one edge shape for all three. Full detail
in `docs/KB-argentine-instruments.md`.

**Providers do not appear to rebase CEDEAR history for ratio changes.** The 2024-01-24 step
is visible, unmarked, in the stored data — consistent with the *issuer* absorbing the
underlying's 2020 4:1 split into the ratio rather than the price series being rebased.
Treat CEDEAR price series as as-traded.

---

## 7. Known defects to code around

| ID | One line | Status |
|---|---|---|
| **F-009** | Incremental import leaves a permanent, unmarked scale discontinuity at splits — the re-fetch window (§2 `correction`) never revisits old dates. | **Confirmed by construction** (fixture backfill + incremental import; ratio 4.90 across boundary, zero `correction` rows, both `ImportRun`s `SUCCESS`). Filed as `docs/histfints-requests/DEFECT-F009.md`, not yet confirmed landed. |
| **F-013** | Same mechanism, applied to any provider that retroactively revises values (FRED). | **Confirmed by construction**, same filing. |
| **F-017** | `import_run.status = SUCCESS` does not imply the requested range was fetched. | **Live**, confirmed (ETHA: 19/~408 bars). |
| **F-021** | CEDEAR `ratio` applied without checking effective date. | **Confirmed wrong in live data** (§6). |
| **F-022** | No data class exists for `Asserted` values (hand-typed ratios, direct-entry identity). | Design gap, Workbench-side. |

None of F-009/F-013/F-017 are theoretical. All three were reproduced against real code and
real data during this review; do not treat them as edge cases.

---

## 8. Pending HistFinTS changes — not yet confirmed landed

Three filings sent, status unconfirmed as of this brief. **Check before assuming any of
these exist:**

1. `docs/histfints-requests/DEFECT-F009.md` — the discontinuity defect above.
2. `docs/histfints-requests/REQUEST-tranche2-migration.md` — adjustment-basis field on
   `provider`/`provider_assignment` (with `NOT APPLICABLE` distinct from `UNKNOWN`), plus a
   provider-assignment-level **availability marker** (`KNOWN`/`UNRESOLVED`) — required
   because `provider_symbol.first_available_date` exists but is unreachable from most
   Series and describes the wrong provider even when reachable (§5). This is an
   **adapter-interface change**, not just a column — see the filing for why.
3. `docs/histfints-requests/REQUEST-event-capture.md` — parse and persist the Yahoo
   `events` (splits/dividends) payload already requested on every fetch (`"events":
   "div,splits"`, `providers/yahoo_finance.py:63`) and currently discarded unread.

**If any of these have landed, update this brief before writing code that assumes they
haven't** — in particular, coverage/completeness logic and adjustment-aware calculations
depend directly on #2.

---

## 9. V0 data reality

11,319 Series total. 74 with zero observations; 11,245 with ≥1; ~9,418 with ≥250 (1yr);
~6,308 with ≥1,250 (5yr). Range 2000-01-03 → 2026-08-14.

**Composition:** ~11,308 US equities/ETFs (Yahoo), 1 macro indicator (FRED), and a
hand-verified set of Argentine/CEDEAR names via Yahoo `.BA` — YPF, Banco Macro, Comercial
del Plata, Pampa Energía, plus CEDEARs for Apple, GLD, ETHA (partial — truncated per F-017),
Alibaba, Baidu, Uber. **Zero Series backed by the BYMA provider itself for prices** — every
Argentine-linked Series' real data comes via Yahoo.

**The `>365-day` gap between `backfill_start_date` and actual first observation (9,544
Series) is mostly explained by `backfill_start_date` having been blanket-set to
`2000-01-01`**, not by truncation — sampled verification against Yahoo's own
`firstTradeDate` confirmed 5/5 checked. Not exhaustively verified; do not treat as fully
ruled out for the whole population.

---

## 10. Terminology (binding — see `docs/DECISIONS.md` §5 for the full glossary)

**Series**, not "instrument". **series_master_list**, not "instrument universe".
