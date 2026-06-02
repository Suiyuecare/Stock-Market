# Data Sources

## Principle

Use legal, documented data providers. Do not build the product around scraping or redistributing data whose license is unclear.

## Required Data Categories

### Taiwan Market Data

- Daily OHLCV
- Corporate actions
- Sector classification
- Market calendar
- Foreign/institutional flow when available

### US Linkage Data

- NASDAQ futures
- S&P 500 futures
- Major US tech stocks
- Semiconductor sector proxy
- ADR data for Taiwan-linked companies
- FX: USD/TWD, DXY

## US / Global Market Data Sources

These providers can feed USMarketScore, pre-open radar, futures linkage, FX, commodities, and backup technical/news data. Most require API keys or commercial licensing.

| # | API / Source | Purpose | URL |
| -: | --- | --- | --- |
| 38 | Massive / Polygon Docs | US stocks, ETFs, indices, options, crypto, FX quotes | `https://massive.com/docs` |
| 39 | Massive / Polygon REST base | US market data REST API | `https://api.polygon.io` |
| 40 | Massive / Polygon WebSocket | US stock real-time streaming | `wss://socket.polygon.io/stocks` |
| 41 | Finnhub API Docs | US quotes, company fundamentals, news, economic data | `https://finnhub.io/docs/api` |
| 42 | Finnhub REST base | Finnhub API base | `https://finnhub.io/api/v1` |
| 43 | Nasdaq Data Link Docs | Global datasets, commodities, futures, alternative data | `https://docs.data.nasdaq.com/` |
| 44 | Nasdaq Data Link API | Nasdaq Data Link REST API | `https://data.nasdaq.com/api/v3` |
| 45 | Nasdaq Data Link API product page | Real-time exchange data and REST / streaming API notes | `https://www.nasdaq.com/solutions/data/nasdaq-data-link/api` |
| 46 | Alpha Vantage Docs | US stocks, ETFs, FX, commodities, technical indicator backup | `https://www.alphavantage.co/documentation/` |
| 47 | Alpha Vantage base | REST API base | `https://www.alphavantage.co/query` |
| 48 | CME Group Market Data APIs | NQ / ES futures, FedWatch, futures/options data | `https://www.cmegroup.com/market-data/market-data-api.html` |
| 49 | CME Real-Time Futures & Options API | CME WebSocket real-time futures/options | `https://www.cmegroup.com/market-data/real-time-futures-and-options-data-api.html` |
| 50 | CME Reference Data API | CME product and contract reference data | `https://www.cmegroup.com/trading/market-tech-and-data-services/cme-reference-data-api.html` |
| 51 | ICE Developer Center | ICE Data Services API documentation | `https://developer.theice.com/hc/en-us` |
| 52 | ICE Data API / Commodity Energy Data | Energy, commodity, derivatives data | `https://developer.ice.com/fixed-income-data-services/catalog/ice-data-derivatives-commodity-energy-data` |
| 53 | Intrinio Docs | US stocks, fundamentals, options, news backup source | `https://docs.intrinio.com/documentation/api_v2/getting_started` |
| 54 | Twelve Data Docs | US stocks, FX, crypto, technical indicator backup | `https://twelvedata.com/docs` |
| 55 | EODHD API | Global stocks, ETFs, FX, news, technical indicator backup | `https://eodhd.com/` |
| 56 | FRED API Docs | US macro, Treasury yields, Fed Funds, USD, credit spreads | `https://fred.stlouisfed.org/docs/api/fred/` |
| 57 | FRED observations endpoint | Time-series observations | `https://api.stlouisfed.org/fred/series/observations` |
| 58 | BLS API Docs | CPI, PPI, unemployment, nonfarm payrolls, wages | `https://www.bls.gov/developers/home.htm` |
| 59 | BLS API v2 endpoint | BLS time-series API | `https://api.bls.gov/publicAPI/v2/timeseries/data/` |
| 60 | SEC EDGAR API Docs | SEC filings and XBRL data | `https://www.sec.gov/search-filings/edgar-application-programming-interfaces` |
| 61 | SEC submissions endpoint | Company filing history | `https://data.sec.gov/submissions/CIK{CIK}.json` |
| 62 | SEC company facts endpoint | XBRL company financial facts | `https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json` |
| 63 | SEC ticker-to-CIK | US ticker to CIK mapping | `https://www.sec.gov/files/company_tickers.json` |

Implementation notes:

- Keep all US/global providers optional and keyed through environment variables.
- Use Massive/Polygon or Finnhub as primary candidates for US equity and ETF linkage when licensing allows.
- Use CME for NQ/ES futures and Fed/futures-related pre-open signals.
- Use Nasdaq Data Link, ICE, Intrinio, Twelve Data, Alpha Vantage, and EODHD as evaluated backup/enrichment sources.
- Do not enable WebSocket streaming in the MVP until real-time licensing, cost, and reliability requirements are clear.
- Use FRED and BLS for US macro factors such as yields, Fed Funds, credit spreads, CPI, PPI, unemployment, nonfarm payrolls, and wages.
- Use SEC EDGAR JSON APIs for US company filing events, 10-K, 10-Q, 8-K, and XBRL company facts. SEC APIs do not require an API key, but requests should include a compliant User-Agent.

### News and Events

- Company news
- Sector news
- Macro news
- Earnings and guidance
- Regulatory/geopolitical events

## Candidate Providers

These are candidates to evaluate, not final commitments:

- Taiwan Stock Exchange open data
- Taipei Exchange open data
- Financial Modeling Prep
- Polygon.io
- Alpha Vantage
- Nasdaq Data Link
- NewsAPI or licensed news feeds
- RSS feeds where terms allow processing

## Commercial Taiwan Data Sources

Commercial providers require a paid contract or trial key before use. Never commit provider API keys; store them in `.env.local` or deployment environment variables.

| # | API / Source | Purpose | URL |
| -: | --- | --- | --- |
| 33 | TEJ API official portal | Main Taiwan commercial data API | `https://api.tej.com.tw/` |
| 34 | TEJ API documentation | API usage guide | `https://www.tejwin.com/en/insight/tej-api-document/` |
| 35 | TEJ REST API documentation | REST API integration guide | `https://www.tejwin.com/en/insight/tej-rest-api-document/` |
| 36 | TEJ Taiwan Stock Data Solutions | Taiwan market, financial, fundamental, event data solutions | `https://www.tejwin.com/en/solution/taiwan-stock-data/` |
| 37 | TEJ REST base URL | Programmatic REST base URL | `https://api.tej.com.tw/api/` |

Implementation notes:

- Use TEJ only after license scope, redistribution rights, and API limits are confirmed.
- Use TEJ as an optional enrichment provider for fundamentals, financial statements, adjusted prices, corporate actions, events, and historical data coverage.
- Keep TEJ behind provider interfaces so the app can still run with official open data and mock data when no commercial key is configured.

## Analyst Estimates / Target Price Data Sources

These commercial providers can feed TargetPriceScore, EPS consensus, target price changes, rating revisions, analyst hit-rate studies, and valuation forecast factors.

| # | API / Source | Purpose | URL |
| -: | --- | --- | --- |
| 64 | FactSet Developer | FactSet API portal | `https://developer.factset.com/` |
| 65 | FactSet Estimates API | EPS estimates, consensus estimates, financial forecasts | `https://developer.factset.com/api-catalog/factset-estimates-api` |
| 66 | FactSet Estimates Report Builder | Report-ready consensus estimate data | `https://developer.factset.com/api-catalog/factset-estimates-report-builder-api` |
| 67 | LSEG I/B/E/S Estimates | Analyst estimates, target prices, ratings, consensus data | `https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates` |
| 68 | LSEG Estimates API for Wealth | I/B/E/S API documentation entry | `https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/estimates-API` |
| 69 | Bloomberg B-PIPE | High-end real-time global market data | `https://professional.bloomberg.com/products/data/enterprise-catalog/real-time-data-feed/` |
| 70 | Bloomberg Server API SAPI | Bloomberg real-time / historical / reference API | `https://professional.bloomberg.com/products/data/data-connectivity/server-api/` |
| 71 | Bloomberg Data License | Bloomberg REST API / SFTP / cloud data license | `https://professional.bloomberg.com/products/data/data-management/data-license/` |
| 72 | Bloomberg Web API host | Bloomberg Web API host, requires license | `https://api.bloomberg.com` |

Implementation notes:

- Use these sources only after commercial contract, redistribution rights, and analyst-data display rights are confirmed.
- Do not commit FactSet, LSEG, or Bloomberg credentials.
- Keep these integrations behind a TargetPrice/AnalystEstimates provider so `TargetPriceScore` can remain a neutral placeholder when no license is configured.
- Normalize provider payloads into EPS consensus, revenue consensus, target price mean/high/low, recommendation revisions, estimate revision direction, analyst count, and data freshness.

## Official Taiwan Data Sources

Use official TWSE/MOPS/TPEx/TAIFEX/TDCC/CBC/DGBAS sources first for Taiwan equities, derivatives, ownership concentration, macro factors, and market linkage. These endpoints are suitable for scheduled MVP ingestion, not real-time intraday redistribution.

| # | API / Source | Purpose | URL |
| -: | --- | --- | --- |
| 1 | TWSE OpenAPI | Listed stocks, indices, after-market data, monthly revenue, company data | `https://openapi.twse.com.tw/` |
| 2 | TWSE Swagger JSON | Machine-readable endpoint specification | `https://openapi.twse.com.tw/v1/swagger.json` |
| 3 | TWSE OpenAPI Base URL | Programmatic base URL | `https://openapi.twse.com.tw/v1` |
| 4 | TWSE market index statistics | Weighted index and market statistics | `https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX` |
| 5 | TWSE listed material information | Listed company daily material information | `https://openapi.twse.com.tw/v1/opendata/t187ap04_L` |
| 6 | MOPS listed company profile CSV | Stock master, company profile, industry data | `https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv` |
| 7 | MOPS listed material information CSV | Backup material information source | `https://mopsfin.twse.com.tw/opendata/t187ap04_L.csv` |
| 8 | MOPS listed monthly revenue CSV | Monthly revenue YoY / MoM factors | `https://mopsfin.twse.com.tw/opendata/t187ap05_L.csv` |
| 9 | MOPS official portal | Financials, revenue, material information, investor conference query entry | `https://mops.twse.com.tw/mops/web/index` |
| 10 | MOPS financial comparison portal | Financial statements and financial-ratio queries | `https://mopsfin.twse.com.tw/` |
| 11 | TWSE data eShop | After-market data, history data, commercial data purchases | `https://eshop.twse.com.tw/` |
| 12 | TWSE real-time trading information licensing | Real-time listed equity quote licensing | `https://www.twse.com.tw/zh/products/information/real-time.html` |
| 13 | TWSE delayed trading information licensing | 20-minute delayed data licensing | `https://www.twse.com.tw/zh/products/information/delayed.html` |
| 14 | TWSE market information usage rules | Contracts, information fees, usage rules | `https://www.twse.com.tw/zh/products/information/use.html` |
| 15 | TPEx OpenAPI | OTC / emerging stock quotes, institutional flow, company data | `https://www.tpex.org.tw/openapi/` |
| 16 | TPEx Swagger JSON | Machine-readable TPEx API specification | `https://www.tpex.org.tw/openapi/swagger.json` |
| 17 | TPEx data purchase | OTC after-market trading data and information downloads | `https://www.tpex.org.tw/zh-tw/service/data/overview.html` |
| 18 | TPEx delayed trading information | OTC delayed quote licensing | `https://www.tpex.org.tw/zh-tw/service/data/product/delay.html` |
| 19 | TPEx after-market trading information download system | Paid subscription data download service | `https://intd.tpex.org.tw` |
| 20 | TAIFEX OpenAPI | Taiwan index futures, options, futures institutional data | `https://openapi.taifex.com.tw/` |
| 21 | TAIFEX Swagger JSON | Machine-readable TAIFEX API specification | `https://openapi.taifex.com.tw/swagger.json` |
| 22 | TAIFEX official portal | Official futures exchange data entry point | `https://www.taifex.com.tw/` |
| 23 | TDCC OpenAPI Swagger | TDCC OpenAPI documentation | `https://openapi-t.tdcc.com.tw/swagger-ui/index.html` |
| 24 | TDCC OpenData API Docs | TDCC OAS documentation entry point | `https://openapi.tdcc.com.tw/tdcc-opendata-api-docs` |
| 25 | TDCC OpenData legacy download | TDCC CSV / OpenData download entry | `https://smart.tdcc.com.tw/opendata/` |
| 26 | TDCC ownership distribution endpoint | Holding brackets, major holders, ownership concentration | `https://smart.tdcc.com.tw/opendata/getOD.ashx?id=1-5` |
| 27 | CBC statistics database | FX, rates, financial statistics, M2, FX reserves | `https://cpx.cbc.gov.tw/` |
| 28 | CBC API documentation | CBC API-JSON documentation | `https://cpx.cbc.gov.tw/Data/ExportToAPIInfo` |
| 29 | CBC API endpoint format | Programmatic API format | `https://cpx.cbc.gov.tw/API/DataAPI/Get?FileName={ITEM_CODE}` |
| 30 | DGBAS macro statistics database | CPI, GDP, unemployment, wages, export orders | `https://nstatdb.dgbas.gov.tw/dgbasall/webMain.aspx?k=main` |
| 31 | DGBAS API documentation PDF | API-JSON specification | `https://nstatdb.dgbas.gov.tw/dgbasall/download/API說明文件.pdf` |
| 32 | Government Open Data Platform | Supplemental Taiwan open-data source | `https://data.gov.tw/` |

Implementation notes:

- For MVP, prefer after-market/open data endpoints over real-time feeds.
- Keep TWSE/MOPS/TPEx/TAIFEX/TDCC/CBC/DGBAS ingestion behind provider interfaces.
- Do not redistribute real-time or delayed trading data without confirming license terms.
- Use `swagger.json` to generate or validate endpoint mappings before adding new fetch methods.
- Use MOPS CSV endpoints as fallback sources when an equivalent OpenAPI endpoint is unavailable.
- Use TPEx OpenAPI for OTC and emerging stock coverage once the field mapping is implemented.
- Use TAIFEX OpenAPI for Taiwan futures/options linkage, futures institutional positioning, and market position factors once endpoint field mapping is implemented.
- Use TDCC OpenData for ownership distribution, large-holder concentration, and chip concentration risk factors once endpoint field mapping is implemented.
- Use CBC and DGBAS official statistics for MacroScore inputs such as FX, rates, M2, CPI, GDP, unemployment, wages, and export orders once item-code mappings are implemented.

## Provider Evaluation Checklist

- License allows the intended use
- Redistribution terms are clear
- Historical coverage is sufficient
- API rate limits match scheduled jobs
- Cost is acceptable at MVP scale
- Data has stable identifiers
- Provider has uptime and support history

## MVP Approach

Use seed/sample data and provider interfaces first. Add one legal Taiwan daily data source and one US linkage data source before adding model complexity.
