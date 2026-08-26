# histfints-v3 Docs Retention — Final 34-Row Disposition Matrix (Four-Class Model)

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE / PO / SDT HistFinTS
**Status: read-only analysis only. No file in `histfints-v3/docs/` deleted or moved.**

---

## Flag before the matrix: two premises I could not verify

1. **"HistFinTS's determinations for the three previously ambiguous artifacts"** —
   searched `histfints-v3` (including today's freshly-updated core docs — `README.md`,
   `ARCHITECTURE.md`, `DOMAIN_MODEL.md`, `DATABASE_SCHEMA.md`, `APPLICATION_SERVICES.md`,
   `PRESENTATION.md`, `KNOWN_LIMITATIONS.md`, all touched 2026-08-25/26) for any record of a
   determination on `INTEGRITY_AUDIT_BASELINE_2026-08-20.md`,
   `DRIFT_TOLERANT_SOURCE_FACTS_2026-08-21.md`, or `INTEGRITY_CAPABILITY_INVENTORY_2026-08-22.md`.
   **Found none.** None of the three files was itself modified since the earlier review, and
   none is referenced from today's updated core docs. Rather than block this deliverable, the
   matrix below carries **Workbench's own reasoned classification** for these three, explicitly
   marked — replace with HistFinTS's actual determination if it exists and differs.
2. The **four-class model's definitions** were given inline in the instruction itself, so
   that part needed no external document — applied directly.

---

## The four classes, as given

- **CR** — Current reference documentation
- **DE** — Durable evidence/audit record
- **RM** — Reusable technical methodology/capability record
- **CH** — Closed historical decision/context

---

## Protected dependencies — formally classified DE, retained

| File | Class | Basis |
|---|---|---|
| `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` | **DE — retained** | Per original instruction; cited by `PROVENANCE_INTEGRITY_import_run_id_mutability.md`. |
| `SDT1_POST_EXECUTION_VALIDATION_2026-08-21.md` | **DE — retained** | Per original instruction; self-declared final closure record of the SDT-1 chain. |
| `SDT1_EXECUTION_RECORD_11345_11346_2026-08-21.md` | **DE — retained** | Found 2026-08-25; cited directly by `DATABASE_SCHEMA.md`, a permanently-kept core doc. |

---

## Full 34-row disposition matrix

| # | File | Class | Inbound refs (who cites it) | Disposition |
|---|---|---|---|---|
| 1 | `ACQUISITION_HEALTH_INVESTIGATION_2026-08-22.md` | CH | 1 — cited by its own superseding doc (#2) | **Retain** (fails deletion condition 1 — see §Deletion candidates) |
| 2 | `ACQUISITION_HEALTH_INVESTIGATION_RECONCILED_2026-08-22.md` | DE | — | Retain — the operative, corrected record |
| 3 | `BYMA_EVIDENCE_COLLECTION_SCHEDULE.md` | CR | — | Retain — describes a standing, still-active configuration |
| 4 | `BYMA_EVIDENCE_PACKAGE_2026-08-19.md` | DE | 2 | Retain — F-033 evidence package |
| 5 | `CLASS_C_EVIDENCE_PACKAGE_2026-08-21.md` | DE | 1 | Retain — evidence for the accepted disposition |
| 6 | `CLASS_C_IMPLEMENTATION_READINESS_2026-08-21.md` | DE | 1 | Retain — pre-execution readiness evidence |
| 7 | `CLASS_C_SEVEN_ROW_DISPOSITION_2026-08-21.md` | DE | 1 | Retain — the Class-C closure record |
| 8 | `CLASS_D_EXECUTION_RECORD_2026-08-21.md` | DE | — | Retain — execution record |
| 9 | `CLASS_D_POST_EXECUTION_CLOSURE_2026-08-21.md` | DE | — | Retain — authoritative closure record |
| 10 | `CLASS_E_EVIDENCE_BOUNDARY_2026-08-21.md` | RM | 2 | Retain — reusable evidentiary-boundary reasoning |
| 11 | `DB_FACT_VERIFICATION_FOR_WORKBENCH_MATRICES_2026-08-21.md` | DE | 2 | Retain — verification evidence |
| 12 | `DRIFT_TOLERANT_SOURCE_FACTS_2026-08-21.md` | RM *(Workbench classification — HistFinTS determination not located)* | 0 | Retain, pending confirmation — describes a reusable moving-data verification technique |
| 13 | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` | DE | Protected | **Retain (protected)** |
| 14 | `G1_G9_IDENTITY_EVIDENCE_EVALUATOR_2026-08-22.md` | RM | — | Retain — reusable capability report |
| 15 | `H_0015_ACTIVATION_RECORD_2026-08-20.md` | DE | 2 | Retain — migration activation record |
| 16 | `H_0015_PRE_EXECUTION_REVIEW_PACKAGE_2026-08-20.md` | DE | — | Retain — pre-execution evidence |
| 17 | `H_ORIGIN_PROVENANCE_MIGRATION_DESIGN_2026-08-20.md` | DE | 1 | Retain — design+verification record for an executed migration |
| 18 | `INDEPENDENT_CEDEAR_SOURCE_BYMA_EOD_2026-08-19.md` | RM | 1 | Retain — reusable data-source/path description |
| 19 | `INTEGRITY_AUDIT_BASELINE_2026-08-20.md` | DE *(Workbench classification — HistFinTS determination not located)* | — | Retain, pending confirmation — a dated baseline snapshot, evidentiary |
| 20 | `INTEGRITY_CAPABILITY_INVENTORY_2026-08-22.md` | RM *(Workbench classification — HistFinTS determination not located)* | — | Retain, pending confirmation — cites 3 other artifacts (#8-ish/#31/#30), so removing it would leave those less discoverable |
| 21 | `INTEGRITY_FINDING_INVENTORY_2026-08-20.md` | DE | 1 | Retain — finding/remediation-classification evidence |
| 22 | `OPEN_ISSUE_evidence_path_uncontrolled_writes.md` | **CR** | 2 | Retain — explicitly self-declared **OPEN**, not closed; must never be a deletion candidate while unresolved |
| 23 | `ORIGIN_PROVENANCE_SEMANTICS_ANSWERS_2026-08-20.md` | CH | 1 — cited by its own superseding doc (#25) | **Retain** (fails deletion condition 1 — see §Deletion candidates) |
| 24 | `PROVENANCE_INTEGRITY_import_run_id_mutability.md` | CR | 1 | Retain — self-declared **Status: Open** |
| 25 | `PROVENANCE_SEMANTIC_CONTRACT_2026-08-20.md` | CR | — | Retain — the resolved, operative contract; **check recommended**: today's updated `DATABASE_SCHEMA.md` may now duplicate this content — worth a redundancy pass, not proposed here |
| 26 | `REMEDIATION_BOUNDARY_PLAN_A_TO_F_2026-08-20.md` | DE | — | Retain — foundational remediation-boundary evidence |
| 27 | `REMEDIATION_DESIGN_A_B_D_2026-08-21.md` | DE | — | Retain — design+evidence record |
| 28 | `REMEDIATION_SEQUENCING_AND_VERIFICATION_2026-08-20.md` | RM | 1 | Retain — reusable sequencing/verification requirements |
| 29 | `SDT1_EXECUTION_GATE_PACKAGE_11345_11346_2026-08-21.md` | DE | 1 | Retain — authorization evidence trail |
| 30 | `SDT1_EXECUTION_NOGO_2026-08-21.md` | CH | 1 — cited by #20 (`INTEGRITY_CAPABILITY_INVENTORY`) | **Retain** (fails deletion condition 1 — see §Deletion candidates) |
| 31 | `SDT1_EXECUTION_RECORD_11345_11346_2026-08-21.md` | DE | Protected | **Retain (protected)** |
| 32 | `SDT1_IDENTITY_DECISION_RECORD_11345_11346_2026-08-21.md` | DE | — | Retain — identity-decision evidence |
| 33 | `SDT1_IMPLEMENTATION_DESIGN_11345_11346_2026-08-21.md` | DE | 1 | Retain — majority of content not superseded |
| 34 | `SDT1_POST_EXECUTION_VALIDATION_2026-08-21.md` | DE | Protected | **Retain (protected)** |

**Class tally**: CR 4, DE 21 (including 3 protected), RM 6, CH 3.

---

## Deletion candidates — verified against all five conditions

**Only files classified CH (closed historical decision/context) are even eligible** — that's
what the class means. Three qualify for consideration: #1, #23, #30.

| # | File | (1) No inbound dependency | (2) No unique evidence/reproducibility content | (3) Operative conclusion preserved elsewhere | (4) Not an authoritative closure/validation record | (5) Removal doesn't make retained docs incomplete/misleading | **Result** |
|---|---|---|---|---|---|---|---|
| 1 | `ACQUISITION_HEALTH_INVESTIGATION_2026-08-22.md` | **FAILS** — cited by name in `ACQUISITION_HEALTH_INVESTIGATION_RECONCILED_2026-08-22.md`'s own "Supersedes (on the NEVER count only): ..." line | Partially fails — holds the original figure/methodology not restated in full elsewhere | Yes, on the corrected figure | Yes | Would fail — the RECONCILED doc's "Supersedes" citation would point to a missing file | **Not a deletion candidate as-is** |
| 23 | `ORIGIN_PROVENANCE_SEMANTICS_ANSWERS_2026-08-20.md` | **FAILS** — cited by name in `PROVENANCE_SEMANTIC_CONTRACT_2026-08-20.md`'s "Supersedes: ORIGIN_PROVENANCE_SEMANTICS_ANSWERS_2026-08-20.md (which identified gaps; this...)" | Partially fails — the original three open questions aren't restated in the contract | Yes, on the resolved contract | Yes | Would fail — same dangling-citation problem | **Not a deletion candidate as-is** |
| 30 | `SDT1_EXECUTION_NOGO_2026-08-21.md` | **FAILS** — cited by name in `INTEGRITY_CAPABILITY_INVENTORY_2026-08-22.md` | Holds the unique halt-reason/timestamp for the first attempt | Yes, on the successful execution | Yes | Would fail — the capability inventory's citation would dangle | **Not a deletion candidate as-is** |

**Result: zero of the 34 currently satisfy all five deletion conditions.** Every candidate that
made it into the CH class is still cited by name from a document that itself is being retained
— removing the cited file would leave a dangling reference in the citing document, which
directly fails condition 5 ("removal does not make retained documentation incomplete or
misleading") in every case checked.

**If SE/PO still wants housekeeping on these three**, the only way any of them could pass all
five conditions is a two-step action, not proposed here: first edit the citing document to
remove or fold in the specific reference (e.g., replace "Supersedes:
`ACQUISITION_HEALTH_INVESTIGATION_2026-08-22.md`" with an inline one-sentence summary of what
was originally wrong), *then* the cited file would newly satisfy condition 1 and could be
re-evaluated. That edit is itself a change to a retained document and would need its own
approval — flagged as a possible follow-up, not executed or proposed as this deliverable's
action.

---

## Exact proposed housekeeping actions for approval — there are none to propose

Per the five-condition verification above, **no file currently qualifies for deletion,
moving, or collapsing.** The only concrete housekeeping items surfaced by this pass are:

1. **Confirm or correct** the three Workbench-authored classifications marked "HistFinTS
   determination not located" (#12, #19, #20) — no action until SE/SDT HistFinTS responds.
2. **Optional redundancy check** on `PROVENANCE_SEMANTIC_CONTRACT_2026-08-20.md` (#25) against
   today's updated `DATABASE_SCHEMA.md` — flagged, not investigated further here, since it
   would require reading today's `DATABASE_SCHEMA.md` in full against this doc's content, which
   this task's scope (34-file baseline, not the 12 already-indexed core docs) didn't call for.
3. **If** SE/PO wants the three CH-classified files (#1, #23, #30) actually removed later, the
   citing documents (#2, #25, #20 respectively) would need their "Supersedes"/citation text
   edited first — a separate, explicitly-approved action.

No file was deleted, moved, or collapsed in producing this matrix.
