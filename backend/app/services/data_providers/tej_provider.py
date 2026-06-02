from app.services.data_providers.base import MarketDataProvider

TEJ_REST_BASE_URL = "https://api.tej.com.tw/api"

TEJ_ENDPOINTS = {
    "official_portal": "https://api.tej.com.tw/",
    "api_documentation": "https://www.tejwin.com/en/insight/tej-api-document/",
    "rest_api_documentation": "https://www.tejwin.com/en/insight/tej-rest-api-document/",
    "taiwan_stock_data_solution": "https://www.tejwin.com/en/solution/taiwan-stock-data/",
    "rest_base_url": f"{TEJ_REST_BASE_URL}/",
}

TEJ_DATASET_EXAMPLES = {
    "taiwan_adjusted_price_daily": "TWN/APRCD",
}


class TEJProvider(MarketDataProvider):
    """Commercial TEJ provider placeholder.

    TEJ can enrich the MVP with licensed Taiwan market, financial, fundamental,
    corporate action, event, and historical datasets. Live fetching remains
    disabled until a valid commercial license, API key, and dataset mapping are
    configured outside the repository.
    """

    rest_base_url = TEJ_REST_BASE_URL
    endpoints = TEJ_ENDPOINTS
    dataset_examples = TEJ_DATASET_EXAMPLES

    def get_instruments(self):
        return []
