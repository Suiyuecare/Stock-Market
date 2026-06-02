from app.services.data_providers.sec_provider import SEC_ENDPOINTS, SEC_FILINGS_OF_INTEREST, SECProvider


def test_sec_provider_exposes_edgar_endpoints() -> None:
    provider = SECProvider()

    assert provider.requires_api_key is False
    assert provider.requires_user_agent is True
    assert SEC_ENDPOINTS["ticker_to_cik"] == "https://www.sec.gov/files/company_tickers.json"
    assert SEC_ENDPOINTS["submissions"] == "https://data.sec.gov/submissions/CIK{CIK}.json"
    assert SEC_ENDPOINTS["company_facts"] == "https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"


def test_sec_provider_tracks_filings_of_interest() -> None:
    assert SEC_FILINGS_OF_INTEREST == ["10-K", "10-Q", "8-K"]
