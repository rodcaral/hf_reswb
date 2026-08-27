# Class-E Identity-Detection Signal — Disposition-Framework Element 5

**Date:** 2026-08-21
**From:** SDT Workbench
**To:** SE
**Status: read-only evidence infrastructure. No mutation, staging, D execution, reassignment,
deletion, or provenance modification performed or authorized by this deliverable. All other
Class-E work (ADR/depositary-layer identity, observation-history disposition) remains held
pending DFA adjudication, per instruction.**

---

## 1. What was built

`src/hf_reswb/application/class_e_identity_signal.py` — a pure, DB-free classification
function, `detect_identity_candidates()`, following the same conventions as
`independence_detector.py` and `provenance_guard.py` (frozen dataclasses, `str, Enum` verdict
types with per-member docstrings, no direct database access — callers assemble input
snapshots separately).

**Primary signal**: `(provider_id, provider_series_identifier)` — an exact match between two
series' provider assignments is the strongest evidence this module produces, replacing the
free-text label match that was the prior, failure-prone signal.

**Secondary signal**: a known venue-suffix relation (default: `.BA`, the BYMA CEDEAR pattern
observed throughout this catalog) between two symbols on the same provider — evidence of a
related-but-distinct instrument (a CEDEAR referencing an underlying), not evidence the two are
the same stored feed.

**Supporting-only signal**: normalized label match (comma/period/whitespace-insensitive,
case-insensitive). This signal alone never elevates a pair above `UNRESOLVED` — it is attached
as corroborating detail when no provider-level evidence exists, never as an independent path
to `SAME_INSTRUMENT` or `RELATED_BUT_DISTINCT`.

## 2. Taxonomy reconciliation (3-way vs. 4-way)

SE's instruction specified the detector's output taxonomy as **same instrument /
related-but-distinct / unresolved** — three values, implemented directly as `IdentityVerdict`.
This is narrower than the four-way taxonomy used in the DFA-facing evidence matrix (`same
issuer / same financial instrument / related-but-distinct / unresolved`,
`CLASS_E_FULL_IDENTITY_MATRIX_2026-08-20.md`).

**Resolution**: the detector's `SAME_INSTRUMENT` corresponds to the matrix's "same financial
instrument" (provider+symbol identity — the evidence dimension decisive for Groups 5–11).
The matrix's "same issuer only" category (Groups 1–4: same underlying company, no
provider-symbol evidence available because these candidates have zero `provider_assignment`
rows of their own) has **no dedicated detector output** — it structurally resolves to
`UNRESOLVED`, with label evidence attached where present, because the detector has no
evidence dimension that can distinguish "same issuer, different instrument" from "unrelated"
without provider data to reason over. This is documented as a known ceiling, not a defect: the
matrix's finer four-way distinction depends on evidence (ADR/depositary-layer facts) this
detector does not have and was not asked to acquire. The detector's `UNRESOLVED` is therefore a
superset of the matrix's "same issuer only" and "unresolved" categories combined — narrowing
that further remains DFA/domain work, not a signal-detection problem.

## 3. Evidence semantics, exactly

| Verdict | What it means | What it does NOT mean |
|---|---|---|
| `SAME_INSTRUMENT` | The two series' provider assignments carry an identical `(provider_id, provider_series_identifier)` pair. | Not proof of financial identity; not authorization to merge, reassign, or deduplicate. Two series can share a provider address and still be the subject of an open DFA question (as Groups 5–11 currently are). |
| `RELATED_BUT_DISTINCT` | The two series share a provider and a symbol connected by a known venue-suffix pattern. | Not evidence they should be kept separate as a policy matter — only that the provider's own addressing treats them as different feeds. |
| `UNRESOLVED` | No provider-assignment evidence connects the pair. Normalized-label match, if present, is reported as supporting detail. | Not evidence of non-identity. A `provider_assignment`-less series (all four Class-C orphans) can never leave this category under this signal alone, regardless of how strong other evidence (e.g. issuer identity) might be. |

No candidate is returned for a pair with zero evidence of any kind — the function is a
candidate-discovery signal, not an exhaustive pairwise report, and its output is explicitly
**not a complete Class-E population** (consistent with every population count in this
project's Class-E work to date being stated as a lower bound, never a total).

## 4. False-positive / false-negative considerations

**False positives** (a candidate reported that is not actually a duplicate/relation):
- `SAME_INSTRUMENT` false positive would require two genuinely distinct securities to be
  independently assigned the identical provider symbol by the provider itself — a data-source
  error, not a detector error; the detector reports what the provider's own catalog says.
- `RELATED_BUT_DISTINCT` false positive: a coincidental symbol collision matching the suffix
  pattern (e.g. an unrelated ticker that happens to end in `.BA`) without an actual
  CEDEAR/underlying relationship. Mitigated by requiring the same `provider_id`, but not
  eliminated — this is why the verdict is `RELATED_BUT_DISTINCT`, an evidence classification,
  not a `SAME_ISSUER_CONFIRMED` claim.
- `UNRESOLVED` label-evidence false positive: two unrelated companies with a coincidentally
  identical normalized name. Bounded impact since `UNRESOLVED` never authorizes any action.

**False negatives** (a real relationship the detector misses):
- Two series can be genuinely related with neither a provider-symbol match nor a label match
  nor a recognized venue suffix (e.g. different providers, no suffix convention, dissimilar
  labels) — the detector reports no candidate at all in this case. This is the primary
  completeness gap and is why detector output is explicitly bounded as a lower bound, not a
  population.
- `DEFAULT_VENUE_SUFFIXES` covers only `.BA` (the one pattern empirically observed in this
  catalog). A relationship expressed through an unlisted suffix convention is invisible to the
  secondary signal and falls through to label-only evidence (`UNRESOLVED`) or nothing.

## 5. Tests

`tests/test_class_e_identity_signal.py` — 15 tests, grounded in real cases from this session:
- Provider-symbol identity: MU current-target (11342) vs. proposed-target (6672), both Yahoo
  Finance symbol `"MU"` → `SAME_INSTRUMENT`.
- Venue-suffix relation: MU referrer CEDEAR (11323, symbol `"MU.BA"`) vs. current target
  (11342, symbol `"MU"`) → `RELATED_BUT_DISTINCT`.
- Provider-symbol match takes precedence over a label mismatch (decisive-signal-first design).
- Different providers with an accidentally identical symbol do not match on the primary
  signal, fall through to label evidence.
- **Punctuation-miss regressions** (the exact failure mode this deliverable targets): BIDU-target
  (11346, zero `provider_assignment` rows, matching the real structural gap) vs. its real
  underlying (1169) resolves to `UNRESOLVED` with label evidence attached — not a silent false
  negative. MELI and AMZN's real comma-difference label pairs are caught as supporting
  evidence and correctly capped at `UNRESOLVED`.
- Structural guarantee test: even an exact label match, with zero provider evidence, cannot
  produce anything above `UNRESOLVED`.
- No-evidence pairs produce no candidate; empty input produces no candidates; blank labels do
  not spuriously match.
- Multi-series input evaluates each pair independently (candidate list, not a whole-population
  claim).

Full suite: 89 passed, 1 skipped, 1 pre-existing unrelated failure
(`test_ground_truth_against_real_production_series_11312`, series 11312's live
`configured_interval` value — flagged repeatedly in this project as pre-existing and
unrelated to any of this session's work), confirming zero regression against the established
baseline.

## 6. What this deliverable does not do

- Does not resolve, merge, reassign, delete, or rewrite provenance for any series.
- Does not execute or advance D.
- Does not extend or finalize the Class-E population count.
- Does not resolve the ADR/depositary-layer identity question or the observation-history
  disposition rule — both remain held pending DFA adjudication, per instruction.
- Does not assign any financial-domain conclusion to any verdict it produces — every verdict
  is an evidence classification over provider-catalog and label data, not a ruling.
