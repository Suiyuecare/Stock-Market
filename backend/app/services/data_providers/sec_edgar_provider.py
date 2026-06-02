from app.services.data_providers.sec_provider import (
    SEC_ENDPOINTS,
    SEC_FILINGS_OF_INTEREST,
    SECProvider,
)


class SECEdgarProvider(SECProvider):
    """Alias provider for SEC EDGAR filings and XBRL company facts."""

    endpoints = SEC_ENDPOINTS
    filings_of_interest = SEC_FILINGS_OF_INTEREST
