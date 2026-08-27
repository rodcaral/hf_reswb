# Evidence Matrices — B/D/Class-C Duplication-Identity Problem

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE, for routing to DFA
**Status: read-only evidence analysis only. No observation deletion, reassignment,
provider-assignment repointing, provenance modification, or other A–F remediation executed,
staged, or authorized. The seven previously adjudicated Class-C rows (seven-pair episode,
value-correct / attribution finding accepted) are preserved unchanged and not reopened.**

**Every figure below was retrieved fresh, read-only, for this report. Where a figure from SE's
framing (e.g. "400") could not be exactly reproduced, that is stated explicitly in place of
forcing a match — consistent with this project's standing practice of reporting a
discrepancy rather than resolving it silently (cf. the 2026-08-19 F-033 correlation
reconciliation).**

---

## Matrix 1 — D's Seven Target/Referrer Relationships

For each of the seven CEDEAR series (the "referrer"), the currently-pointed-to
`underlying_series_id` (the "current target") and the independently-identified alternative
(the "proposed target") are compared on every field available.

| Ticker | Referrer (CEDEAR) | Current target | Proposed target |
|---|---|---|---|
| MU | 11323 | 11342 | 6672 |
| MSFT | 11324 | 11348 | 6602 |
| AMD | 11325 | 11349 | 426 |
| MELI | 11326 | 11350 | 6319 |
| NU | 11327 | 11351 | 7085 |
| QQQ | 11328 | 11352 | 8193 |
| AMZN | 11329 | 11353 | 484 |

### Directly observed fields (identical structure across all seven pairs — shown once, MU as exemplar, with per-pair exceptions noted)

| Field | Referrer (e.g. 11323) | Current target (e.g. 11342) | Proposed target (e.g. 6672) | Directly observed or inferred? |
|---|---|---|---|---|
| Label | "Micron Technology, Inc. CEDEAR (BYMA)" | "Micron Technology, Inc. - Stock (NASDAQ)" | "Micron Technology, Inc. - Common Stock" | **Observed.** All three name the same issuer ("Micron Technology, Inc.") in every one of the seven pairs — no pair shows a differing issuer name across its three series. |
| Currency | ARS | USD | USD | **Observed.** Current and proposed target agree with each other on currency in all seven pairs; referrer differs (ARS), consistent with a CEDEAR/underlying relationship in either direction. |
| `series_type` | STOCK (ETF for QQQ) | STOCK (ETF for QQQ) | STOCK (ETF for QQQ) | **Observed.** Instrument class matches across all three in every pair. |
| `configured_interval` | 1h | 1h | **1d** | **Observed.** Current target matches the referrer's granularity (1h); proposed target is daily. This is a real, structural difference — not evidence of different identity, but evidence the two candidate targets are fetched on different schedules. |
| `country` | None (not populated) | None (not populated) | **US** | **Observed.** Proposed target carries a populated `country` field the other two lack — a metadata completeness difference, not identity evidence either way. |
| Provider / identifier (priority-1 assignment) | Yahoo Finance, `"{TICKER}.BA"` | Yahoo Finance, `"{TICKER}"` (plain) | Yahoo Finance, `"{TICKER}"` (plain) | **Observed.** Current and proposed target use the **identical provider and identical provider-side symbol** in all seven pairs — e.g. both request `"MU"` from Yahoo Finance. Per the provider's own addressing scheme, this is the strongest available evidence that current and proposed target reference the same real-world instrument, not two different ones — **the provider itself does not distinguish them.** |
| `adjustment_basis` | SPLIT_ADJUSTED | SPLIT_ADJUSTED | SPLIT_ADJUSTED | **Observed.** All three agree, in all seven pairs — no adjustment-convention mismatch evidenced. |
| Secondary assignment | (BACKFILL_*, MERVAL — not used for current values) | Twelve Data, plain ticker | (none) | **Observed.** Current target additionally carries a Twelve Data assignment; proposed target does not. Not evidence of differing identity — a second data source, if anything, reinforces that current target is configured as a genuine, actively-maintained series, distinct in configuration effort from a pure artifact. |
| `underlying_series_id` (own) | Points to current target | NULL | NULL | **Observed.** Neither target series itself claims a further underlying — both are leaf nodes in the FK graph, consistent with both being candidates for "the underlying," not further CEDEARs themselves. |
| `ratio` | 1.0 (all seven) | NULL | NULL | **Observed.** No ratio is asserted on either target — consistent with both being direct common-stock/ETF instruments requiring no conversion ratio of their own. |
| Creation timestamp | 2026-08-18 16:15:46 (all seven) | 2026-08-18 19:32–19:43 (postdates referrer by ~3–3.5h) | 2026-08-11 03:45 (predates referrer by ~7 days) | **Observed**, restated from the prior D package. |

### Evidence for vs. against "different securities/listings/share classes/depositary instruments"

**Against** (i.e., supporting same underlying identity, current vs. proposed target):
- Identical issuer name in the label text, all seven pairs.
- Identical provider + identical provider-side symbol (Yahoo Finance, plain ticker) — the
  provider's own system does not distinguish current from proposed target.
- Identical currency, instrument class, and adjustment basis.
- NU's proposed target label is more specific ("Class A Ordinary Shares") than either the
  referrer's or current target's generic "Stock"/"CEDEAR" label — this is additional
  specificity, not a conflicting identity claim; Nu Holdings' NYSE listing is in fact Class A
  ordinary shares, so this is consistent with, not contrary to, same-identity.

**For** (i.e., supporting a genuine difference — evidence found, not assumed):
- **`configured_interval` differs (1h vs. 1d).** This means current and proposed target are
  not simply two records of an identical fetch — they are configured to sample at different
  frequencies, which by itself would produce different stored values even for a genuinely
  identical instrument (an hourly snapshot and a daily close are not the same observation).
  **This is evidence of a sampling/configuration difference, not of a different security.**
- No field examined ties current target's identity to anything other than "Micron Technology,
  Inc." (or the corresponding issuer per pair) — no evidence was found supporting a genuine
  different-security explanation for any of the seven pairs.

**Explicit statement per instruction**: none of the seven pairs is classified as duplicate
financial identity in this matrix merely because timestamps, identifiers, or values overlap.
The classification basis here is the **provider-identifier match** (both target series request
the identical symbol from the identical provider) — a stronger, structural signal than
timestamp or value overlap alone, and it points toward same-identity for all seven, with the
`configured_interval` difference noted as a real, unresolved configuration discrepancy rather
than identity evidence.

**What was not established**: whether current target's Twelve Data secondary assignment ever
returned data materially different from Yahoo Finance's, and whether that would bear on
identity — not investigated in this pass.

---

## Matrix 2 — The Timestamp-Level Disagreements

**SE's framing cites "400" disagreements. This figure could not be exactly reproduced under
any comparison method tried in this pass. Reported below, with the discrepancy stated rather
than resolved.**

### Two data regimes exist within each current-target series — this must be separated before comparison

Before comparing current target to proposed target, a prior finding governs the comparison:
for all seven pairs, current target's value is **bit-identical to its own referrer CEDEAR**
(ratio exactly 1.0) on every date from series inception through **2026-05-27**, then departs
from the referrer entirely starting **2026-05-28** onward, tracking a plausible independent USD
value close to the proposed target from that date forward. This is the already-documented
F-033/same-date-scale-discontinuity transition (`SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md`),
re-confirmed here at the per-date level for MU specifically as an exemplar (identical pattern
found on spot-checks of the other six):

| Date | Referrer (11323) | Current target (11342) | Proposed target (6672) | ref/current | current/proposed |
|---|---|---|---|---|---|
| 2015-01-02 | 295.513 | 295.513 | 34.75 | **1.0** | 8.50 |
| 2020-03-16 | 2238.685 | 2238.685 | 34.47 | **1.0** | 64.95 |
| 2024-01-10 | 70327.691 | 70327.691 | 82.38 | **1.0** | 853.70 |
| 2026-05-27 | 936307.539 | 936307.539 | 928.41 | **1.0** | 1008.51 |
| 2026-08-17 | 1022349.075 | 1011.62 | 1011.75 | **1010.61** | 1.00 (0.13% apart) |

**Comparing current target to proposed target over the full deep-history range, without first
separating these two regimes, is not a meaningful "disagreement" count** — it mostly restates
the already-documented, already-explained F-033 defect, not a new finding. Matrix 2 is
therefore built only on the post-transition window, per series' own transition date.

### Post-transition comparison, all seven pairs

Transition date confirmed identical (2026-05-28) across all seven pairs by direct query (not
assumed to generalize from MU alone):

| Ticker | Live-window common dates (current vs. proposed) | Disagreements (>$0.01, close-price) | Disagreements (exact-timestamp match, any difference) |
|---|---|---|---|
| MU | 58 | 51 | 58 (no exact-timestamp match returns identical value) |
| MSFT | 58 | 47 | 58 |
| AMD | 58 | 52 | 58 |
| MELI | 58 | 52 | 58 |
| NU | 58 | 32 | 58 |
| QQQ | 58 | 56 | 58 |
| AMZN | 58 | 48 | 58 |
| **Total** | **406** | **338** | **406** |

**Neither total (406/338) equals 400 exactly.** 406 is the total count of calendar dates in
the live window where both current and proposed target have a value; 338 is the subset
disagreeing by more than one cent. 406 is close enough to "400" that it may be the intended
figure (a rounding or a slightly different date-boundary convention would move it by single
digits); this report does not assume that and states both numbers as retrieved.

### Characterization, by cause

**Magnitude and direction**: differences in the live window are small in relative terms
(typically well under 5%, consistent with normal intraday-vs-daily-close sampling
differences) — categorically different in character from the ~1,000× differences in the
pre-transition window, which belong to the already-documented defect, not to this
comparison.

**Currency/unit context**: both sides are USD in the live window; no unit mismatch.

**Corporate-action context**: not investigated per-date in this pass; no evidence of a
corporate action was found or looked for specifically within the 58-day live window, which is
short enough that a material corporate action affecting all seven names simultaneously in
this window would be a notable coincidence if not already documented elsewhere in this
project's work — none is on record.

**Provider/source availability**: both sides are sourced from the same provider (Yahoo
Finance) per Matrix 1, but at different intervals (1h vs. 1d) and, per the standing
`MANUAL`/`SCHEDULED` coexistence-by-design finding (`RECONCILIATION-F033-2026-08-19.md`),
potentially different fetch times within a trading day — sufficient to explain small
disagreements without invoking any deeper defect.

**Authoritative/independently reproducible historical value**: **not established in this
pass.** No current-source re-fetch was performed for this report (per SE/HistFinTS's standing
instruction not to manufacture large re-fetches to force a classification). The disagreements
above are stored-value comparisons only; whether either stored value matches the provider's
own historical record today is unknown and unproposed to be resolved here.

---

## Extreme Scale Range Investigation — Referrer CEDEAR Series, 125.15 … 1,224,728.52

**Population**: MU's own CEDEAR series (11323), full history, 2,924 daily values.

**Directly observed**:
- Minimum value 125.1523178680629, dated 2016-02-11.
- Maximum value 1,224,728.520705044, dated 2026-06-25 — **inside the post-transition live
  window**, confirming this is a value the CEDEAR series itself (not the corrupted-FK-target
  regime) actually carries; not an artifact of the pre-2026-05-28 duplicate-of-CEDEAR
  mechanism.
- Ratio, max/min: **9,786×** over the full history.
- **Exactly one** day-over-day change exceeding 50% in the entire 2,924-day series:
  2026-08-17 → 2026-08-18, a −70.96% drop (1,022,349 → 296,900) — **this is the already-
  documented and already-explained transition event**
  (`SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md`), not a newly-found discontinuity.
- **No other single-day change in the entire series exceeds 50%.** The trajectory from
  125.15 (2016-02-11) to 1,224,728.52 (2026-06-25) — nearly the full range in question — is
  gradual, with no discrete jump.

**Candidate explanations checked**:
- **Currency (ARS) depreciation over the period**: independently evidenced elsewhere in this
  project's own work — the implied-FX-like value shared (pre-transition) across the six
  circular pairs moved from ~14.18 (2016) to ~1,008.51 (2026), roughly a **71× drift**, over
  approximately the same span. This is a real, independently-derived figure from a different
  analysis (the F-033 shared-driver investigation), not asserted freshly here.
- **Underlying equity price movement**: the proposed target (6672, the real MU common stock)
  shows its own full-history ratio of **718×** (min $1.69, max $1,213.56) — a large range in
  its own right, reflecting Micron's real, well-documented multi-decade price history
  (including a genuine sub-$2 trough during 2008–2009 and substantial appreciation since).
- **Combined**: 71× (currency) × a plausible multiple of MU's real price appreciation over the
  CEDEAR's specific 2016–2026 window (not the full 718× figure, which spans a longer and
  differently-dated history than the CEDEAR's 2016-02-11-to-2026-06-25 window) is directionally
  consistent with, but not precisely reconciled to, the observed 9,786× CEDEAR ratio. **This
  report does not compute an exact reconciliation** — the two component ranges are measured
  over different, only partially-overlapping date windows, and forcing them into a single
  multiplicative check would overstate the precision of this evidence.

**Finding**: the 125.15…1,224,728.52 range shows **no evidence of a discrete
identity/currency/denomination/corporate-action-style jump** anywhere except the one already-
documented 2026-08-17→18 transition (which is outside this range's own explanation — that
transition is a change in *data source regime* for a different series, 11342, not a change
in the CEDEAR 11323's own reporting basis). The range is **directionally consistent** with
known, independently-evidenced currency depreciation combined with real equity appreciation,
but a precise multiplicative reconciliation was not established in this pass. **Per
instruction, this interval is reported as unresolved rather than labeled corrupted** — the
evidence available neither proves nor disproves commingling; it is consistent with organic
growth and inconsistent with a spliced/discontinuous data source, but "consistent with" is not
"proven."

---

## Evidence → Finding → Unresolved Question → Technical Consequence

### Population 1: Matrix 1 — the seven D target/referrer identity relationships

- **Evidence**: identical issuer name, currency, instrument class, and — most significantly —
  identical provider and provider-side symbol between current and proposed target, on all
  seven pairs. One real configuration difference (`configured_interval`, 1h vs. 1d).
- **Finding**: no evidence was found supporting that current and proposed target represent
  different securities, listings, share classes, or depositary instruments, for any of the
  seven pairs. The provider-identifier match is the strongest available signal and it is
  uniform across all seven.
- **Unresolved question**: whether the `configured_interval` difference (and the Twelve Data
  secondary source on current target only) reflects a deliberate, still-relevant configuration
  choice, or is itself an artifact of how current target was created — not established here.
- **Technical consequence**: if DFA treats the provider-identifier match as sufficient
  evidence of same identity, Matrix 1 does not identify a same-identity blocker for any of the
  seven D repointing candidates. It does not, by itself, authorize the repointing — that
  remains an SE/DFA decision this report does not make.

### Population 2: Matrix 2 — the post-transition live-window disagreements

- **Evidence**: 406 dates of overlap between current and proposed target since the
  2026-05-28 transition, 338 disagreeing by more than one cent, all at a magnitude consistent
  with ordinary intraday-vs-daily sampling difference, not with a deeper defect.
- **Finding**: these disagreements are categorically different in kind from the pre-transition
  regime's ~1,000× differences (which are the already-documented F-033 defect, not part of
  this population). SE's cited figure of "400" was not exactly reproduced; 406 is the closest
  figure obtained and is reported as such, not adjusted to match.
- **Unresolved question**: whether either stored value (current or proposed target) matches
  an authoritative, independently-reproducible historical record for any specific date — not
  established, and per standing instruction, not investigated via a fresh re-fetch in this
  pass.
- **Technical consequence**: this population does not, on the evidence gathered, indicate a
  identity or corruption problem — it is consistent with two legitimately-differently-sampled
  feeds of the same instrument. It does not resolve which of the two stored values (if either)
  should be treated as authoritative for any given date; that is an evidentiary gap, not
  answered here.

### Population 3: the extreme scale range, MU CEDEAR (11323), 125.15…1,224,728.52

- **Evidence**: smooth trajectory (one single already-documented discontinuity in 2,924 days),
  directionally consistent with independently-evidenced currency depreciation and real equity
  appreciation.
- **Finding**: no discrete, unexplained jump exists within this range. The scale span is not,
  on this evidence, proof of commingled or corrupted data.
- **Unresolved question**: a precise multiplicative reconciliation of the observed 9,786×
  ratio against the two component drivers (currency ~71×, equity range 718× over a differently
  -dated window) was not established.
- **Technical consequence**: per instruction, this interval is reported as **unresolved**, not
  labeled corrupted. It should not be used, on this evidence alone, to justify excluding or
  flagging this data as defective — nor should it be treated as fully explained/closed.

---

## What this report does not do

- Does not propose, stage, or execute any repair SQL.
- Does not reopen or modify the seven-row Class-C decision.
- Does not perform a fresh current-source re-fetch to force any classification.
- Does not infer or state a financial disposition — that determination is explicitly reserved
  for SE to route to DFA, per standing instruction.
- Does not broaden into general A–F implementation.
