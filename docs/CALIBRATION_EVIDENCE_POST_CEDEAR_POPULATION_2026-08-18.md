# Post-CEDEAR Population Calibration Evidence (392 obs, 2026-05-29 → 2026-08-18)

**Date:** 2026-08-18
**Requested by:** SE, five sequential SDT directives
**Nature of this document:** Evidence/diagnostic report. **No threshold is selected, promoted,
or hard-coded.** `staleness_policy` remains provisional/uncalibrated. `dispersion_threshold`
retained at CV 0.167 as an existing provisional parameter only — not reinterpreted or
re-validated by anything in this document.

---

## Part 1: Population scope

Restricted to the seven new CEDEAR series' observations dated `>= 2026-05-29`. 56
observations per pair × 7 pairs = **392 observations**, matching the figure reported by SE.
The F-032-derived pre-2026-05-29 observations are excluded from every statistic below; they
remain in the database and provenance chain untouched.

| Pair | Obs | Range |
|---|---|---|
| MU, MSFT, AMD, MELI, QQQ, AMZN, NU | 56 each | 2026-05-29 to 2026-08-18 |

---

## Part 2: Multiplier and contemporaneity prerequisite check

**Transformation applied:** `implied_fx(pair, date) = CEDEAR_price_ARS(date) / (underlying_price_USD(date) × ratio)`

**Multiplier source:** `series.ratio` — the authoritative, documented metadata field. **No
ratio was inferred or substituted from price scale.** All seven pairs carry `ratio = 1.0`
(US common-stock/ETF CEDEARs are 1:1 by CNV registration; this is the documented value, not
an assumption).

**Contemporaneity:** each CEDEAR observation was matched to an underlying-series observation
on the same calendar date. Result, uniform across all seven pairs:

| Prerequisite | Observations surviving |
|---|---|
| Post-CEDEAR population (Part 1) | 392 |
| → with documented multiplier applied (all pairs, ratio=1.0) | 392 (no exclusions — ratio is defined for all seven) |
| → with contemporaneous underlying observation | **378** (54 per pair) |

**14 observations (2 per pair) fail the contemporaneity prerequisite** — `2026-08-17` and
`2026-08-18` have a CEDEAR print but no matching same-date observation in the underlying USD
series for any of the seven pairs (the underlying feed appears to lag the CEDEAR feed by the
same two trading sessions across all seven, consistent with an underlying-side ingestion lag
rather than a pair-specific issue). These 14 observations are excluded from the dispersion
calculation (Part 4) for lack of a contemporaneous denominator; they remain included in the
staleness calculation (Part 3), which does not require the underlying series.

---

## Part 3: Staleness — gap diagnostics, valid population

Computed on all 392 CEDEAR observations (staleness is a property of the CEDEAR print cadence
itself and does not require the underlying-series match).

| Pair | Obs | Gaps | Min | Max | Mean | Median | P90 | P95 |
|---|---|---|---|---|---|---|---|---|
| MU / MSFT / AMD / MELI / QQQ / AMZN / NU | 56 each | 55 each | 1d | 4d | 1.47d | 1d | 3d | 3d |

**Aggregate (7 pairs, 385 gaps):** min 1d, max 4d, mean 1.47d, median 1d, P90 3d, **P95 3d**,
P99 4d.

**Pair-level regime:** all seven pairs are identical to the gap-day resolution — same min,
max, mean, and percentiles. There is no pair with materially different staleness behavior in
this window.

**Upper tail:** the largest gaps (4d) occur at the same two calendar boundaries across all
seven pairs simultaneously (`...ending 2026-06-22` and `...ending 2026-07-06`) — a shared
calendar effect (long weekend / holiday), not a pair-specific staleness event.

**Gap-to-subsequent-residual relationship:** not computable as a meaningful relationship in
this window. The dispersion statistic (Part 4) is degenerate for six of seven pairs (see
below), so "residual behavior following a gap" cannot be distinguished from the residual
behavior on any other date for those six pairs. For QQQ, the one pair with a non-degenerate
residual, the 54 available dates carry no staleness gap directly adjacent to a residual
spike large enough to suggest a relationship, but 54 points in one regime is too few to
assert or rule this out.

**Temporal segmentation:** the window spans 2026-05-29 to 2026-08-18 — about 2.5 months,
entirely inside a single calendar/regime period. None of the structural boundaries used
elsewhere in this project (F-009 era split at 2024, F-021 ratio-step date, crisis-year
regime breaks) fall inside this window, so no further temporal segmentation is meaningful;
aggregate and pair-level are the only informative cuts available.

**No staleness threshold selected.**

---

## Part 4: Dispersion — multiplier-normalized implied-FX, valid population

**Formula:** `implied_fx(pair, date) = CEDEAR_price_ARS(date) / (underlying_price_USD(date) × ratio)`
(ratio = 1.0 for all seven pairs, per Part 2). **Panel center:** `median(implied_fx)` across
pairs present that date. **Dispersion unit:** relative residual, `(implied_fx − median) / median`.

**Inputs:** 378 observations (Part 2), 54 dates with 2+ pairs present.

| Statistic | Value |
|---|---|
| Dates with 2+ pairs | 54 |
| Aggregate MAD (median of per-date median-absolute-residual) | **0.0000** |
| Aggregate P90 / P95 / Max | 0.0000 / 0.0000 / 0.0000 |

**This is not a coherent panel.** Pair-level residual behavior:

| Pair | n | Mean residual | Median residual | Stdev |
|---|---|---|---|---|
| MU | 54 | +0.0000 | +0.0000 | 0.0000 |
| MSFT | 54 | +0.0000 | +0.0000 | 0.0000 |
| AMD | 54 | −0.0000 | +0.0000 | 0.0000 |
| MELI | 54 | +0.0000 | +0.0000 | 0.0000 |
| AMZN | 54 | −0.0000 | +0.0000 | 0.0000 |
| NU | 54 | −0.0000 | +0.0000 | 0.0000 |
| **QQQ** | 54 | **+0.0485** | **+0.0459** | **0.0243** |

**F-033 persists inside the post-CEDEAR window.** Restricting to 2026-05-29+ does not resolve
the circularity documented in `DEFECT-F033.md`: six of the seven pairs (MU, MSFT, AMD, MELI,
AMZN, NU) still produce a bit-identical implied-FX value on every date in this window, to four
decimal places — verified directly, not inferred from the MAD figure. This means **the
circularity is not confined to the pre-2026-05-29 backfilled history** (which was this
directive's working assumption); it is present in the current live/production data for these
six series as well. Only QQQ shows the independent-pricing signature within this window too.
Because the aggregate MAD is a median across seven pair-residuals where six are exactly zero,
the reported 0.0000 is an artifact of that degeneracy, not evidence of panel coherence — it is
reported here as observed, not smoothed over or excluded.

**CV = 0.167 status:** retained exactly as an existing provisional parameter, unchanged. This
report does not apply it as a suppression rule, does not validate it, and does not treat the
above result as either confirming or refuting it — there is no coherent dispersion
distribution here to compare it against.

---

## Part 5: Sufficiency assessment

**392 observations do not provide sufficient independent cross-sectional and temporal
variation for a meaningful calibration study.** Precise insufficiency:

**Cross-sectional insufficiency.** Of the seven nominal panel members, six (MU, MSFT, AMD,
MELI, AMZN, NU) are not independent observations — they carry the exact same implied-FX value
by construction (F-033), collapsing to a single effective data point. The panel's *effective*
cross-sectional width in this window is **2** (the collapsed six-pair value, and QQQ), not 7.
A dispersion statistic computed on 2 effective points cannot characterize a "panel," by
definition — there is no meaningful concept of central tendency or outlier detection at n=2.

**Temporal insufficiency.** 54–56 observations span a single ~2.5-month window, entirely
within one calendar/liquidity/FX regime. This project's own standing evidence-quality
convention (structural period classification: F-009 era, F-021 ratio-step era, crisis/regime
years) has no internal boundary inside this window — there is exactly one segment. A
calibration study intended to characterize behavior across regimes has zero regime variation
to draw on here.

**What would resolve this, distinct from what is reported here as fact:**
- Cross-sectional: F-033 must be resolved (six pairs' data source corrected to independent
  BYMA CEDEAR observations) before the panel has more than 2 effective members.
- Temporal: the window must extend to cover more than one regime, which requires either the
  original-5 cohort's absent deep history to be restored (per the 2026-08-18 anomaly finding)
  or the new-7 cohort's independent observation to accumulate over a longer live period.

**Distinction preserved, per directive:**
- **Observed evidence:** 392 CEDEAR observations exist in this window; 378 have a
  contemporaneous underlying match; staleness gaps are uniformly P95=3d/max=4d across all
  seven pairs; six of seven pairs' implied-FX values are bit-identical on every date.
- **Derived diagnostic:** the aggregate dispersion statistic (MAD=0.0000) is an artifact of
  the six-pair degeneracy, not a measurement of panel coherence.
- **Methodological conclusion:** this population is insufficient for calibration, for the two
  precise reasons stated above — not a general judgment that the metric or the data source is
  unusable once the stated defects are corrected.

No numerical threshold is selected, changed, or implied by any of the above.
