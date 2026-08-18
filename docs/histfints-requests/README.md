# HistFinTS Requests — hf_reswb Workbench

This directory contains all outstanding requests filed with the HistFinTS development team, organized by decision and blocking issue.

---

## Current Status (2026-08-17)

### Tranche 2 Schema Completion — BLOCKING, READY TO ACTION

**Status:** Two independent items verified unimplemented and documented  
**Blocking:** `SPEC-panel-eligibility.md` implementation in Workbench  
**Risk:** Workbench cannot activate `adjustment_policy` or `minimum_coverage` parameters without both items

#### Files
1. **REQUEST-tranche2-completion.md** — Original requirements (D-041)
2. **TRANCHE2-VERIFICATION-2026-08-17.md** — Live database verification, structural analysis (D-043)
3. **ACTION-TRANCHE2-IMPLEMENTATION.md** — Concrete implementation instructions with SQL (D-043)

#### Items
| Item | Status | Effort | Risk | Acceptance Criteria |
|------|--------|--------|------|---------------------|
| 1: Adjust basis backfill | Unimplemented | Minimal (3 UPDATEs) | None | Values populated per spec, query verification |
| 2: Provider-assignment availability marker | Unimplemented | Low (schema + backfill) | Low | Columns exist, populated, no inverted ranges, query verification |

**No dependency between items.** Both can proceed in parallel or sequentially.

---

## Archived/Historical Requests

- **REQUEST-event-capture.md** — F-009 evidence capture (no update since D-032)
- **REQUEST-apply-migrations-0011-0013.md** — Deploy already-built evidence migrations (awaiting completion of Tranche 2 primary work)
- **DEFECT-F009.md** — F-009 upstream defects (status as of D-032)

---

## How to Read These Files

**For implementation planning:**
1. Start with `ACTION-TRANCHE2-IMPLEMENTATION.md` — exact SQL, acceptance criteria, effort/risk
2. Reference `TRANCHE2-VERIFICATION-2026-08-17.md` — why existing data doesn't substitute, verification queries

**For context:**
- `REQUEST-tranche2-completion.md` — original context and reasoning

**For code/architecture:**
- See `docs/DECISIONS.md` D-041, D-043 for decision context
- See `docs/SPEC-panel-eligibility.md` for how Workbench will consume these items

---

## Workbench Status

### Ready Now
- Observation-suitability classification (D-039–D-040, implemented and frozen)
- Three inclusion-rule parameters specified with calibration methodology (D-042)
- Calibration study methodology documented, ready to proceed when Tranche 2 lands

### Blocked On Tranche 2
- Panel eligibility implementation
- Adjustment basis enforcement
- Minimum coverage parameter activation

### Timeline
Both Tranche 2 items must complete before Workbench can proceed to full panel-eligibility implementation.

---

## Questions for HistFinTS SE

See `ACTION-TRANCHE2-IMPLEMENTATION.md` → "Questions for HistFinTS SE" section.

---

## Document Index

| File | Purpose | Date | Status |
|------|---------|------|--------|
| REQUEST-tranche2-completion.md | Initial requirements filing | 2026-08-17 | Filed |
| TRANCHE2-VERIFICATION-2026-08-17.md | Live DB verification + analysis | 2026-08-17 | Complete |
| ACTION-TRANCHE2-IMPLEMENTATION.md | Concrete implementation spec | 2026-08-17 | Ready for SE |
| README.md | This file | 2026-08-17 | Current |
