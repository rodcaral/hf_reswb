# Read-Only Index Migration Check — `PROJECT_INDEX.yaml` Standardization

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE / SDT HistFinTS / UI-UE
**Status: read-only check only. No file renamed or modified anywhere.**

---

## 1. Current machine-readable index, per project — verified directly

| Project | File | Exists? |
|---|---|---|
| `histfints-v3` | `index.yaml` (repo root) | Yes |
| `histfints_uiue` | `PROJECT_INDEX.yaml` (repo root) | Yes — **already at the target canonical name** |
| `workbench` | *(none)* | No machine-readable index of any kind exists |

## 2. Inbound references / consumers

**`histfints-v3/index.yaml`**:
- **No consumer found anywhere** — grep across `src/`, `tests/`, `tools/`, `.claude/`, and
  `docs/README.md` finds zero live references. The one hit in `.claude/settings.local.json` is
  a permission-allowlist record of a one-off `python3 -c "import yaml..."` validation command,
  not a reusable consumer.
- `docs/README.md` does not list or link it — it is not part of the documented reading order.
- **Cross-project**: it references `histfints_uiue/PROJECT_INDEX.yaml` by absolute path (its own
  `related_projects.workbench_ui_ue.index` field) — an outbound reference, not inbound.
- **From `workbench`**: four dated docs written this session (`DOCS_RETENTION_BASELINE_2026-
  08-25.md`, `DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md`,
  `DOCUMENTATION_DISCIPLINE_GAP_MATRIX_2026-08-26.md`, and this session's own `DECISIONS.md`
  entries) mention `index.yaml` by name — all descriptive/historical (reporting what it *is
  called as of that date*), not live pointers or code that would break on rename.

**`histfints_uiue/PROJECT_INDEX.yaml`**:
- Actively consumed as a living workstream/gate tracker — cross-referenced from within itself
  extensively (workstream ids `001`-`029`), and it is the one file `histfints-v3/index.yaml`
  itself points to for UI/UE's own status.
- Only inbound cross-project reference found: `histfints-v3/index.yaml`'s own outbound pointer
  to it (noted above — same relationship, opposite direction).

## 3. Can `histfints-v3/index.yaml` safely become the canonical `PROJECT_INDEX.yaml`? — Mechanically yes; substantively, not without a schema reconciliation first

**Mechanically**: yes. Zero live consumers found anywhere; a rename would break nothing that
currently reads the file programmatically or links to it by name.

**Substantively — the reason not to standardize as literally proposed**: the two files that
would end up sharing the name `PROJECT_INDEX.yaml` across the ecosystem are **not the same kind
of document**. Read in full for this check, not assumed from memory:

- `histfints-v3/index.yaml` is a **static structural/architecture map**: entry points, layer
  ordering, database location, doc categories, tooling, testing conventions, provider adapter
  list. It describes what the *codebase* is shaped like, and changes rarely (only when the
  architecture itself changes).
- `histfints_uiue/PROJECT_INDEX.yaml` is a **living project-status/gate-tracking ledger**:
  authority-by-role, per-workstream document lists with status/dependency fields, blocking vs.
  non-blocking open items, closed-defect log, validation rules, next-step workflow. It describes
  *where the work currently stands*, and is updated with essentially every workstream event.

Renaming `histfints-v3/index.yaml` to `PROJECT_INDEX.yaml` without reconciling this would put
two files with the identical canonical name doing structurally different jobs in two sibling
repositories — undermining the actual point of calling a name "canonical" (that it implies a
shared shape/purpose, not just a filename coincidence). A reader or tool that learns "check
`PROJECT_INDEX.yaml` for project status" from `histfints_uiue`'s example would find something
entirely different in kind at that path in `histfints-v3`.

**This is not a reason to never standardize — it's a reason not to do it as a bare rename.**
The generalization needs one of:
1. A single agreed schema for what `PROJECT_INDEX.yaml` means everywhere (and `histfints-v3`'s
   file restructured to fit it, not merely renamed), or
2. An explicit acknowledgment that `PROJECT_INDEX.yaml` is a *role name* that different projects
   fill with different schemas suited to their own nature (a structural map here, a workstream
   tracker there) — in which case the rename is fine as a label, but the generalization's
   promise of "canonical" should be understood as "canonical *location*," not "canonical
   *contents*."

Either resolution is a real decision for SE/PO, not something this read-only check can settle.

## 4. Required rename/reference updates, if the rename proceeds under either resolution above

- `histfints-v3/index.yaml` → `histfints-v3/PROJECT_INDEX.yaml`: **no external reference needs
  updating** — confirmed zero live consumers (§2). The only file that would need an edit is the
  renamed file's own self-description if it currently says "index.yaml" anywhere in its own
  prose (checked: it does not — it never names itself internally).
- The four `workbench` docs listing `index.yaml` by name: **do not need retrofitting** — they
  are dated, historical descriptions of what the file was called as of their own write date,
  consistent with this project's established "don't retrofit dated docs" convention.
- `histfints_uiue/PROJECT_INDEX.yaml`: **no change needed** — already at the target name.

## 5. Workbench's own position — restated, not newly decided here

`workbench` has no machine-readable index today, and per the 2026-08-26 documentation-
discipline assessment/gap-matrix already on record, creating one now would be premature —
Workbench has a single library surface and no plural entry points a YAML structural map would
usefully enumerate beyond what `CLAUDE.md`'s existing table and the new `docs/README.md`
already say in prose. **Not revisited or changed by this check.**

---

## What this check does not do

- Does not rename, create, or modify any file in any of the three repositories.
- Does not decide which of §3's two resolutions (shared schema vs. role-name-only) applies —
  that's SE/PO's call.
- Does not propose a `PROJECT_INDEX.yaml` for `workbench`.
