# histfints-v3 Docs Retention — Baseline Preservation + Corrected Audit Conclusion

**Date:** 2026-08-25
**From:** SDT Workbench
**To:** SE / SDT HistFinTS
**Status: read-only analysis only. No file in `histfints-v3/docs/` deleted, moved, collapsed,
or rewritten. `memory/`, `docs/README.md`, `CLAUDE.md`, and every source artifact are
untouched.**

**Important scoping note, stated up front**: no prior "34-file inventory audit" document could
be located anywhere in `histfints-v3`, `histfints_uiue`, or `workbench` — this session has no
record of one being produced. The classification below (which files are "closed-decision" vs.
"ambiguous") is therefore **independently derived from this pass**, not a correction applied to
a specific prior document I've verified. Treat it as a fresh baseline, not a continuation of
unseen prior work, until the original audit (if one exists) can be located and reconciled
against it.

---

## 1. Baseline preserved

**34 artifacts** = every `.md` file in `histfints-v3/docs/` **not** named in `index.yaml`'s
`docs:` block (46 total `.md` files − 12 indexed = 34). Confirmed by direct listing, not
assumed. None renamed, moved, or deleted in producing this analysis.

---

## 2. Correction to the audit conclusion

**Checked directly against the live `index.yaml` content, not assumed**: `index.yaml`'s
`docs:` block names exactly 12 files (7 `core_reference` + `README.md` + 4
`accessibility_validation` `.md` files — the fifth accessibility item is a directory, not a
file). **It does not name any of the 34 artifacts by filename anywhere in the document** —
confirmed by direct search. The claim that "three artifacts were already referenced through
`index.yaml`" is **not corroborated by `index.yaml`'s current content**.

What *is* true, found independently this pass:

- `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` is referenced by name from
  **one other artifact in the 34** (`PROVENANCE_INTEGRITY_import_run_id_mutability.md`), not
  from `index.yaml` and not from any of the 12 permanently-kept docs.
- `SDT1_POST_EXECUTION_VALIDATION_2026-08-21.md` has **zero** inbound references from any file
  in the directory, `index.yaml`, `README.md`, or `CLAUDE.md`. Its protected status rests
  entirely on a structural fact, not a citation: it is the self-declared terminal record of the
  SDT-1 (11345/11346) chain (*"Status: FINAL — this is the SDT-1 validation record of record.
  SDT-1 is closed"*) — the last document in a six-document sequence, which is exactly why
  nothing later cites it.
- One inbound reference **was** found that the "three via index.yaml" framing may have been
  reaching for: `DATABASE_SCHEMA.md` — one of the 12 permanently-indexed docs — cites
  `SDT1_EXECUTION_RECORD_11345_11346_2026-08-21.md` directly. That's a real dependency from a
  kept doc into the 34, just not via `index.yaml` itself, and not one of the two names given.

**Recommendation on the correction**: restate the audit conclusion as *"no artifact among the
34 is referenced from `index.yaml`'s own text; at least one (`SDT1_EXECUTION_RECORD_11345_
11346_2026-08-21.md`) is referenced from a permanently-kept doc (`DATABASE_SCHEMA.md`) and
should be treated as a protected retention dependency alongside the two already named,"* rather
than the "three via index.yaml" framing as given — unless the original audit document surfaces
and shows a different basis for that claim.

---

## 3. Protected retention dependencies (per instruction, plus one found)

| File | Why protected |
|---|---|
| `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` | Per instruction. Cited by `PROVENANCE_INTEGRITY_import_run_id_mutability.md`. |
| `SDT1_POST_EXECUTION_VALIDATION_2026-08-21.md` | Per instruction. Zero inbound citations, but is the self-declared final closure record of the six-document SDT-1 chain. |
| `SDT1_EXECUTION_RECORD_11345_11346_2026-08-21.md` (newly found) | Cited directly by `DATABASE_SCHEMA.md`, one of the 12 permanently-kept core-reference docs. Flagging for the same protected treatment, not yet acted on. |

None of these three is included in the 10-row table below — they're excluded from
retire/summarize consideration by definition.

---

## 4. Retention-decision table — 7 closed-decision + 3 ambiguous

Selection basis, stated plainly: **closed-decision** = the document's own content shows its
question was resolved, executed, or explicitly superseded by a later document in the same
chain. **Ambiguous** = zero inbound references and no self-declared terminal/superseding
status — genuinely unclear without asking someone who was closer to the work.

*Existing memory coverage*: checked against this session's own `memory/` — empty except one
unrelated standing rule (sibling-repo write confirmation). **None of the 34 has any memory
coverage today** — restated per row for completeness, not because it varies.

### Closed-decision (7)

| File | Unique information | Inbound references | Memory coverage | Consequence of removal | Recommended |
|---|---|---|---|---|---|
| `SDT1_EXECUTION_NOGO_2026-08-21.md` | The one halted/failed first attempt at the 11345/11346 execution — exact pre-flight failure reason and timestamp. | 0 | None | Loses the record that a first attempt was halted before the successful one — relevant if anyone later asks "why two attempts." | **Summarize** — fold its halt-reason into the SDT-1 chain's own history note, then remove the standalone file. |
| `H_0015_PRE_EXECUTION_REVIEW_PACKAGE_2026-08-20.md` | Pre-execution review snapshot for migration 0015, before activation. | 0 | None | Loses the "what was reviewed before we said yes" snapshot for 0015 — the activation record alone doesn't show what was checked beforehand. | **Retain** — pre-execution review packages are the kind of evidence this whole multi-party protocol has repeatedly needed to reconstruct after the fact (see this session's own repeated "verify before trusting" incidents). Low cost to keep, real cost if a later dispute needs it. |
| `ORIGIN_PROVENANCE_SEMANTICS_ANSWERS_2026-08-20.md` | The original three open questions on `origin_import_run_id` semantics, before they were resolved. | 1 (from `PROVENANCE_SEMANTIC_CONTRACT_2026-08-20.md`, which supersedes it) | None | Loses visibility into what was originally *unclear* about this field — the resolved contract doesn't show the gaps it closed. | **Summarize** — the resolved contract is what matters going forward; a short "originally open questions" note inside it would preserve the history without keeping a full duplicate file. |
| `CLASS_C_IMPLEMENTATION_READINESS_2026-08-21.md` | Pre-execution readiness check for the seven Class-C rows and the BABA/BIDU items, before the accepted disposition. | 1 | None | Loses the readiness-gate detail preceding the accepted disposition. | **Retain** — same reasoning as the 0015 review package: pre-decision evidence has repeatedly mattered later in this project. |
| `ACQUISITION_HEALTH_INVESTIGATION_2026-08-22.md` | Original NEVER-count figure and methodology, explicitly superseded on that one count by its RECONCILED sibling. | 1 (self-referenced by its own superseding doc) | None | Loses the original (now-known-imprecise) figure and the reasoning that led to the correction — useful for anyone auditing *how* the reconciliation happened, not just its result. | **Retain** — this is exactly the kind of "here's what we got wrong and why" record this project has valued keeping (e.g. this session's own retracted-package incidents were kept as cautionary reference, not deleted). |
| `SDT1_IMPLEMENTATION_DESIGN_11345_11346_2026-08-21.md` | The original read-only implementation design for the 11345/11346 disposition, partially superseded (§1–2, §7.1–7.2) by the later gate package. | 1 | None | Loses the full original design rationale — the gate package only supersedes two sections, so most of this doc's content isn't duplicated elsewhere. | **Retain** — majority of its content is not superseded; removing it would lose non-duplicated design reasoning. |
| `SDT1_EXECUTION_GATE_PACKAGE_11345_11346_2026-08-21.md` | The final pre-execution gate checklist actually authorized against. | 1 | None | Loses the exact gate conditions PO/DFA actually signed off on before execution — the execution record shows what happened, not what was required to happen first. | **Retain** — this is the authorization evidence trail; removing it weakens the audit chain between "ruling" and "execution" this whole protocol depends on. |

### Ambiguous (3)

| File | Unique information | Inbound references | Memory coverage | Consequence of removal | Recommended |
|---|---|---|---|---|---|
| `INTEGRITY_AUDIT_BASELINE_2026-08-20.md` | The one full `audit-integrity` baseline run's output, at a specific point in time. | 0 | None | Loses a specific historical baseline — but baselines age; whether this exact one still has comparative value depends on whether a later baseline has since superseded it in practice (not evidenced either way from the file itself). | **Ambiguous — recommend asking SE/SDT HistFinTS** whether a more recent baseline exists that makes this one purely historical, or whether it's still the reference point in active use. |
| `DRIFT_TOLERANT_SOURCE_FACTS_2026-08-21.md` | A verification methodology for facts measured against a live, moving observation table. | 0 | None | Loses either a one-off investigation's result, or a reusable technique description — the file's own content doesn't make clear which. | **Ambiguous — recommend asking**: if this is a reusable methodology, it likely belongs promoted into `core_reference` (it would matter to future work), not removed; if it was a one-time check, it's a closed-decision candidate instead. The distinction isn't resolvable from the file alone. |
| `INTEGRITY_CAPABILITY_INVENTORY_2026-08-22.md` | A read-only inventory of general integrity capabilities as of 2026-08-22 (itself cites the SDT-1 execution record). | 0 (from others; it cites out to others) | None | Loses a snapshot of "what integrity capabilities existed as of this date" — value depends on whether integrity capabilities have materially changed since, which isn't evidenced from the file alone. | **Ambiguous — recommend asking** whether this inventory is still current (in which case it may belong in `core_reference` as living documentation) or already stale (in which case it's closed-decision, summarize-and-remove). |

---

## 5. What this analysis does not do

- Does not delete, move, collapse, or rewrite any of the 34 artifacts, the two protected docs,
  or the newly-flagged third protected dependency.
- Does not modify `memory/`, `docs/README.md`, `CLAUDE.md`, or `index.yaml`.
- Does not treat the "7 closed-decision + 3 ambiguous" selection above as authoritative
  continuation of a prior audit — it is this pass's own independently-derived classification,
  explicitly flagged as such, pending reconciliation against the original audit if it can be
  located.
- Does not execute any of the "Summarize"/"Retain" recommendations — they are recommendations
  only, per instruction.
