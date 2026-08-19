# Reopened Dispersion Analysis — Post-May-29 CEDEAR Population, All Seven Pairs Retained

**Date:** 2026-08-18
**Requested by:** SE, three sequential SDT directives, reopening the prior dispersion finding
**Nature of this document:** Evidence/diagnostic report. **No threshold is selected, promoted,
or modified.** All seven pairs are retained in every calculation below — none are discarded
on the basis of convergence.

---

## Part A: Calculation chain, per pair (sample date 2026-07-09)

`CEDEAR_price_ARS → (÷ documented ratio) → normalized_ARS → (÷ underlying_price_USD) → implied_fx`

| Pair | CEDEAR ARS | Ratio | Normalized ARS | Underlying USD | Implied FX |
|---|---|---|---|---|---|
| MU | 1,001,099.5675 | 1.0 | 1,001,099.5675 | 991.6400 | 1009.5393013100437 |
| MSFT | 388,026.5111 | 1.0 | 388,026.5111 | 384.3600 | 1009.5393013100437 |
| AMD | 551,935.2972 | 1.0 | 551,935.2972 | 546.7200 | 1009.5393013100437 |
| MELI | 1,825,075.3907 | 1.0 | 1,825,075.3907 | 1,807.8300 | 1009.5393013100436 |
| AMZN | 249,396.5822 | 1.0 | 249,396.5822 | 247.0400 | 1009.5393013100437 |
| NU | 13,800.4023 | 1.0 | 13,800.4023 | 13.6700 | 1009.5393013100437 |
| **QQQ** | 758,880.8104 | 1.0 | 758,880.8104 | 723.2800 | **1049.2212969128523** |

The multiplier step is a no-op for all seven (documented `ratio = 1.0`, not inferred — same
value used throughout this and prior reports). Units are consistent on both sides: ARS
numerator, USD denominator, dimensionless implied-FX result in ARS/USD, identically defined
for all seven pairs. **There is no unit or definitional incompatibility in the calculation
chain.** This directly answers the diagnostic question in directive 2, below.

---

## Part B: Is the six-pair convergence economically expected, or something else?

This is the determination directive 2 asked for, made with a precision test rather than
judgment call.

**Method:** for each of the 54 dates in the window, compute the relative range
`(max − min) / median` across the six-pair group {MU, MSFT, AMD, MELI, AMZN, NU}, and
separately QQQ's relative deviation from that group's median.

| Group | Statistic | Result |
|---|---|---|
| Six-pair group internal relative range | mean | **9.39 × 10⁻¹⁷** |
| Six-pair group internal relative range | max | **2.25 × 10⁻¹⁶** |
| QQQ deviation from six-pair median | mean | +4.85% |
| QQQ deviation from six-pair median | stdev | 2.43% |
| QQQ deviation from six-pair median | range | +0.83% to +10.24% |

**2.25 × 10⁻¹⁶ is machine epsilon for IEEE 754 double precision** (`2.22 × 10⁻¹⁶`). The
six-pair group's implied-FX values do not merely converge tightly — they are numerically
**equal**, differing only by floating-point rounding in the final bit. No real-world
arbitrage relationship between six independently-quoted, independently-traded instruments —
subject to bid/ask spread, quote timing, and liquidity differences — converges to
floating-point equality. A genuine tight-arbitrage band (which is a legitimate thing to
expect from CEDEAR/underlying CCL-implied pricing) would show dispersion at the
basis-point-to-low-percent scale, which is exactly what QQQ shows (0.83%–10.24%).

**Conclusion for directive 2:** the near-1:1 relationship among six of the seven pairs is
**not** economically expected convergence, and it is **not** a definitional or unit
incompatibility in the calculation (Part A shows the chain is internally consistent). It is a
data-provenance fact: those six series' stored ARS values are the same real number as
`underlying_USD × common_rate(date)`, carried in six separate rows. This is consistent with,
and sharpens, the F-033 finding — it is no longer a suspicion based on rounded-value
comparison, but a demonstrated floating-point identity.

---

## Part C: Recomputed dispersion diagnostics — all seven pairs retained, none discarded

Per directive 1, the six near-identical relationships are **not** excluded from this
calculation. All 54 dates, all seven pairs, full formula from Part A.

| Statistic | Min | Median | P90 | P95 | Max |
|---|---|---|---|---|---|
| MAD (median absolute relative residual, per date) | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Relative stdev of implied_fx across 7 pairs (per-date CV) | 0.0031 | 0.0174 | 0.0302 | 0.0321 | 0.0387 |

The two statistics diverge because of the six/one split: MAD (order statistic, robust to a
single outlier) is driven to zero by the six-way tie; the per-date CV (a moment statistic)
is pulled upward by QQQ's ~5% deviation acting on one of seven points.

**Pair-level residual distribution, all seven retained:**

| Pair | n | Mean residual | Median residual | Stdev | Min | Max |
|---|---|---|---|---|---|---|
| MU | 54 | +0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| MSFT | 54 | +0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| AMD | 54 | −0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| MELI | 54 | +0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| AMZN | 54 | −0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| NU | 54 | −0.00000 | +0.00000 | 0.00000 | −0.00000 | +0.00000 |
| **QQQ** | 54 | **+0.04854** | **+0.04592** | **0.02433** | **+0.00826** | **+0.10235** |

This is the complete, honest diagnostic with nothing withheld: six pairs report zero residual
to numerical precision because — per Part B — they are the same number six times, and QQQ
reports the only non-degenerate residual series in the cohort.

---

## Part D: Sufficiency reassessment

**Cross-sectional width.** Nominally 7 pairs. Empirically demonstrated in Part B — not
assumed — the six-pair group carries one degree of freedom (internal relative range at
machine epsilon), and QQQ carries a second. **Effective cross-sectional width: 2.**

**Temporal coverage.** 54 dates with full contemporaneous coverage, 2026-05-29 to
2026-08-14 (~2.5 months), inside a single regime with no internal structural boundary
(unchanged from the prior report).

**Pair-level variation.** Six of seven pairs show literally zero variation relative to each
other by construction (Part B). The one pair with real variation (QQQ) has 54 observations
in one regime — enough to describe *that pair's* deviation pattern over this window, not
enough to characterize a cross-sectional panel-coherence distribution, which requires
multiple independent members varying against each other.

**Answer to directive 3:** the window does **not** contain enough independent variation to
estimate a meaningful dispersion distribution. This is stated precisely, not by discarding
data or asserting it without proof: **2** effective independent series, over **1** regime, is
below what any cross-sectional dispersion statistic requires to mean anything statistically
(a "spread across the panel" computed from 2 points is just the distance between 2 points,
not a distribution). This does not change if the six near-identical relationships are
retained in the calculation — they were retained throughout Parts A–C, in accordance with the
directive, and retaining them is what makes the machine-epsilon finding demonstrable in the
first place.

**What this changes from the prior report:** the prior report (`CALIBRATION_EVIDENCE_POST_
CEDEAR_POPULATION_2026-08-18.md`) reported the six-pair convergence as consistent with F-033
based on rounded-value comparison. This report sharpens that into a quantitative,
non-discretionary determination (floating-point-epsilon identity vs. a real few-percent
arbitrage band, shown side by side) and explicitly answers the "is this economically
expected" question the prior report left as an inference. The bottom-line sufficiency
conclusion is unchanged.

No numerical threshold is selected, changed, or implied by any of the above.
