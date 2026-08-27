# Secondary Cohort Evidence — Corrected and Reconciled

**Date:** 2026-08-18
**Supersedes (in part):** `calibration-evidence-secondary-cohort-2026-08-18.md`
**Status of the prior document:** **preserved, unedited, not deleted.** This is a new,
separate document. The prior document remains in the repository as the original evidence
trail; where this document says a claim is "superseded," the prior document's text is not
altered — only this document's determination is that the claim should no longer be relied on.
**Nature of this document:** Corrected secondary-cohort evidence report. **No numerical
threshold is recommended, selected, or promoted anywhere below.**

---

## Reconciliation table — every claim in the prior document, dispositioned

| # | Prior claim | Disposition | Basis |
|---|---|---|---|
| 1 | Cohort composition: YPF (11312/11199), Banco Macro (11313/1284), Pampa Energía (11315/7491) | **Supported** | Re-verified against current `series`/`observation` tables; ids and pair structure confirmed |
| 2 | Banco Macro ratio = 10:1 ("ADR program name, standard") | **Supported** | Empirically verified (Part 1) — economically consistent with Pampa across 4,006 dates |
| 3 | Pampa Energía ratio = 25:1 ("SEC Form 20-F, investor FAQ") | **Supported** | Empirically verified (Part 1) — economically consistent with Banco Macro |
| 4 | **YPF ratio 1:1 (pre-2026-08-04) → 1:10 (post-split), "verified: SEC filing"** | **Superseded** | Part 1 below — ratio=10 constant fits the data; the stepped 1→10 hypothesis does not |
| 5 | Combined observations: 18,795 local + 16,060 ADR = 34,855 | **Supported, with a small unexplained delta** | Recount: local 18,819 (24 more than reported), ADR 16,060 (exact match). The 24-observation local-side difference is not investigated further here — plausibly incremental ingestion between report dates — and does not affect any conclusion in this document |
| 6 | Staleness: P95=5d, mean=1.63d, max 28d(YPF)/15d(BMA)/22d(PAM) | **Superseded** | Part 2 below — full gap enumeration against current data finds no gap exceeding 7 days anywhere in any of the three series' history |
| 7 | YPF split "structural-event validity test" — framework correctly detected/segmented a ratio change | **Superseded** | The premise (a real ratio step existed) is false per claim #4; there is nothing for the framework to have correctly detected. Not a framework validation |
| 8 | Dispersion CV (median 0.089, mean 0.121, P95 0.301) vs. primary cohort CV | **Superseded by metric redefinition, not directly comparable** | These figures use the pre-FDA-ruling raw-price-level CV methodology, retired project-wide (`CV 0.167` retired, dispersion redefined around implied-FX residuals). Not re-derivable for comparison; superseded as a matter of methodology, independent of the YPF ratio issue |
| 9 | Regime segmentation: dispersion peaks 2022-2023 (mean CV 0.149), "normalizes" but stays elevated 2024-2026 (0.108) | **Superseded; root cause substantially, not fully, identified** | Part 3 below |
| 10 | Carry-forward rates (YPF 9.0%, Banco Macro 6.7%, Pampa 12.2%; Pampa flagged for review) | **Unresolved — not re-verified this pass** | No F-026-style carry-forward recount was performed in this report; the prior figures are neither confirmed nor contradicted |
| 11 | "Do not pool with primary cohort for threshold calibration" | **Supported, reaffirmed independently** | Consistent with, and superseded in authority by, the FDA cohort-separation ruling already logged in `DECISIONS.md` |
| 12 | Post-split sample caveat (17 obs insufficient for independent analysis) | **Moot** | There is no split in the ratio sense (claim #4); the caution about small-N independent analysis is sound in principle but was applied to an event that, on the ratio dimension, did not occur |

---

## Part 1: YPF ratio — verified against available structured/database evidence

**Structured database evidence checked and found absent.** `series.ratio` is `NULL` for all
six SECONDARY-cohort series (YPF, Banco Macro, Pampa Energía — both legs each). `field_
override` and `identifier` were also queried directly for all six series ids: zero rows in
either table. **There is no structured, database-native field recording any ratio for this
cohort, for any of the three pairs — not just YPF.** This applies equally to the two ratios
(Banco Macro 10:1, Pampa 25:1) the prior document treated as more solidly sourced ("ADR
program name," "SEC Form 20-F") — those are external assertions in prior documentation, not
data the database itself can confirm, exactly like YPF's.

**Given no structured field exists, the ratio basis used here is empirical: cross-pair
consistency of the implied CCL rate.** This is a P4 "Asserted, verified by construction" tier
— weaker than PRIMARY's `series.ratio` (a documented field), but checked directly rather than
carried forward from the prior document's unverified external citations.

**Test:** `implied_ccl(pair, date) = local_CEDEAR_ARS(date) / (ADR_USD(date) / ratio)`. Banco
Macro (ratio=10) and Pampa Energía (ratio=25) agree tightly across 4,006 contemporaneous
dates spanning 2009–2026 (median relative difference 0.69%, P95 3.51%) — this is the
reference the YPF ratio is checked against, not an assumption.

| Date | YPF @ ratio=1 | YPF @ ratio=10 | Banco Macro | Pampa Energía |
|---|---|---|---|---|
| 2013-02-05 | 0.77 | 7.74 | 7.72 | 7.69 |
| 2026-07-01 | 156.36 | 1563.61 | 1562.05 | 1575.99 |
| 2026-08-03 (day before claimed split) | 158.73 | 1587.35 | 1575.03 | 1585.56 |
| 2026-08-04 (claimed split date) | 157.94 | 1579.37 | 1582.23 | 1580.38 |
| 2026-08-14 | 157.04 | 1570.43 | 1577.12 | 1580.51 |

**`ratio = 1` is off from the two-pair reference by roughly 18–20× at every sampled date.
`ratio = 10`, held constant across the entire history including both sides of the claimed
2026-08-04 boundary, matches the reference to within a few percent throughout** — the same
tolerance Banco Macro and Pampa show against each other. There is no visible discontinuity at
2026-08-04 under `ratio = 10`.

**Interpretation, stated with appropriate uncertainty:** the prior document's SEC-filing
citation almost certainly refers to a real corporate action — YPF's underlying ordinary-share
count changing (~393.3M → 3,933.1M, a 10-for-1 split). What this analysis establishes is that
this action does **not** change the CEDEAR:ADR conversion ratio, because both series carry
Yahoo's `SPLIT_ADJUSTED` basis and the split is already reflected proportionally on both legs.
This document does not claim to know why the prior document reached the 1→10 conclusion (no
audit trail of that document's derivation exists to inspect) — only that the ratio it produced
does not fit the data, and `ratio = 10` constant does.

---

## Part 2: Staleness — recomputed and verified by full gap enumeration

Every gap in each series' complete observation history (not a sample) was enumerated and
sorted by size. Largest gaps found, all three series:

| Rank | Gap | Span |
|---|---|---|
| 1 | 7d | 2013-03-27 → 2013-04-03 |
| 1 (tie) | 7d | 2024-03-27 → 2024-04-03 |
| 3 | 6d | 2014-12-23 → 2014-12-29 |
| 4 | 6d | 2018-03-28 → 2018-04-03 |
| 5+ | ≤5d | (multiple, 2007–2009) |

Identical top gaps across all three series (same dates) — consistent with a shared BYMA
calendar effect (Easter week, year-end), not a pair-specific data problem.

| Pair | Obs (distinct dates) | Gaps | Max | P95 |
|---|---|---|---|---|
| YPF | 6,624 | 6,623 | 7d | 3d |
| Banco Macro | 6,620 | 6,619 | 7d | 3d |
| Pampa Energía | 5,575 | 5,574 | 7d | 3d |

**No gap exceeding 7 days exists anywhere in the current `observation` table for any of the
three series.** The prior document's reported max gaps (28d YPF, 22d Pampa) and P95 (5d) do
not reproduce against current data by any variant of this computation checked. This document
does not determine why — possible explanations include the prior analysis running against an
earlier, less-complete database state, or a different definition of "gap" (e.g., one that
folded in F-026-style zero-volume carry-forward periods as separate from true observation
gaps) — but does not assert either explanation without evidence. **Disposition: superseded by
this recomputation**, not merely differing.

---

## Part 3: Dispersion-regime discrepancy — substantially, not fully, explained

The prior document reported dispersion peaking in 2022–2023 (mean CV 0.149) and only
partially normalizing by 2024–2026 (0.108), still above the 2020–2021 baseline (0.098).
This document's Part 3 in the prior reassessment (`CALIBRATION_FRAMEWORK_REASSESSMENT_
2026-08-18.md`) found the **opposite** ordering under the corrected ratio and the FDA's
implied-residual methodology: dispersion **lowest** in 2024–2026.

**Test performed:** recomputing the regime segmentation with the prior document's YPF ratio
assumption (`ratio=1` pre-2026-08-04, `ratio=10` post) reproduces part of the pattern —
2022–2023 P95 MAD rises to 0.0809 (the highest of any regime under this ratio), and
2024–2026 also rises materially (0.0324) relative to its corrected-ratio value (0.0065):

| Regime | Corrected ratio (this report) | Prior document's ratio assumption |
|---|---|---|
| Pre-2020 | 0.0143 | 0.0347 |
| 2020–2021 | 0.0116 | 0.0240 |
| 2022–2023 | 0.0096 | **0.0809** (highest) |
| 2024–2026 | 0.0065 (lowest) | 0.0324 |

**Disposition: superseded, with the root cause substantially but not fully identified.** The
wrong YPF ratio reproduces the qualitative shape the prior document reported (2022+ elevated
relative to pre-2020) but not its exact figures — the prior document also used a different
dispersion formula entirely (raw-price CV "against local-market consensus," not the
implied-CCL-residual method used here), a second, compounding methodological difference that
cannot be reconstructed retroactively without the prior document's original computation code,
which was not preserved. **This document does not claim full reconciliation** — it establishes
that the YPF ratio error is a material contributor to the discrepancy, not the sole one, and
stops there rather than asserting more than the evidence supports.

---

## Part 4: What remains current from this pass (restated from `CALIBRATION_FRAMEWORK_
REASSESSMENT_2026-08-18.md`, not recomputed again here)

- Dispersion (corrected ratio, implied-CCL-residual methodology): aggregate MAD P95≈0.0126,
  per-date CV P95≈0.0232, all three pairs centered near zero residual with comparable stdev —
  no persistent per-pair bias, no circularity signature.
- Effective independent cross-sectional width: **3** (all three pairs).
- Contemporaneous coverage: 4,006 dates, 2009-10-09 to 2026-08-14.
- Cohort separation from PRIMARY preserved; SECONDARY remains validation-only.

---

## Part 5: Explicitly unresolved

- **Carry-forward / F-026 rates** for all three pairs (prior document's 9.0%/6.7%/12.2%
  figures) — not re-verified in this pass. Do not treat as confirmed or as refuted.
  Given the pattern found in Parts 1–3 (multiple prior figures not reproducing against
  current data), these percentages should be independently re-checked before being relied on,
  not assumed correct by default.
- **The 24-observation delta** in YPF-cohort local-side total count (claim #5) — noted, not
  investigated.
- **Exact numerical reconciliation of the dispersion-regime figures** (Part 3) — the magnitude
  of the residual gap between this report's regime pattern and the prior document's, beyond
  what the YPF ratio error explains, is not determined.

---

## No threshold recommendation

Nothing in this document selects, promotes, or proposes a numerical threshold for
`staleness_policy` or `dispersion_threshold`, for either cohort. This is a corrected evidence
record only.
