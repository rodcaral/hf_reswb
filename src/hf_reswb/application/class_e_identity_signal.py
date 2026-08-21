"""Class-E identity-detection signal: provider identity + provider-side symbol.

Disposition-framework element 5 (`CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md` §"Minimum
Class-E disposition framework", item 5) — a corrected candidate-discovery signal, replacing
reliance on label-normalization alone, which was demonstrated (3 of 11 candidates checked:
BIDU, MELI, AMZN) to miss a duplicate relationship on a single comma's presence or absence.

This module does not resolve identity. It classifies the *strength of evidence* two series
carry toward being the same, related, or unrelated instrument, using the provider assignment
data itself rather than free-text labels as the primary signal. Label matching is retained
only as supporting evidence for the weakest category (`UNRESOLVED`) — it never elevates a
pair to `SAME_INSTRUMENT` or `RELATED_BUT_DISTINCT` on its own, because label text is not a
structured identity fact in this schema (D-003: no enforced FK, and per this project's own
finding, no structured issuer/CUSIP/ISIN field exists to check against).

**This module encodes no financial-domain conclusion.** `SAME_INSTRUMENT` is an evidence
classification ("these two series reference the identical provider symbol"), not a ruling that
they should be merged, and `RELATED_BUT_DISTINCT` is not a ruling that they should be kept
separate — both remain open questions for DFA. The detector performs no deletion, reassignment,
consolidation, provenance rewriting, or D execution, and cannot be used to do so — it returns
data, nothing else.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class IdentityVerdict(str, Enum):
    SAME_INSTRUMENT = "SAME_INSTRUMENT"
    """Two series carry an identical (provider_id, provider_series_identifier) pair between
    them. The strongest signal this detector produces — matching the evidence dimension that
    was decisive for the seven D-contingent candidates (current target vs. proposed target,
    both requesting the identical Yahoo Finance symbol). Not proof of financial identity by
    itself — it is proof that the provider's own addressing scheme does not distinguish the
    two series, which this project has treated as strong corroborating evidence, not as a
    conclusion."""

    RELATED_BUT_DISTINCT = "RELATED_BUT_DISTINCT"
    """Two series share a provider and a symbol related by a known venue-suffix pattern (e.g.
    one requests `"MU"`, the other `"MU.BA"` from the same provider) — consistent with a
    CEDEAR/underlying-style relationship (a real, structurally different instrument
    referencing the same issuer's security through a different listing/venue), not with being
    the same stored feed. This is evidence of relatedness, not evidence the two should be
    treated as interchangeable."""

    UNRESOLVED = "UNRESOLVED"
    """No provider-assignment-level evidence connects the two series (most commonly because
    one or both have no provider assignment at all — the exact structural gap found for all
    four present-state Class-C orphan candidates). Label-text similarity, if present, is
    attached as supporting evidence only — per this module's design, label evidence alone
    never elevates a pair above UNRESOLVED, because it has already been shown to be an
    unreliable signal on its own (the punctuation-sensitivity failure)."""


DEFAULT_VENUE_SUFFIXES: frozenset[str] = frozenset({".BA"})
"""Empirically observed in this catalog (BYMA CEDEAR provider-symbol suffix) — not a general
financial-industry convention. Passed as a parameter, not hardcoded silently, so a caller
extending this to other venues states the assumption explicitly rather than inheriting it."""


@dataclass(frozen=True)
class ProviderAssignmentSnapshot:
    provider_id: int
    provider_series_identifier: str


@dataclass(frozen=True)
class SeriesIdentitySnapshot:
    series_id: int
    label: str
    assignments: tuple[ProviderAssignmentSnapshot, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class IdentityCandidate:
    series_a: int
    series_b: int
    verdict: IdentityVerdict
    provider_symbol_evidence: str | None
    label_evidence: str | None
    detail: str


def normalize_label(label: str) -> str:
    """Punctuation-insensitive, case-insensitive normalization — deliberately narrow: it
    removes exactly the class of difference demonstrated to cause a false negative (commas,
    periods, and extra whitespace), not a broad fuzzy-match. Does not strip corporate suffixes
    ("Inc.", "Ltd.") or reorder words — a stricter normalization risks new, undemonstrated
    false positives, which this module does not trade for the punctuation fix without
    separate evidence that a broader normalization is warranted."""
    return re.sub(r"[,\.\s]+", " ", label).strip().lower()


def _provider_symbol_pairs(snapshot: SeriesIdentitySnapshot) -> set[tuple[int, str]]:
    return {(a.provider_id, a.provider_series_identifier) for a in snapshot.assignments}


def _related_by_suffix(
    a: SeriesIdentitySnapshot, b: SeriesIdentitySnapshot, venue_suffixes: frozenset[str]
) -> str | None:
    for pa in a.assignments:
        for pb in b.assignments:
            if pa.provider_id != pb.provider_id:
                continue
            for suffix in venue_suffixes:
                if pa.provider_series_identifier == pb.provider_series_identifier + suffix:
                    return (
                        f"provider {pa.provider_id}: series {a.series_id} symbol "
                        f"{pa.provider_series_identifier!r} vs. series {b.series_id} symbol "
                        f"{pb.provider_series_identifier!r} (suffix {suffix!r})"
                    )
                if pb.provider_series_identifier == pa.provider_series_identifier + suffix:
                    return (
                        f"provider {pa.provider_id}: series {b.series_id} symbol "
                        f"{pb.provider_series_identifier!r} vs. series {a.series_id} symbol "
                        f"{pa.provider_series_identifier!r} (suffix {suffix!r})"
                    )
    return None


def detect_identity_candidates(
    series: list[SeriesIdentitySnapshot],
    *,
    venue_suffixes: frozenset[str] = DEFAULT_VENUE_SUFFIXES,
) -> list[IdentityCandidate]:
    """Evaluate every unordered pair in `series` and return a candidate for every pair
    carrying at least one form of evidence (provider-symbol match, suffix relation, or
    normalized-label match). Pairs with no evidence at all are not returned — this is a
    candidate-discovery signal, not an exhaustive pairwise report.

    Returns:
        A list of `IdentityCandidate`, each an evidence classification, not a disposition.
        **Not a complete Class-E population** — a candidate list from this function should be
        treated as a lower bound, the same standing caution applied to every count in this
        project's Class-E work to date.
    """
    candidates: list[IdentityCandidate] = []
    for i in range(len(series)):
        for j in range(i + 1, len(series)):
            a, b = series[i], series[j]

            shared = _provider_symbol_pairs(a) & _provider_symbol_pairs(b)
            if shared:
                provider_id, identifier = next(iter(shared))
                candidates.append(
                    IdentityCandidate(
                        series_a=a.series_id,
                        series_b=b.series_id,
                        verdict=IdentityVerdict.SAME_INSTRUMENT,
                        provider_symbol_evidence=(
                            f"both reference provider {provider_id}, symbol {identifier!r}"
                        ),
                        label_evidence=None,
                        detail="identical (provider_id, provider_series_identifier) pair",
                    )
                )
                continue

            suffix_evidence = _related_by_suffix(a, b, venue_suffixes)
            if suffix_evidence:
                candidates.append(
                    IdentityCandidate(
                        series_a=a.series_id,
                        series_b=b.series_id,
                        verdict=IdentityVerdict.RELATED_BUT_DISTINCT,
                        provider_symbol_evidence=suffix_evidence,
                        label_evidence=None,
                        detail="venue-suffix-related provider symbols, same provider",
                    )
                )
                continue

            if normalize_label(a.label) == normalize_label(b.label) and a.label and b.label:
                candidates.append(
                    IdentityCandidate(
                        series_a=a.series_id,
                        series_b=b.series_id,
                        verdict=IdentityVerdict.UNRESOLVED,
                        provider_symbol_evidence=None,
                        label_evidence=(
                            f"normalized label match: {normalize_label(a.label)!r}"
                        ),
                        detail=(
                            "no provider-assignment evidence connects these series; label "
                            "match is supporting evidence only and does not by itself "
                            "establish identity"
                        ),
                    )
                )

    return candidates
