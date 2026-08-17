# SPEC — Panel Eligibility and Diagnostics

**Status:** draft for review · **Version:** 0.1 · **Date:** 2026-08-15
**Governing decisions:** D-016 (panel principle) · D-017 (time-varying membership) · D-024 (this spec) · **D-037 (calendar and alignment)**

> **Update 2026-08-17 — D-037 removes Q-027 as a gate on this spec.** Cross-Series alignment is
> **intersection of common dates, pairwise, differencing *after* intersecting**, with per-date
> panel depth recorded as provenance; forward-fill is prohibited. The trading calendar is
> **derived from the store** by quorum over Series sharing a venue — authoritative for NYSE
> across all eras, reliable for BYMA from ~2019, and **unresolved before ~2015**, which must be
> declared rather than approximated. Needs no HistFinTS change. This spec remains gated on the
> Tranche 2 migration (coverage metadata) and on Q-061 (inclusion rules) only. **See also F-026:**
> zero-volume carried-forward phantom bars in Yahoo's deep `.BA` history will generate false
> ratio-change candidates on the longest-history pairs unless excluded from return series.

---

## 0. The requirement, in one sentence

> For every cross-Series analytical panel, define explicit eligibility rules covering
> minimum historical depth, observation coverage and applicable liquidity requirements,
> **evaluated as of each date in the analysis window rather than once at query time**. The
> resulting analysis must expose the number and proportion of eligible Series actually
> included, their historical coverage, the reasons for exclusion, and appropriate measures of
> cross-sectional dispersion. Where a longer analysis horizon reduces the number of
> qualifying Series, that reduction in panel breadth must be visible to the user rather than
> hidden by the aggregate result.

The emphasised clause is load-bearing. Without it a developer implements a single filter at
query time, which silently restricts a 20-year panel to Series that **survived** to today —
reintroducing the exact bias the final clause exists to surface. See §2.

---

## 1. Purpose

A panel is an explicitly-specified, reproducible set of Series or pairs used to derive an
aggregate result. This spec makes the selection an **object** rather than an implicit
consequence of whatever happened to be in the database at query time.

Two things follow from that, and they are the point of the spec:

- a result carries its own derivation (**P3**);
- the same parameters re-run later produce a *documented* difference rather than a silent
  one.

---

## 2. Core principle — eligibility is evaluated **as of each date**

> **Eligibility MUST be evaluated as of each observation date, never once at query time.**

Evaluated once against today's database, a 20-year panel contains only the Series that
**survived to today**. That is survivorship bias — and it would be introduced by the very
mechanism intended to warn about thin cross-sections. A warning reading *"18 of 137 Series
have sufficient history"* would be silently omitting those that died before acquiring it.

Consequences:

- **Membership varies through the series.** Confirmed empirically: the CEDEAR pair panel
  has three members on 2020-04-14 and six today.
- **Member count is an output, not a configuration.** It is reported per date.
- **`DELISTED_OR_DISCONTINUED` Series retain valid history.** Whether they participate is a
  survivorship decision and MUST be an explicit parameter, not an accident of which rows are
  `ACTIVE` when the query runs.

---

## 3. Two panel types

These are different objects and should not share one parameter set.

| | **Pair panel** | **Cross-section panel** |
|---|---|---|
| Scope | **V0** | Deferred (screeners, studies — V5) |
| Unit | a *pair*: local instrument ↔ underlying | a single Series |
| Purpose | derive implied FX; residual detects ratio change and staleness | screening, benchmarks, studies |
| Failure mode | one bad pair skews the rate | wrong cross-section skews the study |

---

## 4. Pair panel (V0)

### 4.1 Eligibility parameters

```
both_legs_present            # observations exist for both legs on the date
relationship_type            # CEDEAR | DUAL_LISTING | ADR — not interchangeable
ratio_known_as_of_date       # required for CEDEAR; N/A for dual listings
minimum_history              # per leg
minimum_observation_count    # per leg
staleness_policy             # max consecutive days without a new print
liquidity_requirement        # volume or turnover floor
adjustment_policy            # which bases are admissible; mixed bases barred
include_delisted             # survivorship switch
minimum_panel_depth          # below this, publish nothing
dispersion_threshold         # above this, suppress rather than caveat
```

Two of these deserve emphasis:

**`staleness_policy` is separate from `liquidity_requirement`.** A pair can pass any
reasonable volume bar while its prints lag — observed directly: one CEDEAR reached in a
single print what two others took fifteen trading days to reach, arriving at a level within
1.5% of theirs. It was liquid enough to trade and stale enough to drag a consensus toward
its own lagged level. Tradability and price freshness are different properties.

**`ratio_known_as_of_date`, not `ratio_known`.** Conversion ratios change by dated event. A
pair whose ratio is known *today* but unknown for the date being computed is **not
eligible** on that date. Applying a current ratio across a boundary where it did not hold is
the confirmed failure this parameter exists to prevent.

### 4.2 Result

```
rate                         # consensus across eligible pairs
n_included / n_excluded
exclusion_reasons            # {insufficient_history: 12, stale: 4, ratio_unknown: 2, ...}
member_list                  # resolved, stored with the result
dispersion                   # spread across members
per_member_residual          # deviation from consensus
```

`per_member_residual` is not decoration. Its **time signature** is the diagnostic:

| Residual behaviour | Interpretation |
|---|---|
| persistent | instrument-specific level change — likely a ratio change |
| transient, closes | staleness / illiquidity |
| common to all members | a real move in the underlying rate |

### 4.3 Suppression rules

- `n_included < minimum_panel_depth` → **publish nothing**, state why.
- `dispersion > dispersion_threshold` → **suppress**; do not display with a caveat. Above
  threshold the members disagree about what the rate is, and a caveated wrong number is
  worse than an absent one.
- A pair failing `ratio_known_as_of_date` is excluded **for that date only**, not for the
  whole series.

---

## 5. Cross-section panel (deferred — specified, not built)

### 5.1 Eligibility parameters

```
minimum_history
minimum_observation_count
minimum_coverage             # see §7 — not implementable yet
unresolved_coverage_policy   # exclude | include_flagged
liquidity_requirement
staleness_policy
instrument_types             # per the wrapper × underlying-class × venue taxonomy
currency_policy
adjustment_policy
include_delisted
```

### 5.2 Diagnostics

```
n_included / n_excluded
exclusion_reasons
coverage
history: minimum / median / maximum
liquidity distribution
dispersion
member_list
```

---

## 5A. Exclusion diagnostics

Every panel result exposes why Series did not qualify, not merely how many:

```
20Y panel

Universe:                    500
Included:                     35   (7%)

Excluded:
  Insufficient history       312
  Insufficient coverage       98
  Liquidity                   41
  Instrument type             14
  Unresolved                   0
```

### Availability and coverage — final model

```
ProviderAssignment
      │
      └── availability_status: KNOWN | UNRESOLVED          (stored)
                  │
              [KNOWN]
                  │
                  ▼
          coverage: HEAD_TRUNCATED | INTERIOR_GAPS | ADEQUATE     (derived, never stored)
```

**Governing sentence — to appear verbatim wherever coverage is surfaced:**

> Coverage density is a screening diagnostic until an appropriate trading-calendar
> capability exists. It MUST NOT be presented as an authoritative count of missing
> observations or trading-day gaps without a calendar defining the expected observation
> dates.

**`ADEQUATE` means "the screen found nothing," not "coverage is confirmed complete."** A
~252-day approximation cannot surface gaps smaller than its own resolution. The UI must not
imply a verification the screen cannot provide — the mirror, in the positive direction, of the
discipline already required for `UNRESOLVED`.

**Density and interior-gap detection carry different confidence and must be shown as such.**
Density is available now and heuristic. Interior-gap analysis is exact but entirely blocked on
Q-027. Presenting both under one undifferentiated "coverage" heading would launder a heuristic
into something that looks authoritative.

> **Known availability → measurable coverage → diagnosable incompleteness.
> Unknown availability → explicitly unresolved, never silently inferred.**

Keep the two statements separate all the way into the UI:

```
Source coverage begins    2018-01-04     ← what the provider reports
Stored observations from  2020-03-11     ← what HistFinTS holds
→ Coverage incomplete (head)
```

This is what allows the honest **coverage incomplete** in place of the false *insufficient
history*.

**Phrasing discipline.** Say *"this source has data from 2018"*, never *"data should exist
from 2018"*. Yahoo's `firstTradeDate` for a `.BA` cross-listing reports when **Yahoo's**
coverage begins, which may well postdate the actual venue listing. Providers report their own
coverage, not instrument facts — the same discipline P1 applies to identity.

**`INCOMPLETE` is not atomic.** Head truncation (`MIN(observed_at)` later than availability
start) and interior gaps (bar count below expected trading days) have different causes and
should be reported distinctly. A series can begin correctly and still be full of holes.

**`Unresolved` is a category, not a subdivision of coverage.** Where availability metadata is
absent, the system cannot distinguish *insufficient historical existence* from *incomplete
stored coverage* — and binning such Series into either would be a guess presented as a
measurement. It is also **not transitional**: some providers cannot report availability at
all, so for those assignments `Unresolved` is the permanent, correct answer.

**Three implementation rules this display forces.**

1. **Exclusion criteria overlap, so counting needs a stated rule.** A Series can fail history
   *and* liquidity. Either evaluate in a fixed documented order and attribute the **first**
   failure — in which case the counts reconcile to the universe, and the ordering materially
   changes the picture — or count every failure and state plainly that categories overlap and
   the column does not sum. Silent multi-counting produces a breakdown that does not
   reconcile, which users will notice and distrust.
2. **Label the candidate set `Universe`, not `Eligible`.** In the shape above the first line
   is the pre-filter population while *eligible* naturally reads as "passed the filter". A
   mislabelled diagnostic is worse than none.
3. **`Instrument type` is not computable yet.** It presupposes the capability matrix — the
   wrapper × underlying-asset-class × venue taxonomy — which does not yet exist.

---

## 6. Display rules

**Always show the cross-section. Warn past a threshold.**

*"Where a longer horizon substantially reduces the panel"* is not implementable as written —
`substantially` needs a number. Resolve it by always displaying the proportion and escalating
to a warning below a stated ratio of the shortest-window panel.

A warning that appears only on failure teaches users that its absence means no problem. The
count is cheap and always honest:

```
20Y analysis · 18 of 137 eligible Series (13%)
⚠ Based on a substantially smaller cross-section than the 1Y analysis (124 of 137).
```

`N(20Y) << N(1Y)` is not implementable as written. Proposed rule: display the ratio always;
escalate to a warning below a stated proportion of the shortest-window panel.

**Reproducibility.** A result MUST store both its eligibility spec **and** its resolved
member list. Re-running identical parameters in six months yields a different panel, because
more Series will have crossed the history threshold. Without the stored membership, the
difference is invisible.

---

## 7. Dependencies and sequencing

**Most of this is analytical policy, not schema.** Of the four exclusion reasons above, three
are computable against the current database today:

| Exclusion reason | Computable now? |
|---|---|
| Insufficient history | **Yes** — observation count and date range per Series |
| Liquidity | **Yes** — volume on `observation`, though null for value-only sources |
| Insufficient coverage | **No** — see below |
| Instrument type | **No** — needs the capability matrix, which does not exist yet |

Two parameters cannot be implemented yet:

| Parameter | Blocked on |
|---|---|
| `minimum_coverage` | A provider-assignment-level availability marker. Coverage currently cannot distinguish *"the provider has little data"* from *"our fetch was truncated"* — a confirmed live condition. Note the marker must sit on the **operational** path (`Series → ProviderAssignment`), not the Catalog path, or it will be unreachable for directly-created Series and will describe the wrong provider for the rest. |
| interior-gap detection | **A venue trading calendar.** Expected trading days cannot be computed without one, BYMA and NYSE holiday sets differ, no calendar table exists and no provider supplies one. Until then density is a **screen, not a measure**: a ~252-day annual approximation is adequate to flag a series 10%+ below expectation for review, and inadequate to assert a gap count. Label it as such. |
| `unresolved_coverage_policy` | Implementable immediately, but only one value is currently viable. Zero rows carry availability metadata today, so `exclude` yields an empty panel. Start at `include_flagged` and tighten as coverage improves — the policy is a parameter that moves, not a rule fixed once. |
| `adjustment_policy` | the adjustment-basis field. Admissible bases cannot be enforced while the basis is unrecorded. |

Everything else is implementable against the current schema. **The spec can be written now;
these two parameters activate when the upstream migration lands.**

---

## 8. Open items

- Concrete threshold values — `minimum_panel_depth`, `dispersion_threshold`,
  `staleness_policy` — deliberately left unset. They should be calibrated against the
  existing pair history rather than guessed.
- Whether a stale member is **excluded** or **down-weighted**. Exclusion is simpler and more
  honest; down-weighting preserves depth in a panel that is already thin early in history.
- How `relationship_type` interacts with panel composition: whether CEDEAR and dual-listing
  pairs may share one panel, given their different fee and ratio mechanics.
