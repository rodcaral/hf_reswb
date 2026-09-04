# Cross-Sectional Dispersion — Methodology Design Study (2026-09-04)

> **Amended 2026-09-04 (additive — everything below this block through §11 is unedited).** Per
> DFA's methodology rulings, relayed by SE/PO: `LOG_RELATIVE` is now the **primary** residual
> representation (no longer co-equal with `PERCENTAGE_RELATIVE`, which remains only as a
> diagnostic cross-check). The provisional same-date median remains accepted **for methodology
> design only** — not an approved calibration or production center. §12 below records DFA's
> rulings and the next bounded design increment performed under them, using the same five
> `2026-09-02` observations, no new pairs or dates, and no `F-033` retest. §1–§11 are preserved
> exactly as originally written — read them as the prior comparative-design stage's own record,
> superseded only where §12 says so, not retroactively edited.

**Status: CANDIDATE-METHOD DIAGNOSTIC OUTPUT ONLY. Not an accepted production statistic, not a
calibration, not an operating threshold, not a consensus/panel conclusion.** Every number in
this document is labeled as such and must be read as such. This study does not promote any
candidate normalized-residual definition to "the methodology" — it exists to give DFA a
transparent, comparable basis for selecting among a small candidate set at a later, separately
authorized calibration stage.

**Authorization**: PO decision, 2026-09-04 — "Cross-sectional dispersion methodology design is
now REACTIVATED under bounded scope. Calibration, thresholds, suppression rules, and production
use remain deferred." Full decision record: `workbench/docs/ACTION_PLAN.md` §15j;
`workbench/docs/DECISIONS.md`, 2026-09-04 entry.

**Scope boundary, stated once, binding throughout this document**: methodology design only.
Uses only the five already-established, evidence-qualified `2026-09-02` pair-specific
implied-FX observations already recorded at `ACTION_PLAN.md` §15h. No new HistFinTS pair, date,
or ratio curation was performed for this study. No historical raw-price CV methodology,
`P90 CV 0.167`, operating threshold, PASS/FAIL dispersion classification, suppression rule,
consensus FX, representative-panel conclusion, CCL, fair value/mispricing, arbitrage,
recommendation, or trade/execution meaning is computed, adopted, or implied anywhere below.

---

## 1. The financial question

On a given date, how heterogeneous are the evidence-qualified CEDEAR ↔ underlying pair-specific
implied-FX estimates after expressing their differences on a common relative scale?

This is a methodology-design question — what is a technically sound way to *express* the
heterogeneity these five independent numbers already show — not a question about what any
operating consequence of that heterogeneity should be.

## 2. Evidence used — the five `2026-09-02` pair-specific results

Every value below is taken verbatim from `ACTION_PLAN.md` §15h, itself independently
re-verified live against the production database before this study began (spot-check: `implied-
fx 11305/11355/11324/11326/11328 2026-09-02`, all five reproduced exactly).

| Pair | Series (CEDEAR → underlying) | Ratio | Assertion `id` | Implied FX |
|---|---|---|---|---|
| AAPL | `11305 → 33` | `20:1` | `2` | `1591.5805440667510` |
| Banco Bradesco | `11355 → 972` | `1:1` | `3` | `1592.7536011743740` |
| Microsoft | `11324 → 6602` | `30:1` | `4` | `1591.7233371077455` |
| MercadoLibre | `11326 → 6319` | `120:1` | `5` | `1589.5703484805817` |
| QQQ | `11328 → 8193` | `20:1` | `6` | `1593.2547735028038` |

No pair, date, or value was added, dropped, or substituted for this study.

## 3. Candidate normalized-residual definitions

Per instruction, comparing only the smallest set needed to expose meaningful methodological
differences: **two candidates**, both centered on the same robust same-date center (the sample
median at `n=5`), differing only in the residual transform.

### 3.1 Robust center: same-date median

At `n=5` (odd), the median is the middle-ranked value, not a computed blend of any two — no
interpolation is needed. Sorted values:

```
1589.5703484805817  (MELI)
1591.5805440667510  (AAPL)
1591.7233371077455  (MSFT)   <- median (3rd of 5)
1592.7536011743740  (Bradesco)
1593.2547735028038  (QQQ)
```

**Center = `1591.7233371077455`** (MSFT's own value).

**A structural property worth naming explicitly, not glossed over**: at odd `n`, the
median-as-center is always exactly one member's own observed value. That member's residual is
therefore *exactly zero by construction* — a fact about the ranking, not a claim that member's
estimate is more accurate than the other four. A reader must not mistake MSFT's zero residual
below for evidence of correctness; it is an artifact of choosing the median at odd `n`, and a
different member would occupy that role on a different date purely from reordering.

Median was chosen over the arithmetic mean as the *only* robust-center candidate carried
forward, per the instruction to compare the smallest useful set — the mean is shown once, in
§3.4, only to make this choice's consequence visible, not as a second candidate center.

### 3.2 Candidate A — percentage-relative residual around the median

**Definition**: for each pair `i`, `residual_i = (value_i − median) / median × 100%`.

| Pair | Value | Diff from median | Residual (%) |
|---|---|---|---|
| MELI | `1589.5703484805817` | `−2.1529886271637224` | `−0.1352614852701619%` |
| AAPL | `1591.5805440667510` | `−0.1427930409945475` | `−0.0089709711270560%` |
| MSFT | `1591.7233371077455` | `0.0000000000000000` | `0.0000000000000000%` |
| Bradesco | `1592.7536011743740` | `+1.0302640666284333` | `+0.0647263279120154%` |
| QQQ | `1593.2547735028038` | `+1.5314363950583356` | `+0.0962124735722632%` |

### 3.3 Candidate B — log-relative residual around the median

**Definition**: for each pair `i`, `residual_i = ln(value_i / median) × 100`.

| Pair | Value | `ln(value/median)` | Residual (×100) |
|---|---|---|---|
| MELI | `1589.5703484805817` | `−0.0013535304619091` | `−0.1353530461909077%` |
| AAPL | `1591.5805440667510` | `−0.0000897137354274` | `−0.0089713735427356%` |
| MSFT | `1591.7233371077455` | `0.0000000000000000` | `0.0000000000000000%` |
| Bradesco | `1592.7536011743740` | `+0.0006470538945903` | `+0.0647053894590283%` |
| QQQ | `1593.2547735028038` | `+0.0009616621903794` | `+0.0961662190379438%` |

### 3.4 Reference only, not a third candidate — mean-centered percentage residual

Arithmetic mean of the five values: `1591.7765208664512`. Shown once to make the median-vs-mean
choice's consequence visible, not carried forward as a candidate:

| Pair | Residual around mean (%) |
|---|---|
| MELI | `−0.1385981233514198%` |
| AAPL | `−0.0123118287731478%` |
| MSFT | `−0.0033411573803558%` |
| Bradesco | `+0.0613830079231775%` |
| QQQ | `+0.0928681015817459%` |

Unlike the median, the mean is influenced by every member simultaneously and is not the exact
value of any one of them — no member's residual is exactly zero under mean-centering, which
avoids §3.1's own "structural zero" artifact, but the mean is materially more sensitive to a
single distant member at `n=5` (see §5).

### 3.5 Symmetry/asymmetry properties

- **Candidate A (percentage-relative)** is symmetric in the ordinary arithmetic sense — a
  value `x%` above the center and one `x%` below are numerically opposite, but the underlying
  percentage scale itself is not symmetric under inversion: a value twice the center is `+100%`,
  while a value half the center is `−50%`, not `−100%`. At the magnitudes observed here
  (residuals under 0.14% in either direction), this asymmetry is negligible — worth naming as a
  property of the definition, not as a finding about today's data.
- **Candidate B (log-relative)** is exactly symmetric under inversion by construction:
  `ln(2x/x) = −ln(0.5x/x)` in magnitude. This is the log transform's own standard property, not
  specific to this dataset. At today's small magnitudes, Candidates A and B are numerically
  almost indistinguishable (see §3.6) — the symmetry difference would only become material at
  much larger dispersion than observed here.

### 3.6 A and B compared directly

| Pair | Candidate A (%) | Candidate B (%) | Difference (A − B) |
|---|---|---|---|
| MELI | `−0.1352614852701619` | `−0.1353530461909077` | `+0.0000915609207458` |
| AAPL | `−0.0089709711270560` | `−0.0089713735427356` | `+0.0000004024156796` |
| MSFT | `0.0000000000000000` | `0.0000000000000000` | `0.0000000000000000` |
| Bradesco | `+0.0647263279120154` | `+0.0647053894590283` | `+0.0000209384529871` |
| QQQ | `+0.0962124735722632` | `+0.0961662190379438` | `+0.0000462545343194` |

At the magnitudes present in this dataset (all residuals under ±0.14%), `ln(1+x) ≈ x` holds to
high precision, so Candidates A and B are numerically near-identical — the largest observed
difference between them is about `9.2×10⁻⁵` percentage points (MELI). **This is itself a
methodological finding, not a coincidence of this dataset**: the two candidates only diverge
meaningfully at larger dispersion magnitudes than this five-pair, single-date sample happens to
show. A future calibration exercise over a wider or more volatile sample could reveal a real
practical difference between A and B that this study's own small, low-dispersion sample cannot.

## 4. Independence / mechanical-dependence diagnostic

**Method**: direct, read-only queries against the live production database — `series`,
`provider_assignment`, `provider`, `import_run`, and `observation`, tracing each of the ten legs
(five CEDEAR, five underlying) back to the exact provider and import run that produced the
specific `2026-09-02` row each pair's calculation actually used. Cross-referenced against this
project's own prior `F-033` filing (`docs/histfints-requests/DEFECT-F033-shared-driver-
mechanism.md`, `docs/evidence/DEFECT-F033.md`), still recorded `LIVE`/blocking as of this
session's own most recent check (§15d).

### 4.1 Series/provider lineage, both legs, all five pairs

| Pair | CEDEAR Series | CEDEAR live-priority provider | Underlying Series | Underlying provider |
|---|---|---|---|---|
| AAPL | `11305` | Yahoo Finance (`AAPL.BA`) | `33` | Yahoo Finance (`AAPL`) |
| Bradesco | `11355` | Yahoo Finance (`BBD.BA`) | `972` | Yahoo Finance (`BBD`) |
| Microsoft | `11324` | Yahoo Finance (`MSFT.BA`) | `6602` | Yahoo Finance (`MSFT`) |
| MercadoLibre | `11326` | Yahoo Finance (`MELI.BA`) | `6319` | Yahoo Finance (`MELI`) |
| QQQ | `11328` | Yahoo Finance (`QQQ.BA`) | `8193` | Yahoo Finance (`QQQ`) |

**No observation stream is reused across members** — confirmed: ten distinct `Series` ids (five
CEDEAR, five underlying), no id shared between any two of the five pairs. **No member is derived
from another selected member's price stream** — each `Series` has its own independent
`provider_assignment` chain; no CEDEAR or underlying Series in this five-pair set references
another selected Series as a source.

**All ten legs' `2026-09-02` observation rows are directly traced to Yahoo Finance
(`provider_id=2`)** — confirmed via `import_run.provider_assignment_id` → `provider_assignment`
→ `provider` for every one of the specific rows the calculation actually consumed, not merely
the Series' configured priority list. This is a genuine, material shared-infrastructure fact:
**all five pairs, both legs, on this one date, depend on the same single upstream data
provider.** Per instruction, provider commonality by itself is not disqualifying — a systemic
Yahoo Finance outage, timestamp-selection convention, or scale/currency handling quirk would
affect all five pairs identically, which is exactly the kind of *expected* shared exposure a
BYMA-CEDEAR panel structurally carries (all CEDEARs trade the same venue, all quoted against the
same underlying US listings, typically through the same handful of commercial data vendors) —
distinct from a *constructed*, mechanically-forced similarity.

### 4.2 `F-033`-type shared-driver contamination — checked specifically, three of five pairs
directly implicated in the historical finding

`F-033` (filed `2026-08-18`, deepened `2026-08-19`, still recorded `LIVE`/blocking as of this
session's `§15d`) found that a cohort of seven CEDEAR series — **including three of today's five
selected pairs: `MSFT` (`11324`), `MercadoLibre` (`11326`), and `QQQ` (`11328`)** — showed
day-over-day implied-FX return correlation of **exactly `+1.00`** with each other over their
deep-history window (everything before `2026-05-29`), against `+0.04` to `+0.91` for six other,
unflagged CEDEAR series checked the same way. The filing's own diagnosis: all seven series'
pre-`2026-05-29` history is sourced from a `provider_assignment` whose
`provider_series_identifier` is literally `"BACKFILL_{TICKER}"` under a provider labeled
`"BYMA"` — read by the filing's own authors as an internal batch/reprocessing artifact, not a
live market-data fetch, and diagnosed as either (a) all seven mathematically derived from one
shared input series with a per-series multiplier, or (b) a pipeline bug writing one series'
movement into all seven under different labels. **Neither mechanism has been confirmed resolved
in this repository's own records** — no closure entry for `F-033` was found.

**Checked directly for this study's own `2026-09-02` date specifically**: every one of the ten
legs' `2026-09-02` rows (§4.1 above) is traced to the **live Yahoo Finance provider**
(`provider_id=2`, `provider_series_identifier` values like `MSFT.BA`/`MELI.BA`/`QQQ.BA` and
`MSFT`/`MELI`/`QQQ`), **not** the `BACKFILL_` provider (`provider_id=3`) `F-033` flagged. The
`2026-09-02` date falls well inside the live-data window (`2026-05-29` onward) `F-033`'s own
filing itself distinguishes from the contaminated deep-history window. The five CEDEARs' own
`2026-09-02` intraday observed values are visibly instrument-distinct, not a shared constant or
a rescaled duplicate of one another (e.g. `25,860`/`AAPL` vs. `26,360`/`MSFT` vs. `26,580`/`MELI`
vs. `56,500`/`QQQ` vs. `5,495`/`Bradesco` — different price levels, different intraday shapes,
consistent with genuinely independent per-instrument fetches).

**This study's own honest limitation, stated rather than glossed over**: this pass verified
*provider/import-run lineage* and *price-level distinctness* for the one date in question — it
did **not** re-run `F-033`'s own day-over-day *return-correlation* diagnostic (the test that
actually detected the `+1.00` signature after price-level distinctness had already returned,
per the filing's own `2026-08-19` finding — see §"Same test, re-run 2026-08-19" in that
document). **Distinct price levels on one date do not, by themselves, rule out `F-033`'s own
deeper concern** (identical *day-over-day movement*, which the filing's own re-diagnosis found
survived even after the original bit-identical-value symptom disappeared). **Conclusion for this
study**: `MSFT`, `MELI`, and `QQQ`'s `2026-09-02` observations are sourced from the live
provider, not the flagged `BACKFILL_` mechanism, and show instrument-distinct price levels — but
`F-033`'s own unresolved concern about correlated *movement* for these same three tickers has
not been independently re-tested here and must not be read as cleared by this study. **This is
the single most consequential independence caveat in this report** — three of five selected
members carry a live, filed, unresolved defect naming exactly the kind of mechanical dependence
a dispersion methodology exists to detect, and this study's own scope did not extend to
re-running that specific diagnostic.

### 4.3 Instrument-class/issuer relationships

No two of the five selected pairs share an issuer, instrument class, or corporate relationship
that would itself mechanically link their prices: AAPL and Microsoft and Amazon-adjacent
comparators are absent from this set; the five are Apple (technology, US-domestic), Banco
Bradesco (Brazilian bank, ADR-style underlying rather than a US-domestic common stock), Microsoft
(technology, US-domestic), MercadoLibre (Latin American e-commerce, US-domestic-listed), and QQQ
(a Nasdaq-100 index-tracking ETF — its own "underlying" is itself a basket, not a single
company). **QQQ's own structural distinctness is worth naming explicitly**: as an index ETF, its
implied-FX estimate reflects a basket-level price, not a single-company fundamental — it is not
"more independent" or "less independent" than the other four for that reason, but a reader
comparing residuals across the five should not treat QQQ's residual as directly comparable in
kind to a single-company CEDEAR's residual, since the underlying instrument classes differ.

### 4.4 Independence findings, summarized per pair

| Pair | Provider lineage | `F-033` cohort member? | Independence assessment |
|---|---|---|---|
| AAPL | Yahoo Finance, live | No | No known contamination; distinct Series both legs |
| Bradesco | Yahoo Finance, live | No | No known contamination; distinct Series both legs; ADR-style underlying (not a single US-domestic common stock) |
| Microsoft | Yahoo Finance, live (`2026-09-02` specifically) | **Yes — flagged, unresolved** | `2026-09-02` observation confirmed live-sourced, not `BACKFILL_`; `F-033`'s own correlation concern not re-tested this pass |
| MercadoLibre | Yahoo Finance, live (`2026-09-02` specifically) | **Yes — flagged, unresolved** | Same as Microsoft |
| QQQ | Yahoo Finance, live (`2026-09-02` specifically) | **Yes — flagged, unresolved** | Same as Microsoft; additionally structurally distinct (index ETF, not single-company) |

## 5. Sensitivity to cohort membership at `n=5`

Leave-one-out median, recomputed and independently confirmed:

| Excluded pair | New median (`n=4`) | Shift from full-`n=5` median |
|---|---|---|
| AAPL | `1592.2384691410598` | `+0.5151320333143` |
| Bradesco | `1591.6519405872482` | `−0.0713965204973` |
| MSFT | `1592.1670726205625` | `+0.4437355128170` |
| MELI | `1592.2384691410598` | `+0.5151320333143` |
| QQQ | `1591.6519405872482` | `−0.0713965204973` |

**No pair has disproportionate influence on the median** by the usual robust-statistic
standard — the largest shift (`+0.515`, about `0.032%` of the center) occurs whether AAPL or
MELI is dropped, and is small in absolute terms. This is expected, structurally-guaranteed
behavior for a median at small `n`, not a finding specific to today's data: a median can shift by
at most one rank-position's worth of value when one member is removed, which bounds its
sensitivity by construction, unlike the mean (§3.4), which every member influences
simultaneously and which would shift by a different, generally larger amount if the *most
extreme* member (MELI, the largest-magnitude residual) were removed instead of an arbitrary one.

**Full range**: `1593.2547735028038 − 1589.5703484805817 = 3.6844250222221` (about `0.231%` of
the median) — the entire five-pair spread, for reference, not itself a dispersion statistic.

## 6. Interpretability advantages/disadvantages

**Candidate A (percentage-relative)**:
- *Advantage*: immediately legible to a non-technical reader — "0.135% below the median" needs
  no transform to interpret.
- *Disadvantage*: not symmetric under inversion at large magnitudes (§3.5) — a property that
  does not matter at today's small residuals but would need naming again if this method is later
  applied to a wider or more volatile sample.

**Candidate B (log-relative)**:
- *Advantage*: exactly symmetric under inversion at any magnitude — a technically cleaner
  property for a methodology intended to generalize beyond today's narrow, low-dispersion
  sample.
- *Disadvantage*: less immediately legible to a non-technical reader ("a log-ratio of
  `0.00065`" requires more explanation than "0.065% above the median"); at the magnitudes
  observed today, offers no numerically distinguishable benefit over Candidate A (§3.6).

## 7. Numerical/pathological behavior relevant to future use

- **Structural zero at odd `n` under median-centering** (§3.1) — the member occupying the
  median rank always reads as a zero residual regardless of its own true accuracy. A future
  presentation of this methodology must guard against a reader mistaking this for a correctness
  signal.
- **Division-by-center degeneracy**: both candidates divide by the center value; a center of
  zero or near-zero would make either candidate numerically unstable or undefined. Not a live
  concern for implied-FX magnitudes in the thousands, as observed here, but worth naming as a
  standing precondition for any future generalization to a quantity that could legitimately
  approach zero.
- **Log-transform domain restriction**: Candidate B requires every value and the center to be
  strictly positive (`ln` undefined at zero or negative). Implied-FX values are structurally
  positive under this project's own accepted formula (`CEDEAR × ratio ÷ underlying`, all three
  factors positive), so this is not a live concern today, but is a real constraint Candidate B
  carries that Candidate A does not.
- **Small-`n` fragility, general**: both the median and the mean are known to be volatile
  descriptive statistics at `n=5` — §5's own leave-one-out results already show this concretely.
  This is not itself a defect in either candidate; it is a property of small-sample cross-
  sectional description that any future calibration must account for before promoting either
  candidate (or any threshold built on either) to production use.

## 8. Candidates rejected outright, and why

**None of the two compared candidates (A, percentage-relative; B, log-relative) is rejected
outright** — both are technically sound, well-behaved at the magnitudes observed, and each
carries a real, named trade-off (§6) rather than a disqualifying flaw.

**Explicitly rejected as a candidate, not merely deferred**: the historical `2026-08-18` raw
price-level CV methodology (`ACTION_PLAN.md`/`DECISIONS.md` §15d) — its own computational
provenance is unrecoverable, its `P90 CV 0.167` figure remains an unverified historical artifact,
and per §15d's own binding instruction, any future calibration "must be produced using the
then-governing normalized methodology... rather than attempting merely to reproduce `0.167`."
This study's own two candidates are both explicitly *normalized* (relative-to-center) measures,
consistent with that instruction — the raw, un-normalized price-level approach is not carried
forward as a live candidate here.

## 9. Smallest candidate set worth taking back to DFA for financial methodology selection

**Both Candidate A (percentage-relative) and Candidate B (log-relative) residuals around the
same-date median** — this is already the smallest set that exposes a real, named methodological
difference (symmetry under inversion, §3.5) between two well-behaved, normalized approaches. A
smaller set (one candidate only) would not let DFA weigh that trade-off at all; a larger set
would not add a materially different methodological question at this dataset's own observed
magnitudes (§3.6's own finding — A and B are numerically near-identical here, so a third
variant would not expose anything the first two do not already show).

## 10. Exact evidence still missing before calibration could begin

1. **`F-033`'s own return-correlation diagnostic, re-run against current data for `MSFT`/
   `MELI`/`QQQ` specifically** (§4.2) — the single most material open item. Calibration cannot
   responsibly proceed with three of a candidate cohort's five members carrying an unresolved,
   filed independence concern, even though today's specific date shows no price-level red flag.
2. **A wider evidence-qualified pair population.** Five pairs, one date, is sufficient for
   methodology *design comparison* (this study's own scope) but not for any calibration —
   `SPEC-panel-eligibility.md`'s own established discipline (§8.5, cited throughout this
   project's prior calibration work) requires representativeness, temporal/regime diversity, and
   sufficient population, none of which a single date can supply.
3. **A resolution to the shared-provider concentration named in §4.1** — not disqualifying by
   itself, but a future calibration package should document whether any of the five pairs' data
   is ever cross-checked against a second, independent provider, since all five currently trace
   to one upstream source for this date.
4. **DFA's own selection between Candidate A and Candidate B** (or an explicit statement that
   the choice is immaterial at the magnitudes expected in production) — this study documents the
   trade-off (§6) but does not, and is not authorized to, make that selection.
5. **A settled robust-center definition for `n` other than 5**, and for even `n` specifically
   (where the median becomes an average of two values, not one member's own exact value) — this
   study's own §3.1 finding (the structural-zero artifact) applies only to odd `n`; calibration
   over a variable-size future population will need this addressed before the same
   candidate can be applied unmodified.

## 11. What this document does not do

Does not define an operating dispersion threshold, suppression rule, or PASS/FAIL
classification. Does not compute or adopt a consensus FX rate, representative-panel conclusion,
CCL, fair value, mispricing, arbitrage, recommendation, or trade/execution interpretation. Does
not add a pair or a date beyond the five already-established `2026-09-02` observations. Does not
claim `F-033` resolved, or claim today's price-level distinctness clears its own unresolved
return-correlation concern. Does not promote Candidate A or Candidate B to "the methodology."
Does not reactivate calibration — that remains a separately authorized, DFA-gated future stage.
Does not modify HistFinTS, `histfints_uiue`, or any production data — read-only throughout.

---

## 12. DFA's methodology rulings and the next bounded design increment (2026-09-04, additive)

**Recorded exactly as relayed, attributed to DFA — not self-certified or re-derived by SDT-WB.**
§1–§11 above preserved exactly as originally written. This section performs the next bounded
design increment DFA's rulings authorize, using the same five `2026-09-02` observations only —
no new pair, no new date, no `F-033` retest.

### 12.1 Governing design choice, recorded exactly as instructed

**Primary residual representation: `LOG_RELATIVE`, around the provisional same-date median.**
For pair `i`, `LOG_RELATIVE_i = ln(value_i / median)` — the log ratio between that pair's own
implied-FX value and the same-date median center, sign and dimensionless interpretation
preserved (a negative value means below the center on a log scale, a positive value means
above; the quantity itself carries no unit, matching a log-ratio's own standard interpretation).
**`PERCENTAGE_RELATIVE` is no longer a co-equal candidate** — it remains available only as a
diagnostic cross-check demonstrating numerical similarity/difference against `LOG_RELATIVE`, per
§12.3 below, never silently substituted for it.

**The provisional same-date median remains accepted for methodology design only** — restated
per instruction: not yet an approved calibration or production center. Its own value is
unchanged from §3.1: **`1591.7233371077455`** (MSFT's own `2026-09-02` value — the odd-`n`
structural-zero property named in §3.1/§7 applies identically here and is not re-derived).

### 12.2 `LOG_RELATIVE` residuals, exact, for each of the five pairs

`LOG_RELATIVE_i = ln(value_i / 1591.7233371077455)`, independently recomputed and confirmed:

| Pair | Value | `LOG_RELATIVE` (dimensionless) | Sign, relative to provisional center |
|---|---|---|---|
| AAPL | `1591.5805440667510` | `−0.0000897137354274` | below |
| Banco Bradesco | `1592.7536011743740` | `+0.0006470538945903` | above |
| Microsoft | `1591.7233371077455` | `0.0000000000000000` | at center (structural zero, §3.1/§7 — not a correctness signal) |
| MercadoLibre | `1589.5703484805817` | `−0.0013535304619091` | below |
| QQQ | `1593.2547735028038` | `+0.0009616621903794` | above |

Sign is interpreted only and exactly as instructed: whether the pair's own implied-FX value sits
above or below the provisional same-date center on this log scale — no further meaning (no
"outlier," "anomaly," or "error" characterization attaches to sign or magnitude anywhere in this
record).

### 12.3 `PERCENTAGE_RELATIVE`, diagnostic cross-check only, shown beside `LOG_RELATIVE`

| Pair | `LOG_RELATIVE` | `PERCENTAGE_RELATIVE` (diagnostic only) | Difference |
|---|---|---|---|
| AAPL | `−0.0000897137354274` | `−0.0000897097112706` | `−0.0000000040241568` |
| Bradesco | `+0.0006470538945903` | `+0.0006472632791202` | `−0.0000002093845299` |
| MSFT | `0.0000000000000000` | `0.0000000000000000` | `0.0000000000000000` |
| MELI | `−0.0013535304619091` | `−0.0013526148527016` | `−0.0000009156092075` |
| QQQ | `+0.0009616621903794` | `+0.0009621247357226` | `−0.0000004625453432` |

Confirms §3.6's own finding again, now with `LOG_RELATIVE` as primary: at today's small
magnitudes the two are numerically near-identical (largest difference ≈ `9.16×10⁻⁷` in raw
ratio terms, i.e. about `9.16×10⁻⁵` percentage points) — `PERCENTAGE_RELATIVE`'s role here is
exactly what DFA's ruling assigns it: a cross-check confirming the two representations agree
closely at this scale, not an independent second methodology.

### 12.4 Inversion-property demonstration

**Claim to demonstrate**: reversing the FX quote convention (e.g. underlying-per-CEDEAR instead
of CEDEAR-per-underlying — equivalently, using `1/value` and `1/median` instead of `value` and
`median`) changes `LOG_RELATIVE`'s sign without changing its magnitude.

**Computed directly, not asserted**: for each pair, `LOG_RELATIVE_inverted = ln((1/value_i) /
(1/median))`.

| Pair | `LOG_RELATIVE` (original quote) | `LOG_RELATIVE` (inverted quote) | Sum (should be ≈0) |
|---|---|---|---|
| AAPL | `−0.0000897137354274` | `+0.0000897137354274` | `4.88×10⁻¹⁷` |
| Bradesco | `+0.0006470538945903` | `−0.0006470538945902` | `1.07×10⁻¹⁶` |
| MSFT | `0.0000000000000000` | `0.0000000000000000` | `0.0000000000000000` |
| MELI | `−0.0013535304619091` | `+0.0013535304619091` | `3.10×10⁻¹⁷` |
| QQQ | `+0.0009616621903794` | `−0.0009616621903795` | `−4.40×10⁻¹⁷` |

**Confirmed exactly**: `ln(1/x) = −ln(x)` is an algebraic identity, and this holds numerically
here to the limit of IEEE double-precision floating-point representation (residual sums on the
order of `10⁻¹⁷`, i.e. exactly zero to the precision available) — every pair's sign flips
between the two quote conventions while its magnitude is preserved to full numerical precision.
This is the exact inversion-symmetry property §3.5 already named for `LOG_RELATIVE` in the
abstract; this section demonstrates it concretely, on this dataset, both ways.

### 12.5 Cohort-membership sensitivity at `n=5`, already relevant

Restated from §5, unchanged (the residual definition change does not alter which pair occupies
which rank, so the leave-one-out median-shift table is identical regardless of `LOG_RELATIVE` vs
`PERCENTAGE_RELATIVE`):

| Excluded pair | New median (`n=4`) | Shift from full-`n=5` median |
|---|---|---|
| AAPL | `1592.2384691410598` | `+0.5151320333143` |
| Bradesco | `1591.6519405872482` | `−0.0713965204973` |
| MSFT | `1592.1670726205625` | `+0.4437355128170` |
| MELI | `1592.2384691410598` | `+0.5151320333143` |
| QQQ | `1591.6519405872482` | `−0.0713965204973` |

**The median-member exact-zero structural effect (§3.1/§7) is already relevant at `n=5`,
restated precisely for `LOG_RELATIVE`**: because the median is defined as one member's own
value at odd `n`, that member's `LOG_RELATIVE` residual is `ln(median/median) = ln(1) = 0`
exactly, by algebraic necessity — not because MSFT's own estimate is more accurate than the
other four. A future presentation of `LOG_RELATIVE` residuals must carry this caveat explicitly,
every time, not only in a methodology appendix.

**No threshold or PASS/FAIL classification is computed anywhere in this section.**

### 12.6 Calibration-eligibility table, methodology-design membership recorded separately from
future calibration eligibility, exactly as instructed

| Pair | Methodology-design membership | Calibration eligibility |
|---|---|---|
| AAPL | Permitted | No `F-033` exclusion currently identified |
| Banco Bradesco | Permitted | No `F-033` exclusion currently identified |
| Microsoft | Permitted | **CALIBRATION-INELIGIBLE while `F-033` unresolved** |
| MercadoLibre | Permitted | **CALIBRATION-INELIGIBLE while `F-033` unresolved** |
| QQQ | Permitted | **CALIBRATION-INELIGIBLE while `F-033` unresolved** |

**Recorded exactly as instructed**: common Yahoo Finance provider usage alone is not a
disqualifier for any of the five (§4.1's own finding, unaffected) — the specific, unresolved
`F-033` shared-process/deep-history evidence (§4.2) is the calibration concern for Microsoft,
MercadoLibre, and QQQ specifically, not provider commonality in general. **`F-033` was not
retested in this increment** — its status is carried forward exactly as §4.2 recorded it, not
re-verified again here.

### 12.7 Remaining prerequisites before calibration could begin

Unchanged in substance from §10, restated with the calibration-eligibility split now explicit:

1. A fresh `F-033` return-correlation re-test, specifically for Microsoft, MercadoLibre, and
   QQQ — the item that would resolve or confirm their `CALIBRATION-INELIGIBLE` status.
2. A wider evidence-qualified pair population across dates/regimes — five pairs, one date,
   remains sufficient only for design comparison, not calibration.
3. Documentation of the shared-provider concentration (§4.1) for any future calibration package.
4. **DFA's own confirmation that the provisional same-date median may be promoted to an approved
   calibration/production center** — this section's own governing instruction states the median
   remains provisional "for methodology design only"; that promotion is a separate, not-yet-made
   decision.
5. A settled robust-center definition for `n` other than 5, including even `n` (§10's own item 5,
   unaffected by today's `LOG_RELATIVE` promotion).

### 12.8 New methodological ambiguity exposed by this increment, requiring DFA review

**One, worth naming precisely rather than glossing over**: `LOG_RELATIVE`'s inversion-symmetry
property (§12.4) is exact only relative to the *quote convention* (which leg is numerator).
**It does not, and cannot, address whether the provisional median itself is invariant under the
same inversion** — i.e., whether `median(1/value_1, ..., 1/value_5)` equals `1/median(value_1,
..., value_5)`. For an odd-`n` sample this holds exactly for the *median specifically* (median
commutes with any monotonic transform, and `x → 1/x` is monotonic on positive reals), so today's
provisional median does carry this property — but this is a property of the median as a
statistic, not a property `LOG_RELATIVE` itself guarantees for every possible robust-center
choice. **This matters for prerequisite §12.7 item 4**: if a future robust-center candidate
other than the median is ever proposed (e.g. a trimmed mean), DFA should confirm whether
quote-convention invariance is a requirement for that candidate too, since not every robust
statistic shares the median's own monotonic-transform-commutation property. Not resolved here —
named for DFA's awareness before any center other than the median is considered.

**No other new ambiguity identified.** `LOG_RELATIVE`'s own definition, sign interpretation, and
relationship to `PERCENTAGE_RELATIVE` are all fully specified by DFA's ruling and this section's
own transparent calculations — nothing further requires DFA's interpretation to compute or
present `LOG_RELATIVE` for this five-pair, single-date sample.

### 12.9 What this section does not do

Does not compute or adopt an operating dispersion threshold, suppression rule, consensus/panel
FX, production center, calibration statistic, raw-price CV, or the historical `P90 CV 0.167`.
Does not compute CCL, fair value/mispricing, arbitrage, recommendation, or trade/execution
logic. Does not retest `F-033`. Does not add a pair or a date. Does not promote the provisional
median to an approved calibration/production center. Does not modify HistFinTS, `histfints_uiue`,
or any production data — read-only throughout.
