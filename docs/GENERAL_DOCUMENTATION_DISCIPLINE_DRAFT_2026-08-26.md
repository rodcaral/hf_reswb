# General Documentation Discipline (Draft)

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE / PO
**Status: draft, proposed for adoption. Not yet placed in a canonical location, not yet
applied to any repository. Synthesized from the PO-approved baseline and this session's three
completed adoption assessments** (`DOCUMENTATION_DISCIPLINE_ASSESSMENT_2026-08-26.md`,
`DOCUMENTATION_DISCIPLINE_GAP_MATRIX_2026-08-26.md`, `PROJECT_INDEX_MIGRATION_CHECK_2026-08-26.md`).

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
| Decision/continuity ledger | `DECISIONS.md` | **Yes** | Append-only, dated, prose entries: what happened, why, evidence. The project's actual cross-session continuity mechanism — the single highest-value practice observed across every project checked. |
| Reading-order entry point | `README.md` | Once doc count exceeds what a newcomer can skim in under a minute | A short (3–7 item), human, current-state-only pointer. Never a history; never duplicates the ledger. |
| Machine-readable index | `PROJECT_INDEX.yaml` | Only once multiple genuinely different entry points/components exist that prose can't concisely enumerate | No mandated internal schema — a structural map in one project, a living status/gate tracker in another are both legitimate uses of the same name. Sharing the name promises a *location*, not a *shape*. |
| Evidence register | `EVIDENCE_LOG.md` | Only once dated evidence/investigation documents are numerous enough that the ledger and entry point alone can't answer "is this still trustworthy" | A pointer-list only. Never owns or duplicates evidence content — classifies and links to documents that live wherever they already are. |

A project with only a `DECISIONS.md` and nothing else is fully compliant with this discipline
at its current scale.

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

---

## 4. Indexing and discoverability

- Below the reading-order threshold (§1): no entry point needed. A short table inside whatever
  process-guidance file the project already has (e.g. an agent-instructions file) satisfies the
  discipline.
- At and above the threshold: one `README.md`, 3–7 items, current-state only.
- Only once plural, differently-shaped entry points or components exist that a short prose list
  can't concisely enumerate: a `PROJECT_INDEX.yaml`, with whatever internal shape suits that
  project.
- Never introduce a third parallel index without retiring or explicitly subordinating one of
  the existing two — every project checked that has three indexing mechanisms (a ledger, a
  README, and a machine index) carries a real, observed risk of the three drifting out of sync
  with each other. If a third is added, one of the others should state which is authoritative
  for what.

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

- A dated document is a point-in-time record. It is never edited after the fact to make it
  "currently true" — its content stays exactly as originally written.
- When new information corrects or supersedes an earlier document, write a **new** dated
  document. Link in one or both directions with a single explicit line — the new document
  states what it supersedes and on which specific point (not "supersedes everything," which
  invites over-broad dismissal of still-valid content); the old document may, if convenient,
  receive a one-line "superseded on [specific point] by [new document]" note at its top. Adding
  this one line is linking, not rewriting history.
- Never retrofit an old document to match a labeling scheme, terminology, or convention
  established after it was written. If the scheme matters enough to apply retroactively, that's
  a deliberate, separate migration decision — not a side effect of writing something new.

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
| `EVIDENCE_LOG.md` evidence register + formal four-class tagging | Dated evidence/investigation documents are numerous enough that "is this still load-bearing" stops being answerable by skimming |
| Physical archive/closed-historical folders | Closed-historical documents numerically dominate the listing enough to obscure current-reference ones at a glance |
| Full-history extraction into a separate branch/tag | The documentation itself becomes a strictly sequential, self-superseding numbered series (not every dated-topic-name growth pattern has this shape, and may never need this regardless of volume) |
| A formally enforced five-condition deletion gate (§7) | Someone actually proposes deleting a specific document |
| Cross-repo anchor convention (§5) | The first document making a claim about another repository's state — this one has no volume threshold; adopt it immediately once any cross-repo documentation work begins |

---

## Recommended canonical location

**Proposal: a new, dedicated, project-independent location — not inside `workbench`,
`histfints-v3`, or `histfints_uiue`.** None of the three existing repositories is neutral with
respect to the others (HistFinTS is the data-owning system; Workbench and UI/UE are both
consumers of it), and placing the discipline inside any one of them would implicitly subordinate
the others to that project's own conventions — exactly what "project-independent" is meant to
avoid.

Concretely: a sibling directory at the same level as the existing projects (e.g.
`Proyectos/_shared-standards/` or an equivalent name PO prefers), holding this document and any
future cross-project standards, referenced by each project's own entry point rather than
duplicated into each.

**Not created here** — this is a recommendation, not an action, per instruction. This draft
currently lives in `workbench/docs/` only because that is where this synthesis was produced; it
should be moved to wherever PO approves as the canonical location, not left here as the
de facto standard by default.

---

## What this draft does not do

- Does not modify `histfints-v3`, `histfints_uiue`, or create the recommended shared location.
- Does not mandate any HistFinTS-specific YAML schema, folder taxonomy, or human-role
  vocabulary.
- Does not apply retroactively to any existing document in any project (per §6, retroactive
  application is a separate, deliberate decision).
