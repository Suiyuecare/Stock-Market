from app.services.data_providers.tdcc_provider import TDCC_ENDPOINTS, TDCCProvider


def test_tdcc_provider_exposes_official_endpoints() -> None:
    provider = TDCCProvider()

    assert provider.docs_url == "https://openapi.tdcc.com.tw/tdcc-opendata-api-docs"
    assert TDCC_ENDPOINTS["swagger_ui"] == "https://openapi-t.tdcc.com.tw/swagger-ui/index.html"
    assert TDCC_ENDPOINTS["legacy_opendata_home"] == "https://smart.tdcc.com.tw/opendata/"
    assert TDCC_ENDPOINTS["ownership_distribution"] == "https://smart.tdcc.com.tw/opendata/getOD.ashx?id=1-5"
