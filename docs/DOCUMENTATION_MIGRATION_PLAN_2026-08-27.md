# Workbench Documentation Migration Plan — Read-Only Dry Run

**Date:** 2026-08-27
**From:** SDT Workbench
**Status: PLAN ONLY. No file has been moved, renamed, deleted, or rewritten to produce this
document.** Every classification below was verified against the actual file (reference check,
last-modified date, opening content), not assumed from filename alone.

> **Reconciliation addendum — 2026-08-27, post-batch-2.** This plan's original body (below,
> unedited) contains two errors, found by reconciling the table rows against the actual
> 81-file root inventory rather than trusting the prose counts:
>
> 1. **§3/§7/§8 said "16 files" for the `CALIBRATION_*`/`calibration-evidence-*` cluster.**
>    The true count is **13** files matching `CALIBRATION_*` (§5.2) plus **4** differently-named
>    `calibration-evidence-*` siblings (also §5.2) — 17 total, not 16. Batch 2 (executed) moved
>    only the 13 `CALIBRATION_*` files, matching the literal name pattern the batch was
>    commissioned against. The 4 `calibration-evidence-*` files were correctly *not* moved in
>    batch 2 (they were never in scope for it), but this addendum makes that explicit rather
>    than leaving it implied.
> 2. **Two files from the original 81-file inventory were never given a row in any §5 table**
>    — an omission in the original pass, not a deliberate exclusion:
>    - `CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md` — read against Rule B: same cluster as the
>      already-classified `CLASS_D_EXECUTION_GATE_PACKAGE_2026-08-21.md`, dated, closed
>      read-only report to SE, no `src`/`tests` coupling. **Classified DE, added to §5.2.**
>    - `VALIDATION-TRANCHE2-PRE-IMPLEMENTATION.md` — read in full: its own header states
>      `**Gate:** Panel-eligibility implementation blocked until these validations pass`,
>      directly gating the still-current `SPEC-panel-eligibility.md`. This is **not** closed
>      history — moving it into `evidence/` would have hidden a possibly still-binding
>      implementation gate as if it were settled. **Classified HOLD (Rule C), added to §5.4.**
>      This is the more consequential of the two corrections.
>
> **Corrected inventory (81 files, reconciled):**
>
> | Bucket | Original count | Corrected count |
> |---|---|---|
> | §5.1 Current | 6 | 6 (unchanged) |
> | §5.2 Durable evidence / closed historical | 55 (table rows undercounted the prose by 6; true row count was 55) | **56** (+`CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md`) |
> | §5.3 Source-coupled (Rule D, subset of high-confidence) | 6 | 6 (unchanged) |
> | §5.4 HOLD | 12 (prose said 13, table rows were 12) | **13** (+`VALIDATION-TRANCHE2-PRE-IMPLEMENTATION.md`) |
> | **Total** | 79 (2 short of 81) | **81 — reconciles** |
>
> High-confidence set (§5.2 + §5.3) is now **62** files, not 55 or 61 as different prose
> passages in the original plan stated. **14 of the 62 are already moved** (batch 1: 1;
> batch 2: 13) — see §3/§7 execution notes above, now superseded by the actual batch reports.
> **48 remain unmoved.** No file's *classification* changed as a result of correcting the
> count — only two previously-uncounted files were classified for the first time.

**Cross-repo anchor:** not applicable — this plan concerns `workbench` only. No claim below is
made about `histfints-v3`, `histfints_uiue`, or any predecessor repository's current state.

**Relationship to prior proposals:** this plan supersedes and reconciles
[`evidence/PROPOSAL-docs-reorganization.md`](evidence/PROPOSAL-docs-reorganization.md)
(2026-08-18, never adopted; moved to `docs/evidence/` 2026-08-27) and absorbs the findings of
[`evidence/DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md`](evidence/DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md)
and
[`evidence/DOCUMENTATION_DISCIPLINE_GAP_MATRIX_2026-08-26.md`](evidence/DOCUMENTATION_DISCIPLINE_GAP_MATRIX_2026-08-26.md)
(both moved to `docs/evidence/` 2026-08-27, batch 5).
None of those three files is moved by this plan itself — see row treatment below — but on
**approval** of this plan, `PROPOSAL-docs-reorganization.md` should receive the same one-line
supersession pointer already used on `GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md`
(a precedent this plan follows, not invents). That edit is a follow-up action, not part of this
read-only step.

---

## 1. Rules used (every row below cites one of these)

Applying the four-class lens and the entry-point/index roles already adopted in
`Proyectos/_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` (§1–§2, §8), plus §5a
(predecessor-repository lineage — the same "don't let a superseded, dated document look
live" failure mode this plan is applying one level down, to *documents* rather than
*repositories*).

| Rule | Applies when | Class | Destination |
|---|---|---|---|
| **A — Current** | The file is `DECISIONS.md`, `README.md`, `HISTFINTS-BRIEF-v2.md`, or a `SPEC-*.md` still describing a contract with a live, referencing implementation in `src/`/`tests/`. | Current | Stays in `docs/` root. |
| **B — Durable evidence / closed historical** | The file is dated (explicit `YYYY-MM-DD` in name or header), documents a completed investigation/calibration run/defect diagnosis/remediation package/closure record, and is referenced only by other `docs/*.md` files via plain backticked filename mentions — never a relative markdown link, never a functional dependency in `src/`/`tests/`. | Durable evidence or closed historical (sub-tag: closed-historical if the file's own text declares itself closed/final/superseded; durable-evidence otherwise) | `docs/evidence/` |
| **C — Recently active / still-cited design reference** | The file is evidence-shaped by Rule B but is the most recently touched file in its cluster, or a later (more recent) status document still cites it as the design source being worked from, not just as history. | Ambiguous | **HOLD** — defer past the first batch |
| **D — Source-coupled** | The file is cited by filename in a `src/` or `tests/` docstring/comment (verified: none of these citations use a relative path, so a move causes no functional breakage — but the comment becomes a stale same-folder assumption). | Durable evidence (usually) | `docs/evidence/`, but sequenced in its own batch with the citing comment corrected in the same commit |
| **E — Structural mismatch with an existing claim** | `CLAUDE.md`'s own "Where things are" table already asserts a location for this file that does not match where it actually is. | Ambiguous | **HOLD** — the mismatch itself needs a decision (fix the claim, or finally move the file to match it) before either action is taken |
| **F — Non-prose artifact** | The file is not a markdown document (`.json`, `.py`, `.txt` data/manifest files) sitting at `docs/` root. | Usually durable evidence | `docs/evidence/`, flagged — no existing convention in this project for where non-md artifacts belong |
| **G — Open, undecided proposal** | The file is itself a live, not-yet-adopted proposal about documentation structure (i.e., would be self-referential to move it while this plan is pending). | Ambiguous | **HOLD** until this plan is decided |

**Memory-equivalence check (all rows):** none of the candidate files have an equivalent
load-bearing fact captured in `memory/` — per the shared standard's Git/docs/memory boundary
(§3), Workbench's memory layer holds session-relationship facts (user role, feedback,
project-status pointers), not this repository's evidence corpus. Moving any of these files
does **not** orphan a fact that only memory currently holds. This column is answered "No" for
every row below and not repeated per-file.

---

## 2. Target layout (proposed, not yet created)

```
docs/
  README.md                 <- unchanged: reading-order entry point
  DECISIONS.md               <- unchanged: continuity ledger, never archived
  HISTFINTS-BRIEF-v2.md      <- unchanged: current technical reference
  SPEC-f009-evidence-consumption.md   <- unchanged: live contract
  SPEC-observation-suitability.md     <- unchanged: live contract
  SPEC-panel-eligibility.md           <- unchanged: live contract
  EVIDENCE_LOG.md            <- NEW: evidence register (§1 role). Pointer list only —
                                 filename, one-line retention rationale, class tag. Does not
                                 duplicate the underlying documents' content.
  evidence/                  <- NEW: flat physical home for durable-evidence and
                                 closed-historical dated documents. One folder, not
                                 subdivided by class — the class tag lives in
                                 EVIDENCE_LOG.md, not in a subfolder name (avoids two
                                 mechanisms disagreeing about the same fact, per §4).
  histfints-requests/         <- unchanged, out of scope this increment (already a
                                 correctly-separated outbound-filing subfolder)
  preliminares/                <- unchanged, out of scope this increment
  reproducibility/              <- unchanged, out of scope this increment
```

### Why `evidence/`, not `archive/` — not an aesthetic choice

1. **Vocabulary collision avoided.** The just-adopted shared standard's evidence-register role
   is already named `EVIDENCE_LOG.md`. Naming the physical folder `archive/` would create two
   different names for the same concept inside one project — exactly the "overlapping,
   differently-named mechanism" risk §4 of the standard warns against. `evidence/` keeps one
   vocabulary end to end: the register is `EVIDENCE_LOG.md`, the folder is `evidence/`.
2. **Domain fit.** `DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md` already found that
   HistFinTS's `archive/completed_features/` model doesn't transfer to Workbench — Workbench
   has no "features," it has dated investigations, calibration runs, and defect diagnoses.
   `evidence/` names what's actually in the folder; `archive/` would be a borrowed label for a
   different shape of project.
3. **Existing domain-word collision.** This project's own domain vocabulary already uses
   "archived" for a specific, different, technical meaning — `series.archived_at` (D-003,
   HistFinTS's MERGE-driven staleness marker). Reusing "archive" for a documentation folder in
   the same project, describing an unrelated concept, is the kind of same-word/different-meaning
   ambiguity P3 (traceability) exists to prevent.

**Single flat folder, no `evidence/current/` vs `evidence/closed/` split**: the smallest
structure that separates current documentation from retained evidence is one boundary
(`docs/` root vs `docs/evidence/`), not two. Sub-splitting by class inside the folder would be
a second taxonomy competing with `EVIDENCE_LOG.md`'s own per-entry class tag.

---

## 3. Migration sequence (incremental — none of this executes in this step)

1. **Establish conventions (no moves).** Create `docs/EVIDENCE_LOG.md` with its header and
   format (empty of entries, or seeded only with files already informally treated this way —
   see `GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md`, which already carries a
   hand-written supersession banner). Add one line to `docs/README.md`'s reading-order section
   naming `EVIDENCE_LOG.md` and `evidence/` as the destination for dated supporting material,
   mirroring the existing "Convention — marking evidence anchored to a sibling repository"
   section's style. **No file leaves `docs/` root in this step.**
2. **Migrate the smallest, highest-confidence batch.** See §5 — the `CALIBRATION_*` /
   `calibration-evidence-*` cluster (16 files, self-contained, zero `src`/`tests` references,
   zero relative-markdown-link references anywhere in the corpus — confirmed by a full
   reference sweep, see §4). Move files with `git mv` (preserves history), add each to
   `EVIDENCE_LOG.md`, and add a "moved to `evidence/`, [date]" note only if a specific file
   already carries an inbound reference worth updating (most don't, since the corpus cites
   filenames as bare backticked text, not paths).
3. **Update references and indexes.** Re-run the reference sweep from §4 against the moved
   set; confirm no `docs/README.md` link or `src/`/`tests/` docstring pointed at any moved file
   (true for this batch by construction — Rule B explicitly excludes source-coupled files from
   the first batch).
4. **Validate discoverability and authority signaling.** Re-check the acceptance criteria in
   §6 against the post-move state: can a reader still find `DECISIONS.md`/`README.md`/
   `HISTFINTS-BRIEF-v2.md`/the three `SPEC-*.md` files exactly as easily (yes — untouched);
   does anything in `docs/evidence/` now look like a live, competing source (no — each file's
   own dated, closed content is unchanged, and `EVIDENCE_LOG.md` states its status).
5. **Only afterward, revisit Rule C/D/E/F/G HOLD cases**, one cluster at a time, each requiring
   an explicit decision recorded in `DECISIONS.md` before moving (per the standard's own
   supersession discipline, §6) — not folded into the same batch as the high-confidence set.

### Rollback

Every move in step 2 is a single `git mv` per file inside one repository with a clean working
tree beforehand (per this session's own git-safety discipline). Rollback is `git revert` of
the migration commit(s), or, if uncommitted, `git checkout -- docs/` before anything is
committed. No cross-repository state, no database, no generated artifact depends on
`docs/` file location — confirmed by the tooling scan in §4b. This makes the batch fully and
cheaply reversible; rollback risk is not a reason to defer the first batch.

---

## 4. Reference and tooling scan (methodology)

A full-repository reference sweep was run for every candidate filename (`grep -rl` across the
whole `workbench` working tree, `.git/` internals excluded as noise). Findings:

- **No file in this project references another `docs/*.md` file by relative markdown path**
  (`[text](../docs/X.md)` or similar) anywhere in the corpus checked — `DECISIONS.md`, every
  dated evidence doc, and every `src/`/`tests/` docstring cite filenames as plain backticked
  text (e.g. `` `CALIBRATION_ATTEMPT_CLOSED_2026-08-18.md` ``), not as clickable paths. This
  means moving a file into `docs/evidence/` breaks **zero** functional hyperlinks anywhere in
  this repository. The only real relative-markdown-links found are in `docs/README.md`'s
  reading-order list, and none of its five linked targets (`HISTFINTS-BRIEF-v2.md`,
  `DECISIONS.md`, the two `SPEC-*.md` files, `histfints-requests/`) are migration candidates.
- **`src/` and `tests/` docstrings cite several docs by filename**, confirmed for:
  `ACQUISITION_QUALITY_INVENTORY_2026-08-22.md`, `CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`,
  `CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`, `G1_G9_Final_Domain_Ruling.md`,
  `DEFECT-F033.md`, `RATIO_DIAGNOSIS_2026-08-19.md`, and all three `SPEC-*.md` files (which
  stay put under Rule A). These citations are prose inside comments, not import paths — no
  code breaks on a move — but the comment becomes a stale same-folder assumption unless
  corrected in the same commit as the move (Rule D).

### 4b. Scripts, CI, and generators

- No `.github/` workflow directory exists in this repository (confirmed: `find .github` —
  empty). No CI pipeline currently reads `docs/` paths.
- No documentation generator, `index.yaml`, or build tooling references `docs/` file paths
  (confirmed: no `.yml`/`.yaml` config outside `pyproject.toml`, which contains no `docs/`
  reference).
- `pyproject.toml`'s `[tool.pytest.ini_options]` sets `testpaths = ["tests"]` — the stray
  `docs/test_import_service_defect_f009.py` is **not** currently collected by pytest regardless
  of its location; moving it changes nothing about test execution (see row F1 in §5).
- `.claude/settings.local.json` contains one string match on
  `IMPLEMENTATION-PANEL-ELIGIBILITY.md`, but it is a commit-message permission pattern, not a
  path reference — moving the file does not affect it.

---

## 5. File-by-file dry-run table

Legend — **Class**: `CUR` current · `DE` durable evidence · `CH` closed historical ·
`HOLD` ambiguous, decision required. **Ref?**: distinct files elsewhere in the repo that
mention this filename (`.git/` internals excluded). **Breaks links/tooling?**: per §4, "No" for
every row unless noted — no relative-path or functional reference exists anywhere in this
corpus. **Mem. equiv.?**: answered "No" for all rows, per §1's memory-equivalence check.

### 5.1 Core current documents — Rule A — no change proposed

| File | Class | Destination | Reason |
|---|---|---|---|
| `README.md` | CUR | stays | Reading-order entry point |
| `DECISIONS.md` | CUR | stays | Continuity ledger, never archived by its own convention |
| `HISTFINTS-BRIEF-v2.md` | CUR | stays | Current technical reference, linked from `README.md` |
| `SPEC-f009-evidence-consumption.md` | CUR | stays | Live contract, 22 references incl. `src/domain/evidence.py`, `finding.py` |
| `SPEC-observation-suitability.md` | CUR | stays | Live contract, referenced by `src/domain/suitability.py`, `suitability_service.py` |
| `SPEC-panel-eligibility.md` | CUR | stays | Live contract, 28 references incl. 5 `src/application/*` modules |

### 5.2 High-confidence durable evidence / closed historical — Rule B — `docs/evidence/`

| File | Class | Ref? | Confidence |
|---|---|---|---|
| `CALIBRATION_ATTEMPT_CLOSED_2026-08-18.md` | CH (self-declared "closed") | 2 (`DECISIONS.md`, `CALIBRATION_FRAMEWORK_REASSESSMENT`) | High |
| `CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md` | DE | 4 | High |
| `CALIBRATION_EVIDENCE_12PAIR_COMPLETE_2026-08-18.md` | DE | 2 | High |
| `CALIBRATION_EVIDENCE_POST_CEDEAR_POPULATION_2026-08-18.md` | DE | 1 | High |
| `CALIBRATION_EVIDENCE_REOPENED_DISPERSION_2026-08-18.md` | DE | 2 | High |
| `CALIBRATION_EXPANDED_12PAIR_DIAGNOSTICS.md` | DE | 1 | High |
| `CALIBRATION_FRAMEWORK_REASSESSMENT_2026-08-18.md` | DE | 1 | High |
| `CALIBRATION_REOPENED_PROVENANCE_CORRECTED_2026-08-18.md` | DE | 3 | High |
| `CALIBRATION_SAFEGUARDS_INFRASTRUCTURE_2026-08-20.md` | DE | 1 | High |
| `CALIBRATION_SAFEGUARDS_MODULE_CONTRACTS_2026-08-20.md` | DE | 1 | High |
| `CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_2026-08-20.md` | DE | 2 | High |
| `CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_REVIEW_2026-08-20.md` | DE | 1 | High |
| `CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md` | DE | 3 | High |
| `calibration-evidence-2026-08-18.md` | DE (Rule F: lowercase/data-adjacent) | 2 | High |
| `calibration-evidence-2026-08-18.json` | DE (Rule F: non-md artifact) | 1 | High |
| `calibration-evidence-cohort-analysis-2026-08-18.md` | DE (Rule F) | 2 | High |
| `calibration-evidence-secondary-cohort-2026-08-18.md` | DE (Rule F) | 4 | High |
| `CLASS_D_EXECUTION_GATE_PACKAGE_2026-08-21.md` | DE | 1 | High |
| `CLASS_E_11345_11346_DISPOSITION_IMPACT_REVIEW_2026-08-21.md` | DE | 1 | High |
| `CLASS_E_CAPABILITY_BOUNDARY_REPORT_2026-08-21.md` | DE | 1 | High |
| `CLASS_E_CLOSURE_RECORD_2026-08-21.md` | CH (self-declared "closure record") | 2 | High |
| `CLASS_E_GATES_FOR_BABA_BIDU_2026-08-20.md` | DE | 2 | High |
| `CLASS_E_IDENTITY_EVIDENCE_POPULATION_STUDY_2026-08-20.md` | DE | 3 | High |
| `CLASS_E_IDENTITY_SIGNAL_2026-08-21.md` | DE | 4 | High |
| `CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md` | DE | 6 | High |
| `CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md` | DE | 3 | High |
| `CLASS_E_POST_D_OBSERVATION_STUDY_2026-08-21.md` | DE | 2 | High |
| `CLASS_E_POST_TRANSITION_ASSESSMENT_2026-08-21.md` | CH | 2 | High |
| `EVIDENCE_MATRICES_B_D_CLASSC_IDENTITY_2026-08-20.md` | DE | 3 | High |
| `G1_G9_CAPABILITY_IMPLEMENTATION_REPORT_2026-08-21.md` | DE | 1 | High |
| `G1_G9_EVALUATOR_DESIGN_2026-08-21.md` | DE | 3 | High |
| `G1_G9_INDEPENDENT_VALIDATION_2026-08-21.md` | DE | 2 | High |
| `REMEDIATION_ANALYSIS_UPDATE_DFA_RULING_2026-08-20.md` | DE | 2 | High |
| `REMEDIATION_BOUNDARY_ANALYSIS_A_TO_F_2026-08-20.md` | DE | 3 | High |
| `REMEDIATION_DESIGN_PACKAGE_A_TO_F_2026-08-20.md` | DE | 2 | High |
| `REMEDIATION_PACKAGE_CLASS_A_2026-08-20.md` | DE | 1 | High |
| `REMEDIATION_PACKAGE_CLASS_B_2026-08-20.md` | DE | 1 | High |
| `REMEDIATION_PACKAGE_CLASS_D_2026-08-20.md` | DE | 3 | High |
| `DEFECT-F032.md` | CH (defect closed per `FDA_BRIEF_CALIBRATION_EXPANSION_FINDINGS`) | 2 | High |
| `F026_SECONDARY_COHORT_VERIFICATION_2026-08-18.md` | DE | 2 | High |
| `F032_CONVERSION_VALIDATION_REPORT.md` | DE | 3 | High |
| `FDA_BRIEF_CALIBRATION_EXPANSION_FINDINGS.md` | DE | 2 | High |
| `FULL_REVERIFICATION_2026-08-19.md` | DE | 3 | High |
| `PRIMARY_TEMPORAL_REGIME_EVIDENCE_STUDY_2026-08-18.md` | DE | 3 | High |
| `PROVISIONAL_CALIBRATION_STATUS_2026-08-19.md` | CH (superseded by later `CALIBRATION_SAFEGUARDS_*`, Aug 20) | 1 | High |
| `SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md` | DE | 5 | High |
| `SECONDARY_COHORT_FINAL_EVIDENCE_CHARACTERIZATION_2026-08-18.md` | CH | 1 | High |
| `STALENESS_TAIL_RELATIONSHIP_DIAGNOSTICS.md` | DE | 4 | High |
| `BRIEF-engineering-update-2026-08-17.md` | CH | 1 | High |
| `INVESTIGATION-rava-integration.md` | DE | 1 | High |
| `IMPORT_STATUS_UI_VERIFICATION_2026-08-22.md` | DE | 1 | High |
| `CLAUDE_MD_STALE_REFERENCE_INVESTIGATION_2026-08-26.md` | CH (resolved, tracked in `README.md`'s own "Resolved" note) | 3 | High |
| `DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md` | CH (superseded — findings absorbed into adopted standard) | 4 | High |
| `DOCUMENTATION_DISCIPLINE_GAP_MATRIX_2026-08-26.md` | CH | 3 | High |
| `GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md` | CH (**already self-declared** closed-historical with its own pointer note — see §5's opening) | 2 | Highest — recommended proof-of-concept single-file first move |

### 5.3 Source-coupled — Rule D — `docs/evidence/`, own sequenced sub-batch

| File | Class | Ref? | Note |
|---|---|---|---|
| `ACQUISITION_QUALITY_INVENTORY_2026-08-22.md` | DE | 7, incl. `src/application/acquisition_quality_capability.py`, `tests/test_acquisition_quality_capability.py` | Move together with the comment-line fix in the citing module |
| `CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md` | DE | 11, incl. `src/`, `tests/` | Same treatment |
| `CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md` | DE | 11, incl. `src/application/class_e_identity_signal.py`, `tests/` | Same treatment |
| `G1_G9_Final_Domain_Ruling.md` | DE | 7, incl. `src/application/evidence_gated_identity_evaluator.py` | Same treatment |
| `DEFECT-F033.md` | CH | 11, incl. `src/application/independence_detector.py` | Same treatment |
| `RATIO_DIAGNOSIS_2026-08-19.md` | DE | 6, incl. `src/application/independence_detector.py` | Same treatment |

### 5.4 HOLD — decision required (Rules C, E, F, G)

| File | Rule | Why it's ambiguous |
|---|---|---|
| `ACQUISITION_QUALITY_CAPABILITY_DESIGN_D1_D5_2026-08-22.md` | C | Still cited by name as the design reference in `ACQUISITION_QUALITY_D1_D4_STATUS_ASSESSMENT_2026-08-26.md` (Aug 26 — the most recent doc in this repo touching this capability). Closing it now risks looking like the capability itself is closed, when the status assessment treats it as still-open. |
| `ACQUISITION_QUALITY_D1_D4_STATUS_ASSESSMENT_2026-08-26.md` | C | Most recently modified file at `docs/` root (2026-08-26 22:47, same minute as `DECISIONS.md`'s last edit). Almost certainly still current-status, not evidence — needs an explicit "is D1-D4 closed?" answer before classifying, not an inference from filename shape. |
| `D3_D4_APPROVED_DESIGN_INCREMENT_2026-08-22.md` | C | Same cluster as the two rows above; "APPROVED" language suggests still-binding design, not closed history. |
| `IMPLEMENTATION-PANEL-ELIGIBILITY.md` | C | Described in its own commit message as a "roadmap"; `CLAUDE.md`'s status section says panel-eligibility is "ready to implement for non-gated parts" — this may be the live roadmap for exactly that unfinished work, not closed evidence. |
| `TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md` | C | Titled as a status tracker for a workstream `CLAUDE.md` explicitly says is still open ("not yet confirmed landed"). A dated status doc for an *unresolved* workstream is exactly the "looks current, might not be" shape this plan exists to catch — needs a human call on whether `DECISIONS.md`'s Tranche table has fully superseded it. |
| `PROPOSAL-docs-reorganization.md` | G | The predecessor of this very plan. Self-referential to move while pending; gets a supersession pointer note on approval, per the `GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md` precedent — not moved in this pass. |
| `DEFECT-F009.md` | E | `CLAUDE.md`'s own "Where things are" table already (incorrectly) claims this file is at `docs/histfints-requests/DEFECT-F009.md`. It is actually at `docs/DEFECT-F009.md`. This is a **pre-existing bug independent of this plan** — fix direction (correct `CLAUDE.md`, or finally move the file to match it) is a decision, not an inference. |
| `REQUEST-tranche2-migration.md` | E | Same mismatch as above — `CLAUDE.md` claims `docs/histfints-requests/`, file is actually at `docs/` root. |
| `CONSULTANT-PACKAGE-F009.md` | E | Part of the same F009 filing package as the two rows above; its correct home depends on the same undecided call. |
| `CONSULTANT-README-F009.txt` | E, F | Same package; also a non-md artifact. |
| `PACKAGE-MANIFEST-F009.txt` | E, F | Same package; also a non-md artifact. |
| `test_import_service_defect_f009.py` | E, F | Same package; a Python file at `docs/` root is itself structurally unusual — not collected by pytest (`testpaths = ["tests"]`), so moving it breaks nothing functionally, but where evidence-artifact code belongs has no existing convention in this project. |

---

## 6. Acceptance-criteria check against this plan (not yet executed)

| # | Criterion | Status |
|---|---|---|
| 1 | No file movement occurs | **Met** — zero `git mv`/edits performed in producing this plan |
| 2 | Every proposed move traceable to a documented rule | **Met** — every row in §5 cites Rule A–G from §1 |
| 3 | No current authoritative document becomes harder to find | **Met by construction** — §5.1's six files are untouched; §4 confirms no `README.md` link targets a migration candidate |
| 4 | Historical/audit evidence remains permanently discoverable | **Addressed** — `git mv` preserves history (`git log --follow`); `EVIDENCE_LOG.md` gives a durable pointer list; nothing in §5.2/§5.3 is proposed for deletion |
| 5 | Closed/superseded records are not preserved as competing live-looking sources | **Addressed for §5.2/§5.3** — moving out of `docs/` root plus an `EVIDENCE_LOG.md` status tag removes the "looks current" ambiguity. **Not yet addressed for §5.4** — those are exactly the files still capable of looking live, which is why they're HOLD, not silently left in place forever |
| 6 | Ambiguous files remain untouched | **Met** — 13 files explicitly marked HOLD in §5.4, none scheduled for the first batch |
| 7 | Layout reduces root clutter without a new parallel system | **Addressed** — one new folder (`evidence/`), one new register (`EVIDENCE_LOG.md`), both named to match already-adopted shared-standard vocabulary rather than inventing a second taxonomy |

---

## 7. Smallest safe first batch, if this plan is approved

**`GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md` alone**, as a one-file proof of
concept: it already carries its own correct supersession banner from a prior decision, has
zero `src`/`tests` coupling, and is referenced only as plain text from two other docs. A single
`git mv docs/GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md docs/evidence/` plus one
`EVIDENCE_LOG.md` entry validates the whole mechanism (folder creation, register entry,
post-move discoverability check) at minimum risk before committing to the 16-file
`CALIBRATION_*`/`calibration-evidence-*` batch described in §3 step 2.

## 8. Overall recommendation

**GO WITH HOLDS.**

The high-confidence set (§5.2 + §5.3, 55 files) has a clean, rule-traceable classification, no
functional-link breakage anywhere in the repository, and a target layout that reuses rather
than duplicates the vocabulary this project already adopted. The plan should proceed to Phase 1
(conventions) and the single-file proof-of-concept in §7 once approved.

It is **not GO (unqualified)** because 13 files (§5.4) resist confident classification without
a human answer to specific, named questions (is D1–D4 closed? is `TRANCHE2_AND_MIGRATIONS_
STATUS_2026-08-19.md` superseded by `DECISIONS.md`'s own Tranche table? which side of the
`DEFECT-F009.md` location mismatch is correct?) — guessing on any of them risks exactly the
failure this plan exists to prevent: a document that looks authoritative sitting in the wrong
place, or a closed record staying visible as if still live.
