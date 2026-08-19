# Full Re-Verification — Database State as of 2026-08-19

**Date:** 2026-08-19
**Trigger:** a status document found outside the repository (`PROVISIONAL_CALIBRATION_STATUS_
2026-08-19.md`, since saved to `docs/`) asserted an admissibility list (AAPL, BABA, AMD, AMZN,
AZN, BBD) inconsistent with this project's verified findings. Rather than accept or reject that
claim on priors, the database was re-queried from scratch.
**Finding: the database has changed substantially since the last verification pass
(2026-08-18 evening). Both good and bad news. Nothing here is a threshold decision.**

---

## 1. What changed since 2026-08-18

- **11 new CEDEAR series added** at 2026-08-19 01:10 UTC: AstraZeneca (AZN), Banco Bradesco
  (BBD), EWZ, iShares MSCI EAFE (FXID), iShares Bitcoin Trust (IBIT), Johnson & Johnson (JNJ),
  Moderna (MRNA), Petrobras (PBR), Pfizer (PFE), TripAdvisor (TRIP), Vale (VALE).
- **Fresh import activity as recent as 2026-08-19 13:05–13:06 UTC** — the database was still
  receiving writes very close to this verification pass.
- Total observation count is now ~27.9M (was in the tens of thousands for the series this
  project has been working with — the increase reflects the platform's much broader universe,
  not specifically this project's cohort).
- The six previously-blocked new-CEDEAR pairs (MU, MSFT, AMD, MELI, AMZN, NU) each picked up a
  handful of additional observations (2923→2929/2930, NU 1176→1182).

---

## 2. F-033 status: **the machine-precision circularity is gone**

Re-ran the exact test that established F-033 (day-deduplicated implied-FX, internal relative
range across the six previously-blocked pairs) against current data.

| | 2026-08-18 (F-033 finding) | 2026-08-19 (this pass) |
|---|---|---|
| Six-pair (MU/MSFT/AMD/MELI/AMZN/NU) internal relative range | 2.25×10⁻¹⁶ (machine epsilon) | **13.3% mean, up to 743% max** |
| Interpretation | Six values were the same number to the last bit — provider-computed, not independent | Now economically-scaled variation — no circularity signature |

**The specific defect F-033 described — six pairs sharing one formula-derived value — is no
longer present in current data.** This is a genuine, positive change; it is not something this
verification pass caused or assumes without checking.

**What this does not mean:** it does not mean the six pairs are now *coherent* with each
other or with the rest of the cohort. See §3.

---

## 3. New finding: cross-sectional implied-FX values no longer cluster at all

Computing `implied_fx = CEDEAR_ARS / (underlying_USD × ratio)` for all 14 pairs with
substantial data, on the latest common date (2026-08-18):

| Pair | Implied FX | Pair | Implied FX |
|---|---|---|---|
| AAPL | 3.95 | AMD | 157.41 |
| AMZN | 10.96 | BABA | 175.34 |
| MELI | 13.21 | MU | 315.60 |
| GLD | 31.59 | AZN | 394.91 |
| MSFT | 52.57 | NU | 790.94 |
| QQQ | 78.99 | UBER | 791.59 |
| BIDU | 144.05 | BBD | 1587.17 |

**These should, in principle, all be estimating roughly the same quantity (an implied ARS/USD
rate) if every pair's `ratio` is correct and effective for this date.** They span **3.95 to
1,587 — a ~400× range.** Removing AAPL (which carries a known, previously-documented risk —
see below) still leaves a **145× range** among the remaining 13. This is not explained by
F-033's mechanism (already ruled out in §2) and is not something this project has previously
characterized. **It is a new, open finding, not yet diagnosed to a root cause.**

**One partial, already-known contributor: AAPL's ratio is very likely stale.** `series.ratio =
20` for AAPL is a constant, undated value — and this project's own standing record (**F-021,
D-015**, restated in `CLAUDE.md`: *"Never apply a CEDEAR ratio without checking its effective
date. A constant ratio is confirmed wrong for at least one real historical span (AAPL CEDEAR,
2024-01-24 step)"*) already established that AAPL's true ratio changed at 2024-01-24. This
calculation applied the current `series.ratio` value blindly to 2026-08-18 data — exactly the
mistake the standing rule warns against — and AAPL's implausible result (3.95, when every
other pair clusters in the tens-to-thousands range) is consistent with that known risk
materializing, not a new mechanism.

**AAPL's known issue does not explain the other 13.** No comparably documented effective-date
problem exists for the rest of this cohort, and the 145×-without-AAPL spread suggests either
(a) several other pairs' `ratio = 1.0` values are wrong or stale in the same way F-021 found
for AAPL, unverified individually, or (b) a different, not-yet-identified mechanism. **This
report does not diagnose which** — that is the next verification step, not something to guess
at here.

---

## 4. Provenance re-check — the good news holds

Re-verified per pair, which `provider_assignment` produced which observations:

- **AAPL, BABA, BIDU, UBER, GLD**: unchanged from the 2026-08-18 finding — 100% of history
  (all confined to 2026-05-29→2026-08-18) from the single live Yahoo `.BA` pathway. No
  synthetic backfill involved.
- **MU, MSFT, AMD, MELI, AMZN, NU, QQQ**: the recent window (56 obs each) is live; the deep
  2015–2026 history remains sourced from the `BACKFILL_*` pathway, exactly as found in the
  temporal/regime study. Unchanged — this pathway's independence is still unverified.
- **AZN and BBD are a new, positive data point**: their **entire** history (3,211 and 3,307
  observations respectively, back to 2013) comes from the **live** priority-1 `.BA` pathway —
  no `BACKFILL_*` observations at all for either series. If their cross-sectional
  inconsistency (§3) turns out to be a ratio problem rather than a provenance problem, these
  two pairs would be the first genuinely deep, live-fetched CEDEAR history this project has
  seen — directly relevant to the temporal-depth gap.

---

## 5. Reconciling the Desktop status document

The document's claimed admissible list (AAPL, BABA, AMD, AMZN, AZN, BBD) does not match this
project's verified population (AAPL, BABA, BIDU, UBER, GLD, QQQ) either before or after this
re-verification:

- **AMD and AMZN** no longer show F-033's specific circularity (§2) — so the specific reason
  they were excluded as of 2026-08-18 has changed. They are **not**, however, shown to be
  usable now either — §3's finding puts them inside the newly-discovered cross-sectional
  inconsistency along with almost every other pair, AAPL included.
- **AZN and BBD** exist and have substantial, cleanly-sourced live data (§4) — the document
  was not referencing nonexistent tickers, just data that postdates this project's last check.
  They are not yet verified admissible; they carry the same §3 cross-sectional problem as
  everything else.
- **BIDU, UBER, GLD, QQQ** — verified admissible as of 2026-08-18 — are absent from the
  document's list without explanation.

**Neither this project's 2026-08-18 six-pair list nor the Desktop document's six-pair list
should be treated as current.** Both predate or are inconsistent with the §3 finding, which
affects essentially the whole cohort.

---

## 6. Status, restated plainly

- **F-033 (machine-precision circularity): resolved**, confirmed by direct re-test.
- **A new, undiagnosed cross-sectional implied-FX inconsistency affects nearly every pair
  in the cohort**, AAPL/BABA/BIDU/UBER/GLD/QQQ included, not only the previously-blocked six.
- **AAPL's contribution is explained** (stale ratio, a known risk per F-021/D-015, now
  empirically confirmed to matter) — a concrete, actionable item: verify or correct AAPL's
  effective ratio before using it in any cross-pair calculation.
- **The other 12 pairs' spread is not yet explained.** This needs its own investigation —
  most plausibly starting with whether `ratio = 1.0` is actually correct and currently
  effective for each, the same category of question F-021 first raised for AAPL alone.
- **No admissibility list — this project's prior one or the Desktop document's — should be
  used for calibration work until §3 is resolved.**
- **Temporal-depth gap:** unchanged in most of the cohort, but AZN/BBD are a new, promising,
  genuinely-deep, live-sourced data point worth prioritizing once §3 is resolved for them.
- **No threshold selected, changed, or promoted.**

## 7. Suggested next step

Before any further calibration attempt: diagnose §3 per pair — check whether each pair's
`ratio` (and, for AAPL specifically, its known effective-date step) is current and correctly
applied, the same way the SECONDARY cohort's YPF ratio was diagnosed and corrected earlier.
This is a data-verification task, not a threshold decision, and does not require FDA/SE input
to begin.
