# Temporal / Regime Evidence Study — Six Admissible PRIMARY Pairs

**Date:** 2026-08-18
**Requested by:** SDT Workbench
**Scope:** the six PRIMARY-cohort CEDEAR pairs not blocked by F-033 — AAPL, BABA, BIDU, UBER,
GLD (original cohort, independence spot-verified earlier) and QQQ (the one new-CEDEAR pair
whose values do not carry the six-way circularity signature). The other six new-CEDEAR pairs
(MU, MSFT, AMD, MELI, AMZN, NU) remain excluded per F-033 and are not part of this study.
**Nature of this document:** Evidence inventory. **No minimum number of years, dates, or
observations is proposed as a requirement — this establishes what evidence currently exists
and characterizes the gap, per the directive not to invent a threshold.**

---

## 1. Usable observation date ranges

Every observation in the database was queried directly per series, then cross-checked against
which `provider_assignment` produced it (§5), since raw date range alone does not establish
usability.

| Pair | All stored obs | Date range (all) | Live-fetch obs (priority-1, `.BA`) | Date range (live) |
|---|---|---|---|---|
| AAPL | 67 | 2026-05-29 → 2026-08-18 | 67 (100%) | 2026-05-29 → 2026-08-18 |
| BABA | 67 | 2026-05-29 → 2026-08-18 | 67 (100%) | 2026-05-29 → 2026-08-18 |
| BIDU | 67 | 2026-05-29 → 2026-08-18 | 67 (100%) | 2026-05-29 → 2026-08-18 |
| UBER | 65 | 2026-05-29 → 2026-08-18 | 65 (100%) | 2026-05-29 → 2026-08-18 |
| GLD | 132 | 2026-05-29 → 2026-08-18 | 132 (100%; intraday granularity, see §4) | 2026-05-29 → 2026-08-18 |
| QQQ | 2,929 | 2015-01-02 → 2026-08-18 | 62 (2.1%) | 2026-05-29 → 2026-08-18 |

**Five of six pairs have no data outside the 2026-05-29 → 2026-08-18 window at all.** QQQ
nominally has 11 years of additional history, but 97.9% of it did not come from the live
fetch pathway (§5) — its usability is not established by date range alone.

**Net finding: the only period with unambiguously live-fetched observations, across all six
pairs, is 2026-05-29 → 2026-08-18 — roughly 2.5 months, ~55–67 trading days per pair.**

---

## 2. Coverage against the project's existing structural/regime boundaries

Checked against the boundaries already established and used elsewhere in this project's
diagnostics (F-009 era split, F-021 CEDEAR ratio-step date, and the crisis/regime-year bands
used throughout the calibration work):

| Boundary | Date | Falls inside the live-data window? |
|---|---|---|
| F-009 era split (reconciliation status pre/post) | ~2024 | No — entire window is post-2024, single side of the boundary |
| F-021 CEDEAR ratio-step (AAPL) | 2024-01-24 | No — entire window is post-step, single side |
| Pre-crisis / crisis regime boundary | 2022-01-01 | No — window starts 2026-05-29 |
| Crisis / post-crisis regime boundary | 2024-01-01 | No — window starts 2026-05-29 |
| COVID event window | 2020-03 to 2020-06 | No overlap |
| ARS crisis event window | 2022–2023 | No overlap |

**None of the six existing structural boundaries this project uses for segmentation fall
inside the live-data window for any of the six pairs.** The entire usable sample sits on one
side of every boundary simultaneously (post-2024, post-ratio-step, post-crisis-per the
project's own regime labels). There is no boundary crossing to observe, and therefore no
segmentation by structural period is possible from live data alone.

---

## 3. Ordinary-baseline vs. structural-event vs. evidence-quality periods

Because the live window contains no boundary crossing, this three-way split collapses for the
six pairs' current live evidence:

- **Ordinary-baseline period:** the entire 2026-05-29 → 2026-08-18 window, for all six pairs.
  No sub-period within it is distinguishable as different in kind from the rest by any
  existing project classification.
- **Structural-event period:** none present. No ratio step, corporate action, or classified
  crisis event falls inside the window for any of the six pairs.
- **Evidence-quality period:** uniformly `evidence-quality:resolved` (post-2024, per the F-009
  convention used elsewhere) for all observations in the window — a favorable classification,
  but one that applies to 100% of the sample, so it does not provide internal contrast either.

**This is a single, undifferentiated period.** The three-way classification that has been
useful elsewhere in this project (distinguishing ordinary/structural/quality-flagged
sub-periods) has nothing to operate on here — not because the classification failed, but
because the sample itself does not span more than one classification cell.

---

## 4. Missing / stale intervals

Gaps computed on the live-fetch observations only (the only evidence-grade dates):

| Pair | Live obs | Gaps | Max gap | P95 gap | Mean gap |
|---|---|---|---|---|---|
| AAPL | 57 dates | 56 | 4d | 3d | 1.45d |
| BABA | 57 dates | 56 | 4d | 3d | 1.45d |
| BIDU | 57 dates | 56 | 4d | 3d | 1.45d |
| UBER | 55 dates | 54 | 4d | 3d | 1.50d |
| GLD | 55 dates | 54 | 4d | 3d | 1.50d |
| QQQ | 56 dates | 55 | 4d | 3d | 1.47d |

Uniform and unremarkable — consistent with ordinary weekday/holiday spacing, matching the
staleness profile already established for this cohort elsewhere in this project. No pair
shows an outlier gap within the live window.

**GLD carries an additional, separate data-quality issue inside this window**, already
identified and corrected for in prior work: multiple intraday observations on single calendar
dates (up to 73 rows on one date), inconsistent with the daily granularity of its five peers.
This does not change the date-range finding above, but affects any per-date aggregation using
GLD without day-deduplication (documented previously in `CALIBRATION_EVIDENCE_12PAIR_COMPLETE_
2026-08-18.md`, Part 0c).

**Missing interval, restated plainly:** every date from each pair's `backfill_start_date`
(2020-01-01 for AAPL, 2020-03-12/13 for BABA/BIDU, 2022-07-26 for UBER, 2024-12-17 for GLD —
per `series.backfill_start_date`) up to 2026-05-28 is absent from the live-fetch evidence
entirely. This is not a gap within a distribution — it is the entire pre-window history for
five of six pairs.

---

## 5. Independence verification, per period and per provider

This is the section that most changes the picture from a simple date-range inventory.

### AAPL, BABA, BIDU, UBER, GLD

Every stored observation, for all five pairs, across their entire history, comes from exactly
one `provider_assignment`: **priority 1, Yahoo Finance, `"{TICKER}.BA"` identifier,
`SPLIT_ADJUSTED` basis.** There is no second data source, no backfill pathway, and no
synthetic/derived provider assignment contributing any observation to these five series.
**Every observation these five pairs have is, by provenance, on equal footing — a live fetch,
not a derived value.** (This does not by itself certify the *value* is a genuine BYMA trade
print rather than a provider-side computed quote — that determination, made for the new-7
cohort via the machine-precision test in F-033, was not re-run here since these five already
passed an earlier spot-check for economically-scaled, non-degenerate cross-pair variation.)

### QQQ

QQQ's evidence is **not uniform across its own history.** The 62 live-fetch observations
(2026-05-29 → 2026-08-18) share the same provenance as the other five. **The 2,867
observations spanning 2015-01-02 → 2026-05-28 come exclusively from `provider_assignment`
priority 3, provider "BYMA," identifier `"BACKFILL_QQQ"`** — the same synthetic backfill
mechanism identified in F-033 as producing the six circular new-CEDEAR pairs' deep history.
**QQQ's deep history not showing the F-033 machine-precision signature establishes only that
it was not derived by the same shared-rate formula as those six pairs — it does not establish
that `BACKFILL_QQQ` is a genuine independent BYMA market observation.** No positive evidence
of independent sourcing exists for QQQ's pre-2026-05-29 data; this remains exactly the open
item flagged in `CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md` §Gap 1 ("QQQ's provenance
should be confirmed, not just accepted by default").

**Consequence:** QQQ's evidence-grade, provenance-clean observation range is **the same
2026-05-29 → 2026-08-18 window as the other five**, not its full 2015–2026 span. Its deep
history cannot currently be counted as independent market evidence without further
verification of what `BACKFILL_QQQ` actually is.

### A note on unused provider assignments

All six pairs (and several other new-cohort series) carry a fourth, `priority=4`,
`provider="MERVAL"` assignment, none of which have produced any observation for any of the six
pairs studied here. Recorded for completeness; not a current evidence source.

---

## 6. What portion is usable for a primary calibration population

**Usable, with verified independent provenance: the 2026-05-29 → 2026-08-18 window, for all
six pairs, uniformly** — approximately 55–67 observations per pair, ~2.5 months, single
regime, no structural-boundary crossing, evidence-quality classification uniform
(`resolved`) across the entire sample.

**Not usable as independent evidence at this time:** QQQ's pre-2026-05-29 history (2,867
observations, 11+ years) — provenance unverified, same synthetic pathway as the F-033-blocked
pairs, despite not sharing their specific circularity signature. Five pairs' configured
backfill history (2020–2024 per pair) — absent from the database entirely, not merely
unverified.

**This confirms, with the provenance question now settled per pair rather than assumed, the
same substantive gap already recorded in `CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md`
and `CALIBRATION_REOPENED_PROVENANCE_CORRECTED_2026-08-18.md`: six pairs, one regime, no
structural-boundary coverage.** This study adds two things the prior documents did not have:
(a) an explicit per-pair, per-provider provenance trace for all six admissible pairs, not
only the new-7 cohort, and (b) the specific finding that QQQ's apparent temporal depth is not
currently usable evidence, closing (in the negative direction) the "QQQ's provenance should be
confirmed" open item from the data-gap specification.

**No minimum number of years, dates, or regimes is proposed here as a requirement.** What is
established is only this: right now, the admissible PRIMARY population has evidence-grade
coverage of one regime, and the one pair that appeared to offer more (QQQ) does not currently
have verified independent evidence beyond that same regime either. Whatever amount of
additional temporal coverage the financial domain eventually judges necessary, none of it
currently exists in verified form for any of the six pairs.
