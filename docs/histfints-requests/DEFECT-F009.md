# DEFECT — Incremental import leaves a permanent, unmarked scale discontinuity at splits

**ID:** F-009 · **Severity:** High · **Status:** dormant, not yet observed in production
**Component:** `application/import_service.py` (range selection) · `providers/yahoo_finance.py`
**Filed:** 2026-08-15 · **Raised from:** Research Workbench spec review

> **Scope note.** This is a defect report, not a feature request. It is deliberately
> filed separately from the adjustment-basis labeling request, which needs schema, a
> value per provider, and a backfill decision, and deserves its own timeline. Bundled,
> both get deprioritised together. This one stands on its own regardless of who ends up
> owning adjustment logic: **a store whose `observation.value` silently changes scale,
> with no correction row and nothing recorded, is broken as a store.**

---

## 1. Summary

`observation.value` is provider-adjusted, not raw. For Yahoo Finance it is
split-adjusted and dividend-unadjusted. Yahoo re-expresses its entire history onto the
current split basis at query time.

Incremental import fetches only a trailing window forward from the latest stored date;
historical rows are never re-fetched. Therefore a Series backfilled **before** a split
and tracked incrementally **through** it retains pre-split rows at the old scale while
post-split rows arrive already adjusted.

The result is a permanent discontinuity of exactly the split factor, with no marker, no
`correction` row, and no log entry. The series remains internally inconsistent
indefinitely.

---

## 2. Evidence chain

### 2.1 Values are split-adjusted (so the basis can shift under the store)

Series 33 (AAPL, Yahoo Finance, 6,694 daily bars, 2000–2026):

| `observed_at` | stored `value` |
|---|---|
| 2014-06-04 | 23.03 |
| 2014-06-05 | 23.12 |
| 2014-06-06 | 23.06 ← last session before the 7:1 split of 2014-06-09 |
| 2014-06-09 | 23.42 |

Published raw close on 2014-06-06 was ≈ 645.57. `23.06 × 7 × 4 = 645.68` — reconciles
only after backing out **both** the 2014 7:1 and 2020 4:1 splits. No discontinuity is
visible at either date.

The same arithmetic shows the values are dividend-*un*adjusted: a dividend-adjusted
series would sit 10–15% lower, near 20. Consistent with
`providers/yahoo_finance.py` reading `indicators.quote[0].close` rather than
`indicators.adjclose`.

### 2.2 The mechanism

`ImportService._determine_range()` — `application/import_service.py:183–200`.

Per its own docstring, an incremental import starts from the latest stored Observation
**minus that provider's `default_revalidation_window_days`**, with **zero look-back where
that field is unset**. Where no Observations exist yet, it starts instead from the Series'
`backfill_start_date`.

Two consequences follow directly:

- **The one-shot backfill is confirmed at the line level.** First import covers
  `backfill_start_date` onward; every subsequent import covers only the trailing window.
  Historical rows are never re-requested.
- **The look-back is per-provider and may be zero.** The window is not a fixed property of
  the system. For any provider with `default_revalidation_window_days` unset, no stored
  date is ever revisited at all — so `correction` can never fire for that provider under
  any circumstances, and the blind spot described in §2.3 is total rather than partial.

### 2.3 `correction` cannot detect it

All 13,302 `correction` rows ever recorded, every Series, every provider. Age of the
corrected observation (`detected_at − observed_at`):

| Age | Rows |
|---|---|
| 0 days | 7,114 |
| 1 day | 5,851 |
| 2 days | 325 |
| 3 days | 12 |
| 4+ days | **0** |

Oldest `observed_at` ever corrected anywhere in the database: 2026-08-04.

**The hard cliff at 4 days is the re-fetch window's edge, not a property of provider
behaviour.** `correction` compares a re-fetched value against a stored value for the
same date. Dates that are never re-fetched can never produce a correction. The
correction log's coverage is exactly the trailing window and nothing beyond it.

### 2.4 Why production looks clean today — survivorship

Every long-history Series in the store was backfilled *after* its splits had already
occurred. AAPL's `provider_assignment.created_at` is 2026-08-11, four days before
filing; its entire 26-year history arrived internally consistent in one shot, on the
current basis. No tracked Series has yet lived through a split.

The defect is **dormant, not absent.** It begins producing corrupt data the first time
a currently-tracked Series splits.

---

## 3. Reproduction (by construction)

The defect is unfalsifiable by observation of current data — every assignment in the
database was created within the last two weeks, so nothing has yet lived through a
triggering event. It must be forced:

### 3.1 Split case

1. Pick a Series with a known real split at date `S`.
2. Create the `provider_assignment` and backfill history ending at `S − 1`.
3. Run an incremental import covering `S + n`.
4. Assert the stored values on both sides of `S` are on the **same** scale.

Expected under the defect: rows before `S` remain at the pre-split scale, rows after
`S` arrive post-split, no `correction` row is written, and the ratio across the
boundary equals the split factor.

### 3.2 Revision case (same root cause, different trigger)

The same blind spot applies to any provider that restates history — notably FRED,
which revises payroll employment monthly, seasonally adjusted household-survey data at
the January benchmark, and GDP on a published schedule.

1. Set `series.backfill_start_date` back for a FRED-sourced Series.
2. Delete a chunk of recent observations.
3. Re-run `run_import` across that boundary.
4. Assert that an **already-stored** value is actually revisited rather than skipped.

This tests the mechanism rather than the calendar, and does not depend on a provider
revision happening to fall during the test.

> _[Fill in: chosen Series, split date, split ratio, observed values either side.]_

---

## 4. Impact

Wider than display. A 7:1 split injects a single-day return of −85.7% into the series.
That silently corrupts:

- realised volatility
- maximum drawdown
- CAGR and all annualised returns
- beta and correlation against any benchmark
- every normalised comparison chart crossing the boundary

No visual cue beyond the jump itself, and no audit trail. A consumer sees a
plausible-looking number that is simply wrong.

**Trigger frequency.** Because Yahoo's `close` is dividend-unadjusted, ex-dividend
dates do **not** trigger a rescale — only splits do. For US equities that is rare. For
this project's actual universe the relief is smaller: **CEDEAR conversion-ratio changes
and BYMA corporate actions fire considerably more often.**

*Basis for that claim:* CNV Normas, Título II, Capítulo VIII (as substituted by RG
1142/2026) requires CEDEAR issuers to report the conversion ratio **quarterly**, and a
ratio change triggers a Prospectus Supplement. Ratio changes also arise from purely local
causes — issuers halve unit prices by doubling the ratio when peso price levels rise —
with no corporate action on the underlying at all. A confirmed instance exists in this
project's own data: a clean ~2:1 step on 2024-01-24 in a CEDEAR whose US-listed underlying
moved −0.35% that day.

---

## 5. Candidate remedies

Not prescriptive; the trade-offs differ and the choice is the maintainers'.

| # | Remedy | Cost | Notes |
|---|---|---|---|
| R1 | Periodic **full-range re-fetch** per Series | Bandwidth, provider rate limits | Simultaneously detector *and* repair, with no schema change: a healthy Series produces ~zero corrections, a broken one produces a burst dated the same day. Makes history mutable by design — but logged mutation beats silent drift. Does not help provider-splice breaks. |
| R2 | **Parse and persist** the `events` payload already being requested | Small: one parse, one table | `providers/yahoo_finance.py:63` already sends `"events": "div,splits"`; `_to_records()` never reads `chart.result[0].events`. Gives real, provider-observed split dates and ratios instead of inferred ones. Captures go-forward only unless paired with a backfill pass. |
| R3 | Detect the discontinuity and refuse to serve across it | Consumer-side only | Fallback if neither of the above lands. Detects; does not repair. |

R1 and R2 are complementary: R2 supplies the ground truth, R1 supplies the sweep.

---

## 6. Out of scope for this report

- **Adjustment-basis labeling** — recording which basis applies per provider. A genuine
  feature request, filed separately.
- **Cross-provider convention mismatch** — the Yahoo (`quote[0].close`, split-adjusted)
  vs Alpha Vantage (`TIME_SERIES_DAILY`, unadjusted) splice. Related but distinct; not
  empirically confirmable in this database, since no Alpha Vantage data exists here.
- **Where adjustment logic should live.** Decided downstream of this report and
  independent of it.
