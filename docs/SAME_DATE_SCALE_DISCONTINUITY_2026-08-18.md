# Same-Date Scale Discontinuity — Seven CEDEAR Pairs, 2026-08-18

**Date filed:** 2026-08-19
**Nature of this document:** Verified finding, evidence report only. **No threshold selected,
changed, or promoted. No ratio applied or corrected.**
**Origin:** surfaced while checking an unverified claim ("AMZN 2026-08-18 conflicting-source
observations") from an unrelated, since-retracted draft. The claim's substance checked out;
its scope was wrong — this is not an AMZN-specific anomaly.

---

## Finding

**All seven of the CEDEAR pairs implicated in `DEFECT-F033-shared-driver-mechanism.md`** (MU,
MSFT, AMD, MELI, QQQ, AMZN, NU) **carry two irreconcilable value regimes on the same calendar
date, 2026-08-18, from two different import runs on the same `provider_assignment`:**

- **One observation at 13:30 UTC**, from an import run created **2026-08-18 16:25–16:26 UTC**,
  `trigger_type = MANUAL`, at the **old (large) scale** — consistent with the F-033-era values
  documented in the original defect filing.
- **Six further observations at 14:00–19:00 UTC**, from a *different* import run created
  **2026-08-19 13:04–13:05 UTC**, `trigger_type = SCHEDULED`, at a **new, much smaller scale**
  — consistent with the post-2026-08-19 values used throughout `FULL_REVERIFICATION_
  2026-08-19.md` and `RATIO_DIAGNOSIS_2026-08-19.md`.

**Both regimes are stored under the same `provider_assignment_id`, the same series, and the
same nominal calendar date.** This is the actual transition event between the two data
states this project has been characterizing as "before" and "after" 2026-08-19 — captured
directly in the observation table, not inferred.

## Magnitude per pair

| Pair | Old-regime value (13:30, `MANUAL`, `import_run` id) | New-regime value (14:00, `SCHEDULED`, `import_run` id) | Ratio (old/new) |
|---|---|---|---|
| AMZN | 263,993.13 (58234) | 2,870.00 (69660) | **~92×** |
| MELI | 1,825,165.05 (58231) | 23,800.00 (69657) | **~77×** |
| QQQ | 776,695.56 (58233) | 56,725.00 (69659) | **~13.7×** |
| MSFT | 487,212.57 (58229) | 25,340.00 (69655) | **~19.2×** |
| AMD | 483,696.05 (58230) | 75,200.00 (69656) | **~6.4×** |
| MU | 950,617.76 (58228) | 295,900.00 (69654) | **~3.2×** |
| NU | 14,562.82 (58232) | 11,540.00 (69658) | **~1.26×** |

**Per-pair magnitude is not uniform** — it ranges from ~1.26× (NU) to ~92× (AMZN). This is
itself informative: a single global rescaling (e.g., a currency-basis or units fix applied
uniformly) would produce the same ratio across all seven; a *different* ratio per pair is more
consistent with each series having its own broken or since-corrected per-series scale factor —
the same picture `RATIO_DIAGNOSIS_2026-08-19.md` already built independently, from a different
angle (cross-pair return correlation, not a same-date discontinuity).

## Contrast: the six unaffected CEDEAR pairs show no such discontinuity

Checked the same date for BABA, BIDU, UBER, GLD, AZN, BBD: each has **only one** value regime
on 2026-08-18, all from a single import run, no MANUAL/SCHEDULED split, no scale jump.

| Pair | Obs on 2026-08-18 | Import runs involved | Discontinuity? |
|---|---|---|---|
| BABA | 6 | 1 (69647) | No |
| BIDU | 6 | 1 (69648) | No |
| UBER | 6 | 1 (69650) | No |
| GLD | 6 | 1 (69642) | No |
| AZN | 1 | 1 (69693) | No |
| BBD | 1 | 1 (69694) | No |

**This discontinuity is confined exactly to the seven pairs already flagged in
`DEFECT-F033-shared-driver-mechanism.md`, and to no others.**

## Relationship to the filed HistFinTS defect

This is new, more specific evidence for the same underlying issue, not a separate defect. It
pinpoints:

1. **The exact timestamp of the regime change** for all seven pairs simultaneously
   (2026-08-19, ~13:04–13:05 UTC) — a single ~90-second window in which a `SCHEDULED` import
   run rewrote the going-forward scale for every one of the seven pairs at once, while leaving
   the prior `MANUAL` run's observation from the day before in place rather than superseding
   it.
2. **That the transition is per-pair-different in magnitude**, not a uniform rescaling —
   consistent with the shared-driver hypothesis in the filed defect (one input, per-series
   multiplier), where the multiplier itself apparently changed between the two runs, rather
   than the mechanism being replaced.
3. **A data-integrity question the filed defect did not raise**: two `MANUAL`-vs-`SCHEDULED`
   import runs, roughly 21 hours apart, both wrote observations for the *same calendar date*
   under the *same provider assignment* without either superseding or reconciling the other.
   Both rows remain in the table. Any calculation that does not explicitly select "most recent
   import run per date" (as this project's day-dedup convention already does, but not every
   past script did) would silently mix an old-scale and new-scale value for the same date.

## Recommendation

This finding should be **appended to `DEFECT-F033-shared-driver-mechanism.md`** (already filed
with HistFinTS) rather than filed separately — it is the same defect, observed at finer
resolution, and materially strengthens the case that a shared/automated process is producing
these seven series' values rather than independent per-instrument fetches. It also adds a
second, distinct question for HistFinTS: whether `MANUAL` and `SCHEDULED` import runs for the
same provider assignment are expected to coexist for the same calendar date without
reconciliation, since that is a general ingestion-pipeline question beyond these seven series.

**No threshold, ratio, or admissibility conclusion is drawn here.** This is evidence only.
