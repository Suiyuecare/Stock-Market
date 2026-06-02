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
