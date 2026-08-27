# histfints-v3 — Non-`.md` Scripts/Data Registration Decision Packet

**Date:** 2026-08-27 · **From:** SDT Workbench, applying the `documentation-lifecycle` skill ·
**Status: read-only. No file moved, edited, or registered in producing this packet.** Every
pairing below was confirmed by reading each artifact's actual header/docstring content — not
inferred from filename similarity alone, per instruction.

**Cross-repo anchor:** `histfints-v3`, state as read on 2026-08-27, after the first additive
`EVIDENCE_LOG.md` batch (5 entries, executed this session, confirmed reconciling).

**Batch 1 result (already executed, for context):** 5 entries added to `EVIDENCE_LOG.md`
(`ACCESSIBILITY_GATE_STATUS_2026-08-25.md`, `AT_VALIDATION_ATTEMPT_INCIDENT_SUMMARY_2026-08-25.md`,
`AT_VALIDATION_PROCEDURE.md`, `SCREEN_READER_VALIDATION_SCRIPT_2026-08-25.md`,
`INTEGRITY_AUDIT_RAW_EVIDENCE_2026-08-20.txt`). Verified: 36 total register entries (26 DE + 7
RM + 3 CH), discoverable via `README.md` → `EVIDENCE_LOG.md`, no prior entry displaced, all 5
evidence artifacts' own content untouched, all 3 HOLDs (`ENV_TEMP_REVERT_2026-08-20.txt`,
`reconcile_with_workbench.py`, `CAPABILITY_A_D_IMPLEMENTATION_ASSESSMENT_2026-08-26.md`'s
closure status) left exactly as they were.

---

## Confirmed pairings — 20 files, content-verified

Each entry below cites the specific line(s) read that establish the pairing, not just the name.

| Script/data file | Paired document | Evidence for pairing (read, not inferred) |
|---|---|---|
| `byma_evidence_raw.json` | `BYMA_EVIDENCE_PACKAGE_2026-08-19.md` (DE) | Content is raw BYMA market-data records (symbol/trade/quote fields, `market: "BYMA"`) |
| `byma_independence_evidence.py` | `BYMA_EVIDENCE_PACKAGE_2026-08-19.md` / `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (both DE) | Docstring: "BYMA EOD - source, coverage, provenance, and INDEPENDENCE-TEST INPUTS... The F-033 signature is..." |
| `byma_independence_timeseries.py` | Same as above | Docstring: "F-033 time-series independence test against the BYMA evidence path" |
| `capture_remediation_baseline.py` | `REMEDIATION_BOUNDARY_PLAN_A_TO_F_2026-08-20.md` (DE) | Docstring: "Pre-remediation baseline capture (P1) and verification matrix" |
| `classc_orphan_analysis_2026-08-21.txt` | `CLASS_C_SEVEN_ROW_DISPOSITION_2026-08-21.md` / `CLASS_C_EVIDENCE_PACKAGE_2026-08-21.md` (DE) | Content: per-target Class-C orphan analysis (series 11344 GLD, duplicate/conflict analysis) |
| `classc_readiness.py` | `CLASS_C_IMPLEMENTATION_READINESS_2026-08-21.md` (DE) | Docstring: "Class-C implementation readiness -- AUTHORIZED POPULATIONS ONLY" |
| `discrepancy_diagnosis.py` | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (DE) | Docstring header literally: "F-033 CORRELATION DISCREPANCY DIAGNOSIS" |
| `invariants_abd.py` | `REMEDIATION_DESIGN_A_B_D_2026-08-21.md` (DE) | Docstring: "Before/after invariants for the authorized Class-C moves, plus A/B/D readiness evidence" |
| `isolate_mechanism.py` | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (DE) | Docstring: "Isolate WHICH factor drives each reproduction of +1.00" — same F-033 investigation |
| `pairwise_auth.py` | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (DE) | Docstring: "Pair-level detail under AUTHORITATIVE denominators" — same series set (MU/MSFT/AMD/MELI/NU/QQQ/AMZN) as the F-033 investigation |
| `post_activation_verification_20260820T150417Z.txt` | `H_0015_ACTIVATION_RECORD_2026-08-20.md` (DE) | Content: "POST-ACTIVATION PRODUCTION VERIFICATION... epoch (supplied explicitly) = 2026-08-20" — migration 0015 activation |
| `post_activation_verification_20260821T014756Z.txt` | Same as above | Same content pattern, later timestamp — a second run of the same verification |
| `reconcile_with_workbench.py` | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` / `DB_FACT_VERIFICATION_FOR_WORKBENCH_MATRICES_2026-08-21.md` (both DE) | **HOLD resolved by content, not filename.** Docstring: "RECONCILIATION vs Workbench reproducibility package... tests BOTH claims by rerunning each test under two denominator sets" — this is a dated, one-off reconciliation script for a specific, named F-033 discrepancy, not a general-purpose or repeatedly-invoked cross-repo tool. No re-run instruction, no "standing check" language, no evidence anywhere of ongoing use. |
| `remediation_boundary_analysis_2026-08-20.txt` | `REMEDIATION_BOUNDARY_PLAN_A_TO_F_2026-08-20.md` (DE) | Content: "CLASS A -- boundary precision... CLASS B..." — matches the plan doc's own class structure |
| `sdt1_design_probe.py` | `SDT1_IMPLEMENTATION_DESIGN_11345_11346_2026-08-21.md` (DE) | Docstring: "SDT-1 implementation-design probe" |
| `sdt1_identity_evidence.py` | `SDT1_IDENTITY_DECISION_RECORD_11345_11346_2026-08-21.md` (DE) | Docstring: "SDT-1: identity evidence for Series 11345 / 11346" — exact subject match |
| `test_raw_cedear_correlation.py` | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (DE) | Docstring: "Test raw CEDEAR value correlation among the seven" — same seven-CEDEAR F-033 population |
| `test_return_correlation.py` | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (DE) | Docstring explicitly: "Reproduce Workbench's actual measurement... Workbench (DEFECT-F033-shared-driver-mechanism.md) reports..." |
| `test_shared_driver_hypothesis.py` | `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (DE) | Docstring: "Test: are the seven flagged CEDEARs' live-window values synthetic derivations of underlying_USD x shared_FX" |
| `verify_seven_unchanged.py` | `CLASS_C_IMPLEMENTATION_READINESS_2026-08-21.md` (DE) | Docstring **directly cites** the target document by path: "Compares live state against the values recorded in `docs/CLASS_C_IMPLEMENTATION_READINESS_2026-08-21.md` section 1.1" — strongest possible confirmation |

## New nuance found — 3 files, not simple Evidence pairing

Reading these surfaced something the filename-only pass missed: they describe themselves as
**repeatable/standing tools**, not one-off dated artifacts, even though they originated from a
specific investigation.

| File | What was found | Why it doesn't fit plain Evidence |
|---|---|---|
| `verify_0015_activation.py` | Docstring: *"Read-only. **Re-runnable at any time.**"* | A tool meant for ongoing use, not a closed record of one run — closer to Reusable Methodology, or possibly still-current operational tooling |
| `verify_post_activation_collection.py` | Docstring: *"Run after the first post-activation BYMA collection: `python docs/verify_post_activation_collection.py`"* — an invocation instruction, not a past-tense report | Same shape — a runnable procedure, not a dated finding |
| `collect_byma_evidence.py` | Docstring: *"IDEMPOTENT. Safe to run once per trading session."* | Explicitly designed for repeated, ongoing invocation (this is the "controlled" collector `check_evidence_path_uncontrolled_writes.py` refers to) — an operational tool with dated evidence *outputs* (like `byma_evidence_raw.json`, above), not itself a dated artifact |

**Recommendation, not a decision:** these three likely belong in `EVIDENCE_LOG.md`'s Reusable
Methodology section (or a still-current operational-tooling note, if this repo would rather
classify them that way) rather than Durable Evidence — flagged for whoever owns the register's
conventions to confirm, since it's a genuine classification call, not something this pass
should silently resolve.

## Assessed separately — 1 file paired with a current document

`check_evidence_path_uncontrolled_writes.py` — docstring: *"Standing check: has any
UNCONTROLLED path written successfully into an evidence series?... Controlled = the dedicated
collector (`docs/collect_byma_evidence.py`)... A successful uncontrolled write means an
evidence row exists with no raw response behind it, which breaks the evidence-preservation
property the F-033 independence test depends on."* Explicitly a **standing check** tied to
`OPEN_ISSUE_evidence_path_uncontrolled_writes.md` (current/core, unresolved). This is
current-adjacent operational tooling, not Evidence — should not be registered in
`EVIDENCE_LOG.md` at all; if indexed anywhere, it belongs alongside the open issue it checks,
governed by the same current-documentation structure per this repo's own convention (per
`EVIDENCE_LOG.md`'s existing note about the 4 CR-but-unlisted files).

## Confirmed still-HOLD

None. `reconcile_with_workbench.py`'s status is resolved (see table above — recommend
promoting it out of HOLD in the next batch, into the confirmed-Evidence set, paired with the
F-033 investigation documents). `ENV_TEMP_REVERT_2026-08-20.txt` was not in scope for this
pass (it is not a script/data file paired with an investigation — it remains HOLD as reported
previously, untouched). `CAPABILITY_A_D_IMPLEMENTATION_ASSESSMENT_2026-08-26.md`'s closure
status was likewise not investigated further in this pass.

---

## Smallest next safe registration batch

**20 files** — the "Confirmed pairings" table above, all as Durable Evidence entries appended
to their already-listed paired document's line (or as new adjacent bullets), following
`EVIDENCE_LOG.md`'s existing per-document annotation style. This includes
`reconcile_with_workbench.py`, whose HOLD status is now resolved by content evidence, not
inference.

**Held back from this batch, pending a classification call (not ambiguity, a genuine choice):**
`verify_0015_activation.py`, `verify_post_activation_collection.py`,
`collect_byma_evidence.py` — Reusable Methodology vs. current operational tooling.

**Not to be registered as Evidence at all:** `check_evidence_path_uncontrolled_writes.py` —
current-adjacent, belongs with the open issue it checks, not in the Evidence register.

**Untouched, unchanged from the prior packet:** `ENV_TEMP_REVERT_2026-08-20.txt`,
`CAPABILITY_A_D_IMPLEMENTATION_ASSESSMENT_2026-08-26.md`'s closure question.
