# CLAUDE.md

@AGENTS.md

The complete instruction set for this repository lives in `AGENTS.md` — read it. This file
holds only what's specific to working here as Claude Code, on top of that.

## Skill discovery

The `documentation-lifecycle` procedure `AGENTS.md` names is discovered here automatically as
a native user-level skill (no project-local copy, no path to hard-code) — canonical source at
`../_shared-standards/skills/documentation-lifecycle/SKILL.md`, discovered through the
`~/.claude/skills/documentation-lifecycle` junction. This note only covers *how it's found*
here, since that mechanism is Claude Code-specific — a different agent reads the canonical
file directly instead.

## Subagents

`.claude/agents/spec-interrogator.md` — a subagent for continuing the requirements-
interrogation process (one question at a time, verify-before-log, D-009/D-009b discipline).
Use it when a design question needs the same rigor as the original review, not for routine
coding. Claude Code-specific; no equivalent noted for other agents.

## Memory

A closed decision, incident, or resolved investigation's operative conclusion belongs in this
session's persistent memory store, per whatever memory discipline this project uses, not as a
new standalone doc invented for the occasion.
