# `CLAUDE.md`'s `docs/KB-argentine-instruments.md` Reference — Investigation

**Date:** 2026-08-26
**From:** SDT Workbench
**To:** SE / PO
**Status: read-only investigation. `CLAUDE.md` NOT edited — the intended target is not
unambiguous from repository evidence, so no correction was made, per instruction.**

**Cross-repo anchor:** N/A — this investigation is entirely within `workbench`'s own git
history, no sibling-repo claim made.

---

## Finding: the file was deleted, not renamed or moved

`docs/KB-argentine-instruments.md` existed from this repository's very first commit
(`5b0e2e0`, "Initial commit: HistFinTS Research Workbench docs and spec" — its own message
explicitly lists *"Argentine instruments KB"* among the docs created) and was **deleted** in a
later commit, `8ba5a207` ("F-009 evidence-consumption increment: D-032/D-033/D-034, spec, and
first Workbench implementation," 2026-08-17).

Checked directly, not inferred:
- `git log --diff-filter=D -- docs/KB-argentine-instruments.md` shows exactly one deletion
  event, in `8ba5a207`, `delete mode 100644 docs/KB-argentine-instruments.md`.
- No rename was recorded (`git log --diff-filter=R` finds nothing matching), and no file with
  similar content was added in that same commit.
- That commit's own message says nothing about the Argentine-instruments KB specifically — it
  is entirely about the F-009 evidence-consumption increment, with one vague catch-all line
  ("Also folds in prior consultant-package updates... and other pending docs/workspace
  changes") that does not name this file or explain its removal.

## Was its content superseded elsewhere? Checked, not assumed — no

Recovered the deleted file's full original content (`git show 5b0e2e0:docs/KB-
argentine-instruments.md`). It was a substantive, ~2020-08-15-dated reference brief: BYMA/CNV/
BCRA/ALyC market-structure terminology, the multiple-simultaneous-exchange-rate structure
(Oficial/MEP/CCL/Blue, the *canje* spread), regulatory citations (CNV Normas Título II Cap.
VIII, RG 1142/2026, RG 1095/2025), and explicit modelling guidance ("an implied exchange rate
is not a single number... all three [rate type, derivation instrument, date] must be recorded
alongside").

Searched the current repository for this specific content: `DECISIONS.md` mentions "CEDEAR"
126 times and "BYMA"/"MEP" many more, but scattered across individual technical decision
entries about specific series/providers — not as a consolidated market-structure reference.
None of the file's distinctive terms (*"Contado con Liquidación"*, *"dólar bolsa"*,
*"multiple-dollar"*) appear anywhere else in `docs/`. **The standing background-knowledge
content this file provided does not exist anywhere else in the current repository.**

## Why this is reported as ambiguous, not corrected

Repository evidence answers *what happened* (deleted, not renamed, not superseded) but not
*what should happen now*, which is a decision, not a fact to be read off the commit history:

- If the deletion was **intentional** (e.g., the standing knowledge was judged no longer needed,
  or superseded by domain knowledge now held elsewhere outside this repo), the correct fix is
  removing `CLAUDE.md`'s dead reference.
- If the deletion was **incidental** (swept up in an unrelated commit's "other pending
  docs/workspace changes" line, as the commit message's own vagueness suggests is at least
  possible), the correct fix is restoring the file — verbatim from git history, or refreshed
  for the ~year-plus that has passed since its 2026-08-15 compilation date (its FX-rate figures
  in particular are explicitly dated "as of mid-August 2026" and would need re-verification
  before being trusted as current if restored as-is).

Neither of these is determinable from the repository alone, and per instruction, no replacement
is invented and `CLAUDE.md` is left unedited pending a decision.

---

## Options, named for PO/SE — not recommended, not decided here

1. **Restore verbatim** from `git show 5b0e2e0:docs/KB-argentine-instruments.md` — fastest, but
   reintroduces content whose currency (FX rates, regulatory citations) has not been checked
   since 2026-08-15.
2. **Restore and refresh** — same file, with its dated figures/citations re-verified against
   current sources before being trusted again.
3. **Remove the `CLAUDE.md` reference** — if the standing knowledge is no longer needed in this
   repository, or is maintained elsewhere.
4. **Leave as-is** — the dead reference stays, documented as a known gap (as already noted in
   `docs/README.md`'s "Known gap" line from the prior documentation-entry-point change).

**No file modified in producing this investigation.**
