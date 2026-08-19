# HistFinTS Issue: Seven CEDEAR Series Still Driven by a Shared Process — F-032/F-033 Not Fully Resolved

**Date:** 2026-08-19
**Priority:** High
**Category:** Data Quality / Ingestion Mechanism
**Requestor:** Workbench Research Team (D-046 panel-eligibility calibration)
**Related:** `DEFECT-new-cedear-currency-basis.md` (2026-08-18, same seven series, prior symptom)

---

## Problem Statement

The seven CEDEAR series originally flagged in `DEFECT-new-cedear-currency-basis.md` — MU
(11323), MSFT (11324), AMD (11325), MELI (11326), QQQ (11328), AMZN (11329), NU (11327) —
had their currency/scale issue addressed between 2026-08-18 and 2026-08-19: their stored ARS
values are no longer bit-identical to each other (the symptom Workbench previously logged as
finding **F-033**). However, re-diagnosis on 2026-08-19 shows the underlying mechanism that
produced F-033 is **still active** — only its most visible symptom (exact numerical identity)
went away. **The seven series' day-over-day price movements remain perfectly correlated with
each other**, which is not possible for seven independently-traded instruments and indicates
all seven are still being generated from one shared process, just with a different (no longer
identical) per-series scale factor than before.

---

## Evidence

**Machine-precision test (2026-08-18, original F-033 finding):** implied FX
(`CEDEAR_ARS / underlying_USD`) for all seven series was identical to 6 decimal places on
every date checked — internal relative range 2.25×10⁻¹⁶, IEEE double-precision machine
epsilon.

**Same test, re-run 2026-08-19:** the six-decimal identity is gone — internal relative range
is now economically scaled (mean 13.3%, up to 743% on some dates). **This looked, at first
inspection, like independent data.** It is not:

**Return-correlation test (new, 2026-08-19):** computing day-over-day percent change in
implied FX for each of the seven series, over the 53 dates common to all seven
(2026-05-29 → 2026-08-18), and cross-correlating:

| | MU | MSFT | AMD | MELI | QQQ | AMZN | NU |
|---|---|---|---|---|---|---|---|
| **All seven pairs** | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 | +1.00 |

**Every pair among these seven correlates at exactly +1.00 with every other pair in this
group**, on every date pair checked. For comparison, six other CEDEAR series in the same
database, checked the same way over the same window (BABA, BIDU, UBER, GLD, AZN, BBD), show
correlations ranging from +0.04 to +0.91 — the pattern expected of genuinely independent
instruments moving together under a shared macro factor (ARS/USD movement) with idiosyncratic
noise on top. **The seven flagged series show none of that noise: their movement is
identical, not merely similar.**

This is diagnostic, not incidental: a correctly wrong-but-constant `ratio` field cannot
produce this, because dividing a genuine time series by any constant preserves its percent
changes exactly. Only two mechanisms produce +1.00 correlation across seven names: (a) all
seven are mathematically derived from one shared input series with a fixed per-series
multiplier, or (b) a data-pipeline bug is writing one series' movement into all seven under
different scale labels. Workbench cannot distinguish (a) from (b) from outside the ingestion
pipeline — that determination requires HistFinTS-side visibility into how these seven series'
observations are produced.

---

## Affected Series

| ID | Ticker | Live obs (2026-05-29+) | Deep-history obs | Deep-history source |
|----|--------|----|----|----|
| 11323 | MU | 56 | 2,867 | `provider_assignment` priority 3, provider "BYMA", identifier `BACKFILL_MU` |
| 11324 | MSFT | 56 | 2,867 | `BACKFILL_MSFT` |
| 11325 | AMD | 56 | 2,867 | `BACKFILL_AMD` |
| 11326 | MELI | 56 | 2,867 | `BACKFILL_MELI` |
| 11328 | QQQ | 56 | 2,867 | `BACKFILL_QQQ` |
| 11329 | AMZN | 56 | 2,867 | `BACKFILL_AMZN` |
| 11327 | NU | 56 | 1,120 | `BACKFILL_NU` |

**All seven series' deep history (everything before 2026-05-29) is sourced from a
`provider_assignment` whose `provider_series_identifier` is literally `"BACKFILL_{TICKER}"` —
not a market-data ticker symbol — under a `provider` entry labeled "BYMA." This does not read
as a live market-data fetch identifier; it reads as an internal batch/reprocessing job label.**
Workbench flags this pattern explicitly because it is the most likely locus of the shared-
driver mechanism, but has no visibility into what that job does — this is a request for
HistFinTS to characterize it, not an assertion that it is confirmed the cause.

The 56 live-fetch observations per series (2026-05-29 onward, `provider_id=2`, "Yahoo
Finance", identifier `"{TICKER}.BA"`) also show the +1.00 correlation, so this is not confined
to the backfilled portion — whatever produces it appears to still be active in current live
ingestion as of 2026-08-18/19, not only in historical backfill.

**Contrast — six unaffected CEDEAR series in the same database, same test, same window:**
BABA (11316), BIDU (11317), UBER (11319), GLD (11311), AZN (11354), BBD (11355) — all sourced
entirely from live `provider_id=2` fetches, no `BACKFILL_*` pathway involved, and all show
economically-plausible, non-unity correlation with each other.

---

## Root Cause Analysis

**Hypothesis (unconfirmed, Workbench cannot verify from outside the pipeline):** the seven
series were populated — both historically via `BACKFILL_*` and, apparently, in ongoing live
ingestion — by a process that derives each CEDEAR's ARS value from a single shared external
input (plausibly a shared USD/ARS reference-rate time series, as in the original F-032/F-033
finding) multiplied by a per-series constant, rather than by fetching or reconciling each
series against its own independent BYMA market print. The 2026-08-18→08-19 change (identical
values → identical returns at different levels) is consistent with the per-series constant
having been corrected or randomized without changing the shared-input dependency itself.

**Alternative hypothesis:** a caching or fan-out bug in the live `.BA` fetch pathway is
serving one series' price update to multiple `provider_assignment` records under different
per-series scale transforms.

---

## Addendum (2026-08-19): the transition event is directly visible in the data

Subsequent investigation found the old-scale → new-scale transition captured explicitly for
all seven series, at the same date, one calendar day apart in import time. For each of the
seven series, **2026-08-18 carries two observations from two different import runs on the
same `provider_assignment`, at two irreconcilable scales**:

- One observation at 13:30 UTC, from an import run created 2026-08-18 16:25–16:26 UTC
  (`trigger_type = MANUAL`), at the old (large) scale.
- Six further observations at 14:00–19:00 UTC, from a *different* import run created
  2026-08-19 13:04–13:05 UTC (`trigger_type = SCHEDULED`), at a new, smaller scale.

Both rows remain in the table; neither superseded the other. Per-pair magnitude of the jump is
**not uniform** — AMZN ~92×, MELI ~77×, QQQ ~13.7×, MSFT ~19.2×, AMD ~6.4×, MU ~3.2×, NU
~1.26× — which is more consistent with each series carrying its own per-series scale factor
(as this filing's shared-input hypothesis already proposed) than with a single uniform
currency/units correction. **Checked against six other CEDEAR series in the same database
(BABA, BIDU, UBER, GLD, AZN, BBD): none show this same-date dual-import-run pattern** — each
has exactly one value regime on 2026-08-18, confirming this is confined to the seven series
already flagged above.

This raises a second, related question for HistFinTS beyond the shared-driver mechanism
itself: **whether `MANUAL` and `SCHEDULED` import runs against the same `provider_assignment`
are expected to coexist for the same calendar date without reconciliation.** A downstream
consumer that does not explicitly select "most recent import run per date" would silently mix
an old-scale and new-scale observation for the same nominal date.

Full evidence: `SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md` (Workbench repository).

Workbench does not have enough visibility to distinguish these, or rule out a third
explanation. This section states hypotheses, not conclusions.

---

## Impact

1. **Panel-eligibility calibration remains blocked for these seven series** — a ratio
   correction (the fix that resolved several other CEDEARs' level discrepancies in the same
   diagnostic pass, see `RATIO_DIAGNOSIS_2026-08-19.md`) cannot fix a correlation-1.00 defect,
   since scale corrections cannot restore independence to data that never had it.
2. **Effective cross-sectional width for the PRIMARY CEDEAR cohort remains capped** — these
   seven pairs cannot contribute independent evidence to any panel-coherence statistic until
   this is resolved, regardless of any ratio or metadata work Workbench performs on its side.
3. **Confidence in the live `.BA` fetch pathway is affected beyond these seven** — if the
   mechanism is a pipeline-level bug (the alternative hypothesis above) rather than isolated to
   these seven series' specific configuration, other CEDEARs fetched through the same pathway
   may be at risk even if they have not shown the symptom yet.

---

## Requested Action

**Option A: Pipeline audit (preferred)**
- Trace what the `BACKFILL_{TICKER}` provider-assignment path actually does for these seven
  series — confirm or rule out that it derives values from a shared reference-rate series
  rather than fetching each series independently.
- Trace the live `provider_id=2` (`"{TICKER}.BA"`) ingestion path for these same seven series
  specifically — confirm whether it independently fetches each ticker from Yahoo Finance, or
  whether some shared intermediate step (caching, rate-lookup, fan-out) is involved.

**Option B: Comparative diagnostic**
- Provide HistFinTS-side logs or fetch records for two or three of the seven series on a
  single recent date, sufficient for Workbench to see whether the raw provider response
  differs per series (ruling in independent fetches) or is identical/derived (confirming the
  shared-driver hypothesis).

**Option C: Clarification**
- Confirm whether `BACKFILL_*`-identified provider assignments are documented anywhere as a
  known synthetic/reprocessing mechanism, and if so, what it is intended to represent.

---

## Testing Criteria (Resolution)

Issue resolved when:
1. Day-over-day return correlation among MU, MSFT, AMD, MELI, QQQ, AMZN, NU drops from +1.00
   to a range consistent with genuinely independent CEDEARs under a shared macro factor
   (comparable to the +0.04 to +0.91 range observed for BABA/BIDU/UBER/GLD/AZN/BBD).
2. The mechanism behind the `BACKFILL_*` provider assignments is documented, or discontinued
   in favor of independently-sourced observations.

---

## References

- **F-032 / F-033:** Workbench-side findings, `DEFECT-F032.md` (currency/scale, resolved),
  `DEFECT-F033.md` (2026-08-18, original machine-precision circularity finding)
- **`FULL_REVERIFICATION_2026-08-19.md`:** re-test showing F-033's exact symptom resolved
- **`RATIO_DIAGNOSIS_2026-08-19.md`:** diagnostic separating this finding (Finding A) from a
  distinct, independently-fixable ratio-metadata issue affecting other CEDEAR series
  (Finding B)

---

## Status

**Reported:** 2026-08-19
**Expected response:** [Awaiting HistFinTS team]
**Blocker:** Yes — these seven series cannot be admitted to PRIMARY calibration until resolved;
no Workbench-side remediation (ratio correction or otherwise) is available for this defect.
