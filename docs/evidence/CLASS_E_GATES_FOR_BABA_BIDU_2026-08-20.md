# Class-E Consequence Analysis and Pre-Execution Gates — BABA/BIDU (11345/11346)

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: read-only analysis only. No repair executed or staged. No `import_run_id`,
`origin_import_run_id`, `provider_assignment`, or existing observation state touched or
proposed to be touched. DFA's authorization of the BABA/BIDU move is treated as domain
authorization only — not execution authorization, per instruction. Scope confined to
BABA/BIDU and their Class-E consequence; A–F implementation not otherwise addressed here.**

**The seven-row Class-C finding (value-correct, attribution accepted, no mutation) is
acknowledged and not revisited. It is confirmed, independently, to be a different data
population from BABA/BIDU — see §0.**

---

## 0. Confirming separation from the seven-row question

Re-verified read-only: 11345 (BABA-target) and 11346 (BIDU-target) each carry observations
from exactly **one** import run apiece — 25556 and 25557 respectively — both part of the
**five-control episode**, distinct from the seven-pair episode's runs (58228–58234) that
produced the single-row 2026-05-28 collisions DFA just resolved. This corroborates, rather
than merely repeats, the instruction's framing: BABA/BIDU are not adjacent rows in the same
finding — they are a structurally separate Class-C population (the four no-legitimate-row
targets, two of the four), carrying their own distinct disposition question.

---

## 1. What "emptying" 11345/11346 would and would not resolve

Emptying removes the two series' entire observation content (1,513 and 1,512 rows
respectively — their full content, confirmed in the prior Class C evidence package). It does
**not** touch `series.id`, `series.label`, `series.status`, or any other series-level metadata
— the series rows themselves persist, unchanged, as zero-observation `ACTIVE` entries.

**This matters directly for Class E**, because Class E's finding is about *duplicate series
records existing*, not about their observation content. Emptying 11345/11346 changes what
they hold; it does not change whether they should exist as separate series at all.

---

## 2. Gate 1 — BABA-target (11345) is an active, undisclosed three-way label duplicate

Re-verified read-only: `series.label` for 11345 is `"Alibaba Group Holding Limited - ADS
(NYSE)"`. A direct query for any other series sharing the normalized core "Alibaba Group
Holding Limited" returns:

| Series | Label |
|---|---|
| 903 | Alibaba Group Holding Limited American Depositary Shares each representing eight Ordinary share |
| 11316 | Alibaba Group Holding Limited CEDEAR (BYMA) |
| **11345** | **Alibaba Group Holding Limited - ADS (NYSE)** |

**Three series, one company, no merge or disambiguation recorded.** Emptying 11345's
observations does not reduce this to two — the series row remains, still labeled as a
third "Alibaba Group Holding Limited" entity, indistinguishable at the catalog level from a
legitimately-intended third series unless something else marks it otherwise.

---

## 3. Gate 2 — BIDU-target (11346) is the same pattern, and demonstrates why the Class-E label
signal is a floor

Re-verified read-only, all series with "Baidu" anywhere in the label:

| Series | Label |
|---|---|
| 1169 | Baidu, Inc. - American Depositary Shares, each representing 8 ordinary share |
| 11317 | Baidu, Inc. CEDEAR (BYMA) |
| **11346** | **Baidu Inc. - ADS (NASDAQ)** |

**11346's label omits the comma present in 1169's and 11317's ("Baidu Inc." vs. "Baidu,
Inc.").** A naive substring or exact-normalization check derived from 11346's own label text
does **not** match 1169 or 11317 — confirmed directly by running exactly that check, which
returned zero matches until the search was re-run against "Baidu" alone rather than 11346's
own normalized core. **This is a live, concrete instance of the exact limitation the governing
Class-E framework already names as structural**: the label signal under-reports by
construction, and this is a real example of it doing so, not a hypothetical one. If the
disposition of BIDU-target relies on a label-normalization pass to flag it as a duplicate,
this specific punctuation difference is sufficient to make that pass miss it.

---

## 4. Gate 3 — no schema-level blocker, but also no schema-level signal that would catch this later

Re-verified read-only, for both 11345 and 11346:

- **No series** has `underlying_series_id` pointing at either — no FK dependency blocks any
  action (unlike Class D/E's `ON DELETE RESTRICT` relationship).
- **No `provider_assignment` row** references either series — no active or configured write
  path exists for either today, so there is no ongoing-accrual risk analogous to the BYMA
  evidence cohort's scheduled-task exposure (§9 of the original boundary plan).
- **No `identifier` row** references either series.
- `match_candidate` and `series_merge` were checked and found to have no `series_id`-shaped
  column matching this query pattern in the current schema — not a finding about these two
  series specifically, noted so the absence of a result here isn't mistaken for a confirmed
  "no relationship" the way the other three checks are.

**Net:** nothing structurally *prevents* emptying 11345/11346 today. But nothing structurally
*catches* their duplicate-label status either, going forward, if emptying is treated as
resolving the finding. The absence of a blocker is not the same as the absence of a
consequence.

---

## 5. Domain decisions this analysis surfaces, not answers

1. **Is a third "Alibaba Group Holding Limited" / "Baidu[,] Inc." series ever intended to
   exist in this catalog**, or is 11345/11346's continued existence — even empty — itself the
   thing that should be resolved (via merge into 903/1169, or archival, or some other
   disposition), separately from and in addition to emptying their crossed observations?
   This analysis does not answer this; it is the central open question emptying alone does
   not close.
2. **Does emptying 11345/11346 need to be sequenced relative to Class E's own resolution**,
   given Class E is explicitly not begun and its scope explicitly not proven (standing
   instruction, carried through every package this project has returned)? Emptying is a
   Class-C-level action on observation content; it is not itself a Class-E action — but if SE's
   intent in authorizing it is partly to "clean up" these two series, that intent would be
   unmet by emptying alone, and stating that gap now avoids a later assumption that the
   BABA/BIDU move already addressed part of Class E's population.
3. **Should the punctuation-level miss found in §3 be treated as evidence that the label
   signal needs a normalization fix** before it's relied on for any future Class-E work,
   independent of what happens with BABA/BIDU specifically? Not answered here — flagged as a
   concrete data point for whoever eventually scopes Class E.

---

## 6. What this analysis does not do

- Does not propose, stage, or execute any mutation to 11345, 11346, their observations, or any
  other series.
- Does not treat DFA's domain authorization of the BABA/BIDU move as execution authorization —
  per instruction, this remains a gate-identification exercise only.
- Does not revisit or reopen the seven-row Class-C finding.
- Does not begin Class E scoping or propose a merge/disposition for 903/11316/1169/11317.
- Does not broaden into general A–F implementation.
