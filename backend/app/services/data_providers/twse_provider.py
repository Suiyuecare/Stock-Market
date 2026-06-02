import csv
import json
from decimal import Decimal, InvalidOperation
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.services.data_providers.base import MarketDataProvider

TWSE_OPENAPI_BASE_URL = "https://openapi.twse.com.tw/v1"
TWSE_OPENAPI_CATALOG_FILE = Path(__file__).with_name("twse_openapi_catalog.json")

TWSE_ENDPOINTS = {
    "openapi_home": "https://openapi.twse.com.tw/",
    "swagger_json": f"{TWSE_OPENAPI_BASE_URL}/swagger.json",
    "market_index": f"{TWSE_OPENAPI_BASE_URL}/exchangeReport/MI_INDEX",
    "listed_material_information": f"{TWSE_OPENAPI_BASE_URL}/opendata/t187ap04_L",
    "listed_company_profile_csv": "https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv",
    "listed_material_information_csv": "https://mopsfin.twse.com.tw/opendata/t187ap04_L.csv",
    "listed_monthly_revenue_csv": "https://mopsfin.twse.com.tw/opendata/t187ap05_L.csv",
    "mops_portal": "https://mops.twse.com.tw/mops/web/index",
    "mops_financial_portal": "https://mopsfin.twse.com.tw/",
    "twse_data_eshop": "https://eshop.twse.com.tw/",
    "twse_realtime_license": "https://www.twse.com.tw/zh/products/information/real-time.html",
    "twse_delayed_license": "https://www.twse.com.tw/zh/products/information/delayed.html",
    "twse_usage_rules": "https://www.twse.com.tw/zh/products/information/use.html",
}


def load_twse_openapi_catalog() -> Dict[str, Any]:
    """Load the static catalog generated from TWSE's official Swagger JSON."""

    return json.loads(TWSE_OPENAPI_CATALOG_FILE.read_text(encoding="utf-8"))


def list_twse_openapi_endpoints(tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return all documented TWSE OpenAPI endpoints, optionally filtered by tag."""

    endpoints = load_twse_openapi_catalog().get("endpoints", [])
    if tag is None:
        return list(endpoints)
    return [endpoint for endpoint in endpoints if tag in endpoint.get("tags", [])]


def get_twse_openapi_endpoint(path_or_id: str) -> Optional[Dict[str, Any]]:
    """Find a TWSE endpoint by full path, generated id, or absolute URL."""

    normalized = path_or_id.strip()
    for endpoint in list_twse_openapi_endpoints():
        if normalized in {endpoint.get("id"), endpoint.get("path"), endpoint.get("url")}:
            return endpoint
    return None


class TWSEProvider(MarketDataProvider):
    """Official TWSE/MOPS provider with normalized open-data fetch helpers."""

    base_url = TWSE_OPENAPI_BASE_URL
    endpoints = TWSE_ENDPOINTS

    def __init__(self, client: Optional[httpx.Client] = None, timeout: float = 10.0) -> None:
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)

    def get_instruments(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["listed_company_profile_csv"])
        response.raise_for_status()
        return parse_company_profile_csv(_decode_response(response))

    def get_market_index(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["market_index"])
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            return payload.get("data", [])
        return []

    def get_listed_material_information(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["listed_material_information"])
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, list) else []

    def get_monthly_revenue(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["listed_monthly_revenue_csv"])
        response.raise_for_status()
        return parse_monthly_revenue_csv(_decode_response(response))

    def list_openapi_endpoints(self, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        return list_twse_openapi_endpoints(tag=tag)

    def get_openapi_endpoint(self, path_or_id: str) -> Optional[Dict[str, Any]]:
        return get_twse_openapi_endpoint(path_or_id)

    def fetch_openapi_endpoint(self, path_or_id: str, accept: str = "application/json") -> Any:
        """Fetch any cataloged TWSE OpenAPI endpoint.

        This generic helper is intended for ingestion experiments and mapping
        work. Production jobs should still normalize each dataset into explicit
        application tables and record data-availability timestamps.
        """

        endpoint = self.get_openapi_endpoint(path_or_id)
        if endpoint is None:
            raise ValueError(f"Unknown TWSE OpenAPI endpoint: {path_or_id}")
        response = self.client.get(endpoint["url"], headers={"Accept": accept})
        response.raise_for_status()
        if "json" in accept:
            return response.json()
        return _decode_response(response)

    def fetch_openapi_swagger_json(self) -> Dict[str, Any]:
        response = self.client.get(self.endpoints["swagger_json"])
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}


def parse_company_profile_csv(csv_text: str) -> List[Dict[str, Any]]:
    rows = []
    for raw in _dict_rows(csv_text):
        stock_id = _first(raw, ["公司代號", "公司代碼", "股票代號", "stock_id"])
        if not stock_id:
            continue
        rows.append(
            {
                "symbol": stock_id.strip(),
                "stock_id": stock_id.strip(),
                "name": _first(raw, ["公司名稱", "公司簡稱", "stock_name", "name"]).strip(),
                "stock_name": _first(raw, ["公司名稱", "公司簡稱", "stock_name", "name"]).strip(),
                "market": "TW",
                "market_type": "TWSE",
                "sector": _first(raw, ["產業別", "產業類別", "industry"]).strip() or None,
                "industry": _first(raw, ["產業別", "產業類別", "industry"]).strip() or None,
                "currency": "TWD",
                "is_listed": True,
                "is_otc": False,
                "source": "MOPS listed company profile CSV",
            }
        )
    return rows


def parse_monthly_revenue_csv(csv_text: str) -> List[Dict[str, Any]]:
    rows = []
    for raw in _dict_rows(csv_text):
        stock_id = _first(raw, ["公司代號", "公司代碼", "股票代號", "stock_id"])
        if not stock_id:
            continue
        rows.append(
            {
                "stock_id": stock_id.strip(),
                "stock_name": _first(raw, ["公司名稱", "公司簡稱", "stock_name"]).strip(),
                "data_month": _first(raw, ["資料年月", "出表日期", "data_month"]).strip(),
                "revenue": _decimal(_first(raw, ["當月營收", "營業收入-當月營收", "revenue"])),
                "revenue_mom": _decimal(_first(raw, ["上月比較增減(%)", "上月比較增減％", "revenue_mom"])),
                "revenue_yoy": _decimal(_first(raw, ["去年同月增減(%)", "去年同月增減％", "revenue_yoy"])),
                "revenue_acc_yoy": _decimal(_first(raw, ["前期比較增減(%)", "前期比較增減％", "revenue_acc_yoy"])),
                "source": "MOPS listed monthly revenue CSV",
            }
        )
    return rows


def _dict_rows(csv_text: str) -> List[Dict[str, str]]:
    cleaned = csv_text.lstrip("\ufeff")
    return [{_clean_key(key): (value or "").strip() for key, value in row.items()} for row in csv.DictReader(StringIO(cleaned))]


def _clean_key(value: Optional[str]) -> str:
    return (value or "").strip().replace("\ufeff", "")


def _first(row: Dict[str, str], keys: List[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value:
            return value
    return ""


def _decimal(value: str) -> Optional[Decimal]:
    normalized = value.replace(",", "").replace("%", "").strip()
    if not normalized or normalized in {"-", "--", "N/A"}:
        return None
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def _decode_response(response: httpx.Response) -> str:
    content = response.content
    for encoding in ("utf-8-sig", "utf-8", "big5", "cp950"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return response.text
