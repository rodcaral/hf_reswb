# histfints-v3 — Documentation-Lifecycle Skill Applied, Read-Only

**Date:** 2026-08-27 · **From:** SDT Workbench, applying the `documentation-lifecycle` project
skill · **Status: read-only. No file in `histfints-v3` moved, renamed, deleted, or rewritten to
produce this assessment.**

**Cross-repo anchor:** `histfints-v3`, state as read on 2026-08-27 — no commit hash captured
(uncommitted local edits from this session's earlier predecessor-lineage work were present at
read time; re-verify before trusting counts if the repo has changed since).

---

## §1 — Repository-status confirmation

**Already explicit, not inferred.** `histfints-v3/CLAUDE.md`:7 states *"This project's only
current-authoritative source is the `v3` branch, worked in this `histfints-v3` worktree"*, and
names `histfints.v0`/`histfints.v1`/`histfints-v2` as its own predecessors (marked, per the
earlier remediation this session). Workbench's own `CLAUDE.md` and `DECISIONS.md` likewise
treat `histfints-v3` as canonical throughout. No sibling-repository investigation was needed for
this pass — per the skill's revised §1, authority was already established, so this step moved
straight to §2.

---

## §2 — Inventory and §11 — count checksum

**74 files at `docs/` root** (69 `.md`/`.txt` + a handful of scripts/data — see below).
Every bucket below is required to sum back to 74; verified at the end of this section.

The repository **already has a working evidence-register system** — `docs/EVIDENCE_LOG.md` (a
populated, cross-team-reconciled index, itself dated 2026-08-26) and `docs/README.md`'s 7-item
reading order, both referenced from `PROJECT_INDEX.yaml`. Unlike Workbench, files here are
**indexed in place, not physically moved** — `EVIDENCE_LOG.md`:7 states this explicitly
("Nothing here is deleted, moved, or rewritten by being indexed; this is a pointer list only").
**This convention is followed below, not Workbench's `docs/evidence/` physical-move pattern —
per the skill's own §4, the existing convention governs.**

| Bucket | Count | Source |
|---|---|---|
| Current / core (README's 7-item reading order + `README.md` + `EVIDENCE_LOG.md` + 4 files `EVIDENCE_LOG.md` itself marks CR-but-unlisted) | **13** | Already explicit |
| Evidence — durable/audit (already in `EVIDENCE_LOG.md`) | **22** | Already explicit |
| Evidence — reusable methodology (already in `EVIDENCE_LOG.md`) | **6** | Already explicit |
| Evidence — closed historical (already in `EVIDENCE_LOG.md`) | **3** | Already explicit |
| Newly identified, unindexed `.md`/`.txt` at root | **6** | This pass |
| Non-`.md` scripts/data at root, entirely unindexed by `EVIDENCE_LOG.md` | **24** | This pass |
| **Total** | **74** | 13+22+6+3+6+24 = 74 ✓ |

---

## §3 — Classification

### Current / core (13) — unchanged, no action

`ARCHITECTURE.md`, `DOMAIN_MODEL.md`, `DATABASE_SCHEMA.md`, `APPLICATION_SERVICES.md`,
`PROVIDERS_AND_ADAPTERS.md`, `PRESENTATION.md`, `KNOWN_LIMITATIONS.md` (README's reading
order), `README.md`, `EVIDENCE_LOG.md`, plus 4 files `EVIDENCE_LOG.md` itself already marks
current-reference-but-outside-the-numbered-list: `BYMA_EVIDENCE_COLLECTION_SCHEDULE.md`,
`OPEN_ISSUE_evidence_path_uncontrolled_writes.md`, `PROVENANCE_INTEGRITY_import_run_id_
mutability.md`, `PROVENANCE_SEMANTIC_CONTRACT_2026-08-20.md`.

### Evidence (31 already indexed — accepted as-is, one flagged for reconsideration)

The existing 22 durable-evidence + 6 reusable-methodology + 3 closed-historical entries in
`EVIDENCE_LOG.md` were spot-checked, not re-litigated wholesale — this repo's own two-team
(Workbench + HistFinTS SDT) reconciliation already exists and is more authoritative than a
fresh read of filenames.

**One entry worth flagging under the skill's classification-≠-closure rule, not overriding:**
`CAPABILITY_A_D_IMPLEMENTATION_ASSESSMENT_2026-08-26.md` is indexed as durable evidence, but its
own summary line reads *"no capability implemented; next transition is UI/UE specification"* —
this is the same shape as Workbench's own D1–D5 HOLD (assessed-but-not-integrated work). Two
teams already agreed on the DE classification, so this is **not** overridden here — it is named
as a candidate for revisiting if the UI/UE transition it names hasn't happened, not reclassified
unilaterally.

### Newly identified, unindexed (6 `.md`/`.txt`) — 4 Evidence, 1 Reusable-methodology, 1 HOLD

| File | Read | Classification | Rationale |
|---|---|---|---|
| `ACCESSIBILITY_GATE_STATUS_2026-08-25.md` | Full header read | Evidence (DE) | "All 7 required AT checks now PASS" — completed, dated record |
| `AT_VALIDATION_ATTEMPT_INCIDENT_SUMMARY_2026-08-25.md` | Full header read | Evidence (DE) | Explicit "Handoff record" for a closed incident |
| `AT_VALIDATION_PROCEDURE.md` | Full header read | Evidence (RM — reusable methodology) | Self-declared "distilled, reusable procedure... so the next validation pass doesn't have to rediscover" |
| `SCREEN_READER_VALIDATION_SCRIPT_2026-08-25.md` | Full header read | Evidence (DE) | Own title says "Not Evidence" but an addendum confirms checks 1–2 were later run for real against NVDA — the *updated* file is a dated evidence record for that specific session |
| `INTEGRITY_AUDIT_RAW_EVIDENCE_2026-08-20.txt` | Content sampled | Evidence (DE) | Raw data pairing with the already-indexed `INTEGRITY_AUDIT_BASELINE_2026-08-20.md` |
| `ENV_TEMP_REVERT_2026-08-20.txt` | Full content read (3 lines) | **HOLD** | No header, no narrative context, no identifiable owner or linked investigation — a bare `TMPDIR`/`TEMP`/`TMP` value dump. Cannot classify confidently without asking whoever produced it what it supports. |

### Active requests — none found at `docs/` root

Unlike Workbench (which files outbound asks *to* HistFinTS), this repository is the recipient
side of that relationship — no outbound-filing pattern exists here to classify.

### Memory candidates — none found

Nothing at `docs/` root reads as agent-behavior-only guidance rather than a fact about the
repository itself.

### Rule-D / source-coupled (2, both already Evidence-classified)

| File | Cited from |
|---|---|
| `F033_CORRELATION_DISCREPANCY_DIAGNOSIS_2026-08-19.md` (DE) | `src/histfints/domain/integrity_finding.py`, `src/histfints/domain/repositories.py` |
| `INTEGRITY_CAPABILITY_INVENTORY_2026-08-22.md` (RM) | `src/histfints/application/identity_evidence_evaluator.py` |

Since this repository's convention is index-in-place rather than physical move, this coupling
is currently benign — flagged for completeness and in case a future physical reorganization is
ever considered, not because anything needs to change now.

### 24 non-`.md` scripts/data — unindexed by `EVIDENCE_LOG.md` entirely (a real gap)

`EVIDENCE_LOG.md` only indexes `.md` documents; these 24 `.py`/`.json`/`.txt` files at `docs/`
root have **no register entry of any kind**. Name/topic pairing (provisional — not confirmed by
reading every file's content) suggests:

- **~22 pair with an already-indexed Evidence doc** (e.g. `byma_evidence_raw.json` +
  `byma_independence_*.py` + `collect_byma_evidence.py` → `BYMA_EVIDENCE_PACKAGE_2026-08-19.md`;
  `verify_0015_activation.py` + `post_activation_verification_*.txt` →
  `H_0015_ACTIVATION_RECORD_2026-08-20.md`; similar pairing for the `classc_*`, `sdt1_*`,
  `F033`-adjacent, and `remediation_*` scripts). Provisional Evidence classification, inherited
  from their paired document.
- **1 pairs with a *current*, not evidence, document**: `check_evidence_path_uncontrolled_
  writes.py` supports `OPEN_ISSUE_evidence_path_uncontrolled_writes.md` (current/core, an open
  issue) — likely still a live diagnostic tool, not closed evidence.
- **1 is HOLD by ambiguity**: `reconcile_with_workbench.py` — no dated pairing found; could be
  a one-off artifact from a past reconciliation or a still-used live utility. Not classified
  without asking whoever last ran it.

**This is the clearest discoverability defect found**: 24 files with zero indexing of any kind,
discoverable only by guessing at name pairing — exactly the gap `EVIDENCE_LOG.md`'s own scope
statement ("Durable evidence/audit records... under `docs/`") should logically cover but
currently doesn't extend to non-`.md` artifacts.

---

## Existing indexes/registers (already in place, not proposed)

- `docs/README.md` — 7-item current-state reading order, all links verified to resolve.
- `docs/EVIDENCE_LOG.md` — populated, cross-team-reconciled evidence register (31 entries).
- `PROJECT_INDEX.yaml` — machine-readable structural map, already references `EVIDENCE_LOG.md`.
- `docs/archive/{completed_features,planning}/` — physical archive folders (1 entry each,
  out of scope for this pass per the skill's own "already differentiated" guidance).
- `docs/{Wb_UI-UE,help_docs,proposed,future_designs,at_validation_evidence,byma_evidence_
  sessions,class_d_execution_evidence,classc_refetch_evidence,sdt1_execution_evidence,
  remediation_baseline_20260820T055140Z}/` — already-separated subdirectories, spot-checked
  and confirmed coherent (raw evidence bundles, UI/UE liaison artifacts, one still-`proposed`
  migration's SQL/diff/script bundle, one `future_designs` doc) — not clutter, out of scope.

## Authority/discoverability defects found

1. **The 24-file non-`.md` indexing gap** (above) — the most concrete finding.
2. **`CAPABILITY_A_D_IMPLEMENTATION_ASSESSMENT_2026-08-26.md`** flagged for reconsideration,
   not asserted as wrong (see §3).
3. **No broken links** in `README.md`; no stale `CLAUDE.md`/`PROJECT_INDEX.yaml` claims found
   during this pass (contrast with Workbench, where such defects were found and are now fixed).

## HOLDs — exact unresolved questions

| File | Type | Question |
|---|---|---|
| `ENV_TEMP_REVERT_2026-08-20.txt` | Technical/unknown-provenance | What investigation or fix does this file support? No header, no citation elsewhere found. |
| `reconcile_with_workbench.py` | Technical/unknown-status | Is this a one-off artifact from a completed reconciliation, or a still-used live cross-repo tool? |
| `CAPABILITY_A_D_IMPLEMENTATION_ASSESSMENT_2026-08-26.md` | Product/scope | Has the "next transition... UI/UE specification" it names happened? If not, should this remain a live tracker rather than indexed evidence? |

No financial-domain, governance, or cross-project-relationship question was found requiring
escalation in this pass — all three HOLDs above are resolvable by asking whoever has direct
knowledge (an SE/SDT-HistFinTS technical check for the first two, a product/scope call for the
third), not a domain-specialist or PO ruling.

---

## Proposed target layout

**No structural change proposed.** The existing `README.md` + `EVIDENCE_LOG.md` +
`archive/{completed_features,planning}/` + `PROJECT_INDEX.yaml` structure already implements
this skill's §3/§4 intent well, and — per the skill's explicit instruction not to impose
Workbench's paths — is not being replaced with a physical `docs/evidence/` folder. The only
proposed changes are additive:

1. Extend `EVIDENCE_LOG.md` to include the 4 newly-identified Evidence `.md` files and
   `INTEGRITY_AUDIT_RAW_EVIDENCE_2026-08-20.txt`.
2. Add a short new subsection to `EVIDENCE_LOG.md` (or a sibling file, if the register's own
   scope should stay `.md`-only) covering non-`.md` supporting artifacts, closing the 24-file
   gap.
3. Resolve the 3 named HOLDs before indexing `ENV_TEMP_REVERT_2026-08-20.txt` and
   `reconcile_with_workbench.py` one way or the other.

---

## GO / GO WITH HOLDS / NO-GO

**GO WITH HOLDS.**

The high-confidence set (5 newly-identified `.md`/`.txt` files, plus provisional pairing for
~22 of the 24 scripts) is small, low-risk, and additive-only — no physical move is even being
proposed, only index entries. The **smallest safe first batch**: add `ACCESSIBILITY_GATE_
STATUS_2026-08-25.md`, `AT_VALIDATION_ATTEMPT_INCIDENT_SUMMARY_2026-08-25.md`, `AT_VALIDATION_
PROCEDURE.md`, `SCREEN_READER_VALIDATION_SCRIPT_2026-08-25.md`, and `INTEGRITY_AUDIT_RAW_
EVIDENCE_2026-08-20.txt` as new `EVIDENCE_LOG.md` entries — zero HOLD content, zero physical
moves, and the closest available proof-of-concept to how Workbench validated its own first
batch. Not GO unqualified: 3 named HOLDs (one product/scope, two provenance-unknown) remain,
and the 24-script pairing is provisional/inferred, not confirmed by reading each file.
