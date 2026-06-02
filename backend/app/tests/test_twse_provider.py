import pytest
import httpx

from app.services.data_providers.twse_provider import (
    TWSE_ENDPOINTS,
    TWSEProvider,
    get_twse_openapi_endpoint,
    list_twse_openapi_endpoints,
    load_twse_openapi_catalog,
    parse_company_profile_csv,
    parse_monthly_revenue_csv,
)


def test_twse_provider_exposes_official_endpoints() -> None:
    provider = TWSEProvider()

    assert provider.base_url == "https://openapi.twse.com.tw/v1"
    assert TWSE_ENDPOINTS["swagger_json"] == "https://openapi.twse.com.tw/v1/swagger.json"
    assert TWSE_ENDPOINTS["market_index"] == "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
    assert TWSE_ENDPOINTS["listed_company_profile_csv"].endswith("t187ap03_L.csv")
    assert TWSE_ENDPOINTS["listed_monthly_revenue_csv"].endswith("t187ap05_L.csv")


def test_twse_openapi_catalog_contains_official_swagger_paths() -> None:
    catalog = load_twse_openapi_catalog()

    assert catalog["swagger_url"] == "https://openapi.twse.com.tw/v1/swagger.json"
    assert catalog["base_url"] == "https://openapi.twse.com.tw/v1"
    assert catalog["endpoint_count"] == 143
    assert len(catalog["endpoints"]) == catalog["endpoint_count"]

    market_index = get_twse_openapi_endpoint("/exchangeReport/MI_INDEX")
    assert market_index is not None
    assert market_index["url"] == "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
    assert market_index["method"] == "GET"
    assert market_index["tags"] == ["證券交易"]
    assert {field["name"] for field in market_index["response_fields"]} >= {"日期", "指數", "收盤指數"}

    material_news = get_twse_openapi_endpoint("opendata_t187ap04_l")
    assert material_news is not None
    assert material_news["path"] == "/opendata/t187ap04_L"
    assert {field["name"] for field in material_news["response_fields"]} >= {"公司代號", "公司名稱", "說明"}


def test_twse_openapi_catalog_can_filter_by_tag() -> None:
    financial_endpoints = list_twse_openapi_endpoints(tag="財務報表")

    assert len(financial_endpoints) == 30
    assert any(endpoint["path"] == "/opendata/t187ap05_L" for endpoint in financial_endpoints)
    assert all("財務報表" in endpoint["tags"] for endpoint in financial_endpoints)


def test_twse_provider_fetches_any_cataloged_openapi_endpoint_with_injected_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
        assert request.headers["Accept"] == "application/json"
        return httpx.Response(200, json=[{"日期": "20260602", "指數": "發行量加權股價指數", "收盤指數": "22000.00"}])

    provider = TWSEProvider(client=httpx.Client(transport=httpx.MockTransport(handler)))

    rows = provider.fetch_openapi_endpoint("/exchangeReport/MI_INDEX")

    assert rows == [{"日期": "20260602", "指數": "發行量加權股價指數", "收盤指數": "22000.00"}]


def test_twse_provider_rejects_unknown_openapi_endpoint() -> None:
    provider = TWSEProvider(client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(404))))

    with pytest.raises(ValueError, match="Unknown TWSE OpenAPI endpoint"):
        provider.fetch_openapi_endpoint("/not/a/twse/path")


def test_twse_provider_parses_listed_company_profile_csv() -> None:
    csv_text = "公司代號,公司名稱,產業別\n2330,台積電,半導體\n2317,鴻海,電子代工\n"

    rows = parse_company_profile_csv(csv_text)

    assert rows[0]["stock_id"] == "2330"
    assert rows[0]["stock_name"] == "台積電"
    assert rows[0]["market_type"] == "TWSE"
    assert rows[0]["industry"] == "半導體"
    assert rows[0]["is_listed"] is True


def test_twse_provider_parses_monthly_revenue_csv() -> None:
    csv_text = "公司代號,公司名稱,資料年月,當月營收,上月比較增減(%),去年同月增減(%),前期比較增減(%)\n2330,台積電,202605,\"280,000,000\",3.2,18.5,24.1\n"

    rows = parse_monthly_revenue_csv(csv_text)

    assert rows[0]["stock_id"] == "2330"
    assert rows[0]["data_month"] == "202605"
    assert str(rows[0]["revenue"]) == "280000000"
    assert str(rows[0]["revenue_yoy"]) == "18.5"


def test_twse_provider_fetches_official_csv_with_injected_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == TWSE_ENDPOINTS["listed_company_profile_csv"]
        return httpx.Response(200, text="公司代號,公司名稱,產業別\n2330,台積電,半導體\n")

    provider = TWSEProvider(client=httpx.Client(transport=httpx.MockTransport(handler)))

    rows = provider.get_instruments()

    assert rows == [
        {
            "symbol": "2330",
            "stock_id": "2330",
            "name": "台積電",
            "stock_name": "台積電",
            "market": "TW",
            "market_type": "TWSE",
            "sector": "半導體",
            "industry": "半導體",
            "currency": "TWD",
            "is_listed": True,
            "is_otc": False,
            "source": "MOPS listed company profile CSV",
        }
    ]
