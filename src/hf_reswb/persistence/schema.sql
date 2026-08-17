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

CREATE TABLE IF NOT EXISTS evidence_reference (
    id                    INTEGER PRIMARY KEY,
    calculation_id        INTEGER NOT NULL REFERENCES discontinuity_calculation(id),
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
