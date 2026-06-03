from typing import Any, Dict, List, Optional

import httpx

from app.services.data_providers.base import MarketDataProvider

TPEX_OPENAPI_BASE_URL = "https://www.tpex.org.tw/openapi"

TPEX_ENDPOINTS = {
    "openapi_home": "https://www.tpex.org.tw/openapi/",
    "swagger_json": f"{TPEX_OPENAPI_BASE_URL}/swagger.json",
    "mainboard_daily_close_quotes": f"{TPEX_OPENAPI_BASE_URL}/v1/tpex_mainboard_daily_close_quotes",
    "mainboard_peratio_analysis": f"{TPEX_OPENAPI_BASE_URL}/v1/tpex_mainboard_peratio_analysis",
    "data_purchase": "https://www.tpex.org.tw/zh-tw/service/data/overview.html",
    "delayed_trading_license": "https://www.tpex.org.tw/zh-tw/service/data/product/delay.html",
    "after_market_download_system": "https://intd.tpex.org.tw",
}


class TPEXProvider(MarketDataProvider):
    """Official TPEx provider for public OTC open-data endpoints.

    These endpoints are official public OpenAPI feeds. The provider normalizes
    the high-value MVP datasets now and keeps a generic catalog fetcher for
    adding more TPEx datasets without changing the ingestion plumbing.
    """

    base_url = TPEX_OPENAPI_BASE_URL
    endpoints = TPEX_ENDPOINTS

    def __init__(self, client: Optional[httpx.Client] = None, timeout: float = 10.0) -> None:
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)

    def get_instruments(self) -> List[Dict[str, Any]]:
        quotes = self.get_mainboard_daily_close_quotes()
        return [
            {
                "symbol": row["symbol"],
                "stock_id": row["symbol"],
                "name": row["name"],
                "stock_name": row["name"],
                "market": "TPEX",
                "market_type": "TPEX",
                "sector": "上櫃",
                "industry": "上櫃",
                "currency": "TWD",
                "is_listed": False,
                "is_otc": True,
                "source": "TPEx OpenAPI daily close quotes",
            }
            for row in quotes
        ]

    def get_mainboard_daily_close_quotes(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["mainboard_daily_close_quotes"])
        response.raise_for_status()
        payload = response.json()
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return [normalize_tpex_quote(row) for row in rows if normalize_tpex_quote(row)]

    def get_mainboard_peratio_analysis(self) -> List[Dict[str, Any]]:
        response = self.client.get(self.endpoints["mainboard_peratio_analysis"])
        response.raise_for_status()
        payload = response.json()
        rows = payload if isinstance(payload, list) else payload.get("data", [])
        return [normalize_tpex_valuation(row) for row in rows if normalize_tpex_valuation(row)]

    def fetch_openapi_swagger_json(self) -> Dict[str, Any]:
        response = self.client.get(self.endpoints["swagger_json"])
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    def list_openapi_endpoints(self) -> List[Dict[str, Any]]:
        swagger = self.fetch_openapi_swagger_json()
        endpoints: List[Dict[str, Any]] = []
        for path, methods in swagger.get("paths", {}).items():
            if not isinstance(methods, dict):
                continue
            get_spec = methods.get("get") or {}
            endpoints.append(
                {
                    "id": path.strip("/").replace("/", "_"),
                    "path": path,
                    "url": f"{self.base_url}{path}" if path.startswith("/") else f"{self.base_url}/{path}",
                    "summary": get_spec.get("summary") or get_spec.get("description") or "",
                    "tags": get_spec.get("tags", []),
                }
            )
        return endpoints

    def fetch_openapi_endpoint(self, path_or_url: str) -> Any:
        endpoint = path_or_url if path_or_url.startswith("http") else f"{self.base_url}/{path_or_url.lstrip('/')}"
        response = self.client.get(endpoint, headers={"Accept": "application/json"})
        response.raise_for_status()
        return response.json()


def normalize_tpex_quote(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    symbol = str(row.get("SecuritiesCompanyCode") or row.get("Code") or "").strip()
    if not symbol.isdigit():
        return None
    return {
        "date": str(row.get("Date") or "").strip(),
        "symbol": symbol,
        "name": str(row.get("CompanyName") or row.get("Name") or symbol).strip(),
        "open": _number(row.get("Open")),
        "high": _number(row.get("High")),
        "low": _number(row.get("Low")),
        "close": _number(row.get("Close")),
        "change": _number(row.get("Change")),
        "trade_volume": _number(row.get("TradingShares")),
        "trade_value": _number(row.get("TransactionAmount")),
        "transaction_count": _number(row.get("TransactionNumber")),
        "source": "TPEx OpenAPI",
    }


def normalize_tpex_valuation(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    symbol = str(row.get("SecuritiesCompanyCode") or row.get("Code") or "").strip()
    if not symbol.isdigit():
        return None
    return {
        "date": str(row.get("Date") or "").strip(),
        "symbol": symbol,
        "name": str(row.get("CompanyName") or row.get("Name") or symbol).strip(),
        "pe_ratio": _number(row.get("PriceEarningRatio")),
        "dividend_yield": _number(row.get("YieldRatio")),
        "pb_ratio": _number(row.get("PriceBookRatio")),
        "dividend_per_share": _number(row.get("DividendPerShare")),
        "source": "TPEx OpenAPI",
    }


def _number(value: Any) -> Optional[float]:
    if value is None:
        return None
    normalized = str(value).replace(",", "").replace("%", "").strip()
    if not normalized or normalized in {"-", "--", "N/A"}:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None
