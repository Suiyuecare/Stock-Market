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

## Official Taiwan Data Sources

Use official TWSE/MOPS sources first for listed Taiwan equities. These endpoints are suitable for scheduled MVP ingestion, not real-time intraday redistribution.

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

Implementation notes:

- For MVP, prefer after-market/open data endpoints over real-time feeds.
- Keep TWSE/MOPS ingestion behind provider interfaces.
- Do not redistribute real-time or delayed trading data without confirming license terms.
- Use `swagger.json` to generate or validate endpoint mappings before adding new fetch methods.
- Use MOPS CSV endpoints as fallback sources when an equivalent OpenAPI endpoint is unavailable.

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
