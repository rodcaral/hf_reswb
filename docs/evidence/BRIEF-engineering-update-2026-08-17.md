# Brief — F-009 Evidence Consumption: Financial-Domain Review Outcomes

**For:** development team / software engineer
**Date:** 2026-08-17
**Related:** D-035 (freeze), D-036 (this review), A-015, `SPEC-f009-evidence-consumption.md`

---

## Why this brief

The F-009 evidence-consumption increment was frozen except for defects (D-035) pending two
things: Stage 2 validation once HistFinTS applies its migrations, and a financial-domain
review of whether the reconciler's design decisions actually hold up. The second one just
came back. **Nothing here lifts the freeze or requires new code right now** — this is a
status update, not a new work item.

---

## What was sent to the financial advisor

Three questions, framed around the frozen increment's open items:

1. **Q-066** — is the three-verdict vocabulary (`explained` / `not explained` /
   `insufficient evidence`) actually sufficient for V0's research questions, and what should
   a "not explained" or "insufficient evidence" verdict *do* downstream — the system
   currently produces the verdict but defines no consumption behavior after it.
2. **Validation population** — is validating the reconciler against Yahoo events / FRED
   vintages the right test, given this project's differentiating universe is CEDEARs, not
   US equities or macro series.
3. **Detector calibration** — is the 20% step threshold / 15–60 day persistence window a
   financially meaningful definition of a discontinuity, or an arbitrary placeholder.

---

## What came back — three decisions, now logged as D-036

**1. A verdict quarantines the affected time span, not the whole Series.** Precedent:
CEDEAR ratio changes with no dated ratio are already handled by detect-and-quarantine
(D-015), not by discarding the Series. Generalized into a table:

| Verdict | Downstream behaviour |
|---|---|
| Explained | Analysis may proceed, normal diagnostics |
| Not explained | Flag and quarantine the interval for continuity-sensitive analyses |
| Insufficient evidence | Don't treat the interval as validated; proceed only if the method doesn't depend on it |

The consumer, not the finding, decides whether a boundary falls inside its analysis window.
**No quarantine mechanism exists yet — this is a spec for future work, not a build.**

**2. Yahoo/FRED validate the general mechanism, not CEDEAR-specific reconciliation.** CEDEAR
ratio changes have a cause (local tradability-driven changes) that's invisible to any
non-Argentine source — confirmed by the AAPL CEDEAR case (2024-01-24). A CNV/BYMA
ratio-event evidence path is required before any CEDEAR verdict from this reconciler can be
called authoritative. **This does not block continued reconciler work on Yahoo/FRED evidence
— it blocks presenting a CEDEAR verdict as trustworthy until that path exists.**

**3. The 20% step threshold is a candidate filter, not a financial definition.** The
project's own detector-validation history already proved move size alone doesn't work (a
+19.1% move that was a market-wide FX shift, a −18.3% move that reverted, a −49.4% move that
was real and persisted). Persistence + cross-pair residual is the validated discriminator.
The current calendar-day implementation stays labeled **provisional** until Q-027 (trading
calendar) lands — this was already true, now it's explicit everywhere.

**Governing principle, worth knowing for anything built on top of this:** a verdict
describes the evidence state; it does not decide whether an analysis is permissible. That
decision belongs to whatever analytical method consumes the finding.

---

## What's already been done — no engineering action needed

- `DECISIONS.md` D-036 logged; Q-066 closed.
- `SPEC-f009-evidence-consumption.md` updated: new §2.3 (downstream consumption model,
  specified, not built), new §1.2a (CEDEAR validation-gap statement), §4.2 reinforced
  (threshold framing).
- `discontinuity_detector.py` docstring updated to state the candidate-filter framing
  explicitly, in the code, not just in docs.
- **No reconciler logic changed.** Tests re-run after every doc/comment edit: 5/5 still
  passing.
- Committed to `main`: `8d237cf`.

---

## What this actually changes for engineering

- **Right now: nothing.** The D-035 freeze holds. No new code to write.
- **When Stage 2 runs** (gated on HistFinTS's response to
  `REQUEST-apply-migrations-0011-0013.md`), it runs against the exact same `classify()`
  logic — this review didn't touch it.
- **Two new backlog items exist, neither scheduled:**
  - Build the downstream quarantine/consumption mechanism (SPEC §2.3) — genuinely new
    scope, not something to start under the current freeze.
  - Build a BYMA/CNV ratio-event evidence source (SPEC §1.2a) before any CEDEAR verdict
    ships as authoritative — independent of, and not blocking, further Yahoo/FRED-based
    reconciler work.

---

## Still open, unchanged by this review

- Stage 2 validation — waiting on HistFinTS, not on anything here.
- The freeze (D-035) stays in effect except for defects.
