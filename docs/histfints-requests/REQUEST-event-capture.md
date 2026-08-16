# REQUEST — Stop discarding the corporate-action payload already being fetched

**Type:** Application logic, plus one small additive table.
**Filed:** 2026-08-15 · **From:** Research Workbench
**Companion filings:** `DEFECT-F009.md` · `REQUEST-tranche2-migration.md`

---

## The ask, in one sentence

`providers/yahoo_finance.py` requests split and dividend events on **every single fetch**
and the response parser never reads them. **Parse and persist what already arrives.**

---

## Evidence

Grepping `src/` for `events|dividend|adjclose|splits` returns exactly **one** hit:

```python
# providers/yahoo_finance.py:63
"events": "div,splits",
```

`_to_records()` reads only `timestamp` and `indicators.quote[0].{open,high,low,close,volume}`.
`chart.result[0].events` is never touched. No `splits`, `dividends` or `corporate_action`
table exists in the schema.

So the payload is requested, transmitted, paid for in bandwidth, and dropped on the floor —
on every fetch since the adapter was written.

---

## Why this is unusually cheap

- **No new network call.** The request parameter is already being sent.
- **No new dependency**, no new provider, no new credential.
- **No blocked decision.** Nothing else in either companion filing waits on this, and this
  waits on nothing.
- **Contained.** One field parsed in `_to_records()`, plus somewhere to put the result.

---

## The one design fork — and a recommendation

**Dedicated table, not an extension of `entity_change_log`.** The recommendation rests on
what these records *are*, not on convenience.

`entity_change_log` records **changes to entities inside this system**. A split or dividend
is not that. It is an **observed fact about the outside world, reported by a provider** —
the same epistemic status as a row in `observation`: recorded, not interpreted. Observations
do not live in the change log, and events should not either.

Four supporting reasons:

1. **Query pattern.** Events need range queries by series and date. A change log is
   append-often, read-rarely.
2. **Structure.** A split carries a numerator and denominator; a dividend an amount and
   currency. Flattening those into generic log columns loses type safety and pushes the cost
   onto every future consumer.
3. **Coupling.** Extending the change log ties event capture to an audit mechanism that will
   evolve for unrelated reasons.
4. **Provenance.** Events want `provider_assignment_id` and `import_run_id` — the same chain
   `observation` already carries. Natural on a dedicated table, awkward on a log.

The reuse argument for `entity_change_log` is also weaker than it appears: it is hardcoded to
`entity_type='ProviderSymbol'`, so it requires schema and code change either way.

---

## Suggested shape — offered, not prescribed

```
provider_event
    id
    provider_assignment_id   FK   -- who reported it, for which Series
    import_run_id            FK   -- provenance, mirroring observation
    event_type                     -- CHECK ('SPLIT','DIVIDEND', ...)
    occurred_at                    -- the provider's own date for the event
    numerator / denominator        -- splits
    amount                         -- dividends (no currency — see below)
    raw_payload                    -- the provider's representation, unaltered
    UNIQUE (provider_assignment_id, event_type, occurred_at)
```

**On naming.** `provider_event` may read better than `corporate_action`. The former says
*"this is what a provider told us"*; the latter implies a reconciled domain fact. Since
reconciliation is explicitly a separate job with a different owner, a name that marks this as
the raw-capture layer is worth the two extra characters.

**No `currency` on the event row — deliberately, not by oversight.** A real Yahoo dividend
event carries exactly two fields:

```json
{ "amount": 0.108929, "date": 1391697000 }
```

There is no per-event currency. The instrument's currency lives one level up on
`chart.result[0].meta.currency` — a different part of the response entirely. Putting a
`currency` column on this table would either sit permanently null or be back-filled from
elsewhere at capture time, and that second option is **interpretation**, on a table whose
entire purpose is to record what the provider reported as reported. A consumer needing the
currency should resolve it from the instrument.

**`raw_payload` earns its place.** Whatever fields are parsed today, the provider's own
representation is the only thing guaranteed not to lose information the reconciliation layer
later turns out to need.

**Separately, and not part of this request:** `meta.currency` is itself provider-reported and
currently discarded, while `series.currency` is hand-entered. Where they disagree, one of the
two is wrong — a free cross-check against mis-entered Series. Same family as this filing, but
a different concern, so it belongs in its own note rather than bundled here.

---

## Two operational notes

**Idempotency.** Because incremental imports re-request a trailing window, the same event will
arrive repeatedly. The `UNIQUE` constraint above plus an upsert handles it — mirroring how
`observation` already deduplicates on `(series_id, observed_at)`.

**Historical events need a backfill pass, and there is a free one available.** A parse-only
fix captures events **going forward** from the trailing window; everything before that stays
empty. Yahoo returns events for whatever range is requested, so a full-range re-fetch recovers
the complete history.

That is the *same operation* proposed as remedy R1 in `DEFECT-F009.md`. **One full-range
re-fetch would simultaneously repair the scale discontinuities, surface them as correction
rows, and backfill the entire event history.** If R1 is adopted, this filing's backfill is
free.

---

## What is *not* being asked

- **Not reconciliation.** Deciding what a captured event *means* for a stored value —
  adjustment, rebasing, ratio application — is a separate job on the consuming side. This
  filing asks only that the raw record be kept.
- **Not FRED vintages or BYMA `underlying_ratio`.** Both are the same shape as this ask —
  data the provider offers and the adapter discards — but each is its own decision with its
  own justification, and bundling would tie this one's fate to theirs.
- **Not a schema change to `observation`.** Nothing here alters existing data or semantics.
