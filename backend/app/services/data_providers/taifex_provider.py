from app.services.data_providers.base import MarketDataProvider

TAIFEX_OPENAPI_BASE_URL = "https://openapi.taifex.com.tw"

TAIFEX_ENDPOINTS = {
    "openapi_home": "https://openapi.taifex.com.tw/",
    "swagger_json": f"{TAIFEX_OPENAPI_BASE_URL}/swagger.json",
    "official_portal": "https://www.taifex.com.tw/",
}


class TAIFEXProvider(MarketDataProvider):
    """Official TAIFEX provider placeholder.

    TAIFEX OpenAPI is intended for Taiwan futures/options linkage factors such
    as TAIEX futures, electronics futures, financial futures, options,
    institutional futures flow, and market positioning. Live fetching remains
    disabled until endpoint field mappings and usage terms are implemented.
    """

    base_url = TAIFEX_OPENAPI_BASE_URL
    endpoints = TAIFEX_ENDPOINTS

    def get_instruments(self):
        return []
