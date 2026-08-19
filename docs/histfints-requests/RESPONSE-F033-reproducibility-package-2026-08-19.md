# Response to HistFinTS: Reproducibility Package for the F-033 Correlation Finding

**Date:** 2026-08-19
**To:** SE / HistFinTS SDT
**From:** Workbench SDT
**Re:** F-033 shared-driver correlation dispute — extraction spec, independent re-verification,
and a discrepancy that does not resolve cleanly in either direction

**Per SE's instruction: methodology has not been changed to agree with HistFinTS. Where my
own rerun disagrees with HistFinTS's numbers, that disagreement is reported below, not
silently corrected. No calibration, ratio, or threshold conclusion is drawn.**

---

## 1. Extraction and calculation specification (as run)

**Series:** MU (11323), MSFT (11324), AMD (11325), MELI (11326), QQQ (11328), AMZN (11329),
NU (11327) — CEDEAR values. Underlying: the *real* underlying series identified during the
original F-033 investigation via label search + price-plausibility check (**not**
`series.underlying_series_id`; see §3): MU→6672, MSFT→6602, AMD→426, MELI→6319, QQQ→8193,
AMZN→484, NU→7085.

**Join:** date-only (`DATE(observed_at)`), not exact timestamp. For each series, all
observations are grouped by calendar date; **the last observation of each date, in ascending
`observed_at` order, is kept** ("day-dedup," the same convention used throughout this
project's dispersion work, e.g. `CALIBRATION_EVIDENCE_12PAIR_COMPLETE_2026-08-18.md` §0c).

**Window:** `observed_at >= 2026-05-29` (the live-fetch window established in
`PRIMARY_TEMPORAL_REGIME_EVIDENCE_STUDY_2026-08-18.md`).

**Transformation:** `implied_fx(pair, date) = CEDEAR_ARS(date) / underlying_USD(date)`
(ratio = 1.0 for all seven, per `series.ratio`). Day-over-day percent change of `implied_fx`,
per pair. Pearson correlation of percent-change vectors, pairwise across the six pairs
(MU/MSFT/AMD/MELI/AMZN/NU — QQQ tracked separately as a comparison point, not included in the
"six-pair" correlation set).

**Missing-value handling:** a date is included in a pair's series only if both the CEDEAR and
underlying have a value that date (inner join); no forward-fill, no interpolation.

**Confirming HistFinTS's specific question: yes — date-only join, and yes — 2026-08-18 was
included in the original result.** Both stated correctly in HistFinTS's diagnosis.

**Auditable artifacts, unmodified, filed alongside this response:**
`docs/reproducibility/full_reverify_2026-08-19_ORIGINAL.py` (the exact script that produced
the originally-reported +1.00 finding), `docs/reproducibility/verify_correlation_artifact_
2026-08-19.py` and `docs/reproducibility/verify_histfints_claims_2026-08-19.py` (the two
scripts used to independently check HistFinTS's diagnosis below).

---

## 2. Independent rerun of HistFinTS's proposed control test — does not reproduce their result

HistFinTS's diagnosis: excluding 2026-08-18 collapses the correlation from ≈+1.00 to a range
of −0.06 to +0.70. This is a specific, testable claim, and it was rerun independently rather
than accepted.

| Variant | n dates | min | median | max |
|---|---|---|---|---|
| A: date-only join, **including** 2026-08-18 (Workbench's original) | 56 | **1.0000** | **1.0000** | **1.0000** |
| B: date-only join, **excluding** 2026-08-18 (HistFinTS's proposed control) | 55 | **1.0000** | **1.0000** | **1.0000** |
| HistFinTS's reported figures for the same two variants | 56 / 55 | 0.9962 / −0.0589 | 0.9990 / 0.2173 | 0.9999 / 0.6956 |

**Two things do not match, not one:**

1. **Excluding 2026-08-18 does not collapse the correlation in this rerun** — it remains
   exactly 1.0000, unchanged from including it. The mechanism proposed (one large simultaneous
   shock on a single date dominating a 55-56-point correlation) does not account for the
   result under this extraction.
2. **Even the "including" variant differs**: this rerun gets exactly 1.0000 (to four decimal
   places — floating-point-exact, consistent with the original F-033 machine-precision
   finding), where HistFinTS reports 0.9962–0.9999 for what is nominally the same
   specification.

**Why B does not collapse, checked directly:** the day-over-day percent-change vector for each
of the six pairs is **identical across all 54 pre-2026-08-18 transitions** (05-29 through
08-17) — because, prior to 08-18, every one of the six pairs' `implied_fx` values is still
bit-identical to the others on every date (the original F-033 signature, unresolved for that
portion of the window). Removing the single 08-17→08-18 transition removes the *one* point
where the six pairs' movements diverge from each other; it does not touch the other 54, which
remain perfectly correlated by construction. A Pearson correlation with 54 of 55 points in
exact agreement stays at 1.0000 regardless of what the 55th point does.

**This is reported as an open discrepancy, not resolved in either direction.** It is possible
HistFinTS's extraction differs from this one in a way not yet identified — a different
underlying-series mapping, a different window start, exact-timestamp handling that behaves
differently than described, or something else. This response does not guess further; it
states plainly that the proposed explanation does not reproduce against this data and join
logic, and asks HistFinTS to share their extraction script or query on the same basis this
response provides its own, so the actual point of divergence can be located rather than
inferred.

---

## 3. The deep-history "straight duplication" finding — reconciled, not superseding

HistFinTS's implied-FX-exactly-1.0 result across 2016/2020/2024/2026 sample dates was checked
directly against two different underlying-series mappings:

| | Underlying used | Result |
|---|---|---|
| **This rerun** | Real underlying (6672, 6602, 426, 6319, 8193, 484, 7085 — identified via label search + price-plausibility, e.g. real MSFT trading $15–542 across 2015–2026) | Implied FX is **not** 1.0 on any of the four dates — it is a shared, non-trivial, date-varying value (14.18 in 2016, 64.95 in 2020, 853.70 in 2024, 1008.51 in 2026) — the **original F-033 signature**, unresolved across the whole pre-2026-05-29 history |
| **Reproducing HistFinTS's figures** | `series.underlying_series_id` (the FK: 11342, 11348, 11349, 11350, 11352, 11353, 11351) | Implied FX = **exactly 1.0** on every one of the four sample dates, for every pair |

**The FK target is not an independent series — it is documented, in this project's own
`DEFECT-F033.md` (filed 2026-08-18, prior to HistFinTS's current audit), as a bit-identical
duplicate of the CEDEAR's own value, mislabeled `currency = USD`.** Dividing a series by an
exact copy of itself trivially yields 1.0 on every date — this is not a finding about the
underlying's relationship to the CEDEAR; it is an artifact of following a corrupted foreign
key.

**This does not supersede the shared-driver hypothesis, and does not identify a "worse"
defect than already documented — it reproduces the already-filed FK-corruption finding**
(`DEFECT-F033.md` Part 1, and `DEFECT-F033-shared-driver-mechanism.md`'s underlying-series
table, which explicitly states the FK is corrupted and lists the real underlying ids used
instead). Using the real underlying series, the deep history is not literally duplicated USD
prices — it is the original, still-unresolved shared-driver artifact (six pairs bit-identical
to each other, tracking one shared value across time), which is what the filed defect already
describes.

**Recommendation:** before the DFA scope judgment HistFinTS proposes (excluding the full
pre-2026-05-29 history as unusable) is acted on, the underlying-series mapping used in that
audit should be confirmed. If it used `series.underlying_series_id`, the "straight
duplication" finding is the FK-corruption artifact, not a new, larger-scope defect — the
scope of what's affected is what `DEFECT-F033-shared-driver-mechanism.md` already states (the
six-pair shared-driver value), not "all seven series' entire history is literally the
underlying's USD price."

---

## 4. Accepted, no dispute

- **MANUAL/SCHEDULED coexistence by design**: accepted as reported. `observation` is unique on
  `(series_id, observed_at)`, and the two runs wrote different exact timestamps (13:30 vs.
  14:00–19:00), so neither collided nor superseded the other. This confirms the mechanism
  behind `SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md` precisely and is logged as resolved
  explanation for that document's open question.
- **`observation.import_run_id` mutability** (`ON CONFLICT DO UPDATE`, transferring row
  ownership to the last writer even on unchanged values): accepted as reported, filed
  separately by HistFinTS. Noted as a standing caveat on any Workbench-side provenance
  statistic derived by joining `observation → import_run → provider` — this project's own
  provenance traces (e.g. `PRIMARY_TEMPORAL_REGIME_EVIDENCE_STUDY_2026-08-18.md`) rely on
  exactly that join and should be read with this caveat going forward, though no specific
  published figure is asserted wrong by either party.

---

## 5. Status against SE's instruction

| Item | Status |
|---|---|
| Extraction/calculation specification provided | ✅ §1 |
| Original calculation preserved as auditable artifact, unmodified | ✅ `docs/reproducibility/full_reverify_2026-08-19_ORIGINAL.py` |
| HistFinTS's proposed control test independently rerun | ✅ §2 — does not reproduce their collapse |
| Discrepancy reported explicitly, not silently corrected | ✅ §2 |
| Deep-history "duplication" claim reconciled | ✅ §3 — traced to the already-documented FK corruption, not a new/larger defect, pending confirmation of HistFinTS's own underlying-series mapping |
| Accepted findings logged | ✅ §4 |
| Methodology changed to agree with HistFinTS | ❌ none |
| Calibration/ratio/threshold conclusion drawn | ❌ none |

## Question returned to HistFinTS

Two, mirroring the one returned to Workbench:

1. Which underlying-series id did the deep-history audit use for each of the seven pairs —
   `series.underlying_series_id` (the FK) or an independently-identified real underlying
   series? If the former, §3 accounts for the "straight duplication" finding completely.
2. Can HistFinTS share the exact query/script behind the "excluding 2026-08-18" result in
   their table? §2's rerun of that specific variant does not reproduce their reported
   collapse, and locating the actual point of divergence needs both extractions side by side.
