# REQUEST — Tranche 2: adjustment basis (one migration item)

**Type:** Two additive schema changes, one coherent concern.
**Filed:** 2026-08-15 · **Revised same day after schema review** · **From:** Research Workbench
**Prior filings:** `DEFECT-F009.md` · `REQUEST-basis-factsheet.md` · `ASK-histfints-questions.md`

> **Revision note.** An earlier draft proposed three items. Schema review found that one
> already exists (withdrawn below, rather than silently dropped) and that a second targeted
> the wrong row — re-scoped rather than abandoned, since the underlying need is confirmed
> live.

---

## Withdrawn — `import_run_id` on `observation`

**Already exists.** `NOT NULL`, a real FK, in `schema.sql` since the v1 baseline. Every
observation already traces to the run that wrote it, and from there through
`provider_assignment` to the provider and its raw ticker.

The gap we believed existed never did. Our finding was built on a prose column summary read
as exhaustive, and was not checked against the schema. Withdrawn with apologies for the
noise.

*One narrower point, raised as a note rather than a request.* `import_run` records no
adapter version or endpoint variant — confirmed against the schema. If the adapter layer
changes what it requests, nothing distinguishes rows written before the change from those
written after.

Narrow today. It becomes material the moment any adapter change ships — and the cost lands
**retroactively**, since rows already written cannot be attributed after the fact. **Not
requested here**, but if the adapter layer is being modified for any other reason, adding
this in the same migration is close to free, while adding it later is not.

---

## Second item — a completeness marker on `provider_assignment`

**Re-scoped after schema review.** An earlier draft proposed populating the existing
`provider_symbol.first_available_date`. That is the wrong row, for two structural reasons
rather than a missing join.

`provider_symbol_id` appears only on `match_candidate` and `identifier` — never on
`provider_assignment` or `series`. So:

1. **Series created via `add-series` have no path to any `provider_symbol` at all.** They
   never entered Catalog discovery, and this currently includes every hand-curated Series in
   the database.
2. **Even for a resolved Series, the reachable `provider_symbol` is the discovery-side one,
   which need not be the provider supplying observations.** A CEDEAR discovered via BYMA but
   priced from a Yahoo `.BA` assignment has no `ProviderSymbol` row for Yahoo at all — Yahoo
   is never discovery-scanned. A populated `first_available_date` there describes BYMA's
   listing depth, not the depth of the feed actually supplying the values.

**The ask, stated precisely.** A provider-assignment-level availability marker is required
before the system can reliably distinguish *insufficient historical existence* from
*incomplete stored coverage*. It must describe the **provider assignment from which the
observations are being evaluated**, not a discovery-side `ProviderSymbol`, and it must be
reachable from every Series regardless of how that Series was created.

```
Series → ProviderAssignment → availability metadata        (required)
Series → resolved MatchCandidate → ProviderSymbol → …      (not sufficient)
```

`provider_assignment` is the correct row on cardinality grounds as well: availability is
stable across fetches, so not `import_run`; and a Series may carry several assignments with
genuinely different availability, so not `series`.

**This is larger than adding a column, and we would rather say so now than have it discovered
during implementation.** To be both reachable from every Series and descriptive of the actual
observation source, the value must be populated per-assignment **at import time from each
adapter's own metadata** — Yahoo's `meta.firstTradeDate`, FRED's observation range, and so on.
That is an **adapter-interface change**: every adapter must either surface availability
metadata or explicitly declare that it cannot.

**Where an adapter cannot, that is a valid and permanent answer**, not a gap to be filled
later. A consumer that cannot establish availability should report `UNRESOLVED` rather than
guessing between the two explanations — which is the behaviour this marker exists to make
possible.

The existing `provider_symbol` columns are not wrong and need not be removed; they answer a
different question — discovery-side listing depth — and can be populated separately if that
ever matters.

*Design note:* availability metadata is itself provider-reported and can change, since a
provider may extend history backwards. Refreshing it on each import is preferable to storing
it once.

**Why it is needed.** There is currently no way to distinguish an instrument that genuinely
has little history from one whose fetch was truncated — and truncation is confirmed live: a
Series in this database received 19 of roughly 408 real observations from a single wide
date-range request marked `SUCCESS`. Any consumer assumption that *"`SUCCESS` means the
requested range is populated"* is false.

`backfill_start_date` cannot substitute. It was blanket-set to `2000-01-01` during bulk
import, so a requested-versus-received comparison measures the blanket setting rather than
provider behaviour — of 9,544 Series whose received start postdates the requested one, five
of the worst were checked live and all five matched the provider's own `firstTradeDate`
exactly. They simply did not exist in 2000.

With this stored, completeness becomes exact rather than inferential and splits into two
checks a consumer can run unaided: **start completeness** (`MIN(observed_at)` against the
recorded first-available date) and **density** (bar count against expected trading days
across the range, which catches interior gaps the first check cannot see).

---

## First item — adjustment basis

**Record, per provider, what `observation.value` means.** Confirmed as the one genuinely
missing piece.

**Why.** The same column holds different things depending on source. Yahoo Finance is
**split-adjusted, dividend-unadjusted** — the adapter reads `indicators.quote[0].close`,
deliberately not `adjclose`; verified against AAPL across both its splits. Alpha Vantage is
**unadjusted** — `TIME_SERIES_DAILY`, deliberately not the adjusted function. A Series
fallback-spliced across the two contains an unmarked scale change, and no consumer can
detect it or even know to look.

**Suggested placement, offered rather than prescribed.** Basis is fundamentally an adapter
property, so `provider` is the natural home. One complication worth weighing: a provider's
convention may vary by asset class — Yahoo's adjustment applies to equities, while for FX
pairs and index levels no adjustment concept exists at all. A nullable override on
`provider_assignment` would cover that without forcing a value everywhere.

Values should distinguish at least: raw/unadjusted · split-adjusted only · split- and
dividend-adjusted · not applicable.

**No outstanding dependency — the fact sheet is complete.** Established values:

| Provider | Price basis | Revision behaviour | Confidence |
|---|---|---|---|
| Yahoo Finance | split-adjusted, dividend-unadjusted | rebases to current split basis at query time | code + data confirmed |
| Alpha Vantage | raw / unadjusted (`TIME_SERIES_DAILY`) | unknown | code-confirmed, no data present |
| FRED | not applicable — value-only | revises retroactively; adapter passes no vintage parameters, so values freeze at first-fetch vintage | code-confirmed |
| BYMA | not applicable — supplies no observations | not applicable | code-confirmed (excluded from `PROVIDER_REGISTRY`) |
| ECB / World Bank | not applicable — value-only | assumed to revise; **not verified** | assumed |
| Stooq | **UNKNOWN** | **UNKNOWN** | attempted; blocked by client-side bot detection |

**Two consequences for the field's design.**

1. **`NOT APPLICABLE` and `UNKNOWN` must be distinct values.** They are different states:
   FRED and BYMA have no adjustment concept, while Stooq has one nobody has established.
   Collapsing them would erase exactly the distinction the field exists to record.
2. **A `UNKNOWN` basis should bar a provider from serving as fallback** until established.
   No Stooq data exists today, so this costs nothing now and prevents an unmarked scale
   splice later.

**One observation on placement, following from the table.** BYMA supplies no observations
at all — every BYMA-linked Series draws prices from a Yahoo `.BA` cross-listing. So
`provider` currently conflates two roles: sources of reference data and sources of
observations. That is not a problem this request needs to solve, but it is worth knowing
that a basis value will be meaningless for at least one registered provider by design.

**Additive.** No existing data semantics change; no stored values are rewritten.

---

## Summary

| # | Change | Table |
|---|---|---|
| 1 | adjustment-basis field, with optional per-assignment override | `provider` (+ `provider_assignment`) |
| 2 | provider-supplied availability marker (first/last available date), populated per-assignment at import time | `provider_assignment` + adapter interface |

Both additive at the schema level; neither alters existing data semantics nor rewrites stored
values. Item 2 additionally requires an adapter-interface change, which is why it is stated at
length above rather than summarised as a column.

---

## What stays excluded, deliberately

Dated conversion ratios, settlement modelling and corporate-action reconciliation are all
live issues on our side and are **not** here. They concern identity and relationship
modelling rather than observation trustworthiness, and the CEDEAR-ratio work in particular
has one unresolved item pending an authoritative regulatory lookup. Bundling it in would
tie this change's fate to a far less certain timeline.
