# Ratio Diagnosis — PRIMARY Cohort, 2026-08-19 Cross-Sectional Spread

**Date:** 2026-08-19
**Follows:** `FULL_REVERIFICATION_2026-08-19.md` (found F-033's exact-value circularity
resolved, but a new ~400× cross-sectional implied-FX spread across the cohort, undiagnosed)
**Nature of this document:** Diagnostic finding. **No ratio is corrected in the database. No
threshold is selected, changed, or promoted.** Candidate ratio values below are empirical
estimates requiring authoritative confirmation (CNV/BYMA or equivalent), not applied fixes —
the same discipline this project has held to since F-021/D-015 (never apply a ratio without
checking its source and effective date).

---

## Method

Two, not one, diagnostic questions were separated, because they have different fixes:

1. **Is a pair's day-over-day *movement* correlated with its peers?** A wrong-but-constant
   ratio does not break this — dividing by any constant preserves % change. Near-zero or
   perfect (1.00) correlation both indicate something other than a simple ratio error.
2. **Is a pair's *level* (median implied FX over the window) consistent with its peers?** This
   is what a ratio error actually breaks, and what a corrected ratio would fix.

Computed on the 53 dates common to all 13 non-AAPL substantially-populated pairs
(2026-05-29 → 2026-08-18, live-fetch data only), `implied_fx = CEDEAR_ARS / underlying_USD`
(ratio = 1, i.e. no ratio applied yet — the point is to measure what ratio *would* be needed).

---

## Finding A: seven pairs show perfect return correlation — not a ratio problem

MU, MSFT, AMD, MELI, QQQ, AMZN, NU show **pairwise day-over-day correlation of exactly +1.00
with each other**, unchanged from the F-033-era pattern despite the exact-level circularity
(§2 of `FULL_REVERIFICATION_2026-08-19.md`) no longer being present.

**This is the more precise diagnosis of what actually happened between 2026-08-18 and
2026-08-19: the seven pairs' data-generation mechanism appears to still derive all seven from
one shared daily driver — only the per-pair scale factor changed from "identical" (producing
F-033's exact-value tie) to "different but still fixed" (producing today's non-degenerate
levels with still-perfect correlation).** A ratio correction cannot fix this — correlation of
returns is ratio-invariant by construction. Whatever generates these seven series' daily
movement needs to be investigated at the source (the same synthetic/backfill-adjacent process
implicated in F-033), not treated as a metadata/ratio gap.

**This is an escalation of F-033, not a resolution.** F-033's specific symptom (bit-identical
levels) is gone; its underlying mechanism (all seven driven by one process) is not.

---

## Finding B: six pairs show genuine independent behavior, with likely wrong or undocumented ratios

BABA, BIDU, UBER, GLD, AZN, BBD show correlations ranging **+0.04 to +0.91** — high in some
pairs (BABA/GLD 0.91, BABA/UBER 0.81), moderate in others, weak for AZN specifically. This
pattern — correlated-but-not-identical, varying in strength — is what genuinely independent
CEDEARs subject to a shared macro factor (real ARS/USD movement) and idiosyncratic per-name
noise should look like. **No exact-tie signature; not diagnosed as circular.**

**Each of these six pairs is also internally very stable over time** — the coefficient of
variation of each pair's own implied-FX level across the 53-day window is 2.0%–2.4% for all
six. A pair whose *ratio* is simply wrong holds still at a wrong level; this is exactly that
signature, not noisy/unreliable data.

**Empirical scale factors, relative to a BABA/BIDU reference** (the two names this project
has the longest independent verification history for — D-016/D-017 cross-pair coherence,
established well before this session):

| Pair | Median implied FX (ratio=1) | Scale factor vs. reference | Candidate ratio |
|---|---|---|---|
| BABA | 174.23 | 1.10× | ~1 (reference) |
| BIDU | 142.43 | 0.90× | ~1 (reference) |
| **UBER** | 784.66 | **4.96×** | **~5** |
| **GLD** | 31.40 | **0.20×** | **~0.2 (= 1/5)** |
| AZN | 392.01 | 2.48× | ~2.5 |
| **BBD** | 1,564.07 | **9.88×** | **~10** |

**Three of these (UBER≈5, GLD≈0.2, BBD≈10) are close enough to clean round numbers to be
credible candidates**, in the same way YPF's empirically-derived ratio=10 turned out to be
exactly 10, not merely close. **GLD's candidate (0.2 = 1/5) and UBER's (5) are reciprocals of
each other** — worth noting as a pattern, not yet explained: it may indicate a
direction/convention error (CEDEARs-per-share vs. shares-per-CEDEAR) affecting one or both,
rather than two independent ratio facts. **AZN's 2.48 is not clean** and is reported with
lower confidence.

**None of these candidates are applied.** `series.ratio` is not modified by this document. Per
the standing project rule, a candidate ratio needs an authoritative source and effective date
before use — exactly what was missing for AAPL (F-021) and for YPF before its correction.

---

## Finding C: AAPL — already diagnosed, not re-litigated here

AAPL's implausible implied-FX value (3.95) is attributable to `series.ratio = 20`, a constant,
undated value this project already knows is wrong post-2024-01-24 (F-021, D-015). No new
diagnosis is needed; the existing finding stands and should be resolved the same way as
Finding B's candidates — authoritative, dated ratio source required.

---

## Summary table

| Pair | Diagnosis | Action implied |
|---|---|---|
| MU, MSFT, AMD, MELI, QQQ, AMZN, NU | **Not a ratio problem** — perfect return correlation persists; shared-driver mechanism still active | Investigate data-generation source (escalated F-033), not fixable by ratio correction |
| BABA, BIDU | Consistent with each other; likely already correctly ratioed | No action; retain as reference |
| UBER, GLD, BBD | Independent, stable, wrong level; clean candidate ratios found (5, 0.2, 10) | Candidates require authoritative confirmation before use |
| AZN | Independent, stable, wrong level; candidate ratio (2.5) not clean | Requires authoritative confirmation; lower confidence |
| AAPL | Already diagnosed (F-021/D-015) | Requires authoritative, dated ratio; not new work |

---

## What this changes about calibration readiness

- **The cohort splits into two categories that need different remediation**, not one uniform
  "fix the ratios" task. Finding A's seven pairs cannot be made usable by any ratio work.
- **BABA and BIDU remain the most trustworthy pair-level evidence in the cohort** — consistent
  with each other, no circularity signature, no ratio anomaly detected.
- **No pair is newly certified admissible by this document.** Diagnosis only; the temporal-
  depth and independent-evidence gaps recorded in `CALIBRATION_DATA_GAP_SPECIFICATION_
  2026-08-18.md` and `PRIMARY_TEMPORAL_REGIME_EVIDENCE_STUDY_2026-08-18.md` are unaffected.
- **No threshold selected, changed, or promoted.**
