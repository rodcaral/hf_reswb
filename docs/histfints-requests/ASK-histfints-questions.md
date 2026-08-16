# QUESTIONS — three items, no work requested

**Type:** Questions only. No code, no schema, no investigation beyond checking what already exists.
**Filed:** 2026-08-15 · **From:** Research Workbench
**Companion filings:** `DEFECT-F009.md` (defect) · `REQUEST-basis-factsheet.md` (investigation)

> These are deliberately separate from the two companion filings so they can be answered
> immediately without waiting on either. Question 1 in particular is currently blocking a
> schema-change proposal on our side.

---

## 1. Does `correction` record which `import_run` performed the overwrite? *(blocking)*

Two parts:

- **a.** When a correction row is written, is the `import_run` that performed the
  overwrite recorded — or only the old and new values?
- **b.** Does `correction` cover every field, or only some? Volume and close are known to
  be logged; the coverage of `open`, `high`, `low` and any others is unconfirmed.

**Why it blocks us.** We are preparing a single batched migration proposal covering
observation provenance. Whether that proposal needs to extend to `correction`, or can
stop at `observation`, depends entirely on this answer. We would rather send one
well-scoped migration than two.

---

## 2. After a MERGE, does the archived Series row point at the survivor?

When two Series are deduplicated and the absorbed row is archived (`archived_at` set),
does that row carry a reference to the surviving `series_id`?

**Why it matters.** We store `series_id` as an application-level reference across the
database boundary. We understand ids never dangle, since Series are never hard-deleted —
so our defensive check is on `status`/`archived_at` rather than existence. But detecting
that a stored reference has gone stale is only half the problem. Without a pointer to the
survivor, a downstream watchlist or peer set can *notice* it is stale and cannot *repair*
itself; it would have to be re-resolved by hand.

If no such pointer exists today, that is useful to know as-is — we can design around it.

---

## 3. Where did the `ratio` value on series 11305 (Apple CEDEAR) come from?

Specifically:

- Was it hand-entered during resolution, carried from a provider field, scraped, or
  inferred?
- Is it associated with any effective date?
- Is it understood to be current as of today, or as of some earlier moment?

**Why we are asking.** Argentine regulation (CNV Normas, Título II, Cap. VIII, as
substituted by RG 1142/2026) makes CEDEAR conversion ratios explicitly **variable**:
issuers report the ratio quarterly, and a change requires a Prospectus Supplement with an
effective date. Ratio history is published through the CNV's AIF.

A single undated scalar therefore cannot be correct for all history, and we are about to
build a headline calculation on top of this field. We would rather establish its
provenance now than discover later that we were computing a flagship number from a value
of unknown origin.

No change is being requested here — we need to know what the value *is* before proposing
what it should become.
