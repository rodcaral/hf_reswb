# Workbench Documentation

A lightweight entry point into `docs/` — not a restructuring of it. Everything that already
lived here stays exactly where it is; this file only adds a reading order and one convention.

## Reading order — start here for current-state understanding

1. [`HISTFINTS-BRIEF-v2.md`](HISTFINTS-BRIEF-v2.md) — the corrected, current-state technical
   reference for HistFinTS (schema facts, known defects, adjustment basis, V0 data reality).
   Read this before writing any code.
2. [`DECISIONS.md`](DECISIONS.md) — the full specification and reasoning log. Every
   architectural decision, open question, known defect, and queued spec amendment, each with
   evidence, in reverse-chronological order. This is the project's actual continuity
   mechanism across sessions — when in doubt about *why* something is the way it is, this is
   where the answer lives.
3. [`SPEC-panel-eligibility.md`](SPEC-panel-eligibility.md) — the converged spec for
   panel-derived analytics.
4. [`SPEC-f009-evidence-consumption.md`](SPEC-f009-evidence-consumption.md) — the design note
   for the F-009 evidence-consumption/reconciliation capability.
5. [`histfints-requests/`](histfints-requests/) — filings sent to (or pending for) the
   HistFinTS team, and cross-repository review/status reports. Each filing is independently
   dated; there is no separate reading order within this directory.

Everything else in `docs/` is dated, topic-named supporting material — investigations,
evidence packages, design increments, closure records. It is not indexed separately from this
list; find it by filename/date or by what `DECISIONS.md` links to when describing the work
that produced it.

**Known gap, not fixed here**: `CLAUDE.md`'s own "Where things are" table names
`docs/KB-argentine-instruments.md`, which does not exist under that filename in the current
tree — flagged for whoever next touches that table, not corrected as part of this
documentation-entry-point change (out of scope for a minimal addition).

## Convention — marking evidence anchored to a sibling repository

Many documents in `docs/histfints-requests/` (and elsewhere) make claims about the current
state of `histfints-v3` — a separate, independently-changing git repository. That state can
drift after the claim was written, without anything in *this* repository changing to signal
it. Mark any such claim with a one-line anchor near the top of the document (right after the
existing `**From:**`/`**To:**`/`**Date:**` header block), in one of these two forms:

- **If the sibling repo has version control** (as `histfints-v3` now does):
  `**Cross-repo anchor:** histfints-v3 @ <commit-hash> (<short description>), verified <YYYY-MM-DD>.`
  Example: `**Cross-repo anchor:** histfints-v3 @ 1ce71c1 ("Apply the four-class documentation
  retention model"), verified 2026-08-26.`
- **If the sibling repo has no version control at the time of writing**:
  `**Cross-repo anchor:** histfints-v3, state as read on <YYYY-MM-DD> — no commit hash available (no VCS at that time).`

Either form makes explicit what this session has repeatedly had to rediscover the hard way:
that a claim about another repository's code or behavior is only as current as the moment it
was checked, and must be re-verified — not assumed — before being trusted again. This is a
per-document annotation, not a new index, schema, or directory: nothing else about how
`docs/histfints-requests/` is organized changes.

Documents written before this convention was established are not retrofitted — apply it going
forward.

## Cross-project standard

This project's documentation practices follow the shared **General Documentation Discipline**
at `../../_shared-standards/GENERAL_DOCUMENTATION_DISCIPLINE.md` — the canonical copy; not
duplicated here. `DECISIONS.md` above is this project's continuity-mechanism implementation
under that standard (§1); the numbered items in `docs/` are this project's durable-evidence and
closed-historical record under the standard's four-class lens (§2).
