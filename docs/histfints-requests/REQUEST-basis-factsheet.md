# REQUEST — Provider adjustment-basis and revision-behaviour fact sheet

**Type:** Investigation. No code or schema change requested at this stage.
**Filed:** 2026-08-15 · **Requested by:** Research Workbench
**Related:** DEFECT-F009 (filed separately — please prioritise independently)

---

## What is being asked

A short, documented statement — one row per provider — of **what `observation.value`
actually means** for data that provider supplies, and **how that provider revises
history**.

This is investigation work, not implementation. It is being requested now because the
answers are a prerequisite for a later schema change and can be produced in parallel
with other work.

---

## Why it is needed

`observation` stores one number per `(series_id, observed_at)`. That number means
different things depending on which provider supplied it, and `provider_assignment`
permits a Series to be served by several providers over time. A Series
fallback-spliced across providers with different conventions therefore contains an
unmarked scale change, and nothing downstream can detect or correct it without knowing
the conventions involved.

---

## Requested format

| Provider | Price basis | Historical revision behaviour | Confidence |
|---|---|---|---|
| Yahoo Finance | | | |
| Alpha Vantage | | | |
| Stooq | | | |
| BYMA | | | |
| FRED | | | |
| ECB | | | |
| *(others configured)* | | | |

**Price basis** — one of: raw/unadjusted · split-adjusted only · split- and
dividend-adjusted · not applicable (value-only series).

**Historical revision behaviour** — does the provider restate values for past dates
after first publication, and over what horizon? For price providers this is mostly
split rescaling. For statistical providers (FRED, ECB) it is routine data revision,
which matters just as much and is easy to overlook.

**Confidence** — code-confirmed · empirically confirmed · documented by provider ·
assumed.

---

## Already established (please verify rather than re-derive)

**Yahoo Finance — split-adjusted, dividend-unadjusted. Code- and data-confirmed.**
`providers/yahoo_finance.py` reads `indicators.quote[0].close`, deliberately not
`indicators.adjclose`. Confirmed against series 33 (AAPL): stored `23.06` for
2014-06-06 against a published raw close of ≈`645.57`; `23.06 × 7 × 4 = 645.68`,
reconciling only after backing out both the 2014 7:1 and 2020 4:1 splits. The same
arithmetic rules out dividend adjustment — a dividend-adjusted series would sit
10–15% lower, near `20`.

**Alpha Vantage — unadjusted. Code-confirmed, not empirically checked.**
`providers/alpha_vantage.py` calls `TIME_SERIES_DAILY`, deliberately not
`TIME_SERIES_DAILY_ADJUSTED`. No Alpha Vantage data currently exists in the database,
so this could not be verified against stored values.

**This is already a live mismatch.** Yahoo and Alpha Vantage are configured against
the same schema with opposite conventions.

---

## One item worth checking first

**FRED revises history routinely** — payroll employment revises the prior two months,
seasonally adjusted household-survey data is revised at the January benchmark, and GDP
has scheduled second and third estimates. Because incremental import re-fetches only a
short trailing window, revisions older than that window are never seen, and stored
series freeze at the vintage current at first backfill.

Note that comparing a stored value against FRED's current publication **cannot settle
this** while every assignment in the database is days old — a match is guaranteed
either way. The test that does settle it is constructive, and it is the same test the
split case needs; see DEFECT-F009 §3.

The reason it belongs in this fact sheet: revision behaviour is a per-provider
property exactly as adjustment basis is, and both are needed before a downstream
consumer can reason about what a stored value means.

---

## What is *not* being requested here

Stated explicitly to avoid scope drift:

- **Not** a request to implement adjustment logic. Re-expressing series onto a common
  basis belongs downstream, where cross-provider and cross-asset-class reconciliation
  happens; Yahoo's event feed cannot cover BYMA or CEDEAR ratio changes.
- **Not** a schema change — yet. A basis column is expected to follow, batched with
  other schema work into a single migration.
- **Not** a request for bitemporality or vintage storage.
- **Not** DEFECT-F009. That is a separate filing and should be prioritised on its own
  merits.
