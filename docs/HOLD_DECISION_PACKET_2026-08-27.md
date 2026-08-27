# HOLD Decision Packet — 13 Remaining Files, Documentation Migration

**Date:** 2026-08-27
**From:** SDT Workbench
**Status: read-only. No HOLD file moved, edited, or reclassified in producing this packet.**
Technical facts below were verified directly against `DECISIONS.md` and the files themselves,
not assumed — findings are marked with their source. This packet does not decide any
financial-domain or product/scope question; it routes each to where that decision belongs.

Migration status: all 62 non-HOLD, high-confidence files are migrated (see
`DOCUMENTATION_MIGRATION_PLAN_2026-08-27.md` and `EVIDENCE_LOG.md`). These 13 are everything
left at `docs/` root beyond the 6 current/core documents.

---

## Dependency map (read this first)

```
Decision A (Tranche 2 status)  ──upstream of──▶  Decision B (panel-eligibility completeness)
Decision C (D1-D5 completeness) ── independent ── Decision D (F-009 filing status)
                                                          │
                                                          ▼
                                              Decision E (F-009 package location, technical)
Decision Z (proposal supersession) ── independent, near-mechanical
```

Only **A→B** is a true dependency: B cannot be answered without knowing A. Everything else is
independent and can be decided in any order, in parallel, by whoever owns that call.

---

## Cluster 1 — Tranche 2 status (2 files) — Decision A

### `TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md`
- **Why HOLD:** titled as a live status tracker for a workstream `CLAUDE.md`'s handoff section
  still calls "not yet confirmed landed."
- **Unresolved question:** is this status still current, or has it been superseded by later
  findings?
- **Verified finding (technical, not a judgment call):** `DECISIONS.md`'s own later entries
  (**D-044**, 2026-08-17: *"Both Tranche 2 gates cleared... Workbench panel-eligibility
  implementation may proceed"*) and this very document's own headline (*"both filings have
  substantially landed"*, `PRAGMA user_version` 10→14) already establish Tranche 2 as landed.
  This document **is** the validation record D-044 asked for, not an open tracker.
- **Decision type:** Technical (verifiable against the repo's own ledger) — **not**
  financial-domain, **not** product/scope.
- **Dependent capability:** none blocks on this file directly; it is evidence *for* the
  now-settled Tranche 2 question.
- **Dispositions:**
  - Stay current: incorrect — nothing currently treats it as a live tracker; `DECISIONS.md`'s
    D-044/D-019 entries are now the authoritative record.
  - **Move to `docs/evidence/` (closed historical):** consistent with what it actually is — a
    completed status check, superseded as a *tracker* by `DECISIONS.md` itself.
  - Collapse into memory: no — this is repository-committed fact, not session-relationship
    guidance; belongs in documentation per the shared standard's Git/docs/memory boundary.
- **Recommended routing:** **SE confirms** (this is a "does the evidence say what I read it as
  saying" check, not a scope call) → move to `docs/evidence/`.

### `VALIDATION-TRANCHE2-PRE-IMPLEMENTATION.md`
- **Why HOLD:** its own header states `**Gate:** Panel-eligibility implementation blocked until
  these validations pass` — read in isolation, this looks like an active blocker.
- **Unresolved question:** has the checklist this file specifies actually been run and closed?
- **Verified finding:** yes. `D-044` (2026-08-17) is the same decision that authorized this
  checklist (*"Next step for Workbench: Validate the availability data... Confirmation queries
  should be run"*), and `TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md` (2 days later) is that
  validation, run and reported. This file's "Gate" line is stale, not currently binding — it
  describes a gate that has already been passed.
- **Decision type:** Technical.
- **Dependent capability:** `SPEC-panel-eligibility.md` implementation — but only *historically*
  gated on this; the gate is already cleared per the above.
- **Dispositions:**
  - Stay current: **risk** — a reader taking the "Gate: blocked" line at face value today would
    wrongly conclude panel-eligibility work is still blocked.
  - **Move to `docs/evidence/` (closed historical), with a one-line "gate cleared, see D-044 /
    TRANCHE2_AND_MIGRATIONS_STATUS_2026-08-19.md" note** — an additive marker, not a rewrite of
    the checklist's substance.
  - Collapse into memory: no, same reasoning as above.
- **Recommended routing:** **SE confirms**, same batch as the file above — add the one-line
  status note (additive, not substantive rewrite, consistent with the migration's established
  practice), then move.

---

## Cluster 2 — Panel-eligibility roadmap (1 file) — Decision B, downstream of A

### `IMPLEMENTATION-PANEL-ELIGIBILITY.md`
- **Why HOLD:** described in its own commit message as a "roadmap"; `CLAUDE.md`'s status
  section says panel-eligibility is "ready to implement for non-gated parts" — could be the
  live roadmap for still-unfinished work.
- **Unresolved question:** is the roadmap's Phase 1+ work complete, partially complete, or
  still the active plan? This requires reading implementation status against
  `src/hf_reswb/application/panel_eligibility_service.py`'s actual current state — a **product/
  scope judgment** (what counts as "done" for this feature), not something this packet decides.
- **Now that Decision A is resolved:** the roadmap's own stated gate (`**Gate:** Upstream
  validation complete (D-045)`) is cleared, same as Cluster 1 — so the roadmap is no longer
  blocked from starting, but that does not by itself tell us whether it has *finished*.
- **Decision type:** Product/scope.
- **Dependent capability:** `SPEC-panel-eligibility.md` (current, stays put regardless) and the
  live `panel_eligibility_service.py`/`calibration_analyzer.py`/`panel_integration.py`/
  `suitability_service.py` implementation.
- **Dispositions:**
  - **Stay current** (if the roadmap still has open phases): correct disposition — this would
    make it load-bearing, not evidence.
  - **Move to `docs/evidence/`** (if all phases are complete and it's now a historical plan):
    correct if implementation is finished.
  - HOLD, further split by phase: a plausible fallback if some phases are done and others
    aren't — decide per-phase rather than per-file.
- **Recommended routing:** **SE/PO** — needs a phase-by-phase completion check against the
  actual `src/` implementation, which is a product/scope call about what "done" means for this
  feature, not a technical status lookup like Cluster 1.

---

## Cluster 3 — Acquisition-quality D1–D5 (3 files) — Decision C, independent

### `ACQUISITION_QUALITY_CAPABILITY_DESIGN_D1_D5_2026-08-22.md`
### `D3_D4_APPROVED_DESIGN_INCREMENT_2026-08-22.md`
### `ACQUISITION_QUALITY_D1_D4_STATUS_ASSESSMENT_2026-08-26.md`

- **Why HOLD (all three, one shared question):** the most recent of the three (Aug 26) is the
  most recently modified file in the entire original 81-file inventory, and its own verified
  finding is: *"all four DFA-approved capabilities are fully implemented as pure, DB-free
  evidence classifiers with complete test coverage (45/45 passing) and zero production
  callers... What remains for each is not classifier work but (a) wiring real callers against
  live `histfints-v3` data... and (b) upstream evidence only HistFinTS can supply (D4)."*
- **Unresolved question:** is "classifier implemented, zero production callers, integration
  pending" **DONE** (design phase closed, integration tracked as separate future work) or
  **STILL OPEN** (the capability isn't real until it's wired to a live caller)? This is a
  genuine product/scope definition-of-done question, not something derivable from the code.
- **Decision type:** Product/scope.
- **Dependent capability:** `src/hf_reswb/application/acquisition_quality_capability.py` — real,
  tested, live in the codebase regardless of this decision; the question is purely about the
  three *documents'* status, not the code's.
- **Note on D4 specifically:** D4's "evidence gate still unavailable" column names *"Tranche 2,
  unconfirmed landed"* — per Decision A above, Tranche 2 **is** now confirmed landed, so D4's
  own noted blocker may already be partially resolved. This does not resolve the broader
  done/open question but should be folded into whoever answers Decision C.
- **Dispositions:**
  - **Stay current** (if "implemented, not wired" = still open): correct — these describe an
    active punch list.
  - **Move to `docs/evidence/`** (if "implemented, not wired" = design-closed): correct if the
    integration work is being tracked elsewhere (a ticket, a future spec) rather than in these
    documents.
  - Split disposition (design docs move, status assessment stays as the current punch-list
    tracker): plausible middle ground — the two Aug-22 design docs could close while the Aug-26
    status assessment remains the living tracker until integration lands.
- **Recommended routing:** **SE/PO** — a single "what does done mean for D1-D5" call resolves
  all three at once.

---

## Cluster 4 — F-009 defect and its filing package (6 files) — Decisions D and E

### `DEFECT-F009.md`
- **Why HOLD:** structural mismatch (Rule E) — `CLAUDE.md`'s "Where things are" table already
  claims this file is at `docs/histfints-requests/DEFECT-F009.md`; it is actually at `docs/
  DEFECT-F009.md`.
- **Verified finding:** the file's own status line reads **"dormant, not yet observed in
  production"** — this is a real, still-open defect filing, not closed history. Cross-checked
  against `DECISIONS.md` D-032: *"F-009 remediation halted in HistFinTS; focus moved to proving
  Workbench evidence consumption"* — the underlying defect was never fixed, work pivoted to a
  different mitigation (the F009-evidence-consumption spec, which is `SPEC-f009-evidence-
  consumption.md`, current, staying put).
- **Unresolved question (product/relationship, not technical):** given remediation was halted
  and Workbench built an evidence-consumption workaround instead, is this filing still an
  **active ask** to HistFinTS, or should it be marked **withdrawn/superseded** by the
  evidence-consumption approach? This determines whether it belongs in `docs/histfints-
  requests/` (still-pending filing) or `docs/evidence/` (closed, superseded by a different
  mitigation).
- **Decision type:** Product/scope — specifically, ownership of the Workbench↔HistFinTS
  filing relationship. **Not decided here.**
- **Dependent capability:** none Workbench-side; this is purely about the filing's own status.
- **Dispositions:**
  - Stay current: no — it was never in the current-reference set to begin with.
  - **Move to `docs/histfints-requests/`** (matching `CLAUDE.md`'s existing claim, if the
    filing is still active): correct if PO wants to keep pressing this ask.
  - **Move to `docs/evidence/`** (closed historical, if superseded by the evidence-consumption
    approach): correct if PO considers the workaround sufficient and the original ask moot.
  - Fix `CLAUDE.md` instead of moving the file (if the file should just stay at `docs/` root):
    least likely correct answer, since `docs/` root is being actively cleared of everything
    except current/core material by this migration, but included for completeness.
- **Recommended routing:** **PO** — this is a call about the Workbench↔HistFinTS relationship,
  not a technical or documentation-structure question.

### `REQUEST-tranche2-migration.md`
- **Why HOLD:** same structural mismatch as `DEFECT-F009.md` (`CLAUDE.md` claims `docs/
  histfints-requests/`, file is at `docs/` root).
- **Verified finding:** **this one is landed** — per D-044/D-019 (Cluster 1), the adjustment-
  basis ask this file makes was deployed and confirmed. Unlike `DEFECT-F009.md`, there is no
  live product/relationship question here — only the mechanical location question.
- **Decision type:** Technical/structural only.
- **Dispositions:** **move to `docs/evidence/`** (closed, landed) — the cleanest of the six
  F-009-adjacent files, no PO input needed.
- **Recommended routing:** **SE** — confirm and move; does not need to wait for Decision D.

### `CONSULTANT-PACKAGE-F009.md`, `CONSULTANT-README-F009.txt`, `PACKAGE-MANIFEST-F009.txt`, `test_import_service_defect_f009.py`
- **Why HOLD:** bundled companions to `DEFECT-F009.md` — a consultant-facing package (readme,
  manifest, and a captured reproduction script, confirmed **not** collected by pytest since
  `testpaths = ["tests"]` excludes `docs/`).
- **Unresolved question:** same as `DEFECT-F009.md` — their correct destination follows
  whichever way Decision D resolves, since they only exist to support that filing.
- **Decision type:** Product/scope (inherited from Decision D) for *whether* they move with
  `DEFECT-F009.md`; technical/mechanical for *where exactly* once D is answered.
- **Dependent capability:** none.
- **Dispositions:** identical set to `DEFECT-F009.md` — move together as one bundle, never
  split across `docs/evidence/` and `docs/histfints-requests/`.
- **Recommended routing:** **PO** (via Decision D) — no separate decision needed; these four
  ride on whatever Decision D concludes.

---

## Standalone — near-mechanical, ready now

### `PROPOSAL-docs-reorganization.md`
- **Why HOLD:** self-referential — it is the predecessor proposal to the migration this packet
  is closing out; moving it while the migration was in flight would have been premature.
- **Unresolved question:** none substantive remains — the migration it proposed is now
  complete (62/62 high-confidence files moved). The only open item is procedural: has the
  migration been formally accepted as its resolution?
- **Decision type:** Documentation-process, not financial/product — essentially the same
  mechanical step already applied to `GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md` in
  batch 1 (one-line supersession pointer, then move).
- **Dependent capability:** none.
- **Dispositions:** **add a supersession pointer** ("superseded by `DOCUMENTATION_MIGRATION_
  PLAN_2026-08-27.md`, executed 2026-08-27") **then move to `docs/evidence/`** — the same
  treatment already precedented in this migration, requiring no new judgment.
- **Recommended routing:** **SE** — can be executed on the same nod that approves closing out
  the migration; does not need PO or DFA.

---

## Smallest set of concrete decisions needed

| # | Decision | Owner | Type | Files resolved | Depends on |
|---|---|---|---|---|---|
| Z | Accept migration as `PROPOSAL-docs-reorganization.md`'s resolution | SE | Mechanical | 1 | none |
| A | Confirm Tranche 2 status docs are closed (technical finding already verified above) | SE | Technical | 2 | none |
| B | Is panel-eligibility implementation complete? | SE/PO | Product/scope | 1 | **A** |
| C | Does "implemented, zero production callers" count as done for D1–D5? | SE/PO | Product/scope | 3 | none |
| D | Is the F-009 filing still active, or superseded by the evidence-consumption workaround? | PO | Product/relationship | 5 (`DEFECT-F009.md` + 4 companions) | none |
| — | `REQUEST-tranche2-migration.md` — landed, move now | SE | Technical | 1 | none (no PO wait needed) |

**Five decisions, one of them (A) already technically resolved and only needing SE sign-off,
one (Z) purely mechanical, and one file (`REQUEST-tranche2-migration.md`) requiring no decision
at all beyond SE confirming and moving it.** The only decision genuinely gated on another is B
on A. Nothing here requires DFA — no financial-domain interpretation question surfaced among
the 13; the two live product/scope calls (B, C) and the one relationship call (D) belong to
SE/PO.
