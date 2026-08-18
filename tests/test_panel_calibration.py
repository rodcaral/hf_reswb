"""Phase 5 calibration study framework tests (D-046).

Tests for calibration analysis and report generation framework.
These tests demonstrate the structure and usage of the calibration system
for staleness and dispersion threshold tuning.

Note: Full calibration study requires historical panel data. These tests
use synthetic data to verify the framework structure.
"""
from __future__ import annotations

import pytest

from hf_reswb.application.calibration_analyzer import (
    CalibrationReport,
    CalibrationRequest,
    DispersionDistribution,
    StalenessDistribution,
    ThresholdImpact,
)
from hf_reswb.application.calibration_utilities import (
    compute_staleness_statistics,
    estimate_threshold_impact,
)


class TestCalibrationDataStructures:
    """Test calibration data structure definitions."""

    def test_staleness_distribution_creation(self):
        """Create and use staleness distribution."""
        dist = StalenessDistribution(
            min_days=1,
            max_days=50,
            median_days=8,
            mean_days=10.5,
            p25_days=4,
            p75_days=15,
            p95_days=35,
            count_series=100,
            count_observations=5000,
        )

        assert dist.median_days == 8
        assert dist.p95_days == 35
        assert "median=8d" in dist.description

    def test_dispersion_distribution_creation(self):
        """Create and use dispersion distribution."""
        dist = DispersionDistribution(
            metric_name="coefficient_of_variation",
            min_value=0.01,
            max_value=0.50,
            median_value=0.08,
            mean_value=0.10,
            p25_value=0.04,
            p75_value=0.12,
            p95_value=0.25,
            count_panel_dates=6500,
            suppression_rate_at_p95=0.05,
        )

        assert dist.metric_name == "coefficient_of_variation"
        assert dist.suppression_rate_at_p95 == 0.05

    def test_threshold_impact_creation(self):
        """Create and use threshold impact."""
        impact = ThresholdImpact(
            parameter_name="staleness_policy",
            threshold_value=10,
            description="max_consecutive_no_trade_days=10",
            affected_dates=500,
            affected_series_count=45,
            avg_panel_depth_change=-0.08,
            min_panel_depth=8,
        )

        assert impact.threshold_value == 10
        assert impact.affected_series_count == 45
        assert "affects 500 dates" in impact.summary


class TestCalibrationReport:
    """Test calibration report structure and formatting."""

    def test_empty_report_creation(self):
        """Create an empty calibration report."""
        report = CalibrationReport(
            date_generated="2026-08-18T12:00:00Z",
            period_start="2000-01-01",
            period_end="2026-08-18",
        )

        assert report.title == "Panel Eligibility Calibration Study"
        assert not report.is_complete

    def test_complete_report_creation(self):
        """Create a complete calibration report."""
        staleness_dist = StalenessDistribution(
            min_days=1, max_days=50, median_days=8, mean_days=10.5,
            p25_days=4, p75_days=15, p95_days=35,
            count_series=100, count_observations=5000,
        )

        dispersion_dist = DispersionDistribution(
            metric_name="coefficient_of_variation",
            min_value=0.01, max_value=0.50, median_value=0.08,
            mean_value=0.10, p25_value=0.04, p75_value=0.12,
            p95_value=0.25, count_panel_dates=6500,
            suppression_rate_at_p95=0.05,
        )

        impacts = [
            ThresholdImpact(
                parameter_name="staleness_policy",
                threshold_value=5,
                description="max_consecutive_no_trade_days=5",
                affected_dates=800, affected_series_count=60,
                avg_panel_depth_change=-0.15, min_panel_depth=5,
            ),
            ThresholdImpact(
                parameter_name="staleness_policy",
                threshold_value=10,
                description="max_consecutive_no_trade_days=10",
                affected_dates=500, affected_series_count=45,
                avg_panel_depth_change=-0.08, min_panel_depth=8,
            ),
        ]

        report = CalibrationReport(
            date_generated="2026-08-18T12:00:00Z",
            period_start="2000-01-01",
            period_end="2026-08-18",
            staleness_distribution=staleness_dist,
            dispersion_distribution_cv=dispersion_dist,
            staleness_threshold_impacts=impacts,
            dispersion_threshold_impacts_cv=impacts[:1],
            staleness_recommendation="Recommend max_consecutive_no_trade_days=10 (median=8d, p95=35d)",
            dispersion_recommendation="Recommend coefficient_of_variation threshold=0.10 (median=0.08, p95=0.25)",
            caveats=[
                "Recommendation based on historical data 2000-2026, may not reflect current regime",
                "Zero-volume carry-forward observations handled per observation-suitability classification",
            ],
        )

        assert report.is_complete
        assert "Staleness Distribution" in report.format_markdown()
        assert "Coefficient of Variation" in report.format_markdown()


class TestCalibrationRequest:
    """Test calibration request structure."""

    def test_calibration_request_defaults(self):
        """Calibration request with defaults."""
        req = CalibrationRequest(
            period_start="2000-01-01",
            period_end="2026-08-18",
        )

        assert req.period_start == "2000-01-01"
        assert req.staleness_threshold_candidates == [5, 10, 15, 20, 25]
        assert req.dispersion_percentile_candidates == [50, 75, 90, 95]

    def test_calibration_request_custom(self):
        """Calibration request with custom parameters."""
        req = CalibrationRequest(
            period_start="2020-01-01",
            period_end="2026-08-18",
            panel_pairs=[(1, 11305), (2, 11314)],
            staleness_threshold_candidates=[7, 14, 21],
            dispersion_percentile_candidates=[80, 90],
        )

        assert len(req.panel_pairs) == 2
        assert req.staleness_threshold_candidates == [7, 14, 21]
        assert len(req.dispersion_percentile_candidates) == 2


class TestCalibrationUtilities:
    """Test calibration utility functions."""

    def test_staleness_statistics_computation(self):
        """Compute statistics from synthetic staleness data."""
        staleness_by_series = {
            1: [5, 10, 8, 12],
            2: [3, 7, 9],
            3: [15, 20],
        }

        stats = compute_staleness_statistics(staleness_by_series)

        assert stats["min"] == 3
        assert stats["max"] == 20
        # Mean = (5+10+8+12+3+7+9+15+20) / 9 = 89/9 ≈ 9.889
        assert stats["mean"] == pytest.approx(9.889, rel=0.01)
        assert stats["count_series"] == 3
        assert stats["count_gaps"] == 9

    def test_threshold_impact_estimation(self):
        """Estimate impact of candidate threshold."""
        stats = {
            "median": 8,
            "p95": 35,
            "mean": 10.5,
        }

        impact_5 = estimate_threshold_impact(stats, 5)
        impact_10 = estimate_threshold_impact(stats, 10)
        impact_20 = estimate_threshold_impact(stats, 20)

        # Higher threshold = lower impact
        assert impact_5["affected_proportion"] >= impact_10["affected_proportion"]
        assert impact_10["affected_proportion"] >= impact_20["affected_proportion"]

        # Specificity is complement of impact
        assert impact_5["specificity"] <= impact_10["specificity"]


class TestCalibrationReportFormatting:
    """Test calibration report formatting."""

    def test_report_markdown_formatting(self):
        """Verify Markdown formatting of complete report."""
        report = CalibrationReport(
            date_generated="2026-08-18T12:00:00Z",
            period_start="2000-01-01",
            period_end="2026-08-18",
            staleness_distribution=StalenessDistribution(
                min_days=1, max_days=50, median_days=8, mean_days=10.5,
                p25_days=4, p75_days=15, p95_days=35,
                count_series=100, count_observations=5000,
            ),
            staleness_recommendation="Recommend max_consecutive_no_trade_days=10",
            caveats=["Based on historical data", "May not reflect current regime"],
        )

        markdown = report.format_markdown()

        assert "# Panel Eligibility Calibration Study" in markdown
        assert "2026-08-18T12:00:00Z" in markdown
        assert "Staleness Distribution" in markdown
        assert "Staleness Threshold Recommendation" in markdown
        assert "Caveats and Limitations" in markdown
        assert "PROVISIONAL" in markdown
        assert "domain review and financial advisor approval" in markdown


class TestCalibrationWorkflow:
    """Integration test: calibration workflow."""

    def test_complete_calibration_workflow(self):
        """Demonstrate complete calibration workflow."""
        # Step 1: Create calibration request
        req = CalibrationRequest(
            period_start="2000-01-01",
            period_end="2026-08-18",
            staleness_threshold_candidates=[5, 10, 15, 20],
        )

        # Step 2: (In real usage) Analyze historical data
        # Simulated: create synthetic analysis results

        # Step 3: Build calibration report
        impacts = [
            ThresholdImpact(
                parameter_name="staleness_policy",
                threshold_value=t,
                description=f"max_consecutive_no_trade_days={t}",
                affected_dates=1000 - (t * 30),
                affected_series_count=80 - (t * 2),
                avg_panel_depth_change=-0.01 * t,
                min_panel_depth=10,
            )
            for t in req.staleness_threshold_candidates
        ]

        report = CalibrationReport(
            date_generated="2026-08-18T12:00:00Z",
            period_start=req.period_start,
            period_end=req.period_end,
            staleness_distribution=StalenessDistribution(
                min_days=1, max_days=50, median_days=8, mean_days=10.5,
                p25_days=4, p75_days=15, p95_days=35,
                count_series=100, count_observations=5000,
            ),
            dispersion_distribution_cv=DispersionDistribution(
                metric_name="coefficient_of_variation",
                min_value=0.01, max_value=0.50, median_value=0.08,
                mean_value=0.10, p25_value=0.04, p75_value=0.12,
                p95_value=0.25, count_panel_dates=6500,
                suppression_rate_at_p95=0.05,
            ),
            staleness_threshold_impacts=impacts,
            dispersion_threshold_impacts_cv=[
                ThresholdImpact(
                    parameter_name="dispersion_threshold",
                    threshold_value=0.10,
                    description="coefficient_of_variation=0.10",
                    affected_dates=325, affected_series_count=25,
                    avg_panel_depth_change=-0.05, min_panel_depth=12,
                )
            ],
            staleness_recommendation="Recommend max_consecutive_no_trade_days=10 based on p75=15d balance",
            dispersion_recommendation="Recommend coefficient_of_variation=0.10 (median=0.08, p95=0.25)",
            caveats=[
                "Based on historical data 2000-2026",
                "Does not reflect potential regime changes",
                "Zero-volume carry-forward handled per observation-suitability",
            ],
        )

        # Step 4: Verify report completeness
        assert report.is_complete

        # Step 5: (In real usage) Submit report for domain review
        markdown_output = report.format_markdown()
        assert "Panel Eligibility Calibration Study" in markdown_output
        assert len(report.caveats) > 0
