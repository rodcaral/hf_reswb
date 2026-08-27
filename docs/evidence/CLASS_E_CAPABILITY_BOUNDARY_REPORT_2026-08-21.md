# Class-E Identity-Signal Infrastructure — Capability/Boundary Report

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: read-only review only. No detector or database change made in producing this
report.**

---

## 10165 ↔ 11340 — dual state, restated precisely

| Layer | Value |
|---|---|
| **Technical verdict** (`class_e_identity_signal.py`) | `SAME_INSTRUMENT` — both series carry an identical `(provider_id, provider_series_identifier)` pair: Yahoo Finance, symbol `UBER`. Unchanged since first surfaced (`CLASS_E_IDENTITY_SIGNAL_DISCOVERY_RUN_2026-08-21.md`), re-confirmed zero-drift as of `CLASS_E_CLOSURE_RECORD_2026-08-21.md`. |
| **DFA financial disposition** | `UNRESOLVED` — no DFA ruling has been made on whether these two catalog rows represent the same financial instrument. |

These are two different axes, not two conflicting answers to one question: the technical
verdict is a provider-catalog fact; the financial disposition is a domain judgment DFA has not
yet issued. Not resolved, broadened, or acted on further by this report.

---

## Capability/boundary review against DFA's six requirements

| Requirement | Current support | Boundary — what would require a new domain decision |
|---|---|---|
| **Detection vs. remediation separation** | **Fully supported, by construction.** `detect_identity_candidates()` has no database write access, is a pure function, and returns `IdentityCandidate` dataclasses only. Grep-confirmed (repeated at every prior deliverable this session): no code path in this codebase consumes an `IdentityVerdict` to trigger a mutation. | None — this is a structural property of the module, not a policy that could drift without a code change, which would itself be a visible, reviewable event. |
| **Explicit unresolved identity** | **Supported.** `IdentityVerdict.UNRESOLVED` is a first-class terminal state (not an absence of output) whenever no provider-assignment evidence connects a pair — it is the default outcome for any candidate lacking primary/secondary evidence, including all four Group 1-4 orphans. Label evidence is attached as supporting detail but never promotes a pair out of `UNRESOLVED`. | None for the *technical* signal. A **separate, DFA-only decision** is needed to resolve a pair's *financial* disposition — the detector deliberately has no mechanism to do this, and none should be added without a DFA ruling defining what evidence would suffice. |
| **Financial-identity-aware matching** | **Not supported, by design — and correctly so.** The detector matches on provider-catalog facts (symbol identity, venue-suffix convention) and label text, never on issuer, CUSIP/ISIN, share-class, or depositary-layer facts, because no such structured field exists in this schema (confirmed repeatedly this session — no ISIN/CUSIP column, no structured issuer field). `SAME_INSTRUMENT` therefore means "the provider's own addressing does not distinguish these two," not "these are the same financial instrument." | **This is the detector's central, already-documented boundary.** Any move toward genuine financial-identity-aware matching (e.g., weighting ADR/depositary-layer relationships, issuer-level identity beyond provider symbol) requires DFA to first define what evidence would count and how it should be weighted — Workbench has consistently declined to infer this itself (`CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`'s ADR/depositary-layer question, still open). |
| **Evidence-bound conclusions** | **Supported.** Every `IdentityCandidate` carries `provider_symbol_evidence`, `label_evidence`, and a `detail` string stating exactly what was compared — no verdict is issued without a recorded, inspectable reason attached to it. | None — this is satisfied structurally by the dataclass shape itself. |
| **Provider/ticker signals vs. actual instrument identity** | **The distinction is maintained explicitly in every accompanying document** (module docstring, `CLASS_E_IDENTITY_SIGNAL_2026-08-21.md` §3's evidence-semantics table: `SAME_INSTRUMENT` "is not proof of financial identity by itself"). The code enforces this by never labeling its output as a financial conclusion — the enum member names describe evidence tiers, not identity rulings. | If DFA wants the *reported label* itself changed (e.g. to avoid any reader inferring more than intended from the name `SAME_INSTRUMENT`), that is a naming/communication decision for DFA/SE, not a technical gap — the underlying semantics would not need to change. |
| **Treatment of `SAME_INSTRUMENT` / `RELATED_BUT_DISTINCT` / financially `UNRESOLVED`** | **Supported as three independently meaningful, non-overlapping technical states**, each with a documented evidentiary basis (exact provider-symbol match; venue-suffix relation; no provider evidence). None of the three implies a financial ruling — all three route to the same "preserve and do nothing automatically" terminal behavior DFA has already accepted (2026-08-21 gate ruling). | The financial-disposition layer for pairs *technically* `SAME_INSTRUMENT` or `RELATED_BUT_DISTINCT` (as with 10165↔11340) is not something the detector produces or could produce — that adjudication is DFA's, on a case-by-case basis, and nothing about the current implementation blocks or pre-empts it either way. |

---

## Summary

**What the current implementation already supports**: full detection/remediation separation
(structural, not policy-based), an explicit and evidence-attached `UNRESOLVED` terminal state,
evidence-bound reporting on every verdict, and a consistently maintained distinction (in code
comments, docstrings, and every accompanying document) between what the provider catalog shows
and what that means financially.

**What would require a new domain decision, if ever pursued**: any move to make the detector
itself financial-identity-aware (weighting issuer/depositary-layer/ADR facts, or any evidence
beyond provider symbol and label) requires DFA to specify the evidence and weighting first —
Workbench has not attempted this and does not propose attempting it here. No other gap was
identified in this review.

**No detector or database change made. No candidate created, resolved, or proposed for
remediation.**
