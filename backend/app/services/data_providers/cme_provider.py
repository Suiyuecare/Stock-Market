from app.services.data_providers.us_market_provider import US_MARKET_ENDPOINTS

CME_ENDPOINTS = {
    "market_data_apis": US_MARKET_ENDPOINTS["cme_market_data_apis"],
    "realtime_futures_options_api": US_MARKET_ENDPOINTS["cme_realtime_futures_options_api"],
    "reference_data_api": US_MARKET_ENDPOINTS["cme_reference_data_api"],
}


class CMEProvider:
    """CME market data placeholder for futures and reference data."""

    endpoints = CME_ENDPOINTS
    requires_license = True
