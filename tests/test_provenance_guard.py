"""Tests for FK provenance verification (F-032/F-033 safeguard infrastructure).

Synthetic data mirroring the two real cases this project found by hand:
- `series.underlying_series_id` pointing to a near-duplicate of the source series itself
  (the corrupted FK both Workbench's F-033 finding and HistFinTS's initial audit walked
  into — see RECONCILIATION-F033-2026-08-19.md).
- A genuine, independently-sourced underlying (the pattern verified for AAPL/BABA/BIDU/
  UBER/GLD's real underlying series).
"""
from __future__ import annotations

from hf_reswb.application.provenance_guard import ProvenanceVerdict, verify_fk_target


class TestVerifyFkTarget:
    def test_duplicate_of_source_flagged(self):
        """The exact F-033 pattern: FK target's values equal the source's own values to
        within floating-point noise, on every common date."""
        source = {"2026-08-17": 1010.4760, "2026-08-18": 1011.62}
        fk_target = {"2026-08-17": 1010.4760, "2026-08-18": 1011.6199999999999}  # fp noise

        result = verify_fk_target(
            source_series_id=11323,
            fk_target_series_id=11342,
            source_values=source,
            fk_target_values=fk_target,
        )

        assert result.verdict == ProvenanceVerdict.SUSPECT_DUPLICATE_OF_SOURCE

    def test_genuinely_distinct_underlying_trusted(self):
        """A real underlying series (e.g. the actual MSFT common stock) — distinct values,
        plausible price range."""
        source = {"2026-08-17": 1010.4760, "2026-08-18": 1010.40}  # CEDEAR, ARS
        fk_target = {"2026-08-17": 495.40, "2026-08-18": 495.40}  # real underlying, USD

        result = verify_fk_target(
            source_series_id=11324,
            fk_target_series_id=6602,
            source_values=source,
            fk_target_values=fk_target,
            expected_min=15.0,
            expected_max=550.0,
        )

        assert result.verdict == ProvenanceVerdict.TRUSTED

    def test_distinct_but_implausible_range_flagged(self):
        """Distinct from the source (not a duplicate) but outside a supplied plausible
        range — e.g. a series labeled as a real-world instrument whose values don't match
        any known trading range for that instrument."""
        source = {"2026-08-17": 1010.48}
        fk_target = {"2026-08-17": 348.06}  # far outside a $15-$542 real MSFT range...

        result = verify_fk_target(
            source_series_id=11324,
            fk_target_series_id=99999,
            source_values=source,
            fk_target_values=fk_target,
            expected_min=15.0,
            expected_max=250.0,  # deliberately excludes 348.06
        )

        assert result.verdict == ProvenanceVerdict.IMPLAUSIBLE_RANGE

    def test_no_common_dates(self):
        result = verify_fk_target(
            source_series_id=1,
            fk_target_series_id=2,
            source_values={"2026-08-17": 100.0},
            fk_target_values={"2026-08-18": 100.0},
        )
        assert result.verdict == ProvenanceVerdict.NO_COMMON_DATES

    def test_trusted_without_range_check_when_none_supplied(self):
        """If no expected range is given, distinctness from the source alone is enough for
        TRUSTED — the range check is opt-in, not required."""
        result = verify_fk_target(
            source_series_id=1,
            fk_target_series_id=2,
            source_values={"2026-08-17": 1000.0},
            fk_target_values={"2026-08-17": 5.0},
        )
        assert result.verdict == ProvenanceVerdict.TRUSTED

    def test_dates_checked_reported(self):
        result = verify_fk_target(
            source_series_id=1,
            fk_target_series_id=2,
            source_values={"2026-08-17": 1000.0, "2026-08-18": 1010.0, "2026-08-19": 1005.0},
            fk_target_values={"2026-08-17": 5.0, "2026-08-18": 5.1},
        )
        assert result.dates_checked == 2
