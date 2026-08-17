# Investigation: Rava as a Data Provider for HistFinTS

**Date:** 2026-08-17  
**Objective:** Empirical test to understand Rava's data availability and API for potential HistFinTS integration  
**Status:** Investigation complete — Rava not suitable for direct integration

---

## Findings

### API Status: No Public API

**Result:** ❌ Rava does not expose a documented public API.

- All endpoint patterns (`/api/v1/`, `/api/v2/`, `/api/instruments/`, etc.) return 404
- Data loading is entirely client-side JavaScript (Alpine.js + modern SPA)
- No authentication/API key documentation exists
- The platform is browser-first, not API-first

### Architecture: Consumer Aggregator

Rava is a consumer-facing financial data aggregator, **not a primary data source**. 

Evidence:
1. Site architecture is purely web (no API documentation, no CLI, no data export)
2. All data rendering happens in the browser via JavaScript
3. Real-time updates suggest WebSocket subscription to upstream providers
4. No indication of proprietary data collection or venue relationship

### Implications

**For HistFinTS V0:** Rava cannot be integrated directly. The project's scope explicitly excludes Argentine domestic equities (BYMA-listed stocks and CEDEARs) from V0.

**For Future Argentine Support:** If Argentine market data becomes a requirement:
1. **BYMA** (Buenos Aires Stock Exchange) is the authoritative source for Argentine instruments
2. **BYMA provides:** real-time and historical prices for domestic stocks, CEDEARs, bonds, and indices
3. **Rava's role:** consumer interface to BYMA + news + tools, not a data provider itself
4. **Recommended approach:** Implement a BYMA adapter directly, using official documentation and API

### Questions Answered (10-point Checklist)

The empirical test could not answer these questions because no API access exists:

| Question | Status | Finding |
|---|---|---|
| 1. Earliest observation available | ❌ Untested | Rava doesn't expose data programmatically |
| 2. OHLC availability across history | ❌ Untested | Browser-only; no API access |
| 3. Volume availability across history | ❌ Untested | Browser-only; no API access |
| 4. Behavior around CEDEAR ratio changes | ❌ Untested | Would require historical pricing + metadata |
| 5. Historical price basis (as-traded vs adjusted) | ❌ Untested | Unknown; CEDEAR ratio application unclear |
| 6. Queryability of inactive/delisted CEDEARs | ❌ Untested | Browser-only; no filtering/search API |
| 7. Ticker identity changes | ❌ Untested | Bitemporal/historical symbol tracking not exposed |
| 8. Date correspondence to Argentine trading sessions | ❌ Untested | Calendar alignment would require provider metadata |
| 9. Volume units (shares/CEDEARs vs monetary) | ❌ Untested | Not documented; inferred from context only |
| 10. Maximum date-range/window limits | ❌ Untested | No pagination/range parameters exposed |

---

## Recommendation

**Do not pursue Rava for HistFinTS integration.** 

If Argentine financial data becomes in-scope for HistFinTS:

1. **Evaluate BYMA direct access** — the authoritative source for:
   - Argentine domestic equities
   - CEDEARs (with CNV regulation compliance)
   - Ratio/adjustment metadata for derivatives
   - Official trading calendar and holidays

2. **Contact BYMA for:**
   - Historical data availability (backfill depth)
   - CEDEAR ratio tables (dated, per CNV reporting schedule)
   - Data access terms and API documentation
   - Whether real-time vs. end-of-day data is available

3. **Document findings** in [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) if Argentine support is deferred.

---

## Method

**Empirical test script:** `F:\claude\...\scratchpad\rava_empirical_test.py`

Probed endpoints:
- `https://www.rava.com/api/{instruments,quotes}/{ticker}/history`
- `https://www.rava.com/api/v{1,2}/*`
- `https://api.rava.com/*`

All returned HTTP 404. Browser inspection confirmed JavaScript-driven data loading with no exposed REST API.

