from app.services.data_providers.taifex_provider import TAIFEX_ENDPOINTS, TAIFEXProvider


def test_taifex_provider_exposes_official_endpoints() -> None:
    provider = TAIFEXProvider()

    assert provider.base_url == "https://openapi.taifex.com.tw"
    assert TAIFEX_ENDPOINTS["openapi_home"] == "https://openapi.taifex.com.tw/"
    assert TAIFEX_ENDPOINTS["swagger_json"] == "https://openapi.taifex.com.tw/swagger.json"
    assert TAIFEX_ENDPOINTS["official_portal"] == "https://www.taifex.com.tw/"
