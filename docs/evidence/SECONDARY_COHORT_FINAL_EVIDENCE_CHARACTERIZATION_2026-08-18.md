# Secondary Cohort — Final Corrected Evidence Characterization

**Date:** 2026-08-18
**Requested by:** SDT Workbench
**Supersedes for reference purposes:** `calibration-evidence-secondary-cohort-2026-08-18.md`
(original, preserved unedited), `CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md`
(reconciliation), `F026_SECONDARY_COHORT_VERIFICATION_2026-08-18.md` (phantom verification).
**This document consolidates all three into one final characterization and adds the one piece
not yet computed — a clean, phantom-excluded dispersion distribution.** None of the prior
three documents are edited or deleted.
**Nature of this document:** Evidence characterization only. **No threshold is selected,
changed, or promoted. The secondary cohort is not promoted into PRIMARY V0 calibration.**

**Cohort:** YPF (11312/11199), Banco Macro (11313/1284), Pampa Energía (11315/7491) — CEDEAR
(BYMA, ARS) vs. ADR (NYSE, USD), ratios 10 / 10 / 25 respectively (YPF corrected from the
original document's erroneous 1→10 step; see reconciliation document Part 1 for the
verification basis — no structured DB field exists for any of the three ratios, all are
empirically checked, not documented).

---

## 1. Ordinary staleness distribution (phantom-inclusive — the naive figure)

Computed on every stored observation, without distinguishing genuine trade prints from
carried-forward bars. This is what a query against the raw `observation` table returns
directly.

| Pair | Obs | Gaps | Max | Mean | P95 |
|---|---|---|---|---|---|
| YPF | 6,624 | 6,623 | 7d | 1.47d | 3d |
| Banco Macro | 6,620 | 6,619 | 7d | 1.47d | 3d |
| Pampa Energía | 5,575 | 5,574 | 7d | 1.48d | 3d |

**This is the correct distribution to use for "how often is a fresh print available," and it
does match a full gap enumeration** (not a sample) — no larger gap exists in the raw data.
**It is the wrong distribution to use for "how stale can a genuine market observation
actually be,"** because ~7–10% of the "observations" behind it are not genuine market prints
(§3).

---

## 2. True staleness tail after phantom-bar exclusion

Recomputed using only observations that fail the F-026 phantom test (§3) — i.e., dates with a
real, distinct trade print.

| Pair | Real (non-phantom) obs | Gaps | Max | P95 | Mean |
|---|---|---|---|---|---|
| YPF | 6,082 | 6,081 | **56d** | 4d | 1.60d |
| Banco Macro | 6,182 | 6,181 | **107d** | 3d | 1.57d |
| Pampa Energía | 5,027 | 5,026 | **163d** | 4d | 1.64d |

**The typical case is close to §1** — P95 shifts by at most one day, mean by a few hundredths
of a day. **The tail is not.** Real maximum staleness is one to two orders of magnitude
larger than the naive figure suggests: up to **163 days** for Pampa Energía. Any use of this
cohort that depends on a worst-case or tail staleness assumption must use this section, not
§1. Neither of these figures matches the original (superseded) document's claimed max gaps
(28d YPF, 22d Pampa) — those remain unreproduced under any method checked.

---

## 3. Phantom / calendar artifacts — what they are and how much of the data they are

**Detection rule** (this project's established D-038 F-026 test): an observation is phantom
if `volume = 0`, `open = high = low = value`, and `value` equals the immediately prior stored
close at exact float equality.

| Pair | Phantom count | Rate | Prior document's claim | Verified vs. claimed |
|---|---|---|---|---|
| YPF | 542 | 8.18% | 9.0% | Close, not exact |
| Banco Macro | 438 | 6.62% | 6.7% | Close, not exact |
| Pampa Energía | 548 | 9.83% | 12.2% | Confirmed elevated, magnitude overstated |

**Pattern found beyond the rate itself:** phantom bars are not randomly distributed across
the three pairs independently. Checking the corrected report's originally-flagged top-8
highest-dispersion dates, **5 of 8 had all three pairs on a phantom bar simultaneously** —
consistent with a shared BYMA/NYSE calendar-closure day that Yahoo nonetheless populated a
bar for, across all three tickers at once, rather than three independent stale-print events.
Of the full 4,006-date contemporaneous cross-section used for dispersion (§4), **168 dates
(4.2%) have at least one pair on a phantom bar.**

**Practical consequence:** phantom bars behave as a **calendar artifact**, not as three
independent per-pair liquidity signals. Treating a phantom-bar date as informative about
either staleness risk or cross-pair disagreement double-counts the same underlying fact (the
market was likely closed or the feed carried a stale quote) as if it were three separate
observations.

---

## 4. Economically meaningful dispersion (phantom-excluded, computed for this document)

Not previously delivered as a separate distribution — computed here for the first time.
Same formula as the corrected report (`implied_ccl = local_ARS / (ADR_USD / ratio)`, robust
median center, relative residual), restricted to the **3,838 of 4,006** contemporaneous dates
with **no** pair on a phantom bar.

| Statistic | Min | Median | P75 | P90 | P95 | Max |
|---|---|---|---|---|---|---|
| MAD | 0.0000 | **0.0026** | 0.0052 | 0.0086 | **0.0114** | 0.0490 |
| CV | 0.0001 | **0.0061** | 0.0103 | 0.0162 | **0.0214** | 0.2141 |

Compared with the phantom-inclusive figures in the corrected report (P95 MAD 0.0126, P95 CV
0.0232): the clean distribution is modestly **tighter** at every percentile, as expected once
calendar-artifact dates are removed — but the shift is small (P95 MAD 0.0114 vs. 0.0126,
roughly 10% lower). **The bulk statistic was not badly distorted; the specific "highest-
dispersion dates" narrative was.** Re-running the top-8 on the clean data:

| Date | Clean MAD | Was it in the phantom-inclusive top-8? |
|---|---|---|
| 2023-11-21 | 0.0490 | Yes (genuine — not a phantom date) |
| 2013-02-28 | 0.0402 | Yes (genuine) |
| 2019-08-12 | 0.0391 | Yes (genuine) |
| 2014-12-23 | 0.0332 | No — newly surfaced once phantom dates are removed |
| 2013-02-25 | 0.0303 | No — newly surfaced |
| 2012-11-15 | 0.0298 | No — newly surfaced |
| 2012-10-31 | 0.0291 | No — newly surfaced |
| 2024-07-03 | 0.0267 | No — newly surfaced |

Three of the original top-8 (2023-11-21, 2013-02-28, 2019-08-12) were genuine all along and
remain the highest-dispersion dates in the clean data too — those are real evidence of
cross-pair disagreement, not artifacts. The other five slots are filled by different,
previously lower-ranked genuine dates once the calendar-artifact dates are removed from
contention.

**Pair-level residual behavior, clean:** all three pairs remain centered near zero (mean
+0.0008 / −0.0004 / −0.0005), no persistent bias, stdev 0.0086–0.0134 — consistent with the
phantom-inclusive finding that this cohort shows genuine cross-sectional coherence, not a
circularity artifact (F-033's signature is absent here at both the raw and clean level).

**Regime segmentation, clean:** unchanged in direction from the phantom-inclusive corrected
report — dispersion lowest in 2024–2026 (P95 0.0064), highest pre-2020 (0.0129). The
phantom-inclusive vs. clean regime figures differ by only a few percent at each point; regime
ordering is not sensitive to the phantom-bar question.

**This is the distribution that should be cited if the secondary cohort is used as long-
horizon validation evidence going forward** — it is the most rigorously derived of the four
dispersion figures this cohort has now produced across three documents.

---

## 5. Unresolved methodology / data limitations — consolidated

Carried forward from the reconciliation and verification documents, not re-litigated here:

1. **No structured ratio field exists for any of the six SECONDARY series** (`series.ratio`
   NULL, `field_override`/`identifier` empty). All three ratios (YPF=10, Banco Macro=10,
   Pampa=25) are empirically verified via cross-pair consistency, not database-documented —
   weaker provenance than PRIMARY's structured `series.ratio` field.
2. **A 24-observation delta** between this pass's local-side observation count (18,819) and
   the original document's reported figure (18,795) — not investigated.
3. **The original document's regime-dispersion figures are only partially explained.**
   Recomputing with its (wrong) YPF ratio reproduces the qualitative 2022–2023 elevation it
   reported, but not the exact magnitude — a second, compounding factor (its raw-price-CV
   formula vs. this cohort's implied-CCL-residual formula, adopted after that document was
   written) cannot be reconstructed without its original computation, which was not preserved.
4. **The original document's staleness figures (P95=5d, max=28d/22d) do not reproduce under
   any method checked here** — neither the phantom-inclusive nor the phantom-excluded
   recomputation matches them. The cause (an earlier, less-complete database state vs. a
   different gap-computation method vs. an error in the original) is not determined.
5. **F-009 era boundary** (pre/post ~2024 reconciliation status) has not been separately
   examined for this cohort in any of the four documents to date.
6. **Contemporaneity is asymmetric across pairs**, driven by the ADR-side series starting
   later than the CEDEAR-side series (Banco Macro ADR from 2006, Pampa ADR from 2009, vs. both
   CEDEAR sides from 2000/2004) — this sets the common window's start date (2009-10-09), not a
   data-quality defect, but worth restating since it caps how far back any cross-sectional
   statistic in this cohort can go.
7. **Phantom-bar detection was applied only to the local (CEDEAR/BYMA) leg.** The ADR
   (NYSE/USD) leg was not separately checked for its own carry-forward behavior; if the ADR
   leg also carries phantom bars on different dates than the local leg, the "clean" 3,838-date
   distribution in §4 may still include some ADR-side artifacts not filtered out. This is a
   gap in this document's own scope, stated rather than assumed away.
8. **Cohort separation from PRIMARY remains in force** and is not reconsidered by this
   document; nothing here bears on whether or when SECONDARY could ever be pooled with
   PRIMARY, which remains an FDA-level decision independent of data quality.

---

## Bottom line

- **§1 vs §2** is the single most important distinction this document establishes: the naive
  staleness figure is fine for typical-case use and wrong by orders of magnitude for tail/
  worst-case use.
- **§4** is now the most defensible dispersion evidence this cohort has produced, and the one
  to cite going forward if SECONDARY is used as long-horizon validation.
- **§5** lists what remains genuinely open — this document resolves what it can from existing
  data and states plainly what it cannot.
- **No threshold implication anywhere above.** PRIMARY CEDEAR calibration remains blocked by
  its own, separate independent-evidence and temporal-depth problems, unaffected by anything
  in this characterization.
