# Line-by-Line Comparison Package for F-033 Correlation Dispute

**Date:** 2026-08-19
**To:** HistFinTS SDT
**From:** Workbench SDT, per SE instruction
**Purpose:** enable a direct, row-by-row comparison against HistFinTS's own rerun, rather than
further prose description. **The reproducibility result from `RESPONSE-F033-reproducibility-
package-2026-08-19.md` is preserved unchanged.** This document adds exact query text and full
intermediate data; it draws no new conclusions, does not alter the calculation, and does not
convert either disputed finding into an admissibility or calibration decision. Both parties'
next step is to compare inputs directly and locate where the two extractions diverge.

---

## 1. Exact SQL (SQLite), directly runnable, equivalent to the Python logic already provided

```sql
WITH pair_map(ticker, cedear_id, underlying_id) AS (
  VALUES ('MU',11323,6672), ('MSFT',11324,6602), ('AMD',11325,426),
         ('MELI',11326,6319), ('AMZN',11329,484), ('NU',11327,7085)
),
cedear_daily AS (
  SELECT o.series_id, DATE(o.observed_at) AS d, o.value, o.observed_at,
         ROW_NUMBER() OVER (PARTITION BY o.series_id, DATE(o.observed_at)
                             ORDER BY o.observed_at ASC) AS rn_asc,
         COUNT(*) OVER (PARTITION BY o.series_id, DATE(o.observed_at)) AS n
  FROM observation o
  JOIN pair_map pm ON o.series_id = pm.cedear_id
),
cedear_last AS (
  -- "last observation of the day, day-deduped, ties broken by ascending observed_at"
  SELECT series_id AS cedear_id, d, value AS cedear_value, observed_at AS cedear_ts
  FROM cedear_daily WHERE rn_asc = n
),
underlying_daily AS (
  SELECT o.series_id, DATE(o.observed_at) AS d, o.value, o.observed_at,
         ROW_NUMBER() OVER (PARTITION BY o.series_id, DATE(o.observed_at)
                             ORDER BY o.observed_at ASC) AS rn_asc,
         COUNT(*) OVER (PARTITION BY o.series_id, DATE(o.observed_at)) AS n
  FROM observation o
  JOIN pair_map pm ON o.series_id = pm.underlying_id
),
underlying_last AS (
  SELECT series_id AS underlying_id, d, value AS underlying_value, observed_at AS underlying_ts
  FROM underlying_daily WHERE rn_asc = n
)
SELECT pm.ticker, cl.d AS date,
       cl.cedear_value, ul.underlying_value,
       cl.cedear_value / ul.underlying_value AS implied_fx,
       cl.cedear_ts, ul.underlying_ts
FROM pair_map pm
JOIN cedear_last cl ON cl.cedear_id = pm.cedear_id
JOIN underlying_last ul ON ul.underlying_id = pm.underlying_id AND ul.d = cl.d
WHERE cl.d >= '2026-05-29'
ORDER BY pm.ticker, cl.d;
```

**Date-only join:** `DATE(observed_at)`, as shown — not exact timestamp.
**Timestamp handling:** within each `(series_id, date)` group, the row with the latest
`observed_at` wins (`rn_asc = n`, i.e. last in ascending order). No averaging, no OHLC field
used — `value` (close) only.
**Date exclusion variant:** identical query with `AND cl.d >= '2026-05-29' AND cl.d !=
'2026-08-18'` appended, to reproduce the "excluding 2026-08-18" scenario from the prior
response.
**Underlying series IDs:** `pair_map` above — the *real* underlying series (identified in the
original F-033 work via label search + price-plausibility check), explicitly **not**
`series.underlying_series_id`. That FK, for direct side-by-side reference:

| Ticker | CEDEAR id | Real underlying used (this package) | `series.underlying_series_id` (FK) |
|---|---|---|---|
| MU | 11323 | 6672 | 11342 |
| MSFT | 11324 | 6602 | 11348 |
| AMD | 11325 | 426 | 11349 |
| MELI | 11326 | 6319 | 11350 |
| AMZN | 11329 | 484 | 11353 |
| NU | 11327 | 7085 | 11351 |
| QQQ (tracked separately, not in the six-pair correlation set) | 11328 | 8193 | 11352 |

---

## 2. Full intermediate data — every row behind the correlation figure

**Attached: `docs/reproducibility/implied_fx_full_dump_2026-08-19.csv`** — all 56 common
dates (2026-05-29 → 2026-08-18), for each of the six pairs: CEDEAR value, underlying value,
computed `implied_fx`, and the exact `observed_at` timestamp selected by the day-dedup for
both the CEDEAR and underlying leg. This is the literal input to the correlation calculation
in `RESPONSE-F033-reproducibility-package-2026-08-19.md` §2 — nothing is summarized or
aggregated beyond what's in this file.

---

## 3. One additional raw fact, surfaced while assembling this package, presented without interpretation

Checking whether the CEDEAR-side and underlying-side day-dedup select the same `observed_at`
timestamp on every date (they should, if both legs update on the same schedule): **they do,
on all 56 dates, except 2026-08-18, where all six pairs' CEDEAR-side dedup selects a
19:00–20:00 UTC timestamp while the underlying-side dedup selects 13:30 UTC.**

| Date | Pair | CEDEAR `observed_at` selected | Underlying `observed_at` selected |
|---|---|---|---|
| 2026-08-18 | MU | 19:00:00 | 13:30:00 |
| 2026-08-18 | MSFT | 20:00:00 | 13:30:00 |
| 2026-08-18 | AMD | 19:00:00 | 13:30:00 |
| 2026-08-18 | MELI | 19:00:00 | 13:30:00 |
| 2026-08-18 | AMZN | 19:00:00 | 13:30:00 |
| 2026-08-18 | NU | 19:00:00 | 13:30:00 |

This is reported as an observed property of the input data on this one date, for both parties
to account for in their own extractions — **not** offered as an explanation for either
disputed finding, and not acted on by altering the calculation in this package.

---

## 4. Status

Per SE instruction: reproducibility result unchanged from `RESPONSE-F033-reproducibility-
package-2026-08-19.md`; no calculation altered to force agreement; no admissibility or
calibration conclusion drawn from anything in this document. Workbench is now waiting on
HistFinTS's rerun against this exact query/data package to identify the point of divergence.
