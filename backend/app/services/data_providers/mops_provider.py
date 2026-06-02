from typing import Any, Dict, List, Optional

import httpx

from app.services.data_providers.base import MarketDataProvider
from app.services.data_providers.twse_provider import TWSE_ENDPOINTS, _decode_response, parse_company_profile_csv, parse_monthly_revenue_csv

MOPS_ENDPOINTS = {
    "mops_portal": TWSE_ENDPOINTS["mops_portal"],
    "mops_financial_portal": TWSE_ENDPOINTS["mops_financial_portal"],
    "listed_company_profile_csv": TWSE_ENDPOINTS["listed_company_profile_csv"],
    "listed_material_information_csv": TWSE_ENDPOINTS["listed_material_information_csv"],
    "listed_monthly_revenue_csv": TWSE_ENDPOINTS["listed_monthly_revenue_csv"],
}


class MOPSProvider(MarketDataProvider):
    """MOPS/mopsfin provider for company profiles, revenue, and disclosures."""

    endpoints = MOPS_ENDPOINTS

    def __init__(self, client: Optional[httpx.Client] = None, timeout: float = 10.0) -> None:
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)

    def get_instruments(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["listed_company_profile_csv"])
        response.raise_for_status()
        return parse_company_profile_csv(_decode_response(response))

    def get_monthly_revenue(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["listed_monthly_revenue_csv"])
        response.raise_for_status()
        return parse_monthly_revenue_csv(_decode_response(response))

    def get_material_information(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["listed_material_information_csv"])
        response.raise_for_status()
        return parse_material_information_csv(_decode_response(response))


def parse_material_information_csv(csv_text: str) -> List[Dict[str, Any]]:
    import csv
    from io import StringIO

    rows = []
    for raw in csv.DictReader(StringIO(csv_text.lstrip("\ufeff"))):
        row = {str(key or "").strip().replace("\ufeff", ""): (value or "").strip() for key, value in raw.items()}
        stock_id = _first(row, ["公司代號", "公司代碼", "股票代號", "stock_id"])
        title = _first(row, ["主旨", "標題", "title"])
        if not stock_id and not title:
            continue
        rows.append(
            {
                "stock_id": stock_id,
                "stock_name": _first(row, ["公司名稱", "公司簡稱", "stock_name"]),
                "event_date": _first(row, ["發言日期", "公告日期", "event_date"]),
                "event_time": _first(row, ["發言時間", "公告時間", "event_time"]),
                "title": title,
                "summary": _first(row, ["說明", "符合條款", "summary"]) or title,
                "source": "MOPS listed material information CSV",
            }
        )
    return rows


def _first(row: Dict[str, str], keys: List[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value:
            return value
    return ""
