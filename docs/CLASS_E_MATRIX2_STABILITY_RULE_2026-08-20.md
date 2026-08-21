# Class-E Identity-Evidence Study — Matrix 2 Under the Stability Rule

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: read-only. No mutation, staging, D execution, reassignment, deletion, or
provenance modification. The seven previously adjudicated Class-C rows are inside the
leading-edge population characterized below and are marked closed, not reopened, per
instruction.**

---

## Stability rule and evidence watermark

**Rule applied**: an observation is treated as stable when its `observed_at` is strictly
older than its own series' current `MAX(observed_at)` — consistent with HistFinTS's verified
finding that scheduled imports have no revalidation window and append only at the leading
edge. The single most-recent observation per series is therefore excluded from every
comparison below, since it is the one row not yet "sealed" by a subsequent append.

**Watermark recorded for reproducibility** (queried at the time of this study; a rerun
against a later database state should expect these to have advanced):

| Series role | Series id (MU exemplar; identical pattern all seven pairs) | `MAX(observed_at)` at time of study |
|---|---|---|
| Referrer (CEDEAR) | 11323 | 2026-08-19T19:00:00+00:00 |
| Current target | 11342 | 2026-08-19T20:00:00+00:00 |
| Proposed target | 6672 | 2026-08-20T13:30:00+00:00 |

(QQQ's proposed target, 8193, differs: `2026-08-19T13:30:00+00:00` — one day behind its six
siblings; noted, not investigated further here.)

---

## Part A — 18,315 shared historical timestamps, re-verified under the stability rule

| Pair | Stable pre-transition common dates (referrer vs. current target) | Mismatches |
|---|---|---|
| MU | 2,866 | 0 |
| MSFT | 2,866 | 0 |
| AMD | 2,866 | 0 |
| MELI | 2,866 | 0 |
| NU | 1,119 | 0 |
| QQQ | 2,866 | 0 |
| AMZN | 2,866 | 0 |
| **Total** | **18,315** | **0** |

**Confirms exactly, under the stability rule, the previously-stated fact**: 18,315 shared
historical timestamps (2015-01-02 → 2026-05-27, the day before the transition) are
value-identical between referrer and current target with zero exceptions. This population is
preserved as-is — not re-characterized, not reopened.

---

## Part B — The leading-edge population ("~400"), two distinct ratio measures kept separate

Two different ratios were computed against the same leading-edge (post-2026-05-28) window,
both under the stability rule. They answer different questions and are reported separately to
avoid conflating them, as the prior draft of this analysis risked doing.

### B.1 — current target vs. proposed target (both USD; the "representation difference" measure)

| Pair | Stable common dates | Ratio min | Ratio median | Ratio max |
|---|---|---|---|---|
| MU | 58 | 0.9939 | 0.9999 | 1.0018 |
| MSFT | 58 | 0.9957 | 1.0000 | 1.0048 |
| AMD | 58 | 0.9966 | 1.0000 | 1.0143 |
| MELI | 58 | 0.9990 | 1.0000 | 1.0013 |
| NU | 58 | 0.9975 | 1.0000 | 1.0017 |
| QQQ | 57 | 0.9986 | 1.0000 | 1.0002 |
| AMZN | 58 | 0.9908 | 0.9999 | 1.0023 |
| **Total** | **405** | **0.9908** | **1.0000** | **1.0143** |

**Provider identifiers (both sides)**: Yahoo Finance for both current and proposed target, on
all seven pairs (confirmed in Matrix 1). Current target is fetched hourly (`configured_
interval = 1h`); proposed target daily (`1d`).

**Characterization, per instruction**: this is a **representation/source-population
difference, not 400 historical data errors.** The ratio distribution clusters tightly around
1.0000 (median exactly 1.0000 or 0.9999 on every pair), with a spread of roughly ±0.5–1.4%
consistent with an hourly feed and a daily-close feed sampling the same underlying market at
different points in the trading session — not with a deeper data defect. **No financial
meaning (FX, denomination, ADR ratio, or otherwise) is assigned to this ratio** — it is
reported as a sampling-timing artifact, pending DFA adjudication if a stricter interpretation
is ever required.

**Count reconciliation**: 405, not exactly 400 — reported as obtained under the stability
rule, not adjusted to match. The earlier, non-watermarked pass (`EVIDENCE_MATRICES_B_D_
CLASSC_IDENTITY_2026-08-20.md`) reported 406/338 at a one-cent tolerance; the difference
reflects the stability-rule exclusion of each series' single most recent row, not a
substantive change in finding.

### B.2 — referrer (CEDEAR) vs. proposed target (ARS/USD; the implied-FX-like measure)

| Pair | Stable common dates | Ratio min | Ratio median | Ratio max |
|---|---|---|---|---|
| MU | 58 | 314.37 | 1009.50 | 1010.48 |
| MSFT | 58 | **52.53** | 1009.50 | 1010.48 |
| AMD | 58 | 157.41 | 1009.50 | 1010.48 |
| MELI | 58 | 13.08 | 1009.50 | 1010.48 |
| NU | 58 | 785.08 | 1009.50 | 1010.48 |
| QQQ | 57 | 78.99 | 1055.00 | 1113.40 |
| AMZN | 58 | 10.92 | 1009.50 | 1010.48 |

**56 of 58 dates, for six of the seven pairs, cluster tightly at ~1008.5–1010.5** — a stable,
plausible implied ARS/USD level consistent with this project's independently-derived FX
context for this period. **This is the "ratio distribution" requested; no financial meaning
(i.e., that ~1009 is "the" ARS/USD rate) is asserted here** — it is reported as an observed
statistical clustering, pending DFA adjudication.

**MSFT's 52.53–52.57 values, isolated as instructed, not generalized**: these occur on
**exactly two dates — 2026-08-18 and 2026-08-19** — and only on those two. Every other date in
MSFT's 58-day window sits in the ~1008.5–1010.5 cluster with the other five. **These two dates
are the already-documented, already-explained same-date scale-discontinuity transition**
(`SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md`) — this time visible on the *referrer* series'
own values, not (as previously documented) on a current-target series. This is reported as a
recurrence of a known, characterized mechanism, not a new unexplained anomaly. The same
two-date pattern was checked and confirmed present in MU, AMD, MELI, NU, and AMZN as well
(each shows its own minimum at exactly these two dates) — **isolated to those two dates for
all six pairs showing it, not generalized into a population-wide "400 ratios are unreliable"
claim.**

**QQQ's separate profile, restated, not re-explained here**: QQQ's median (1055.00) and range
extend beyond the other six's tight cluster even outside the two-date discontinuity —
consistent with QQQ's already-documented, still-unresolved separate-driver status
(`RECONCILIATION-F033-2026-08-19.md`). Not investigated further in this pass.

---

## The seven Class-C rows, inside this population — explicit disposition marker

**2026-05-28 is one of the dates in the leading-edge population above** (the first date in
both B.1 and B.2's live windows). The seven previously-adjudicated Class-C rows (one crossed
observation per target, on this date, from the seven-pair episode) exist in the raw
`observation` table on this date, alongside the legitimate rows this study's day-level
comparison actually uses (day-dedup selects the last observation of the day, which is the
legitimate `SCHEDULED`-run row, not the Class-C crossed row, for 2026-05-28 on every target
except AAPL — see `CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md` Part 3 for the AAPL exception).

**Explicit marker, per instruction**:

> **The seven Class-C rows (seven-pair episode, 2026-05-28): verified value-correct /
> attribution finding accepted — disposition closed. Not reopened. Not reclassified by
> appearing within this Matrix-2 population or any ratio computed above.**

Nothing in Part B's ratio computations reclassifies, re-evaluates, or depends on these seven
rows specifically — they are not the rows the day-level comparison selects for 2026-05-28 on
six of the seven targets, and where they are adjacent (AAPL's interleaved case), they remain
untouched by this study.

---

## Identity taxonomy — continuity with the population study, not restated in full

The four-way distinction (same issuer / same financial instrument / related-but-distinct
instruments / unresolved identity) and the eleven-candidate population were established in
`CLASS_E_IDENTITY_EVIDENCE_POPULATION_STUDY_2026-08-20.md` and are **not re-derived here**.
Matrix 2's evidence (Parts A and B above) is **value-level and date-level**, not
entity-identity evidence — it does not move any of the eleven candidates between taxonomy
categories, and this study does not attempt to. Specifically:

- Part A's zero-mismatch finding reinforces (does not newly establish) the same-instrument
  classification already given to Groups 5–11 (the seven D-contingent candidates) in the
  population study.
- Part B.1's tight, small-spread ratio is consistent with, but does not by itself prove,
  same-instrument identity — sampling-timing differences would look similar whether or not
  the two series are literally the same security, so this is corroborating, not decisive,
  evidence, and is presented as such.
- Part B.2 does not bear on any of the eleven candidates' identity assessment at all — it
  characterizes the referrer/proposed relationship, not the current-target/proposed-target
  relationship the population study's identity work is about.

---

## Standing separations, restated

- **The four present-state orphan candidates (Groups 1–4) and the seven D-contingent
  candidates (Groups 5–11) retain their separate statuses**, unchanged by anything in this
  document. The seven D-contingent candidates remain **not active** Class-E candidates until D
  executes.
- **D is not executed, staged, or brought closer to execution by this document.**
- **No mutation, reassignment, deletion, or provenance modification of any kind was performed
  or proposed.**

---

## What this document does not do

- Does not authorize or execute D.
- Does not resolve or reclassify the seven Class-C rows.
- Does not assign financial meaning to any ratio reported.
- Does not extend or re-derive the eleven-candidate identity taxonomy.
- Does not investigate QQQ's separate-driver status further.
- Does not propose repair SQL.
