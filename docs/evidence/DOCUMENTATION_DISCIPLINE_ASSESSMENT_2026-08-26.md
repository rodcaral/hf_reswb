# Reusable Documentation Discipline — Assessment for Workbench and Future Projects

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE
**Status: read-only analysis only. No file reorganized, moved, or deleted. No HistFinTS
convention adopted here merely because it already exists there — each recommendation below is
justified against Workbench's own observed situation, not copied.**

---

## 0. What was actually compared, verified directly

**Workbench (`docs/`)**: 71 top-level `.md` files, no `README.md`, no machine-readable index of
any kind. The only navigational aid is `CLAUDE.md`'s "Where things are" table (§20), which
names roughly 8 files by hand. `docs/DECISIONS.md` is 3,831 lines, a single reverse-chronological
prose ledger. Two informal subdirectories exist already: `docs/preliminares/` (early planning
docs) and `docs/reproducibility/` (code+data backing one investigation) — both predate this
review and were never formalized as a category.

**HistFinTS's demonstrated model** (read directly, not from memory of the earlier retention
exercise): `index.yaml` (machine-readable structural map — entry points, layers, doc categories,
tooling, testing conventions); `docs/README.md` (a 7-item human "reading order" for
current-state reference only, explicitly *not* history — "Nothing was deleted... read `v2`" for
history); `EVIDENCE_LOG.md` (a 109-line pointer-list for the Durable-evidence and Reusable-
methodology classes only, now genuinely populated — 21 + 6 entries, reconciled with Workbench's
own 2026-08-26 matrix); `archive/completed_features/`, `archive/planning/`, `future_designs/`
folders; and a git-tag-based full-history extraction (`v2` ref holds the old numbered `docs/01`-
`37` set, deleted from the working tree but permanently addressable via `git show v2:...`).

---

## 1. Which proposed concepts transfer cleanly

- **The four-class lens itself** (current reference / durable evidence-audit / reusable
  methodology-capability / closed historical) as a *way of thinking* about any doc when deciding
  what to do with it — transfers cleanly as a mental checklist, independent of whether it's ever
  formalized into a directory structure or a dedicated index file.
- **The five-condition deletion gate** (no inbound dependency; no unique evidence/reproducibility
  content; operative conclusion preserved elsewhere; not an authoritative closure/validation
  record; removal doesn't make retained docs incomplete/misleading) — domain-agnostic hygiene,
  useful for any project, at any scale, the moment someone actually proposes removing a
  document. Nothing about it is HistFinTS-specific.
- **"Reclassify and point-to, never delete by default"** — the same standing discipline this
  whole session has applied to code and data, just extended to documentation. Transfers as a
  principle regardless of the specific mechanism (a pointer-list, a folder move, or a git-tag
  extraction).
- **A single, short "read these first" entry point** for anyone (human or agent) landing on the
  repo cold — the *need* transfers directly; Workbench's 71 ungrouped files are a real instance
  of exactly the problem this concept solves. The specific two-file (`README.md` +
  `index.yaml`) implementation does not need to transfer wholesale — see §2.

## 2. Which would be unnecessary overhead in Workbench

- **A separate machine-readable `index.yaml`.** HistFinTS's earns its keep because it has
  multiple real entry points (CLI, web, an on-hold GUI), ten provider adapters, and a layered
  architecture with import-boundary rules worth stating machine-readably. Workbench has one
  library surface, no UI, and no plural entry points to enumerate — a YAML structural map today
  would describe almost nothing `CLAUDE.md`'s existing prose table doesn't already say. Premature
  ceremony for the current shape of this project.
- **A third parallel index (`EVIDENCE_LOG.md`) on top of `CLAUDE.md`'s table and
  `DECISIONS.md`.** For 71 files this *might* eventually help (see §5), but adding a third
  indexing mechanism without retiring or subordinating either of the other two creates a real,
  observed risk: HistFinTS itself now has three places that could theoretically drift out of
  sync (`index.yaml`, `README.md`, `EVIDENCE_LOG.md`) — a cost worth naming honestly rather than
  importing uncritically.
- **The git-tag/branch full-history-extraction move** (`v2`-style). This solves a problem
  specific to HistFinTS's history: a *sequential, numbered* 37-document design-doc set that
  strictly superseded itself version-to-version. Workbench's `DECISIONS.md` was never structured
  that way — it is already a single, append-only, current ledger, so there is no equivalent
  "extract the old numbered sequence into a separate ref" migration to perform. Adopting this
  mechanic would be solving a problem Workbench doesn't have.
- **A mandatory three-folder archive taxonomy** (`archive/completed_features/`,
  `archive/planning/`, `future_designs/`) as a *required* structure. Workbench already has rough
  functional equivalents (`preliminares/`, and dated docs already read as their own timeline);
  forcing HistFinTS's exact folder names and count onto a differently-shaped project is
  over-fitting, not adoption of a principle.

## 3. Documentation problems the HistFinTS model would fail to address in Workbench

- **Cross-repository evidence anchoring.** Every one of this session's `docs/histfints-requests/`
  deliverables cites specific line numbers, function names, or test counts in a *sibling* git
  repository (`histfints-v3`) that has its own independent commit history and can drift without
  Workbench's own repo state changing at all. HistFinTS's four-class model classifies documents
  *within one repository*; it has no concept of "this Durable-evidence doc's claims are anchored
  to external-repo state that must be re-verified, not assumed, before trusting it again" — which
  is exactly the failure mode this session hit and corrected multiple times (e.g. re-verifying
  `index.yaml` content directly rather than trusting a prior turn's description of it). A reusable
  standard for Workbench needs an explicit marker for "cross-repo-anchored evidence," which the
  HistFinTS model has no equivalent of because it doesn't need one.
- **A rapidly-growing, single-file prose ledger as the primary continuity mechanism.**
  `DECISIONS.md` (3,831 lines) isn't just a changelog — because Claude sessions carry no memory
  of prior conversations, it functions as the *actual mechanism* by which a fresh session
  reconstructs full context. HistFinTS's model has no analog to this at all: its "why" lives in a
  git-tag-addressable old doc set, read on demand, not in one ever-growing file that every new
  session is implicitly expected to be able to search. The four-class model classifies
  *standalone files*; it says nothing about how to keep one single, ever-growing ledger navigable
  as it approaches a size where even `grep`-based recall starts to strain. This is Workbench's
  most load-bearing document and the one furthest outside HistFinTS's model's scope.
- **Multi-party addressing/authority conventions.** This session generated real, durable process
  learnings — the standing rule that sibling-repo *writes* require PO confirmation while *reads*
  don't, correctly refusing instructions addressed to the wrong party, chain-of-custody tracking
  across DFA/SE/PO/UI-UE/SDT roles. These aren't technical findings about the system; they're
  process rules about how this agent should behave in this working relationship. The four-class
  model has no bucket for this at all, by design — it's out of scope for a *documentation*
  retention exercise. Workbench needs an explicit answer for where this kind of thing goes (see
  §6); HistFinTS's model doesn't supply one because it was never asked to.

## 4. Proposed minimum viable standard for a new project

Deliberately small — "minimum viable," not a scaled-down copy of HistFinTS's full system:

1. **One short reading-order pointer** (a `README.md`, or a table inside `CLAUDE.md` as
   Workbench already has) — 3-7 items naming what a newcomer should read first to understand
   current-state truth. No formal taxonomy behind it yet.
2. **One append-only decision/evidence ledger** (Workbench's `DECISIONS.md` shape: date, what
   happened, why, evidence, in reverse-chronological order) — the single highest-value practice
   observed this session, since it's what lets a memoryless session reconstruct full context
   reliably. Not split into multiple files or classes from day one.
3. **An informal, write-time mental sort**, applied by whoever is writing a new doc, not enforced
   as a separate ritual: is this describing *current truth* (belongs in the reading-order set),
   a *dated one-off finding* (stays wherever it's written, gets linked from whatever references
   it), or a *decision* (goes in the ledger)? No dedicated folders or labels required yet.
4. **One stated norm**: don't delete a document without checking what references it. Stated once,
   in prose, not enforced via a formal five-point checklist until volume actually justifies one
   (§5).

Everything else in HistFinTS's model — `index.yaml`, `EVIDENCE_LOG.md`, archive/ subfolders,
formal four-class labeling, git-tag history extraction — is explicitly **not** part of the
minimum viable standard. They're §5 material.

## 5. Optional practices — activate only as volume/evidence grows

Stated as heuristics, not hard counts:

- **Formal four-class labeling + a dedicated evidence-log index** — once the flat, dated-doc
  count is large enough that a newcomer (or an agent) can no longer answer "which of these are
  still load-bearing" by skimming the directory listing or `CLAUDE.md`'s table in under a
  minute. HistFinTS crossed this line somewhere around 40-50 loose files; Workbench, at 71 with
  zero categorization, is arguably already past it for `docs/` specifically — this is the one
  concrete, actionable signal from this review, though acting on it is a separate decision from
  this analysis.
- **A separate machine-readable index (`index.yaml`)** — only once there are genuinely multiple,
  differently-shaped entry points (several interfaces, several independently-versioned
  components) that a short prose table can no longer concisely enumerate. Not yet true for
  Workbench.
- **Physical archive/ subfolders** — once closed-historical documents numerically dominate the
  listing enough to obscure the current-reference ones at a glance.
- **Git-tag/branch history extraction** — only if Workbench's documentation ever becomes a
  strictly-sequential, self-superseding numbered series the way HistFinTS's old `docs/01-37` was.
  Its current dated-topic-name growth pattern doesn't have that shape, so this practice may never
  become relevant regardless of volume.
- **A formally enforced five-condition deletion gate** — build it in response to an actual
  request to delete something, the way this session's own exercise unfolded for HistFinTS, not
  speculatively ahead of any concrete need.

## 6. The boundary between repository documentation and project/agent memory

Grounded in this session's own direct operational experience with the `memory/` system, not
theory:

- **Repository documentation** (`docs/`, `DECISIONS.md`) should hold facts that remain true
  regardless of *who* — which session, which agent, which human — is working on the project
  next: decisions made, evidence gathered, current architecture, open technical questions.
  Anyone cloning the repo fresh gets the same picture from it.
- **Project/agent memory** (this session's `memory/` + `MEMORY.md`) should hold behavioral and
  relationship-specific guidance: corrections, confirmed preferences, standing scope/authority
  rules (e.g. this session's "read sibling repos freely, confirm with PO before writing"), and
  context about the user's role that wouldn't read sensibly as a line in a technical changelog
  and isn't itself a fact about the system.
- **The dividing test used throughout this session**: *would this still be true and worth
  recording if a different agent or a human engineer picked up this exact repository with no
  memory of this conversation?* If yes, it's a repo-documentation fact. If the fact is really
  about how *this agent* should behave going forward, or what's been learned about the working
  relationship, it belongs in memory — and should not be duplicated into `docs/`, where it would
  clutter the technical record with process/relationship content other engineers don't need.
- **A reasonable, already-demonstrated middle case**: a repo changelog entry may *note that* a
  standing rule was established on a given date (a project fact — "a rule was set") without
  becoming the canonical location for the rule's content itself (which stays in memory). This
  session's own `DECISIONS.md` entry for the sibling-repo-write rule follows exactly this
  pattern.
- HistFinTS's four-class model has **no concept of memory at all** — every one of the 34 files it
  triages is repo-committed documentation. It offers nothing about where cross-session
  behavioral learnings should live, because that question is out of its scope by design, not
  because it was considered and rejected. A reusable standard for Workbench (or any future
  project run this way) needs to state this boundary explicitly, since the HistFinTS exercise
  never had to.

---

## What this assessment does not do

- Does not reorganize any file in Workbench's `docs/` directory.
- Does not create an `index.yaml`, `EVIDENCE_LOG.md`, or archive/ subfolder for Workbench.
- Does not adopt any HistFinTS convention merely because it already exists there — every
  recommendation above is justified against Workbench's own observed scale and shape, and several
  HistFinTS practices are explicitly rejected as overhead for this project's current state.
