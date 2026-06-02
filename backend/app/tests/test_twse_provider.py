from app.services.data_providers.twse_provider import TWSE_ENDPOINTS, TWSEProvider


def test_twse_provider_exposes_official_endpoints() -> None:
    provider = TWSEProvider()

    assert provider.base_url == "https://openapi.twse.com.tw/v1"
    assert TWSE_ENDPOINTS["swagger_json"] == "https://openapi.twse.com.tw/v1/swagger.json"
    assert TWSE_ENDPOINTS["market_index"] == "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
    assert TWSE_ENDPOINTS["listed_company_profile_csv"].endswith("t187ap03_L.csv")
    assert TWSE_ENDPOINTS["listed_monthly_revenue_csv"].endswith("t187ap05_L.csv")
