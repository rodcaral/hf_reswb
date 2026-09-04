# DOM-1 — Repository-Wide Dispersion-Threshold (`0.167`) Impact Trace (2026-09-04)

**Status: READ-ONLY EVIDENCE TRACE.** Performed to support DFA's DOM-1 ruling
(`DECISIONS.md`, 2026-09-04 entry) and the corresponding `SPEC_PANEL_ELIGIBILITY.md` correction.
No HistFinTS, Workbench, or production data modified. No code changed as part of this trace.

**Purpose**: search code, configuration, tests, specifications, implementation notes, evidence
documents, UI strings, fixtures, and generated outputs for `0.167` and materially equivalent
hard-coded/default representations of the historical dispersion threshold; classify every
occurrence; confirm whether any accepted bounded INC-7 result consumed it.

---

## 1. Method

Repository-wide, case-sensitive literal search for `0.167` across all tracked file types
(`.py`, `.md`, `.json`, `.yaml`/`.yml`, `.html`, `.sql`, `.txt`), excluding `.venv/`, `.git/`,
and `node_modules/`. Followed by targeted searches for materially equivalent representations:
`dispersion_threshold` assignments/defaults in `src/`, any numeric literal near `167` outside
prose, and the machine-readable calibration evidence JSON (`calibration-evidence-2026-08-18.json`)
for a stored (not merely narrated) threshold value.

## 2. Repository-wide occurrence inventory

**Fifteen files contain the literal string `0.167`.** All fifteen are documentation files —
**zero occurrences in `src/` or `tests/`**:

| File | Occurrences | Category |
|---|---|---|
| `docs/DECISIONS.md` | multiple (this session's own §15d/§15j/§15k/§15l/§15m/§15n changelog entries, now DOM-1 itself) | 1 |
| `docs/ACTION_PLAN.md` | multiple (§15d/§15h/§15j/§15k/§15l/§15m/§15n master-row and section text) | 1 |
| `docs/SPEC_PANEL_ELIGIBILITY.md` | multiple (§8.3/§8.5/§8 Open items, all now marked `[SUPERSEDED BY DOM-1]` in this same change) | 1 (corrected in this change) |
| `docs/evidence/CROSS_SECTIONAL_DISPERSION_METHODOLOGY_STUDY_2026-09-04.md` | 3 | 1 |
| `docs/evidence/calibration-evidence-cohort-analysis-2026-08-18.md` | multiple | 1 |
| `docs/evidence/PROVISIONAL_CALIBRATION_STATUS_2026-08-19.md` | 2 | 1 |
| `docs/evidence/CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md` | 1 | 1 |
| `docs/evidence/CALIBRATION_FRAMEWORK_REASSESSMENT_2026-08-18.md` | 1 | 1 |
| `docs/evidence/CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md` | 1 | 1 |
| `docs/evidence/CALIBRATION_ATTEMPT_CLOSED_2026-08-18.md` | 1 | 1 |
| `docs/evidence/CALIBRATION_EVIDENCE_POST_CEDEAR_POPULATION_2026-08-18.md` | 2 | 1 |
| `docs/evidence/CALIBRATION_EVIDENCE_12PAIR_COMPLETE_2026-08-18.md` | 5 | 1 (see §4 note — closest borderline case) |
| `docs/evidence/CALIBRATION_EXPANDED_12PAIR_DIAGNOSTICS.md` | 4 | 1 (see §4 note) |
| `docs/evidence/FDA_BRIEF_CALIBRATION_EXPANSION_FINDINGS.md` | 4 | 1 |
| `docs/evidence/DEFECT-F032.md` | 1 | 1 |

**No presentation-layer occurrence**: `grep -rl "0.167" src/hf_reswb/presentation/` returns
nothing — no CLI or web template string references `0.167`.

**No stored-value occurrence in the one machine-readable calibration artifact**:
`docs/evidence/calibration-evidence-2026-08-18.json` stores only candidate percentile levels
(`[50, 75, 90, 95]`) and staleness-day candidates — the literal value `0.167` (the P90 result of
applying those percentiles to the underlying distribution) exists only in the accompanying
narrative markdown, never as a stored JSON field.

## 3. Materially equivalent hard-coded/default representations — checked, none found

- **`dispersion_threshold` field default**: `src/hf_reswb/domain/panel.py:88` —
  `dispersion_threshold: Optional[DispersionThreshold] = None`. Default is `None`, not `0.167`
  or any other value. A `DispersionThreshold` instance must be explicitly constructed and passed
  by a caller for the field to be populated at all.
- **`should_suppress_result()`** (`src/hf_reswb/application/dispersion_analyzer.py`) takes
  `threshold: float` as a required, caller-supplied parameter — no default value in its own
  signature.
- **No config file, environment variable, or CLI flag default** found anywhere in `src/`
  referencing `167`, `0.167`, or a `DISPERSION_THRESHOLD`-named constant.
- **No test fixture** anywhere in `tests/` constructs a `DispersionThreshold` with value `0.167`
  — confirmed by the same repository-wide search returning zero `tests/` matches.

**Conclusion: `0.167` has never been wired into `hf_reswb`'s own code as a default, a
configuration value, or a test-fixture input.** The mechanism that *would* accept and apply a
dispersion threshold (`DispersionThreshold`, `should_suppress_result()`) is fully built and
tested in the abstract, but no call site anywhere in this codebase ever supplies `0.167` — or
any other concrete value — to it.

## 4. Classification detail — the two closest borderline cases

Every one of the fifteen files is Category 1 (historical/non-decision-bearing, permitted to
remain given correct qualification). Two files warrant explicit note because they contain a
genuine *computation* using `0.167` as an input, not merely a narrative mention:

- **`CALIBRATION_EVIDENCE_12PAIR_COMPLETE_2026-08-18.md`** (line 93): *"Suppression at
  provisional CV 0.167 | 2,925 / 2,925 (100.0%)"* — this document computed what would happen if
  `0.167` were applied as a live suppression rule against a 12-pair expanded cohort, and found it
  would suppress **100% of dates** — i.e., the document's own finding is that `0.167` is
  **inoperable** at that scale, not that it produced a usable, published, or accepted result.
  The document's own explicit framing: *"No threshold is selected, promoted, or hard-coded...
  Threshold action taken: None."* **Classified Category 1** — a diagnostic demonstration that
  the threshold does not work, feeding into (not itself constituting) the eventual downgrade
  decision (§15d) — not a decision-bearing application of the threshold to a real, accepted, or
  published result.
- **`CALIBRATION_EXPANDED_12PAIR_DIAGNOSTICS.md`** (lines 68/84/151/170) — the same finding,
  independently reported: *"Dates suppressed at CV > 0.167: 58/58 (100%)"*, *"CV = 0.167 remains
  **inoperable for expanded cohort**"*, *"Do not promote CV 0.167 to expanded cohort."*
  **Classified Category 1** for the identical reason — a diagnostic finding that the threshold
  fails, not an applied suppression affecting a real result.

No other file computes a suppression, eligibility, or classification outcome using `0.167` as a
live input against real data intended for publication or acceptance — every other occurrence is
purely narrative (stating the value, its provisional status, or its later retirement).

## 5. Full classification, all fifteen files

| Category | Count | Files |
|---|---|---|
| **1 — Historical/non-decision-bearing record** | **15** | All fifteen files listed in §2 |
| **2 — Pure implementation scaffolding, `0.167` not the authorized default** | **0** (see §3 — the scaffolding exists but is never populated with `0.167` anywhere, so there is no occurrence of the literal value in this category; the scaffolding itself is noted in §3, not counted as a `0.167` occurrence since it contains no such literal) | — |
| **3 — Unauthorized current default or runtime parameter** | **0** | None found |
| **4 — Actual decision-bearing consumption** | **0** | None found |

**No category-3 or category-4 occurrence was found anywhere in this repository.**

## 6. Accepted bounded INC-7 result — confirmed, not assumed, that none consumed `0.167`

Checked directly rather than taken on the prior session record's own stated expectation:

- **Module-boundary confirmation**: INC-7's entire accepted implied-FX diagnostic chain
  (`domain/implied_fx.py`, `application/implied_fx_diagnostic_service.py`,
  `application/ratio_applicability_service.py`) lives in **HistFinTS**, not Workbench. This
  session's own repeated Gate A conformance reviews of `daa0152e`/`4cb3091`/`0077a67` read every
  line of this chain — none of it imports, calls, or references `hf_reswb`'s
  `dispersion_analyzer.py`, `panel_eligibility_service.py`, or `panel.py` in any way. The two
  code bases are structurally disjoint for this capability.
- **Within `hf_reswb` itself**: `dispersion_threshold` is never populated with `0.167` (§3) —
  so even if some future Workbench-side surface *did* call into the panel/dispersion module
  chain, no code path in the current codebase would have supplied `0.167` to it.
- **Every accepted bounded INC-7 result** (§15b AAPL/Bradesco closure, §15f point-date
  capability closure, §15g AAPL production curation, §15h five-pair descriptive comparison,
  §15i Bradesco sparse temporal comparison) is a pair-specific implied-FX calculation for one
  date, computed entirely within the HistFinTS module chain above — none of these calculations
  has ever touched a dispersion, suppression, or cross-sectional aggregation code path of any
  kind, confirmed both by this trace's own source search and by every one of those closures'
  own explicit, independently-verified "no cross-sectional dispersion/consensus feature"
  finding at the time each was recorded.

**Confirmed: no accepted bounded INC-7 result consumed `0.167`, directly or indirectly.**

## 7. What this document does not do

Does not implement any code change, configuration change, or specification correction beyond
what is recorded separately at `SPEC_PANEL_ELIGIBILITY.md` (corrected in the same change this
document was produced under) and `DECISIONS.md`'s DOM-1 entry. Does not reopen any accepted
bounded INC-7 result. Does not independently declare any prior historical calibration finding
financially invalid — that adjudication remains DFA's, and PO involvement follows only if an
accepted product result is found affected (none was, per §6). Does not modify HistFinTS,
Workbench, or any production data — read-only throughout, confirmed by `git status` showing no
unexplained changes in either repository attributable to this trace.
