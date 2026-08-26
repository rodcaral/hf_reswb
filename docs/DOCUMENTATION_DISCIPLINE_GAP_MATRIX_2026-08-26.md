# Workbench vs. Approved General Documentation Discipline — Gap/Action Matrix

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: read-only assessment only. No file modified. State verified directly (72 top-level
`docs/*.md`, `DECISIONS.md` at 3,832 lines, no `README.md`/`index.yaml`/`EVIDENCE_LOG.md`/
`archive/` present) — not reused from the prior assessment's snapshot.**

Standard referenced: the minimum-viable discipline and activation heuristics proposed in
`DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md` §4–6 (no separately-named document titled
"General Documentation Discipline" exists in any repo checked — treating that assessment's
proposal as the approved content).

| Area | Current state | Gap | Action | Priority |
|---|---|---|---|---|
| **Entry point** | No `README.md` or index in `docs/`; only `CLAUDE.md`'s hand-maintained "Where things are" table (~8 files named) | 72 files in `docs/`, ~64 of them named nowhere — a newcomer (human or agent) has no reading-order beyond what's already in `CLAUDE.md` | Add one short reading-order pointer per the minimum-viable standard (3–7 items, current-state focus) — either as `docs/README.md` or an expansion of `CLAUDE.md`'s existing table. No index.yaml. | **High** — this is the one gap with no informal substitute already covering it |
| **Large `DECISIONS.md`** | 3,832 lines, single append-only reverse-chronological ledger, growing every session | Not yet at a size where `grep`/date-range recall meaningfully fails, but it is the file this session relies on most for cross-session continuity, and it has no internal index of its own (no section anchors, no D-###/F-###/A-### tag list) | No structural change yet — splitting or classifying entries risks breaking the exact append-only, single-source-of-truth property that makes it work as a memoryless-session continuity mechanism. Lowest-cost mitigation: a periodic tag/topic index appended at the top (not a new file, not a new class system) if and when recall actually starts failing. | **Low** — named as a watch item, not a current failure |
| **Cross-repository evidence anchoring** | No marker exists anywhere distinguishing a doc whose evidence is self-contained from one anchored to a sibling repo's (`histfints-v3`) independently-drifting state | Every `docs/histfints-requests/*.md` deliverable this session cites specific line numbers/behavior in the other repo; nothing flags "re-verify this against current `histfints-v3` state before trusting" | Adopt one lightweight convention going forward: a one-line "Anchored to `histfints-v3` @ [date/commit-equivalent]" note at the top of any doc making cross-repo claims. Not a new index, not a schema — a per-file annotation. | **Medium** — a real, demonstrated failure mode this session hit repeatedly, but cheaply mitigated |
| **Avoiding unnecessary HistFinTS-style machinery** | Confirmed directly: no `index.yaml`, no `EVIDENCE_LOG.md`, no `archive/` subfolder, no git-tag history extraction anywhere in this repo | None — this is a compliance check, not a gap | No action. Continue declining to adopt these until Workbench's own shape (multiple entry points, archive-dominated directory, a strictly sequential doc history) actually produces the need, per the activation heuristics already on record. | **N/A — passing** |

---

## Summary

One real, actionable gap (entry point), one demonstrated-but-cheaply-fixed risk (cross-repo
anchoring), one watch item with no action warranted yet (`DECISIONS.md` size), and one clean
pass (no unnecessary machinery adopted). No file modified in producing this matrix.
