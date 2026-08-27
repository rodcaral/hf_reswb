# F-033: New-7 CEDEAR cohort is not independent evidence for implied-FX panel coherence

**Date:** 2026-08-18
**Severity:** High — invalidates the empirical basis for the FDA-directed implied-FX
panel-coherence calibration on the current database state.
**Status:** Finding, blocking. No calibration distribution has been reported on top of it.

---

## Context

Following the FDA ruling redefining the panel-coherence metric around cross-sectional
implied-FX residuals (`implied_fx = CEDEAR_price_ARS / underlying_price_USD`, robust center
= median, dispersion = relative residual to that center), SDT began computing the empirical
distribution on the verified new-7 CEDEAR cohort per the SE directive.

**Before reporting any distribution, the object was verified by construction (per the
standing project discipline: a clean empirical result is not evidence of anything without
checking how it was produced — D-009/D-009b).**

## What was found

`series.underlying_series_id` on the seven new CEDEAR series does **not** point to real
market-quoted USD prices. It points to a series that is a bit-identical copy of the CEDEAR's
own (already-ARS-converted) values, mislabeled `currency = USD`:

| Ticker | CEDEAR id | `underlying_series_id` target | Target's actual content |
|---|---|---|---|
| MSFT | 11324 | 11348 | Identical to CEDEAR 11324, to full float precision, every sampled date |
| MU | 11323 | 11342 | Identical to CEDEAR 11323 |
| NU | 11327 | 11351 | Identical to CEDEAR 11327 |
| (AMD, MELI, QQQ, AMZN follow the same pattern — not individually re-verified but same FK provenance) | | | |

The **real** USD-priced series for these names exist under different, unrelated series ids,
located by label search and sanity-checked against known price ranges (e.g. MSFT $15–542
across 2015–2026 is a real trading range; the FK target's $348–544,299 "range" is the ARS
CEDEAR range mislabeled): MU→6672, MSFT→6602, AMD→426, MELI→6319, QQQ→8193, AMZN→484, NU→7085.

Using the **real** underlying series, a second and more serious problem appeared. Sampling
`implied_fx = CEDEAR_ARS / underlying_USD` for six of the seven pairs (MU, MSFT, AMD, MELI,
AMZN, NU) on three widely separated dates:

| Date | MU | MSFT | AMD | MELI | AMZN | NU | QQQ |
|---|---|---|---|---|---|---|---|
| 2020-06-15 | 70.987705 | 70.987705 | 70.987705 | 70.987705 | 70.987705 | — | **91.295388** |
| 2023-03-01 | 216.710526 | 216.710526 | 216.710526 | 216.710526 | 216.710526 | 216.710526 | **293.764792** |
| 2026-08-14 | 1010.403930 | 1010.403930 | 1010.403930 | 1010.403930 | 1010.403930 | 1010.403930 | **1072.971133** |

**Six of the seven pairs produce a bit-identical implied-FX value on every date, to six
decimal places.** This is not empirical convergence — it is what results when a CEDEAR's ARS
value is manufactured as `underlying_USD_price × single_shared_daily_rate(date)` (the F-032
Phase 2 BCRA-rate conversion), rather than being an independently observed market price. The
"implied FX" recovered from these six pairs is not a measurement of anything; it is the
conversion table used to construct the data, read back out. Cross-sectional dispersion
computed across these six pairs is measuring the internal self-consistency of one conversion
job, not market disagreement among independently-priced instruments.

**QQQ is the only one of the seven that diverges** — consistently 6–28% above the other six's
common value, on every sampled date. This is equally uninformative on its own: it does not
demonstrate genuine panel coherence being violated by one outlier pair, because the other six
were never independent observations to begin with. QQQ's divergence could reflect a real,
independently-sourced CEDEAR value, or a different conversion defect specific to that series —
this has not been determined.

## Why this blocks the calibration

The FDA ruling's redefined metric assumes each pair's implied FX is an *independent*
cross-check on a shared, unobserved FX rate — that is the entire premise of using
cross-sectional disagreement as a coherence signal. Six of the seven new pairs do not meet
that premise on the current database: their ARS values were derived arithmetically from the
same underlying-price × rate-table construction, not fetched or reconciled independently.
Any dispersion statistic computed on this cohort right now would show near-perfect
"coherence" for those six by construction, contaminated by whatever QQQ's difference actually
is — and would misrepresent manufactured self-consistency as validated market behavior.

**No calibration distribution is reported from this run.** Reporting one would repeat the
exact failure mode this project's discipline exists to prevent (D-009b): a clean, low-dispersion
result that looks like evidence but isn't, because it was never checked against how the
underlying data was produced.

## What is needed before the implied-FX calibration can proceed

1. Confirm with HistFinTS/F-032's implementers whether the six converged pairs' CEDEAR ARS
   values were derived by formula (`underlying × BCRA rate`) rather than fetched from BYMA
   market data. If so, they are not currently usable as an independent panel-coherence input
   regardless of which underlying series is referenced.
2. Correct the `underlying_series_id` FK on all seven new CEDEAR series — it currently points
   to a corrupted, mislabeled duplicate of the CEDEAR itself, not a market-quoted USD series.
3. Determine QQQ's provenance specifically — it is the only one of the seven not showing the
   circularity signature, and understanding why is necessary before treating it as either a
   valid data point or a defect instance.
4. Once (1)–(3) are resolved, rerun the implied-FX residual calibration exactly as specified
   by the FDA ruling: robust panel center (median), relative residuals, empirical distribution,
   no numerical threshold selection.

## Cross-references

Extends **F-032** (currency/scale incompatibility, resolved 2026-08-18 for the currency-field
and completeness dimensions) with a new, distinct finding about the *provenance* of the
converted values. Does not reopen F-032's Phase 1/2 completeness conclusions, which remain
correct — completeness and provenance are orthogonal properties, and this defect requires
both to be true (complete AND independently sourced) to support the FDA's redefined metric.
