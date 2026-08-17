# SPEC — Observation Suitability (zero-volume and carried-forward bars)

**Status:** implemented (§7 items 1–3, 6), ratified · **Version:** 0.2 · **Date:** 2026-08-17
**Governing decisions:** D-001 (read-only boundary) · D-033 (reference by key, four epistemic
layers) · D-036 (a verdict describes evidence state, not permission) · D-037 (derived venue
calendar, pairwise intersection) · D-038 (this spec) · **D-039 (ratified; items 1–3 and the
F-030 guard implemented, `src/hf_reswb/{domain,application}/suitability*.py`,
`tests/test_observation_suitability.py`, 6/6 passing)**
**Findings addressed:** F-026 (phantom bars) · F-027 (null-close marker discarded) ·
F-028 · F-029 · F-030 · F-031

> Implementation matches this spec exactly — no rule was loosened or reinterpreted during
> the build. Q-067 (§8) remains open and provisional; the classification layer records
> `TRADE_EVIDENCE_UNRESOLVED` but does not itself exclude it — that is a consuming
> calculation's obligation (§4), not built here.

> **Why this is a separate document rather than a section of
> `SPEC-panel-eligibility.md`.** The classification specified here is consumed by three
> different capabilities — panel/implied-FX return series (`SPEC-panel-eligibility.md`), the
> F-009 discontinuity detector (`SPEC-f009-evidence-consumption.md` §4, per F-031), and
> D-037's own venue-calendar derivation. It cannot live inside any one of its consumers
> without one of the other two acquiring a dependency on a document about something else.
> A-016's calendar-and-alignment section stays where it was queued; this is the per-row
> evidence question that sits underneath it.

---

## 0. The requirement, in one sentence

> Distinguish, for every observation the Workbench reads, whether the row is **evidence that
> a trade occurred at that price on that date** — separately from whether the row exists in
> HistFinTS, and separately from whether the venue was open — record that distinction as a
> Workbench-owned `Calculated` classification that references the upstream row by key and
> never copies its value, and make continuity-sensitive calculations consume the
> classification rather than the raw row.

The emphasis is load-bearing in two places. **"A trade occurred"** and not "the venue was
open": §2 shows these are different questions with different answers on roughly half the
affected rows, and it is the first that governs suitability. **"Never copies its value"**: at
the cardinality involved (§6) a value copy would make the Workbench a second time-series
store, which D-001 exists to prevent.

---

## 1. What HistFinTS actually contains

All figures verified by query against
`C:\Users\CarlonTinto\AppData\Local\histfints\histfints\histfints.db`,
`sqlite3 -readonly`, `PRAGMA temp_store=2`. Full query text is recorded under *Evidence* in
D-038; this section states the results the design depends on.

### 1.1 `volume = 0` is a provider-reported value, not a missing one

`providers/yahoo_finance.py:162` passes Yahoo's `volume` straight through; the only rows
skipped are those with a **null close** (`yahoo_finance.py:149–154`, F-027). Across the nine
tracked BYMA Series and a 300-Series US sample, `observation.volume IS NULL` count is **0**.
So a zero is Yahoo asserting zero, not HistFinTS defaulting.

### 1.2 `volume = 0` alone is **not** a no-trade signal

300-Series USD equity/ETF sample, all history — 27,564 zero-volume bars, decomposed by
whether the bar's OHLC collapse to a single price and whether that price equals the prior
stored close:

| `open=high=low=close` | `close = prior close` | count | reading |
|---|---|---|---|
| yes | yes | 19,883 | carried-forward fill |
| yes | no | 2,235 | single price, but the price moved |
| no | no | 4,247 | **genuine intraday range, volume reported 0** |
| no | yes | 1,187 | genuine intraday range, closing back at the prior close |

**5,434 of 27,564 zero-volume bars (19.7%) carry a real high/low range.** Spot-checked:
series 118 (Aclarion) 2023-11-22 → 2023-12-14 shows ranges of 3–15% with `volume = 0`
throughout. These are real bars with a defective volume field. **F-028** records that
F-026's proposed mitigation — *"treat `volume = 0` on an equity Series as no observed trade,
exclude such bars"* — would discard all 5,434 of them.

### 1.3 The conjunctive signature has 100% recall against independent ground truth

Ground truth chosen to be independent of anything derived from the store: Argentina's
*feriados inamovibles*, which no decree moves — 01-01, 05-01, 07-09, 12-08, 12-25. BYMA is
unambiguously closed on all five. Across series 11312/11313/11314/11315, **every** bar found
on those dates (75 rows) has `volume = 0`, `open = high = low = close`, and a close
**bit-identical** to the prior stored close (e.g. `29.3999996185303` repeated from
2000-12-22 to 2000-12-25 to 2001-01-01).

Deliberately excluded from the ground-truth set: 04-02 (Malvinas). In 2020 the store has a
full-volume session on 2020-04-02 and **no** bar on 2020-03-31, i.e. the holiday was moved
and the store is right about it. This is the same failure mode that made
`exchange_calendars`' `XBUE` wrong on ten 2025 dates (D-037(c)), and it is why the ground
truth is restricted to the five immovable dates.

### 1.4 Roughly half the carried-forward bars are on **real** trading sessions

Eight daily BYMA Series (11311 excluded, see §1.6), 1,910 bars matching the full conjunctive
signature, split by whether *any* of the eight reported a trade on the same date:

| | no BYMA Series traded that date | another BYMA Series traded that date |
|---|---|---|
| pre-2015 | 966 | 868 |
| 2015+ | 68 | 8 |
| **total** | **1,034 (54%)** | **876 (46%)** |

Concrete instance: **2026-07-06**, a Monday on which seven of nine Series traded normally,
while series 11305 (`AAPL.BA`) and 11317 (`BIDU.BA`) each carry a zero-volume
carried-forward bar. The venue was open; those two Series did not trade; Yahoo emitted a fill
rather than the null close F-027 documents.

On the US side the split is total: across the 300-Series sample there is **not one
observation** on 2025-01-09 (Carter closure), 2018-12-05, 2012-10-29/30 (Sandy),
2001-09-11…14, 2025-01-01, 2025-07-04 or 2025-12-25. All 19,883 US carried-forward bars are
therefore on genuine sessions. No weekend bars exist on any BYMA Series
(`strftime('%w')` ∈ {1..5} only).

**This is the finding the whole design turns on.** "Not in the derived venue calendar" is
neither necessary (46% of BYMA cases, 100% of US cases are on real sessions) nor sufficient
(§3.3) as a detection rule.

### 1.5 The mechanism is live in 2026, not a historical artifact

D-037(f) recorded that raw session dates equal `volume > 0` session dates from ~2019, and
F-026 concluded the pattern "disappear[s] entirely from ~2019". Extending the same count
through the current year:

| year | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| raw dates | 244 | 241 | 244 | 244 | 243 | 246 | 243 | **156** |
| `volume > 0` dates | 244 | 241 | 244 | 244 | 243 | 246 | 243 | **152** |

The four 2026 divergences are 05-01, 05-25, 06-15 and 07-09 — all real Argentine holidays —
and each carries a phantom bar on **seven of nine** Series simultaneously. Raised as
**F-029**. Two consequences: the derived BYMA calendar is threshold-sensitive at 7/9 in the
era D-037 called *Reliable*, and no era-boundary cut-off can be hard-coded.

The obvious explanation — a recent rolling window in Yahoo's response — is **dead**: all
6,624 observations of series 11312, spanning 2000-01-03 to 2026-08-14, carry
`import_run_id = 25552`. One provider response contained fills for 2000–2018 and for
2026-05…07 and none for 2019–2025. Why is not determinable from the store, and this spec does
not guess. It is the reason classification must run continuously over whatever range is
analysed rather than as a one-off cleanup of deep history.

### 1.6 Series 11311 is not classifiable by date

Series 11311 (`GLD.BA`) has `configured_interval = '5m'` and holds 398 daily bars **plus** 72
five-minute bars, all from 2026-08-14, in one Series. `date(observed_at)` is therefore not a
session key for it, `lag(value) ORDER BY observed_at` mixes granularities, and its
session-open 5m bar legitimately carries `volume = 0`. It was one of D-037's nine quorum
contributors. Raised as **F-030**; excluded from every measurement in this section.

### 1.7 Not testable: other providers

`provider` holds exactly three rows — `fred`, `yahoo_finance`, `byma` — and `byma` has two
assignments supplying no observations (D-021). F-026's open item *"whether the same pattern
exists in Alpha Vantage or Stooq history"* is **unanswerable from the store**: no such
provider row exists. It must stay open as a question about a provider not yet in use, not be
recorded as a clean result (D-009).

---

## 2. The classification model

### 2.1 Two orthogonal axes, not one three-valued enum

The natural-sounding vocabulary — `PHANTOM_FILL` / `LEGITIMATE_ZERO_VOLUME` / `AMBIGUOUS` —
is rejected, and the reason is §1.4 rather than taste. It collapses two independent questions
into one enum, and the word *legitimate* attaches a permission judgement to the axis that
matters least for suitability. A carried-forward fill on a genuine session (876 BYMA rows,
19,883 US rows) is "legitimate" in the sense that the venue really was open — and is exactly
as unusable for a return as a fill on Christmas Day, for the same reason: no trade stands
behind the price.

**Axis A — `trade_evidence`.** Decidable from the row and its immediate predecessor alone. No
calendar input.

| Value | Rule |
|---|---|
| `NO_TRADE_REPORTED` | `volume = 0` **and** `open = high = low = value` **and** `value` = the prior stored close for this Series, compared for **exact** equality |
| `TRADE_EVIDENCE_UNRESOLVED` | `volume = 0` **and** `open = high = low = value` **and** `value ≠` prior close (2,235 US / 50 BYMA rows) |
| `TRADE_OBSERVED` | everything else, including `volume = 0` with a genuine `high > low` range — which additionally sets `volume_unreliable` (5,434 US / 149 BYMA rows) |

**Axis B — `session_status`.** From D-037's derived venue calendar, which is downstream of
Axis A (§3.3).

| Value | Meaning |
|---|---|
| `SESSION_CONFIRMED` | the date is in the derived calendar for this Series' venue, in an era D-037(f) rates *Authoritative* or *Reliable* |
| `SESSION_ABSENT` | the date is not in the derived calendar for an era so rated |
| `SESSION_UNRESOLVED` | the era's calendar is *Usable with caveat* or *Unresolved* per D-037(f) — BYMA before ~2015 — or the Series is the only one HistFinTS holds for its venue (F-027) |

### 2.2 The grid, and what each cell means

|  | `SESSION_CONFIRMED` | `SESSION_ABSENT` | `SESSION_UNRESOLVED` |
|---|---|---|---|
| `TRADE_OBSERVED` | normal | **contradiction** — a trade on a non-session date. Investigate as a calendar-derivation or date-key defect (F-030), never silently accept | usable; session context unknown |
| `NO_TRADE_REPORTED` | fill on a real session — *the Series did not trade* | fill on a non-session date — the case F-026 named *phantom* | fill; cannot say which |
| `TRADE_EVIDENCE_UNRESOLVED` | ambiguous | ambiguous | ambiguous |

`PHANTOM_FILL` survives only as a **presentation label** for the (`NO_TRADE_REPORTED`,
`SESSION_ABSENT`) cell. It is derived at display time, never stored as a primitive — P43, the
UI is a projection.

### 2.3 Why exact equality and not a tolerance

The repeated closes are bit-identical (`29.3999996185303`, `0.00854299962520599`), because
Yahoo is echoing the same float, not recomputing a price. A tolerance would therefore buy
nothing on the true positives and would start admitting genuine thin-session prints that
happen to land near the prior close. Any tolerance is a false-positive generator with no
compensating recall. Compare `=`.

The comparison is against the **prior stored close for that Series**, not the prior
*calendar* day and not the prior *session* — deliberately, so Axis A stays row-local.

### 2.4 P4 status

`Calculated` (P4), owned by the Workbench, per D-033's second layer. Its inputs are two named
upstream `Observed` rows plus a rule version. It is **not** `Observed`: the conjunction is the
Workbench's assertion, even though each conjunct is a direct reading of the provider's own
report. The distinction matters for §4.

---

## 3. Detection rule — what it is not

### 3.1 Not `volume = 0`

19.7% false-positive rate on the US sample (§1.2). This is F-028 and it invalidates the
mitigation sentence in F-026 and the trailing instruction in A-016.

### 3.2 Not "the price didn't change"

An unchanged close on positive volume is an ordinary event in an illiquid name and is real
evidence: trades occurred and cleared at the prior level. Excluding it would discard
information and would silently implement a staleness filter, which is Q-061(b)'s question,
not this one.

### 3.3 Not "the date is absent from the derived venue calendar" — and it *cannot* be

Three independent reasons, in increasing order of weight:

1. **Not necessary.** 46% of BYMA and 100% of US carried-forward bars are on real sessions
   (§1.4).
2. **Not available where it is most needed.** The calendar is *Unresolved* for BYMA before
   ~2015 (D-037(f)), which is where 1,834 of the 1,910 BYMA cases live.
3. **Circular.** D-037 derives the calendar from observation dates, and D-037(f) states in
   terms that the derivation over-counts *because of these very bars*. A rule that classified
   bars using the calendar would be inferring the calendar from the bars and the bars from the
   calendar.

The resolution is an **ordering**, and it is the reason Axis A is specified as row-local:

```
1. Axis A       — per observation, from the row and its predecessor. No calendar input.
2. Calendar     — derived per D-037, quorum over TRADE_OBSERVED dates only, not raw dates.
3. Axis B       — per observation, from the calendar produced in step 2.
```

No cycle. Step 2 is a **correction to D-037**: the quorum must run over trade-bearing dates,
and D-037(f)'s raw-versus-filtered table must be extended to 2026, where the two diverge
again (§1.5). D-037's own reason for not filtering by volume — that a real session can be
quiet across all of two or three thin contributors — survives untouched, and is precisely why
step 3 returns `SESSION_UNRESOLVED` rather than `SESSION_ABSENT` for the thin era.

---

## 4. Does D-036's principle transfer?

D-036 established: *a verdict describes evidence state; it does not itself decide whether an
analysis is permissible — that is the analytical method's call.* Two defensible readings were
available and the difference is not cosmetic.

**Reading (a) — full transfer.** The classification is a flag; every consumer decides. Argues
from consistency: one epistemic posture across the Workbench, no capability quietly acquiring
the authority to void data.

**Reading (b) — harder exclusion.** A `NO_TRADE_REPORTED` row is not an unresolved question
about the world; it is the provider stating that nothing traded. Treating that as merely
advisory lets a calculation consume a price no trade produced, which is the P3 fabricated-
lineage failure with the fabrication performed upstream instead of locally.

**Adopted: the principle transfers, the *softness* does not — and the reason is that
D-036's softness was a consequence of evidence absence, not of the principle.**

D-036's three-verdict vocabulary is soft because its third value exists to describe HistFinTS
not having captured something (`TABLE_ABSENT`, an empty `provider_event`, a provider that
publishes no revisions). Under that constraint the analytical method genuinely is better
placed to judge whether it can tolerate the uncertainty. Axis A has **no analogous
absence**: it is decided deterministically from two rows that are always present, with no
dependence on any evidence that may or may not have been captured. So the uncertainty D-036's
softness exists to respect is not present here, and importing the softness would import a
hedge against a risk that does not apply.

Concretely, three rules:

1. **No global gate.** There is no "this observation is bad" flag and no suppression at the
   read layer. Every consumer reads the classification alongside the row, exactly as D-036
   requires. A price-history chart, a volume study, a data-quality panel and a coverage count
   all legitimately want these rows, and two of them want them *because* of the
   classification.
2. **A non-overridable-in-silence default.** Continuity-sensitive calculations — returns,
   volatility, correlation, beta, CAGR, implied-FX ratio series, and F-009 discontinuity
   candidate generation — exclude `NO_TRADE_REPORTED` rows **by default**. A calculation that
   includes them is permitted and must declare it in its own P3 provenance, naming the count
   included. The strength is in the audit obligation, not in a prohibition.
3. **`TRADE_EVIDENCE_UNRESOLVED` follows the D-036 pattern unchanged**, because it *is* an
   evidence-absence case: excluded by default from continuity-sensitive calculations, with the
   exclusion reported separately from `NO_TRADE_REPORTED` exclusions, never merged into one
   count. See Q-067.

Axis B never gates anything. It exists to explain a classification to a reader and to feed
the calendar-confidence display A-016(f) requires. A row is not less suitable for a return
because the venue was shut; it is unsuitable because no trade produced its price.

---

## 5. Treatment — exclusion is a date removal, not a gap and not a zero

When a `NO_TRADE_REPORTED` row is excluded, the correct operation is to remove that **date**
from the Series' usable date set *before* D-037's pairwise intersection. Three properties fall
out, and none of them needs new analytical machinery:

- The CEDEAR leg simply does not contribute the date. The intersection produces no pair, so no
  implied-FX point is computed and none is displayed.
- No forward-fill is introduced — the thing D-037(d) prohibited, partly *because* it is
  indistinguishable from these bars.
- The surviving return spans more than one session and must be labelled with the number of
  sessions it spans, per A-016(d). That obligation already exists; this simply makes more
  returns subject to it.

Worked example, and the argument in one case. Series 11315 (`PAMP.BA`) has an unbroken
116-bar `NO_TRADE_REPORTED` run from **2004-11-09 to 2005-04-19**, frozen at
`0.113329999148846`. Untreated, that run yields 116 fabricated zero returns followed by one
compressed jump — D-017's staleness pathology, understating volatility and attenuating
correlation, wrong in the flattering direction. Treated, the leg has a 116-session hole and
the intersection yields a single ~5.5-month multi-session return, labelled as such. The
second is honest and the first is not. Run-length distribution across the four deep Series:
756 runs of length 1, 151 of 2, and a tail at 20, 30, 37, 39, 51, 76 and 116.

**A run is never bridged, interpolated, averaged or annualised into daily terms.** A
116-session return is reported as a 116-session return.

### 5.1 The F-031 interaction — a discontinuity between two fills is not a discontinuity

Series 11312 has a 10× step at **2001-12-12**: `17.0` on 12-10 and 12-11, `1.70000004768372`
from 12-12 onward. Every one of those bars is `volume = 0`, OHLC-collapsed and
carried-forward — the step sits **inside** a `NO_TRADE_REPORTED` region on both sides. The
F-009 detector, run on raw rows, would generate this as a 10× candidate and — the legacy
`correction` table holding nothing — return *not explained by captured evidence*
(`SPEC-f009-evidence-consumption.md` §4.3), quarantining a span on the strength of two rows
that represent no trade. Raised as **F-031**.

**Rule:** candidate generation runs on the filtered series. A boundary whose endpoints are
both `NO_TRADE_REPORTED` is not a candidate. A boundary with one such endpoint is a candidate
whose calculation must record the endpoint's classification. Specification only — the D-035
freeze holds and no reconciler code changes here.

---

## 6. Workbench object shape

Reference by key, never a copy (D-033 §2.1). Reuses F-009's `evidence_reference` rather than
inventing a second pointer type.

**`observation_suitability`** — one row per classified observation. P4 `Calculated`.

| Field | Purpose |
|---|---|
| `evidence_reference_id` | → `evidence_reference` with `histfints_object = OBSERVATION`. Carries `resolution_state`, so a classification of an archived or overwritten row renders as unresolvable rather than stale (D-003, D-033) |
| `prior_evidence_reference_id` | → the predecessor observation the equality test used. Without it the test is not restatable |
| `histfints_series_id` | denormalised for query; convention-level (D-003) |
| `observed_date` | the session date classified; denormalised |
| `trade_evidence` | `TRADE_OBSERVED` · `NO_TRADE_REPORTED` · `TRADE_EVIDENCE_UNRESOLVED` |
| `volume_unreliable` | boolean; set when `volume = 0` on a `TRADE_OBSERVED` row (§1.2) |
| `session_status` | `SESSION_CONFIRMED` · `SESSION_ABSENT` · `SESSION_UNRESOLVED` |
| `basis` | which conjuncts fired: `VOLUME_ZERO`, `OHLC_COLLAPSED`, `EQUALS_PRIOR_CLOSE` |
| `calendar_derivation_id` | → the calendar used for `session_status` |
| `rule_version` | the spec/code version that produced the row |
| `classified_at` | when |

**`calendar_derivation`** — the D-037 calendar as a citable object, since it is an input to a
displayed number. Venue MIC (`XBUE`/`XNYS`, P4 `Asserted` per D-037(e)), the contributing
`series_id` list, the quorum rule, the date range, the era-confidence band from D-037(f), and
`derived_at`. Reused across many `observation_suitability` rows.

**`suitability_run`** — series, date range, `rule_version`, `calendar_derivation_id`, and
counts per grid cell. Without it, the **absence** of an `observation_suitability` row is
ambiguous between *classified as ordinary* and *never classified* — the D-009b trap in its own
right. A consumer must refuse to apply the default in §4.2 over a range no run covers, rather
than treat unclassified as clean.

**`no_trade_run`** — derived, not authoritative: series, first and last date, length, and the
bounding `evidence_reference` ids. Exists because §5 shows run length, not row count, is what
a display must warn on.

### 6.1 A deliberate narrowing of D-033's exception

D-033 permits a *finding* to record the specific numbers it asserts about, because a finding
that cannot restate its own arithmetic is not traceable. That exception is **not** extended
here. `observation_suitability` records the boolean conjuncts and both upstream keys, and no
values. Two reasons: the assertion is an equality *relation*, fully restatable by re-reading
two named rows; and at this cardinality — ~20k rows on a 300-Series sample, extrapolating to
~750k across the store — a value copy is not an audit note, it is a shadow price store, which
D-001 forbids. Stated explicitly so it does not read as an oversight.

### 6.2 Classify lazily

Consequent scope rule: classification runs over the Series and date range an analysis
actually touches, driven by `suitability_run`, not eagerly across all 11,317 Series. This also
means a re-import that mutates upstream rows (F-009) invalidates a run rather than corrupting
a stored answer — `rule_version` plus the run's date range make the invalidation checkable.

---

## 7. Dependencies and sequencing

| # | Item | State |
|---|---|---|
| 1 | Axis A over a Series and range | **Implemented** — `application/suitability_service.py:classify_series()`. No HistFinTS change. |
| 2 | `calendar_derivation` over `TRADE_OBSERVED` dates | **Implemented** — `derive_calendar()`, quorum filtered to trade-bearing dates per §3.3. Confidence band is caller-supplied (not re-derived per era in code); the era-confidence findings from D-037(f)/D-038 remain the source for what value to pass. |
| 3 | Axis B | **Implemented** — `apply_calendar()`. Follows 2. |
| 4 | `SPEC-panel-eligibility.md` implementation | **Unblocked by D-039** for this gate specifically. Tranche 2 and Q-061 remain independent gates — see `SPEC-panel-eligibility.md` header. |
| 5 | F-009 candidate generation on filtered rows (§5.1) | Specification only; **D-035 freeze holds.** Not implemented — out of scope for D-039. |
| 6 | F-030 (series 11311 mixed interval) | **Guarded, not fixed** — `is_classifiable()` refuses classification and calendar-quorum participation for any Series failing the daily/unique-date check. Series 11311 itself is untouched upstream. |
| 7 | Alpha Vantage / Stooq behaviour (§1.7) | Not testable; open, not clean. |

---

## 8. Open items

- **Q-067** — should `TRADE_EVIDENCE_UNRESOLVED` be excluded from continuity-sensitive
  calculations by default? §4.3 adopts *yes* provisionally. 2,235 US and 50 BYMA rows: a
  single-price zero-volume bar at a price that *moved*. It cannot be a pure carry-forward, and
  it cannot be confirmed as a trade. Excluding is the conservative reading; including is
  defensible on the grounds that the price moved, so something happened. Not decidable from
  the store — needs either an external print source or a domain judgement.
- **Why 2019–2025 is clean and 2026 is not** (§1.5) is unexplained, from a single import run.
  No cleanup may be scoped on an era boundary until it is understood, and the classification
  must run continuously regardless.
- **F-027 remains the honest limit.** The null-close marker would have made Axis A
  unnecessary for every future fetch, and it is unrecoverable for history already held. Axis A
  is a reconstruction of a signal the provider sent and HistFinTS discarded; it should be
  labelled as such wherever its confidence is displayed.
