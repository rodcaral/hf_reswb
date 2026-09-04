# SPEC — Panel Eligibility and Diagnostics

**Status:** specification complete; both named implementation gates (Tranche 2 schema, Q-061) resolved — implementation authorized per D-046, provisional parameters remain calibration-gated (§8.5) · **Version:** 0.2 · **Date:** 2026-08-17
**Governing decisions:** D-016 (panel principle) · D-017 (time-varying membership) · D-024 (this spec) · D-037 (calendar and alignment) · D-038/D-039 (observation suitability — implemented, gate cleared) · D-041 (Q-061 resolved; three parameters specified with calibration methodology, provisional status) · **D-044/D-045 (Tranche 2 implemented and validated) · D-046 (panel-eligibility implementation authorized)**

> **Update 2026-09-04 — stale status corrected.** This spec's own two remaining gates, both
> named below (Tranche 2 migration, Q-061), are resolved: Q-061 by D-041 (2026-08-17, already
> reflected above); Tranche 2 by D-044/D-045 (implemented and validated in production).
> D-046 authorizes panel-eligibility implementation on that basis. The provisional
> parameters (`include_delisted`, `staleness_policy`, `dispersion_threshold`) remain
> calibration-gated per §8.5, unaffected by this correction. The historical update blocks
> below are preserved unedited as dated narrative of 2026-08-17's own state, not rewritten.

> **Update 2026-09-04 — DOM-1: dispersion threshold status corrected; `CV 0.167` superseded.**
> DFA has issued **DOM-1**, superseding every normative statement below asserting that
> `dispersion_threshold = 0.167` is a current operational parameter, that `0.167` may proceed
> analytically, that `0.167` is sufficient for PRIMARY-cohort analytical use, that dispersion
> presently has an operational numerical threshold, or that raw-price coefficient of variation
> remains the current dispersion methodology. **None of those statements is current.** The
> governing current state, per DOM-1:
>
> **Dispersion threshold: UNCALIBRATED.** No numerical dispersion threshold is currently
> authorized for analytical, suppression, eligibility, or production use. The historical
> `CV 0.167` value is retained only as an unverified/non-decision-bearing artifact and must not
> be reused as calibration evidence. Current methodology design uses `LOG_RELATIVE` residuals
> around a provisional same-date median; neither the residual distribution nor any operating
> threshold has yet been calibrated. Calibration remains gated on an eligible multi-date/regime
> population and applicable independence requirements.
>
> Every §8.3/§8.5/§8 (Open items) passage below that states or implies `0.167` is a live,
> operational, or analytically-usable parameter is **marked `[SUPERSEDED BY DOM-1]` in place,
> preserved verbatim as dated historical record — not deleted, not rewritten to read as if it
> had never been reported.** Full DOM-1 text and provenance: `DECISIONS.md`, 2026-09-04 entry;
> full impact trace: `workbench/docs/evidence/DOM1_DISPERSION_THRESHOLD_IMPACT_TRACE_2026-09-04.md`.
> Governing calibration-artifact downgrade this DOM-1 reaffirms, unchanged: `ACTION_PLAN.md` §15d.

> **Update 2026-08-17 — Q-061 resolved at financial-domain level; three inclusion-rule parameters now specified.**
> `include_delisted` (default to inclusion for historical research), `staleness_policy` (time-local exclusion, 
> detection separate from eligibility), and `dispersion_threshold` (parameterized aggregate suppression). All three
> are provisional analytical parameters (§8) pending empirical calibration against historical panel data (§8.5).
> No hard-coded thresholds in production until calibration is complete and, where financially material, reviewed by 
> the FDA. Implementation stays blocked on Tranche 2 schema (Workbench cannot proceed without `provider.adjustment_basis` 
> backfill and the missing provider-assignment availability marker).

> **Update 2026-08-17 — D-039: the `SPEC_OBSERVATION_SUITABILITY.md` gate is cleared.**
> Items 1–3 (trade-evidence classification, trade-filtered calendar derivation, session
> status) are implemented and tested (`src/hf_reswb/application/suitability_service.py`,
> 6/6 passing). This spec's **other** two gates — Tranche 2 migration (`minimum_coverage`,
> `adjustment_policy`) and Q-061 (inclusion rules) — are independent and still stand; see
> §7 below. Nothing here may be implemented against raw `observation` rows without routing
> through `classify_series()`/`apply_calendar()` first, per SPEC_OBSERVATION_SUITABILITY.md
> §5's treatment rule (date removal upstream of the pairwise intersection).

> **Update 2026-08-17 — D-037 removes Q-027 as a gate on this spec.** Cross-Series alignment is
> **intersection of common dates, pairwise, differencing *after* intersecting**, with per-date
> panel depth recorded as provenance; forward-fill is prohibited. The trading calendar is
> **derived from the store** by quorum over Series sharing a venue — authoritative for NYSE
> across all eras, reliable for BYMA from ~2019, and **unresolved before ~2015**, which must be
> declared rather than approximated. Needs no HistFinTS change. This spec remains gated on the
> Tranche 2 migration (coverage metadata) and on Q-061 (inclusion rules) only. **See also F-026:**
> zero-volume carried-forward phantom bars in Yahoo's deep `.BA` history will generate false
> ratio-change candidates on the longest-history pairs unless excluded from return series.

> ### Update 2026-08-17 — **implementation of this spec is GATED on `SPEC_OBSERVATION_SUITABILITY.md`** (D-038)
>
> Per an explicit directive, no part of this spec is to be implemented until observation
> suitability lands. The gate is not procedural. F-026's phantom bars include an unbroken
> **116-session** frozen run on `PAMP.BA` (2004-11-09 → 2005-04-19), plus runs of 76, 51, 39,
> 37, 30 and 20 sessions. Each produces a persistent implied-FX excursion on the CEDEAR leg
> that is the *same signature* the panel residual uses to flag a ratio change (D-016/D-017) —
> on the longest-history pairs, which are exactly the ones A-012's demo depends on. Built
> before the filter, this spec would generate confident false ratio-change candidates.
>
> Three corrections to the update above, all from D-038:
>
> 1. **F-026's mitigation is withdrawn (F-028).** Do **not** treat `volume = 0` as no observed
>    trade: 19.7% of zero-volume bars in a 300-Series US sample carry a genuine intraday range.
>    Use the conjunctive rule in `SPEC_OBSERVATION_SUITABILITY.md` §2.1.
> 2. **The calendar quorum must run over trade-bearing dates, not raw dates,** and D-037's
>    BYMA ~2019+ *Reliable* rating holds only in that filtered form — the unfiltered
>    derivation admits four 2026 Argentine holidays at 7-of-9 participation (F-029).
> 3. **Phantom bars are not confined to the deep `.BA` era.** They are live in 2026, present on
>    US Series at scale (19,883 in the 300-Series sample), and 46% of them fall on **real**
>    trading sessions. Any assumption that this is a pre-2015 BYMA problem is wrong.
>
> The alignment machinery itself needs no change: exclusion is a **date removal upstream of the
> pairwise intersection**, so a filtered leg simply contributes fewer dates and the resulting
> multi-session return carries the label A-016(d) already requires.

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
| Liquidity | **Qualified yes** — volume on `observation`, null for value-only sources, and **`volume = 0` does not mean no trade** (F-028: 19.7% of zero-volume bars carry a real intraday range). A liquidity screen must read `trade_evidence`, not raw volume. |
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

**Superseding gate (D-038).** The sentence above is about *upstream* blockers and still holds.
Independently of it, **implementation of any part of this spec is gated on
`SPEC_OBSERVATION_SUITABILITY.md` items 1–3** (trade-evidence classification, the trade-filtered
calendar derivation, session status). Those three need nothing from HistFinTS and are buildable
today; they are simply not built yet. Nothing here may be implemented against raw
`observation` rows.

| Additional blocker | Blocked on |
|---|---|
| Any return, volatility, correlation or implied-FX series | `trade_evidence` classification (`SPEC_OBSERVATION_SUITABILITY.md` §2.1, §5) |
| interior-gap detection *and* the derived calendar it now rests on | the calendar quorum being filtered to trade-bearing dates (F-029) |
| Series 11311 (`GLD.BA`) participating in any panel or quorum | **F-030** — mixed daily/5-minute bars in one Series |

---

## 8. Eligibility parameter specifications — Q-061 resolution

*Resolved 2026-08-17 at financial-domain level (D-041). Three parameters were identified as
decisions requiring domain judgment (D-024 "Additions to the parameter set"); all three are now
specified below as provisional analytical parameters pending empirical calibration.*

### 8.1 `include_delisted` — Survivorship switch

**Semantic:** Boolean; defaults to `TRUE` for historical research context.

**Definition:** When `TRUE`, a Series marked `status = DELISTED_OR_DISCONTINUED` in its
observation era (the date range being analyzed) retains its historical observations and
participates in the panel on dates where it would otherwise be eligible. When `FALSE`, such
Series are excluded retroactively from the entire historical window, even for dates when they
were actively trading.

**Role:** Governs survivorship bias. In historical analysis (e.g., "what was the rate on
2015-03-15?"), exclusion of Series that later delisted is false — they were real participants
on that date. In present-day analytics where investability or contemporaneous tradability is
part of the question, exclusion is appropriate.

**Observational rule:** A Series contributes its observations on dates where **all** the
following hold: (a) both legs have observations (§4.1 `both_legs_present`); (b) the
relationship and ratio are known as-of-date; (c) the Series' own `status` **at that historical
date** would have been `ACTIVE` (not `DELISTED_OR_DISCONTINUED`). The `status` field is
historical per row, not a current flag. If `include_delisted = TRUE`, condition (c) is
ignored.

**Why separate from calendar/coverage gates:** A discontinued Series' history is evidence; the
decision to exclude it is analytical, not technical. It does not belong in a technical
"missing data" flag.

**Provisional status:** No calibration needed — this is a binary analytical choice, not a
threshold. The field definition is authoritative; documentation and UI must make the choice
explicit.

### 8.2 `staleness_policy` — Time-local observation exclusion

**Semantic:** A dictionary mapping series/pair to a staleness condition and its exclusion rule.

```
staleness_policy: {
    "condition": "max_consecutive_no_trade_days",
    "value": <PROVISIONAL_PARAMETER>,
    "unit": "calendar days",
    "exclusion_mode": "time_local"
}
```

**Definition:** Observations remain eligible and contribute to the panel before the staleness
condition is detected on a Series/pair. Once the condition is detected on a specific date `D`,
that Series/pair is excluded **from date D onward within the analysis window**, not
retroactively for its entire history.

**Time-local exclusion semantics:**

- Compute for each Series: the most recent observation date `last_observed` in a rolling
  window.
- On each panel date `D`: if (`D` - `last_observed`) > `value` (in calendar days), the Series
  is stale on date `D`.
- A stale Series on date `D` is excluded from the panel on that date and all subsequent dates
  within the window.
- Earlier observations of the same Series (before staleness detected) remain eligible and
  participate in panels for earlier dates.
- If staleness resolves (new observation arrives), the Series may re-enter the panel on the
  date the new observation appears, subject to the staleness criterion at that point.

**Why separate from liquidity:** Volume and recency are orthogonal properties. A pair can pass
a volume floor while prints lag, dragging consensus toward its own stale level (D-017).
Staleness detection must operate independently, using the observed date, not volume.

**Detection vs. eligibility:** Staleness detection is conceptually separate from the
eligibility rule. The system detects stale conditions and records them (e.g., as metadata on
the panel result and per-pair residual diagnostics), but does not alter or remove the
underlying observations. The exclusion is applied at aggregation time, not at the read layer.

**Provisional status:** The numerical value (calendar days) and the exact condition are
provisional. See §8.5 (calibration methodology) for how this parameter is empirically
determined.

### 8.3 `dispersion_threshold` — Aggregate result suppression

**Semantic:** A real number; dimensionless (typically expressed as a basis-point tolerance or
percentage). Provisional; no universal value should be assumed.

**Definition:** When the panel's per-member residual dispersion exceeds `dispersion_threshold`,
the aggregate implied-FX rate is **suppressed** — not published, not displayed with a caveat,
not interpolated into the result stream.

**Suppression mechanics:**

- Compute the consensus rate across eligible members.
- Compute each member's residual: (member_rate - consensus_rate) / consensus_rate.
- Compute dispersion: a summary statistic of the residual distribution (e.g., inter-quartile
  range, coefficient of variation, or percentile spread — see calibration methodology below
  for the choice).
- If dispersion > `dispersion_threshold`, set `result_status = SUPPRESSED`.
- **The aggregate result itself is suppressed, not stored, not interpolated.**
- **Underlying observations, per-member rates, residuals, dispersion diagnostics, and
  evidence remain available for inspection and traceability.** A data quality view can show
  why the result was suppressed without requiring access to a separate database.

**Why suppression, not caveat:** When members disagree about what the rate is by more than
the threshold, a caveated best-guess is worse than no number. A missing result is honest; a
false one with a disclaimer is a trap.

**Economically contextual:** The threshold is not a universal constant. It depends on:
- The currency pair and the volatility regime (high-volatility periods tolerate wider
  dispersion).
- Whether the question is "what is today's rate?" (lower tolerance) vs. "what was the rate
  that period?" (higher tolerance for historical aggregation).
- The intended use (trading execution vs. analytical reference).
- The panel depth (a two-member panel's dispersion is noisier than a five-member one).

No single number fits all contexts. The parameter must be configurable per panel spec and
calibrated against data in that context.

**Provisional status:** The value is provisional. Multiple calibration scenarios (by period,
by pair, by depth) may emerge from the calibration study (§8.5).

### 8.4 Interaction with time-varying membership

All three parameters operate under the as-of-date principle (§2):

- `include_delisted`: Applied independently on each panel date; a Series that is delisted on
  date D is excluded from that date onward (when `include_delisted = FALSE`), but included
  before.
- `staleness_policy`: Time-local by design; exclusion applies from the detected staleness
  onward.
- `dispersion_threshold`: Computed per panel date; the result status (suppressed or published)
  is per-date.

All three preserve **per-date panel depth** — a diagnostic showing how many members
contributed to each date's aggregation.

### 8.5 Calibration methodology and validation procedure

**No hard-coded thresholds are to be used in production until both (a) empirical calibration
against historical panel data is complete and (b) where calibration results have financial-
domain implications, they are reviewed by the FDA.**

**Calibration inputs:**

1. Historical pair panel across the relevant date range (e.g., the 20-year CEDEAR/USD sample).
2. Per-date panel membership, residuals, dispersion metrics, and outcome of eligibility rules.
3. Known real events: actual ratio changes (from audit, public filing), real FX moves (from
   external CCL history), currency regime shifts.
4. Out-of-sample validation window: a held-back period where the calibrated parameters are
   tested against new data without re-fitting.

**Staleness calibration approach:**

- For each Series in the calibration set, compute rolling observation recency (days since
  last trade).
- Measure the residual's **time signature** (D-017): does a persistent residual correlate
  with a period where the Series was stale? Do transient residuals appear during periods of
  normal recency?
- **FDA directive (2026-08-18):** Compute **empirical tail and relationship diagnostics** for
  candidate windows below the observed maximum, rather than selecting a numerical threshold at
  this stage. Candidate window analysis should show:
  - Fraction of observations excluded at each candidate window
  - Which pairs are affected
  - Distribution across time periods
  - Co-occurrence patterns with dispersion elevation and evidence-quality events
  - Relationship between staleness and ratio-change detection (tail behavior)
- Do not promote a numerical staleness criterion to production until tail/relationship
  diagnostics are complete and reviewed by the financial domain.
- Validate on the out-of-sample window once a candidate is selected.

**Dispersion calibration approach:**

> **[SUPERSEDED BY DOM-1, 2026-09-04 — preserved verbatim as dated historical record, not
> current specification.]** The passage below (through the end of §8.5's dispersion-specific
> text) describes the 2026-08-18 provisional state as it stood before DOM-1. It is **not**
> current: no numerical dispersion threshold is currently authorized for any use, and
> `CV 0.167` is retained only as an unverified/non-decision-bearing historical artifact
> (`ACTION_PLAN.md` §15d). Do not read anything below this marker, through the end of §8.5, as
> a live operational parameter.

**Current provisional parameter (FDA directive 2026-08-18):** `dispersion_threshold = 0.167` (coefficient of variation).

This parameter is **provisional and not a financially validated universal threshold.** It is set as an operational parameter for current use while calibration proceeds, with the following constraints:

- **Provisional scope:** Applicable only to the PRIMARY cohort (CEDEAR ↔ foreign underlying pairs; currently 5 pairs, expanding to 12 pending schema resolution per F-032).
- **Not universal:** The threshold must be recalibrated as the primary CEDEAR population expands, as evidence base improves, and as regime-specific analysis matures.
- **Cohort separation (binding):** CEDEAR/foreign-underlying is the PRIMARY calibration cohort. ADR/ADS ↔ Argentine local-share pairs are a SECONDARY validation population. Do **not** pool cohorts for threshold calibration. Separate thresholds may emerge per cohort.
- **Not financially sanctioned:** This parameter has not undergone financial-domain review for universal applicability. Decisions to suppress results based on this threshold remain analytical and provisional until reviewed by the FDA.

**Calibration approach:**

1. Compute dispersion metrics for every panel date in the calibration set using multiple
   candidates (IQR, coefficient of variation, 90th percentile of |residual|, etc.).
2. Measure correlation between dispersion and:
   - Known ratio changes (did dispersion spike around announced changes?).
   - Currency regime shifts (did dispersion change across CCL-regime boundaries?).
   - Real FX moves (does high dispersion coincide with high-volatility periods?).
   - Evidence-quality events (F-009 reconciliation gaps, F-017 import truncation, F-021 ratio steps, F-026 zero-volume carries).
3. For each candidate metric and threshold:
   - Measure **suppression rate**: what % of panels would be suppressed?
   - Measure **false-suppression rate**: of suppressed panels, how many contained genuine
     market moves rather than ratio anomalies?
   - Measure **missed signals**: of non-suppressed panels, how many later turned out to
     reflect undetected ratio changes?
4. **Distribution analysis:** Show how observations above/below the threshold distribute across:
   - Structural events (evidence-quality dimensions)
   - Staleness states
   - Time periods and market regimes
   - Pair identity
5. Validate on the out-of-sample window. Document any regime or pair-specific variations.

**Validation procedure:**

- Apply calibrated parameters to the out-of-sample window.
- Measure:
  - Suppression rate (does it match the calibration rate, or is it unstable?).
  - Comparison to external CCL data: for dates where the result was published, how well
    does it match the published external rate?
  - Comparison to audit findings: for dates where staleness or ratio changes were manually
    identified, was the parametrized system's behavior consistent with those findings?
- Document any regime or pair-specific variations. If calibration results differ materially
  by pair or era, define separate parameter sets per context (e.g., "dispersion threshold for
  AAPL pre-2015", "dispersion threshold for BABA post-2020").

**Output of calibration:**

**Staleness:**
- Empirical tail and relationship diagnostics for candidate windows below observed maximum.
- Distribution of exclusions and co-occurrence patterns per FDA directive.
- **No numerical criterion promoted to production** until tail/relationship analysis complete and
  financially reviewed.

**Dispersion:**
- Current provisional parameter: `dispersion_threshold = 0.167` (coefficient of variation).
- Distribution analysis across structural events, staleness states, time periods, and pair identity.
- Calibration report documenting:
  - Methodology and candidate thresholds evaluated.
  - Validation results on out-of-sample data.
  - Known limitations and regime/pair dependencies.
  - Cohort-specific thresholds if analysis reveals PRIMARY and SECONDARY populations require
    different parameters.
  - Recommended update frequency (when to re-calibrate as new data arrives or population expands).

**FDA review gate:** 
- **Staleness:** No promotion to production criterion until tail/relationship diagnostics reviewed
  by financial domain.
- **Dispersion:** Current provisional parameter (0.167) may proceed analytically without new
  financial review, pending recalibration as PRIMARY cohort expands (F-032 resolution) and
  SECONDARY cohort evidence matures. Financially material changes to thresholds require FDA review.

**Provisional status:** Both parameters remain provisional. Staleness is uncalibrated and
analytically non-committal. Dispersion has a provisional operational parameter that must be
recalibrated as the population, evidence base, and understanding of regime dependencies improve.
The specification is a contract for *how* calibration and validation will proceed.

---

## 8. Open items

**Staleness (awaiting tail/relationship diagnostics per FDA directive 2026-08-18):**
- Empirical tail behavior below observed maximum across candidate windows [2d, 3d, 4d, 5d, 6d, 7d].
- Relationship diagnostics: co-occurrence with dispersion elevation, evidence-quality events, and
  ratio-change detection signals.
- **Do not select a numerical staleness criterion** until these diagnostics are complete and
  reviewed by the financial domain. No production use of staleness_policy until then.

**Dispersion:**

> **[SUPERSEDED BY DOM-1, 2026-09-04.]** The first bullet below ("sufficient for analytical
> use") is not current — preserved verbatim as dated historical record. Current state:
> **UNCALIBRATED, no numerical threshold authorized for any use** (see the 2026-09-04 update
> block at the top of this document).

- Current provisional parameter (CV 0.167) sufficient for analytical use in PRIMARY cohort.
- Recalibration required when:
  - F-032 resolution expands PRIMARY cohort from 5 to 12 pairs (pending Phase 3 validation).
  - SECONDARY cohort (ADR/local-share) evidence matures and separate thresholds may be warranted.
  - Regime-dependent analysis reveals material differences across periods.
- Dispersion metric choice remains open for future refinement (IQR, coefficient of variation,
  percentile spread, or other).

**Cohort interaction:**
- Whether CEDEAR (PRIMARY) and dual-listing/ADR (SECONDARY) pairs may share one analysis
  or require separate thresholds, given their different fee and ratio mechanics.
- Confirmed: do **not** pool cohorts for threshold calibration per FDA ruling.

**Context-dependent parameters:**
- Will a single `staleness_policy` and `dispersion_threshold` apply across all pairs and eras,
  or will calibration reveal regime-specific requirements?
- Already confirmed: separate parameters likely for PRIMARY (CEDEAR/foreign) and SECONDARY
  (ADR/local-share) cohorts.
