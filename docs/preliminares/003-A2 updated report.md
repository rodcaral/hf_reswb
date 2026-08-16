Below is the **revised specification**, incorporating the feedback and the refinements we discussed. I have also rechecked the current Yahoo Finance `B` page and Yahoo's own documentation so that the functional description reflects the current product rather than an older mental model. The current page exposes, among other things, the quote header, regular/overnight pricing, chart ranges, news, performance versus a benchmark, earnings trends, analyst insights, statistics, and peer comparison; Yahoo's documentation confirms the broader quote-page areas such as Chart, Statistics, Historical Data, Profile, Financials, Analysis, Options, Holders and Sustainability. ([Yahoo Finanzas][1])

# HistFinTS Research Workbench

## Yahoo-Finance-Inspired Multi-Asset Financial Research Application

### Product and Functional Specification — Draft

---

# 1. Product Definition

HistFinTS Research Workbench is a **multi-asset financial research application** for identifying, monitoring and analyzing financial instruments and their historical and current market information.

Its user experience is inspired by the functionality and information architecture of Yahoo Finance, but it is **not intended to be a Yahoo Finance clone**.

Yahoo Finance is a **UX and functional reference**. It is not the HistFinTS domain model, identity system, or necessarily the data provider.

HistFinTS remains authoritative for:

* Series identity;
* Provider identity;
* ProviderSymbol identity;
* relationships between Series;
* locally stored historical observations;
* data provenance;
* catalog resolution and instrument classification.

External providers supply data to HistFinTS. **They do not define HistFinTS identity.**

---

# 2. Core Design Principles

The following principles are architectural requirements, not optional design preferences.

### P1 — Series is the primary financial-data identity

A ticker is a provider-specific symbol.

The application MUST NOT use a ticker as the fundamental identity of an instrument.

The conceptual relationship remains:

```text
Provider
   │
   └── ProviderSymbol
           │
           └── Series
```

A single real-world instrument may have multiple ProviderSymbols.

Conversely, similar or identical ticker strings may refer to different Series.

This is particularly important for:

* CEDEARs;
* cross-listed securities;
* securities traded on multiple venues;
* provider-specific symbols;
* ticker reuse.

---

### P2 — The application MUST be instrument-aware

The UI MUST adapt its available information and operations according to the instrument/security type.

An equity, ETF, CEDEAR, index, commodity and bond MUST NOT be presented through an identical set of financial metrics.

The application MUST suppress, replace or disable metrics that are not meaningful for the selected instrument.

For example:

| Instrument | Relevant information                                                   |
| ---------- | ---------------------------------------------------------------------- |
| Equity     | EPS, P/E, revenue, ROE, dividends                                      |
| ETF        | NAV, expense ratio, AUM, holdings, tracking difference                 |
| CEDEAR     | local price, underlying, conversion ratio, currencies, FX relationship |
| Index      | index level, return, constituents, methodology                         |
| Commodity  | spot/futures price, contract, expiration, roll                         |
| Bond       | coupon, maturity, yield, duration, credit information                  |

This requirement is a central design principle of the application.

---

### P3 — Every value MUST be traceable

Every externally sourced or calculated value displayed to the user MUST have machine-accessible provenance.

The minimum conceptual lineage is:

```text
Displayed Value
      ↓
Metric
      ↓
Source Provider
      ↓
Provider Symbol / Identifier
      ↓
Raw Observation / Source Record
      ↓
Transformation / Calculation
      ↓
Displayed Value
```

The UI does **not** need to display all this information next to every number.

Instead, the user MUST have an obvious way to inspect the provenance.

For example:

```text
P/E       10.08   ⓘ
```

could reveal:

```text
Source: Provider X
Provider symbol: B
As of: 2026-07-29
Price: 37.70
TTM EPS: 3.74
Calculation: Price / TTM EPS
```

---

### P4 — Distinguish data classes

The application MUST distinguish at least three categories:

**Observed**

Data directly supplied by a provider.

```text
Close = 37.70
Volume = 7,163,437
```

**Calculated**

Values calculated by HistFinTS.

```text
CAGR = 8.4%
Volatility = 24.1%
Maximum Drawdown = -31%
```

**Reported / Estimated**

Values supplied by another organization or provider as an estimate, opinion or forecast.

```text
Analyst target = 52.87
EPS estimate = 4.12
```

These categories MUST NOT be silently conflated.

---

### P5 — Yahoo Finance is a UX benchmark, not the domain model

Yahoo's navigation:

```text
Summary
Chart
Statistics
Historical Data
Profile
Financials
Analysis
Options
Holders
Sustainability
```

is useful as a reference for user workflows.

It MUST NOT determine HistFinTS's domain objects or persistence structure.

---

### P6 — Incremental development

The application MUST be developed in clearly bounded stages.

A fully featured Yahoo-like system is not a suitable single implementation task.

Each phase MUST provide a usable product.

---

# 3. Primary User Workflow

The fundamental workflow is:

```text
Search
   ↓
Identify Series
   ↓
Open Research View
   ↓
Inspect current state
   ↓
Analyze historical behavior
   ↓
Compare
   ↓
Investigate fundamentals / events / other information
```

The user should be able to remain focused on the same Series while moving between research sections.

---

# 4. Global Application Structure

The principal navigation should eventually resemble:

```text
Search

Markets

Research
    Summary
    Chart
    Performance
    Historical
    Statistics
    Financials
    Profile
    Analysis
    Corporate Actions
    Dividends
    News
    Peers
    Holders
    Options
    Sustainability

Watchlists

Portfolios

Screeners

Calendar
```

However, these areas do **not** all belong to V1.

---

# 5. Search

## 5.1 Search input

The user MUST be able to search by:

* provider ticker;
* company/security name;
* ISIN;
* CUSIP where available;
* FIGI;
* CIK where applicable;
* HistFinTS Series ID;
* other supported identifiers.

Example:

```text
Search
[ Barrick Mining________________ ]
```

Results:

```text
B       Barrick Mining Corporation       NYSE   USD
ABX.TO  Barrick Mining Corporation       TSX    CAD
```

Yahoo's finance-specific search is explicitly designed to locate companies, funds, indexes and quotes. ([Yahoo Ayuda][2])

---

# 6. Series Selection

Selecting a search result MUST identify a HistFinTS Series.

The application SHOULD show enough information to distinguish potentially confusing instruments.

Example:

```text
Barrick Mining Corporation

Series ID: 1234
Provider: NYSE Provider
Provider Symbol: B
Currency: USD
Venue: NYSE
Security Type: Equity
```

For a CEDEAR:

```text
GLD CEDEAR

Series ID: 5678
Provider: BYMA
Provider Symbol: GLD
Currency: ARS
Security Type: CEDEAR

Underlying:
SPDR Gold Shares
```

The user should never be left to infer identity from the ticker alone.

---

# 7. Research Header

Every Research page MUST begin with a compact identity/quote header.

Example:

```text
Barrick Mining Corporation
B

NYSE · USD · Equity

37.70
+1.34 (+3.69%)

At close: 2026-07-30 16:01 EDT
```

The current Yahoo page distinguishes regular-session and overnight pricing. For example, its current B page shows the regular close separately from overnight activity and explicitly describes the overnight session. ([Yahoo Finanzas][1])

HistFinTS MUST preserve this distinction.

---

## 7.1 Market status

Possible states include:

```text
Open
Closed
Pre-market
After-hours
Overnight
Suspended
Unknown
```

The displayed price MUST identify which session it represents.

The application MUST NOT silently mix:

```text
regular-session price
```

with:

```text
extended-hours price
```

---

## 7.2 Timestamp

A quote MUST have an explicit timestamp.

Where possible, display:

* observation timestamp;
* timezone;
* session;
* source;
* data freshness.

---

# 8. Summary

The Summary page is the principal research dashboard.

Yahoo currently combines the quote header, chart preview, news, key statistics, performance, earnings information, analyst information, statistics and peer comparison on its current B page. ([Yahoo Finanzas][1])

HistFinTS SHOULD use a similar information hierarchy while adapting the content to the instrument.

---

## 8.1 Summary contents

For an equity, the summary SHOULD contain:

1. identity;
2. current quote;
3. market status;
4. chart preview;
5. key statistics;
6. performance;
7. news;
8. earnings;
9. analyst information;
10. peer comparison.

Not every section is applicable to every instrument.

---

# 9. Interactive Chart

The chart is a core V1 capability.

Yahoo's chart functionality allows changing time ranges, viewing historical points and expanding into an interactive chart; Yahoo also documents comparison, indicators, time periods and scale controls. ([Yahoo Ayuda][3])

## 9.1 Time ranges

At minimum:

```text
1D
5D
1M
6M
YTD
1Y
5Y
All
```

The current B page exposes these kinds of ranges, including 1D, 5D, 1M, 6M, YTD, 1Y, 5Y and All. ([Yahoo Finanzas][1])

---

## 9.2 Frequency

Frequency MUST be constrained by:

* requested period;
* provider availability;
* instrument type;
* stored observations.

For example:

```text
1D → intraday
5D → intraday
1M → daily
6M → daily
1Y → daily
5Y → daily/weekly
All → weekly/monthly
```

These are defaults, not promises.

The application MUST NOT fabricate an interval unavailable from the underlying data.

---

## 9.3 Chart types

Initial:

* line;
* OHLC;
* candlestick.

Later:

* area;
* additional specialized chart types.

---

## 9.4 Scale

Support:

```text
Linear
Logarithmic
Percentage
```

---

## 9.5 Indicators

Initial:

* SMA;
* EMA;
* Bollinger Bands;
* RSI;
* MACD;
* volume.

Later:

* ATR;
* ADX;
* stochastic;
* OBV.

Indicators SHOULD normally be calculated from HistFinTS observations rather than stored as independent Series.

---

## 9.6 Corporate actions

The chart SHOULD eventually support markers for:

* dividends;
* splits;
* other material corporate actions.

---

# 10. Comparison

The user MUST be able to compare multiple Series.

Example:

```text
B
NEM
AEM
GLD
S&P 500
```

The comparison chart MUST support normalization.

Recommended default:

```text
Initial value = 100
```

This answers:

> What would $100 invested in each instrument have become?

The comparison MUST clearly identify:

* starting date;
* ending date;
* price vs total-return basis;
* currency;
* corporate-action treatment.

Yahoo explicitly supports comparing multiple symbols in interactive charts. ([Yahoo Ayuda][2])

---

# 11. Performance Analysis

Performance should be more than a chart.

Yahoo currently shows benchmark-relative YTD, 1-year, 3-year and 5-year performance on the B page. ([Yahoo Finanzas][1])

HistFinTS SHOULD extend this substantially.

## Standard outputs

```text
1D
1W
1M
3M
6M
YTD
1Y
3Y
5Y
All
```

For appropriate periods:

* absolute return;
* annualized return;
* CAGR;
* volatility;
* maximum drawdown;
* Sharpe ratio;
* Sortino ratio;
* beta;
* correlation.

---

## 11.1 Benchmark

The benchmark SHOULD be:

1. instrument-specific default where appropriate;
2. user-selectable;
3. explicitly identified.

Example:

```text
B
vs
S&P/TSX Composite
```

The current Yahoo B page uses the S&P/TSX Composite as its performance benchmark. ([Yahoo Finanzas][1])

---

# 12. Historical Data

Historical Data is a core HistFinTS capability.

Yahoo provides customizable historical tables containing prices, splits and dividends and allows historical data to be downloaded. ([Ayuda Yahoo][4])

HistFinTS SHOULD provide:

```text
From: [2020-01-01]
To:   [2026-08-15]

Frequency:
[Daily ▼]
```

and:

```text
Date
Open
High
Low
Close
Adjusted Close
Volume
```

where applicable.

Additional datasets:

```text
Dividends
Splits
Corporate Actions
```

---

## 12.1 Historical-data provenance

The user MUST be able to inspect:

```text
Series
Provider
Provider Symbol
Observation timestamp
Source timestamp
Import run
Adjustment status
```

This is a key HistFinTS differentiator.

---

# 13. Statistics

Yahoo's current B page provides valuation measures, profitability/income statistics, balance-sheet/cash-flow statistics and peer comparison; Yahoo's documentation describes Statistics as including key financial highlights, valuation measures and trading information. ([Yahoo Finanzas][1])

HistFinTS SHOULD organize statistics into logical groups.

## Valuation

```text
Market Capitalization
Enterprise Value
P/E
Forward P/E
PEG
Price/Sales
Price/Book
EV/Revenue
EV/EBITDA
```

## Profitability

```text
Profit Margin
Operating Margin
ROA
ROE
```

## Income

```text
Revenue
Revenue Growth
Gross Profit
Operating Income
Net Income
EPS
```

## Balance Sheet

```text
Cash
Debt
Debt/Equity
Current Ratio
Book Value
```

## Cash Flow

```text
Operating Cash Flow
Free Cash Flow
Levered Free Cash Flow
```

## Trading

```text
Beta
52-week High
52-week Low
50-day MA
200-day MA
Volume
Average Volume
```

## Shares

```text
Shares Outstanding
Float
Institutional Ownership
Insider Ownership
Short Interest
```

## Dividends

```text
Trailing Dividend
Forward Dividend
Yield
Payout Ratio
Ex-Dividend Date
Payment Date
```

Yahoo explicitly distinguishes trailing and forward dividend information and identifies forward values as estimates for the next year. ([Yahoo Ayuda][5])

---

# 14. Financial Statements

For applicable instruments, provide:

```text
Income Statement
Balance Sheet
Cash Flow
```

with:

```text
Annual
Quarterly
TTM
```

Yahoo's quote-page documentation confirms annual and quarterly income statements, balance sheets and cash-flow data. ([Ayuda Yahoo][4])

The UI SHOULD allow:

* absolute values;
* percentage margins;
* YoY change;
* period comparison.

---

# 15. Profile

For corporate securities:

```text
Company
Description
Country
Headquarters
Sector
Industry
Employees
Executives
Website
```

For funds:

```text
Fund category
Issuer
Expense ratio
Assets
Objective
Holdings
```

Yahoo describes Profile as providing basic company information, management information and, depending on the instrument, fund information. ([Ayuda Yahoo][4])

---

# 16. Analyst Analysis

For applicable equities:

```text
EPS estimates
Revenue estimates
Growth estimates
Earnings history
EPS revisions
Revenue revisions
Price targets
Recommendations
```

The current B page includes analyst price targets, latest rating information and analyst recommendations. ([Yahoo Finanzas][1])

Example:

```text
Price Target

Low       29.00
Average   52.87
Current   37.70
High      64.00
```

These values are an example of current Yahoo presentation only; they MUST NOT be hard-coded into the HistFinTS specification.

---

# 17. Earnings

Applicable securities SHOULD expose:

```text
Historical earnings
Expected EPS
Actual EPS
Surprise
Revenue
Revenue growth
```

The current B page includes earnings trends and revenue-versus-earnings views. ([Yahoo Finanzas][1])

---

# 18. News

The application SHOULD eventually provide security-specific news.

Categories may include:

```text
All
News
Earnings Calls
Press Releases
Regulatory Filings
```

The current B page uses these categories. ([Yahoo Finanzas][1])

Each item SHOULD retain:

```text
Headline
Source
Publication time
URL
Related Series
Category
```

HistFinTS should store article metadata rather than reproducing third-party article content.

---

# 19. Peer Comparison

The application SHOULD allow both:

* automatically suggested peers;
* manually selected peers.

Yahoo currently displays a peer set for B including other gold-mining companies and permits comparison using key performance information. ([Yahoo Finanzas][1])

HistFinTS should support a comparison table such as:

| Security | Price | Market Cap | P/E | ROE | Growth | Yield |
| -------- | ----: | ---------: | --: | --: | -----: | ----: |
| B        |       |            |     |     |        |       |
| NEM      |       |            |     |     |        |       |
| AEM      |       |            |     |     |        |       |

The peer-selection mechanism itself should remain independent of the Series identity model.

---

# 20. Corporate Actions

Corporate actions should be a first-class data domain.

At minimum:

```text
Dividends
Splits
Ticker Changes
Name Changes
Mergers
Spin-offs
Rights
```

Each event SHOULD retain:

* event type;
* effective date;
* announcement date where available;
* provider;
* source;
* affected Series;
* transformation information.

This is especially important because historical-price interpretation may depend on corporate actions.

---

# 21. Options

For optionable securities:

```text
Expiration
Calls
Puts
```

with:

```text
Strike
Last
Bid
Ask
Volume
Open Interest
Implied Volatility
```

Later:

* Greeks;
* IV analysis;
* OI/volume analysis.

Yahoo's quote-page functionality includes options and call/put statistics. ([Ayuda Yahoo][4])

Options are **not V1**.

---

# 22. Holders

For applicable equities:

```text
Institutional Holders
Major Holders
Insiders
Insider Transactions
```

Yahoo documents major holders, insider rosters and insider transactions as part of its quote research functionality. ([Ayuda Yahoo][4])

---

# 23. Sustainability

For applicable securities:

```text
Environmental
Social
Governance
Controversies
ESG Risk
```

Yahoo currently provides Sustainability information for applicable investments. ([Ayuda Yahoo][4])

This is a later-stage feature.

---

# 24. Watchlists

The application SHOULD eventually allow:

```text
My Watchlist
```

with:

```text
Series
Price
Change
Change %
```

Additional columns should be user-selectable.

Multiple watchlists SHOULD eventually be supported.

Yahoo supports custom portfolios/watchlists as part of its broader product. ([Yahoo Ayuda][2])

---

# 25. Portfolio

A later version MAY support:

```text
Portfolio
    Holdings
    Transactions
    Cash
    Dividends
    Performance
    Allocation
    P/L
```

Transactions:

```text
BUY
SELL
DIVIDEND
DEPOSIT
WITHDRAWAL
FEE
```

Portfolio accounting MUST be explicitly specified rather than implicitly copied from Yahoo.

---

# 26. Alerts

Later versions SHOULD support:

```text
Price > X
Price < X
Change > X%
Change < X%
Volume > X
52-week high
52-week low
Dividend event
Earnings event
```

Yahoo itself provides custom price alerts. ([Yahoo Ayuda][2])

---

# 27. Market Overview

A future Markets area should include:

```text
World Indices
Commodities
Currencies
Bonds
Most Active
Gainers
Losers
```

Yahoo documents these as part of its broader market functionality. ([Yahoo Ayuda][2])

---

# 28. Screener

A future screener should allow conditions such as:

```text
Market: US
Sector: Materials
Market Cap > $10B
P/E < 15
ROE > 15%
Revenue Growth > 5%
Dividend Yield > 2%
```

The user should be able to:

* save screens;
* reload screens;
* modify conditions;
* export results.

Yahoo provides both predefined and custom screeners. ([Yahoo Ayuda][2])

---

# 29. Calendar

A future financial calendar should include:

```text
Earnings
Dividends
Splits
IPOs
Other corporate events
```

Yahoo's broader market-event functionality includes earnings announcements, IPOs and stock splits. ([Yahoo Ayuda][6])

---

# 30. HistFinTS Data Architecture

The Yahoo-like UI MUST NOT dictate the internal architecture.

The conceptual architecture remains:

```text
                    ┌──────────────────┐
                    │     Web UI       │
                    └────────┬─────────┘
                             │
                   Application Services
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
 Series Catalog         Market Data         Fundamental Data
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                        Persistence
                             │
                           SQLite
```

External providers remain behind the provider layer.

```text
                   Provider Layer
                         │
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
       BYMA          US providers       Other APIs
```

---

# 31. Domain Separation

The application SHOULD conceptually separate:

### Security identity

```text
Series
Provider
ProviderSymbol
SeriesGroup
```

### Market observations

```text
PriceObservation
VolumeObservation
QuoteSnapshot
```

### Corporate actions

```text
Dividend
Split
CorporateAction
```

### Fundamentals

```text
IncomeStatement
BalanceSheet
CashFlowStatement
```

### Estimates

```text
AnalystEstimate
PriceTarget
Recommendation
EarningsEstimate
```

### Ownership

```text
InstitutionalHolding
InsiderHolding
InsiderTransaction
```

### Derivatives

```text
OptionContract
OptionQuote
```

### Research/news

```text
NewsArticle
ResearchReport
```

The UI may combine these into one Research page, but the domain MUST NOT.

---

# 32. Provenance Model

The provenance requirement deserves explicit treatment.

A value such as:

```text
P/E = 10.08
```

could conceptually have:

```text
Metric
    P/E

Classification
    Calculated

Inputs
    Price = 37.70
    TTM EPS = 3.74

Source of Price
    Provider A
    ProviderSymbol B

Source of EPS
    Provider B
    Financial Statement X

Calculation
    Price / TTM EPS

As-of
    2026-07-29
```

The system should therefore be able to answer:

> **Where did this number come from?**

and, for calculated metrics:

> **How did HistFinTS derive it?**

---

# 33. UI Help and Provenance

The contextual-help mechanism discussed previously fits naturally into this architecture.

For example:

```text
P/E     10.08   ⓘ
```

The icon can expose provenance without changing the layout of the research table.

For ordinary forms/pages:

```text
Field name ⓘ
```

can use native HTML disclosure.

For dense tables:

```text
CSS-positioned floating help
```

is preferable because it does not increase row height.

No JavaScript is required for either approach.

---

# 34. V1 — Core Research Workbench

V1 should be deliberately narrow.

## V1 MUST provide

### Search

* search by ticker/name/identifier;
* Series selection;
* clear instrument identity.

### Quote

* current price where available;
* change;
* percentage change;
* market status;
* timestamp;
* session distinction.

### Chart

* 1D;
* 5D;
* 1M;
* 6M;
* YTD;
* 1Y;
* 5Y;
* All;
* supported frequencies;
* line;
* OHLC/candlestick where appropriate;
* volume;
* comparison;
* linear/log scale.

### Performance

* period returns;
* benchmark;
* CAGR;
* volatility;
* maximum drawdown;
* beta;
* correlation;
* Sharpe/Sortino where statistically appropriate.

### Historical

* historical table;
* date range;
* frequency;
* CSV export;
* provenance.

### Statistics

Only **instrument-appropriate** key statistics.

### Provenance

Every displayed value MUST be traceable.

---

# 35. V1 Explicitly Excludes

To protect the development scope, V1 SHOULD NOT implement:

* portfolio accounting;
* options;
* screeners;
* news aggregation;
* analyst estimates;
* ESG;
* insider holdings;
* advanced financial statements;
* alerts;
* economic calendar.

Those belong to subsequent phases.

---

# 36. V2 — Fundamental Research

Add:

1. Statistics expansion;
2. Financial statements;
3. Profile;
4. Dividends;
5. Corporate actions;
6. ETF-specific data;
7. instrument-specific metrics.

This is where instrument-awareness becomes particularly important.

---

# 37. V3 — Investment Research

Add:

1. Analyst estimates;
2. Price targets;
3. Recommendations;
4. Earnings history;
5. News;
6. Peer comparison;
7. Holders.

---

# 38. V4 — Investment Management

Add:

1. Watchlists;
2. Portfolios;
3. Transactions;
4. P/L;
5. dividends;
6. allocations;
7. alerts.

---

# 39. V5 — Discovery and Market Intelligence

Add:

1. Screeners;
2. market overview;
3. earnings calendar;
4. corporate-event calendar;
5. advanced comparison;
6. advanced portfolio analytics.

Yahoo's broader product demonstrates that these functions form a coherent ecosystem around the quote/research workflow. ([Yahoo Ayuda][2])

---

# 40. Highest-Value V1 Screen

The first screen should look conceptually like this:

```text
┌──────────────────────────────────────────────────────────────────┐
│ Search: [ Barrick Mining_______________________________ ]        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Barrick Mining Corporation                                      │
│ B · NYSE · USD · Equity                                         │
│                                                                  │
│ 37.70       +1.34 (+3.69%)       Market Closed                 │
│ At close · timestamp · source                                   │
│                                                                  │
│ [1D] [5D] [1M] [6M] [YTD] [1Y] [5Y] [ALL]                     │
│                                                                  │
│                         PRICE CHART                              │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Performance                                                      │
│                                                                  │
│ Return       CAGR       Volatility    Max DD     Sharpe          │
│ ...          ...        ...           ...        ...             │
│                                                                  │
│ Benchmark: S&P/TSX Composite                                    │
├──────────────────────────────────────────────────────────────────┤
│ Key Statistics                                                   │
│                                                                  │
│ Market Cap     ...       P/E       ...       Beta       ...      │
│ Revenue        ...       EPS       ...       Yield      ...      │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Historical Data                                                  │
│                                                                  │
│ Date          Open      High      Low       Close      Volume    │
│ ...                                                             │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Data Provenance                                                  │
│                                                                  │
│ [Inspect source / calculation / timestamp]                      │
└──────────────────────────────────────────────────────────────────┘
```

This is the **definition of V1 success**.

It gives an investor the most important capabilities of a Yahoo-style quote page without attempting to build Yahoo Finance.

---

# 41. Acceptance Criteria for V1

A developer should be able to demonstrate all of the following.

### AC-01 — Identity

Given a Series, the Research page identifies:

* Series;
* provider;
* ProviderSymbol;
* instrument type;
* currency;
* venue where applicable.

### AC-02 — Quote

A quote displays:

* value;
* change;
* percentage;
* timestamp;
* market/session status;
* source.

### AC-03 — Session integrity

Regular and extended-hours prices are never silently mixed.

### AC-04 — Instrument awareness

Selecting an ETF does not display meaningless equity-only metrics.

Selecting an index does not display P/E unless an explicit, meaningful index valuation concept exists.

### AC-05 — Historical data

The user can select a date range and view stored observations.

### AC-06 — Chart

The chart and historical table represent the same underlying observations and clearly state frequency and adjustment basis.

### AC-07 — Comparison

The user can compare at least two Series using normalized performance.

### AC-08 — Risk

The application calculates the specified performance/risk metrics from documented observations and parameters.

### AC-09 — Provenance

The user can determine the source and derivation of every displayed externally sourced/calculated value.

### AC-10 — No ticker identity leakage

The application does not treat the provider ticker as the Series identity.

---

# 42. Architectural Boundary

This statement should appear prominently in the developer specification:

> **HistFinTS is inspired by Yahoo Finance's user experience but is not a Yahoo Finance clone.**
>
> Yahoo Finance provides a reference for user workflows, information categories and interaction patterns. HistFinTS MUST retain its own domain model and identity architecture.
>
> **Series, Provider and ProviderSymbol remain authoritative HistFinTS concepts.**
>
> External providers supply observations and reference information. They do not define the identity of HistFinTS Series.
>
> The Research Workbench is a presentation and analytical layer over the HistFinTS domain and data architecture, not a replacement for it.

---

# 43. One additional architectural principle: the UI is a projection

I would explicitly add this because it protects the project from future scope problems.

> **The Research Workbench UI is a projection of the underlying HistFinTS data model. It must not require the domain model to mirror the visual organization of the UI.**

Thus:

```text
Domain
  Series
  ProviderSymbol
  Observation
  CorporateAction
  FinancialStatement
  ...

             ↓

Application Services

             ↓

Research UI
  Summary
  Chart
  Statistics
  Financials
  ...
```

This means that if the UI later changes from:

```text
Summary | Chart | Statistics
```

to:

```text
Overview | Market | Fundamentals
```

the domain model does not need to change.

---

# 44. Final Product Vision

The long-term goal is therefore **not**:

> "Build our own Yahoo Finance."

It is:

> **Build a personal, provenance-aware, multi-asset financial research workstation on top of the HistFinTS Series Catalog and historical-data infrastructure, using mature financial research products such as Yahoo Finance as UX references while retaining HistFinTS's own identity, data, calculation and provenance architecture.**

That distinction is important.

Yahoo Finance's great strength is the **breadth and convenience of its research interface**. HistFinTS can potentially have a different strength:

**the ability to know exactly what financial instrument a value belongs to, where the value came from, what source symbol produced it, when it was observed, and how any derived value was calculated.**

That is a much more defensible foundation for the application you are building. ([Yahoo Finanzas][1])

[1]: https://finance.yahoo.com/quote/B/?utm_source=chatgpt.com "Barrick Mining Corporation (B) Stock Price, News, Quote & History - Yahoo Finance"
[2]: https://help.yahoo.com/kb/market-data-research-tools-yahoo-finance-sln24381.html?utm_source=chatgpt.com "Market data and research tools available in Yahoo Finance | Yahoo Help"
[3]: https://help.yahoo.com/kb/finance/quote-summary-chart-preview-sln26346.html?utm_source=chatgpt.com "Use the quote summary chart preview | Finance Help | Yahoo Help"
[4]: https://uk.help.yahoo.com/kb/SLN28277.html?utm_source=chatgpt.com "Research stocks, mutual funds and ETFs with Yahoo Finance quote pages | Yahoo Help"
[5]: https://help.yahoo.com/kb/SLN4628.html?utm_source=chatgpt.com "Find forward and trailing dividend information in Yahoo Finance for Web | Yahoo Help"
[6]: https://help.yahoo.com/kb/SLN3642.html?utm_source=chatgpt.com "Getting started with Yahoo Finance | Yahoo Help"
