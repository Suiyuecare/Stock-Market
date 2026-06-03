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

## Implemented Open-Data Providers

The codebase now includes production-shaped provider classes for legal open-data ingestion. These providers use injectable HTTP clients so tests do not depend on external network availability.

| Provider | File | Current capability |
| --- | --- | --- |
| TWSE / MOPS listed data | `backend/app/services/data_providers/twse_provider.py` | Fetch and parse listed company profiles, market index JSON, listed material information JSON, and monthly revenue CSV |
| MOPS / mopsfin | `backend/app/services/data_providers/mops_provider.py` | Fetch and parse listed company profiles, monthly revenue CSV, and listed material information CSV |
| CNA RSS | `backend/app/services/data_providers/news_provider.py` | Fetch and parse CNA finance and technology RSS into normalized news event payloads |

Deployment notes:

- These providers are safe to use as the first official-data layer, but their endpoint terms should still be reviewed before storing or redisplaying raw payloads.
- The frontend must label data freshness and source status clearly.
- Scheduled jobs still need to be switched from `MockMarketDataProvider` to official providers before claiming production data coverage.
- Paid, real-time, analyst estimate, and licensed news providers remain disabled until contracts, API keys, and display rights are confirmed.

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

## News / RSS / Financial News Data Sources

These providers can feed NewsScore, event timelines, earnings/revenue news classification, sector sentiment, US linkage news, and risk-event detection. RSS and free/news-trial APIs still require terms-of-use review before production ingestion or redistribution.

| # | API / Source | Purpose | URL |
| -: | --- | --- | --- |
| 73 | CNA RSS documentation | Taiwan news RSS documentation | `https://www.cna.com.tw/about/rss.aspx` |
| 74 | CNA finance and securities RSS | Taiwan stock / industry news | `https://feeds.feedburner.com/rsscna/finance` |
| 75 | CNA technology RSS | Technology / AI / semiconductor news | `https://feeds.feedburner.com/rsscna/technology` |
| 76 | Anue Cnyes Open API documentation | Taiwan stocks, US stocks, financial news and market data; commercial cooperation required | `https://openapi.api.cnyes.com/swagger-ui.html` |
| 77 | Anue Cnyes OpenAPI base | Cnyes API base | `https://openapi.api.cnyes.com/` |
| 78 | NewsAPI documentation | Global news search backup | `https://newsapi.org/docs` |
| 79 | NewsAPI REST base | NewsAPI base | `https://newsapi.org/v2` |
| 80 | NewsAPI Everything endpoint | Search news articles | `https://newsapi.org/v2/everything` |
| 81 | Reuters API Integrations | Reuters international financial news | `https://reutersagency.com/content-delivery-platforms/api-integrations/` |
| 82 | LSEG News API | Reuters / LSEG News API | `https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/news-API` |
| 83 | Thomson Reuters Developer Portal | Reuters / TR developer entry point | `https://developers.thomsonreuters.com/` |
| 84 | NewsData.io documentation | Multi-country news backup | `https://newsdata.io/documentation` |
| 85 | TheNewsAPI documentation | Multi-country news backup | `https://www.thenewsapi.com/documentation` |

Implementation notes:

- The production Next.js frontend now directly reads official/open news sources when the FastAPI service is not available: TWSE/MOPS material information (`/opendata/t187ap04_L`), TWSE news (`/news/newsList`), TWSE events (`/news/eventList`), CNA finance RSS, and CNA technology RSS.
- Individual stock pages first match material information by company code, then add contextual CNA/TWSE events by company name, sector, and supply-chain keywords. The resulting events update `NewsScore`, event risk, timeline display, and source references.
- Keep mock news only as a local resilience fallback when every official/open source is unreachable.
- Treat Cnyes, Reuters/LSEG, NewsAPI, NewsData.io, and TheNewsAPI as licensed or key-based integrations; do not commit credentials.
- Cnyes Open API is not assumed free for production use. Confirm commercial cooperation, data scope, display rights, and redistribution terms before enabling it.
- Normalize all provider payloads into event time, market, stock ID or related symbol, source, title, summary, sentiment score, event type, impact score, confidence, and URL.
- Store raw provider payloads only if license terms allow retention; otherwise store normalized event metadata needed for scoring and auditability.
- Keep source attribution available in API responses so the UI can explain why a `NewsScore` was generated.

## OpenAI API / News Parsing / Event Classification

OpenAI can power the AI news parser interface for summarization, event classification, company/ticker matching, US-to-Taiwan supply-chain linkage reasoning, investor-conference summaries, and structured `NewsScore` inputs. The MVP keeps this as an optional provider and falls back to rule-based parsing when no API key is configured.

| # | API / Source | Purpose | URL |
| -: | --- | --- | --- |
| 86 | OpenAI Platform | Developer platform | `https://platform.openai.com/` |
| 87 | OpenAI API Reference | API documentation | `https://platform.openai.com/docs/api-reference` |
| 88 | OpenAI Responses API endpoint | News summarization, classification, reasoning | `https://api.openai.com/v1/responses` |
| 89 | OpenAI API Keys | API key management | `https://platform.openai.com/api-keys` |
| 90 | OpenAI Pricing | Cost estimation | `https://openai.com/api/pricing/` |

Implementation notes:

- Store OpenAI credentials only in local or deployment environment variables such as `OPENAI_API_KEY`; never commit plaintext API keys.
- Use the Responses API behind the existing `NewsParser` interface so the app can keep a rule-based fallback for local tests and demos.
- Request structured output for summary, tickers, related Taiwan stock IDs, related US symbols, event type, sentiment, impact score, confidence, and reasoning notes.
- Keep prompts product-safe: classify research signals and risk events, but do not generate personalized investment advice or direct order instructions.
- Add cost controls before production use: model selection, max output size, timeout, retry limits, caching, and batch/background processing for scheduled news jobs.
- Keep source URLs and attribution from the original news provider; OpenAI should classify and summarize, not become the source of market facts.

## Brokerage Trading / Real-Time Taiwan Quote APIs

The MVP is an analysis and alerting app, so it does not require brokerage APIs. Broker APIs should only be considered for a future product scope that includes simulated trading, live order routing, account balances, positions, order reports, or execution reports.

| # | API / Source | Purpose | URL |
| -: | --- | --- | --- |
| 91 | SinoPac Shioaji official portal | Taiwan stocks / futures orders, real-time quotes, account data | `https://ai.sinotrade.com.tw/python/Main/index.aspx` |
| 92 | Shioaji GitHub Docs | SinoPac API documentation | `https://sinotrade.github.io/` |
| 93 | Fubon Neo API Trading Docs | Fubon order API | `https://www.fbs.com.tw/TradeAPI/en/docs/trading/introduction` |
| 94 | Fubon Neo API Market Data | Fubon Taiwan stock market data API | `https://www.fbs.com.tw/TradeAPI/en/docs/market-data/intro/` |
| 95 | Fubon Neo Futures Market Data | Fubon Taiwan futures market data API | `https://www.fbs.com.tw/TradeAPI/en/docs/market-data-future/intro` |
| 96 | Yuanta SPARK API | Yuanta Securities trading API platform | `https://www.yuanta.com.tw/file-repository/content/API/page/index.html` |
| 97 | Yuanta API order service | Yuanta API order application notes | `https://www.yuanta.com.tw/eyuanta/Securities/DigitalArea/ApiOrder` |
| 98 | Yuanta Futures API | Yuanta Futures API | `https://www.yuantafutures.com.tw/ytf/easywin/api/download.html` |

Implementation notes:

- Do not enable live order placement in the current MVP.
- Keep any future brokerage integration behind an explicit `BrokerageProvider` boundary with separate permissions for market data, simulation, order routing, account data, positions, and order reports.
- Require user opt-in, broker account approval, certificate/API-key setup, paper-trading tests, and risk controls before any live trading feature.
- Store broker credentials, certificates, and API keys outside the repository and outside client-side frontend code.
- For real-time quote display, confirm exchange/vendor redistribution terms before streaming data to users or storing tick data.
- Product copy must continue to avoid direct investment instructions. Brokerage APIs are infrastructure capabilities, not recommendations.

## App Operations APIs

These providers support user notifications, transactional email, SMS, billing, authentication, project management, and production monitoring. They are infrastructure services, not market-data sources. Keep all secret keys in deployment environment variables and never expose server-side keys in the browser.

| API / Source | Purpose | URL |
| --- | --- | --- |
| Firebase Cloud Messaging Docs | Push notification setup | `https://firebase.google.com/docs/cloud-messaging` |
| Firebase Cloud Messaging REST Docs | FCM REST API reference | `https://firebase.google.com/docs/reference/fcm/rest` |
| Firebase Cloud Messaging send endpoint | Send push notifications | `https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send` |
| SendGrid API reference | Transactional email API | `https://www.twilio.com/docs/sendgrid/api-reference` |
| SendGrid Mail Send endpoint | Send transactional email | `https://api.sendgrid.com/v3/mail/send` |
| Twilio Messaging API | SMS and messaging API | `https://www.twilio.com/docs/messaging/api` |
| Twilio SMS endpoint | Send SMS messages | `https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json` |
| Stripe API docs | Billing and payments API | `https://docs.stripe.com/api` |
| Stripe REST base | Stripe REST API base | `https://api.stripe.com/v1` |
| Supabase Auth docs | Auth, Google OAuth, sessions, JWT, RLS integration | `https://supabase.com/docs/guides/auth` |
| Supabase Data API docs | Auto-generated Postgres REST API | `https://supabase.com/docs/guides/api` |
| Supabase Management API | Supabase project management API | `https://api.supabase.com/api/v1` |
| Auth0 Management API | Alternative identity provider management API | `https://auth0.com/docs/api/management/v2` |
| Auth0 tenant API base | Tenant-specific Auth0 Management API base | `https://{YOUR_DOMAIN}/api/v2/` |
| Clerk Backend API | Alternative identity provider backend API | `https://clerk.com/docs/reference/backend-api` |
| Clerk REST base | Clerk REST API base | `https://api.clerk.com/v1` |
| Sentry API docs | Error monitoring and release operations API | `https://docs.sentry.io/api/` |
| Sentry REST base | Sentry REST API base | `https://sentry.io/api/0` |

Implementation notes:

- Use Supabase Auth first for Google login unless product requirements later justify Auth0 or Clerk.
- Enable RLS on user-owned tables exposed through Supabase Data API and never use Supabase service-role keys in frontend code.
- Keep payment features behind a separate Stripe integration scope with webhook verification, idempotency, and server-only secret keys.
- Notifications should be opt-in and user-scoped. Store notification preferences per user before sending push, email, or SMS alerts.
- FCM, SendGrid, Twilio, Stripe, Supabase Management, Auth0, Clerk, and Sentry keys must be server-side environment variables only.
- For the MVP, implement mock notification and billing adapters first so local development and tests do not call external services.

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

### TWSE OpenAPI Catalog

The full TWSE Swagger endpoint catalog from `https://openapi.twse.com.tw/#/` is now stored in:

- `backend/app/services/data_providers/twse_openapi_catalog.json`
- `docs/TWSE_OPENAPI_CATALOG.md`

Current official catalog coverage:

| Category | Endpoint count |
| --- | ---: |
| 證券交易 | 36 |
| 財務報表 | 30 |
| 公司治理 | 56 |
| 券商資料 | 9 |
| 指數 | 5 |
| 權證 | 3 |
| 其他 | 4 |
| Total | 143 |

Provider helpers:

- `load_twse_openapi_catalog()`: load the full static catalog.
- `list_twse_openapi_endpoints(tag=None)`: list all TWSE OpenAPI endpoints or filter by official Swagger tag.
- `get_twse_openapi_endpoint(path_or_id)`: find an endpoint by path, generated id, or URL.
- `TWSEProvider.fetch_openapi_endpoint(path_or_id)`: fetch any cataloged TWSE endpoint using an injectable HTTP client.

Use the catalog as the source of endpoint truth, then implement explicit normalization into application tables for each dataset used by scores or UI pages.

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
