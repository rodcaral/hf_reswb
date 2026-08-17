-- Workbench-owned evidence-consumption tables (SPEC-f009-evidence-consumption.md §2.2, D-033).
--
-- Stores upstream KEYS and the Workbench's own CALCULATED numbers. Never a copy of
-- historical HistFinTS observation values beyond the specific two values a finding's own
-- arithmetic is about — that exception is deliberate (D-033): a finding that cannot restate
-- its own calculation is not traceable, and re-deriving it later against mutated upstream
-- data would silently change what the finding said.

CREATE TABLE IF NOT EXISTS discontinuity_calculation (
    id                              INTEGER PRIMARY KEY,
    series_id                       INTEGER NOT NULL,
    period_start                    TEXT NOT NULL,
    period_end                      TEXT NOT NULL,
    boundary_date                   TEXT NOT NULL,
    value_before                    REAL NOT NULL,
    value_after                     REAL NOT NULL,
    step_factor                     REAL NOT NULL,
    persistence_horizon_days_1      INTEGER NOT NULL,
    persistence_horizon_days_2      INTEGER NOT NULL,
    persisted                       INTEGER NOT NULL CHECK (persisted IN (0, 1)),
    step_threshold                  REAL NOT NULL,
    tolerance                       REAL NOT NULL,
    calendar_basis                  TEXT NOT NULL,
    code_version                    TEXT NOT NULL,
    evidence_observation_before_id  INTEGER NOT NULL,  -- histfints.observation.id
    evidence_observation_after_id   INTEGER NOT NULL,  -- histfints.observation.id
    created_at                      TEXT NOT NULL
);

-- calculation_id is nullable: F-009's reconciler always sets it (a finding's evidence),
-- but SPEC-observation-suitability.md (D-038) reuses this same pointer type for
-- classification evidence that has no discontinuity_calculation at all. Reusing one
-- pointer type rather than inventing a second is deliberate (SPEC-observation-
-- suitability.md §6). This does not change F-009 reconciler behaviour -- it always
-- passes calculation_id, so its rows are unaffected; see tests/test_reconciliation_
-- boundary.py, still 5/5 after this change.
CREATE TABLE IF NOT EXISTS evidence_reference (
    id                    INTEGER PRIMARY KEY,
    calculation_id        INTEGER REFERENCES discontinuity_calculation(id),
    histfints_object      TEXT NOT NULL CHECK (histfints_object IN (
                               'OBSERVATION', 'CORRECTION', 'IMPORT_RUN',
                               'PROVIDER_ASSIGNMENT', 'PROVIDER_EVENT', 'OBSERVATION_CORRECTION'
                           )),
    histfints_id          INTEGER,             -- NULL exactly when resolution_state = TABLE_ABSENT
    histfints_series_id   INTEGER NOT NULL,
    resolution_state      TEXT NOT NULL CHECK (resolution_state IN (
                               'RESOLVED', 'MISSING', 'TABLE_ABSENT', 'SERIES_ARCHIVED'
                           )),
    resolved_at           TEXT NOT NULL,
    detail                TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_evidence_reference_calculation
    ON evidence_reference (calculation_id);

-- Observation-suitability tables (SPEC-observation-suitability.md §6, D-038).
-- Axis A (trade_evidence) is row-local; Axis B (session_status) is downstream of a
-- derived venue calendar. Never a copy of an observation's value (§6.1) -- the equality
-- assertions are restatable from the two named evidence_reference rows.

CREATE TABLE IF NOT EXISTS calendar_derivation (
    id                       INTEGER PRIMARY KEY,
    venue                    TEXT NOT NULL,                -- MIC, e.g. XBUE/XNYS -- P4 Asserted (D-037e)
    contributing_series_ids  TEXT NOT NULL,                -- JSON array of histfints series ids
    quorum_rule              TEXT NOT NULL,
    period_start             TEXT NOT NULL,
    period_end               TEXT NOT NULL,
    confidence_band          TEXT NOT NULL CHECK (confidence_band IN (
                                  'AUTHORITATIVE', 'RELIABLE', 'USABLE_WITH_CAVEAT', 'UNRESOLVED'
                              )),
    derived_at               TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS suitability_run (
    id                              INTEGER PRIMARY KEY,
    series_id                       INTEGER NOT NULL,
    period_start                    TEXT NOT NULL,
    period_end                      TEXT NOT NULL,
    rule_version                    TEXT NOT NULL,
    calendar_derivation_id          INTEGER REFERENCES calendar_derivation(id),
    count_trade_observed            INTEGER NOT NULL,
    count_no_trade_reported         INTEGER NOT NULL,
    count_trade_evidence_unresolved INTEGER NOT NULL,
    created_at                      TEXT NOT NULL
);

-- Absence of an observation_suitability row is ambiguous between "classified as
-- ordinary" and "never classified" without suitability_run to say what was covered
-- (§6, the D-009b trap named explicitly in the spec).
CREATE TABLE IF NOT EXISTS observation_suitability (
    id                            INTEGER PRIMARY KEY,
    suitability_run_id            INTEGER NOT NULL REFERENCES suitability_run(id),
    evidence_reference_id         INTEGER NOT NULL REFERENCES evidence_reference(id),
    prior_evidence_reference_id   INTEGER REFERENCES evidence_reference(id),
    histfints_series_id           INTEGER NOT NULL,
    observed_date                 TEXT NOT NULL,
    trade_evidence                TEXT NOT NULL CHECK (trade_evidence IN (
                                       'TRADE_OBSERVED', 'NO_TRADE_REPORTED', 'TRADE_EVIDENCE_UNRESOLVED'
                                   )),
    volume_unreliable             INTEGER NOT NULL CHECK (volume_unreliable IN (0, 1)),
    session_status                TEXT NOT NULL CHECK (session_status IN (
                                       'SESSION_CONFIRMED', 'SESSION_ABSENT', 'SESSION_UNRESOLVED'
                                   )),
    basis                         TEXT NOT NULL,   -- comma-joined conjuncts: VOLUME_ZERO,OHLC_COLLAPSED,EQUALS_PRIOR_CLOSE
    calendar_derivation_id        INTEGER REFERENCES calendar_derivation(id),
    rule_version                  TEXT NOT NULL,
    classified_at                 TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_observation_suitability_run
    ON observation_suitability (suitability_run_id);
CREATE INDEX IF NOT EXISTS idx_observation_suitability_series_date
    ON observation_suitability (histfints_series_id, observed_date);

-- Derived, not authoritative (§6): a display warns on run length, not row count.
CREATE TABLE IF NOT EXISTS no_trade_run (
    id                           INTEGER PRIMARY KEY,
    histfints_series_id          INTEGER NOT NULL,
    first_date                   TEXT NOT NULL,
    last_date                    TEXT NOT NULL,
    length                       INTEGER NOT NULL,
    first_evidence_reference_id  INTEGER NOT NULL REFERENCES evidence_reference(id),
    last_evidence_reference_id   INTEGER NOT NULL REFERENCES evidence_reference(id),
    suitability_run_id           INTEGER NOT NULL REFERENCES suitability_run(id),
    created_at                   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analytical_finding (
    id                    INTEGER PRIMARY KEY,
    calculation_id        INTEGER NOT NULL REFERENCES discontinuity_calculation(id),
    verdict               TEXT NOT NULL CHECK (verdict IN (
                               'explained by captured evidence',
                               'not explained by captured evidence',
                               'insufficient evidence'
                           )),
    reason_code           TEXT NOT NULL,
    correlation_tolerance REAL,
    residual              REAL,
    created_at            TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_analytical_finding_calculation
    ON analytical_finding (calculation_id);
