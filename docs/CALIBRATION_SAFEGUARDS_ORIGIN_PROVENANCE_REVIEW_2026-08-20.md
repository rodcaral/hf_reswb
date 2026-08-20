# Contract-Level Review: `classify_origin_provenance()`

**Date:** 2026-08-20
**Requested by:** SDT directive, treating five semantics as established (historical-NULL
non-exclusionary, post-epoch-NULL as the candidate condition, temporal-not-lexical
comparison, unparseable timestamps as a distinct diagnostic condition, application-level
but not database-enforced immutability).
**Nature of this document:** contract review for SE. **No integration into
`panel_eligibility_service.py`, calibration code, PRIMARY admissibility, or any production
policy path. No schema change, no epoch enforcement, no trigger, no historical
reconstruction.**

---

## (1) Was the current implementation internally correct?

**No — one real defect, found by this review, not assumed from the directive's framing.**

The prior implementation (`created_at < epoch`) was a **plain string comparison**, despite
its own docstring claiming compatibility ("lexicographically comparable... this function does
no timezone-aware parsing, only string comparison"). This is only safe when both values share
an identical format — same fractional-second digit count, same timezone-offset
representation. It silently breaks for two equally-valid ISO 8601 timestamps that represent
different instants correctly but don't sort the same way as strings: e.g. `created_at =
"2026-08-21T02:00:00+14:00"` (an instant temporally **before**
`epoch = "2026-08-20T12:08:12+00:00"`, once resolved to UTC) sorted as **string-greater**,
which would have misclassified a genuinely historical row as `ORIGIN_MISSING_POST_EPOCH`.

**No live instance of this defect firing was found** — all timestamps observed in the live
database follow one consistent format (`created_at` written by one code path), so the bug was
latent rather than actively producing wrong classifications today. It would have surfaced the
moment any caller supplied an epoch or created_at in a differently-formatted (but equally
valid) representation.

**Fixed in this review** (not previously): `created_at` and `epoch` are now parsed via
`datetime.fromisoformat` (with `Z`-suffix normalization) and compared as `datetime` objects.
Everything else in the prior implementation — the three-way verdict structure, the
`ORIGIN_RECORDED` short-circuit before any date handling, the required-keyword-only `epoch`
parameter with no module default — was already correct against the corrected semantics and is
unchanged.

---

## (2) Additive test/contract changes made

**Contract changes** (all additive, `OriginProvenanceVerdict` gains one member, no existing
member removed or renamed):

- Added `UNPARSEABLE_TIMESTAMP` — returned, never raised, when `created_at` or `epoch` fails
  to parse, **or** when the two are not safely comparable (one timezone-naive, one
  timezone-aware — a case the directive's "unparseable timestamps" language covers by
  implication: a value that parses individually but cannot be temporally ordered against the
  other is exactly as unusable for this classification as one that doesn't parse at all).
- `OriginProvenanceCheckResult` gains an optional `detail: str = ""` field, populated only on
  `UNPARSEABLE_TIMESTAMP`, naming which side failed and why — additive, defaults to `""` for
  every existing call site and test.
- Corrected the module's immutability claim: `origin_import_run_id` is now documented as
  "not overwritten by the current application write path... not a database-enforced
  guarantee... no trigger or constraint... prevents a future UPDATE" — replacing the prior,
  stronger, unqualified "intended to be set once and never overwritten." This matches the
  fifth established semantic exactly and corrects an overclaim in the original module
  docstring.

**Tests added** (6 new, all passing; `TestClassifyOriginProvenance` goes from 5 to 11 cases,
full file now 17 tests):

| Test | What it proves |
|---|---|
| `test_comparison_is_temporal_not_lexical` | The regression this review exists for — a string-later, temporally-earlier timestamp classifies correctly as historical |
| `test_z_suffix_and_offset_suffix_compare_correctly` | `Z`-suffix and offset-suffix timestamps compare correctly against each other |
| `test_garbage_created_at_is_unparseable_not_defaulted` | Malformed `created_at` → `UNPARSEABLE_TIMESTAMP`, not silently historical or post-epoch |
| `test_garbage_epoch_is_unparseable_not_defaulted` | Same, for a malformed `epoch` |
| `test_naive_vs_aware_mismatch_is_unparseable_not_guessed` | A naive/aware mismatch is flagged, not coerced by assumption |
| `test_populated_origin_short_circuits_before_any_parsing` | `ORIGIN_RECORDED` never depends on `created_at` being parseable — the origin check runs first |

No existing test was modified or removed; all 5 tests from the prior round still pass
unchanged (their fixture timestamps happen to be temporally consistent with their prior
lexical result, so the fix doesn't change their expected outcome — verified, not assumed).

---

## (3) Exact conditions before downstream eligibility integration could be considered

Stated as concrete, checkable conditions — not a recommendation to proceed, and not
attempted here:

1. **HistFinTS confirmation of the three open dependencies** already raised in the prior
   round (`CALIBRATION_SAFEGUARDS_ORIGIN_PROVENANCE_2026-08-20.md`): epoch monotonicity
   going forward, whether a historical backfill of `origin_import_run_id` is planned, and
   whether the field's immutability guarantee is expected to hold structurally or only by
   current application convention (this review's point 5 correction makes explicit that it is
   the latter, today).
2. **A decision on how `UNPARSEABLE_TIMESTAMP` should be treated** if it is ever wired to
   panel eligibility — this review deliberately leaves it unmapped to any `ExclusionReason`
   (diagnostic-only), and whether it should map to one, be treated as a data-quality defect
   report, or something else is an open design question for whoever does that integration,
   not settled by this infrastructure work.
3. **A decision on what `ORIGIN_MISSING_POST_EPOCH` should mean operationally** — it
   currently has zero observed instances in the live database, so its behavior under
   integration is entirely untested against real data. Before wiring it to an exclusion,
   someone should confirm what a real occurrence would actually indicate (an ingestion bug?
   a legitimate direct-write path this project hasn't accounted for?) rather than assuming
   the theoretical case matches the documented one.
4. **Explicit SE/DFA authorization**, per the standing instruction repeated in every round of
   this work — not a technical precondition, but the actual gating one.

---

## Distinction preserved throughout

Every verdict this module returns (`ORIGIN_RECORDED`, `HISTORICAL_NULL_ORIGIN`,
`ORIGIN_MISSING_POST_EPOCH`, `UNPARSEABLE_TIMESTAMP`) is diagnostic classification only.
`ExclusionReason.ORIGIN_PROVENANCE_MISSING` exists in the domain vocabulary (added in the
prior round) but is not assigned by this function or any other code path — the classifier
produces information; nothing in this codebase currently converts that information into an
admissibility decision.

## Verification

- Full suite: **74 passed** (68 baseline + 6 new), 1 skipped, 1 failed (the same
  pre-existing, unrelated `configured_interval='1h'` failure, untouched).
- `grep` for `origin_import_run_id`, `ORIGIN_PROVENANCE_MISSING`, `classify_origin_provenance`,
  `OriginProvenance`, `UNPARSEABLE_TIMESTAMP` across `panel_eligibility_service.py`,
  `panel_integration.py`, `calibration_analyzer.py`, `calibration_utilities.py`: zero matches.
- No schema change, no epoch-enforcement mechanism, no trigger, no historical reconstruction.
