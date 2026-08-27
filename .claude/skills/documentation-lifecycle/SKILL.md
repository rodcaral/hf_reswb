---
name: documentation-lifecycle
description: Use when a repository's documentation has grown into undifferentiated clutter (dated investigation docs, closed decisions, superseded proposals, active external filings, and current reference material all sitting in one flat location) and needs a disciplined, incremental path to a clean current/evidence/request split — or when a repository has a predecessor (an old branch, worktree, fork, or prior version) whose historical material could be mistaken for current authoritative truth. Covers classification, dry-run planning, incremental migration with validation, and predecessor-repository lineage marking. Not for routine day-to-day doc edits — this is a structural remediation exercise, triggered explicitly (e.g. "clean up our docs", "plan a docs migration", "is this old repo still authoritative", "reconcile our HOLD files").
---

# Documentation Lifecycle

A repeatable method for taking an undifferentiated documentation corpus — or a set of
repositories with unclear current/predecessor status — to a state where **a reader or agent
can always tell, at the point of entry, what is current and what is historical**, without
losing evidence, provenance, or the ability to trace *why* something is the way it is.

This skill is process, not content. It carries no facts about any specific project's schema,
domain, team roles, or naming conventions. Every example below is illustrative only —
substitute your own repository's actual structure, team names, and vocabulary.

**Epistemic boundary.** This skill may determine *technical* facts — repository structure,
git lineage, reference patterns, whether something is cited elsewhere, whether a status
claimed in one document is contradicted by a later authoritative one. **It must not silently
decide product, domain, governance, or relationship status when those remain open.** A file
whose disposition turns on any of those questions becomes a HOLD item, routed to whoever
actually owns that decision type (§5) — never resolved by inference, however confident the
inference feels. This principle governs every section below, not only the dependency-routing
mechanics in §5.

**Historical evidence is preserved; current authority is not.** A predecessor artifact may be
authoritative evidence of what that predecessor implemented, documented, or decided at the
time — that value does not expire and is never a reason to treat it as unreliable. But it does
not govern the current project unless a current authoritative source explicitly adopts or
carries forward whatever it says. "Historical" describes *where a rule's authority currently
comes from*, not the trustworthiness of the record itself. This is the governance boundary the
rest of the skill enforces; keep it in mind especially in §3 and §8.

---

## 0. When this applies

Two related but distinct problem shapes trigger this skill:

**A. Single-repository documentation clutter.** A `docs/`-style directory (or equivalent) has
accumulated dozens of dated, topic-named files — investigation writeups, closed decisions,
remediation packages, status checks — alongside the small set of files that are actually
current reference material, with no structural distinction between them.

**B. Predecessor-repository ambiguity.** A repository has one or more predecessors — an old
branch, a `git worktree` on a stale ref, a forked-and-abandoned earlier version, a folder that
looks like an alternate copy — and neither the predecessor nor the current repository states,
at its own entry point, which one is authoritative.

Both shapes share the same underlying risk: **authority ambiguity** — an artifact whose
current/historical status is not stated at its own point of entry, so a reader or agent has no
way to tell which is which short of checking timestamps or asking someone. This is not a claim
that dated material is inherently suspect: a dated evidence record can remain load-bearing
indefinitely (see §3's Evidence bucket). The problem this skill addresses is the *absence of an
explicit authority signal*, not age itself.

---

## 1. Repository-status determination

Before classifying documentation structurally, establish whether the repository's
current/historical authority status is **already explicit** — stated in current project
documentation, an existing governance decision, or equivalent authoritative evidence. If it
is not, investigate repository lineage first. Not every invocation of this skill requires a
broad sibling-repository search: if authority is already established, move on to §2.

**Evidence of relationship is not evidence of authority.** Git ancestry, worktree
relationships (`git worktree list` from any worktree in the family; a `.git` file that is a
one-line pointer rather than a real directory is a worktree, not an independent repo), commit
recency, naming similarity, and content lineage are all evidence that two repositories are
*related*. None of them, alone or combined, establishes which one is *authoritative* — that is
a project-governance fact, not a topological one. `git log <predecessor>..<current>` showing
the predecessor as a zero-unmerged-commits ancestor is strong evidence of *lineage*; it is not,
by itself, a governance ruling about which one the project currently treats as canonical.
Cite lineage evidence as exactly that — evidence to bring to whoever can confirm authority —
not as the conclusion itself.

**No shared version control does not mean unrelated.** A folder with no `.git` at all can
still be genuine historical predecessor material — e.g., pre-repository design/ideation content
a later repository's early structure was distilled from. But this judgment rests on *content
lineage*, which is inherently inferential (does later material cite or visibly build on this
folder's content?). When a predecessor classification rests on inferred content lineage rather
than something explicitly documented, **label the conclusion provisional** and route any
consequential reclassification decision to the appropriate owner — do not silently treat the
folder as settled-historical on inference alone.

**This step is read-only by default.** Identifying a likely predecessor — by any evidence
above — does not itself authorize changing, archiving, relabeling, or otherwise acting on it.
That requires the appropriate project/governance decision, unless authority was already
explicit going in.

**Output of this step:** a short list of every known predecessor, each tagged with (a) what
kind of evidence supports the relationship (branch ancestry / commit recency / naming /
content lineage), (b) whether authority status is already explicit or is a provisional
inference from that evidence, and (c) if provisional, who the reclassification decision routes
to.

---

## 2. Inventory

Enumerate every candidate documentation artifact at the location(s) under review — typically
everything at the root of a `docs/`-equivalent directory, since subdirectories that already
separate concerns (an existing outbound-request folder, an existing evidence folder) are
usually *already* differentiated and out of scope for a fresh pass.

Record the **total count** at this step and treat it as a checksum: every later classification
bucket must sum back to this number, or something was missed or double-counted. (This is not
a formality — see §12, this is where real errors get caught.)

---

## 3. Classification taxonomy

Classify every inventoried file into exactly one bucket. Do not skip a file because it "looks
obviously fine" — every bucket assignment should be checkable against a stated rule, not
vibes.

| Bucket | Definition | Typical destination |
|---|---|---|
| **Current** | Describes present, still-valid system truth; a live reference, spec, or contract with an active implementation depending on it. | Stays at the reading-order root. |
| **Evidence** (durable-evidence / closed-historical) | A dated, completed investigation, decision record, or point-in-time finding. Its *conclusion* may later be superseded, but its reproducibility/audit value survives. Never edited for content after the fact — only an additive status marker. | A dedicated, clearly-named physical location (see §4 for naming). |
| **Active request** | An outbound filing, ask, or defect report to another team/party that has **not** been confirmed resolved. Distinct from Evidence: an active request is still load-bearing on a real, unresolved external relationship — moving it to "evidence" would misrepresent it as closed. | An interface/outbound-request location, kept separate from Evidence. |
| **Memory candidate** | Describes *how an agent or session should behave* going forward (a standing scope rule, a confirmed working preference), not a fact about the system that would remain true regardless of who works on it next. | A session/agent memory layer, not repository documentation — see the dividing test in §7. |
| **Rule-D / source-coupled** | Otherwise Evidence-classified, but cited by filename inside live source code or test comments/docstrings. Still movable — but requires a coordinated reference update in the *same* change, and is sequenced into its own batch rather than bundled with plain Evidence moves. | Evidence location, plus a source-comment fix (see §7). |
| **HOLD** | Genuinely ambiguous: recency, an explicit "gate"/"blocking" statement, a structural mismatch with what another document already claims about its location, or a live, undecided proposal about documentation structure itself. | Left in place. Never guessed. |

**A file only qualifies as HOLD if you can name the specific unresolved question.** "Not sure"
is not a classification; "unsure whether this design is closed because the most recent status
document treats it as still-open" is.

**Classification from repository facts is provisional, not a closure determination.** A
file's date, filename pattern, or apparent completeness makes it a *candidate* for the
Evidence bucket — actually moving it there additionally requires confirming that the
capability, decision, or defect it describes is genuinely closed, not merely old-looking.
"Implemented" is not "integrated"; a downstream mitigation is not the closure of the upstream
problem it mitigates; a partial implementation is not a completed one (see the Anti-rules for
the specific failure shapes). When closure itself is not established by the repository's own
record, the file's disposition is HOLD, routed per §5 — never an Evidence move made on the
strength of surface classification alone.

---

## 4. Choosing a physical Evidence location — not an aesthetic choice

If a dedicated evidence/archive location doesn't already exist, choose its name deliberately,
against these two checks, not by convention-copying from an unrelated project:

1. **Vocabulary consistency.** If the project already has (or is adopting) an evidence
   *register* concept (a pointer-list file, however named), the physical folder should share
   that word. Two different words for the same concept inside one project is exactly the kind
   of drift this skill exists to prevent.
2. **Domain-word collision check.** Check whether the candidate name already means something
   else, specific and technical, inside this project's own domain vocabulary. If so, pick a
   different name — reusing an already-loaded word for an unrelated documentation concept
   creates the same kind of ambiguity as a stale predecessor repo.

Prefer a **single flat folder**, not a folder-per-class split. The classification (which of
the sub-types in §3 a file is) belongs in the register's per-entry metadata, not in a second
directory taxonomy that could drift out of sync with the first.

---

## 5. Dependency routing

Not every HOLD question has the same owner or the same resolution path. Before asking anyone
to decide anything, classify **the type of question**, and route accordingly:

| Question type | Who resolves it | How you know it's this type |
|---|---|---|
| **Technical / verifiable** | You, by checking the repository's own record (a decision ledger, git history, current source state) — then present the finding for sign-off, don't leave it as an open question if it's actually answered. | A later, authoritative entry in the project's own continuity mechanism already states the fact you were about to ask someone about. |
| **Product / scope** | The team member who owns "what does done mean for this feature" — usually engineering/product leadership. | The question is about definition-of-done, not about what the code or ledger currently says. |
| **Domain / specialist** | A named domain expert (financial, legal, medical — whatever the project's actual specialist role is). | The question requires interpreting the *meaning* of a threshold, policy, or domain-specific judgment call, not just its implementation status. |
| **Relationship / external-party** | Whoever owns the relationship with the external team or party the document concerns. | The question is about whether an outbound ask is still active, withdrawn, or superseded by a different mitigation — this is a stance on the relationship, not a technical fact. |

**Map dependencies before routing.** If answering question B requires knowing the answer to
question A, resolve or verify A first and say so explicitly — never ask a downstream question
prematurely. Independent questions can be asked in parallel; only genuine dependencies need
ordering.

---

## 6. Dry-run planning

Before moving anything, produce a complete, file-by-file table covering every inventoried
item, with at minimum: current path, classification, proposed destination, the specific rule
that justifies it, whether it's referenced elsewhere in the repository (and by what kind of
reference — see §7), whether moving it would break anything, and a confidence level.
**Ambiguous cases are marked HOLD explicitly in this table, not silently omitted.**

Cross-check the table's bucket counts against the §2 inventory checksum before treating the
plan as final.

Propose a **target layout** and a **migration sequence**, not a single big move:
1. Establish conventions first (create the register/index structure) with zero files moved.
2. Migrate the smallest, highest-confidence, zero-coupling batch as a proof of concept.
3. Validate thoroughly (§10) before touching anything else.
4. Expand to larger clean batches once the mechanism is proven.
5. Only after all clean batches are done, revisit HOLD items — one resolved question at a
   time, each with an explicit decision recorded before the corresponding file moves.

State a rollback plan (usually trivial if every move preserves history and nothing outside
version control depends on file location) so reversibility is established, not assumed.

---

## 7. Reference handling

Before moving anything, determine **how this repository's documents actually reference each
other** — do not assume. Sweep for both patterns:

- **Bare-name citations** (a filename mentioned in prose, with no path) — moving the file does
  not break these; they were never location-specific. Consider adding a short "(now in
  `<location>`)" discoverability note, but it is not required for correctness.
- **Literal path citations** (a citation that includes the actual directory path) — these
  **do** become wrong after a move, even if nothing programmatically resolves them, because
  they now assert a false fact. These require an actual correction, in the same change as the
  move.
- **Real hyperlinks** (markdown relative links, or anything resolved by tooling) — check these
  most carefully; a broken hyperlink is the most visible failure mode and the easiest to
  verify mechanically (does the target path exist on disk after the move?).

**Draw a hard line between a live index/entry-point and a historical narrative record.** A
decision ledger, changelog, or dated report describing "what was true when this was written"
is not retrofitted after a move — its citations stay exactly as written, because rewriting them
would misrepresent what the record actually said at the time (see §8's immutability rule). A
current, still-maintained entry point (a README, a migration plan actively being executed, a
machine-readable index) **is** corrected, because its job is to be accurate *now*.

When a citing location is itself source code (a docstring or comment naming a doc file): this
is still movable, and rarely breaks anything functionally (comments are not resolved paths at
runtime) — but update the comment in the same commit as the move regardless, and run the full
test suite afterward, not just a documentation check, since this is the one place a
documentation move touches code.

---

## 8. Historical-repository preservation policy

When §1 identified a predecessor repository (not just a predecessor *document*), apply a
**symmetric marker requirement**:

1. **In the predecessor itself:** an unambiguous, additive marker at its own first entry
   point (whatever a reader would open first — its README, its agent-instructions file)
   stating: it is superseded/historical; it is retained for historical methodology,
   implementation, or decision traceability; it is **not** authoritative for current
   decisions; and it names the current canonical location by name and path.
2. **In the current, canonical repository:** a lineage reference, reachable from its own entry
   point, enumerating every known predecessor and its non-authoritative status.

**Both directions are mandatory, not optional.** A marker only in the current repo doesn't help
a reader who enters through the predecessor directly (e.g., because it shares a very similar
name, or appears first in a directory listing) — which is the actual failure mode this guards
against. Do not skip either direction because the other "seems sufficient" — a predecessor
found without a matching lineage entry in the current repo, or a current repo whose lineage
reference doesn't yet name a known predecessor, is an incomplete application of this policy,
not a lighter valid variant of it.

**This is a standing invariant, not a one-time cleanup.** Any newly discovered predecessor —
found later, during unrelated work — must receive both markers before that discovery is
considered closed, not just reported and left.

**Once a predecessor relationship is established, applying its markers is systematic, not a
fresh governance decision each time.** §1 already routes *whether something is a predecessor
with authority implications* to the appropriate owner when that relationship itself is
uncertain. Once that relationship is settled — for a specific fork, branch, or version — a
newly discovered sibling of the same, already-established lineage (e.g., a `v0` turning up
after `v1`/`v2` were already confirmed predecessors of the same lineage) does not need its own
separate governance decision to receive the same two markers; it inherits the established
classification. A fresh decision is only needed when the *new* candidate's relationship to the
current repository is itself unclear — not merely because it hasn't been individually
discussed yet.

**Immutability applies to the substance, not the marker.** Never rewrite, delete, or
retroactively relabel a predecessor's actual historical content (its design docs, decision
trails, implementation notes) to match current terminology or conclusions. The marker is
additive — a clearly bounded notice at the entry point — never an edit to the history it
points at.

---

## 9. Incremental migration mechanics

- Execute one batch at a time. Confirm the previous batch's validation (§10) before starting
  the next — do not queue multiple unvalidated batches.
- Every move should be a pure rename where the tooling supports it (preserves history,
  produces a zero-diff move that's trivial to verify).
- Update only the register/index and the specific references identified in §7 as needing it.
  **Do not fold unrelated cleanup, unrelated stale-reference fixes, or unrelated file edits
  into a migration batch** — even when you notice something else that's wrong nearby. Flag it
  separately.
- Stop and report after each batch. Do not proceed to the next batch without explicit
  confirmation, especially the first batch that touches live source code rather than pure
  documentation.

---

## 10. Validation (after every batch, no exceptions)

- Confirm every moved file is present at its new location and absent from the old one.
- Confirm the register/index has exactly one entry per moved file — no more, no fewer.
- Run the actual test suite (not just a documentation lint) whenever a batch touches anything
  referenced from source code. A pre-existing, unrelated failure baseline should be
  established once and compared against on every subsequent batch — don't let a
  batch's validation get conflated with an unrelated flaky or already-broken test.
- Sweep for dangling references using the distinctions from §7 — a hit inside a historical
  narrative record is expected and correct; a hit inside a live index or a real hyperlink is a
  defect to fix.
- Confirm the moved evidence location has not itself become a second "looks current" source —
  spot-check that nothing in it reads as a live instruction or an active gate.

---

## 11. Count reconciliation

After every batch, and especially before declaring the whole effort complete, recompute:
**does every bucket's count, summed together, still equal the original inventory checksum
from §2?** If not, find the specific missing or double-counted file before proceeding — do
not average the discrepancy away in a summary sentence. A plan's own prose-summary counts are
not authoritative; the actual table rows (or actual moved-file counts, verified by listing the
target directory) are. Treat any mismatch between a written summary and the literal file count
as a defect to find and fix, not a rounding error.

---

## 12. Formal closure

The effort is only closed when:

- Every inventoried file has a final, recorded disposition (moved, or explicitly kept current,
  or explicitly still HOLD with a named reason).
- The register/index states, in one place, that migration is complete and how many items are
  in each bucket.
- Zero files remain in an ambiguous, undocumented state at the shared root.
- Every genuinely unresolved HOLD question has been routed to its correct owner (§5) with the
  supported alternatives and consequences stated — not silently decided, not left to rot
  without a named next step.

A HOLD item resolved by an explicit ruling (from whoever actually owns that decision type) is
then executed as its own small batch, validated the same as any other, and the closure
statement updated.

---

## Anti-rules

These are not soft preferences — violating any of them reintroduces the exact failure mode
this skill exists to prevent.

- **Never move files in bulk without per-file classification first.** A directory-wide
  "archive everything old" pass is exactly how genuinely current material gets buried and
  genuinely closed material gets left looking live. Classify every file individually, even
  when a whole cluster ends up with the same disposition.

- **Never silently resolve a HOLD.** If a file's status is genuinely ambiguous, it stays HOLD
  and gets routed to the right decision-owner (§5) — it does not get moved on a best guess
  because the batch would otherwise be "almost done." An unresolved question left visibly open
  is always better than a wrong disposition presented as settled.

- **Never rewrite historical evidence for cleanliness.** A dated, closed record's citations,
  claims, and conclusions are written as of when it was produced. Correcting its wording,
  its filenames, or its path references to match a later convention destroys its value as a
  record of what was actually true or believed at the time. The only acceptable edit to
  historical evidence is an additive, clearly-bounded status marker at its top — never a
  rewrite of its body.

- **Never equate "implemented" with "integrated."** Code that exists, is tested, and has zero
  production callers is not the same claim as a feature being live. Treat "the module exists
  and passes its own tests" and "this is wired into the system's actual execution path" as two
  separate facts, and never let documentation collapse the distinction — this is a common,
  specific way a status document goes stale without anyone noticing.

- **Never equate a mitigation with the closure of the thing it mitigates.** A workaround,
  detection mechanism, or reconciliation layer built to cope with an unresolved defect is not
  evidence that the underlying defect was fixed. If both a defect record and its mitigation
  exist in the same repository, state the distinction explicitly in the mitigation's own
  documentation — do not let the mitigation's existence imply, by proximity, that the original
  problem is closed.

- **Never treat canonicality as requiring physical centralization.** A predecessor repository,
  branch, or document does not need to be deleted, merged, or moved into the current
  repository to be correctly non-authoritative. Marking it clearly (§8) is sufficient and
  correct; conflating "make it canonical" with "make it disappear or merge it in" both
  destroys history unnecessarily and is usually not even asked for.
