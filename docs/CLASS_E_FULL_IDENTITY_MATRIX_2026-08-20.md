# Class-E Identity-Evidence Matrix and Minimum Disposition Framework

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE, for DFA domain adjudication
**Status: read-only. No mutation, staging, D execution, reassignment, deletion, or
provenance modification. The seven Class-C rows are not touched or reclassified. This
package classifies evidence; it does not resolve any financial-identity question — those are
explicitly left for DFA.**

**Evidence basis**: the stable data established in `CLASS_E_MATRIX2_STABILITY_RULE_2026-08-20.md`
and the catalog/provider evidence in `EVIDENCE_MATRICES_B_D_CLASSC_IDENTITY_2026-08-20.md` and
`CLASS_E_IDENTITY_EVIDENCE_POPULATION_STUDY_2026-08-20.md`. Gaps in those documents (venue as
a distinct field, full creation-timestamp coverage for Groups 1–4) were filled by fresh
read-only query for this package, noted where new.

---

## Groups 1–4: currently existing orphan candidates (present-state, not contingent)

### Candidate 1 — GLD-target (series 11344)

| # | Field | Evidence |
|---|---|---|
| 1 | Series identity / catalog metadata | id=11344, label "SPDR Gold Shares - ETF (NYSE)", `status=ACTIVE`, `currency=USD`, `instrument_subtype=NULL`, `country=NULL`, created 2026-08-18 19:43:26 |
| 2 | Issuer evidence | Label text names "SPDR Gold Shares" — same issuer/product name as series 2 and series 11311. No structured issuer field exists in this schema; this is label-text evidence only. |
| 3 | Financial-instrument/security identity evidence | No provider assignment of its own (see #4) — no independent instrument-identifying data source exists for this series at all. Instrument identity rests entirely on stored observation values and label text. |
| 4 | Provider and provider-side symbol evidence | **None.** Zero `provider_assignment` rows reference series 11344 — confirmed by direct query. |
| 5 | Currency evidence | `currency = USD`, a structured field value. |
| 6 | Instrument-class evidence | Label states "ETF"; `series_type` field not separately checked in this pass for this candidate; `instrument_subtype = NULL` (not structurally marked, unlike its CEDEAR counterpart which is marked `CEDEAR`). |
| 7 | Listing/venue evidence | "(NYSE)" appears in the label text only — **this is label-text observation, not a structured field or cross-provider-confirmed fact.** No provider assignment exists to cross-check it against. |
| 8 | Adjustment-basis evidence | Not observable — no provider assignment means no `adjustment_basis` is attached to this series at all. |
| 9 | Historical effective-date/regime evidence | Observation range 2024-12-17→2026-05-28 (344 rows), all from a single import run (11376) whose `provider_assignment.series_id` = 11311 (the CEDEAR, not this series) — i.e., every row is a cross-series attribution, not this series' own history. |
| 10 | Classification | **Same issuer only.** |
| 11 | Specific supporting evidence | Label-text issuer match to series 2 (real ETF) and 11311 (CEDEAR); currency and instrument-class text consistent with both. No provider-symbol match is possible (no assignment exists), so the stronger same-instrument signal available for Groups 5–11 cannot be applied here. |
| 12 | Missing evidence preventing a stronger classification | No provider/symbol evidence at all (the single strongest signal used elsewhere in this study is structurally absent for this candidate); no adjustment-basis; no independently-confirmed venue; no corporate-action or effective-date evidence beyond the crossed-row origin already established under Class C. |

### Candidate 2 — BABA-target (series 11345)

| # | Field | Evidence |
|---|---|---|
| 1 | Series identity / catalog metadata | id=11345, label "Alibaba Group Holding Limited - ADS (NYSE)", `status=ACTIVE`, `currency=USD`, `instrument_subtype=NULL`, `country=NULL`, created 2026-08-18 19:43:28 |
| 2 | Issuer evidence | Label names "Alibaba Group Holding Limited" — matches series 903 (real ADR) and 11316 (CEDEAR). Label-text only. |
| 3 | Financial-instrument/security identity evidence | No provider assignment of its own. Series 903 is structurally marked `instrument_subtype = ADR`, meaning the *real* counterpart is itself a depositary instrument, not an ordinary/local share — a genuine, structurally-recorded complication for identity, not a label artifact. |
| 4 | Provider and provider-side symbol evidence | **None** — zero `provider_assignment` rows. |
| 5 | Currency evidence | `currency = USD`. |
| 6 | Instrument-class evidence | Label states "ADS" (American Depositary Shares); `instrument_subtype = NULL` on this candidate itself, vs. `ADR` structurally recorded on series 903. |
| 7 | Listing/venue evidence | "(NYSE)" in label text only — not structurally confirmed, no provider assignment to cross-check. |
| 8 | Adjustment-basis evidence | Not observable — no provider assignment. |
| 9 | Historical effective-date/regime evidence | 2020-03-12→2026-05-28 (1,513 rows), single import run (25556), `provider_assignment.series_id = 11316` (the CEDEAR) — cross-series attribution, not this candidate's own history. |
| 10 | Classification | **Same issuer only**, with an explicit open sub-question (see #12). |
| 11 | Specific supporting evidence | Label-text issuer match to 903 and 11316; currency and "ADS"/CEDEAR structure consistent with a genuine ADR↔CEDEAR relationship pattern seen elsewhere in this catalog. |
| 12 | Missing evidence preventing a stronger classification | Same structural gaps as Candidate 1 (no provider/symbol, no adjustment basis). **Additionally, and specifically for this candidate**: whether "same issuer via the ADR depositary layer" should be treated as the *same financial instrument* as the CEDEAR (which itself represents the ADR, not the ordinary share) is an unresolved identity-convention question this study does not answer — named explicitly for DFA. |

### Candidate 3 — BIDU-target (series 11346)

| # | Field | Evidence |
|---|---|---|
| 1 | Series identity / catalog metadata | id=11346, label "Baidu Inc. - ADS (NASDAQ)", `status=ACTIVE`, `currency=USD`, `instrument_subtype=NULL`, `country=NULL`, created 2026-08-18 19:43:28 |
| 2 | Issuer evidence | Label names "Baidu Inc." — normalizes to the same issuer as series 1169 ("Baidu, Inc. - ADR...") and 11317 ("Baidu, Inc. CEDEAR"), **only once the comma-punctuation difference is accounted for** — see the false-negative note below. |
| 3 | Financial-instrument/security identity evidence | No provider assignment of its own. Series 1169 structurally marked `instrument_subtype = ADR` — same ADR-layer complication as BABA. |
| 4 | Provider and provider-side symbol evidence | **None.** |
| 5 | Currency evidence | `currency = USD`. |
| 6 | Instrument-class evidence | Label states "ADS"; `instrument_subtype = NULL` on this candidate vs. `ADR` on 1169. |
| 7 | Listing/venue evidence | "(NASDAQ)" in label text only, not structurally confirmed. |
| 8 | Adjustment-basis evidence | Not observable. |
| 9 | Historical effective-date/regime evidence | 2020-03-13→2026-05-28 (1,512 rows), single import run (25557), `provider_assignment.series_id = 11317` (CEDEAR) — cross-series attribution. |
| 10 | Classification | **Same issuer only**, same open ADR sub-question as BABA. |
| 11 | Specific supporting evidence | Same structure as BABA (§ Candidate 2, #11), once the label match is found by dropping the punctuation assumption. |
| 12 | Missing evidence | Same as Candidate 2. **This candidate is also the primary demonstrated instance of the label-detector's punctuation-normalization failure** — a naive match built from this candidate's own label text ("Baidu Inc.") does not find 1169/11317 ("Baidu, Inc.") without that assumption being dropped. Preserved as a **detector limitation**, not a completeness estimate, per instruction. |

### Candidate 4 — UBER-target (series 11347)

| # | Field | Evidence |
|---|---|---|
| 1 | Series identity / catalog metadata | id=11347, label "Uber Technologies - Stock (NYSE)", `status=ACTIVE`, `currency=USD`, `instrument_subtype=NULL`, `country=NULL`, created 2026-08-18 19:43:28 |
| 2 | Issuer evidence | Label names "Uber Technologies" — matches series 10165 ("Uber Technologies, Inc. Common Stock") and 11319 (CEDEAR). |
| 3 | Financial-instrument/security identity evidence | No provider assignment of its own. Series 10165 is **not** ADR-marked (`instrument_subtype = NULL`) — this candidate does not carry the ADR-layer complication BABA/BIDU do; it is a direct common-stock relationship. |
| 4 | Provider and provider-side symbol evidence | **None.** |
| 5 | Currency evidence | `currency = USD`. |
| 6 | Instrument-class evidence | Label states "Stock"; matches 10165's "Common Stock" in kind. |
| 7 | Listing/venue evidence | "(NYSE)" in label text only, not structurally confirmed. |
| 8 | Adjustment-basis evidence | Not observable. |
| 9 | Historical effective-date/regime evidence | 2022-07-26→2026-05-28 (935 rows), single import run (25559), `provider_assignment.series_id = 11319` (CEDEAR) — cross-series attribution. |
| 10 | Classification | **Same issuer only** — closer to same-instrument than BABA/BIDU (no ADR complication), but still lacking the provider-symbol confirmation that would justify a stronger classification. |
| 11 | Specific supporting evidence | Label-text issuer match; no depositary-layer complication found in the real-underlying's own metadata. |
| 12 | Missing evidence | No provider/symbol evidence, no adjustment basis, no venue confirmation beyond label text — identical structural gap to the other three, without the ADR sub-question that specifically affects BABA/BIDU. |

---

## Groups 5–11: D-contingent candidates — NOT active Class-E candidates unless D executes

**Restated before the matrix, not after**: these seven do not exist as orphaned series today.
They are characterized here as a **projection** of what D's execution would create, per the
governing instruction that they must not be treated as active candidates.

### Candidates 5–11 — shared structure, tabulated (MU exemplar; identical pattern all seven)

| # | Field | Evidence (all seven pairs, differences noted per-pair below) |
|---|---|---|
| 1 | Series identity / catalog metadata | e.g. id=11342, label "Micron Technology, Inc. - Stock (NASDAQ)", `status=ACTIVE`, `currency=USD`, `instrument_subtype=NULL`, `country=NULL`, `configured_interval=1h`, created 2026-08-18 19:32–19:43 |
| 2 | Issuer evidence | Label names the same issuer as the referrer CEDEAR and the proposed target, in all seven pairs — confirmed after correcting for the punctuation-normalization failure (affects MELI, AMZN specifically; see below). |
| 3 | Financial-instrument/security identity evidence | Two data regimes within the same series id: bit-identical to referrer through 2026-05-27 (18,315 rows total, zero exceptions), then independently tracking a value close to the proposed target from 2026-05-28 (405 stable dates, ratio median 1.0000). No ADR/depositary-layer complication in any of the seven — all direct CEDEAR-to-common-stock or CEDEAR-to-ETF (QQQ) relationships. |
| 4 | Provider and provider-side symbol evidence | **Present, and the strongest signal in this entire study**: current target and proposed target use the **identical provider (Yahoo Finance) and identical provider-side symbol** (plain ticker, e.g. `MU`) in all seven pairs — confirmed directly, not inferred. This is the one dimension where Groups 5–11 have categorically stronger evidence than Groups 1–4. |
| 5 | Currency evidence | `currency = USD` on both current and proposed target, all seven. |
| 6 | Instrument-class evidence | STOCK (ETF for QQQ) on referrer, current target, and proposed target — consistent across all three, all seven pairs. |
| 7 | Listing/venue evidence | Current target's label states a venue ("NASDAQ", "NYSE") in text only. Proposed target carries a populated, structured `country = US` field current target lacks — a **structured field**, not label text, available on the proposed-target side only. **Cross-provider inference**: since current and proposed target share the identical provider/symbol (#4), the venue implied by that shared symbol is the same real-world listing for both — this is an *inference from the provider-symbol match*, not a direct observation of a venue field on current target itself. |
| 8 | Adjustment-basis evidence | `SPLIT_ADJUSTED` on both current and proposed target (and the referrer), all seven pairs — directly observed, matching. |
| 9 | Historical effective-date/regime evidence | The 2026-05-28 transition date, identical across all seven pairs (confirmed, not assumed to generalize from one). Referrer creation 2026-08-18 16:15:46; current target creation 2026-08-18 19:32–19:43 (postdates referrer ~3–3.5h); proposed target creation 2026-08-11 03:45 (predates referrer ~1 week) — the structural evidence already underlying Class D's own repointing rationale. |
| 10 | Classification | **Same financial instrument** — the strongest classification available in this study, resting on the provider-symbol match (#4), not on label or timestamp similarity alone. |
| 11 | Specific supporting evidence | Identical provider + identical provider-side symbol (decisive); matching currency, instrument class, and adjustment basis; structural creation-timestamp evidence already established for D. |
| 12 | Missing evidence preventing an even stronger classification | `configured_interval` differs (1h current vs. 1d proposed) — an unexplained configuration difference, not identity evidence, but not yet reconciled either; no corporate-action-specific evidence was checked for any of the seven in this pass. |

**Per-pair label-match correction, restated**: MELI ("MercadoLibre Inc." vs. referrer/proposed
"MercadoLibre, Inc.") and AMZN ("Amazon.com Inc." vs. "Amazon.com, Inc.") are both confirmed
same-issuer only once the comma-punctuation assumption is dropped — the second and third
demonstrated instances of the detector limitation, alongside BIDU (Candidate 3, above).

---

## False-negative risk in the label-based detector — restated as a limitation, not an estimate

**Demonstrated in three of the eleven candidates checked in this study (BIDU, MELI, AMZN)** —
in each case, a normalization search built from the candidate's own label text misses its true
counterpart because of a single comma's presence or absence. **No completeness percentage is
extrapolated from this** — three confirmed instances in an eleven-candidate population is
reported as exactly that: a demonstrated failure mode in this specific population, not a
general rate calibrated across a larger catalog. The correct reading, restated: a "no match"
result from this detector does not establish "no duplicate."

---

## Minimum Class-E disposition framework

Requested elements, each addressed as scaffolding — **none resolved, none authorizing action**:

### 1. Taxonomy for the candidate groups

Two structurally distinct group types, evidenced (not asserted) by this matrix:
- **Type I — present-state orphans with same-issuer-only evidence** (Groups 1–4): no provider/
  symbol confirmation exists or can exist without new data acquisition; classification ceiling
  is "same issuer" absent further evidence.
- **Type II — D-contingent, same-financial-instrument evidence** (Groups 5–11): provider-symbol
  confirmed; classification ceiling is higher, but activation is conditional on D (§4 below).

A minimum framework needs at least these two types, since they warrant different evidentiary
thresholds and different urgency — Type I's ceiling cannot improve without new evidence
sources; Type II's evidence is already as strong as this study can make it without DFA input.

### 2. ADR/ordinary-share/depositary-layer identity treatment

Affects Candidates 2 and 3 (BABA, BIDU) specifically, where the real-underlying counterpart is
structurally marked `instrument_subtype = ADR`. **This study poses the question explicitly and
does not answer it**: is an ADR and the CEDEAR/other-series that represents *it* (not the
ordinary share directly) the same financial instrument for Class-E purposes, or a legitimately
distinct instrument pairing (different CUSIP/ISIN in real-world convention)? The framework
requires an explicit rule here **before** Candidates 2 and 3 can be classified above "same
issuer only," regardless of any further data-gathering.

### 3. Observation-history disposition

Neither this study nor any prior one selects among merge / archive / leave-active-empty for
any candidate's observation history. The framework requires this option set to be named and a
selection rule established — e.g., "merge into the earliest-created counterpart series,"
"archive with an explicit superseded-by marker," or another convention — before any candidate
moves, for any of the eleven.

### 4. Activation condition for D-contingent candidates

**Explicit, restated precisely**: Groups 5–11 become live Class-E candidates **at the moment D
executes**, not before. The framework requires this trigger be operationalized (e.g., a
required Class-E re-scoping step immediately following D's execution, not deferred to a later,
unscheduled "eventually") so that D's execution does not silently create seven live candidates
with no immediate disposition process attached.

### 5. Corrected identity-detection signal

The demonstrated punctuation-normalization failure (3 of 11 candidates in this study) means the
existing label-based detector cannot be relied on for a "clean" result to mean "no duplicates."
The framework requires a signal that does not depend on label text alone — the provider-symbol
match used as the primary evidence dimension throughout this matrix (#4 in every candidate's
row) is the strongest available alternative signal demonstrated in this study, though this
document does not formally design a replacement detector, only names that one is required and
identifies the dimension (provider + provider-side symbol) most load-bearing in the evidence
gathered so far.

---

## Standing separations, restated

- **Groups 1–4 and Groups 5–11 remain separate populations** — Type I (present, ceiling
  same-issuer) vs. Type II (contingent, ceiling same-instrument), per §1 above.
- **The seven D-contingent candidates are not active Class-E candidates.** D has not executed.
- **The seven Class-C rows are not touched, reclassified, or referenced as evidence for any
  identity assessment in this matrix.**
- **No mutation, staging, reassignment, deletion, or provenance modification** was performed or
  proposed in producing this package.

---

## What this package does not do

- Does not resolve any of the eleven candidates' final disposition.
- Does not answer the ADR/ordinary-share identity question.
- Does not design the corrected detection signal, only identifies its most load-bearing
  dimension.
- Does not execute, stage, or bring D closer to execution.
- Does not extrapolate a completeness or false-negative rate.
- Does not decide any financial-identity question DFA has not yet ruled on.
