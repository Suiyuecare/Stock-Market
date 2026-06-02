import httpx

from app.services.data_providers.twse_provider import TWSE_ENDPOINTS, TWSEProvider, parse_company_profile_csv, parse_monthly_revenue_csv


def test_twse_provider_exposes_official_endpoints() -> None:
    provider = TWSEProvider()

    assert provider.base_url == "https://openapi.twse.com.tw/v1"
    assert TWSE_ENDPOINTS["swagger_json"] == "https://openapi.twse.com.tw/v1/swagger.json"
    assert TWSE_ENDPOINTS["market_index"] == "https://openapi.twse.com.tw/v1/exchangeReport/MI_INDEX"
    assert TWSE_ENDPOINTS["listed_company_profile_csv"].endswith("t187ap03_L.csv")
    assert TWSE_ENDPOINTS["listed_monthly_revenue_csv"].endswith("t187ap05_L.csv")


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
