# Data-Gap Specification: What Is Required to Reopen V0 Dispersion Calibration

**Date:** 2026-08-18
**Requested by:** SE
**Nature of this document:** Evidence-requirement specification. **No minimum N, sample
size, or numerical threshold is proposed here.** This identifies what independent evidence is
missing; it does not decide how much would be "enough" — that is a domain judgment for FDA
once the identified gaps are closed and a real distribution can be examined.

---

## Starting point: what independence currently exists

Before specifying the gap, the current state needs to be precise, since the two available
CEDEAR cohorts fail for two different reasons — this affects what closes the gap.

| Cohort | Pairs | Independence status | Temporal coverage |
|---|---|---|---|
| New 7 (MU, MSFT, AMD, MELI, QQQ, AMZN, NU) | 6 of 7 | **Not independent** — F-033: bit-identical implied-FX to machine precision (`CALIBRATION_EVIDENCE_REOPENED_DISPERSION_2026-08-18.md`) | 2026-05-29→2026-08-18 only (2.5 months); deep 2015–2026 history exists in the DB but is equally affected by F-033 (confirmed in the same report) |
| New 7 | QQQ only | Independent (0.83%–10.24% deviation from the degenerate block, economically plausible) | Same 2.5-month window |
| Original 5 (AAPL, BABA, BIDU, UBER, GLD) | 5 of 5 | **Verified independent** in this pass — spot-checked underlying-FK values are genuinely distinct, daily-varying, and show no machine-precision circularity signature (see verification below) | 2026-05-29→2026-08-18 only; deep 2020–2024 history was configured (`backfill_start_date`) but is absent from the live database (2026-08-18 anomaly finding, unresolved, HistFinTS-side) |

**Net current usable independent cross-section: at most 6 series (original 5 + QQQ), all
confined to the same single 2.5-month window.** This is better than the 2 previously reported
for the new-7-only attempt, but the temporal problem is unchanged — nothing currently
independent has more than one regime of history live in the database.

---

## Gap 1: Additional eligible relationships — resolve, don't just add

The seven new CEDEARs are already-designated PRIMARY-cohort relationships; the gap is not
"find more tickers," it is **make the existing seven usable**:

- **F-033 resolution for six pairs** (MU, MSFT, AMD, MELI, AMZN, NU): their stored ARS values
  must be replaced with, or confirmed to already be, independently observed BYMA CEDEAR
  quotes — not values derived by formula from the underlying USD price. This is squarely a
  HistFinTS-side data question (how were these seven ingested, and does BYMA data for six of
  them actually exist anywhere upstream), not something Workbench can resolve by recomputation.
- **QQQ's provenance should be confirmed, not just accepted by default.** It is the one pair
  that doesn't show the F-033 signature, which is consistent with it being genuinely
  independent — but that has not been separately verified against a BYMA source; it has only
  been shown to *differ* from the other six. Absence of the circularity signature is necessary
  but not sufficient evidence of correctness.
- **Original 5's `underlying_series_id` FK should be spot-checked at the same rigor applied to
  the new 7** before being relied on further — this pass verified it for three sample dates
  per pair, not a full-population check.

No new tickers are proposed. The population that would close this gap already exists in the
`series` table; it needs its data verified or corrected, not expanded in count.

---

## Gap 2: Required independent market observations

For a cross-sectional dispersion statistic to be meaningful, each panel member on a given date
must be an observation that could, in principle, have come out differently from its peers —
i.e., sourced from an actual BYMA print, not derived from another series' value by a shared
formula. Concretely, before any pair is used as a calibration input, its inclusion needs:

1. A stored value traceable to a specific `import_run_id` whose provider/adapter path is
   confirmed to be a live BYMA (or equivalent) market fetch for that specific series — not a
   backfill/conversion job that computed the value from another series.
2. No shared derivation with any other panel member for the same date (the exact failure mode
   found in F-033 — this needs to be checked pairwise, not assumed absent just because a series
   "looks like" a market series).

This is a provenance-verification requirement, not a data-volume requirement — it applies
equally whether the eventual panel has 2 pairs or 20.

---

## Gap 3: Temporal coverage / regime diversity

The specification (`SPEC-panel-eligibility.md` §8.5) deliberately leaves `minimum_panel_depth`
and calibration sample size **unspecified as a number** — it is a parameter to be set by
calibration, not a precondition assumed in advance. This document follows that same
discipline and does not invent one. What the spec **does** already establish, and what this
project's other calibration work has already used as classification categories (not sample-
size minimums), are the structural boundaries a temporally adequate sample would need to span
in order to support the segmentation this project's own methodology calls for:

- The F-009 era boundary (pre/post ~2024, evidence-quality resolved vs. unresolved).
- The F-021 CEDEAR ratio-step boundary (2024-01-24), where applicable per pair.
- At least one full crisis/non-crisis regime pair (this project's own diagnostics have used
  pre-crisis / crisis / post-crisis calendar-year bands as the working segmentation, not as a
  minimum-count requirement).

The concrete gap: **zero currently-independent series carry data across more than one of
these boundaries.** Every independent series identified in this pass (original 5, QQQ) is
confined to the single post-2026-05-29 window. Closing this gap requires either (a) the
original 5's configured-but-absent 2020–2024 backfill being restored in the live database
(a HistFinTS-side question, already flagged as unresolved in the 2026-08-18 population-state
anomaly finding), or (b) sufficient live/independent history accumulating forward from the
current window, or (c) F-033 being resolved such that the new 7's existing 2015–2026 history
becomes usable, whichever arrives first. This report does not rank these paths or estimate
how long either would take — that is an operational question, not an evidence-definition one.

---

## Gap 4: Metadata / provenance prerequisites

1. **`underlying_series_id` integrity.** At minimum the six affected new-7 series need this FK
   corrected or their values need independent re-derivation; going forward, this FK should not
   be trusted without a value-level sanity check (as this and the prior report both had to do
   manually) — there is currently no automated guard against it pointing at a duplicate/derived
   series.
2. **ADR/CEDEAR representation ratios beyond `series.ratio`.** Spot-checking the original 5
   surfaced a related, previously unflagged gap: BABA and BIDU's *underlying* series are ADRs
   where each ADR represents **8 ordinary shares** (per the series label text), a
   representation ratio distinct from the CEDEAR-to-ADR `ratio` field (which is 1.0 for both).
   If BABA/BIDU are ever brought into a normalized implied-FX calculation alongside the CEDEAR
   ↔ direct-underlying pairs, this second ratio layer needs a documented, dated source — it is
   currently only visible as label text, not a structured field. This mirrors the standing
   constraint (`CLAUDE.md`, D-015/F-021) that no ratio may be applied without a checked
   effective date; an undocumented ADR representation ratio is the same category of risk.
3. **A provenance marker distinguishing "independently observed" from "derived/backfilled"
   at the observation or import-run level.** Every verification in this and the prior three
   reports has had to be done by manual spot-check (comparing raw values, checking for
   floating-point identity) because no existing field records how a stored value was produced.
   Formalizing this — even as a simple flag on `import_run` — would make future calibration
   attempts self-verifying instead of requiring this kind of forensic pass each time.

---

## Explicitly not addressed here

- No minimum number of independent pairs is proposed.
- No minimum number of dates, regimes, or years is proposed.
- No timeline or priority ordering across Gaps 1–4 is proposed.
- No statement is made about whether CV 0.167, or any other value, would be validated once
  these gaps close — that determination requires the actual resulting distribution, which does
  not exist yet.

These are FDA/SE calls once the underlying evidence exists, not conclusions this report is
positioned to draw from an admittedly insufficient sample.
