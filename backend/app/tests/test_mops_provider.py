import httpx

from app.services.data_providers.mops_provider import MOPS_ENDPOINTS, MOPSProvider, parse_material_information_csv


def test_mops_provider_parses_material_information_csv() -> None:
    csv_text = "公司代號,公司名稱,發言日期,發言時間,主旨,說明\n2330,台積電,20260603,150000,公告董事會重要決議,擴充產能\n"

    rows = parse_material_information_csv(csv_text)

    assert rows[0]["stock_id"] == "2330"
    assert rows[0]["stock_name"] == "台積電"
    assert rows[0]["event_date"] == "20260603"
    assert rows[0]["title"] == "公告董事會重要決議"
    assert rows[0]["summary"] == "擴充產能"
    assert rows[0]["source"] == "MOPS listed material information CSV"


def test_mops_provider_fetches_monthly_revenue_with_injected_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == MOPS_ENDPOINTS["listed_monthly_revenue_csv"]
        return httpx.Response(
            200,
            text="公司代號,公司名稱,資料年月,當月營收,上月比較增減(%),去年同月增減(%),前期比較增減(%)\n2330,台積電,202605,\"280,000\",3.2,18.5,24.1\n",
        )

    provider = MOPSProvider(client=httpx.Client(transport=httpx.MockTransport(handler)))

    rows = provider.get_monthly_revenue()

    assert rows[0]["stock_id"] == "2330"
    assert str(rows[0]["revenue"]) == "280000"
