You are a finnancial analyst and investor. You wank to specify your software developper a program sharing many functionalities of the Yahoo Finnance (like https://finance.yahoo.com/quote/B/). Not a copy, but a source of inspiration. Analyze that page and it's functionality and improve the report here below.

---

I would approach this as a **product specification for an investment-research application**, not as a request to clone Yahoo Finance literally.

I examined the current Yahoo Finance quote page for `B` (Barrick Mining Corporation) and the associated Yahoo documentation. The current page is considerably richer than a simple quote screen: it combines market data, charting, company fundamentals, analyst information, news, peer comparison, historical data, options, holders, sustainability, and portfolio/watchlist functions. Yahoo itself describes the quote-page family as covering Summary, Chart, Statistics, Historical Data, Profile, Financials, Analysis, Options, Holders, Sustainability and, depending on the instrument, Conversations. ([Yahoo Finanzas][1])

For HistFinTS, I would **not attempt to reproduce all of Yahoo Finance in the first version**. I would build a strong **Quote/Research Workbench** around your existing Series Catalog and historical price infrastructure, and add the other analytical domains incrementally.

---

# 1. Product concept

I would specify the application as:

> **A multi-asset financial research workstation that allows an investor to identify a security, inspect its current market state, analyze its historical price behavior, examine fundamental and corporate information, compare it with peers and benchmarks, and maintain watchlists/portfolios.**

The primary object is **not a ticker**.

This is particularly important for HistFinTS.

The primary object should be:

> **Series**

with provider-specific symbols/tickers used to retrieve data.

Thus:

```text
User enters: B
        ↓
Instrument/Security search
        ↓
Series
        ↓
ProviderSymbol
        ↓
Market data
```

This is much better than making `"B"` itself the identity.

---

# 2. Main application structure

I would organize the application around a selected Series:

```text
┌───────────────────────────────────────────────────────────────┐
│ Search                                                         │
│ [ Barrick / B / ISIN / ... ]                                  │
├───────────────────────────────────────────────────────────────┤
│ B · Barrick Mining Corporation                                 │
│ NYSE · USD · Equity                                            │
│                                                               │
│ Summary | Chart | Statistics | Historical | Financials | ...  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│                  Selected research view                       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

The selected Series should persist while the user moves between tabs.

---

# 3. SEARCH

Search is foundational.

Yahoo's finance-specific search accepts company names, ticker symbols and other investment identifiers. ([Yahoo Ayuda][2])

### Input

```text
Search
[ Barrick Mining____________________________ ]
```

### Search results

```text
B       Barrick Mining Corporation       NYSE       USD
ABX.TO  Barrick Mining Corporation       TSX        CAD
```

Potential identifiers:

* provider ticker;
* company name;
* ISIN;
* CUSIP;
* FIGI;
* CIK;
* internal Series ID.

For HistFinTS, this should use your **Series Catalog**, not directly query an external provider.

### Result selection

Once selected:

```text
Series ID: 1234
Provider: BYMA
Provider Symbol: GLD
```

could be distinguished from:

```text
Series ID: 5678
Provider: Yahoo
Provider Symbol: GLD.BA
```

This is one of the places where your Series Catalog architecture gives you an advantage over a simplistic Yahoo-like implementation.

---

# 4. SUMMARY PAGE

This should be the equivalent of Yahoo's current Summary page.

For `B`, Yahoo currently presents the security name, current/previous/extended-hours price information, chart, key statistics, company overview, news, performance, analyst information, valuation, financial highlights and peer comparison. ([Yahoo Finanzas][1])

I would specify the Summary page as follows.

## 4.1 Security header

```text
Barrick Mining Corporation
B

NYSE · USD
Gold / Basic Materials

37.70
+1.34 (+3.69%)
```

Display:

* Series name
* ticker/provider symbol
* exchange/venue
* currency
* security type
* current price
* absolute change
* percentage change
* quote timestamp
* market status

If applicable:

```text
Market Open
Pre-market
After-hours
Closed
```

Do **not** silently mix regular-session and extended-hours prices.

Yahoo currently explicitly distinguishes regular close from overnight activity on the page. ([Yahoo Finanzas][1])

---

# 5. PRICE CHART

This is probably the single most important analytical component.

Yahoo's chart supports multiple periods, interactive historical inspection, comparison and technical indicators. Yahoo also provides linear, logarithmic and percentage scales and optional extended-hours display. ([Yahoo Ayuda][3])

## 5.1 Default chart

```text
Price

60 ┤
   │             ╭─────╮
50 ┤        ╭────╯     ╰──
   │   ╭────╯
40 ┤───╯
   └────────────────────────
     Jan       Apr       Aug
```

### Time buttons

```text
1D  5D  1M  6M  YTD  1Y  5Y  Max
```

These should be configurable by asset class.

---

## 5.2 Frequency

Depending on requested period:

```text
1D     1m / 5m / 15m / 1h
5D     15m / 1h
1M     1D
6M     1D
1Y     1D
5Y     1D / 1W
Max    1W / 1M
```

**Important:** the application should not promise an interval that the underlying Provider does not supply.

---

## 5.3 Chart type

Minimum:

* line;
* OHLC;
* candlestick.

Later:

* area;
* Heikin-Ashi;
* volume overlay/subpanel.

---

## 5.4 Scale

Provide:

```text
Linear
Logarithmic
Percentage
```

Yahoo currently supports these scale choices. ([Yahoo Ayuda][4])

---

## 5.5 Indicators

Initial set:

* SMA 20;
* SMA 50;
* SMA 100;
* SMA 200;
* EMA;
* Bollinger Bands;
* RSI;
* MACD;
* volume.

Later:

* ATR;
* stochastic;
* ADX;
* OBV.

Indicators should be **calculated from the stored price observations**, not downloaded as independent Series unless there is a specific reason.

---

# 6. COMPARISON

This is a major analytical function.

Example:

```text
B
NEM
AEM
GOLD ETF
S&P 500
```

Chart:

```text
                B
                NEM
                AEM
                Gold
                S&P 500
```

Allow normalization:

```text
Starting value = 100
```

so the investor sees:

> "What would have happened to $100 invested in each security?"

This is much more informative than comparing absolute prices.

Yahoo explicitly supports comparing multiple symbols on its interactive charts. ([Yahoo Ayuda][2])

---

# 7. PERFORMANCE

I would create a dedicated performance component rather than forcing the investor to infer everything from the chart.

Example:

| Period |       B | Benchmark |
| ------ | ------: | --------: |
| 1D     |  +3.69% |     +1.2% |
| 1W     |   +2.4% |     +0.8% |
| 1M     |   -5.1% |     +1.1% |
| YTD    |  +13.7% |    +11.4% |
| 1Y     |  +82.8% |    +29.7% |
| 3Y     | +137.8% |    +73.0% |
| 5Y     |  +99.4% |    +75.0% |

The current Yahoo page presents this type of benchmark-relative performance overview. ([Yahoo Finanzas][1])

For HistFinTS I'd go further and calculate:

* CAGR;
* volatility;
* maximum drawdown;
* Sharpe ratio;
* Sortino ratio;
* beta;
* correlation;
* best/worst period.

Those are extremely useful investor functions.

---

# 8. STATISTICS

This should be a dedicated tab.

Yahoo's Statistics page contains valuation measures, profitability, balance-sheet metrics, cash flow, trading statistics, share statistics and dividends/splits. It also exposes historical valuation snapshots. ([Yahoo Finanzas][5])

I would organize it into collapsible sections.

## Valuation

```text
Market Cap
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
EBITDA
Net Income
EPS
EPS Growth
```

## Balance Sheet

```text
Cash
Debt
Debt/Equity
Current Ratio
Book Value/Share
```

## Cash Flow

```text
Operating Cash Flow
Free Cash Flow
Levered FCF
```

## Trading

```text
Beta
52-week high
52-week low
50-day MA
200-day MA
```

## Shares

```text
Shares Outstanding
Float
Institutional %
Insider %
Short Interest
Short Ratio
Short %
```

## Dividends

```text
Forward Dividend
Yield
Trailing Dividend
5Y Average Yield
Payout Ratio
Ex-Dividend Date
Payment Date
```

The current Yahoo implementation exposes essentially this structure. ([Yahoo Finanzas][5])

---

# 9. HISTORICAL DATA

This should be one of the strongest parts of your application because it connects directly to HistFinTS.

Yahoo provides customizable historical price tables and, where licensing permits, downloadable CSV data. It allows selection of time period, data type and frequency. ([Yahoo Ayuda][6])

I would provide:

```text
From: [2020-01-01]
To:   [2026-08-15]

Frequency:
[Daily ▼]

Data:
[x] Prices
[x] Dividends
[x] Splits
```

Table:

| Date | Open | High | Low | Close | Adj Close | Volume |
| ---- | ---: | ---: | --: | ----: | --------: | -----: |

And:

```text
[Download CSV]
[Export Excel]
```

But I would add something Yahoo doesn't emphasize sufficiently:

### Data provenance

Every historical dataset should identify:

```text
Series
Provider
ProviderSymbol
Provider observation date
Imported at
Source
Adjustment status
```

For example:

```text
Source: BYMA
Provider Symbol: GLD
Currency: ARS
Frequency: Daily
Adjustment: Raw close
Imported: 2026-08-15 07:00
```

That is extremely valuable for your project.

---

# 10. FINANCIALS

Yahoo provides annual and quarterly income statements, balance sheets and cash-flow statements. ([Yahoo Ayuda][7])

I would have three sub-tabs:

```text
Income Statement | Balance Sheet | Cash Flow
```

and:

```text
Annual | Quarterly | TTM
```

Example income statement:

|                  | 2024 | 2025 | TTM |
| ---------------- | ---: | ---: | --: |
| Revenue          |      |      |     |
| Cost of Revenue  |      |      |     |
| Gross Profit     |      |      |     |
| Operating Income |      |      |     |
| Pretax Income    |      |      |     |
| Net Income       |      |      |     |
| EPS              |      |      |     |

Allow:

* absolute values;
* YoY growth;
* margins;
* currency;
* reporting period;
* source.

---

# 11. ANALYSIS

This deserves a separate page.

Yahoo's Analysis area covers current/future estimates, earnings/revenue/growth expectations, earnings history, EPS trends and revisions. ([Yahoo Ayuda][7])

I would implement:

### Analyst estimates

```text
Revenue
Current year
Next year
5-year growth

EPS
Current year
Next year
5-year growth
```

### Earnings history

| Quarter | Estimate | Actual | Surprise |
| ------- | -------: | -----: | -------: |

### EPS trend

```text
Current
7 days ago
30 days ago
60 days ago
90 days ago
```

### Revenue trend

Same structure.

### Analyst price targets

```text
Low
Average
Current
High
```

### Recommendations

```text
Strong Buy
Buy
Hold
Underperform
Sell
```

The current Yahoo page displays this type of analyst information. ([Yahoo Finanzas][1])

---

# 12. PROFILE

This should be a factual security/company information page.

For an equity:

```text
Company
Sector
Industry
Country
Website
Employees
Founded
Headquarters
CEO
Key executives
Description
```

Yahoo describes Profile as basic information, location, industry, employees and executives, with additional company/fund information depending on instrument type. ([Yahoo Ayuda][8])

---

# 13. NEWS

The Summary page currently includes recent news and categories such as:

* News
* Earnings Calls
* Press Releases
* SEC Filings

for B. ([Yahoo Finanzas][1])

I'd create:

```text
Latest News
────────────────────────────────
[time] Headline
       Source

[time] Headline
       Source

[time] Headline
       Source
```

Filters:

```text
All | News | Company | Earnings | Regulatory
```

Each article should retain:

* source;
* publication timestamp;
* title;
* URL;
* related Series;
* article category.

Don't attempt to reproduce the article itself.

---

# 14. PEER COMPARISON

Yahoo currently shows a peer set based on the company's industry. ([Yahoo Finanzas][1])

I would make this much more useful.

Example:

| Company | Price | Mkt Cap |  P/E | P/B | ROE | Revenue Growth |
| ------- | ----: | ------: | ---: | --: | --: | -------------: |
| B       | 37.70 |     63B | 10.1 | 2.2 | 25% |            ... |
| NEM     |   ... |     ... |  ... | ... | ... |            ... |
| AEM     |   ... |     ... |  ... | ... | ... |            ... |

Allow the user to add/remove peers manually.

---

# 15. OPTIONS

For optionable securities:

```text
Expiration:
[2026-09-18 ▼]

Calls | Puts
```

Columns:

```text
Strike
Last
Bid
Ask
Volume
Open Interest
Implied Volatility
```

And optionally:

* Greeks;
* IV chart;
* open-interest chart;
* volume/OI comparison.

Yahoo identifies Options as a quote-page research area for calls and puts. ([Yahoo Ayuda][7])

I would **not put this in V1** unless options are an explicit requirement.

---

# 16. HOLDERS

Yahoo exposes major holders, insider holdings and insider transactions. ([Yahoo Ayuda][7])

Structure:

```text
Major Holders

Institutions
Insiders
Mutual Funds
```

and:

```text
Insider Transactions

Date | Insider | Transaction | Shares | Price | Value
```

---

# 17. DIVIDENDS & CORPORATE ACTIONS

This deserves more prominence in an investment application.

Store/display:

```text
Declaration date
Ex-dividend date
Record date
Payment date
Amount
Currency
Frequency
```

And:

```text
Splits
Spin-offs
Rights
Mergers
Name changes
Ticker changes
```

This becomes especially important for HistFinTS because historical price interpretation depends on corporate actions.

---

# 18. SUSTAINABILITY / ESG

Yahoo has a Sustainability section for applicable instruments, including ESG ratings. ([Yahoo Ayuda][7])

I'd treat this as **optional data**, not part of the financial core.

Possible categories:

```text
Environmental
Social
Governance
Controversies
Risk scores
```

---

# 19. PORTFOLIO / WATCHLIST

This is where the application transitions from **research tool** into **investment workstation**.

Yahoo supports watchlists and multiple portfolios, with holdings, transactions, cash, lots and dividend management. ([Yahoo Ayuda][9])

I would specify:

### Watchlist

```text
My Watchlist

B       37.70   +3.69%
NEM     95.76   +4.84%
GLD    ...
```

### Portfolio

```text
Portfolio: Long-term

Security      Qty     Avg Cost     Value      P/L
B             100     31.20        3,770      +650
GLD           50      ...
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

Yahoo currently supports buy/sell transactions and lots, and uses FIFO for average-cost/share calculations in its portfolio implementation. ([Yahoo Ayuda][10])

For HistFinTS I would **not copy Yahoo's FIFO rule blindly**. Make the accounting method explicit and configurable.

---

# 20. ALERTS

Useful alerts:

```text
Price > X
Price < X
Daily change > X%
Daily change < X%
52-week high
52-week low
Volume > X
Dividend announced
Earnings announced
```

Yahoo supports custom price alerts. ([Yahoo Ayuda][11])

For a desktop/local HistFinTS implementation, alerts could initially be:

```text
Application notification
Email
```

rather than mobile push.

---

# 21. MARKET OVERVIEW

A Yahoo-like system shouldn't force the investor to start from an individual security.

Add:

```text
Markets
```

with:

```text
World Indices
US
Argentina
Europe
Asia

Currencies

Commodities

Bonds
```

Yahoo's broader market tools include market lists, Treasury rates, currency conversion, earnings calendars and screeners. ([Yahoo Ayuda][2])

---

# 22. SCREENER

This is potentially one of the most valuable functions for an investor.

Example:

```text
Market: US
Sector: Materials
Market Cap > $10B
P/E < 15
ROE > 15%
Revenue growth > 5%
Dividend yield > 2%
```

Results:

```text
Ticker | Company | Price | P/E | ROE | Yield
```

Allow:

```text
Save Screen
Load Screen
Export Results
```

Yahoo supports both predefined and custom screeners. ([Yahoo Ayuda][2])

But again: **not V1**.

---

# 23. FINANCIAL CALENDAR

A research application should eventually have:

```text
Earnings
Dividends
Splits
IPOs
Economic events
```

Yahoo has a Market Events Calendar covering earnings, IPOs, stock splits and other events. ([Yahoo Ayuda][12])

---

# 24. DATA ARCHITECTURE — particularly important for HistFinTS

I would **not design this as a Yahoo clone internally**.

Your existing architecture should remain:

```text
                    ┌─────────────────┐
                    │     Web UI      │
                    └────────┬────────┘
                             │
                    Application Services
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
         Series Catalog   Market Data    Fundamentals
              │              │              │
              └──────────────┼──────────────┘
                             ↓
                         Persistence
                             │
                         SQLite
```

And external providers:

```text
                 ┌───────────────┐
                 │ Provider layer│
                 └───────┬───────┘
                         │
        ┌────────────────┼─────────────────┐
        ↓                ↓                 ↓
       BYMA          NASDAQ/SEC        Other APIs
```

This is extremely important because **Yahoo Finance should be viewed as a UX benchmark, not necessarily your data provider**.

---

# 25. Separate the data domains

I would define at least these conceptual domains:

### Market data

```text
PriceObservation
VolumeObservation
QuoteSnapshot
```

### Security master

```text
Series
Provider
ProviderSymbol
SeriesGroup
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

### Market structure

```text
OptionContract
OptionQuote
```

### Research

```text
NewsArticle
ResearchReport
```

This avoids trying to cram Yahoo's heterogeneous information into your `Series` table.

---

# 26. A very important HistFinTS-specific principle

**Do not make the Yahoo page structure your domain model.**

Yahoo presents:

```text
Summary
Chart
Statistics
Financials
...
```

because that's convenient for a human.

Your domain should remain:

```text
Series
Provider
Observation
FundamentalReport
CorporateAction
AnalystEstimate
...
```

The UI is merely one **projection** of that data.

This distinction will save you a lot of architectural trouble later.

---

# 27. Data provenance should be much stronger than Yahoo's UI

One thing I would deliberately improve on Yahoo's model is provenance.

Yahoo itself identifies different data providers in its statistics footnotes—for example Refinitiv, EDGAR Online, Morningstar, S&P Global Market Intelligence and Yahoo-derived calculations. ([Yahoo Finanzas][5])

HistFinTS should make this explicit.

Every displayed metric should be traceable to:

```text
Metric
  ↓
Source Provider
  ↓
Provider Symbol / Identifier
  ↓
Raw observation/document
  ↓
Transformation
  ↓
Displayed value
```

For example:

```text
P/E = 10.08

Source: Provider X
As-of: 2026-07-29
Formula: Price / TTM EPS
Price: 37.70
EPS: 3.74
```

That is much more appropriate for a serious personal investment/research system.

---

# 28. Recommended implementation phases

I would **strongly resist specifying all of this as one development task**.

### V1 — Quote & historical research

Build:

1. Search
2. Series selection
3. Summary
4. Current quote
5. Historical chart
6. Historical table
7. CSV export
8. Performance
9. Benchmark comparison

This would already be a very useful application.

### V2 — Fundamental research

Add:

10. Statistics
11. Financials
12. Profile
13. Dividends
14. Corporate actions

### V3 — Investment research

Add:

15. Analyst estimates
16. Price targets
17. Recommendations
18. News
19. Peer comparison
20. Holders

### V4 — Trading/investment tools

Add:

21. Options
22. Watchlists
23. Portfolios
24. Transactions
25. Alerts

### V5 — Discovery

Add:

26. Screener
27. Market overview
28. Economic/earnings calendar
29. Advanced portfolio analytics

---

# 29. The most important V1 screen

If I were your investor/client, I would want this:

```text
┌─────────────────────────────────────────────────────────────────┐
│ 🔎 Search: Barrick Mining                                      │
├─────────────────────────────────────────────────────────────────┤
│ B · Barrick Mining Corporation                                 │
│ NYSE · USD · Equity                                            │
│                                                                 │
│ 37.70       +1.34 (+3.69%)                                    │
│                                                                 │
│ [1D][5D][1M][6M][YTD][1Y][5Y][MAX]                             │
│                                                                 │
│              PRICE CHART                                       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Performance                                                    │
│ 1D       1M       YTD       1Y       5Y                        │
│ +3.69%   -...     +13.7%    +82.8%   +99.4%                    │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Key Statistics                                                 │
│ Market Cap       $63.3B       P/E       10.1                  │
│ Revenue          $19.0B       EPS       $3.74                 │
│ Dividend         1.93%        Beta      1.10                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ B vs Benchmark                                                 │
│ [chart]                                                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Latest News                                                    │
│ ...                                                             │
└─────────────────────────────────────────────────────────────────┘
```

That gives an investor the **80/20 of Yahoo Finance** without reproducing the entire product.

---

# 30. One final recommendation for your developer specification

I would explicitly put this near the beginning of the specification:

> **The application is inspired by the information architecture and functionality of Yahoo Finance but is not intended to reproduce Yahoo Finance's implementation, branding, proprietary calculations, proprietary content, or data sources.**
>
> **HistFinTS remains the authoritative system for Series identity, provider identity, historical observations stored locally, provenance, and domain relationships. External providers supply data; they do not define HistFinTS identity.**

That is especially important for your project because you've already invested substantial effort in defining **Series vs ProviderSymbol vs Provider**, and a Yahoo-like UI could otherwise tempt the developer into making the ticker the central identity again.

---

## My recommended product boundary

If I were actually commissioning this software as the investor, my **initial requirement would be much narrower**:

> **Build a Yahoo-Finance-style Security Research page for any Series in the HistFinTS catalog, with current quote, interactive historical price chart, selectable periods/frequencies, benchmark comparison, performance statistics, key financial statistics, historical observations, corporate actions and source/provenance information.**
>
> **The page must work for equities, ETFs, CEDEARs, indices and commodities where the corresponding data exists. The UI must adapt to the asset class rather than displaying meaningless equity metrics for every Series.**

That last sentence is crucial for HistFinTS. A Yahoo-like page for **B**, **GLD**, a **CEDEAR**, an index, a commodity future and a bond cannot simply use the same set of fields.

Your existing **Series Catalog** gives you the right foundation to make the UI **instrument-aware** rather than merely **ticker-aware**.

[1]: https://finance.yahoo.com/quote/B/?utm_source=chatgpt.com "Barrick Mining Corporation (B) Stock Price, News, Quote & History - Yahoo Finance"
[2]: https://help.yahoo.com/kb/market-data-research-tools-yahoo-finance-sln24381.html?utm_source=chatgpt.com "Market data and research tools available in Yahoo Finance | Yahoo Help"
[3]: https://help.yahoo.com/kb/finance/quote-summary-chart-preview-sln26346.html?utm_source=chatgpt.com "Use the quote summary chart preview | Finance Help | Yahoo Help"
[4]: https://help.yahoo.com/kb/finance/customize-interactive-chart-settings-sln26786.html?utm_source=chatgpt.com "Customize chart settings in Yahoo Finance for Web | Finance Help | Yahoo Help"
[5]: https://uk.finance.yahoo.com/quote/B/key-statistics/?utm_source=chatgpt.com "Barrick Mining Corporation (B) valuation measures and financial statistics"
[6]: https://help.yahoo.com/kb/download-historical-data-yahoo-finance-sln2311.html?utm_source=chatgpt.com "Download historical data in Yahoo Finance | Yahoo Help"
[7]: https://help.yahoo.com/kb/finance-for-web/research-stocks-mutual-funds-etfs-yahoo-finance-quote-pages-sln28277.html?utm_source=chatgpt.com "Research stocks, mutual funds and ETFs with Yahoo Finance quote pages | Finance for Web Help | Yahoo Help"
[8]: https://help.yahoo.com/kb/SLN28276.html?utm_source=chatgpt.com "Research investments in Yahoo Finance search results | Yahoo Help"
[9]: https://help.yahoo.com/kb/finance/track-investments-watch-portfolio-toolkit-sln7034.html?utm_source=chatgpt.com "Track investments you own or watch using the My Portfolio toolkit | Finance Help | Yahoo Help"
[10]: https://help.yahoo.com/kb/yahoo-finance-plus/started-yahoo-finance-portfolio-sln36927.html?utm_source=chatgpt.com "Get Started with Yahoo Finance Portfolio | Yahoo Finance subscription plans Help | Yahoo Help"
[11]: https://help.yahoo.com/kb/SLN35070.html?utm_source=chatgpt.com "Set and receive custom price alerts for stocks in Yahoo Finance for Android | Yahoo Help"
[12]: https://help.yahoo.com/kb/SLN3642.html?utm_source=chatgpt.com "Getting started with Yahoo Finance | Yahoo Help"
