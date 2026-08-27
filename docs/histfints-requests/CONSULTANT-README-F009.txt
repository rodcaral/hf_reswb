================================================================================
DEFECT-F009 CONSULTANT REVIEW PACKAGE
================================================================================

Repository: HistFinTS (v3 branch)
https://github.com/anthropics/histfints-v3

This package contains everything needed for an independent technical review of
DEFECT-F009 (incremental import scale discontinuities).

================================================================================
START HERE
================================================================================

1. Read the package overview:
   -> CONSULTANT-PACKAGE-F009.md (this is your entry point)

2. Then read the full defect analysis:
   -> DEFECT-F009.md

3. Verify the mechanism in the code:
   -> histfints-v3/src/histfints/application/import_service.py (lines 183-200)

4. Run the regression test:
   -> python -m pytest tests/application/test_import_service_defect_f009.py -v

5. Evaluate remedies using the framework:
   -> CONSULTANT-PACKAGE-F009.md (section: Remedy Evaluation Framework)

================================================================================
PACKAGE CONTENTS
================================================================================

Documentation:
  CONSULTANT-PACKAGE-F009.md
    Quick-start guide + full remedy evaluation framework
    (10-15 min read)

  DEFECT-F009.md
    Full analysis with evidence chain, root cause, data examples
    (20-30 min read)

  REQUEST-basis-factsheet.md
    Provider adjustment-basis inventory (context for why values shift)
    (5-10 min read)

  REQUEST-event-capture.md
    Event capture proposal (background for Remedy R2)
    (5 min read)

Code & Tests:
  test_import_service_defect_f009.py
    Regression test harness (cases a & b)
    Runnable against the real HistFinTS codebase
    (see CONSULTANT-PACKAGE-F009.md for how to run)

================================================================================
WHAT WE'RE ASKING FOR
================================================================================

1. Independent verification of the defect mechanism
2. Evaluation of three proposed remedies:
   - R1: Periodic full-range re-fetch (complete fix, high cost)
   - R2: Event capture backfill (partial fix, lower cost)
   - R3: Detect-and-refuse consumer-side (gate against use, no upstream cost)
3. Recommendation on which approach is appropriate
4. Any guidance on implementation or risk mitigation

See CONSULTANT-PACKAGE-F009.md for detailed evaluation framework.

================================================================================
CONTEXT
================================================================================

Why this matters:
  - HistFinTS is a historical data store for financial time series
  - Research Workbench depends on it for reliable data in statistical analysis
  - A silent scale break (split, revision) makes data unreliable
  - No existing mechanism detects or marks these breaks

When does this occur:
  - A Series is backfilled before a stock split
  - Later, incremental import runs and fetches only new data
  - Pre-split rows are never re-fetched
  - Provider (Yahoo) returns post-split-adjusted prices for new rows
  - Result: permanent scale discontinuity, no correction row, no marker

Who is affected:
  - Any Series tracked through a basis-changing event (split, dividend, revision)
  - Yahoo Finance (stock splits) -- infrequent for US large-caps
  - FRED (economic indicator revisions)
  - CEDEAR/BYMA conversion-ratio changes -- fire quarterly by regulation (CNV RG
    1142/2026), plus ad hoc local ratio changes; a confirmed real instance already
    exists in this database. This is the higher-frequency trigger for this project's
    actual universe. See CONSULTANT-PACKAGE-F009.md ("Trigger Frequency") for detail.

Sequencing note:
  - Implementation order is not fully open, but the original D-008 tranche table has
    been superseded by D-019 -- Tranche 2 reduced to ONE item (adjustment-basis field),
    not four. That one item is now done. F-009 itself is Tranche 1 (gated only on the
    reproduction, satisfied by the included regression tests). R2 (event capture) was
    NEVER part of Tranche 2 -- it's explicitly excluded (filed separately as F-012,
    REQUEST-event-capture.md) and remains unscheduled. See CONSULTANT-PACKAGE-F009.md
    ("Sequencing: What's Already Decided") for the corrected picture before
    recommending an order from scratch.

================================================================================
CONTACT
================================================================================

Questions about the defect, test harness, or package contents:
  Contact: HistFinTS team (this review is part of a formal specification process)

The full decision log and spec is available in the Workbench repository:
  https://github.com/anthropics/histfints-workbench

Current status: Unfixed, dormant (no production Series yet affected)
Severity: High (data integrity issue, but no current impact)
Date filed: 2026-08-15

================================================================================
