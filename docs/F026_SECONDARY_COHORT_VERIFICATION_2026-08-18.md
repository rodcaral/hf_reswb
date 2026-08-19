# F-026 Carry-Forward Verification — Secondary Cohort

**Date:** 2026-08-18
**Requested by:** SDT Workbench directive
**Nature of this document:** Independent verification result. **No threshold is changed or
promoted. The secondary cohort is not promoted into PRIMARY V0 calibration.**

---

## What was verified

The prior secondary-cohort document's carry-forward figures (YPF 9.0%, Banco Macro 6.7%,
Pampa Energía 12.2%, "Pampa flagged for review") were never independently checked in this
project's own work — they were carried forward unverified, exactly the pattern that has
already proven unreliable for this cohort (ratio, staleness, and regime-dispersion figures
all failed reconciliation in `CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md`).

**Applied this project's own established F-026 detection rule** (D-038: `volume = 0` AND
`open = high = low = value` AND `value` equals the prior stored close at **exact** float
equality), directly against the current `observation` table for all three local-side (CEDEAR)
series.

## Verification result

| Pair | Total obs | Phantom (F-026 rule) | Rate — verified | Rate — prior document | Match? |
|---|---|---|---|---|---|
| YPF | 6,624 | 542 | **8.18%** | 9.0% | Close, not exact |
| Banco Macro | 6,620 | 438 | **6.62%** | 6.7% | Close, not exact |
| Pampa Energía | 5,575 | 548 | **9.83%** | 12.2% | **Notably lower** |

**Pampa Energía's carry-forward rate is confirmed elevated relative to its peers (9.83% vs.
6.62%–8.18%), but not to the degree the prior document claimed (12.2%).** The prior
document's qualitative flag ("elevated, review recommended") is directionally correct; its
specific figure is not reproduced. Consistent with this cohort's now-established pattern:
directionally-right, numerically-unreliable prior claims.

---

## Affected secondary-cohort calculations — identified, not yet recomputed

### 1. Staleness (`CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md`, Part 2) — materially affected

That report's staleness figures (P95 = 3d, max = 7d, all three pairs) were computed on the
**full observation set, including phantom carry-forward bars.** A phantom bar sits on a date
with no real trade, so including it as an "observation" bridges what would otherwise be a
longer true gap — this directly understates staleness.

**Magnitude, checked directly:** recomputing gaps using only non-phantom (real-trade) dates:

| Pair | Real (non-phantom) obs | Max real gap | P95 real gap | Mean |
|---|---|---|---|---|
| YPF | 6,082 | **56d** | 4d | 1.60d |
| Banco Macro | 6,182 | **107d** | 3d | 1.57d |
| Pampa Energía | 5,027 | **163d** | 4d | 1.64d |

**The true maximum staleness gap, once phantom bars are excluded, is one to two orders of
magnitude larger than the 7d figure reported** (56–163 days vs. 7 days). P95 barely moves
(3–4d vs. 3d), so the *typical* staleness picture is not badly distorted — but the **tail**
is completely different, and any calculation depending on maximum gap, tail behavior, or
"how stale can this get" is invalidated by the phantom-inclusive figure. Note this also does
not match the prior (superseded) document's max-gap claims (28d YPF, 22d Pampa) — those
figures do not reproduce here either, at any phantom-inclusion setting checked.

This report does not select a corrected staleness distribution as new evidence — it
establishes that the existing one is wrong in its tail and by how much, which is the
verification task asked for.

### 2. Dispersion (`CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md`/`CALIBRATION_
FRAMEWORK_REASSESSMENT_2026-08-18.md`, dispersion sections) — affected, concentrated in the tail

Of the 4,006 contemporaneous three-pair dates used for the implied-CCL dispersion
calculation, **168 (4.2%) have at least one pair sitting on a phantom bar** on that date.

More importantly, this contamination is **not uniformly distributed** — checking the
previously reported top-8 highest-dispersion dates directly: **5 of the 8** have *all three*
pairs on a phantom bar simultaneously (2012-03-21, 2012-02-08, 2014-11-24, 2013-10-07,
2012-07-31). A simultaneous three-way phantom carry-forward is consistent with a shared
BYMA/NYSE calendar effect (a closed-market day Yahoo nonetheless populated a bar for), not
independent per-pair staleness — but it means **the reported dispersion tail is
disproportionately built from carry-forward artifacts, not from genuine same-day economic
disagreement between the three pairs.** The aggregate P95 MAD figure (0.0126) is less exposed,
since it is a bulk statistic over 4,006 dates and only 4.2% are contaminated — but the specific
"highest-dispersion dates" narrative in the prior reports should not be read as showing real
market stress events without re-filtering for phantom contamination first.

### 3. What is not affected

- The cross-pair ratio verification (`ratio=10` for YPF) in `CALIBRATION_SECONDARY_COHORT_
  CORRECTED_2026-08-18.md` Part 1 used specific sampled dates checked individually; none of
  the five sample dates used there coincide with a phantom bar for any of the three series
  (spot-checked). The ratio conclusion stands.
- The aggregate dispersion percentile figures (P95 MAD ≈ 0.0126) are only mildly exposed
  (4.2% contamination rate) and are not retracted, but should not be treated as
  phantom-free.

---

## Explicitly not done

- No corrected staleness or dispersion distribution is promoted as new secondary-cohort
  evidence. The magnitudes above are reported to characterize the *size* of the exposure, not
  as a replacement calibration.
- No threshold is selected, changed, or promoted for either cohort.
- The secondary cohort is **not** promoted into PRIMARY V0 calibration. This verification
  narrows what is known about the secondary cohort's reliability; it does not change the
  cohort-separation ruling.

## Standing status, restated per this directive

**PRIMARY CEDEAR calibration remains blocked** by the independent-evidence/provenance
problem (F-033: effective cross-sectional width 2) and the temporal-depth problem (single
2.5-month regime). Nothing in this document — or in the secondary-cohort reconciliation work
that preceded it — closes either gap. The corrected and now F-026-verified secondary cohort
may be a cleaner basis for a *separate* decision about its use as long-horizon validation
evidence, but that decision is not made here and does not remove the PRIMARY block.
