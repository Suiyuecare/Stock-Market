from app.services.data_providers.us_macro_provider import (
    FRED_OBSERVATIONS_URL,
    FRED_SERIES_EXAMPLES,
    USMacroProvider,
)

FRED_ENDPOINTS = {
    "api_docs": "https://fred.stlouisfed.org/docs/api/fred/",
    "observations": FRED_OBSERVATIONS_URL,
}


class FREDProvider(USMacroProvider):
    """FRED macro provider placeholder."""

    endpoints = FRED_ENDPOINTS
    series_examples = FRED_SERIES_EXAMPLES
