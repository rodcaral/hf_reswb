# F-034 Cadence Impact Assessment — DOM-2 Technical Impact (2026-09-04)

**Status: READ-ONLY TECHNICAL IMPACT ASSESSMENT.** Performed to support DFA's DOM-2 ruling
("Observation cadence suitability is time-local," `DECISIONS.md` DOM-2 entry). No HistFinTS,
Workbench, or production data modified. **No historical-cadence inference mechanism
implemented — this document identifies the design space, it does not choose within it.**
**Implementation ordering, restated as binding**: (1) F-033 Workbench quarantine integration;
(2) F-034 cadence correction; (3) historical-status correction. This assessment does not
implement item 2 ahead of item 1.

---

## 1. Governing requirement (DOM-2), restated for grounding

Observation cadence suitability is time-local. A Series' current `configured_interval` must
not be projected backward to determine whether observations in an earlier analysis period are
classifiable by session date. Eligibility for date-based observation suitability must be
established for the specific observation range. If the cadence applicable to that range cannot
be established from sufficient evidence, classification for that range is `UNRESOLVED`; current
metadata must not decide the historical state. DOM-2 does **not** authorize inferring historical
cadence merely because stored observations appear daily.

## 2. Occurrence inventory — every code path, test, specification, and UI contract where
current `configured_interval` determines historical-range classifiability

### 2.1 Code

| Location | Current behavior | What becomes `UNRESOLVED` under DOM-2 |
|---|---|---|
| `src/hf_reswb/application/suitability_service.py:45-68`, `is_classifiable()` | Queries `series.configured_interval` — the single current scalar, **no `period_start`/`period_end` parameter at all** — and returns `False` (with a reason string) whenever the current value isn't `'1d'`, or whenever *any* date in the Series' entire stored history shares a calendar date with another observation (the F-030 mixed-granularity check, itself also series-global, not range-scoped). | For a Series whose cadence changed partway through its history, a request to classify an **earlier, genuinely-daily** range must not be refused solely because the **current** value is non-daily. Under DOM-2, that range's classifiability is `UNRESOLVED` only if the cadence *applicable to that specific range* cannot be established — not automatically refused by the current value. |
| `src/hf_reswb/application/suitability_service.py:71-77`, `classify_series()` | Calls `is_classifiable()` once, unconditionally, **before** any use of its own `period_start`/`period_end` arguments; raises `ValueError` (not a soft `UNRESOLVED` result) if `is_classifiable()` returns `False`. | The exception path itself is a design point: DOM-2 requires a per-range `UNRESOLVED` classification, not necessarily a hard raise that prevents any result for the requested period at all. Whether the corrected behavior is "return `UNRESOLVED` suitability records for the range" or "raise, but only when the range's own applicable cadence is actually unresolvable" is exactly the downstream design question this assessment does not settle (§4). |
| `src/hf_reswb/application/panel_eligibility_service.py` (precondition check, "Run `classify_series()` before computing panel eligibility") | Treats a `classify_series()` failure as a hard precondition violation — if `is_classifiable()` refuses a Series, no panel eligibility computation for that Series proceeds at all, for any period. | Same as above, one level downstream — a Series wrongly excluded from an entire panel-eligibility computation (for a period where its cadence was genuinely daily) becomes eligible for correct per-range `UNRESOLVED` handling instead, once `classify_series()` itself is corrected. This module makes no independent `configured_interval` decision of its own — it inherits `classify_series()`'s behavior verbatim. |
| `src/hf_reswb/application/panel_integration.py`, `validate_suitability_coverage()` | Verifies that `classify_series()` has already been run for every contributing Series over the requested period — a coverage check, not a classification decision. | No independent behavior change — this function's own correctness is unaffected by DOM-2; it will simply see whatever `classify_series()` itself now produces once corrected. |

**No occurrence found in `src/hf_reswb/presentation/`** — `configured_interval`/cadence
classification is never displayed, labeled, or exposed in any CLI or web surface in this
codebase. **No UI contract is affected.**

### 2.2 Tests

| Test file | Finding |
|---|---|
| `tests/test_observation_suitability.py::test_ground_truth_against_real_production_series_11312` | **Confirmed still actively failing today**, independently re-run: `ValueError: series 11312 is not classifiable: configured_interval='1h', not classifiable by calendar date (F-030)`. This is the exact real-production ground-truth case DOM-2 concerns — series 11312's cadence changed from daily to hourly on `2026-08-14` (per F-034's own already-recorded root cause), and the test's own requested range (`2000-12-20`–`2001-01-02`) sits entirely inside the genuinely-daily era, over two decades before the change. |
| `tests/test_observation_suitability.py::_seed_series()` fixture | Always constructs a test Series with **one static `configured_interval` value for its entire fixture lifetime** — confirmed by direct read, no test fixture in this file (or the seven other files referencing `configured_interval`: `test_publication_aware_acquisition_diagnostic.py`, `test_acquisition_evidence_integration.py`, `conftest.py`, `test_panel_eligibility_superseded.py`, `test_panel_eligibility_phase1.py`, `test_panel_eligibility_phase2.py`, `test_panel_eligibility_integration.py`) exercises a Series whose cadence changes mid-history. **The only real evidence of this scenario in the entire test suite is the one real-production ground-truth test above, which is currently failing** — there is no synthetic/fixture-based regression test covering the DOM-2 scenario at all. |

### 2.3 Specifications

| Location | Finding |
|---|---|
| `docs/SPEC_OBSERVATION_SUITABILITY.md` (status line, and its item-6 gate table, *"F-030 (series 11311 mixed interval) — Guarded, not fixed — `is_classifiable()` refuses classification and calendar-quorum participation for any Series failing the daily/unique-date check"*) | Describes the current, series-global guard accurately as of when written — this is the specification's own honest account of a real limitation, not a false claim (unlike `SPEC_PANEL_ELIGIBILITY.md`'s separate `series.status` defect, §3 below). Amended additively per DOM-2 in the same documentation increment as this assessment — see `DECISIONS.md` DOM-2 entry and the spec's own new update block. |

## 3. Related, separately-confirmed finding: current `series.status` treated as historical
point-in-time status

Per DOM-2's own instruction to correct this in the same increment: this session's own prior
read-only Workbench impact assessment already found, and this assessment reconfirms directly:

- **`src/hf_reswb/application/panel_eligibility_service.py:99-109`** queries the plain, current
  `series.status` column (`WHERE status = 'DELISTED_OR_DISCONTINUED'`) with **no temporal
  qualifier at all**, despite the enclosing function taking an `analysis_date` parameter.
  HistFinTS's actual schema has no per-date status history table — `series.status` is a single
  current scalar.
- **`docs/SPEC_PANEL_ELIGIBILITY.md` §8.1** states, incorrectly: *"The Series' own `status` **at
  that historical date** would have been `ACTIVE`... **The `status` field is historical per
  row, not a current flag.**"* This is factually wrong about the schema and is corrected in the
  same documentation increment as this assessment (additive `[SUPERSEDED BY DOM-2]` marker,
  original text preserved).

**Until point-in-time status evidence exists, current `series.status` cannot establish
historical status for a prior analysis date** — restated per DOM-2's own instruction. **No
historical-status mechanism is invented here.**

## 4. Smallest technically viable design options for establishing cadence for a historical
range — separated by evidence category, per instruction

**Evidence already persisted today:**

- **Raw stored-observation shape for the requested range itself** — the actual `observed_at`
  timestamps and their calendar-date distinctness *within the requested `period_start`/
  `period_end`*, independent of the Series' current `configured_interval`. This is exactly what
  F-034's own root-cause finding already used to establish that series 11312's `2000-12-20`–
  `2001-01-02` window is genuinely daily (6,681 total rows, 6,632 distinct days for the Series
  overall; the requested window's own rows are one-per-day). **This evidence exists today and
  requires no schema change** — it would require the classification function itself to inspect
  the *requested range's own rows* rather than the Series-level `configured_interval` field.
  **This is evidence-derivation by direct observation of the range in question, not inference
  from a different period** — the closest option to "evidence already persisted," though it
  still requires a design decision about *what pattern within the range counts as sufficient*
  (see the financial-sufficiency question below).
- **`import_run` history for observations in the range** — which import runs produced the
  range's own rows, and whether those runs' own metadata (if any exists) recorded an intended
  cadence at the time of that specific import. Requires checking whether `import_run` (or any
  linked table) carries a per-run cadence assertion today — **not confirmed by this assessment;
  a follow-up query against the live schema would be needed**, not performed here since it edges
  toward root-causing the mechanism, which this assessment does not do.

**Evidence derivable only by inference:**

- **Inferring "this range is daily" purely from the fact that stored observations for that
  range happen to appear one-per-day.** **DOM-2 explicitly does not authorize this** — the
  ruling's own text: *"DOM-2 does not authorize inferring historical cadence merely because
  stored observations appear daily."* Named here only to rule it out explicitly, not as a live
  option.
- **Inferring a per-range cadence from a broader population's own typical cadence-change
  date** (e.g., "all CEDEAR series changed cadence around 2026-08-14, so any request before that
  date is presumptively daily") — this generalizes across Series rather than establishing the
  *specific* Series/range's own applicable cadence, and would require DFA's own judgment on
  whether cross-Series generalization is ever financially sufficient evidence — **not decided
  here, flagged for DFA if this direction is ever pursued.**

**Schema/history that does not currently exist:**

- **A per-date or per-range `configured_interval` history table** — the structurally cleanest
  fix (mirroring how `provider_assignment.first_available_date`/`last_available_date` at least
  *attempt* to carry a bounded span, however imperfectly per this session's own separate DOM-1/
  circularity finding) — but this requires a new HistFinTS-side schema addition and a backfill
  of historical cadence-change dates, neither of which exists today. **This is the option most
  likely to satisfy DOM-2's own requirement cleanly, but is also the most expensive and requires
  HistFinTS-side design/migration work**, not something Workbench can build unilaterally given
  the read-only architectural boundary (D-001).
- **A structured cadence-change event log** (an evidence-signal-style append-only record of
  "Series X's cadence changed from A to B, effective date D, source/reason") — a lighter-weight
  alternative to a full per-date history table, closer in shape to this project's own
  `EvidenceSignal`/`ratio_applicability_assertion` precedent (a POINT/PERIOD-style dated
  assertion, rather than a per-row column). Also does not exist today; also requires new
  HistFinTS-side schema.

## 5. Operational consequences and migration requirements, by option

| Option | Operational consequence | Migration required |
|---|---|---|
| Inspect the requested range's own stored-observation shape directly | Changes `is_classifiable()`'s own signature to accept `period_start`/`period_end` (currently absent) and re-derive its calendar-date-uniqueness check scoped to the range, not the whole Series history. No schema change. | None — a Workbench-side code change only, once the design question below is settled. |
| Cross-Series/population-level cadence-change inference | Would require a new analytical construct (a "population cadence-change date" concept) with its own evidentiary bar. | Design-only; no schema change strictly required, but the *evidence-sufficiency* question is unresolved (see below). |
| Per-date/per-range `configured_interval` history table | Requires a new HistFinTS migration, a backfill campaign (of unknown feasibility — historical cadence-change dates may not be independently recorded anywhere upstream), and a new Workbench-side read path. | HistFinTS-side schema migration + backfill; Workbench-side consumer changes. |
| Structured cadence-change event log (evidence-signal-style) | Same HistFinTS-side schema requirement as above, but additive/append-only rather than a dense per-date table — likely cheaper to backfill incrementally as evidence is found, at the cost of remaining incomplete for undocumented changes. | HistFinTS-side schema migration; Workbench-side consumer changes; ongoing curation discipline (matching the `RatioApplicabilityAssertion` precedent already established for a structurally similar problem). |

## 6. Explicit DFA-adjudication flag — evidence sufficiency, not engineering convenience

**This assessment does not choose among these options on engineering convenience, per
instruction.** The genuinely open, financially-material question underlying every option above
is: **what evidence is financially sufficient to establish that a specific historical range's
cadence was daily (or any other specific interval)?** Candidates include (but this assessment
does not rank or select among them):

- The requested range's own stored-observation shape alone (one row per calendar date,
  consistently, for the entire range) — evidentially available today, but DOM-2's own text
  suggests this alone may not be considered sufficient, since it is close in kind to "inferring
  cadence merely because stored observations appear daily" (the explicitly-prohibited
  inference) unless it is understood as *directly observing* the range rather than
  *inferring* from a different range.
- A recorded, sourced cadence-change event (a new schema concept, not yet built).
- Cross-Series population evidence (explicitly the weakest, least range-specific candidate
  named above).

**This is identified explicitly for DFA adjudication, not resolved here.**

## 7. What this document does not do

Does not implement a historical-cadence inference mechanism. Does not choose among the design
options in §4/§5. Does not implement items 2 (F-034 cadence correction) or 3 (historical-status
correction) of the binding implementation ordering — item 1 (F-033 Workbench quarantine
integration) has not yet landed, and this assessment does not get ahead of it. Does not modify
HistFinTS, Workbench, or any production data — read-only throughout, confirmed: the one test run
performed (`test_ground_truth_against_real_production_series_11312`) reads the real production
database in read-only mode and writes nothing.
