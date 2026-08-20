"""Tests for cross-sectional independence detection (F-033 safeguard infrastructure).

Synthetic data only. Cases are constructed to mirror the real patterns this project found
by hand: the F-033 exact-identity circularity, the 2026-08-19 returns-locked variant, and
genuinely independent CEDEARs (BABA/BIDU/UBER/GLD-style — correlated, never identical).
"""
from __future__ import annotations

from hf_reswb.application.independence_detector import (
    IndependenceFlag,
    classify_cohort_independence,
    day_over_day_returns,
    relative_range,
)


class TestRelativeRange:
    def test_identical_values_have_zero_range(self):
        assert relative_range([100.0, 100.0, 100.0]) == 0.0

    def test_empty_input_is_zero(self):
        assert relative_range([]) == 0.0

    def test_zero_median_is_zero_not_a_crash(self):
        assert relative_range([-1.0, 0.0, 1.0]) == 0.0

    def test_real_spread_is_nonzero(self):
        # Reproduces the F-033 magnitude order for the six-pair group's internal spread
        # once it stopped being exactly circular (2026-08-19): a real, computable range.
        r = relative_range([1010.48, 315.60, 52.57, 157.41, 13.21, 10.96, 790.94])
        assert r > 0.9


class TestDayOverDayReturns:
    def test_single_date_has_no_return(self):
        assert day_over_day_returns({"2026-01-01": 100.0}) == {}

    def test_computes_percent_change(self):
        returns = day_over_day_returns({"2026-01-01": 100.0, "2026-01-02": 110.0})
        assert returns == {"2026-01-02": 0.10}

    def test_zero_prior_value_skipped_not_crashed(self):
        returns = day_over_day_returns({"2026-01-01": 0.0, "2026-01-02": 5.0})
        assert returns == {}


class TestClassifyCohortIndependence:
    def test_exact_identity_flagged_f033_pattern(self):
        """Six series sharing one computed origin — the original F-033 signature: bit-
        identical implied FX on every date, drifting together over time."""
        shared_path = {"2026-05-29": 1008.55, "2026-06-01": 1008.63, "2026-08-17": 1010.48}
        cohort = {tk: dict(shared_path) for tk in ["MU", "MSFT", "AMD", "MELI", "AMZN", "NU"]}

        report = classify_cohort_independence(cohort)

        assert all(r.flag == IndependenceFlag.EXACT_IDENTITY for r in report.results)
        assert report.effective_independent_width == 1

    def test_returns_locked_but_different_levels_still_flagged(self):
        """The 2026-08-19 variant: exact-level identity resolved, but every series still
        moves by the identical percentage each day — a ratio fix cannot repair this because
        return correlation is scale-invariant."""
        base_path = {"2026-05-29": 1000.0, "2026-06-01": 1010.0, "2026-06-02": 1000.0}
        # Each series scaled by a different constant: identical returns, different levels.
        cohort = {
            "MU": {d: v * 1.0 for d, v in base_path.items()},
            "MSFT": {d: v * 0.05 for d, v in base_path.items()},
            "AMD": {d: v * 0.15 for d, v in base_path.items()},
            "MELI": {d: v * 0.013 for d, v in base_path.items()},
        }

        report = classify_cohort_independence(cohort)

        assert all(
            r.flag in (IndependenceFlag.RETURNS_LOCKED, IndependenceFlag.EXACT_IDENTITY)
            for r in report.results
        )
        assert report.effective_independent_width == 1

    def test_genuinely_independent_cohort_not_flagged(self):
        """BABA/BIDU/UBER/GLD-style: correlated (all drift with a shared macro factor) but
        never identical — the pattern this project verified as real, independent evidence."""
        cohort = {
            "BABA": {"2026-05-29": 174.0, "2026-06-01": 176.5, "2026-06-02": 173.2},
            "BIDU": {"2026-05-29": 142.0, "2026-06-01": 144.8, "2026-06-02": 141.1},
            "UBER": {"2026-05-29": 784.0, "2026-06-01": 795.3, "2026-06-02": 780.6},
            "GLD": {"2026-05-29": 31.4, "2026-06-01": 31.9, "2026-06-02": 31.2},
        }

        report = classify_cohort_independence(cohort)

        assert all(r.flag == IndependenceFlag.INDEPENDENT for r in report.results)
        assert report.effective_independent_width == 4

    def test_mixed_cohort_separates_locked_group_from_independent_outlier(self):
        """QQQ-style: six locked together, one genuinely distinct — effective width 2,
        matching this project's own F-033 finding (six-pair block + QQQ)."""
        shared_path = {"2026-05-29": 1008.55, "2026-06-01": 1008.63, "2026-06-02": 1008.70}
        cohort = {tk: dict(shared_path) for tk in ["MU", "MSFT", "AMD", "MELI", "AMZN", "NU"]}
        cohort["QQQ"] = {"2026-05-29": 1033.38, "2026-06-01": 1030.08, "2026-06-02": 1026.78}

        report = classify_cohort_independence(cohort)

        locked = [r for r in report.results if r.series_key != "QQQ"]
        qqq = next(r for r in report.results if r.series_key == "QQQ")

        assert all(r.flag == IndependenceFlag.EXACT_IDENTITY for r in locked)
        assert qqq.flag == IndependenceFlag.INDEPENDENT
        assert report.effective_independent_width == 2

    def test_empty_cohort_does_not_crash(self):
        report = classify_cohort_independence({})
        assert report.effective_independent_width == 0
        assert report.results == []
