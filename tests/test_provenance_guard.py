"""Tests for FK provenance verification (F-032/F-033 safeguard infrastructure).

Synthetic data mirroring the two real cases this project found by hand:
- `series.underlying_series_id` pointing to a near-duplicate of the source series itself
  (the corrupted FK both Workbench's F-033 finding and HistFinTS's initial audit walked
  into — see RECONCILIATION-F033-2026-08-19.md).
- A genuine, independently-sourced underlying (the pattern verified for AAPL/BABA/BIDU/
  UBER/GLD's real underlying series).
"""
from __future__ import annotations

from hf_reswb.application.provenance_guard import (
    OriginProvenanceVerdict,
    ProvenanceVerdict,
    classify_origin_provenance,
    verify_fk_target,
)

# The epoch empirically observed in the live database at the time this module was written
# (2026-08-20): first created_at carrying a non-NULL origin_import_run_id, with a clean
# cutover verified at that time. Tests use it as a realistic fixture value, not as a claim
# that it is a stable, HistFinTS-confirmed constant — see the module's dependency note.
OBSERVED_EPOCH = "2026-08-20T12:08:12.982123+00:00"


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


class TestClassifyOriginProvenance:
    """Row-level write provenance (observation.origin_import_run_id), added 2026-08-20
    (PRAGMA user_version = 15) in response to the import_run_id mutability issue. Distinct
    axis from verify_fk_target's series-level reference checks."""

    def test_populated_origin_is_recorded_regardless_of_date(self):
        """Real sample shape from the live database: a post-epoch row with
        origin_import_run_id == import_run_id (the normal case immediately after write,
        before any subsequent revalidation could diverge the two)."""
        result = classify_origin_provenance(
            observation_id=27968689,
            created_at="2026-08-20T12:08:12.982123+00:00",
            origin_import_run_id=69747,
            epoch=OBSERVED_EPOCH,
        )
        assert result.verdict == OriginProvenanceVerdict.ORIGIN_RECORDED

    def test_null_origin_before_epoch_is_historical_not_anomalous(self):
        """The overwhelming majority case as of 2026-08-20: 27,949,974 of 27,961,375
        observations (99.96%) predate the column's existence. Expected, not a defect."""
        result = classify_origin_provenance(
            observation_id=1,
            created_at="2026-08-19T23:27:28.537258+00:00",  # the observed latest pre-epoch NULL
            origin_import_run_id=None,
            epoch=OBSERVED_EPOCH,
        )
        assert result.verdict == OriginProvenanceVerdict.HISTORICAL_NULL_ORIGIN

    def test_null_origin_at_or_after_epoch_is_a_candidate_anomaly(self):
        """No live instance of this existed at the time this module was written (0 of
        11,401 post-epoch rows) -- this is the theoretical case the classification exists
        to catch if the pipeline ever fails to populate the column going forward."""
        result = classify_origin_provenance(
            observation_id=99999999,
            created_at="2026-08-20T12:08:13.000000+00:00",
            origin_import_run_id=None,
            epoch=OBSERVED_EPOCH,
        )
        assert result.verdict == OriginProvenanceVerdict.ORIGIN_MISSING_POST_EPOCH

    def test_epoch_boundary_is_exclusive_of_historical(self):
        """A row created exactly at the epoch, with NULL origin, counts as post-epoch (not
        historical) -- the historical case is strictly created_at < epoch."""
        result = classify_origin_provenance(
            observation_id=2,
            created_at=OBSERVED_EPOCH,
            origin_import_run_id=None,
            epoch=OBSERVED_EPOCH,
        )
        assert result.verdict == OriginProvenanceVerdict.ORIGIN_MISSING_POST_EPOCH

    def test_epoch_is_a_required_argument(self):
        """No module-level default epoch exists -- callers must supply one explicitly,
        per this module's caution against hardcoding an unconfirmed cutover."""
        import inspect

        sig = inspect.signature(classify_origin_provenance)
        assert sig.parameters["epoch"].default is inspect.Parameter.empty
