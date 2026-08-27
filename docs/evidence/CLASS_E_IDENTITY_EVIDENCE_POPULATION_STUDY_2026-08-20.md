# Class-E Identity-Evidence Population Study

**Date:** 2026-08-20
**From:** SDT Workbench
**To:** SE
**Status: read-only evidence/design package. No repair SQL, no staged mutation, no
execution. No observation, FK, provenance field, schema, or calibration/policy state
altered. D is not executed by or because of this document — this document exists because D
has not executed, precisely to characterize what D would create before it does.**

**Governing boundary, per DFA ruling, applied throughout**: the ≥9 previously-cited candidates
are a provisional lower bound, not the authoritative population. Label equality/normalization
is not used as a disposition criterion anywhere below — every candidate's assessment rests on
multi-dimensional identity evidence, with the label-signal's demonstrated failure mode treated
as a limitation of the *detector*, not as evidence about any candidate's actual identity.

---

## 0. Candidate population — extended beyond the previously-cited 9

The prior "≥9" figure (2 from Class C's BABA/BIDU orphans + 7 from Class D's orphans-to-be)
is a lower bound by explicit instruction. Checking the same identity pattern against the two
Class-C orphan targets **not** previously analyzed for Class-E purposes (GLD-target 11344,
UBER-target 11347 — held pending, per standing instruction, but not yet checked for this
specific consequence) finds they fit the identical structural pattern as BABA/BIDU: no
provider assignment of their own, single crossed-run origin, and — checked fresh for this
report — the same three-way label relationship with their real underlying and CEDEAR
counterparts.

**Population is therefore 11, not 9**, as of this study. This extension is reported as new
evidence, not as a claim that 11 is itself complete — per the governing boundary, no number in
this document should be read as authoritative.

| # | Candidate | Origin | Group |
|---|---|---|---|
| 1 | 11344 (GLD-target) | Class C orphan (no legitimate rows) | GLD |
| 2 | 11345 (BABA-target) | Class C orphan (no legitimate rows) | BABA |
| 3 | 11346 (BIDU-target) | Class C orphan (no legitimate rows) | BIDU |
| 4 | 11347 (UBER-target) | Class C orphan (no legitimate rows) | UBER |
| 5 | 11342 (MU-target) | Class D orphan-to-be | MU |
| 6 | 11348 (MSFT-target) | Class D orphan-to-be | MSFT |
| 7 | 11349 (AMD-target) | Class D orphan-to-be | AMD |
| 8 | 11350 (MELI-target) | Class D orphan-to-be | MELI |
| 9 | 11351 (NU-target) | Class D orphan-to-be | NU |
| 10 | 11352 (QQQ-target) | Class D orphan-to-be | QQQ |
| 11 | 11353 (AMZN-target) | Class D orphan-to-be | AMZN |

---

## 1. Per-candidate identity-evidence assessment

Template applied to each: **Evidence → Candidate rationale → Instrument-identity assessment
→ Confidence/limitations → Potential disposition class → Dependency/consequence.**

Groups 1–4 (Class C orphans) and 5–11 (Class D orphans-to-be) share enough structural
similarity that per-candidate rows are tabulated, with group-level narrative for what does not
vary by candidate.

### Groups 1–4: Class C orphans (GLD, BABA, BIDU, UBER)

| Field | GLD (11344) | BABA (11345) | BIDU (11346) | UBER (11347) |
|---|---|---|---|---|
| Label | SPDR Gold Shares - ETF (NYSE) | Alibaba Group Holding Limited - ADS (NYSE) | Baidu Inc. - ADS (NASDAQ) | Uber Technologies - Stock (NYSE) |
| Currency | USD | USD | USD | USD |
| Instrument class | (ETF, per label; `instrument_subtype` NULL) | (ADS, per label; `instrument_subtype` NULL) | (ADS, per label; `instrument_subtype` NULL) | (Stock, per label; `instrument_subtype` NULL) |
| Provider/symbol of its own | **None — no `provider_assignment` row exists** | **None** | **None** | **None** |
| Real-underlying counterpart | 2 ("SPDR Gold Shares", Yahoo `GLD`, `SPLIT_ADJUSTED`) | 903 ("...ADR...eight Ordinary share", `instrument_subtype=ADR`, Yahoo `BABA`) | 1169 ("...ADR...8 ordinary share", `instrument_subtype=ADR`, Yahoo `BIDU`) | 10165 ("Uber Technologies, Inc. Common Stock", Yahoo `UBER` + Finnhub) |
| CEDEAR counterpart | 11311 (`instrument_subtype=CEDEAR`, `country=AR`, ARS, Yahoo `GLD.BA`) | 11316 (CEDEAR, AR, ARS, Yahoo `BABA.BA`) | 11317 (CEDEAR, AR, ARS, Yahoo `BIDU.BA`) | 11319 (CEDEAR, AR, ARS, Yahoo `UBER.BA`) |
| Historical range (orphan) | 2024-12-17→2026-05-28 | 2020-03-12→2026-05-28 | 2020-03-13→2026-05-28 | 2022-07-26→2026-05-28 |
| Historical range (real underlying) | 2004-11-18→2026-08-20 | 2014-09-19→2026-08-20 | 2005-08-05→2026-08-20 | 2019-05-10→2026-08-19 |

**Candidate rationale (all four)**: each carries a single-run, cross-series-attributed
observation history (Class C's own finding), holds no provider assignment of its own, and —
checked fresh this pass — shares a normalized issuer/company name with two other existing
series (a real-underlying series and a CEDEAR series).

**Instrument-identity assessment**: **evidence supports same underlying company identity for
all four**, but with an important structural distinction the label alone does not carry —
BABA's and BIDU's real-underlying counterparts are structurally marked `instrument_subtype =
ADR`, meaning the *real* underlying series for those two is itself a depositary instrument
(American Depositary Shares/Receipts), not the ordinary/local share. This is directly relevant
to identity, not merely cosmetic: an ADR and its underlying ordinary share are, in some
classification conventions, treated as distinct securities (different CUSIP/ISIN in
practice), even though they represent the same issuer. **This study does not resolve whether
"same issuer" is a sufficient identity match for Class-E disposition purposes, or whether the
ADR/ordinary-share distinction should be preserved as a genuine separate-identity signal** —
that determination is named as an open question below, not answered here.

**Confidence/limitations**: high confidence that all four orphans represent the same
*issuer* as their real-underlying and CEDEAR counterparts (multiple concurring signals:
label, provider symbol pattern, currency-pairing structure). Lower confidence on whether
"same issuer" should be treated as "same instrument" for BABA/BIDU specifically, given the
ADR-subtype marking. No corporate-action evidence was checked for any of these four in this
pass (out of scope for this study; flagged as a gap, not investigated).

**Potential disposition class**: candidates for merge-or-archive, pending resolution of the
ADR-identity question for BABA/BIDU and pending a general disposition framework (§3).

**Dependency/consequence**: none of these four is blocked by an FK — no series references
any of them as `underlying_series_id` (checked previously, `CLASS_E_GATES_FOR_BABA_BIDU_
2026-08-20.md`, and re-confirmed for GLD/UBER this pass by the same query pattern). They could
be addressed independently of Class D's sequencing, in principle — but see §3 on why a
disposition framework, not case-by-case action, is recommended before any of them moves.

### Groups 5–11: Class D orphans-to-be (MU, MSFT, AMD, MELI, NU, QQQ, AMZN)

Full identity table already returned in `EVIDENCE_MATRICES_B_D_CLASSC_IDENTITY_2026-08-20.md`
Matrix 1 and `CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md` §2 — not re-derived, referenced and
reframed here in the four-way evidence structure this study requires.

**Candidate rationale (all seven)**: exactly one incoming FK reference each (their own D-pair
referrer) today; would have zero after D's repoint; each shares a normalized issuer name with
its own referrer CEDEAR and proposed target (all seven, once the punctuation-sensitivity
correction is applied — see §2).

**Instrument-identity assessment**: **evidence supports same instrument, not merely same
issuer, for all seven** — this group differs materially from Groups 1–4 in strength of
evidence, because current-target and proposed-target use the **identical provider and
identical provider-side symbol** (Yahoo Finance, plain ticker, e.g. `MU`), confirmed in Matrix
1. This is a stronger identity signal than Groups 1–4 have (where the orphan itself has no
provider assignment to compare against at all). No ADR/ordinary-share subtype distinction
applies to this group — all seven referrer/target relationships are direct CEDEAR-to-common-
stock (or CEDEAR-to-ETF, for QQQ) pairs, not ADR-mediated.

**Confidence/limitations**: high confidence of same-instrument identity for all seven, on
stronger evidence than Groups 1–4. Limitation: `configured_interval` differs between current
target (1h) and proposed target (1d) — a real, unexplained configuration difference, not
identity evidence, but also not yet accounted for in any disposition plan.

**Potential disposition class**: candidates for merge/archive, contingent entirely on Class D
executing — these seven do not exist as orphans until D's repoint happens. Distinguish
sharply from Groups 1–4, which are already orphaned today, independent of any pending action.

**Dependency/consequence**: **entirely dependent on D.** If D does not execute, these seven
remain non-orphaned (still referenced by their CEDEARs) and are not live Class-E candidates
at all — they are a *projected* consequence, correctly described as such throughout this
study, not a present-state finding equivalent to Groups 1–4.

---

## 2. False-negative risk in the current label-based detector

**Demonstrated, not projected**: the label-normalization signal has been shown to miss a
duplicate relationship in **three of three checked instances** where the orphan/candidate's
label differs from its counterpart's only by a comma (BIDU: "Baidu Inc." vs. "Baidu, Inc.";
MELI: "MercadoLibre Inc." vs. "MercadoLibre, Inc."; AMZN: "Amazon.com Inc." vs. "Amazon.com,
Inc."). In each case, a normalization search built from the candidate's *own* label text
returned zero matches until re-run without that assumption.

**Per instruction, no completeness percentage is extrapolated from these three examples.**
Three confirmed misses out of the eleven-candidate population checked in this study (§0, §1)
is a rate specific to *this* population and *this* specific failure mode (comma presence/
absence) — it says nothing calibrated about the true miss rate across a broader catalog, and
this study does not claim otherwise. The correct reading is narrower and more defensible: **a
punctuation-sensitive label match is not a reliable negative signal** — "no match" from this
detector does not mean "no duplicate," demonstrated three separate times in this specific
population, not estimated as a general rate.

**Other plausible false-negative mechanisms, not yet demonstrated (named, not claimed)**:
abbreviation variants ("Corp." vs. "Corporation," "Inc." vs. "Incorporated"), word-order
differences, and the ADR-subtype distinction itself (Groups 1–4's BABA/BIDU) potentially
causing a *correct* non-match under a stricter identity standard that a looser label detector
would still flag — i.e., the detector's false-negative risk and false-positive risk are not
symmetric, and this study does not attempt to bound either beyond the punctuation case
actually observed.

---

## 3. Minimum Class-E disposition framework required to absorb D's consequence

**Purpose stated precisely, per instruction**: this section defines what framework is
*required*, not a resolution of any specific candidate. It does not authorize or resolve any
of the eleven.

1. **A disposition-class taxonomy distinct from the detection signal.** Candidates currently
   collapse into one undifferentiated "Class E" bucket regardless of *why* they were flagged
   or *what kind* of duplication they represent. This study's own evidence shows at least two
   qualitatively different populations: Groups 1–4 (same-issuer, ADR-subtype-complicated,
   already-orphaned) and Groups 5–7 (same-instrument, provider-symbol-confirmed, orphaned only
   contingent on D). A minimum framework needs at least these two categories, not one.
2. **An explicit rule for the ADR/ordinary-share identity question** (Groups 1–4, BABA/BIDU
   specifically) — whether "same issuer via different depositary layer" counts as Class-E
   duplication or is a legitimately distinct instrument pairing. Without this rule, no
   disposition can be proposed for BABA/BIDU even in outline, since the answer changes what
   "duplicate" means for that group specifically.
3. **A rule for what happens to a candidate's observation history on disposition** — merge
   (into which series?), archive (with what status marker?), or leave-active-empty — none of
   which this study selects, but the framework needs to name the available options before any
   candidate can move.
4. **An explicit trigger condition tied to D's execution status**, since Groups 5–7 are
   contingent candidates, not present-state ones — the framework must state that these seven
   become live candidates *at* D's execution, not before, so they are not prematurely acted on
   nor silently forgotten if D executes without this study being revisited.
5. **A corrected or supplemented detection signal** that does not rely on label-normalization
   alone, given the demonstrated punctuation blind spot — this study does not design that
   signal, but the framework requires *something* beyond the current label check before any
   "clean" result from it is treated as meaningful, consistent with the standing governing-plan
   principle that a quiet detector is not proof of a clean population.

**This is the minimum scaffolding, not a complete framework** — it does not resolve categories
2–4 above, only names that they must exist before any of the eleven candidates can be
dispositioned.

---

## 4. Explicit separation, restated

- **The seven Class-C rows** (seven-pair episode, value-correct/attribution accepted, no
  mutation) are not reopened, not touched, and not treated as bearing on any candidate's
  identity assessment in this study.
- **The 338/406 Class-D post-transition discrepancies** are not addressed, resolved, or
  invoked as evidence anywhere in this study — they remain their own separate, unresolved
  item.
- **D is not executed while this gate is open**, per instruction — nothing in this document
  changes that status.

---

## What this study does not do

- Does not authorize or resolve the disposition of any of the eleven candidates.
- Does not extrapolate a completeness or false-negative rate beyond the three demonstrated
  instances.
- Does not design the corrected detection signal named as required in §3.
- Does not answer the ADR/ordinary-share identity question for BABA/BIDU.
- Does not execute, stage, or draft repair SQL for any candidate.
- Does not treat the 11-candidate population as final or authoritative.
