from app.services.data_providers.base import MarketDataProvider

TDCC_OPENAPI_DOCS_URL = "https://openapi.tdcc.com.tw/tdcc-opendata-api-docs"

TDCC_ENDPOINTS = {
    "swagger_ui": "https://openapi-t.tdcc.com.tw/swagger-ui/index.html",
    "opendata_api_docs": TDCC_OPENAPI_DOCS_URL,
    "legacy_opendata_home": "https://smart.tdcc.com.tw/opendata/",
    "ownership_distribution": "https://smart.tdcc.com.tw/opendata/getOD.ashx?id=1-5",
}


class TDCCProvider(MarketDataProvider):
    """Official TDCC provider placeholder.

    TDCC OpenData is intended for ownership distribution, depository inventory,
    holding brackets, large-holder ratios, ownership concentration, and chip
    concentration risk factors. Live fetching remains disabled until endpoint
    field mappings and usage terms are implemented.
    """

    docs_url = TDCC_OPENAPI_DOCS_URL
    endpoints = TDCC_ENDPOINTS

    def get_instruments(self):
        return []
