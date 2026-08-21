"""Tests for the Class-E identity-detection signal (disposition-framework element 5).

Fixtures are grounded in real cases established during this session's Class-E work, not
synthetic data: the MU current-target/proposed-target pair (identical Yahoo Finance symbol,
Groups 5-11 pattern), the MU referrer-CEDEAR/current-target pair (`.BA`-suffix relation), and
the three demonstrated punctuation-normalization misses (BIDU, MELI, AMZN — see
`CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`).
"""
from __future__ import annotations

from hf_reswb.application.class_e_identity_signal import (
    IdentityVerdict,
    ProviderAssignmentSnapshot,
    SeriesIdentitySnapshot,
    detect_identity_candidates,
    normalize_label,
)

YAHOO = 1


def snap(series_id: int, label: str, assignments: tuple = ()) -> SeriesIdentitySnapshot:
    return SeriesIdentitySnapshot(series_id=series_id, label=label, assignments=assignments)


def assign(symbol: str) -> tuple[ProviderAssignmentSnapshot, ...]:
    return (ProviderAssignmentSnapshot(provider_id=YAHOO, provider_series_identifier=symbol),)


class TestNormalizeLabel:
    def test_strips_comma_difference(self) -> None:
        assert normalize_label("Baidu Inc.") == normalize_label("Baidu, Inc.")

    def test_case_insensitive(self) -> None:
        assert normalize_label("MercadoLibre Inc.") == normalize_label("MERCADOLIBRE INC")

    def test_distinct_labels_remain_distinct(self) -> None:
        assert normalize_label("Micron Technology Inc.") != normalize_label("Advanced Micro Devices Inc.")


class TestDetectIdentityCandidatesProviderSymbol:
    def test_identical_provider_symbol_is_same_instrument(self) -> None:
        # MU current target (11342) vs. proposed target (6672): both Yahoo, symbol "MU".
        current_target = snap(11342, "Micron Technology Inc.", assign("MU"))
        proposed_target = snap(6672, "Micron Technology, Inc.", assign("MU"))
        candidates = detect_identity_candidates([current_target, proposed_target])
        assert len(candidates) == 1
        assert candidates[0].verdict == IdentityVerdict.SAME_INSTRUMENT
        assert candidates[0].provider_symbol_evidence is not None
        assert candidates[0].label_evidence is None

    def test_venue_suffix_relation_is_related_but_distinct(self) -> None:
        # MU referrer CEDEAR (11323, "MU.BA") vs. current target (11342, "MU"): same provider,
        # BYMA-suffix relation — a real, structurally different instrument, not identity.
        referrer = snap(11323, "Micron Technology CEDEAR", assign("MU.BA"))
        current_target = snap(11342, "Micron Technology Inc.", assign("MU"))
        candidates = detect_identity_candidates([referrer, current_target])
        assert len(candidates) == 1
        assert candidates[0].verdict == IdentityVerdict.RELATED_BUT_DISTINCT
        assert candidates[0].label_evidence is None

    def test_provider_symbol_match_takes_precedence_over_label_mismatch(self) -> None:
        # Even with dissimilar labels, an identical provider symbol is still decisive.
        a = snap(1, "Alpha Corp", assign("XYZ"))
        b = snap(2, "Totally Different Name Ltd", assign("XYZ"))
        candidates = detect_identity_candidates([a, b])
        assert candidates[0].verdict == IdentityVerdict.SAME_INSTRUMENT

    def test_different_providers_same_symbol_not_matched(self) -> None:
        a = snap(1, "Alpha Corp", (ProviderAssignmentSnapshot(provider_id=1, provider_series_identifier="XYZ"),))
        b = snap(2, "Alpha Corp", (ProviderAssignmentSnapshot(provider_id=2, provider_series_identifier="XYZ"),))
        candidates = detect_identity_candidates([a, b])
        # No provider-symbol evidence (different providers); falls through to label evidence.
        assert len(candidates) == 1
        assert candidates[0].verdict == IdentityVerdict.UNRESOLVED
        assert candidates[0].label_evidence is not None


class TestPunctuationMissRegressions:
    """The exact failure mode disposition-framework element 5 was commissioned to eliminate:
    a naive label match built from a candidate's own text missed its true duplicate purely
    because of a comma difference (BIDU, MELI, AMZN — 3 of 11 candidates checked)."""

    def test_bidu_zero_provider_assignments_resolves_unresolved_not_false_negative(self) -> None:
        # BIDU-target (11346) has zero provider_assignment rows of its own — the structural
        # gap shared by all four present-state Class-C orphans (Groups 1-4).
        bidu_target = snap(11346, "Baidu Inc.")
        real_underlying = snap(1169, "Baidu, Inc.")
        candidates = detect_identity_candidates([bidu_target, real_underlying])
        assert len(candidates) == 1
        assert candidates[0].verdict == IdentityVerdict.UNRESOLVED
        assert candidates[0].label_evidence is not None
        assert candidates[0].provider_symbol_evidence is None

    def test_meli_punctuation_miss_now_caught_as_supporting_evidence(self) -> None:
        a = snap(1, "MercadoLibre Inc.")
        b = snap(2, "MercadoLibre, Inc.")
        candidates = detect_identity_candidates([a, b])
        assert candidates[0].verdict == IdentityVerdict.UNRESOLVED
        assert normalize_label("MercadoLibre Inc.") in candidates[0].label_evidence

    def test_amzn_punctuation_miss_now_caught_as_supporting_evidence(self) -> None:
        a = snap(1, "Amazon.com Inc.")
        b = snap(2, "Amazon.com, Inc.")
        candidates = detect_identity_candidates([a, b])
        assert candidates[0].verdict == IdentityVerdict.UNRESOLVED

    def test_label_evidence_never_elevates_above_unresolved(self) -> None:
        # Structural guarantee: with no provider-assignment evidence at all, no label
        # similarity (however exact) can produce SAME_INSTRUMENT or RELATED_BUT_DISTINCT.
        a = snap(1, "Identical Label Co")
        b = snap(2, "Identical Label Co")
        candidates = detect_identity_candidates([a, b])
        assert candidates[0].verdict == IdentityVerdict.UNRESOLVED


class TestNoEvidenceNoCandidate:
    def test_unrelated_series_produce_no_candidate(self) -> None:
        a = snap(1, "Alpha Corp", assign("AAA"))
        b = snap(2, "Beta Corp", assign("BBB"))
        candidates = detect_identity_candidates([a, b])
        assert candidates == []

    def test_empty_input_produces_no_candidates(self) -> None:
        assert detect_identity_candidates([]) == []

    def test_blank_labels_do_not_spuriously_match(self) -> None:
        a = snap(1, "")
        b = snap(2, "")
        assert detect_identity_candidates([a, b]) == []


class TestOutputIsCandidateListNotPopulation:
    def test_multiple_pairs_each_evaluated_independently(self) -> None:
        current_target = snap(11342, "Micron Technology Inc.", assign("MU"))
        proposed_target = snap(6672, "Micron Technology, Inc.", assign("MU"))
        unrelated = snap(999, "Nothing To Do With Micron", assign("ZZZ"))
        candidates = detect_identity_candidates([current_target, proposed_target, unrelated])
        assert len(candidates) == 1
        assert {candidates[0].series_a, candidates[0].series_b} == {11342, 6672}
