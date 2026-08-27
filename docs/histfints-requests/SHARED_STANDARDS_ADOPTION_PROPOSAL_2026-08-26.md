# Shared Standards Adoption Proposal — General Documentation Discipline

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** PO (for approval)
**Status: proposal only. No file has been created, moved, or modified in `histfints-v3`,
`histfints_uiue`, or any new shared location. Everything below is exact proposed content,
returned for review before any action is taken.**

**Cross-repo anchor:** histfints-v3 @ `a3dfb47` ("CI: target master and v3, not the nonexistent
main branch"), verified 2026-08-26 — `docs/README.md` content quoted/referenced below is as of
this commit.
**Cross-repo anchor:** histfints_uiue, state as read on 2026-08-26 — no commit hash available
(repo has no `.git`; confirmed by direct `git log` failure at read time).

---

## 1. What is being proposed

Move the General Documentation Discipline out of `workbench/docs/` (where it was drafted and
revised as a byproduct of authorship, per `GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md`)
into a new, neutral sibling location, and have all three projects — `histfints-v3`, `workbench`,
`histfints_uiue` — point to it rather than each holding or restating it.

```
Proyectos/
├── _shared-standards/                              ← NEW directory, not inside any of the three
│   ├── GENERAL_DOCUMENTATION_DISCIPLINE.md          ← the discipline itself (canonical, v1.0)
│   └── PROJECT_INDEX.yaml                           ← minimal: identifies the standard + scope
├── histfints-v3/
│   └── docs/README.md                               ← MODIFIED: one new pointer section
├── workbench/
│   └── docs/README.md                               ← MODIFIED: one new pointer section
│   └── docs/GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md   ← retained as-is, dated draft
│                                                        record (§6 of the standard itself: a
│                                                        closed-historical/durable-evidence
│                                                        document is never deleted for being
│                                                        superseded — it gets a one-line
│                                                        superseded-by note, not removal)
└── histfints_uiue/
    └── PROJECT_INDEX.yaml                           ← MODIFIED: one new top-level key
```

No project's own `DECISIONS.md`, `PROJECT_INDEX.yaml` internal schema, `README.md` reading
order, or any other existing content changes beyond the one addition named for each.

---

## 2. New file: `_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md`

Full proposed content (the revised draft, with only the header/status block and the closing
"canonical location" section rewritten to reflect that this **is** now the canonical copy,
rather than a draft recommending one; §§0–8 are carried over unchanged from the PO-approved,
six-point-revised version — no substantive change to the discipline itself):

~~~markdown
# General Documentation Discipline

**Version:** 1.0
**Canonical location:** `Proyectos/_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md`
**Applies to:** `histfints-v3`, `workbench`, `histfints_uiue` (referenced, not duplicated, by
each project's own entry point).
**Origin:** Authored by SDT Workbench, synthesized from the PO-approved evidence-strength
baseline and three completed adoption assessments, then revised per SE's six-point directive
using the independent HistFinTS/UI-UX adoption reviews. History of this document's drafting
and revision is preserved in `workbench/docs/DECISIONS.md` and in the retained draft at
`workbench/docs/GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md` — this file is the
adopted result, not a restatement of that history.

**Explicitly not copied from HistFinTS**: no mandated YAML schema, no fixed folder taxonomy
(`archive/completed_features/` etc.), no human governance-role names (PO/SE/DFA/UI-UE/SDT-*
are this ecosystem's own multi-party protocol, not part of a general documentation discipline).
What *is* carried forward is vocabulary already agreed across more than one project in this
ecosystem — the four canonical file roles (one of which, `DECISIONS.md`, originates in
Workbench, not HistFinTS; another, `PROJECT_INDEX.yaml`, originates in `histfints_uiue`) and
the four-class evidence lens (PO-approved, applied identically wherever it's been used so far).

---

## 0. Philosophy

Minimum viable by default. Every mechanism below states its own activation condition — nothing
is adopted speculatively ahead of the scale or pain that would justify it. A new project starts
with almost none of this; a project's documentation grows into more of it as its own evidence
volume demonstrates the need, never before.

---

## 1. Canonical file roles

Four roles, by name — a shared naming convention across projects, not a shared schema. Sharing
a name means "if this file exists, this is what it's for," not "this file has these YAML keys"
or "this file follows this exact template."

| Role | Canonical name | Required from day one? | Purpose |
|---|---|---|---|
| Decision/continuity ledger | `DECISIONS.md` (default implementation) | **A continuity mechanism is required from day one — not specifically this file.** | Whatever lets a later session reconstruct what happened and why without the original conversation. `DECISIONS.md` (append-only, dated, prose) is the default and the single highest-value practice observed across every project checked, but it is not the only validated implementation — see the note below. |
| Reading-order entry point | `README.md` | Once doc count exceeds what a newcomer can skim in under a minute | A short (3–7 item), human, current-state-only pointer. Never a history; never duplicates the ledger. |
| Machine-readable index | `PROJECT_INDEX.yaml` | Only once multiple genuinely different entry points/components exist that prose can't concisely enumerate | Standardizes *location and name only, not schema* — a structural map in one project, a living status/gate tracker in another are both legitimate uses of the same name. **Consumers must not assume identical internal structure across projects**; reading one project's `PROJECT_INDEX.yaml` does not tell you the shape of another's. |
| Evidence register | `EVIDENCE_LOG.md` | Only once dated evidence/investigation documents are numerous enough that the ledger and entry point alone can't answer "is this still trustworthy" | Covers **durable evidence, reusable method/capability, and closed historical** records where applicable — not durable-evidence/reusable-method only, and not a bare filename list. Each entry carries a concise retention/dependency rationale (why it's kept, what depends on it, or why it's excluded from the current-reference set) — not just a pointer. Still never owns or duplicates the underlying document's content. |

**Validated alternative to `DECISIONS.md` specifically**: a project may satisfy the continuity-
mechanism requirement with well-formed Git commit history (one logical decision per commit,
descriptive messages) plus a pointer-style project-memory layer that indexes *into* that
history, rather than a standalone prose ledger file — this has been independently validated in
this ecosystem (HistFinTS's own memory layer takes this shape) and is not a lesser substitute,
provided it actually delivers the same reconstruction capability a fresh session needs.

A project with only a continuity mechanism (in either validated form) and nothing else is fully
compliant with this discipline at its current scale.

---

## 2. Lifecycle / evidence-strength dimensions

Four classes, applied as a lens — at write time, or during a periodic review — not as a
mandatory folder or filename-prefix taxonomy imposed from day one:

- **Current** — describes present, still-valid system truth. Belongs in the reading-order set
  once one exists.
- **Durable evidence** — a point-in-time finding or record. Its *conclusion* may later be
  superseded, but its reproducibility/audit value survives regardless — never deleted on the
  strength of being outdated alone.
- **Reusable method/capability** — describes a technique or capability usable again,
  independent of the one investigation that produced it.
- **Closed historical** — resolved, no longer actionable, retained only for narrative/context.

These four names are shared cross-project vocabulary already (via the PO-approved model) and
are kept as-is rather than re-labeled — but applying them via a formal per-document tag/index
is itself a scale-dependent control (§8), not a day-one requirement.

---

## 3. The Git/docs/memory boundary

A repository's committed documentation (the ledger, the entry point, the index, the evidence
register) holds facts that remain true regardless of *who* — which session, which agent, which
human — works on the project next.

A separate, non-repository memory layer (whatever an individual agent or tool maintains across
sessions) holds behavior- and relationship-specific guidance: corrections, confirmed
preferences, standing scope/authority rules, and context about a specific working relationship.

**The dividing test**: would this fact still be true and worth recording if a different agent
or a different human engineer picked up this exact repository with no memory of this
conversation? If yes, it belongs in repository documentation. If it's really about how a
specific agent should behave going forward, it belongs in that agent's own memory layer, not
duplicated into the repository — a repository changelog entry may *note that* such a rule was
established on a given date, without becoming the rule's canonical location.

**Memory may hold compact retrieval pointers or summaries of repository-canonical facts** —
this is not a boundary violation, provided two conditions both hold: the memory entry is
explicitly marked non-authoritative (a cache/index, not a source), and it names or links the
canonical repository location the fact actually lives at. This is exactly the shape HistFinTS's
own memory layer already uses successfully (e.g. a pointer noting where the related-repos
reference lives, rather than re-stating the reference's full content) and is the intended,
supported use of memory alongside repository documentation, not a workaround to be discouraged.
What memory must not do is *originate* a fact about the system with no repository-side source —
that content belongs in repository documentation from the start, with memory holding at most a
pointer to it.

---

## 4. Indexing and discoverability

- Below the reading-order threshold (§1): no entry point needed. A short table inside whatever
  process-guidance file the project already has (e.g. an agent-instructions file) satisfies the
  discipline.
- At and above the threshold: one `README.md`, 3–7 items, current-state only.
- Only once plural, differently-shaped entry points or components exist that a short prose list
  can't concisely enumerate: a `PROJECT_INDEX.yaml`, with whatever internal shape suits that
  project.
- `README.md`, `PROJECT_INDEX.yaml`, and `EVIDENCE_LOG.md` may coexist — three indexes with
  three **distinct, non-overlapping** canonical roles (human reading-order; machine-readable
  structure/status; evidence retention register) is not itself a problem, and is not what §1's
  activation thresholds are warning against.
- What to actually guard against is **overlapping or redundant** indexing — two files that could
  answer the same question and might drift apart on it (e.g. a README that also tries to track
  evidence status, or a machine index that duplicates the ledger's decision history). If two
  indexing mechanisms would ever need to agree on the same fact, one of them should state
  outright that it defers to the other for that fact, rather than both maintaining it
  independently.

---

## 5. Cross-repository evidence anchoring

Any document making a claim about the current state of a *different* repository — code
behavior, test counts, file contents, line numbers — must carry a one-line anchor near its
header:

- If the other repository has version control:
  `**Cross-repo anchor:** <repo> @ <commit-hash> (<short description>), verified <date>.`
- If it does not (at the time of writing):
  `**Cross-repo anchor:** <repo>, state as read on <date> — no commit hash available.`

This is a per-document annotation, not a new index or schema. Its purpose: make explicit that
a claim about another repository's state is only as current as the moment it was checked, and
must be re-verified — not assumed — before being trusted again in a later session.

---

## 6. Supersession and correction

**Immutability applies to durable-evidence and closed-historical records** (§2). A dated
document in either of those two classes is a point-in-time record: it is never edited after the
fact to make it "currently true" — its content stays exactly as originally written.

- When new information corrects or supersedes a durable-evidence or closed-historical document,
  write a **new** dated document. Link in one or both directions with a single explicit line —
  the new document states what it supersedes and on which specific point (not "supersedes
  everything," which invites over-broad dismissal of still-valid content); the old document may,
  if convenient, receive a one-line "superseded on [specific point] by [new document]" note at
  its top. Adding this one line is linking, not rewriting history.
- Never retrofit an old document to match a labeling scheme, terminology, or convention
  established after it was written. If the scheme matters enough to apply retroactively, that's
  a deliberate, separate migration decision — not a side effect of writing something new.

**Reusable method/capability documents (§2) are the deliberate exception.** A document
describing a living, still-in-use technique or capability may be maintained and corrected in
place, the same way current-state reference material is — it is not a point-in-time record of
one investigation, and freezing it at its original text would make it progressively less useful
as the capability it describes evolves. The one requirement: corrections must be **explicit**,
not silent — a maintained-in-place document should show that it was updated (a short "updated
[date]: [what changed]" note is enough), so a reader can tell the difference between "this has
always said this" and "this used to say something else." This is narrower than current-state
documents' own update discipline only in that explicit correction marking is required here,
where it's optional for pure current-state material.

**This document itself follows this rule as a reusable method/capability document.** Future
revisions are made in place, with an "updated [date]: [what changed]" note added here rather
than a new dated file being written each time.

---

## 7. Retention and deletion safeguards

Before removing any document, verify all five conditions — if any fails, retain:

1. No inbound dependency (nothing else references or points to it).
2. No unique evidence or reproducibility content not preserved elsewhere.
3. Its operative conclusion is preserved elsewhere (a superseding document exists and covers
   the same ground).
4. It is not an authoritative closure/validation record (the final record of a decided
   question).
5. Removing it does not make the documents that remain incomplete or misleading.

Build this as an enforced, formal gate only in response to an actual proposal to delete
something (§8) — not speculatively, ahead of any concrete need.

---

## 8. Scale-dependent controls — activation heuristics

| Practice | Activate when |
|---|---|
| `README.md` reading-order entry point | Doc count exceeds what a newcomer can skim in under a minute without one |
| `PROJECT_INDEX.yaml` machine-readable index | Multiple genuinely different entry points/components exist |
| `EVIDENCE_LOG.md` evidence register (covering durable-evidence, reusable-method, and closed-historical records, each with a retention/dependency rationale) | Dated evidence/investigation documents are numerous enough that "is this still load-bearing" stops being answerable by skimming |
| Physical archive/closed-historical folders | Closed-historical documents numerically dominate the listing enough to obscure current-reference ones at a glance |
| Full-history extraction into a separate branch/tag | The documentation itself becomes a strictly sequential, self-superseding numbered series (not every dated-topic-name growth pattern has this shape, and may never need this regardless of volume) |
| A formally enforced five-condition deletion gate (§7) | Someone actually proposes deleting a specific document |
| Cross-repo anchor convention (§5) | The first document making a claim about another repository's state — this one has no volume threshold; adopt it immediately once any cross-repo documentation work begins |

---

## Scope note

- Does not mandate any HistFinTS-specific YAML schema, folder taxonomy, or human-role
  vocabulary.
- Does not apply retroactively to any existing document in any project (per §6, retroactive
  application is a separate, deliberate decision).
- Referencing this file from a project's entry point does not obligate that project to adopt
  any control ahead of its own §8 activation threshold.
~~~

---

## 3. New file: `_shared-standards/PROJECT_INDEX.yaml`

Deliberately minimal — identifies the standard and its scope, nothing else. Per §1/§6 of the
standard itself, this is a machine-readable index in the sense the discipline defines the term
(location/name convention, not shared schema with any other project's file of the same name):

```yaml
# _shared-standards/PROJECT_INDEX.yaml
# Machine-readable index for this shared-standards location. Per the General Documentation
# Discipline's own §1, PROJECT_INDEX.yaml standardizes name/location only — this file's shape
# is specific to what this location holds, not a schema other projects must match.

standard:
  name: General Documentation Discipline
  file: GENERAL_DOCUMENTATION_DISCIPLINE.md
  version: "1.0"
  status: proposed — pending PO approval
  authored_by: SDT Workbench
  scope: >-
    Project-independent documentation-discipline standard: canonical file roles
    (DECISIONS.md/README.md/PROJECT_INDEX.yaml/EVIDENCE_LOG.md by name, not schema),
    a four-class evidence-strength lens, the git/docs/memory boundary, indexing and
    discoverability rules, the cross-repo evidence-anchoring convention, supersession/
    correction rules, retention/deletion safeguards, and scale-dependent activation
    heuristics. Not a mandate for any project-specific structure, folder taxonomy, or
    role vocabulary.
  applies_to:
    - histfints-v3
    - workbench
    - histfints_uiue
  referencing_projects_must:
    - point to this file from their own entry point (README.md or PROJECT_INDEX.yaml)
    - not duplicate its content into their own repository
    - not assume any other project's PROJECT_INDEX.yaml or README.md shares this
      location's file names, schema, or internal structure
  history:
    - Drafted in workbench/docs/GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md
      (2026-08-26), revised per SE's six-point directive same day, proposed for
      relocation here per SE's shared-standards-adoption directive (2026-08-26). See
      workbench/docs/DECISIONS.md for the full reasoning trail.
```

---

## 4. Proposed pointer changes (exact text, not yet applied)

### 4a. `workbench/docs/README.md`

Add as a new final section, after the existing "Convention — marking evidence anchored to a
sibling repository" section:

```markdown
## Cross-project standard

This project's documentation practices follow the shared **General Documentation Discipline**
at `../../_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` — the canonical copy; not
duplicated here. `DECISIONS.md` above is this project's continuity-mechanism implementation
under that standard (§1); the numbered items in `docs/` are this project's durable-evidence and
closed-historical record under the standard's four-class lens (§2).
```

### 4b. `histfints-v3/docs/README.md`

Add as a new final section, after the existing reading-order list (item 7, `KNOWN_LIMITATIONS.md`):

```markdown
## Cross-project standard

This project's documentation practices follow the shared **General Documentation Discipline**
at `../../_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` — the canonical copy; not
duplicated here. This project's own `v2` ref (§6/§8's full-history-extraction control) and its
`PROJECT_INDEX.yaml` (§1's machine-readable-index role, structural-map shape) are this
project's own implementations under that standard.
```

### 4c. `histfints_uiue/PROJECT_INDEX.yaml`

Add as a new top-level key, placed after the existing `project:` block and before `authority:`:

```yaml
documentation_standard:
  follows: ../_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md
  note: >-
    Canonical source; not duplicated here. This file's own schema (living workstream
    status/gate tracker) is this project's own choice under the standard's §1 name-not-
    schema rule for PROJECT_INDEX.yaml — it is not expected to structurally match
    histfints-v3's PROJECT_INDEX.yaml (a static structural map) or any future workbench
    file of the same name.
```

---

## 5. What this proposal does not do

- Does not create `_shared-standards/` or any file inside it.
- Does not modify `histfints-v3/docs/README.md` or `histfints_uiue/PROJECT_INDEX.yaml`.
- Does not delete or alter `workbench/docs/GENERAL_DOCUMENTATION_DISCIPLINE_DRAFT_2026-08-26.md`
  — per the standard's own §6, it is retained in place as the dated record of how the canonical
  version came to be, with the canonical file (§2 above) noting that history rather than
  restating it.
- Does not commit any of the above anywhere. All content above is returned for PO review; on
  approval, SDT Workbench will create `_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md`
  and its `PROJECT_INDEX.yaml`, apply §4a to `workbench/docs/README.md` directly, and — per the
  standing sibling-repo rule — present §4b/§4c to SDT HistFinTS and UI/UE respectively for their
  own repos rather than writing into `histfints-v3` or `histfints_uiue` directly.
