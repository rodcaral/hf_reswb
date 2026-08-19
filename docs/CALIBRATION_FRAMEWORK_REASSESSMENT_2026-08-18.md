# Calibration Framework Reassessment — PRIMARY and SECONDARY Cohorts

**Date:** 2026-08-18
**Requested by:** SDT/SE
**Nature of this document:** Evidence/diagnostic report across both cohorts. **No numerical
threshold is selected, changed, or promoted.** Cohort separation is preserved throughout —
figures from the two cohorts are reported side by side for comparison, never pooled for a
single calibration statistic.

---

## Part 0: Cohort definitions, restated

| Cohort | Composition | Structure |
|---|---|---|
| **PRIMARY** | 12 CEDEAR ↔ direct-USD-underlying pairs (AAPL, BABA, BIDU, UBER, GLD, MU, MSFT, AMD, MELI, QQQ, AMZN, NU) | CEDEAR (BYMA, ARS) vs. the underlying's own common-stock/ETF quote (NASDAQ/NYSE, USD) |
| **SECONDARY** | 3 CEDEAR ↔ ADR pairs (YPF, Banco Macro, Pampa Energía) | CEDEAR (BYMA, ARS) vs. an **ADR** (NYSE, USD) that itself represents a multiple of local ordinary shares — an extra ratio layer PRIMARY does not have |

**No pooling.** Every distribution below is reported per cohort; nothing is combined into a
single cross-cohort statistic.

---

## Part 1: PRIMARY cohort — status unchanged, summarized from existing evidence

No new computation was performed on PRIMARY in this pass; it is summarized here for
side-by-side comparison, per the established record:

- Staleness: P95 = 3d, uniform across all 12 series (`CALIBRATION_EVIDENCE_12PAIR_COMPLETE_
  2026-08-18.md`, `STALENESS_TAIL_RELATIONSHIP_DIAGNOSTICS.md`).
- Dispersion (implied-FX residual methodology): effective cross-sectional width **2** (six of
  seven new-CEDEAR pairs are not independent — F-033; QQQ is the only non-degenerate member),
  over a single ~2.5-month regime (`CALIBRATION_REOPENED_PROVENANCE_CORRECTED_2026-08-18.md`).
  Insufficient for calibration; closed as such (`CALIBRATION_ATTEMPT_CLOSED_2026-08-18.md`).
- Deep multi-year history is configured but absent from the live database for the original 5
  pairs (unresolved, HistFinTS-side).

---

## Part 2: SECONDARY cohort — new finding: a ratio error in the prior secondary-cohort record

Before computing anything, the ratio inputs were checked, since `series.ratio` is `NULL` for
all six SECONDARY-cohort series (unlike PRIMARY, where it is a structured field) — the ratios
this cohort depends on are asserted in `calibration-evidence-secondary-cohort-2026-08-18.md`
from external sources (SEC filings, ADR program names), not read from the database. That
document asserted **YPF's CEDEAR:ADR ratio changed from 1:1 to 1:10 on 2026-08-04**
("YPF split").

**This is contradicted by the data.** Computing implied CCL (`local_ARS / (ADR_USD / ratio)`)
with `ratio = 1` for YPF produces values ~18× smaller than Banco Macro and Pampa Energía's
implied CCL on the same dates (e.g. 2013-02-05: YPF at ratio=1 gives 0.7743; Banco Macro gives
7.7219, Pampa gives 7.6923 — a decade-plus apart, not noise). **Testing `ratio = 10`
constant across YPF's entire history — not just post-2026-08-04 — resolves this discrepancy
to the same tight agreement seen between Banco Macro and Pampa:**

| Date | YPF (ratio=10) | Banco Macro | Pampa Energía |
|---|---|---|---|
| 2013-02-05 | 7.7433 | 7.7219 | 7.6923 |
| 2026-07-01 | 1563.61 | 1562.05 | 1575.99 |
| 2026-08-03 (pre "split") | 1587.35 | 1575.03 | 1585.56 |
| 2026-08-04 ("split" date) | 1579.37 | 1582.23 | 1580.38 |
| 2026-08-14 | 1570.43 | 1577.12 | 1580.51 |

**YPF's CEDEAR:ADR ratio is constant at 10 throughout, including across the claimed
"split boundary."** There is no visible ratio step at 2026-08-04 once the correct ratio is
used — the prior document's "YPF split" (1:1→1:10) appears to have conflated a real, correctly
SEC-filed corporate action (YPF's underlying ordinary-share stock split, ~393.3M→3,933.1M
shares) with the CEDEAR:ADR ratio itself. Since both the CEDEAR and ADR legs carry Yahoo's
`SPLIT_ADJUSTED` basis, the share-count split is already reflected proportionally on both
sides and does not change their ratio to each other — the same caution this project has
applied before (D-015/F-021, AAPL's genuine ratio step) cuts the other way here: not every
corporate action that changes a ratio number changes the *conversion* ratio between two
already-adjusted series.

**This finding is new and unreconciled with the prior document's "structural-event validity
test" claim** (`calibration-evidence-secondary-cohort-2026-08-18.md`, "YPF split serves as
validation of framework behavior") — that claim rests on the ratio assertion just shown to be
incorrect. It is recorded here as a finding, not silently corrected in place; the prior
document is not edited, per this project's evidence-preservation discipline. Flagging for a
DECISIONS.md entry (below) rather than treating it as settled without review.

**Practical effect:** with `ratio = 10` (constant, not stepped), YPF becomes economically
consistent with its two SECONDARY-cohort peers and is retained as a full member of every
statistic below, rather than being a visible outlier from a data error.

---

## Part 3: SECONDARY cohort — empirical distributions

### Staleness (local-CEDEAR side, full available history)

| Pair | Obs | Gaps | Min | Max | Mean | Median | P90 | P95 |
|---|---|---|---|---|---|---|---|---|
| YPF | 6,624 | 6,623 | 1d | 7d | 1.47d | 1d | 3d | 3d |
| Banco Macro | 6,620 | 6,619 | 1d | 7d | 1.47d | 1d | 3d | 3d |
| Pampa Energía | 5,575 | 5,574 | 1d | 7d | 1.48d | 1d | 3d | 3d |
| **Aggregate** | — | 18,816 | 1d | 7d | 1.47d | — | 3d | **3d** |

**This is a materially different picture from the prior secondary-cohort document**, which
reported P95 = 5d and max gaps up to 28d. This pass recomputed gaps directly from the current
`observation` table rather than reusing the earlier figures, and finds P95 = 3d, max = 7d,
matching PRIMARY's staleness profile closely. The discrepancy with the earlier document is
noted, not resolved here — it may reflect database state changes since that document was
written (additional backfill, corrections) or a methodological difference in how gaps were
computed; this is flagged as an open reconciliation item rather than asserted either way.

### Dispersion (implied-CCL residuals, corrected ratio, all three pairs retained)

Formula: `implied_ccl(pair, date) = local_CEDEAR_ARS(date) / (ADR_USD(date) / ratio)`,
ratio = 10 (YPF, corrected), 10 (Banco Macro), 25 (Pampa Energía). Panel center = median
across the three pairs present. Contemporaneous observations only.

**Coverage:** 4,006 dates with all three pairs present, spanning **2009-10-09 to
2026-08-14** — nearly 17 years, the deepest contemporaneous cross-sectional window available
anywhere in this project's calibration work to date.

**Circularity check (same test applied to PRIMARY under F-033):** the three-pair relative
range is economically scaled (mean 1.65%, not the floating-point-epsilon scale that flagged
F-033) — **no circularity signature in SECONDARY.**

| Statistic | Min | Median | P90 | P95 | Max |
|---|---|---|---|---|---|
| MAD (median abs. relative residual, per date) | 0.0000 | 0.0027 | 0.0092 | **0.0126** | 0.0490 |
| Aggregate CV (per-date, 3 pairs) | 0.0001 | 0.0063 | 0.0173 | **0.0232** | 0.2141 |

**Pair-level residual behavior:**

| Pair | n | Mean | Median | Stdev | P95 \|residual\| |
|---|---|---|---|---|---|
| YPF | 4,006 | +0.0008 | +0.0000 | 0.0096 | 0.0200 |
| Banco Macro | 4,006 | −0.0004 | +0.0000 | 0.0137 | 0.0231 |
| Pampa Energía | 4,006 | −0.0004 | +0.0000 | 0.0111 | 0.0205 |

No pair shows a persistent one-signed mean residual — all three are centered near zero, with
comparable stdev. This is consistent with genuine cross-sectional coherence around a shared
implied CCL rate, not a systematic per-pair bias.

### Temporal / regime segmentation

| Regime | Dates | Median MAD | P95 MAD |
|---|---|---|---|
| Pre-2020 | 2,432 | 0.0030 | 0.0143 |
| 2020–2021 (pre-crisis) | 475 | 0.0035 | 0.0116 |
| 2022–2023 (crisis) | 474 | 0.0024 | 0.0096 |
| 2024–2026 (post-crisis) | 625 | 0.0016 | 0.0065 |

Dispersion is **lowest in the most recent regime**, not elevated during the 2022–2023 ARS
crisis window as the prior secondary document reported (it found dispersion peaking in
2022–2023). This pass's regime segmentation shows the opposite direction — another point of
disagreement with the prior document that is flagged, not silently reconciled (see Part 2's
note on the staleness discrepancy — the two documents may be measuring different underlying
quantities: the prior one used raw-price CV against "local-market consensus," this one uses
the FDA-directed implied-FX-residual methodology adopted after that document was written).

---

## Part 4: Effective independent cross-sectional width

| Cohort | Nominal width | Effective width (this pass) | Basis |
|---|---|---|---|
| PRIMARY | 7 (new) / 12 (all) | **2** | F-033: six of seven new pairs are the same number to machine precision; unresolved |
| SECONDARY | 3 | **3** | All three pairs show economically-scaled, mutually consistent residuals once YPF's ratio is corrected; no circularity signature |

**SECONDARY currently offers a materially better-conditioned cross-section than PRIMARY** —
three genuinely independent members instead of two, and nearly 17 years of contemporaneous
coverage instead of 2.5 months. This does not change the FDA ruling's cohort-separation
requirement (SECONDARY remains validation-only, not pooled into PRIMARY calibration), but it
is a materially different sufficiency picture than PRIMARY's, worth stating plainly rather
than letting PRIMARY's insufficiency read as if it applied project-wide.

---

## Part 5: Evidence-quality limitations

**PRIMARY** (restated, unchanged): F-033 blocking (6 of 7 new pairs non-independent, provider-
side computed cross-rate, exact mechanism unestablished); original-5 deep history absent from
live DB; 2.5-month single-regime window even where data is usable.

**SECONDARY** (this pass):
1. **Ratio provenance is not a structured field.** `series.ratio` is NULL for all six series;
   the 10/10/25 ratios used here (and the erroneous 1→10 YPF step in the prior document) are
   externally asserted, not database-verified. This is the same category of gap flagged in
   `CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md` for BABA/BIDU's ADR representation
   ratio — it now has a concrete instance where getting it wrong produced a materially wrong
   conclusion (the "YPF split" claim).
2. **Two unreconciled discrepancies with the prior secondary-cohort document** (staleness
   P95 3d vs. 5d; dispersion peak regime 2024-2026-lowest vs. 2022-2023-highest) are recorded
   as open items, not resolved by this pass — see Parts 3's notes. Both documents should not
   be treated as interchangeable until reconciled.
3. **F-026 carry-forward exposure**, previously flagged for Pampa Energía (12.2% zero-volume
   rate in the prior document), was not re-verified in this pass and should not be assumed
   resolved.
4. **F-009 era boundary** (pre/post ~2024 reconciliation status) applies to SECONDARY exactly
   as it does to PRIMARY and was not separately re-examined here.
5. **Contemporaneity loss is asymmetric across pairs**: YPF retains 6,434 of 6,624 local
   observations with an ADR match (97%), Banco Macro 4,866 of 6,620 (74%), Pampa Energía
   4,008 of 5,575 (72%) — Banco Macro and Pampa's ADR-side histories start later (2006 and
   2009 respectively) than their CEDEAR-side histories (both 2000), which is why the common
   window in Part 3 starts at 2009-10-09 rather than 2000.

---

## Part 6: What this reassessment does and does not conclude

- **Does not select, change, or promote any numerical threshold** — CV 0.167 remains
  retired/provisional exactly as it stood before this pass; no SECONDARY-derived value is
  proposed as a replacement or cross-check.
- **Does not pool PRIMARY and SECONDARY** — cohort separation preserved throughout; the
  side-by-side tables above are for comparison, not combination.
- **Does** identify that SECONDARY, once the YPF ratio correction is accounted for, has
  meaningfully different (better) sufficiency characteristics than PRIMARY — worth FDA/SE
  awareness when deciding where calibration effort goes next, without this report making that
  prioritization call itself.
- **Does** surface a new, unreconciled finding (YPF ratio) requiring a DECISIONS.md entry and,
  if SECONDARY is ever used beyond validation, a decision on whether/how to correct the prior
  document.
