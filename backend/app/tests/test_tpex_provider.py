from app.services.data_providers.tpex_provider import TPEX_ENDPOINTS, TPEXProvider


def test_tpex_provider_exposes_official_endpoints() -> None:
    provider = TPEXProvider()

    assert provider.base_url == "https://www.tpex.org.tw/openapi"
    assert TPEX_ENDPOINTS["openapi_home"] == "https://www.tpex.org.tw/openapi/"
    assert TPEX_ENDPOINTS["swagger_json"] == "https://www.tpex.org.tw/openapi/swagger.json"
    assert TPEX_ENDPOINTS["data_purchase"].endswith("/service/data/overview.html")
    assert TPEX_ENDPOINTS["after_market_download_system"] == "https://intd.tpex.org.tw"
