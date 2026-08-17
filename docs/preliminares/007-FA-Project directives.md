Yes. I would say one thing to the team, and I have **one question**.

### Message to the Workbench team

**Don't start designing the Workbench around the current HistFinTS schema. Start designing it around the financial questions the Workbench must answer.**

The work you've done so far has uncovered several important constraints—especially provider-dependent price meaning, dated CEDEAR ratios, provenance, coverage uncertainty, survivorship, and the read-only boundary. Those are necessary foundations. But they should now become **constraints on the Workbench design**, rather than becoming the design itself.

In particular, I would establish this sequence:

> **Financial question → analytical result → required evidence/data → calculation → diagnostics → UI**

rather than:

> HistFinTS table → query → calculation → screen.

This matters because the same HistFinTS observation can be appropriate for one financial question and inappropriate for another. For example, a split-adjusted, dividend-unadjusted price is a reasonable input for a price-return calculation, but it is not sufficient to answer a total-return question.

The panel specification is already moving in this direction: it doesn't merely say "calculate an implied FX series"; it asks whether the resulting cross-section is sufficiently coherent to justify publishing the result, and it requires the result to expose its membership, exclusions, dispersion and provenance. 

### The question I'd put to the team

**What are the first 3–5 financial questions that `hf_reswb` must answer for Argentine assets?**

Not features. Not screens. Not database entities.

Actual questions, phrased as a user would ask them.

For example, as placeholders—not proposals:

* *What ARS/USD exchange rate is implied by the current CEDEAR market, and how reliable is that estimate?*
* *Has the price relationship between this Argentine-listed instrument and its underlying changed?*
* *How has this Argentine asset performed relative to an appropriate benchmark over a specified historical period?*
* *Is this apparent price movement real, or could it be explained by a corporate action, ratio change, stale quotation, or data problem?*

I would want the team to produce its own list before we design the corresponding domain objects.

There is a particularly important reason for doing this now: **the current V0 is still heavily shaped by what HistFinTS happens to contain**—mostly US equities/ETFs, macro, and a small manually verified Argentine/CEDEAR set.  That is a data-availability fact, **not necessarily the desired financial scope of the Workbench**.

So my advice is:

> **Don't let today's HistFinTS inventory define tomorrow's Research Workbench. Let the financial questions define what the Workbench needs from HistFinTS.**

That is where I would start the design stage.
