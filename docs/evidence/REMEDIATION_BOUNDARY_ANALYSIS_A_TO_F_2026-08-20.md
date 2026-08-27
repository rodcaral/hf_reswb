# Read-Only Remediation-Boundary Analysis, Classes A–F

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Governing framework:** `docs/REMEDIATION_BOUNDARY_PLAN_A_TO_F_2026-08-20.md` and
`docs/REMEDIATION_SEQUENCING_AND_VERIFICATION_2026-08-20.md` (SDT HistFinTS,
`histfints-v3/docs/`), frozen baseline
`histfints-v3/docs/remediation_baseline_20260820T055140Z/`. **Class definitions taken as given,
not reconstructed.** Database checksum in `manifest.json`
(`7aa6b2100493897228c8fafa992ef65a67594453d4106f1784d8d927860c5e59`) verified as the
authoritative source before use.
**Status: no repair executed. No observation deleted, no pointer altered, no `import_run_id` or
`origin_import_run_id` touched, no schema change, no calibration/policy change. Every query in
this analysis was read-only (`SELECT`) against the live database.**

---

## 0. What this document is

A Workbench-side read of the HistFinTS-authored A–F plan, with the load-bearing claims
independently re-verified against the live database (not re-derived from a different
methodology — the class definitions are HistFinTS's, taken as governing). Where a number is
stated below without a "re-verified" note, it is quoted from the HistFinTS documents and was
not independently re-checked in this pass; where "re-verified" appears, Workbench ran its own
read-only query against the live database and confirmed the figure independently.

---

## 1. Affected populations, per class

| Class | Population | Rows | Re-verified |
|---|---|---|---|
| **A** | 111 fabricated MERVAL observations, four import runs (58332–58335) | 111 | ✅ exact match, including the per-run split (26+33+24+28=111) |
| **B** | `BACKFILL_*`-owned rows, seven CEDEAR series (11323–11329) | 18,322 | ✅ spot-checked series 11323: 2,867 BACKFILL rows, 2015-01-02→2026-05-28 |
| **C** | Cross-series rows, two episodes: seven-pair (18,322) + five-control (5,865) | 24,187 | Not independently re-verified this pass; internally consistent with B's count for the seven-pair episode |
| **D** | Repointed `underlying_series_id`, seven CEDEARs | 7 | ✅ exact match: current map `{11323→11342, 11324→11348, 11325→11349, 11326→11350, 11327→11351, 11328→11352, 11329→11353}` reproduced independently |
| **E** | Shadow-series duplicate groups | 14 (label signal) / 33 (identifier signal) | Not independently re-verified this pass |
| **F** | Same-date multi-run findings | 12 HIGH / 188 INFO | Not independently re-verified this pass |
| **H** (not a repair class; the origin-column migration) | `origin_import_run_id` presence | 11,401 post-epoch rows, 0 pre-epoch | ✅ already independently verified in this project's own prior work (`CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_2026-08-20.md`) |

---

## 2. Separability of legitimate vs. defective observations, per class

- **A: fully separable, orthogonal signature.** `instr(observed_at, '.') > 0` (fractional
  seconds) identifies exactly the 111 rows independent of `import_run_id`. Re-verified: this
  signature and the run-id boundary agree exactly, with zero rows outside the intersection.
- **B: fully separable by date, not by run id.** Zero overlapping dates between `BACKFILL_*`
  rows (2015-01-02→2026-05-28) and legitimate rows (2026-05-29→2026-08-19) on the series
  spot-checked. A `(series_id, observed_at < 2026-05-29)` boundary does not depend on the
  mutable `import_run_id` field.
- **C: separable for 4 of 12 targets, NOT separable for 8 of 12** (see §3).
- **D: fully separable, metadata-only.** No observation row is touched by this class at all —
  it is a single FK value per series, independently reproducible.
- **E: not separable as a closed set.** Two detection signals (label normalization: 14 groups;
  identifier-based: 33 groups) disagree by 2.4×, meaning the true population is unknown, not
  merely uncounted — both signals are stated floors.
- **F: not separable as its own class at all before A/B/C are addressed** — 8 of its 12 HIGH
  findings are stated to be downstream consequences of A/B/C, not independent instances.

---

## 3. Class C's 8-of-12 boundary overlap — the specific targets, and why they don't separate

Per the governing plan (§4 of the boundary plan), Class C's 12 targets split into two groups:

**8 targets with a one-date collision** (2026-05-28 carries both crossed and legitimate rows):

| Target series | Crossed rows | Crossed range | Own rows | Own range |
|---|---|---|---|---|
| 11342, 11348, 11349, 11350, 11352, 11353 (six of the seven-pair FK targets) | 2,867 each | 2015-01-02→2026-05-28 | 407 | 2026-05-28→2026-08-19 |
| 11351 (NU's FK target) | 1,120 | 2021-12-09→2026-05-28 | 407 | 2026-05-28→2026-08-19 |
| 11343 (AAPL, five-control episode) | 1,561 | 2020-01-02→2026-05-28 | 408 | 2026-05-28→2026-08-19 |

**Why not separable:** unlike Class B, the crossed range and the series' own legitimate range
**share the single date 2026-05-28**. A date-boundary rule (the mechanism that cleanly
separated Class B) would take a legitimate row on that date with it. An `import_run_id`-based
boundary is independently unreliable here because ownership is mutable (Class H's own
finding) — the same defect this project spent today's earlier work characterizing for
`origin_import_run_id`. **That single date requires row-by-row resolution against re-fetched
values before any bulk action; no boundary rule alone resolves it.**

**4 targets with no legitimate rows at all, zero overlap, still not a clean repair boundary**:
11344 (GLD), 11345 (BABA), 11346 (BIDU), 11347 (UBER) — the crossed rows are the *entire*
content of these series. Zero date overlap here isn't separability in the useful sense: acting
on these targets is a content-disposition decision (does the data belong elsewhere, or is this
the only copy), not a mechanical boundary application. Their inclusion in the "12" and
exclusion from the "8" is the plan's own distinction, reproduced here, not reinterpreted.

**Restated plainly:** "8 of 12 overlap" does not mean 8 targets are simply harder — it means 8
targets require external re-fetched evidence to resolve one shared date correctly, while the
other 4 present a different, non-mechanical problem (whether emptying a series that holds only
crossed data is correct at all).

---

## 4. Dependencies between classes

Per the governing plan's sequencing (§8/§2 of the two source documents), reproduced, not
altered:

```
A — independent, no dependency
B — independent, no dependency
C — must resolve before E (shadow series hold the 24,187 crossed rows)
D — must resolve before E (ON DELETE RESTRICT on underlying_series_id)
E — depends on both C and D; last in sequence
F — cannot be meaningfully measured until A/B/C are addressed (8 of 12 HIGH findings are
    stated consequences of A/B/C, not independent F instances)
H — precedes C specifically (repairing provenance with a still-mutable key at the time
    would leave nothing reliable to verify against); A and B do not strictly require H
    first since they are provable by exact count deltas against the frozen baseline
```

A and B are the only two classes with no dependency on any other class or on H.

---

## 5. Independent evidence needed to verify a future repair, without relying on the detector that found it

Per class, restated from the governing plan and cross-referenced against what this project's
own work already provides:

- **A:** the fractional-second count over the whole table, post-repair, must be exactly 0 — a
  property of `observed_at` string content, independent of `import_run_id` or any detector
  logic. Secondary: total observation count decreases by exactly 111 net of the BYMA
  evidence-cohort's normal ~21-row-per-session growth.
- **B:** re-fetch the affected date range for series 11323–11329 from each series' own
  legitimate assignment and compare values directly — correctness of the numbers, checked
  independently of what any provenance field claims.
- **C:** re-derive each affected series from its *own* assignment and compare; `find_cross_
  series_import_runs()` returning 0 is stated as necessary but **not sufficient**, since that
  check reads the same mutable provenance the repair would rewrite.
- **D:** recompute this project's own F-033 implied-FX statistic against the corrected
  pointers — it must reproduce the **already pre-registered** value (15/21 pairs at exactly
  `1.000000000000`, matching this project's own `RECONCILIATION-F033-2026-08-19.md` finding
  exactly) — a value no repair could satisfy by accident. Secondary: a structural sweep (no
  series' `underlying_series_id` points at a target created after itself) is stated as *not*
  heuristic, unlike the label-based checks elsewhere in this plan.
- **E:** must be clean under *both* the label-normalization and the identifier-based signal
  simultaneously — even then, the governing plan is explicit that completeness cannot be
  established, only "no duplicate detectable by two independent methods."
- **F:** schema route — no series carries more than one observation per calendar date,
  countable directly. Convention route — a shared most-recent-run-per-date helper plus a test
  proving a naive consumer cannot silently mix regimes (code-level verification, not
  data-level).

**Governing principle restated, because it applies to every class above:** a detector going
quiet is necessary but never sufficient evidence a repair worked — `import_run_id`
mutability, and the fact that E/D's label signal are floors by construction, both mean a
repair could silence its own detector without fixing its cause.

---

## 6. Read-only pre/post invariants for any future remediation

**Verification criteria only. Nothing below authorizes, schedules, or recommends
remediation.**

1. **`origin_import_run_id` preservation.** Every observation's `origin_import_run_id` value
   immediately before any future repair must equal its value immediately after, for every row
   not itself deleted by that repair. A repair that changes a surviving row's
   `origin_import_run_id` has violated the one immutability property Class H exists to
   provide, regardless of what else it accomplishes.
2. **`import_run_id` is not a verification input.** Because it is mutable (Class H's own
   finding, independently reproduced by this project's `PROVENANCE_INTEGRITY_import_run_id_
   mutability.md` work), no pre/post invariant may rely on `import_run_id` remaining stable
   or on its value proving anything about origin. Only `origin_import_run_id` (post-epoch) or
   independently re-fetched values (any era) may serve as verification evidence.
3. **BYMA evidence cohort isolation.** All 21 `[F-033 evidence]`-labeled series (re-verified
   present, 21 series, this pass) must show zero rows touched by any A–F repair action. Their
   accrual rate (~21 rows/session) must be netted out of every count-delta claim, or a
   legitimate accrual will be misread as a repair side effect.
4. **Count-delta arithmetic must use the frozen P1 baseline as denominator**, not "current
   minus assumption" — the observation total legitimately grows via ordinary operation
   (confirmed: 27,949,974 at baseline capture → 27,961,375 current, +11,401, all accounted for
   by the general scheduled import per the governing plan's §0).
5. **No class's repair may be verified using the same detector/heuristic that identified it**
   (the circularity the governing plan names explicitly for E, and implicitly for D's label
   half) — an orthogonal signal, per class as enumerated in §5 above, is required.
6. **Class D's verification value is pre-registered and must not be adjusted post hoc.** The
   expected post-repair F-033 statistic (15/21 pairs at exactly `1.000000000000`) is already
   known from this project's own independent work, predating any repair — a repair producing a
   different value is falsified, not "explained."
7. **Sequencing dependencies (§4 above) are pre/post invariants in themselves** — e.g., a
   verification pass finding E "clean" while D or C remain unresolved indicates a broken
   verification, not a successful repair, since E structurally depends on both.

---

## 7. Provenance-epoch discrepancy — unresolved, untouched in this task

Restated per instruction, not acted on: `provenance_epoch.applied_at =
'2026-08-20 06:23:35'` (the table's single authoritative row) does not match the empirically
observed epoch (`2026-08-20T12:08:12.982123+00:00`) currently used in this project's
`provenance_guard.py` docstrings and tests. **No code, test, documentation, or baseline was
modified in this task as a result of this discrepancy.** It remains an open external
dependency, separate from the A–F analysis above, requiring reconciliation before (not as
part of) any future safeguard update.

---

## 8. Standing constraints, restated

- BYMA evidence collection: unchanged, continuing as-is, not touched by this analysis.
- Uncontrolled-write stop condition: not evaluated or altered in this task.
- No safeguard (`independence_detector.py`, `provenance_guard.py`) integrated into
  `panel_eligibility_service.py` or calibration code as a result of this analysis.
- No inference drawn that any of the above authorizes or recommends remediation. This is a
  boundary map, not a repair proposal.
