from app.services.data_providers.us_macro_provider import (
    BLS_SERIES_EXAMPLES,
    BLS_TIMESERIES_URL,
    USMacroProvider,
)

BLS_ENDPOINTS = {
    "api_docs": "https://www.bls.gov/developers/home.htm",
    "timeseries_v2": BLS_TIMESERIES_URL,
}


class BLSProvider(USMacroProvider):
    """BLS macro provider placeholder."""

    endpoints = BLS_ENDPOINTS
    series_examples = BLS_SERIES_EXAMPLES
