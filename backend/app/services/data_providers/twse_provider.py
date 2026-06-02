from app.services.data_providers.base import MarketDataProvider

TWSE_OPENAPI_BASE_URL = "https://openapi.twse.com.tw/v1"

TWSE_ENDPOINTS = {
    "openapi_home": "https://openapi.twse.com.tw/",
    "swagger_json": f"{TWSE_OPENAPI_BASE_URL}/swagger.json",
    "market_index": f"{TWSE_OPENAPI_BASE_URL}/exchangeReport/MI_INDEX",
    "listed_material_information": f"{TWSE_OPENAPI_BASE_URL}/opendata/t187ap04_L",
    "listed_company_profile_csv": "https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv",
    "listed_material_information_csv": "https://mopsfin.twse.com.tw/opendata/t187ap04_L.csv",
    "listed_monthly_revenue_csv": "https://mopsfin.twse.com.tw/opendata/t187ap05_L.csv",
    "mops_portal": "https://mops.twse.com.tw/mops/web/index",
    "mops_financial_portal": "https://mopsfin.twse.com.tw/",
    "twse_data_eshop": "https://eshop.twse.com.tw/",
    "twse_realtime_license": "https://www.twse.com.tw/zh/products/information/real-time.html",
    "twse_delayed_license": "https://www.twse.com.tw/zh/products/information/delayed.html",
    "twse_usage_rules": "https://www.twse.com.tw/zh/products/information/use.html",
}


class TWSEProvider(MarketDataProvider):
    """Official TWSE/MOPS provider placeholder.

    The MVP keeps live fetching disabled and uses this class as the single place
    to map legal official endpoints before scheduled ingestion is connected.
    """

    base_url = TWSE_OPENAPI_BASE_URL
    endpoints = TWSE_ENDPOINTS

    def get_instruments(self):
        return []
