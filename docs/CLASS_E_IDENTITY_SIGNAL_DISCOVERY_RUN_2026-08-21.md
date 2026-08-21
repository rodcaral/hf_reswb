# Class-E Identity-Detection Signal — Discovery Run Against Live Production Data

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: read-only discovery run only. All queries against the live HistFinTS database were
`SELECT`-only (no ATTACH write, no copy). No observation, series, provider_assignment, or
provenance field was modified. No repair SQL staged. D not executed, staged, or advanced.**

This document runs the signal implemented in `class_e_identity_signal.py`
(`CLASS_E_IDENTITY_SIGNAL_2026-08-21.md`) against real production series data for Groups 1–4,
and separately against the MU exemplar for Groups 5–11, per SE's request to report "the
resulting candidate population as a discovery result only, not as an authoritative Class-E
population." **Every finding below is exactly that — a discovery-tool output, not a
disposition, not a completeness claim, not a financial-identity ruling.**

---

## 1. Groups 1–4 (present-state candidates) — signal run against the real orphan targets

For each of the four orphan targets, its own real production label and provider-assignment
set were loaded (read-only) alongside its previously-identified plausible counterpart(s), and
run through `detect_identity_candidates()`.

### 1.1 The orphan targets themselves: zero candidates from this signal

| Target | Label (verbatim, production) | Provider assignments |
|---|---|---|
| 11344 (GLD-target) | `SPDR Gold Shares - ETF (NYSE)` | none |
| 11345 (BABA-target) | `Alibaba Group Holding Limited - ADS (NYSE)` | none |
| 11346 (BIDU-target) | `Baidu Inc. - ADS (NASDAQ)` | none |
| 11347 (UBER-target) | `Uber Technologies - Stock (NYSE)` | none |

**Primary signal (provider+symbol): inapplicable, as expected.** Confirms, by direct query
rather than by inference, the structural gap already established for these four candidates —
zero `provider_assignment` rows, so there is no provider-catalog fact to compare.

**Supporting label signal: also produced no match against real production text**, and this is
reported precisely rather than smoothed over. The demonstrated punctuation failure this
deliverable targets (BIDU/MELI/AMZN, as recorded in `CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`
and `CLASS_D_FINAL_PACKAGE_FOR_SE_2026-08-20.md`) was characterized using short core-name label
forms (e.g. `"Baidu Inc."` vs. `"Baidu, Inc."`) that differ by punctuation alone. The actual
production labels differ by more than punctuation — the orphan targets carry a distinct
`"<Name> - <Type> (<Venue>)"` descriptor convention (e.g. `"Baidu Inc. - ADS (NASDAQ)"`) that
their real counterparts do not share verbatim (e.g. `"Baidu, Inc. - American Depositary
Shares, each representing 8 ordinary share"`). Punctuation-insensitive normalization does not
bridge that gap, and this detector was deliberately not given a broader fuzzy-matching layer
(SE's instruction: labels are supporting evidence, not the discovery mechanism — broadening
normalization to catch wording differences risks new, undemonstrated false positives that
were not authorized here).

**Disclosed limitation, not silently patched**: as currently scoped, this signal alone finds
**no** candidate at all for any of the four Group 1–4 orphan targets when run against their
real production labels and (nonexistent) provider assignments. This does not reopen or
contradict the prior finding that these four are "same issuer only" candidates — that finding
was reached through direct domain/issuer knowledge in the earlier population study, not
through this mechanical signal, and this signal was never expected to independently rediscover
it without a wider evidence layer than SE authorized for this task.

### 1.2 Evidence surfaced among the counterparts themselves (not the orphan targets)

Although the orphan targets produced no candidates, running the same real data revealed
genuine `RELATED_BUT_DISTINCT` evidence **between the ADR/underlying and its own CEDEAR** for
two of the four groups — already-known relationships, now reproduced mechanically rather than
by manual inspection:

| Pair | Verdict | Evidence |
|---|---|---|
| 903 (Alibaba ADR) vs. 11316 (Alibaba CEDEAR) | `RELATED_BUT_DISTINCT` | provider 2: `BABA.BA` vs. `BABA` |
| 1169 (Baidu ADR) vs. 11317 (Baidu CEDEAR) | `RELATED_BUT_DISTINCT` | provider 2: `BIDU.BA` vs. `BIDU` |

### 1.3 New evidence surfaced, not previously part of this session's Class-E work

Running UBER's counterpart set (10165, 11340, 11319 — none of them the orphan target 11347)
surfaced a **previously undiscussed pair**:

| Pair | Verdict | Evidence |
|---|---|---|
| 10165 vs. 11340 | `SAME_INSTRUMENT` | both reference provider 2, symbol `UBER` |
| 10165 vs. 11319 (CEDEAR) | `RELATED_BUT_DISTINCT` | provider 2: `UBER.BA` vs. `UBER` |
| 11340 vs. 11319 (CEDEAR) | `RELATED_BUT_DISTINCT` | provider 2: `UBER.BA` vs. `UBER` |

Series 10165 (`Uber Technologies, Inc. Common Stock`, ACTIVE, 1,830 observations,
`created_at` 2026-08-11) and series 11340 (`Uber Technologies Inc. Common Stock`, ACTIVE, 0
observations, `created_at` 2026-08-18) both carry an identical provider-2 symbol (`UBER`).
**Reported strictly as a discovery-tool output — not investigated further, not added to any
Class-E count, not classified as a defect.** This is flagged for SE/DFA to decide whether it
warrants its own evidence item; Workbench takes no position on disposition here, consistent
with the standing prohibition on inferring identity conclusions from detector output.

---

## 2. Groups 5–11 exemplar (MU) — reproduction only, explicitly not activated

Per instruction, Groups 5–11 remain D-contingent and are **not** to be counted as current
Class-E candidates. The MU triple (referrer 11323, current target 11342, proposed target 6672)
was run only to confirm the signal reproduces the already-established pattern correctly — this
is a correctness check on the tool, not a new discovery, and changes nothing about Groups
5–11's inactive status:

| Pair | Verdict | Evidence |
|---|---|---|
| 11323 (referrer CEDEAR) vs. 11342 (current target) | `RELATED_BUT_DISTINCT` | provider 2: `MU.BA` vs. `MU` |
| 11323 (referrer CEDEAR) vs. 6672 (proposed target) | `RELATED_BUT_DISTINCT` | provider 2: `MU.BA` vs. `MU` |
| 11342 (current target) vs. 6672 (proposed target) | `SAME_INSTRUMENT` | both reference provider 2, symbol `MU` |

**This reproduction is not an activation.** Groups 5–11 remain contingent on D's execution, and
D is not executed, staged, or brought closer to execution by this document or this run.

---

## 3. What this discovery run establishes and does not establish

**Establishes**:
- The signal functions correctly against real data: it reproduces the known
  `SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT` pattern for Groups 5–11's MU exemplar exactly as
  designed, and correctly abstains (returns no candidate) for the Group 1–4 orphan targets
  themselves rather than fabricating a match.
- It surfaces two already-known ADR/CEDEAR relationships (BABA, BIDU) mechanically.
- It surfaces one new, previously undiscussed `SAME_INSTRUMENT` pair (UBER 10165/11340),
  reported as evidence only.

**Does not establish**:
- Does not establish that Groups 1–4's orphan targets are, or are not, duplicates of their
  counterparts — the signal simply has no evidence to offer for that specific pair given the
  real label/assignment gap described in §1.1.
- Does not establish that the UBER 10165/11340 pair is a defect requiring remediation — no
  disposition is proposed.
- Does not change the Class-E population count, the Groups 1–4/5–11 separation, or any
  standing disposition.
- Does not resolve, or bear on, the ADR/depositary-layer identity question or the
  observation-history disposition rule — both remain outside this task, per instruction.

---

## 4. Execution boundary, restated

All queries in this document were read-only `SELECT`s against the live HistFinTS database.
No `INSERT`/`UPDATE`/`DELETE` was issued. No `provider_assignment`, `series`, `observation`,
`import_run_id`, or `origin_import_run_id` value was altered. No repair SQL was drafted or
staged. D was not executed or advanced.
