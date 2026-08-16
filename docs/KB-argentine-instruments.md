# Knowledge Base — CEDEARs and Argentine Instruments

**Audience:** anyone modelling, ingesting or analysing Argentine market data
**Status:** reference brief · **Compiled:** 2026-08-15
**Primary source:** CNV Normas, Título II, Capítulo VIII (as substituted by RG 1142/2026,
B.O. 01/06/2026, and RG 1095/2025), plus market data current to mid-August 2026

> **Why this exists.** Argentine instruments break assumptions that hold almost
> everywhere else: a single security may quote in three currencies at once, a
> depositary certificate's conversion ratio changes over time, and nominal returns in
> the local currency are close to meaningless. A pipeline designed for US equities will
> silently produce wrong numbers here rather than failing loudly.

---

## 1. Market map

| Term | What it is |
|---|---|
| **BYMA** | Bolsas y Mercados Argentinos — the principal exchange |
| **CNV** | Comisión Nacional de Valores — the securities regulator |
| **AIF** | Autopista de la Información Financiera — CNV's public disclosure system (prospectuses, supplements, material events) |
| **BCRA** | Banco Central — sets FX regime and capital controls |
| **ALyC** | Agente de Liquidación y Compensación — broker/clearing agent |
| **ADCVN** | Agente Depositario Central de Valores Negociables — central securities depository |
| **CEDEAR** | Certificado de Depósito Argentino — local certificate over a *foreign* security |
| **CEVA** | Certificado de Valores — local vehicle for passively-managed ETPs (new, 2026) |
| **ON** | Obligación Negociable — corporate bond |
| **CER / UVA** | Inflation-indexation coefficients |

---

## 2. The multiple-dollar structure

Argentina has historically had several simultaneous exchange rates. The gaps have
narrowed substantially but have **not** disappeared.

**As of mid-August 2026** — retail official quoted around <cite index="9-1">$1,470 buy / $1,520 sell, wholesale near $1,495.50, MEP around $1,526 and CCL around $1,585</cite>. <cite index="4-1">The official-to-MEP gap sits near 0.6%, largely eliminating arbitrage between the banking and exchange channels.</cite>

The rates that matter for security pricing:

| Rate | Derivation | Settles |
|---|---|---|
| **Oficial** | BCRA-regulated exchange market | ARS ↔ USD onshore, regulated |
| **MEP** (*dólar bolsa*) | Buy a security in ARS, sell the same security in USD **locally** | USD in a local account |
| **CCL** (*Contado con Liquidación*) | Buy a security in ARS, sell the same security in USD **abroad** | USD offshore |
| **Blue** | Informal parallel market | cash |

**The CCL–MEP spread is called the *canje*.** At current levels it runs near 3.9% —
small by Argentine standards, but far from negligible for return calculations.

**This distinction is not academic for instrument pricing.** <cite index="11-1">CEDEARs, foreign-law corporate bonds and other internationally-linked assets track the CCL more closely, while more locally-oriented instruments track the MEP.</cite> Choosing the wrong rate to
express a CEDEAR return in USD introduces a systematic several-percent error.

**Capital controls persist in modified form.** As of early 2026 a cross-restriction
applied: <cite index="12-1">buyers of official-market dollars were barred from operating in the financial markets for 90 days</cite>. Any historical analysis crossing a
regime change must account for the rules in force at the time, not today's.

> **Modelling conclusion.** An implied exchange rate is not a single number. It is
> (rate type × derivation instrument × date), and all three must be recorded alongside
> any USD-expressed figure.

---

## 3. CEDEARs — what they actually are

A CEDEAR is a **certificate evidencing the deposit of a foreign security held in
custody abroad**. It is not the foreign share. The regulation is explicit that the
structure separates ownership of the underlying — held offshore by a depositary bank —
from the CEDEAR holder.

**Key structural facts:**

- **The issuer is a local entity, not the foreign company.** Commercial banks
  authorised by the BCRA and registered with the CNV, certain financial trustees, fund
  managers, and the central depository may issue CEDEARs.
- **Management must be passive.** No discretionary strategy is permitted.
- **The underlying must be segregated**, held free of encumbrance, recorded in
  off-balance-sheet accounts, and not form part of the issuer's own assets.
- **The issuer exercises the underlying's rights** on holders' behalf — voting,
  dividends, corporate actions.
- **Exchangeability is optional** and set by the prospectus terms; where offered,
  holders may exchange CEDEARs for the underlying securities.
- **Sponsored or unsponsored.** Most CEDEARs are *no patrocinado* — created by the
  local issuer without the foreign company's involvement.

**Credit risk is real and disclosed.** The mandated prospectus warning states plainly
that in certain circumstances an Argentine bankruptcy court could recharacterise the
relationship, leaving the holder as an unsecured creditor of the local issuer, and that
insolvency of the international depositary is a further risk. **A CEDEAR is not a
perfect substitute for the underlying share.**

---

## 4. CEDEAR subtypes — a regulatory requirement

The prospectus must identify whether the CEDEAR represents:

- **acciones** (shares)
- **ADR**
- **ETF**
- **bono corporativo** (corporate bond)

CEDEARs over ETFs are separately provided for and may track equities, **virtual assets**
or **commodities**, with passive replication demonstrated via index composition.

> **Modelling conclusion — the most important one in this brief.**
> **"CEDEAR" is a wrapper, not an asset class.** The metrics that apply are determined
> by the *underlying*, not the wrapper. A CEDEAR over an ETF needs NAV, tracking error
> and expense ratio; over a corporate bond, coupon, maturity and yield; over shares,
> EPS and dividends. Any type system with a single `CEDEAR` value is already wrong.
>
> Minimum viable taxonomy needs three orthogonal axes:
> **wrapper** (direct / CEDEAR / CEVA / ADR) × **underlying asset class** (shares / ETF
> / bond / commodity / virtual asset / index) × **venue + currency + settlement**.
> Sponsored-vs-unsponsored is a fourth attribute.

---

## 5. The conversion ratio is variable

Each CEDEAR represents some quantity of the underlying — e.g. 20 CEDEARs to 1 share.
**This ratio is not fixed for the life of the instrument.**

- Issuers must report the quantity of underlying securities **and the conversion
  ratio** quarterly to the CNV and the market, along with certificates outstanding,
  quantities exchanged and withdrawn, new issuance against deposits, and custody
  location.
- A change in the exchange ratio requires a **Prospectus Supplement**, named in the
  regulation alongside a split or extraordinary dividend of the underlying as a
  triggering event.
- Prospectuses must set out the treatment of corporate events on the underlying —
  splits, mergers, liquidation — and the dividend collection and conversion procedure.

**How splits usually propagate.** A split of the underlying is typically absorbed by a
ratio change rather than a rescaling of the CEDEAR price — economically the two are
equivalent, but they leave different traces in a price series.

**Ratio changes have two distinct causes, and only one is visible internationally:**

1. **Underlying corporate actions** — split, extraordinary dividend, merger. These appear
   in any competent US corporate-actions feed.
2. **Local tradability adjustments** — when peso price levels rise (after a devaluation,
   say), issuers halve the unit price by doubling the ratio. There is **no corporate
   action on the underlying at all**, so no international source carries it.

*Confirmed instance.* The Apple CEDEAR shows a clean ~2:1 step on **2024-01-24** — the
CEDEAR price roughly halved while the US-listed share moved −0.35%, weeks after the
December 2023 devaluation had roughly doubled CEDEAR peso prices. No underlying corporate
action. A US-centric pipeline would have recorded a spurious 49% one-day currency move.

**Providers do not appear to adjust for ratio changes.** The same series runs smoothly
through the underlying's 2020 4:1 split — consistent not with the vendor rebasing history,
but with the *issuer* having changed the ratio by exactly the split factor, leaving the
peso price continuous. The practical implication: CEDEAR price series are best treated as
**as-traded**, with ratio changes appearing as genuine, unmarked discontinuities.

> **Modelling conclusions.**
> 1. **A scalar `ratio` field is insufficient.** Ratio must be dated, and any
>    calculation relating a CEDEAR to its underlying must use the ratio in force on the
>    observation date.
> 2. **Ratio changes are corporate actions** with an announcement date, an effective
>    date and a published value.
> 3. **Ratio history is publicly obtainable** via the CNV's AIF and quarterly issuer
>    reports. It should never be reverse-engineered from price discontinuities — that
>    inference is fragile in any week combining a ratio change with normal volatility.

---

## 6. CEDEAR economics differ from the underlying

Beyond FX, several wedges separate a CEDEAR's return from its underlying's:

| Wedge | Effect |
|---|---|
| **Issuer fees on dividends** | Prospectuses must disclose a dividend-payment commission. CEDEAR total return < underlying total return. |
| **Issuance/cancellation fees** | Charged on creation and redemption. |
| **Arbitrage imperfection** | Local price can trade at a premium or discount to theoretical value. |
| **Which dollar** | CEDEARs track CCL more than MEP; the *canje* flows into the return. |
| **Local liquidity** | Many CEDEARs are thin. Stale prices corrupt volatility and correlation estimates. |

> **Modelling conclusion.** Never present a CEDEAR's return as the underlying's return
> converted at an exchange rate. They are different instruments with different cash
> flows, fees and liquidity.

---

## 7. Ticker suffixes and settlement mechanism

A single Argentine security commonly quotes under **several tickers simultaneously**,
differing by settlement currency and venue:

| Pattern | Currency | Settles | Example |
|---|---|---|---|
| base ticker | ARS | local | `GGAL`, `BMA`, `PAMP` |
| suffix **C** | USD | abroad (CCL) | `GGALC`, `BMA.C` |
| suffix **D** | USD | locally (MEP) | `GGALD`, `BMA.D` |
| suffix **B** | ARS | local | `GGALB`, `BMADB` — **meaning unconfirmed** |

**The `B` suffix is an open question.** Observed instances carry the *same* currency and
settlement mechanism as the base ticker, so neither field distinguishes them. Candidate
explanations — a different settlement period (*contado inmediato* versus the standard
*plazo*), a share class, or a market segment — remain unverified. Treat any code that
assumes currency plus settlement uniquely identifies a listing as unsafe.

> **Modelling conclusion.** These are genuinely distinct listings from the exchange's
> point of view, with their own order books and prices. Whether they are one instrument
> or several depends on the question being asked — and the *canje* means the C and D
> variants of the same share do **not** have identical USD prices.

---

## 8. Deriving implied FX

The implied rate from any ARS/USD security pair is:

```
implied rate = ARS price ÷ USD price       (direct dual listing)
implied rate = ARS price ÷ (USD price ÷ conversion ratio_as_of_date)   (CEDEAR)
```

**Sovereign bonds are the market-standard reference**, not equities — typically the
locally-issued and foreign-law USD bonds against their ARS-quoted counterparts. They are
more liquid and less contaminated by idiosyncratic equity risk. <cite index="4-1">Corporates use CCL through sovereign bonds to settle transfers and imports.</cite>

Equity- and CEDEAR-derived rates are usable but noisier: thin volume, non-synchronous
closes between BYMA and US venues, and instrument-specific supply-demand distortions all
show up as apparent FX movement.

**Timing matters.** BYMA and US market hours only partially overlap. A rate computed
from two closes is a rate between two different moments.

---

## 9. Other Argentine instrument classes

| Class | Notes for modelling |
|---|---|
| **Acciones locales** | Domestic equities. Multiple settlement tickers as above. Merval is the headline index. |
| **ADRs** | Argentine companies listed abroad (YPF, Banco Macro, Pampa). Separately regulated; depositary and custodian banks must be identified, with specific divergent-voting rules. **A distinct relationship from CEDEAR — opposite direction, no conversion-ratio mechanics.** |
| **Doble Listado** | Foreign companies listing their *actual shares* locally under a special regime. **No wrapper, no ratio, no custodian** — a third distinct relationship type. |
| **Soberanos** | Sovereign bonds. Local-law and foreign-law variants trade at different prices — the spread itself is a watched indicator. The backbone of MEP/CCL computation. |
| **ONs** | Corporate bonds. Frequently USD-denominated (hard dollar) or dollar-linked. Need clean/dirty price, accrued interest and amortisation schedules — a separate domain from equities, not a variant. |
| **CER / UVA instruments** | Principal indexed to inflation. Nominal price series are uninterpretable without the index. |
| **LECAP / Treasury bills** | Short-dated peso instruments; yields quoted on local conventions. |
| **FCI** | Mutual funds; NAV-based, not exchange-priced. |
| **CEVA** | **New (RG 1142/2026).** Local vehicle for creating passive ETPs. Requires daily basket publication, real-time indicative NAV, tracking-error metrics, and disclosure of securities-lending policy. Cannot be composed of ETF fund units, other CEVA ETPs or CEDEARs. Leveraged and inverse structures are restricted to qualified investors. |

---

## 10. Inflation: nominal ARS series are not analysable

Argentina has run high inflation for years. Consequences that are not optional:

- **Nominal ARS returns over any horizon beyond a few months are close to meaningless.**
  A 100% nominal annual return may be a real loss.
- **Real returns require an index** — CER or the INDEC CPI — applied as of each
  observation date.
- **Sharpe and Sortino ratios need an ARS risk-free rate.** Without an explicit,
  documented choice, risk-adjusted metrics on ARS-denominated series are not computable
  and should be suppressed rather than approximated.
- **A USD-expressed series is not automatically a real series.** It is a nominal USD
  series, subject to US inflation and to whichever implied rate was used.

Notably, the CEVA regime **prohibits reference indices from being subject to
retroactive adjustment of already-published values** — a useful regulatory precedent for
anyone storing index history.

---

## 11. Data sources

| Source | Provides | Characteristics |
|---|---|---|
| **BYMA** (`open.bymadata.com.ar`) | Local panels, all settlement variants | Geo-sensitive; incomplete certificate chain; suffix parsing quirks; `denominationCcy` is the authoritative currency field; `securityDesc` is a misnomer; symbols can be truncated |
| **Yahoo `.BA` tickers** | Cross-listed ARS prices, multi-year history | **One feed per company, not per settlement mechanism** — so the C/D/B variants are not separately available. Convenient but flattens the settlement dimension. |
| **CNV AIF** | Prospectuses, supplements, material events, quarterly issuer reports | **The authoritative source for conversion ratios and CEDEAR corporate actions.** Document-oriented, not a price API. |
| **Markets' own disclosure** | Prices and volumes of underlyings; real-time CEVA baskets and indicative NAV | Regulation requires markets to make underlying prices and volumes publicly available |
| **BCRA** | Official rates, reserves, monetary aggregates | Authoritative for the official rate |
| **INDEC** | CPI, CER | Required for any real-return work |

---

## 12. Practical gotchas

1. **Currency plus settlement does not uniquely identify a listing** (the `B` suffix
   problem). Do not build a primary key on that assumption.
2. **A CEDEAR's conversion ratio applies as of a date.** A constant ratio silently
   corrupts any historical series crossing a ratio change.
3. **Splits on the underlying may surface as ratio changes**, leaving no visible
   discontinuity in the CEDEAR price — or as a rescale, leaving a large one. Which
   happens depends on the issuer.
4. **Never infer a ratio from a price discontinuity.** The authoritative value is
   published.
5. **Choose and record the FX rate type.** CCL and MEP differ by the *canje*; using the
   wrong one is a systematic error, not noise.
6. **BYMA and US calendars differ.** Holiday sets diverge; correlation and beta
   computed on misaligned dates are wrong.
7. **Many CEDEARs are illiquid.** Stale prices inflate apparent stability. Volatility on
   a series with multi-day gaps is not volatility.
8. **A ticker string is not an identity.** Argentine tickers collide with foreign ones,
   and cross-listing suffixes are not reliably unique across data providers.
9. **Regimes change.** Capital controls, parking requirements and cross-restrictions have
   varied repeatedly. Historical analysis must respect the rules in force at the time.
10. **CEDEARs can be cancelled.** The CNV may cancel a CEDEAR ex officio if it remains in
    a cancellation or liquidation event for six months without remedy, requiring redemption
    within a set period. Delisting and cancellation are different lifecycle states.

---

## 13. Conclusions

1. **The wrapper is not the asset class.** Instrument-awareness must key on the
   underlying, not on "CEDEAR". This is a regulatory requirement, not a preference.
2. **Conversion ratios are temporal data.** Any model storing a scalar ratio will produce
   wrong historical figures, and the errors will look plausible.
3. **There are three distinct depositary/listing relationships** — CEDEAR, ADR and Doble
   Listado — with different mechanics. One relationship type cannot represent all three.
4. **Currency is a first-class analytical dimension, not a display setting.** Which
   dollar, derived from which instrument, on which date.
5. **Nominal ARS is not an analytical currency.** Real terms or a stated USD basis, with
   the conversion documented.
6. **The authoritative sources for corporate actions are regulatory, not commercial.**
   The AIF carries what price vendors do not.
7. **This is where the analytical edge is.** Convenient international products handle US
   equities well and Argentine settlement, ratio and FX structure poorly or not at all.
   Getting these right is more defensible than replicating a quote page.

---

## 14. What this brief does not settle

- The meaning of the `B` ticker suffix.
- Whether price vendors rebase CEDEAR history for past ratio changes (testable: compute
  an implied-FX series with a constant ratio and look for step discontinuities at known
  ratio-change dates).
- Current standard settlement periods on BYMA, which have changed over time.
- Whether a multi-settlement security is best modelled as one entity with a settlement
  attribute or as several related entities — the answer likely depends on whether a
  per-settlement price source is available.
- Which sovereign bond pair is currently the market-standard CCL/MEP reference.
