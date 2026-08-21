# A–F Remediation Analysis Update — DFA Ruling on Class D

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: read-only update. No repair SQL generated or executed. No observation, FK,
provenance field, schema, or calibration/policy state altered. The seven Class-C rows remain
a separate, deliberately unchanged population — not merged with D's disposition.**

---

## Evidence

Restated from `EVIDENCE_MATRICES_B_D_CLASSC_IDENTITY_2026-08-20.md`, not re-derived:

- All seven D pairs' current and proposed targets share issuer name, currency, instrument
  class, adjustment basis, and — the strongest signal — identical provider and identical
  provider-side symbol (Yahoo Finance, plain ticker).
- Each current target's value is bit-identical to its own referrer CEDEAR (ratio exactly 1.0)
  from series inception through 2026-05-27, then transitions on 2026-05-28 to independently
  tracking a value close to the proposed target.
- Post-transition: 406 common dates across the seven pairs, 338 disagreeing by more than
  $0.01 — small-magnitude, consistent with intraday-vs-daily sampling difference.
- **Newly verified for this update**: each of the seven current targets has **exactly one
  incoming FK reference** — its own D-pair referrer — confirmed by direct query, zero other
  series point at any of them.

---

## Domain ruling (DFA, relayed by SE)

The seven target/referrer pairs are the same financial instrument, observed through two
different historical data regimes (pre-2026-05-28 duplicate-of-CEDEAR, post-2026-05-28
independent live tracking), with the transition date established. The 338/406 post-transition
disagreements remain **unresolved observation-level discrepancies** — not to be resolved by
majority vote, by preferring the proposed-target value as "the destination identity," or by a
general current-source preference. The 2026-05-28 extreme jump is consistent with this
established regime transition; no precise FX/equity decomposition is asserted.

**This document does not restate the ruling as a Workbench finding — it is recorded as given,
per instruction, and used only to re-evaluate technical implications below.**

---

## Technical implications for A–F sequencing

1. **D's proposed mutation is unaffected in scope.** It remains exactly seven metadata
   values (`series.underlying_series_id`), zero observation rows. The ruling clarifies *what
   the current and proposed targets are* (same instrument, different regime) without changing
   what the repoint itself does.

2. **D's pre-registered verification signal does not depend on the 338 discrepancies.** The
   F-033 statistic (15/21 pairs at exactly `1.000000000000`) is a **cross-pair consistency
   check computed against deep-history data** — it establishes that the six previously-
   circular CEDEARs' implied-FX values become identical to each other once the proposed
   (authoritative) denominators are used, a structural signature independent of the live
   post-transition window entirely. **The 338 discrepancies live in a different data slice
   (post-2026-05-28) than the one the verification statistic is computed against.** Resolving
   them is not a technical precondition for computing or trusting this statistic.

3. **A new technical fact, not previously stated**: repointing the referrer away from the
   current target leaves the current target **with zero incoming FK references** — verified
   this pass, each of the seven current targets (11342, 11348, 11349, 11350, 11351, 11352,
   11353) has exactly one incoming reference today, its own referrer. Post-repoint, each
   becomes an orphaned series still holding its full dual-regime observation history
   (thousands of pre-transition duplicate rows plus dozens of post-transition independently-
   fetched rows), referenced by nothing. This does not block D's mutation — D touches no
   observation data — but it is a consequence D's design package should state plainly rather
   than leave implicit.

4. **The regime classification does not adjudicate observation correctness**, and this
   analysis does not attempt to. Whether any specific post-transition value (current target's
   own live fetch, or proposed target's daily fetch) is the more accurate observation for a
   given date remains open, exactly as the ruling states. D's metadata fix changes which
   series is *referenced* as the CEDEAR's underlying; it does not select, prefer, or validate
   either regime's post-transition values.

---

## Can D have a verification/design package without resolving the 338 discrepancies?

**Yes — technically supportable, on the evidence above.** D's scope (seven FK values), its
verification signal (a deep-history cross-pair statistic independent of the live window), and
its rollback (trivial metadata revert, already specified in `REMEDIATION_PACKAGE_CLASS_D_
2026-08-20.md`) do not require the 338 discrepancies to be resolved first. That package's
content is **not superseded** by this ruling — it is reinforced: the ruling confirms current
and proposed target are the same instrument, which is the evidentiary premise that package's
proposed repoint already rested on.

**This is a technical determination, not a decision to proceed.** Whether D *should* execute
while an adjacent, related observation-level question (the 338 discrepancies) remains open is
a judgment this document does not make — it answers whether the package can be verified
independently of that question, not whether SE/DFA should authorize it before or after
resolving it.

---

## Remaining gates — exactly what still prevents a D mutation from being proposed for execution

1. **SE/DFA execution authorization** — not granted by this document or any prior one; the
   standing gate on every package returned so far.
2. **The newly-identified orphan consequence (§ Technical implications, item 3) has no
   disposition decision attached.** Whether the seven current-target series, once orphaned,
   should be archived, left as-is, or otherwise addressed is not answered by D's design
   package and is not created or resolved by this update — flagged as a gap in D's package
   that should be closed (with a decision, even if the decision is "leave them, no action
   required") before execution, not before verification.
3. **Contemporaneous re-confirmation of the pre-repair F-033 statistic at execution time**,
   already stated as a prerequisite in `REMEDIATION_PACKAGE_CLASS_D_2026-08-20.md` — unchanged
   by this ruling, restated because it remains a real gate, not superseded.
4. **Confirmation Class E work has not begun concurrently** — unchanged structural dependency
   (`ON DELETE RESTRICT`), restated as still applicable.
5. **The 338 discrepancies themselves remain a separate, unresolved evidence gap** — not a
   gate on D's *verification*, per the technical determination above, but this document does
   not clear them as resolved, does not propose they be ignored going forward, and does not
   fold them into D's disposition. They stand as their own open item, exactly as the ruling
   requires.

---

## Class-C's seven rows — preserved as a separate population, not merged with D

The seven previously-adjudicated Class-C rows (seven-pair episode: one crossed row per target
on 2026-05-28, value-correct, attribution finding accepted, no mutation) are a **structurally
different finding** from D's dual-regime pattern, restated explicitly per instruction:

- Class C's seven rows are a single misattributed observation each, on one specific date, on
  the *current target* series — a row-level attribution question, already resolved.
- D's finding is a *structural, whole-series* pattern spanning thousands of rows across
  nearly the entire history of each current-target series — a metadata/identity question,
  not yet resolved for execution.

Both happen to involve "historical attribution" in a loose sense, and both happen to touch
the same seven current-target series ids — but the mechanisms, populations, and resolutions
are not the same, and this document does not treat DFA's ruling on one as bearing on the
other. The seven Class-C rows remain closed and untouched by anything in this update.

---

## What this document does not do

- Does not generate or execute repair SQL.
- Does not make a remediation decision on behalf of DFA or PO.
- Does not resolve the 338 post-transition discrepancies, or propose a method for resolving
  them.
- Does not reopen or modify the seven Class-C rows' disposition.
- Does not authorize D's execution — it answers a narrower technical question (can D's
  verification proceed independent of the 338 discrepancies) and enumerates what still gates
  execution specifically.
