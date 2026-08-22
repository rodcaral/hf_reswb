# G1/G9 Final Domain Ruling — Financial Identity and Duplicate Detection

**Status:** Final DFA requirements-adjudication ruling  
**Scope:** Financial identity evidence, duplicate detection, and automatic identity resolution  
**Authorization:** Automatic resolution authorized in principle; current production eligibility not authorized. No remediation or data mutation authorized.

## 1. Identity conclusion states

The three financial identity conclusions remain distinct and must not be conflated:

- **`SAME_INSTRUMENT`** — Authoritative evidence establishes that the two Series represent the same financial instrument.
- **`RELATED_BUT_DISTINCT`** — Authoritative evidence establishes a meaningful financial relationship and a material security/instrument distinction.
- **`UNRESOLVED`** — Evidence is insufficient, unavailable, stale, contradictory, or otherwise unsuitable to establish either conclusion.

## 2. Authoritative evidence hierarchy

Financial identity evidence takes precedence over provider/catalog representation. A provider symbol is an addressing mechanism unless independently documented as an authoritative security identifier.

### Tier 1 — Primary/security-level authoritative evidence

- Issuer or security-program documentation.
- Regulated exchange/listing documentation.
- Regulatory filings or official depositary/program documentation.
- Authoritative structured security identifiers whose semantics and issuer/security mapping are independently established.

These sources may establish identity-bearing dimensions directly.

### Tier 2 — Authoritative structured market-data evidence

Structured provider/catalog data may establish a dimension when its semantics are documented and the provider mapping is sufficiently authoritative for that dimension. It normally corroborates Tier 1 rather than overriding it.

### Tier 3 — Provider operational evidence

Provider symbol, assignment, ticker, label, normalized symbol, import path, and similar operational metadata are supporting/candidate evidence, not primary financial identity evidence.

### Tier 4 — Analytical inference

Correlation, price similarity, timestamps, inferred venue, label parsing, ticker normalization, common provenance, and similar calculations can detect candidates or corroborate a conclusion, but cannot establish financial identity by themselves.

## 3. Precedence when sources disagree

There is no universal rule such as provider A beats provider B. Precedence follows authority for the particular identity dimension.

Temporal validity is part of the evidence. A historically correct document does not establish identity for a later period if the instrument or listing subsequently changed.

Where two genuinely authoritative sources covering the same identity dimension conflict and the conflict cannot be resolved by effective date/version, the result is:

**`UNRESOLVED`** — not majority vote, latest-provider-wins, or implementation convenience.

## 4. Identity dimensions

The evaluator should assess, independently:

1. Issuer/security identity
2. Instrument class/subtype
3. Listing/venue
4. Currency/denomination or documented equivalence
5. Provider identifier where relevant
6. Adjustment/conversion basis where representation depends on it
7. Material corporate-action/effective-date history

## 5. Minimum evidence for automatic `SAME_INSTRUMENT`

Automatic financial-identity resolution is permissible in principle only when a security-level identity is established by authoritative evidence, with no material contradictory evidence, and all identity dimensions that could distinguish the two representations are either established as equivalent or demonstrated to be irrelevant.

At minimum this requires:

- Authoritative support for issuer/security identity.
- Authoritative support for compatible instrument class/subtype.
- Relevant listing/security relationship established.
- Currency/denomination or documented equivalence established.
- Adjustment/conversion basis established where representation depends on it.
- Material corporate-action/effective-date history established where relevant.
- No material contradictory evidence.
- Provider identifiers may corroborate but cannot substitute for missing security identity.

## 6. Minimum evidence for automatic `RELATED_BUT_DISTINCT`

Automatic `RELATED_BUT_DISTINCT` is permissible only when:

1. Authoritative evidence establishes a meaningful relationship.
2. Authoritative evidence establishes at least one material security/instrument distinction.
3. The distinction is not merely a provider naming convention.
4. No unresolved evidence could reasonably reverse the conclusion.

Typical examples include an issuer's ordinary share versus a separately identified ADR/ADS, or two securities with a documented depositary relationship but distinct security identities.

Correlation, ticker differences, or labels alone cannot establish this state.

## 7. Mandatory `UNRESOLVED` conditions

`UNRESOLVED` is mandatory when:

- Security identity cannot be independently established.
- A mandatory identity dimension is unavailable.
- Authoritative evidence conflicts.
- Relevant evidence is stale or its effective period is unknown.
- ADR/ADS/CEDEAR/depositary status is unresolved where it matters.
- Denomination or conversion basis is material but unknown.
- Adjustment basis is material but unknown.
- Corporate-action history could have changed identity/representation and cannot be established.
- The conclusion depends on an analyst-only transformation.
- The only positive evidence is provider symbol, label, or provenance similarity.
- Evidence supports economic relatedness but cannot establish whether the securities are identical or distinct.

**`UNKNOWN` must not become `DIFFERENT`.** Missing evidence is not evidence of non-identity.

## 8. Detection and adjudication boundary

### Detection may

- Discover candidate pairs.
- Collect evidence.
- Classify evidence quality.
- Produce an evidence matrix.
- Produce a technical candidate signal.

### Detection must not

- Modify Series.
- Modify observations.
- Modify provider assignments.
- Modify provenance.
- Merge or delete records.
- Reassign observations.
- Silently convert technical evidence into a financial disposition.

## 9. Current HistFinTS consequence

HistFinTS currently does not have sufficient structured authoritative evidence to enable broad automatic financial-identity resolution.

The immediate technical requirement is to preserve the evidence matrix and three identity states while keeping automatic resolution disabled unless the authoritative evidence prerequisites are actually present.

For **10165 ↔ 11340**, the financial disposition remains **`UNRESOLVED`**. Its technical provider signal remains candidate evidence, not financial identity proof.

## 10. Final ruling

Automatic financial-identity resolution is permissible, but only as an evidence-gated operation based on authoritative, temporally valid security identity evidence.

Provider/catalog signals may discover candidates and corroborate conclusions, but cannot independently resolve them.

Conflicting or materially incomplete authoritative evidence must produce **`UNRESOLVED`**.

**No remediation or data mutation is authorized by this ruling.**

## 11. Required implementation posture

The next technical increment may define and test the read-only evidence/state evaluator.

Automatic resolution must remain disabled by default. Any subsequent production activation requires a separate scope/authorization decision after the required evidence sources and their semantics are established.
