# Proposal: Documentation Reorganization

**Superseded on adoption by `DOCUMENTATION_MIGRATION_PLAN_2026-08-27.md`, executed
2026-08-27 (`docs/EVIDENCE_LOG.md` is the resulting register).** This file is retained per
the shared standard's §7 (fails "no inbound dependency" — `DECISIONS.md` and the executed
migration plan cite it by name) and classified **closed historical** — kept for narrative/
audit continuity, not edited further beyond this notice.

**Date:** 2026-08-18
**Status:** PROPOSAL — not adopted, no files moved
**Origin:** Evaluation of a supplied generic "Documentation Reorganization Guide" template
against the actual `docs/` corpus of this project.

> This document records a suggestion only. Nothing in `docs/` has been moved, renamed, or
> edited on the basis of it. Adoption requires an explicit decision and a `D-###` entry in
> `DECISIONS.md`.

---

## 1. Objective

Separate the documentation corpus into clearly distinguishable tiers:

1. **Present status** — what is currently binding and must be read.
2. **Fulfilled / superseded / closed** — retained for audit, not for guidance.
3. **Knowledge pool** — phase-independent background that never becomes stale.

The supplied template addresses (1)–(3) only partially. This proposal extends it.

---

## 2. Evaluation of the supplied template

### What fits and should be kept

- The core current / archive / future split matches the stated objective directly.
- The **context-note pattern** — a short header prepended to every archived document
  stating when it was archived, why, and what supersedes it — is the most valuable element
  of the template. It prevents the failure mode already recorded in `CLAUDE.md`, where a
  superseded brief was twice misread as current.
- Restructuring the directory README into a navigational map is appropriate here.

### Where it does not fit this project

| # | Gap | Consequence |
|---|---|---|
| 1 | Assumes a feature-development project; `archive/completed_features/` has no analogue. | This is a research/evidence project: decision log, specs, defect records, dated diagnostic runs, upstream filings. The template's primary archive bucket would be empty or misused. |
| 2 | **No tier for dated evidence artifacts.** | At least eight files are timestamped empirical runs (`calibration-evidence-2026-08-18.md`/`.json`, `calibration-evidence-cohort-analysis-2026-08-18.md`, `calibration-evidence-secondary-cohort-2026-08-18.md`, `STALENESS_TAIL_RELATIONSHIP_DIAGNOSTICS.md`, `CALIBRATION_EXPANDED_12PAIR_DIAGNOSTICS.md`, `F032_CONVERSION_VALIDATION_REPORT.md`, `VALIDATION-TRANCHE2-PRE-IMPLEMENTATION.md`). These are neither current reference nor completed feature nor planning. They are **immutable evidence** — never edited, never deleted, because D-009/D-009b discipline depends on being able to re-read what was actually observed. This is the template's largest gap. |
| 3 | No outbound / interface tier. | `docs/histfints-requests/` is correspondence with an external team, with its own lifecycle (filed → landed → verified) tracked in the `DECISIONS.md` Tranche table. It is neither current-spec nor archive. |
| 4 | Conflates "completed" with "superseded". | A closed defect record and an actively-misleading superseded brief need different handling; the latter warrants a louder banner. |
| 5 | No slot for stable domain knowledge. | `KB-argentine-instruments.md` is explicitly *not* project state — it is background valid regardless of project phase. |
| 6 | Does not flag path-coupling risk. | `CLAUDE.md` hardcodes paths to six documents. Any move must update `CLAUDE.md` in the same commit or session onboarding breaks. |

---

## 3. Substitute blueprint

```
docs/
  README.md                    <- map of the corpus; what to read, in what order
  DECISIONS.md                 <- the log; never archived, append-only
  HISTFINTS-BRIEF-v2.md        <- current technical reference
  specs/                       <- live contracts (SPEC-*, IMPLEMENTATION-*)
  knowledge/                   <- KB-*, domain background, phase-independent
  evidence/                    <- dated, immutable empirical runs (read-only by convention)
  interface/histfints/         <- outbound filings and defect records (was histfints-requests/)
  archive/
    superseded/                <- replaced by a newer doc; banner names the replacement
    closed/                    <- work finished, retained for audit
    exploratory/               <- investigations that did not lead to a binding outcome
  future/                      <- designs not yet gated in
```

Six tiers rather than three, each mapping to a category already present in the corpus.

### Naming discipline

- Retain the existing `TYPE-topic` convention (`SPEC-`, `DEFECT-`, `REQUEST-`, `KB-`).
- Normalise the SHOUTING_SNAKE_CASE files into it; evidence documents become
  `EVIDENCE-<topic>-<YYYY-MM-DD>.md`.

---

## 4. Proposed retroactive mapping

| Destination | Files |
|---|---|
| `docs/` root | `DECISIONS.md`, `HISTFINTS-BRIEF-v2.md`, new `README.md` |
| `specs/` | `SPEC-panel-eligibility.md`, `SPEC-observation-suitability.md`, `SPEC-f009-evidence-consumption.md`, `IMPLEMENTATION-PANEL-ELIGIBILITY.md` |
| `knowledge/` | `KB-argentine-instruments.md` |
| `evidence/` | `calibration-evidence-2026-08-18.md` + `.json`, `calibration-evidence-cohort-analysis-2026-08-18.md`, `calibration-evidence-secondary-cohort-2026-08-18.md`, `STALENESS_TAIL_RELATIONSHIP_DIAGNOSTICS.md`, `CALIBRATION_EXPANDED_12PAIR_DIAGNOSTICS.md`, `F032_CONVERSION_VALIDATION_REPORT.md`, `VALIDATION-TRANCHE2-PRE-IMPLEMENTATION.md` |
| `interface/histfints/` | all current contents of `histfints-requests/`, plus `DEFECT-F032.md`, `DEFECT-F009.md`, `REQUEST-tranche2-migration.md` |
| `archive/closed/` | `CONSULTANT-PACKAGE-F009.md`, `CONSULTANT-README-F009.txt`, `PACKAGE-MANIFEST-F009.txt`, `BRIEF-engineering-update-2026-08-17.md`, `FDA_BRIEF_CALIBRATION_EXPANSION_FINDINGS.md` |
| `archive/exploratory/` | `INVESTIGATION-rava-integration.md`, `preliminares/`, `IA_schemes/` |

### Two items needing resolution before any move

1. **`test_import_service_defect_f009.py`** is source code residing in `docs/`. It belongs
   in a test tree, not in a documentation archive.
2. **`KB-argentine-instruments.md`** is referenced by `CLAUDE.md` but does not appear in the
   current `docs/` listing. It must be located (or its reference corrected) before the
   `knowledge/` tier can be populated.

---

## 5. Suggested sequence, if adopted

1. Confirm or amend the tiering in §3.
2. Resolve the two items in §4 (locate the missing KB document; relocate the stray test file).
3. Write `docs/README.md` as the corpus map.
4. Perform moves with `git mv`, one commit per tier, so file history is preserved.
5. Prepend context banners (3–5 lines: date archived, reason, superseding document) to every
   file placed under `archive/`.
6. Update the path table in `CLAUDE.md` in the same commit as the moves.
7. Record the reorganization as a new `D-###` entry in `DECISIONS.md`.

---

## 6. Context-banner template for archived documents

```markdown
> **ARCHIVED — <YYYY-MM-DD>**
> Status: <closed | superseded | exploratory>
> Reason: <one sentence>
> Superseded by: <path, or "n/a">
> Retained for: <audit trail | evidence chain | historical reasoning>
```

Evidence documents under `evidence/` receive **no** banner and are never modified; their
status is conveyed by their tier and their filename date.
