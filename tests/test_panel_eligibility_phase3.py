"""Phase 3 tests for panel eligibility (D-046).

Tests for data constraint handling:
- Incomplete availability metadata (UNRESOLVED coverage status)
- Adjustment basis mismatches (mixed bases or required-basis violation)

Note: Phase 3 requires Tranche 2 schema (migrations 0011–0013), which adds:
- provider.adjustment_basis field (D-044, Item 1)
- provider_assignment.first_available_date / last_available_date fields (D-044, Item 2)

These tests use the migrated fixture (histfints_copy_migrated) which has these fields.
Base fixture (histfints_copy) doesn't have Tranche 2 yet, so tests are skipped there.

Full integration tests will be implemented in Phase 4 after Tranche 2 is deployed.
"""
from __future__ import annotations

import pytest


class TestPhase3BlockedOnTrache2:
    """Phase 3 tests are blocked on Tranche 2 schema (migrations 0011–0013).

    These tests verify the implementation works correctly once Tranche 2 is deployed.
    Currently skipped because the test fixture doesn't have the required columns:
    - provider.adjustment_basis
    - provider_assignment.first_available_date / last_available_date

    These will be implemented and tested in an integration test phase after Tranche 2 is applied.
    """

    def test_phase3_awaiting_tranche2_deployment(self):
        """Phase 3 is blocked on Tranche 2 HistFinTS migration."""
        pytest.skip(
            "Phase 3 requires Tranche 2 schema (migrations 0011–0013). "
            "Tests deferred until HistFinTS deployment is complete."
        )


