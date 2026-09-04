# Evidence Log

**Role:** evidence register, per `Proyectos/_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md`
§1. A pointer list for `docs/evidence/` — durable-evidence and closed-historical documents
under the shared standard's four-class lens (§2). Each entry states why the document is
retained and, where applicable, what supersedes it. This file does not duplicate the
underlying documents' content, and is not itself a decision ledger — see `DECISIONS.md` for
that.

**Status of this file:** created 2026-08-27 (batch 1), extended through batch 6 (2026-08-27).
Batch 2: `CALIBRATION_*` cluster (13). Batch 3: `calibration-evidence-*` siblings (4). Batch 4:
`CLASS_E_*` except `CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md` (10). Batch 5: remaining
non-HOLD, non-Rule-D, non-core high-confidence files (28). Batch 6: the 6 Rule-D
(`src`/`tests`-cited) files — `ACQUISITION_QUALITY_INVENTORY_2026-08-22.md`,
`CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`, `CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`,
`G1_G9_Final_Domain_Ruling.md`, `DEFECT-F033.md`, `RATIO_DIAGNOSIS_2026-08-19.md` — with 8
citing docstring/comment sites across 5 source/test files updated in the same commit (7 got a
`(docs/evidence/)` discoverability note; `evidence_gated_identity_evaluator.py:3`'s literal
`docs/G1_G9_Final_Domain_Ruling.md` path was corrected to `docs/evidence/G1_G9_Final_Domain_
Ruling.md`, the one citation that would otherwise have been a wrong path rather than merely
stale). Per the 2026-08-27 reconciliation addendum to `DOCUMENTATION_MIGRATION_PLAN_2026-08-27.md`,
the reconciled inventory is 81 files total: 6 current, 56 durable-evidence/closed-historical, 6
source-coupled (Rule D), 13 HOLD. **The full 62-file high-confidence set is now migrated.**
Only 13 HOLD files and 6 current/core documents remain at `docs/` root — no further
high-confidence material is pending.

| File | Class | Retention rationale | Superseded by |
|---|---|---|---|
| [`evidence/DOM1_DISPERSION_THRESHOLD_IMPACT_TRACE_2026-09-04.md`](evidence/DOM1_DISPERSION_THRESHOLD_IMPACT_TRACE_2026-09-04.md) | Durable evidence | Read-only repository-wide impact trace for `0.167` supporting DFA's DOM-1 ruling; classifies every occurrence, confirms zero Category 3/4 findings and that no accepted INC-7 result consumed `0.167`; cited directly by `DECISIONS.md`'s DOM-1 entry and `ACTION_PLAN.md` §15o. | — |
| [`evidence/CROSS_SECTIONAL_DISPERSION_METHODOLOGY_STUDY_2026-09-04.md`](evidence/CROSS_SECTIONAL_DISPERSION_METHODOLOGY_STUDY_2026-09-04.md) | Durable evidence | Bounded, read-only cross-sectional dispersion methodology-design study (PO-authorized reactivation, `ACTION_PLAN.md` §15j); candidate-method diagnostic output only, cited directly by `ACTION_PLAN.md` §15j and the `DECISIONS.md` 2026-09-04 changelog entry. | — |
| [`evidence/F033_RETEST_2026-09-04.md`](evidence/F033_RETEST_2026-09-04.md) | Durable evidence | Bounded, read-only fresh `F-033` re-test for Microsoft/MercadoLibre/QQQ — `F033_CONFIRMED` for all three, cited directly by `ACTION_PLAN.md` §15l and the `DECISIONS.md` 2026-09-04 changelog entry; contains the exact HistFinTS question handed off for a subsequent SDT-HF root-cause investigation. | — |
| [`evidence/GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md`](evidence/GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md) | Closed historical | Authoritative record of how the adopted shared documentation-discipline standard reached its final text; cited by name in three `DECISIONS.md` changelog entries (fails the §7 "no inbound dependency" and "not an authoritative closure record" deletion conditions, so retained per §7). | `Proyectos/_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` (adopted 2026-08-26) — see the file's own header banner for the exact supersession statement. |
| [`evidence/CALIBRATION_ATTEMPT_CLOSED_2026-08-18.md`](evidence/CALIBRATION_ATTEMPT_CLOSED_2026-08-18.md) | Closed historical | Self-declared closed: the 2026-08-18 dispersion-calibration attempt, closed as insufficient evidence rather than converted into a result. | — |
| [`evidence/CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md`](evidence/CALIBRATION_DATA_GAP_SPECIFICATION_2026-08-18.md) | Durable evidence | Specifies what would close the calibration data gap identified 2026-08-18; referenced by `DECISIONS.md` and three sibling calibration docs. | — |
| [`evidence/CALIBRATION_EVIDENCE_12PAIR_COMPLETE_2026-08-18.md`](evidence/CALIBRATION_EVIDENCE_12PAIR_COMPLETE_2026-08-18.md) | Durable evidence | Point-in-time 12-pair calibration evidence run. | — |
| [`evidence/CALIBRATION_EVIDENCE_POST_CEDEAR_POPULATION_2026-08-18.md`](evidence/CALIBRATION_EVIDENCE_POST_CEDEAR_POPULATION_2026-08-18.md) | Durable evidence | Point-in-time calibration evidence, post-CEDEAR-population run. | — |
| [`evidence/CALIBRATION_EVIDENCE_REOPENED_DISPERSION_2026-08-18.md`](evidence/CALIBRATION_EVIDENCE_REOPENED_DISPERSION_2026-08-18.md) | Durable evidence | Point-in-time reopened-dispersion calibration run. | — |
| [`evidence/CALIBRATION_EXPANDED_12PAIR_DIAGNOSTICS.md`](evidence/CALIBRATION_EXPANDED_12PAIR_DIAGNOSTICS.md) | Durable evidence | Expanded 12-pair diagnostic run backing the 12-pair-complete evidence doc. | — |
| [`evidence/CALIBRATION_FRAMEWORK_REASSESSMENT_2026-08-18.md`](evidence/CALIBRATION_FRAMEWORK_REASSESSMENT_2026-08-18.md) | Durable evidence | Point-in-time reassessment of the calibration framework; cited by three sibling closure/reopen docs. | — |
| [`evidence/CALIBRATION_REOPENED_PROVENANCE_CORRECTED_2026-08-18.md`](evidence/CALIBRATION_REOPENED_PROVENANCE_CORRECTED_2026-08-18.md) | Durable evidence | Provenance-corrected reopening of the calibration analysis. | — |
| [`evidence/CALIBRATION_SAFEGUARDS_INFRASTRUCTURE_2026-08-20.md`](evidence/CALIBRATION_SAFEGUARDS_INFRASTRUCTURE_2026-08-20.md) | Durable evidence | Infrastructure design record for calibration safeguards. | — |
| [`evidence/CALIBRATION_SAFEGUARDS_MODULE_CONTRACTS_2026-08-20.md`](evidence/CALIBRATION_SAFEGUARDS_MODULE_CONTRACTS_2026-08-20.md) | Durable evidence | Module-contract design record for calibration safeguards. | — |
| [`evidence/CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_2026-08-20.md`](evidence/CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_2026-08-20.md) | Durable evidence | Origin-provenance design record for calibration safeguards; reviewed by the sibling doc below. | — |
| [`evidence/CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_REVIEW_2026-08-20.md`](evidence/CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_REVIEW_2026-08-20.md) | Durable evidence | Review of the origin-provenance safeguards design. | — |
| [`evidence/CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md`](evidence/CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md) | Durable evidence | Corrected secondary-cohort calibration run; referenced by the F026 and secondary-cohort characterization docs. | — |
| [`evidence/calibration-evidence-2026-08-18.md`](evidence/calibration-evidence-2026-08-18.md) | Durable evidence | Raw calibration evidence run, 2026-08-18; referenced by `DECISIONS.md`. | — |
| [`evidence/calibration-evidence-2026-08-18.json`](evidence/calibration-evidence-2026-08-18.json) | Durable evidence | Machine-readable data backing the calibration evidence run above; non-prose artifact retained alongside its narrative counterpart. | — |
| [`evidence/calibration-evidence-cohort-analysis-2026-08-18.md`](evidence/calibration-evidence-cohort-analysis-2026-08-18.md) | Durable evidence | Cohort-analysis breakdown of the 2026-08-18 calibration evidence run. | — |
| [`evidence/calibration-evidence-secondary-cohort-2026-08-18.md`](evidence/calibration-evidence-secondary-cohort-2026-08-18.md) | Durable evidence | Secondary-cohort breakdown of the same run; referenced by `CALIBRATION_FRAMEWORK_REASSESSMENT_2026-08-18.md` and `CALIBRATION_SECONDARY_COHORT_CORRECTED_2026-08-18.md`. | — |
| [`evidence/CLASS_E_11345_11346_DISPOSITION_IMPACT_REVIEW_2026-08-21.md`](evidence/CLASS_E_11345_11346_DISPOSITION_IMPACT_REVIEW_2026-08-21.md) | Durable evidence | Dated disposition-impact review for series 11345/11346. | — |
| [`evidence/CLASS_E_CAPABILITY_BOUNDARY_REPORT_2026-08-21.md`](evidence/CLASS_E_CAPABILITY_BOUNDARY_REPORT_2026-08-21.md) | Durable evidence | Dated capability-boundary report; cited by `CLASS_E_CLOSURE_RECORD` and `CLASS_E_IDENTITY_SIGNAL`. | — |
| [`evidence/CLASS_E_CLOSURE_RECORD_2026-08-21.md`](evidence/CLASS_E_CLOSURE_RECORD_2026-08-21.md) | Closed historical | Self-declared closure record for the Class E identity-signal work. | — |
| [`evidence/CLASS_E_GATES_FOR_BABA_BIDU_2026-08-20.md`](evidence/CLASS_E_GATES_FOR_BABA_BIDU_2026-08-20.md) | Durable evidence | Dated pair-specific (BABA/BIDU) gate evidence; cited by `CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md` (stays at `docs/` root, not yet moved). | — |
| [`evidence/CLASS_E_IDENTITY_EVIDENCE_POPULATION_STUDY_2026-08-20.md`](evidence/CLASS_E_IDENTITY_EVIDENCE_POPULATION_STUDY_2026-08-20.md) | Durable evidence | Dated population study; cited by `CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md` (Rule D, stays at `docs/` root) and `CLASS_E_MATRIX2_STABILITY_RULE` (this batch). | — |
| [`evidence/CLASS_E_IDENTITY_SIGNAL_2026-08-21.md`](evidence/CLASS_E_IDENTITY_SIGNAL_2026-08-21.md) | Durable evidence | Dated identity-signal design record; cited by `CLASS_D_EXECUTION_GATE_PACKAGE_2026-08-21.md` (stays at `docs/` root, not yet moved). | — |
| [`evidence/CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md`](evidence/CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md) | Durable evidence | Dated discovery-run record for the identity signal. | — |
| [`evidence/CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md`](evidence/CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md) | Durable evidence | Dated stability-rule record; cited by `ACQUISITION_QUALITY_INVENTORY_2026-08-22.md` and `CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md` (both Rule D, stay at `docs/` root). | — |
| [`evidence/CLASS_E_POST_D_OBSERVATION_STUDY_2026-08-21.md`](evidence/CLASS_E_POST_D_OBSERVATION_STUDY_2026-08-21.md) | Durable evidence | Dated post-D observation study. | — |
| [`evidence/CLASS_E_POST_TRANSITION_ASSESSMENT_2026-08-21.md`](evidence/CLASS_E_POST_TRANSITION_ASSESSMENT_2026-08-21.md) | Closed historical | Closure-stage assessment; cited by `CLASS_E_CLOSURE_RECORD` (this batch). | — |
| [`evidence/BRIEF-engineering-update-2026-08-17.md`](evidence/BRIEF-engineering-update-2026-08-17.md) | Closed historical | Dated engineering-status brief. | — |
| [`evidence/CLASS_D_EXECUTION_GATE_PACKAGE_2026-08-21.md`](evidence/CLASS_D_EXECUTION_GATE_PACKAGE_2026-08-21.md) | Durable evidence | Dated Class D execution-gate package; cited by several Class E docs (this and prior batches). | — |
| [`evidence/CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md`](evidence/CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md) | Durable evidence | Dated final consolidated Class D package to SE; identified during the 2026-08-27 reconciliation as omitted from the original plan table, classified DE. | — |
| [`evidence/CLAUDE_MD_STALE_REFERENCE_INVESTIGATION_2026-08-26.md`](evidence/CLAUDE_MD_STALE_REFERENCE_INVESTIGATION_2026-08-26.md) | Closed historical | Resolved investigation into a stale `CLAUDE.md` reference; cited directly from `docs/README.md`'s "Resolved 2026-08-26" note, updated to a working relative link in this batch. | — |
| [`evidence/DEFECT-F032.md`](evidence/DEFECT-F032.md) | Closed historical | Closed defect record. | — |
| [`evidence/DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md`](evidence/DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md) | Closed historical | Decision-support trail behind the adopted shared documentation-discipline standard. | `Proyectos/_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` |
| [`evidence/DOCUMENTATION_DISCIPLINE_GAP_MATRIX_2026-08-26.md`](evidence/DOCUMENTATION_DISCIPLINE_GAP_MATRIX_2026-08-26.md) | Closed historical | Same decision-support trail. | `Proyectos/_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` |
| [`evidence/EVIDENCE_MATRICES_B_D_CLASSC_IDENTITY_2026-08-20.md`](evidence/EVIDENCE_MATRICES_B_D_CLASSC_IDENTITY_2026-08-20.md) | Durable evidence | Dated cross-class evidence matrices. | — |
| [`evidence/F026_SECONDARY_COHORT_VERIFICATION_2026-08-18.md`](evidence/F026_SECONDARY_COHORT_VERIFICATION_2026-08-18.md) | Durable evidence | Dated secondary-cohort verification for finding F026. | — |
| [`evidence/F032_CONVERSION_VALIDATION_REPORT.md`](evidence/F032_CONVERSION_VALIDATION_REPORT.md) | Durable evidence | Dated conversion-validation report for finding F032. | — |
| [`evidence/FDA_BRIEF_CALIBRATION_EXPANSION_FINDINGS.md`](evidence/FDA_BRIEF_CALIBRATION_EXPANSION_FINDINGS.md) | Durable evidence | Dated FDA-facing brief on calibration-expansion findings. | — |
| [`evidence/FULL_REVERIFICATION_2026-08-19.md`](evidence/FULL_REVERIFICATION_2026-08-19.md) | Durable evidence | Dated full-reverification run. | — |
| [`evidence/G1_G9_CAPABILITY_IMPLEMENTATION_REPORT_2026-08-21.md`](evidence/G1_G9_CAPABILITY_IMPLEMENTATION_REPORT_2026-08-21.md) | Durable evidence | Dated implementation report for the G1-G9 capability. | — |
| [`evidence/G1_G9_EVALUATOR_DESIGN_2026-08-21.md`](evidence/G1_G9_EVALUATOR_DESIGN_2026-08-21.md) | Durable evidence | Dated evaluator design record. | — |
| [`evidence/G1_G9_INDEPENDENT_VALIDATION_2026-08-21.md`](evidence/G1_G9_INDEPENDENT_VALIDATION_2026-08-21.md) | Durable evidence | Dated independent validation record; cites `G1_G9_Final_Domain_Ruling.md` (Rule D, stays at `docs/` root). | — |
| [`evidence/IMPORT_STATUS_UI_VERIFICATION_2026-08-22.md`](evidence/IMPORT_STATUS_UI_VERIFICATION_2026-08-22.md) | Durable evidence | Dated UI import-status verification; cites `ACQUISITION_QUALITY_INVENTORY_2026-08-22.md` (Rule D, stays at `docs/` root). | — |
| [`evidence/INVESTIGATION-rava-integration.md`](evidence/INVESTIGATION-rava-integration.md) | Durable evidence | Dated single investigation. | — |
| [`evidence/PRIMARY_TEMPORAL_REGIME_EVIDENCE_STUDY_2026-08-18.md`](evidence/PRIMARY_TEMPORAL_REGIME_EVIDENCE_STUDY_2026-08-18.md) | Durable evidence | Dated temporal-regime evidence study. | — |
| [`evidence/PROVISIONAL_CALIBRATION_STATUS_2026-08-19.md`](evidence/PROVISIONAL_CALIBRATION_STATUS_2026-08-19.md) | Closed historical | Superseded by the later `CALIBRATION_SAFEGUARDS_*` records (2026-08-20, already migrated). | `evidence/CALIBRATION_SAFEGUARDS_INFRASTRUCTURE_2026-08-20.md` and siblings |
| [`evidence/REMEDIATION_ANALYSIS_UPDATE_DFA_RULING_2026-08-20.md`](evidence/REMEDIATION_ANALYSIS_UPDATE_DFA_RULING_2026-08-20.md) | Durable evidence | Dated remediation-analysis update. | — |
| [`evidence/REMEDIATION_BOUNDARY_ANALYSIS_A_TO_F_2026-08-20.md`](evidence/REMEDIATION_BOUNDARY_ANALYSIS_A_TO_F_2026-08-20.md) | Durable evidence | Dated boundary analysis, classes A-F. | — |
| [`evidence/REMEDIATION_DESIGN_PACKAGE_A_TO_F_2026-08-20.md`](evidence/REMEDIATION_DESIGN_PACKAGE_A_TO_F_2026-08-20.md) | Durable evidence | Dated design package, classes A-F. | — |
| [`evidence/REMEDIATION_PACKAGE_CLASS_A_2026-08-20.md`](evidence/REMEDIATION_PACKAGE_CLASS_A_2026-08-20.md) | Durable evidence | Dated remediation package, class A. | — |
| [`evidence/REMEDIATION_PACKAGE_CLASS_B_2026-08-20.md`](evidence/REMEDIATION_PACKAGE_CLASS_B_2026-08-20.md) | Durable evidence | Dated remediation package, class B. | — |
| [`evidence/REMEDIATION_PACKAGE_CLASS_D_2026-08-20.md`](evidence/REMEDIATION_PACKAGE_CLASS_D_2026-08-20.md) | Durable evidence | Dated remediation package, class D; cites `RATIO_DIAGNOSIS_2026-08-19.md` (Rule D, stays at `docs/` root). | — |
| [`evidence/SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md`](evidence/SAME_DATE_SCALE_DISCONTINUITY_2026-08-18.md) | Durable evidence | Dated discontinuity finding; cites `RATIO_DIAGNOSIS_2026-08-19.md` (Rule D, stays at `docs/` root). | — |
| [`evidence/SECONDARY_COHORT_FINAL_EVIDENCE_CHARACTERIZATION_2026-08-18.md`](evidence/SECONDARY_COHORT_FINAL_EVIDENCE_CHARACTERIZATION_2026-08-18.md) | Closed historical | Final characterization closing the secondary-cohort investigation. | — |
| [`evidence/STALENESS_TAIL_RELATIONSHIP_DIAGNOSTICS.md`](evidence/STALENESS_TAIL_RELATIONSHIP_DIAGNOSTICS.md) | Durable evidence | Dated staleness-tail diagnostic run. | — |
| [`evidence/ACQUISITION_QUALITY_INVENTORY_2026-08-22.md`](evidence/ACQUISITION_QUALITY_INVENTORY_2026-08-22.md) | Durable evidence | Dated capability inventory; cited by `src/hf_reswb/application/acquisition_quality_capability.py` and its test docstrings — both updated in this batch to note the `docs/evidence/` location. | — |
| [`evidence/CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md`](evidence/CLASS_C_EVIDENCE_PACKAGE_2026-08-20.md) | Durable evidence | Dated evidence package; cited by the same module/test pair, updated in this batch. | — |
| [`evidence/CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`](evidence/CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md) | Durable evidence | Dated identity matrix; cited by `src/hf_reswb/application/class_e_identity_signal.py` and its test docstrings, updated in this batch. | — |
| [`evidence/G1_G9_Final_Domain_Ruling.md`](evidence/G1_G9_Final_Domain_Ruling.md) | Closed historical | Final domain ruling for the G1-G9 evidence-gated identity model; cited by `src/hf_reswb/application/evidence_gated_identity_evaluator.py:3` — the one citation in this batch with a literal `docs/`-prefixed path, corrected in this batch to `docs/evidence/G1_G9_Final_Domain_Ruling.md`. | — |
| [`evidence/DEFECT-F033.md`](evidence/DEFECT-F033.md) | Closed historical | Closed defect record; cited alongside `RATIO_DIAGNOSIS_2026-08-19.md` in `src/hf_reswb/application/independence_detector.py:35`, updated in this batch. | — |
| [`evidence/RATIO_DIAGNOSIS_2026-08-19.md`](evidence/RATIO_DIAGNOSIS_2026-08-19.md) | Durable evidence | Dated ratio-diagnosis run; same citing line as above. | — |

**Batch 7 (2026-08-27, PO-ruled):** 5 more HOLD files resolved and moved on explicit PO
decision (see `HOLD_DECISION_PACKET_2026-08-27.md`), bringing the total to 67. The remaining
8 HOLD files (`IMPLEMENTATION-PANEL-ELIGIBILITY.md` — ruled current, stays; `ACQUISITION_
QUALITY_D1_D4_STATUS_ASSESSMENT_2026-08-26.md` — ruled current, stays; the 5-file F-009
bundle — ruled active, moved to `docs/histfints-requests/` instead of `docs/evidence/`; and
`PROPOSAL-docs-reorganization.md` — not yet ruled) are accounted for below and in `CLAUDE.md`,
not silently missing.

| File | Class | Retention rationale | Superseded by |
|---|---|---|---|
| [`evidence/TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md`](evidence/TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md) | Closed historical | PO-ruled: the completed Tranche-2 validation run D-044 called for; landed status confirmed. | — |
| [`evidence/VALIDATION-TRANCHE2-PRE-IMPLEMENTATION.md`](evidence/VALIDATION-TRANCHE2-PRE-IMPLEMENTATION.md) | Closed historical | PO-ruled closed; carries an additive closure note (2026-08-27) pointing to D-044 and the status-check doc above — its own "Gate: blocked" line is retained as-written but no longer current. | `evidence/TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md` |
| [`evidence/REQUEST-tranche2-migration.md`](evidence/REQUEST-tranche2-migration.md) | Closed historical | PO-ruled: landed per D-044/D-019, no longer an active filing. `CLAUDE.md`'s "Where things are" table updated accordingly. | — |
| [`evidence/ACQUISITION_QUALITY_CAPABILITY_DESIGN_D1_D5_2026-08-22.md`](evidence/ACQUISITION_QUALITY_CAPABILITY_DESIGN_D1_D5_2026-08-22.md) | Closed historical | PO-ruled: design phase closed; `ACQUISITION_QUALITY_D1_D4_STATUS_ASSESSMENT_2026-08-26.md` remains current as the live integration tracker. | — |
| [`evidence/D3_D4_APPROVED_DESIGN_INCREMENT_2026-08-22.md`](evidence/D3_D4_APPROVED_DESIGN_INCREMENT_2026-08-22.md) | Closed historical | Same PO ruling as above. | — |

| [`evidence/PROPOSAL-docs-reorganization.md`](evidence/PROPOSAL-docs-reorganization.md) | Closed historical | Decision Z, ruled 2026-08-27 (Alternative A): the predecessor proposal to this migration, now executed. Carries its own supersession banner, added in this batch. | `DOCUMENTATION_MIGRATION_PLAN_2026-08-27.md` (executed) |

**Migration status: COMPLETE.** All 68 non-current files are resolved: 68 in `docs/evidence/`
(the full high-confidence set plus all 6 PO-ruled HOLD files), the 5-file F-009 bundle in
`docs/histfints-requests/` (active filing, not evidence). **Zero HOLD files remain
unresolved.** `IMPLEMENTATION-PANEL-ELIGIBILITY.md` and `ACQUISITION_QUALITY_D1_D4_STATUS_
ASSESSMENT_2026-08-26.md` are ruled **current** (stay at `docs/` root by decision, not
oversight). The documentation migration described in `DOCUMENTATION_MIGRATION_PLAN_2026-08-27.md`
is formally closed.

## Known historical path-citations (not defects)

`DECISIONS.md` lines 2946, 2947, 2989, and 2999 cite four of the batch-3 files with a literal
`docs/` prefix (e.g. `` `docs/calibration-evidence-2026-08-18.md` ``) rather than a bare
filename. These are point-in-time ledger entries describing where the evidence was *at the
time each entry was written*, not markdown hyperlinks — no code or tooling resolves them, and
per the standard's no-retrofit rule (§6) they are intentionally left as originally written,
not corrected to the new `docs/evidence/` location. This is a documented, intentional
historical-citation pattern, not an unresolved broken-link defect — recorded here so it is not
mistaken for one in a later pass.
