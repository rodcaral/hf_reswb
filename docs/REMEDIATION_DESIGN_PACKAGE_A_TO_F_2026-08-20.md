# Read-Only Remediation Design Package, Classes A–F

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE, for domain/product routing
**Basis:** `REMEDIATION_BOUNDARY_ANALYSIS_A_TO_F_2026-08-20.md` (this project's independently
re-verified read of the HistFinTS-authored governing framework), frozen baseline
`histfints-v3/docs/remediation_baseline_20260820T055140Z/`.

**This is a design package, not an implementation. No repair SQL is executed or staged in
this document or in producing it. No observation deleted, no FK repointed, no provenance
field altered, no calibration/policy state changed, no frozen baseline touched.**

**Standing invariant carried through every class below**: `origin_import_run_id` must be
preserved, unchanged, for every row that survives any future repair, and must never be
inferred, backfilled, or reconstructed from `import_run_id` — `import_run_id` is mutable
(Class H's own finding) and using it to infer origin would launder a last-writer value into
looking like authoritative history.

---

## Class A — 111 fabricated MERVAL observations

| Field | Content |
|---|---|
| **Candidate population** | 111 rows, `import_run_id IN (58332, 58333, 58334, 58335)`, series 11364/11366 |
| **Evidence supporting inclusion** | Two independent signals agree exactly: the run-id boundary (111 rows) and `instr(observed_at, '.') > 0` — a fractional-second signature in `observed_at`, orthogonal to `import_run_id` entirely. Independently re-verified this project's own read-only query: 111 rows, split 26/33/24/28 across the four runs, exact match. Endpoint-unreachability evidence (`ConnectionResetError` on all paths) already documented separately. |
| **Cleanly separable?** | **Yes.** Two independent signals define the identical set. |
| **Proposed disposition** | Candidate for removal, pending SE/product authorization — not proposed here as authorized. Series 11364/11366 retain other legitimate rows (6 confirmed), so removal does not empty either series. |
| **Required evidence for repair** | Full row export before any change (already captured: `class_a_rows.csv`); the four `import_run` rows preserved as the fabrication record, not deleted alongside the observations. |
| **Repair type** | Data deletion (observation rows) + separate provider correction (the adapter producing these must be fixed independently, or it will write more) |
| **Independent post-repair verification** | Fractional-second count over the *entire* `observation` table returns 0 — a property of `observed_at` content, not of any provenance field the repair touches. Secondary: total observation count decreases by exactly 111, net of ordinary BYMA-cohort accrual. |
| **Permanently unavailable evidence** | None specific to this class beyond the standing origin-provenance gap (below) — the fabrication is fully characterized by the two agreeing signals; no further evidence is needed to *identify* it. |
| **Rows to remain unresolved** | None — this is the one class in the package with a fully closed, exact boundary. |

---

## Class B — 18,322 `BACKFILL_*`-owned rows, seven CEDEAR series

| Field | Content |
|---|---|
| **Candidate population** | 18,322 rows across series 11323–11329, currently owned by import runs 58325–58331 |
| **Evidence supporting inclusion** | Date-range boundary, not run-id boundary: on every one of the seven series, `BACKFILL_*` rows occupy 2015-01-02→2026-05-28 (or 2021-12-09→2026-05-28 for NU) with **zero overlapping dates** against the series' own legitimate rows (2026-05-29 onward). Independently re-verified for series 11323 this project's own query. `byma` absent from `PROVIDER_REGISTRY`, `BACKFILL_` absent from shipped source — evidence these rows were written outside the shipped pipeline (as documented by HistFinTS; not independently re-derived by Workbench). |
| **Cleanly separable?** | **Yes, by date — the cleanest row-level boundary in the package.** `(series_id, observed_at < 2026-05-29)` does not depend on the mutable `import_run_id` field at all. |
| **Proposed disposition** | Candidate for quarantine or removal, pending SE/product authorization. Not proposed here as authorized. |
| **Required evidence for repair** | Per-series row export of all 18,322 rows before deletion; the seven `import_run` rows (58325–58331), with their zero-elapsed timestamps, preserved as the record of how these rows were produced. |
| **Repair type** | Data deletion/quarantine + provider re-derivation for verification (re-fetch from each series' own legitimate assignment) + a separate pipeline correction (so the same mechanism cannot write again) |
| **Independent post-repair verification** | Re-fetch the affected date range for each of the seven series from its own legitimate assignment and compare values directly. Correctness of the numbers is checked independently of what any provenance field claims. Secondary: `zero_duration_import` count drops from 11 to 4 (the remaining 4 being Class A). |
| **Permanently unavailable evidence** | **Origin provenance for all 18,322 rows is permanently unrecoverable** — they predate the origin column (Class H), and the BYMA evidence cohort's origin-recoverability property (§1 of the boundary analysis) does not extend to this population. Value-level re-derivation is available only where the provider still actively serves the historical range in question; this is not guaranteed for the full 2015–2026 span. |
| **Rows to remain unresolved** | Any date within the affected range where the provider no longer serves that historical data (cannot be re-fetched for value verification) should remain flagged as unresolved rather than assumed correct or assumed wrong. This project has not determined which specific dates, if any, fall into that category — stated as an open question, not answered here. |

---

## Class C — 24,187 cross-series rows, two materially different populations

Per the framing directive: **these are two separate remediation problems, not one class with
a partial boundary.** No boundary-based repair is proposed for the 8 collision targets.

### C.1 — 8 targets with a legitimate/crossed-row date collision

| Field | Content |
|---|---|
| **Candidate population** | Targets 11342, 11348, 11349, 11350, 11352, 11353 (six seven-pair FK targets), 11351 (NU's target), 11343 (AAPL's target, five-control episode). Crossed-row counts range 1,120–2,867 per target (seven-pair) and 1,561 (AAPL). |
| **Evidence supporting inclusion** | Each target's crossed-row date range (2015-01-02/2020-01-02/2021-12-09→2026-05-28, depending on target) overlaps its own legitimate-row range (2026-05-28→2026-08-19) on exactly one date: **2026-05-28.** |
| **Cleanly separable?** | **No.** This is the point of the collision: a date-range boundary (the mechanism that worked cleanly for Class B) would remove a legitimate row alongside the crossed ones on 2026-05-28. An `import_run_id`-based boundary is independently unreliable, since ownership on this date may have migrated (Class H). **No boundary rule of either kind is proposed here as sufficient.** |
| **Proposed disposition** | **Row-by-row resolution of 2026-05-28 only, against independently re-fetched values, before any bulk action on the surrounding crossed-row population.** This is not a boundary rule; it is a case-by-case evidentiary check on a single date, repeated per target. The pre-2026-05-28 crossed rows, once 2026-05-28 is resolved, may then be addressed by the same re-derivation approach as Class B — but that step is not proposed here as scoped or authorized. |
| **Required evidence for repair** | Full export of all crossed rows for these 8 targets before any change; the relevant `import_run` rows and their `provider_assignment` linkage (evidence of the cross-series write itself — destroyed by re-attribution if not captured first); independently re-fetched values for 2026-05-28 specifically, from each target's own legitimate assignment. |
| **Repair type** | Cannot be classified as a single repair type — the collision date requires row-level reconstruction/comparison (not mechanical deletion); the pre-collision range, once separated, would be data deletion + provider re-derivation, structurally similar to Class B but not proposed as scoped here. |
| **Independent post-repair verification** | Re-derive each affected series from its own assignment and compare values; then `find_cross_series_import_runs()` returning 0 — stated explicitly as **necessary, not sufficient**, since that check reads the same mutable provenance the repair would rewrite. |
| **Permanently unavailable evidence** | Origin provenance, as with Class B, is permanently unrecoverable for this entire population (outside the BYMA cohort). Deep-history rows (pre-2020 for some targets) may exceed provider re-fetch windows, making value-level re-derivation unavailable for those specific dates as well — not yet determined which, if any. |
| **Rows to remain unresolved** | **2026-05-28 specifically, for any of the 8 targets, if independent re-fetch does not resolve unambiguously** (e.g. the provider's own historical value for that date is itself ambiguous or unavailable) — must remain flagged rather than assigned to either the "legitimate" or "crossed" bucket by assumption. |

### C.2 — 4 targets with no legitimate rows at all

| Field | Content |
|---|---|
| **Candidate population** | 11344 (GLD), 11345 (BABA), 11346 (BIDU), 11347 (UBER) — crossed rows are the **entire** content of each series (344–1,513 rows each). |
| **Evidence supporting inclusion** | Zero own/legitimate rows on any of the four, confirmed in the governing analysis. Not independently re-verified by Workbench this pass (stated in the prior boundary-analysis document). |
| **Cleanly separable?** | Trivially yes at the row level (100% of each series' content is "crossed") — but separability is not the obstacle here. |
| **Proposed disposition** | **Not proposable as a mechanical repair. This is a content-disposition decision**, not evidence-gated in the way A/B/C.1 are: does this data belong to another series entirely (in which case re-attribution, not deletion, may be correct), or is this the only surviving copy of otherwise-lost data (in which case deletion would be a permanent loss, not a cleanup)? Routing to SE/domain for a decision, not proposing an answer. |
| **Required evidence for repair** | Whatever would establish which of the two dispositions above is correct — e.g., whether a legitimately-configured assignment for these four series exists or ever existed elsewhere, and whether the crossed data is recoverable/re-derivable from an independent source matching what these four series are meant to represent. Not currently established. |
| **Repair type** | Indeterminate pending the disposition decision — could be catalog correction (re-attribution) or data deletion, and these are not equivalent choices. |
| **Independent post-repair verification** | Cannot be specified until the disposition is chosen — a re-attribution's verification criterion (does the data now correctly belong to its true series) differs entirely from a deletion's (does removing it leave nothing behind that was actually needed). |
| **Permanently unavailable evidence** | If these four series' crossed data is deleted without first confirming it exists correctly elsewhere, whatever these series were meant to hold could become **permanently unrecoverable** — this is the central risk the disposition decision must weigh, not a technical repair detail. |
| **Rows to remain unresolved** | **All of them, until the disposition decision is made.** No proposal here to act on any of these 4 targets' rows in either direction. |

---

## Class D — 7 repointed `underlying_series_id` values

| Field | Content |
|---|---|
| **Candidate population** | `series.underlying_series_id` on 11323–11329, currently `{11323→11342, 11324→11348, 11325→11349, 11326→11350, 11327→11351, 11328→11352, 11329→11353}` |
| **Evidence supporting inclusion** | Creation-timestamp violation: each current target was created after the series referencing it (~3 hours later) — a structural check, not a label heuristic. Independently re-verified this project's own query: the current pointer map matches exactly. |
| **Cleanly separable?** | **Yes, exactly.** No observation row is touched by this class at all — it is a single metadata field per series. |
| **Proposed disposition** | Candidate for repoint to `{11323→6672, 11324→6602, 11325→426, 11326→6319, 11327→7085, 11328→8193, 11329→484}`, pending SE/product authorization — not proposed here as authorized. |
| **Required evidence for repair** | Current pointer map (captured, `series_catalog.csv`); creation timestamps proving the postdating relationship; the pre-repair F-033 statistic, so any post-repair value is a comparison, not a fresh, unanchored claim. |
| **Repair type** | Catalog correction (metadata only) — no data deletion, no reconstruction, no observation touched. |
| **Independent post-repair verification** | Recompute this project's own F-033 implied-FX statistic against the new pointers — it must reproduce the **already pre-registered** value: 15/21 pairs at exactly `1.000000000000` (matching `RECONCILIATION-F033-2026-08-19.md` exactly, established before any repair). A value a repair cannot accidentally satisfy. Secondary: the structural sweep (no series' `underlying_series_id` points at a target created after itself) is **not** a label heuristic and a clean result here is meaningful on its own. |
| **Permanently unavailable evidence** | None — this class touches no observation data, so nothing about it depends on unrecoverable provenance. |
| **Rows to remain unresolved** | None applicable — no rows, only 7 metadata values, all fully specified. |

**Ordering constraint, restated from the governing plan, not altered:** D must precede E
(`ON DELETE RESTRICT` on the FK).

---

## Class E — shadow-series duplicate groups

| Field | Content |
|---|---|
| **Candidate population** | 14 groups (label-normalization signal) or 33 groups (identifier-based signal — `(provider_id, provider_series_identifier)` mapped to more than one series) |
| **Evidence supporting inclusion** | Two independent signals, both stated as floors (under-report by construction), disagreeing by 2.4×. |
| **Cleanly separable?** | **No — not determinable as a closed set at all**, by the governing plan's own framing, not merely "harder than A/B/D." The 33-vs-14 divergence is direct evidence that scoping by either signal alone would miss most of the true population. |
| **Proposed disposition** | Not proposable as a scoped repair until the discrepancy between the two signals is itself investigated — routing to SE/domain rather than proposing action on either candidate set. |
| **Required evidence for repair** | Full catalog snapshot (captured); both detection signals run and reconciled; for each candidate group, which member is authoritative and what references it — not currently established. |
| **Repair type** | Catalog correction (merge/remove duplicates) — but see disposition above; not scoped as proposable yet. |
| **Independent post-repair verification** | Clean under **both** signals simultaneously — and even then, the governing plan states explicitly that the resulting claim is only "no duplicate detectable by two independent methods," not completeness. |
| **Permanently unavailable evidence** | **Completeness of the duplicate population cannot be established, structurally, not merely currently** — both signals are floors by construction, so no amount of additional checking with the same two methods closes this gap. |
| **Rows to remain unresolved** | Every candidate group not confirmed by *both* signals simultaneously should remain unmerged rather than resolved by preferring one signal over the other. |

**Ordering constraint, restated:** E requires D complete (FK dependency) and C's rows resolved
(shadow series hold the Class C crossed rows) — E is last in the sequence for structural
reasons, not priority.

---

## Class F — 12 same-date multi-run findings (12 HIGH; 188 INFO separately)

| Field | Content |
|---|---|
| **Candidate population** | 12 HIGH findings (`(series, date)` pairs with runs disagreeing ≥1.5×) + 188 INFO (ordinary revalidation, not itself a candidate for repair) |
| **Evidence supporting inclusion** | Multiple import runs writing to the same `(series_id, date)` — detectable directly from `observation`/`import_run`. |
| **Cleanly separable?** | **Not meaningfully assessable yet.** 8 of the 12 HIGH findings are stated to be downstream consequences of Classes A/B/C (6 from the 2026-08-18 MANUAL/SCHEDULED event on the F-033 seven, 2 from the Class A MERVAL rows on 11364/11366) — they are expected to disappear once A/B/C are addressed, without being separately repaired. |
| **Proposed disposition** | **Re-measure after A/B/C are addressed; do not decide F's disposition against today's count**, per the governing plan's own explicit caution — deciding now would be deciding against a number that is mostly not independently F. |
| **Required evidence for repair** | A post-A/B/C re-measurement of the same detector, to isolate the genuinely independent remainder (expected ≤4 of the current 12) before any repair route is chosen. |
| **Repair type** | Two candidate routes named by the governing plan, neither scoped here: schema-level date-dedup, or an enforced most-recent-run-per-date consumer convention. Choosing between them is out of scope for this package. |
| **Independent post-repair verification** | Schema route: no series carries more than one observation per calendar date — countable and positive. Convention route: a shared query helper plus a test proving a naive consumer cannot silently mix regimes — code-level verification, not data-level. |
| **Permanently unavailable evidence** | Whatever is permanently unavailable for the underlying A/B/C rows applies transitively to F's consequential findings; the genuinely independent remainder (post re-measurement) has not yet been evidenced at all. |
| **Rows to remain unresolved** | The entire class, until re-measured after A/B/C — no finding in the current 12 should be treated as resolved, disproven, or scoped for repair based on today's count. |

---

## Cross-class notes, not new content

- **Standing origin-provenance limit** (from the boundary analysis, restated): only the 21-row
  BYMA evidence cohort has origin recoverable in principle, independent of `import_run_id`.
  Every other class's affected rows — all of B, all of C, and by extension F's consequential
  findings — carry a **permanent, structural** origin-provenance gap, not a temporarily
  missing one.
- **No class's repair may be verified by the detector that scoped it** (E and D's label half
  explicitly named as floors in the governing plan; this package's verification criteria for
  every class are chosen to be orthogonal to the scoping detector, per class above).
- **Governing principle restated once more because it bears on every disposition above**: "a
  detector going quiet is necessary but never sufficient evidence that a repair worked."

## What this package does not do

- Does not authorize, schedule, or recommend that any repair proceed.
- Does not execute or stage any repair SQL.
- Does not propose a boundary-based repair for Class C's 8 collision targets — explicitly
  declined per instruction, with the row-by-row alternative stated instead.
- Does not choose a disposition for Class C's 4 no-legitimate-row targets or for Class E —
  both are routed to SE/domain as decisions, not answered here.
- Does not alter the frozen baseline, any observation, any FK, any provenance field
  (`import_run_id` or `origin_import_run_id`), any schema, or any calibration/policy state.
