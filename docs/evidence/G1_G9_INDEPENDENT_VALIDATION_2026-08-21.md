# Independent Read-Only Validation — G1/G9 Evidence-Gated Evaluator

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE (PO validation request)
**Status: read-only validation only. No code or production data modified in producing this
report.**

---

## Overall: PASS

All nine items verified against `G1_G9_Final_Domain_Ruling.md`, the current content of
`evidence_gated_identity_evaluator.py`, and live re-query of the production database. No
divergence from the ruling found.

---

## Evidence matrix

| # | Requirement | Verdict | Evidence |
|---|---|---|---|
| 1 | `FinancialIdentityConclusion` cannot be conflated with technical `IdentityVerdict` | **PASS** | Two separate `str, Enum` classes in two separate modules (`evidence_gated_identity_evaluator.py` vs. `class_e_identity_signal.py`). No shared base class, no coercion between them anywhere in the codebase (grep-confirmed: `evaluate_financial_identity`/`evidence_gated_identity_evaluator` referenced only in its own module and `application/__init__.py`'s export list — zero use inside `class_e_identity_signal.py`). Module docstring states the distinction explicitly (lines 8–17). |
| 2 | The three states remain distinct financial conclusions | **PASS** | `FinancialIdentityConclusion` has exactly three members (`SAME_INSTRUMENT`, `RELATED_BUT_DISTINCT`, `UNRESOLVED`, lines 154–169), each independently docstringed with its ruling citation. `evaluate_financial_identity()` returns exactly one of the three per call — no fourth/blended state exists in the type. |
| 3 | Seven identity dimensions represented; missing evidence cannot be silently inferred | **PASS** | `IdentityDimension` has exactly seven members (lines 88–94), matching G1/G9 §4 one-to-one. `dimension_assessments.get(dim)` (used throughout, e.g. line 238, 260, 291) returns `None` for any dimension absent from the caller's dict — the code then treats `None` identically to `DimensionStatus.UNKNOWN` (line 239, line 261, line 292), never defaulting a missing dimension to `ESTABLISHED_EQUIVALENT` or any other status. Confirmed by `TestMissingEvidence` (4 tests, all passing on re-run). |
| 4 | Provider symbols, labels, normalization, correlation, provenance signals cannot independently resolve identity | **PASS** | The `SAME_INSTRUMENT` predicate's per-dimension tier check (line 298) rejects any assessment whose `tier` is not `TIER_1_PRIMARY`/`TIER_2_STRUCTURED_MARKET_DATA` — Tier 3 (provider operational: symbol, ticker, label, import path) and Tier 4 (correlation, price similarity, timestamps, provenance) are both excluded. The issuer-identity check additionally has its own explicit Tier 3/4 rejection (line 247) before any other logic runs. The `RELATED_BUT_DISTINCT` path requires `relationship_evidence.tier` and the material-distinction dimension's `tier` to both be Tier 1/2 (lines 314–320) — Tier 3/4 evidence cannot satisfy either half of that predicate either. Confirmed by `TestCrossProviderAndProviderSymbolOnly` (2 tests). |
| 5 | Contradictory, stale, cross-provider, or materially incomplete authoritative evidence forces `UNRESOLVED` | **PASS** | Contradiction: any non-empty `contradictory_dimensions` short-circuits to `UNRESOLVED` unconditionally (lines 228–236) before any other evidence is even examined — no majority-vote or latest-wins logic exists anywhere in the function body (confirmed by reading the full function; no vote-counting or date-comparison-for-precedence code exists). Staleness: `is_stale()`/`has_unknown_effective_period()` checked for every supplied assessment (lines 270–286), before the `SAME_INSTRUMENT`/`RELATED_BUT_DISTINCT` predicates run. Cross-provider: covered under item 4 — Tier 3/4 rejection is provider-agnostic, so even multi-provider agreement is capped at Tier 3. Materially incomplete: the `MANDATORY_DIMENSIONS` loop (lines 288–300) fails `same_instrument_ok` on any missing/`UNKNOWN`/wrong-tier dimension. Confirmed by `TestContradictoryEvidence` (2), `TestStaleEvidence` (3), `TestCrossProviderAndProviderSymbolOnly` (2), `TestMissingEvidence` (4) — 11 tests total, all passing. |
| 6 | Automatic resolution disabled by default; no production caller enables it | **PASS** | `automatic_resolution_enabled: bool = False` (line 191) is the first condition checked in the function body (line 216) — every other parameter is ignored when `False`. Grep of `src/` for `automatic_resolution_enabled` returns only the definition itself, its docstring mentions, and the one `if not automatic_resolution_enabled:` check — **no call site anywhere in `src/` passes `True`**. Confirmed independently, not merely restated from the prior design doc. |
| 7 | No detector output can trigger mutation or catalog/observation remediation | **PASS** | `evidence_gated_identity_evaluator.py` contains no `import sqlite3`, no database connection parameter, no write statement of any kind — confirmed by reading the full file. `class_e_identity_signal.py` (the technical detector) was already confirmed DB-free in its own prior review, re-confirmed unchanged by this validation. Grep of the full `src/` tree for consumers of either module's verdict types (`IdentityVerdict`, `FinancialIdentityConclusion`) finds only the modules' own definitions and `application/__init__.py`'s export list — no service module (`panel_eligibility_service.py`, `panel_integration.py`, `calibration_analyzer.py`, `calibration_utilities.py`) imports either. |
| 8 | Tests exercise the DFA-mandated gates, particularly `UNKNOWN` vs. `DIFFERENT` | **PASS** | `TestMissingEvidence::test_unknown_never_becomes_different` explicitly asserts that a bare `UNKNOWN` issuer-identity assessment routes to `UNRESOLVED`, and its own comment states the evaluator "never assigns `ESTABLISHED_DIFFERENT` — only a caller-supplied `DimensionAssessment` can, and none was supplied here" — confirmed true by code inspection: no line in `evaluate_financial_identity()` constructs or assigns a `DimensionStatus.ESTABLISHED_DIFFERENT` value; that status can only ever originate from the caller's own input. Re-ran the full test file plus the technical-signal test file together at validation time: **35 passed** (20 evaluator + 15 technical-signal tests), no failures, no modification made to either test file in the process. |
| 9 | No production schema, data, provider assignment, Class-E population, or 10165/11340 disposition changed | **PASS** | Re-queried live, read-only, at validation time: total `observation` count **27,972,837** — identical to the last-recorded value (`CLASS_E_CLOSURE_RECORD_2026-08-21.md`). 11345/11346: `SUPERSEDED`, 0 provider assignments — identical. 10165/11340: both `ACTIVE`, 2 provider assignments each — identical, and its stored technical verdict is unaffected (the new evaluator was never invoked with `automatic_resolution_enabled=True` against any real pair, so its financial disposition is exactly as it was: `UNRESOLVED`, per G1/G9 §9's own statement, unchanged). No schema query (`sqlite_master`) was needed to confirm this, since the evaluator's own source contains no DDL or write statement to begin with. |

---

## Divergence from the ruling

**None found.** Every check above traces to a specific line or test in the current code, not
to the design document's own prose (the design document was used to know where to look, not
accepted as proof on its own).

---

## Conclusion

**PASS.** Read-only validation supports treating G1/G9 requirements adjudication as complete
at the capability level: the evaluator is implemented, tested, structurally incapable of
mutation, and disabled by default with no production caller. Production eligibility (i.e.
actually enabling `automatic_resolution_enabled=True` for any real pair) remains correctly
blocked — not by policy alone, but because, as this session's own dimension-availability
survey (`G1_G9_EVALUATOR_DESIGN_2026-08-21.md` §3) found, no candidate examined has the
required Tier 1/2 evidence in HistFinTS today. This validation does not change that; it
confirms the gate holding it back is real, not merely declared.

No code or production data was modified in producing this validation.
