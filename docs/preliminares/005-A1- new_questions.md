That brief is more useful than an answer to question 1 — it settles several others (3: you're a reader over a local store; 9: macro and FX already *are* Series; 2: your data cost is effectively zero because your providers are free-tier). But it also breaks parts of the spec in ways worth naming now, while the document is still cheap to change.

## What the brief settles

Your store is a **clean historical time-series warehouse**. That's the strongest possible foundation for §9 (chart), §11 (performance), §12 (historical data) and §10 (comparison) — roughly 70% of V1 is buildable today against `observation` alone.

It is *not* a research database. There are no fundamentals, no corporate actions, no quotes, no relationships between Series. Everything in §13–§23 has no source. That's fine — but the spec currently reads as though the data exists.

## Six findings, in order of severity

**1. Observations cannot be traced to a provider. [most serious]**

`observation` carries `series_id`, `observed_at`, `value`, OHLC — and no foreign key to `import_run` or `provider_assignment`. The brief suggests joining through those tables "if provenance matters," but there's no join key: you'd be correlating by timestamp, which is inference, not provenance. And because a Series can be served by different providers over time via fallback, the inference is exactly wrong in the cases that matter most.

This makes §12.1 (per-row Provider / Provider Symbol / Import run) and **AC-09 unbuildable**, which is awkward given that provenance is your stated differentiator (§44).

The fix is small and belongs in the pipeline, not the UI: a nullable `import_run_id` on `observation`, backfilled where inferable and left `NULL`/`UNKNOWN` elsewhere. Honest gaps beat fabricated lineage.

**2. `UNIQUE(series_id, observed_at)` plus a single `value` erases the raw/adjusted distinction.**

You can store one number per instant. So: is that number the raw close or the adjusted close? If your Yahoo path stores adjusted values, your history silently rewrites itself on every ex-dividend date, and your `correction` table will spike on those dates for reasons that have nothing to do with data errors. Worse, if a Series is spliced across providers with different adjustment conventions, you get an artificial jump at the handover with no marker.

AC-06 requires the chart to state its "adjustment basis." Today that's unknowable from the schema.

**3. Corrections overwrite, so the store is not bitemporal.**

"You never need to reconcile `correction` yourself; `observation.value` is always the current number" is a fine design for a pipeline and a problem for a provenance-first research tool. §32 promises to answer "where did this number come from" — but not "what did this chart look like when I made that decision in March."

Whether that's recoverable depends entirely on how complete `correction` is (see Q39).

**4. There is no quote, no session, no current price.**

§7's header (live price, change, market status), §7.1's seven session states and **AC-03 (regular vs extended hours never silently mixed)** have no backing data. `observation` has a UTC timestamp and nothing that tags a session.

**5. No relationships and no corporate actions.**

CEDEAR ↔ underlying (§6), dual listings, index membership, benchmark assignment (§11.1): nowhere to store any of it. Dividends, splits and CEDEAR ratio changes (§20): same. This is the largest genuinely *new* domain the Workbench must own, and it forces the architectural decision in Q37 below.

**6. Value-only Series are a first-class case, not an edge case.**

FRED/ECB series have `value` and NULL OHLC. So does anything you compute as a ratio. §P2's instrument-awareness table doesn't cover "no OHLC → no candlestick, no volume, no intraday" — and for you that's a large slice of the universe, not an exception.

Also worth saying plainly: the database is proprietary, the *data* isn't. Yahoo, Stooq and Alpha Vantage terms bind on redistribution. Irrelevant if this stays on your team's machines; decisive the moment anyone talks about sharing it.

## Next questions

**Architecture**

37. **[blocking]** Where do Workbench-owned data live — Series relationships, corporate actions, watchlists, peer sets, benchmark assignments, fundamentals? Three options: (a) new tables in the same SQLite file, (b) a second "workbench" database that references `series_id` across the boundary, (c) extend HistFinTS proper. (b) preserves your read-only rule and lets the two evolve independently; it costs you cross-database joins and referential integrity. Which do you want?

38. **[blocking]** Can you change the HistFinTS pipeline and schema, or is it frozen? Finding 1's fix requires a migration. If it's frozen, provenance in V1 degrades to Series → provider *set*, and AC-09 must be rewritten to match.

39. Does `correction` log every overwrite including OHLC and volume, and does it record which `import_run` did the overwriting? If yes, you can reconstruct as-of history and Finding 3 dissolves. If it only tracks `value`, you'll need to decide whether reproducibility is worth the schema change.

40. Does the pipeline ever write while the Workbench is reading? If so: WAL mode, or read from a snapshot copy?

**Prices and adjustment**

41. **[blocking]** Today, is `observation.value` raw or adjusted — and is it consistent across providers? Please check one dividend-paying US equity across a past ex-date before answering; the intent and the reality often differ here.

42. If it's adjusted, do you want V1 to (a) accept mutable history and label it clearly, or (b) move to storing raw prices plus a corporate-actions table you own, adjusting on read? Option (b) is the only one compatible with your provenance ambition — and it pulls dividends and splits *into* V1, contradicting §35.

43. What `configured_interval` values are actually in use? If everything is daily, then 1D and 5D must come out of the V1 chart (§9.1) — §9.2 forbids fabricating intervals, and rightly so.

44. Is a live-quote path in scope at all, or does V1 honestly display "Last close · 2026-08-14 · Stooq"? I'd argue for the latter: it's cheaper, more truthful, and it's what a provenance-first tool should look like.

**Identity and types**

45. **[blocking]** How do `series_type` (STOCK/ETF/BOND/CURRENCY_PAIR) and `instrument_subtype` map onto the capability matrix §P2 needs? Specifically: is a CEDEAR a `STOCK` with subtype `CEDEAR`, and is an FX-implicit ratio a `CURRENCY_PAIR` or something else?

46. **[blocking]** Still open from last round: what individuates a Series? Are GGAL / GGALC / GGALD one Series or three in your current `series` table? Please answer from what the table actually contains, not from what it should contain.

47. Since a Series can have several providers ranked by priority, and the spec's §7 header wants to show "Provider Symbol" — which one does it show when three providers back the Series? The primary, all of them, or the one that produced the displayed value (which per Finding 1 you may not know)?

**Scope**

48. Confirm the V1 Statistics decision. Given no fundamentals exist, I'd propose V1 shows only price-derived statistics — 52-week high/low, 50/200-day MAs, average volume, realized volatility, beta vs a chosen benchmark — and that market cap, P/E, EPS and yield move to V2 with the fundamentals pipeline. Agreed?

49. Do you accept the V0 proposal from Q36 — search, identity, EOD chart, historical table with provenance-carrying export, one comparison, nothing else?

Answer 37, 38, 41, 45, 46 plus 39 and 43, and I can redraft §7, §12.1, §13, §30–§32 and the whole V1/V2 boundary into something your team can estimate against the database you actually have.