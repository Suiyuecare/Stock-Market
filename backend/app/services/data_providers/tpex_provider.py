from app.services.data_providers.base import MarketDataProvider

TPEX_OPENAPI_BASE_URL = "https://www.tpex.org.tw/openapi"

TPEX_ENDPOINTS = {
    "openapi_home": "https://www.tpex.org.tw/openapi/",
    "swagger_json": f"{TPEX_OPENAPI_BASE_URL}/swagger.json",
    "data_purchase": "https://www.tpex.org.tw/zh-tw/service/data/overview.html",
    "delayed_trading_license": "https://www.tpex.org.tw/zh-tw/service/data/product/delay.html",
    "after_market_download_system": "https://intd.tpex.org.tw",
}


class TPEXProvider(MarketDataProvider):
    """Official TPEx provider placeholder.

    TPEx OpenAPI covers OTC, emerging stock, innovation board, and bond
    issuance/trading information. Live fetching remains disabled until endpoint
    field mappings and data-license rules are implemented.
    """

    base_url = TPEX_OPENAPI_BASE_URL
    endpoints = TPEX_ENDPOINTS

    def get_instruments(self):
        return []
