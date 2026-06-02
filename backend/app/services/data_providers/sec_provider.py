from app.services.data_providers.base import MarketDataProvider

SEC_ENDPOINTS = {
    "edgar_api_docs": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
    "submissions": "https://data.sec.gov/submissions/CIK{CIK}.json",
    "company_facts": "https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json",
    "ticker_to_cik": "https://www.sec.gov/files/company_tickers.json",
}

SEC_FILINGS_OF_INTEREST = ["10-K", "10-Q", "8-K"]


class SECProvider(MarketDataProvider):
    """SEC EDGAR provider placeholder.

    SEC JSON APIs can feed US filing events, earnings-related filings, 10-K,
    10-Q, 8-K, and XBRL company facts. SEC APIs do not require an API key, but
    production requests should include a compliant User-Agent.
    """

    endpoints = SEC_ENDPOINTS
    filings_of_interest = SEC_FILINGS_OF_INTEREST
    requires_api_key = False
    requires_user_agent = True

    def get_instruments(self):
        return []
