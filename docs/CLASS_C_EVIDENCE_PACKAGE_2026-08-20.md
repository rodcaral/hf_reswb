# Class C Evidence Package for DFA Adjudication

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE, for DFA
**Basis:** `REMEDIATION_BOUNDARY_ANALYSIS_A_TO_F_2026-08-20.md`,
`REMEDIATION_DESIGN_PACKAGE_A_TO_F_2026-08-20.md` (this project), the HistFinTS-authored
governing framework in `histfints-v3/docs/`. Every value below was retrieved by fresh,
read-only (`SELECT`-only) query against the live database and cross-checked against the
existing baseline/design package; nothing here contradicts them.

**No HistFinTS modification, no data repair, no repair SQL staged, no provenance field
altered, no change to the A–F design. `import_run_id` is used below only as a descriptive
label on retrieved evidence — never as an authoritative boundary for any conclusion, per
standing instruction.**

---

## Part 1 — The four no-legitimate-observation targets

| Target series | Label | Total observations | Import run(s) owning them | Provider assignment(s) actually referencing this series id |
|---|---|---|---|---|
| **11344** | SPDR Gold Shares - ETF (NYSE) | **344** | run 11376 only | **none** |
| **11345** | Alibaba Group Holding Limited - ADS (NYSE) | **1,513** | run 25556 only | **none** |
| **11346** | Baidu Inc. - ADS (NASDAQ) | **1,512** | run 25557 only | **none** |
| **11347** | Uber Technologies - Stock (NYSE) | **935** | run 25559 only | **none** |

**Evidence supporting "no legitimate observations remain," per target:**

- **11344**: all 344 rows come from run 11376, whose `provider_assignment` (id 11312,
  identifier `GLD.BA`) has `series_id = 11311` — i.e. **the original GLD CEDEAR series, not
  11344**. Every row is attributable to a write intended for a different series.
- **11345**: all 1,513 rows from run 25556, assignment id 11318 (`BABA.BA`), `series_id =
  11316` (BABA CEDEAR) — same pattern.
- **11346**: all 1,512 rows from run 25557, assignment id 11319 (`BIDU.BA`), `series_id =
  11317` (BIDU CEDEAR) — same pattern.
- **11347**: all 935 rows from run 25559, assignment id 11321 (`UBER.BA`), `series_id =
  11319` (UBER CEDEAR) — same pattern.

**Stronger than absence of legitimate rows**: queried `provider_assignment` directly for any
row where `series_id` equals 11344, 11345, 11346, or 11347 — **zero results for all four**.
These four target series have **no provider assignment of their own at all**, under any
provider. This is not merely "no legitimate row happens to exist yet" — there is currently no
configured path by which one could be written. This sharpens, and is consistent with, the
prior boundary analysis's framing of these four as a content-disposition question rather than
a data-collection gap.

---

## Part 2 — The eight collision targets: identity and the 2026-05-28 evidence

| Target series | Label | Total obs | Crossed-row source (run, assignment, owning series) | Own/legitimate source (run, assignment) |
|---|---|---|---|---|
| **11342** | Micron Technology, Inc. - Stock (NASDAQ) | 3,274 | run 58228, assignment 11326 (`MU.BA`), owns series 11323 | runs 69685+81093, assignment 11365 (`MU`) |
| **11348** | Microsoft Corporation - Stock (NASDAQ) | 3,274 | run 58229, assignment 11327 (`MSFT.BA`), owns series 11324 | runs 69687+81095, assignment 11376 (`MSFT`) |
| **11349** | Advanced Micro Devices - Stock (NASDAQ) | 3,274 | run 58230, assignment 11328 (`AMD.BA`), owns series 11325 | runs 69688+81096, assignment 11378 (`AMD`) |
| **11350** | MercadoLibre Inc. - Stock (NASDAQ) | 3,274 | run 58231, assignment 11329 (`MELI.BA`), owns series 11326 | runs 69689+81097, assignment 11380 (`MELI`) |
| **11352** | Invesco QQQ Trust - ETF (NASDAQ) | 3,274 | run 58233, assignment 11331 (`QQQ.BA`), owns series 11328 | runs 69691+81099, assignment 11384 (`QQQ`) |
| **11353** | Amazon.com Inc. - Stock (NASDAQ) | 3,274 | run 58234, assignment 11332 (`AMZN.BA`), owns series 11329 | runs 69692+81100, assignment 11386 (`AMZN`) |
| **11351** | Nu Holdings Ltd. - Stock (NYSE) | 1,527 | run 58232, assignment 11330 (`NU.BA`), owns series 11327 | runs 69690+81098, assignment 11382 (`NU`) |
| **11343** | Apple Inc. - Stock (NASDAQ) | 1,969 | run 25560, assignment 11322 (`AAPL.BA`), owns series 11305 | runs 69686+81094, assignment 11367 (`AAPL`) |

**Evidence of the shared 2026-05-28 collision, per target — every crossed source's rows run
through 2026-05-28 (inclusive), and every own/legitimate source's rows begin on 2026-05-28
(inclusive), confirmed directly**:

| Target | Crossed range | Own/legitimate range |
|---|---|---|
| 11342 | 2015-01-02 → **2026-05-28** | **2026-05-28** → 2026-08-19 |
| 11348 | 2015-01-02 → **2026-05-28** | **2026-05-28** → 2026-08-19 |
| 11349 | 2015-01-02 → **2026-05-28** | **2026-05-28** → 2026-08-19 |
| 11350 | 2015-01-02 → **2026-05-28** | **2026-05-28** → 2026-08-19 |
| 11352 | 2015-01-02 → **2026-05-28** | **2026-05-28** → 2026-08-19 |
| 11353 | 2015-01-02 → **2026-05-28** | **2026-05-28** → 2026-08-19 |
| 11351 | 2021-12-09 → **2026-05-28** | **2026-05-28** → 2026-08-19 |
| 11343 | 2020-01-02 → **2026-05-28** | **2026-05-28** → 2026-08-19 |

`2026-05-28` is the exact and only date shared by both sides on all eight targets.

---

## Part 3 — The exact colliding rows on 2026-05-28, per target

All values below are as stored, retrieved read-only. **`origin_import_run_id` is `NULL` on
every row listed** — every one of these observations, both crossed and legitimate, predates
the origin-column epoch. There is no immutable-origin marker to lean on for any row in this
part; that is stated as a fact for DFA's adjudication, not proposed to be worked around.

| Target | Tag | obs_id | observed_at | value | import_run_id (descriptive only) | trigger |
|---|---|---|---|---|---|---|
| **11342** | CROSSED | 27895588 | 13:30:00 | 932.190002 | 58228 | MANUAL |
| 11342 | LEGITIMATE | 27951219 | 14:30:00 | 942.145020 | 69685 | SCHEDULED |
| 11342 | LEGITIMATE | 27951220 | 15:30:00 | 940.905396 | 69685 | SCHEDULED |
| 11342 | LEGITIMATE | 27951221 | 16:30:00 | 936.000000 | 69685 | SCHEDULED |
| 11342 | LEGITIMATE | 27951222 | 17:30:00 | 937.020020 | 69685 | SCHEDULED |
| 11342 | LEGITIMATE | 27951223 | 18:30:00 | 923.424988 | 69685 | SCHEDULED |
| 11342 | LEGITIMATE | 27951224 | 19:30:00 | 923.520020 | 69685 | SCHEDULED |
| **11348** | CROSSED | 27898511 | 13:30:00 | 425.256287 | 58229 | MANUAL |
| 11348 | LEGITIMATE | 27952018 | 14:30:00 | 424.750000 | 69687 | SCHEDULED |
| 11348 | LEGITIMATE | 27952019 | 15:30:00 | 425.845001 | 69687 | SCHEDULED |
| 11348 | LEGITIMATE | 27952020 | 16:30:00 | 425.809998 | 69687 | SCHEDULED |
| 11348 | LEGITIMATE | 27952021 | 17:30:00 | 426.500000 | 69687 | SCHEDULED |
| 11348 | LEGITIMATE | 27952022 | 18:30:00 | 426.029999 | 69687 | SCHEDULED |
| 11348 | LEGITIMATE | 27952023 | 19:30:00 | 427.019989 | 69687 | SCHEDULED |
| **11349** | CROSSED | 27901434 | 13:30:00 | 505.260010 | 58230 | MANUAL |
| 11349 | LEGITIMATE | 27952417 | 14:30:00 | 523.609985 | 69688 | SCHEDULED |
| 11349 | LEGITIMATE | 27952418 | 15:30:00 | 518.945984 | 69688 | SCHEDULED |
| 11349 | LEGITIMATE | 27952419 | 16:30:00 | 518.729980 | 69688 | SCHEDULED |
| 11349 | LEGITIMATE | 27952420 | 17:30:00 | 519.489990 | 69688 | SCHEDULED |
| 11349 | LEGITIMATE | 27952421 | 18:30:00 | 518.000000 | 69688 | SCHEDULED |
| 11349 | LEGITIMATE | 27952422 | 19:30:00 | 518.140015 | 69688 | SCHEDULED |
| **11350** | CROSSED | 27904357 | 13:30:00 | 1691.270020 | 58231 | MANUAL |
| 11350 | LEGITIMATE | 27952816 | 14:30:00 | 1702.140015 | 69689 | SCHEDULED |
| 11350 | LEGITIMATE | 27952817 | 15:30:00 | 1710.314941 | 69689 | SCHEDULED |
| 11350 | LEGITIMATE | 27952818 | 16:30:00 | 1711.185059 | 69689 | SCHEDULED |
| 11350 | LEGITIMATE | 27952819 | 17:30:00 | 1697.300049 | 69689 | SCHEDULED |
| 11350 | LEGITIMATE | 27952820 | 18:30:00 | 1692.859985 | 69689 | SCHEDULED |
| 11350 | LEGITIMATE | 27952821 | 19:30:00 | 1694.849976 | 69689 | SCHEDULED |
| **11352** | CROSSED | 27908456 | 13:30:00 | 731.929871 | 58233 | MANUAL |
| 11352 | LEGITIMATE | 27953614 | 14:30:00 | 734.669983 | 69691 | SCHEDULED |
| 11352 | LEGITIMATE | 27953615 | 15:30:00 | 735.640015 | 69691 | SCHEDULED |
| 11352 | LEGITIMATE | 27953616 | 16:30:00 | 735.575012 | 69691 | SCHEDULED |
| 11352 | LEGITIMATE | 27953617 | 17:30:00 | 735.969971 | 69691 | SCHEDULED |
| 11352 | LEGITIMATE | 27953618 | 18:30:00 | 735.650024 | 69691 | SCHEDULED |
| 11352 | LEGITIMATE | 27953619 | 19:30:00 | 735.570007 | 69691 | SCHEDULED |
| **11353** | CROSSED | 27911379 | 13:30:00 | 269.700012 | 58234 | MANUAL |
| 11353 | LEGITIMATE | 27954013 | 14:30:00 | 269.750000 | 69692 | SCHEDULED |
| 11353 | LEGITIMATE | 27954014 | 15:30:00 | 269.429993 | 69692 | SCHEDULED |
| 11353 | LEGITIMATE | 27954015 | 16:30:00 | 271.040009 | 69692 | SCHEDULED |
| 11353 | LEGITIMATE | 27954016 | 17:30:00 | 272.654999 | 69692 | SCHEDULED |
| 11353 | LEGITIMATE | 27954017 | 18:30:00 | 274.019989 | 69692 | SCHEDULED |
| 11353 | LEGITIMATE | 27954018 | 19:30:00 | 273.959991 | 69692 | SCHEDULED |
| **11351** | CROSSED | 27905533 | 13:30:00 | 13.155000 | 58232 | MANUAL |
| 11351 | LEGITIMATE | 27953215 | 14:30:00 | 13.165000 | 69690 | SCHEDULED |
| 11351 | LEGITIMATE | 27953216 | 15:30:00 | 13.185000 | 69690 | SCHEDULED |
| 11351 | LEGITIMATE | 27953217 | 16:30:00 | 13.210000 | 69690 | SCHEDULED |
| 11351 | LEGITIMATE | 27953218 | 17:30:00 | 13.170000 | 69690 | SCHEDULED |
| 11351 | LEGITIMATE | 27953219 | 18:30:00 | 13.175000 | 69690 | SCHEDULED |
| 11351 | LEGITIMATE | 27953220 | 19:30:00 | 13.055000 | 69690 | SCHEDULED |
| **11343** | LEGITIMATE | 27951618 | 13:30:00 | 311.700012 | 69686 | SCHEDULED |
| 11343 | CROSSED | 27858570 | **14:00:00** | 23140.000000 | 25560 | MANUAL |
| 11343 | LEGITIMATE | 27951619 | 14:30:00 | 311.825012 | 69686 | SCHEDULED |
| 11343 | LEGITIMATE | 27951620 | 15:30:00 | 310.440002 | 69686 | SCHEDULED |
| 11343 | LEGITIMATE | 27951621 | 16:30:00 | 310.799988 | 69686 | SCHEDULED |
| 11343 | LEGITIMATE | 27951622 | 17:30:00 | 310.839996 | 69686 | SCHEDULED |
| 11343 | LEGITIMATE | 27951623 | 18:30:00 | 311.315002 | 69686 | SCHEDULED |
| 11343 | LEGITIMATE | 27951624 | 19:30:00 | 312.500000 | 69686 | SCHEDULED |

**One structural difference on 11343 (AAPL-target), noted rather than smoothed over**: on the
other seven targets, the single crossed row sits at 13:30:00, before the legitimate run's
first row at 14:30:00. On 11343, the legitimate run's *first* row is at 13:30:00, and the
single crossed row falls at **14:00:00**, interleaved between two legitimate rows (13:30 and
14:30) rather than preceding all of them. **The crossed value (23,140.0) is also on a
completely different scale from the surrounding legitimate values (~310–312)** — consistent
with the AAPL CEDEAR's raw ARS price level rather than the underlying USD stock price,
reinforcing (not merely repeating) that this is a genuine cross-series write, not a
borderline case. This is evidence for DFA's adjudication, not a proposed resolution.

---

## Part 4 — Proposed row-level independent re-fetch procedure (design only, not executed)

**This section specifies a procedure. No step below has been run. No repair is authorized by
specifying it.**

| Element | Specification |
|---|---|
| **Source** | Each target's own configured provider assignment — i.e., the "own/legitimate" assignment identified in Part 2 for that target (e.g. for 11342, assignment 11365, provider Yahoo Finance, identifier `MU`) — queried live from the provider, independent of any value already stored in `observation`. |
| **Requested date/range** | `2026-05-28` only, for this specific adjudication (the single colliding date). A broader re-fetch of the full crossed-row range is a separate, larger procedure not specified here. |
| **Fields compared** | `value` (close) at minimum; `open`, `high`, `low`, `volume` where the source provides them, for a stronger match than close-price alone. |
| **Match criterion** | The re-fetched value for 2026-05-28 agrees with the **legitimate-row** value already stored (Part 3) within a stated, documented tolerance (e.g. matching this project's established float-equality-with-epsilon convention used elsewhere in this project's F-033 work — a specific tolerance value is not proposed here, since setting one is itself a decision, not a mechanical fact). A match supports treating the stored legitimate row as correct and the crossed row as safely excludable on this date. |
| **Non-match criterion** | The re-fetched value disagrees with the stored legitimate row beyond the documented tolerance. A non-match does **not** imply the crossed row is correct instead — it means neither stored value is yet confirmed, and both remain open pending further evidence (e.g. checking whether the source itself revised the value between the original write and the re-fetch, a distinct, real possibility this project has documented before for other series — F-009 territory). |
| **Inconclusive conditions** | (a) The provider returns no data for 2026-05-28 (a real gap, holiday, or delisting-adjacent gap). (b) The provider's returned value for that date has itself changed since original capture in a way that cannot be dated (no revision history available from the source). (c) Multiple intraday values exist at the source for that date and no documented convention exists yet for which one is "the" value to compare against a single stored row — this project's own day-dedup convention would need to be applied consistently, and is not assumed correct without restating it as an explicit step. |
| **Unavailable conditions** | (a) The provider's historical serving window does not reach back to 2026-05-28 at the time of re-fetch (unlikely for a date this recent, but not assumed — should be checked, not presumed available). (b) The configured assignment itself has since been reconfigured or removed. (c) Network/endpoint failure at fetch time — distinguishable from "no data" and should be retried, not recorded as a negative result. |
| **What a re-fetch does *not* establish** | A successful match on 2026-05-28 says nothing about the correctness of the other 2,866 (or 1,119/1,560) crossed-row dates preceding it — those would each need their own re-fetch under the same procedure, which is explicitly out of scope for this single-date adjudication. |

**This procedure is not converted into a repair authorization by being specified.** Executing
it requires separate authorization; nothing above should be read as scheduling or recommending
that authorization.

---

## Summary for DFA adjudication

Two distinct decisions are before DFA, kept explicitly separate per standing instruction:

1. **The four no-legitimate-observation targets (11344, 11345, 11346, 11347)**: not merely
   lacking a legitimate row today — lacking any provider assignment through which one could
   ever have been written. The decision is whether their crossed content belongs to another
   series' history (re-attribution) or represents the only surviving copy of otherwise-lost
   data (in which case deletion is a permanent loss, not a cleanup). Not answered here.
2. **The eight collision targets**: a single shared date (2026-05-28) where re-fetching from
   each target's own legitimate assignment (Part 4) is proposed as the resolving evidence,
   pending authorization to execute it. Every row on that date, on all eight targets, currently
   carries `origin_import_run_id = NULL` — no immutable-origin evidence exists to substitute
   for a re-fetch.

`import_run_id` was used above only to label which retrieved row came from which run — never
as the basis for any inclusion, exclusion, or match determination.
