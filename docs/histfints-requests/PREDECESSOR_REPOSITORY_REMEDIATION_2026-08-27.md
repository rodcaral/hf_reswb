# Predecessor-Repository Documentation Remediation — 2026-08-27

**From:** Workbench SDT · **To:** HistFinTS lineage (`histfints.v0`, `histfints.v1`,
`histfints-v2`, `histfints-v3`) and `_shared-standards` · **Date:** 2026-08-27

**Cross-repo anchor:** `histfints-v3` @ `a3dfb47` ("CI: target master and v3, not the
nonexistent main branch"), `histfints.v1`/`master` @ `77cdd26` (same commit), `histfints-v2`
@ `e69e2dc` ("Add bulk-series-import-v1 to the tag glossary") — all as read on 2026-08-27,
**before** this session's edits below, which are local/uncommitted in each repository
pending each project's own commit discipline. `histfints.v0` has no version control.

**Status:** implementation complete, evaluated against the acceptance criterion below.
Follow-up: an [assessment earlier this session](../DECISIONS.md) found `histfints.v2`
undocumented and confusable with current authoritative material (FAIL); the working
assumption at that time was that `histfints.v2` was the only predecessor. Discovery
during this remediation surfaced two more: `histfints.v1` (physical repo + its own
`docs/`) and `histfints.v0` (pre-repository ideation, no Git) — both now covered.

## What was found

- `histfints.v1`, `histfints-v2`, and `histfints-v3` are **not three repositories** —
  they are one Git repository (physical location `histfints.v1`) with two additional
  `git worktree` checkouts on branches `v2` and `v3`. `histfints.v0` is unrelated Git
  history: a sibling folder with no `.git`, holding the pre-repository ideation material
  `v2`'s numbered docs were distilled from.
- `histfints-v3/CLAUDE.md` **already** named all three predecessors with their
  historical/non-authoritative status, reachable as the first file at its repo root —
  this direction (entering from current) was already largely compliant.
- The reverse direction was not: nothing in `histfints.v0`, `histfints.v1`, or
  `histfints-v2` pointed back to `histfints-v3`. `histfints.v1/CLAUDE.md` additionally
  carried a **stale, contradicted claim** — "`master` and `v3` are the same commit" —
  when `histfints-v3/CLAUDE.md` itself already recorded `master` as 103 commits behind.
- `histfints_macro` and `histfints_backups` were checked and excluded: `histfints_macro`
  holds `Status: Proposed` domain-design notes with no Git history and no claim of being
  a past HistFinTS codebase state — not a predecessor repository under §5a's definition.
  `histfints_backups` holds only `.db` backup files, no documentation to mark.
  `histfints_uiue` is a separate, currently-active consumer project per existing
  documentation, not a predecessor.

## Files changed

| Repository | File | Change |
|---|---|---|
| `histfints.v0` | `README.md` (new) | Entry-point marker: superseded/historical, retained for design-process traceability, not authoritative, points to `histfints-v3`. |
| `histfints.v1` | `CLAUDE.md` | Banner at top: `master` is not canonical current source, flags the stale same-commit claim below it, points to `histfints-v3`. |
| `histfints.v1` | `docs/README.md` | Banner at top: this doc set describes `master`, which can lag `v3`; points to `histfints-v3/docs/README.md` as authoritative when diverged. |
| `histfints.v2` | `CLAUDE.md` | Banner at top: superseded/historical, pure ancestor, not authoritative, points to `histfints-v3`. |
| `histfints-v3` | `CLAUDE.md` | Added explicit "only current-authoritative source" statement above the existing (already-good) branch-layout prose; referenced the new `_shared-standards` §5a invariant. |
| `histfints-v3` | `PROJECT_INDEX.yaml` | Extended `branch_layout` to cover `v0` (was missing) and added explicit authoritative/non-authoritative status per entry; added a `predecessor_repositories` block pointing to each marker and to `_shared-standards` §5a. |
| `_shared-standards` | `GENERAL_DOCUMENTATION_DISCIPLINE.md` | New §5a, "Predecessor-repository lineage" — the systematic rule (symmetric entry-point + lineage-reference obligation, standing invariant for newly discovered predecessors, explicitly does not require rewriting historical content). Updated in place per the document's own §6 self-correction rule, with an "Added 2026-08-27" note. `Applies to` header line extended accordingly. |
| `workbench` | this file | Cross-repository status record. |

No design-document content (`docs/01`–`docs/37` in `histfints-v2`, the ideation drafts in
`histfints.v0`, or `histfints.v1`'s existing `ARCHITECTURE.md`/`DOMAIN_MODEL.md`/etc.) was
modified, deleted, or rewritten. Every change is an additive banner or index entry.

## Mechanism

Symmetric, per `_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` §5a:

1. **Predecessor → current:** an unambiguous marker at the predecessor's first
   documentation entry point, stating superseded/historical status, retention rationale
   (methodology/implementation/provider-assumption/decision traceability), explicit
   non-authoritative status, and naming `histfints-v3` by name and path.
2. **Current → predecessors:** a lineage reference reachable from `histfints-v3`'s own
   entry point (`CLAUDE.md`, and now `PROJECT_INDEX.yaml`) enumerating every known
   predecessor and its status.
3. **Standing invariant:** any predecessor discovered later — of any project covered by
   the shared standard, not only HistFinTS — must receive both markers before that
   discovery is considered closed; this is now written into the shared standard itself,
   not left as a one-time cleanup specific to this increment.

## Acceptance criterion — PASS/FAIL evidence, both directions

**Criterion:** a reader or agent entering either `histfints-v3` or any predecessor
repository must be able to determine unambiguously which repository is current and
which material is historical evidence only.

| Entry point | Result | Evidence |
|---|---|---|
| `histfints-v3/CLAUDE.md` (root, first file) | **PASS** | Opens (after this change) with an explicit "only current-authoritative source" statement, names all three predecessors, states their non-authoritative status, and cites `_shared-standards` §5a for the standing rule. |
| `histfints-v3/PROJECT_INDEX.yaml` | **PASS** | `branch_layout` and `predecessor_repositories` blocks state authoritative/non-authoritative status per entry, including `v0`, machine-readably. |
| `histfints.v0/README.md` (new; previously no entry point existed) | **PASS** | First line states superseded/historical and not authoritative; names `histfints-v3` by path. |
| `histfints.v1/CLAUDE.md` (root, first file) | **PASS** | Banner above the existing content states `master` is not canonical, flags the stale same-commit claim for re-verification, points to `histfints-v3`. |
| `histfints.v1/docs/README.md` (documentation reading-order entry) | **PASS** | Banner states the doc set describes `master`, which can lag `v3`, and names `histfints-v3/docs/README.md` as authoritative on divergence. |
| `histfints-v2/CLAUDE.md` (root, first file) | **PASS** | Banner states superseded/historical, pure-ancestor, not authoritative, points to `histfints-v3`. |

Before this remediation, only the `histfints-v3` entry points passed; all four
predecessor entry points failed (three had no marker at all, and `histfints.v1/CLAUDE.md`
additionally asserted a claim `histfints-v3`'s own documentation contradicted).
