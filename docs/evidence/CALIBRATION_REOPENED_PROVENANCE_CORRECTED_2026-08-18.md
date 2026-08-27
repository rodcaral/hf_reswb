# Reopened Calibration — Provenance-Corrected, All Seven Pairs Retained

**Date:** 2026-08-18
**Requested by:** SE, four sequential SDT directives
**Nature of this document:** Evidence/diagnostic report. **No threshold is selected, changed,
or promoted.** All seven pairs are retained in every table below; none are excluded on the
basis of the prior machine-precision finding.

---

## Part 1: The corrected provenance conclusion — verified, and it is real

Per directive 1, this reopens the analysis and does not summarily re-exclude any pair.
Before recomputing, the provenance question was checked directly against `provider_assignment`
/ `import_run`, because the prior F-033 finding assumed (without checking) that the six
near-identical pairs' recent data came from the same synthetic process as the historical
backfill. **That assumption was wrong, and this is a genuine, evidenced correction:**

Every one of the 392 post-2026-05-29 CEDEAR observations, for **all seven pairs including
QQQ**, was produced by the same live pathway: `provider_id = 2` ("Yahoo Finance"),
`provider_series_identifier = "{TICKER}.BA"`, `adjustment_basis = SPLIT_ADJUSTED`. None of
them came from the `BACKFILL_*`-identified provider assignment (provider_id 3, "BYMA",
used for the separate deep-history rows). This is a distinct provider assignment from, and
not reachable through, the F-032 Phase 2 conversion job.

**This corrects Part 1 of `DEFECT-F033.md` and `CALIBRATION_EVIDENCE_REOPENED_DISPERSION_
2026-08-18.md`, which characterized the recent window's circularity as consistent with
backfill-style construction.** It is not — the post-May-29 window's data for all seven pairs
was independently *fetched*, via the same live Yahoo Finance `.BA` mechanism, on equal
footing. There is no provenance distinction between QQQ and the other six at the
fetch-mechanism level. This is worth stating plainly: the directive's premise that a
provenance correction was needed here was right, and Workbench's prior framing was
incomplete.

**What this does not change:** the machine-precision equality among six of the seven pairs'
implied-FX values (re-verified below, unchanged) is a fact about the *numbers Yahoo Finance
returned*, not about how HistFinTS/Workbench ingested them. The correction relocates where the
non-independence originates — from a hypothesized Workbench-side backfill artifact to a
provider-side property of Yahoo's `.BA` data for these six tickers — it does not make the six
values independent of each other. Both statements are held at once below.

---

## Part 2: What quantity does the Yahoo `.BA` observation represent?

**Available evidence:**
- `adjustment_basis = SPLIT_ADJUSTED` on both the CEDEAR and underlying provider assignments,
  for all seven pairs — same basis on both sides, ruling out an adjustment-basis mismatch as
  the explanation for the six-pair identity.
- `series.ratio = 1.0`, documented, applied correctly (Part A of the prior report; unchanged).
- No field in `provider_assignment`, `import_run`, or elsewhere records *how* Yahoo computed
  the `.BA` value it returned — there is no "quote type" (trade print vs. computed
  cross-rate), no raw payload archive to inspect (this is the same gap as **F-027**: Yahoo's
  raw response is not archived, so provider-side context that would answer this directly does
  not exist in the database).

**What can be established from the evidence that does exist:** the six-pair group's implied-FX
values are equal to IEEE 754 double-precision machine epsilon (2.25×10⁻¹⁶ relative range,
re-confirmed in Part 3). No real trade-print series — subject to discrete tick sizes, bid/ask
spread, and independent timing across six different securities — can reproduce that level of
agreement by coincidence or by market efficiency. A tight arbitrage band (which is a real,
expected phenomenon for CEDEAR/underlying-linked pricing) manifests at the basis-point-to-
percent scale, not the floating-point-rounding scale. **This is dispositive that the value
Yahoo returns under `.BA` for these six tickers is a computed quantity — most consistent with
`underlying_USD_price × a shared reference FX rate`, produced on Yahoo's side — rather than an
independently formed BYMA trade observation,** even though the fetch itself was live and
genuine.

**What cannot be established from available evidence, per the explicit fallback in directive
2:** the exact formula, reference-rate source, or update cadence Yahoo uses internally to
produce this number. **This limitation is reported as a limitation, not filled in with an
assumed normalization.** No formula is assumed beyond what the arithmetic itself already
proves (that a single shared multiplier reproduces all six values).

**QQQ is not explained by any evidence above.** It went through the identical fetch mechanism
and cannot be distinguished from the other six by provenance metadata. Its economically
plausible, non-degenerate deviation pattern (0.83%–10.24% from the six-pair group) is
consistent with either a genuine BYMA-sourced trade print or a different Yahoo-side
computation specific to ETFs — the evidence available does not decide between these, and this
report does not assume one.

---

## Part 3: Recomputed implied-FX residual and dispersion diagnostics — all seven pairs retained

Formula unchanged: `implied_fx(pair, date) = CEDEAR_price_ARS(date) / (underlying_price_USD(date) × ratio)`,
`ratio = 1.0` for all seven, contemporaneous observations only (same date on both sides).

**Coverage:** 54 of 56 dates per pair have a contemporaneous underlying match (378 of 392
observations). **Sensitivity to the 14 missing observations:** these are exactly the 2
most recent dates (2026-08-17, 2026-08-18) for **every one of the seven pairs, uniformly** —
the underlying-series fetch has not yet caught up to `2026-08-14` for any of the seven names,
while the CEDEAR fetch has. This is a shared recency lag in the underlying-series ingestion,
not a pair-specific or provenance-related gap. Excluding these 2 dates removes ~3.6% of the
window and does not materially change any distribution below (verified: including a
partial-panel estimate for those 2 dates using the last available underlying price shows the
same six-pair identity and the same QQQ deviation magnitude).

| Statistic | Min | Median | P90 | P95 | Max |
|---|---|---|---|---|---|
| MAD (median absolute relative residual, per date) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Relative stdev of implied_fx across 7 pairs (per-date CV) | 0.0031 | 0.0174 | 0.0302 | 0.0321 | 0.0387 |

**Pair-level residual distribution, all seven retained, none excluded:**

| Pair | n | Mean residual | Median residual | Stdev | Min | Max |
|---|---|---|---|---|---|---|
| MU | 54 | +0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| MSFT | 54 | +0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| AMD | 54 | −0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| MELI | 54 | +0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| AMZN | 54 | −0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| NU | 54 | −0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| **QQQ** | 54 | **+0.04854** | **+0.04592** | **0.02433** | **+0.00826** | **+0.10235** |

These figures are numerically identical to the prior report's — the computation was not
altered, only re-verified with the corrected provenance context and with an explicit
sensitivity check on the 14-observation gap. Nothing was recomputed differently because
nothing about the underlying math changes when the fetch mechanism is understood correctly;
what changes is the explanation for *why* six pairs behave this way.

---

## Part 4: Sufficiency reassessment — two separate questions, neither answered with an invented number

**Question A: Does the seven-pair cross-section now provide meaningful dispersion evidence?**

No, and the reason is now more precisely stated than before. It is not that the data is
"backfill-contaminated" — Part 1 establishes it is not. It is that **the quantity six of the
seven series report is, on the evidence in Part 2, not an independent market observation of
CEDEAR pricing** — most consistent with a provider-side computed cross-rate. A cross-sectional
dispersion statistic needs multiple members whose values could differ from each other for
economic reasons; six of seven cannot, by the same arithmetic evidence that answered Part 2.
This conclusion holds *given the two pairs retained and computed in full* (Part 3) — it is not
a decision to exclude data, it is what the retained, fully-computed data shows.

**Question B: Is the 2.5-month single-regime window sufficient to calibrate a production
parameter, independent of Question A?**

No, and this is a separate limitation that would hold even if all seven pairs were
independent. 54–56 observations inside one calendar/liquidity/FX regime, with no internal
structural boundary (F-009 era split, F-021 ratio-step date, or crisis/regime-year
boundaries all fall outside this window), cannot support a parameter intended to generalize
across regimes — there is exactly one regime's worth of behavior to observe. This limitation
is orthogonal to Question A: fixing the six-pair provenance issue would not, by itself, add
temporal variation.

**No minimum panel depth, sample size, or threshold is proposed by this reassessment.** Both
answers are stated as observed limitations of the current evidence, consistent with the
open items already logged in `CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md`, which this
report does not revise.
