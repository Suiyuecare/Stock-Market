import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings
from app.services.data_providers.base import MarketDataProvider

ANALYST_ESTIMATES_ENDPOINTS = {
    "factset_developer": "https://developer.factset.com/",
    "factset_estimates_api": "https://developer.factset.com/api-catalog/factset-estimates-api",
    "factset_estimates_report_builder_api": "https://developer.factset.com/api-catalog/factset-estimates-report-builder-api",
    "lseg_ibes_estimates": "https://www.lseg.com/en/data-analytics/financial-data/company-data/ibes-estimates",
    "lseg_estimates_api_for_wealth": "https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/estimates-API",
    "bloomberg_bpipe": "https://professional.bloomberg.com/products/data/enterprise-catalog/real-time-data-feed/",
    "bloomberg_sapi": "https://professional.bloomberg.com/products/data/data-connectivity/server-api/",
    "bloomberg_data_license": "https://professional.bloomberg.com/products/data/data-management/data-license/",
    "bloomberg_web_api_host": "https://api.bloomberg.com",
    "fmp_price_target_consensus": "https://financialmodelingprep.com/stable/price-target-consensus",
    "fmp_analyst_estimates": "https://financialmodelingprep.com/stable/analyst-estimates",
    "fmp_ratings_historical": "https://financialmodelingprep.com/stable/ratings-historical",
}

ANALYST_ESTIMATES_FIELDS = [
    "eps_consensus",
    "revenue_consensus",
    "target_price_mean",
    "target_price_high",
    "target_price_low",
    "rating_revision",
    "estimate_revision_direction",
    "analyst_count",
    "analyst_hit_rate",
    "data_freshness",
]


class AnalystEstimatesProvider(MarketDataProvider):
    """Commercial analyst estimates provider with safe fallback extraction.

    FactSet, LSEG I/B/E/S, and Bloomberg can feed TargetPriceScore with EPS
    consensus, target prices, ratings, estimate revisions, and analyst-quality
    signals. Direct live fetching is enabled only when credentials are present.
    Without licenses, the provider can still extract target-price mentions from
    already-ingested news snippets and keep them clearly marked as extracted
    references rather than official consensus data.
    """

    endpoints = ANALYST_ESTIMATES_ENDPOINTS
    normalized_fields = ANALYST_ESTIMATES_FIELDS

    def __init__(self, client: Optional[httpx.Client] = None, timeout: float = 10.0) -> None:
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self.settings = get_settings()

    def get_instruments(self) -> List[Dict[str, Any]]:
        return []

    def get_target_price_consensus(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch consensus target prices from configured licensed/keyed APIs.

        FMP is supported as a lightweight keyed source. FactSet/LSEG/Bloomberg
        are tracked in endpoints but require customer-specific auth flows, so
        they should be implemented behind the same normalized return shape when
        credentials and redistribution rights are available.
        """

        fmp_key = self.settings.fmp_api_key or self.settings.financial_modeling_prep_api_key
        if not fmp_key:
            return None
        response = self.client.get(
            self.endpoints["fmp_price_target_consensus"],
            params={"symbol": symbol, "apikey": fmp_key},
        )
        response.raise_for_status()
        payload = response.json()
        row = payload[0] if isinstance(payload, list) and payload else payload if isinstance(payload, dict) else {}
        if not row:
            return None
        return normalize_fmp_target_price(symbol, row)

    def get_analyst_estimates(self, symbol: str) -> List[Dict[str, Any]]:
        fmp_key = self.settings.fmp_api_key or self.settings.financial_modeling_prep_api_key
        if not fmp_key:
            return []
        response = self.client.get(
            self.endpoints["fmp_analyst_estimates"],
            params={"symbol": symbol, "apikey": fmp_key},
        )
        response.raise_for_status()
        payload = response.json()
        rows = payload if isinstance(payload, list) else []
        return [{"symbol": symbol, "source": "FMP analyst estimates", **row} for row in rows]

    def extract_target_prices_from_news(self, symbol: str, news_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        extracted: List[Dict[str, Any]] = []
        for event in news_events:
            text = f"{event.get('title', '')}\n{event.get('summary', '')}"
            for target in extract_target_price_mentions(text):
                extracted.append(
                    {
                        "symbol": symbol,
                        "broker": target.get("broker"),
                        "target_price": target["target_price"],
                        "target_price_low": target.get("target_price_low"),
                        "target_price_high": target.get("target_price_high"),
                        "currency": "TWD",
                        "rating": target.get("rating"),
                        "source": event.get("source", "news"),
                        "source_type": "ai_extracted_news",
                        "source_url": event.get("url") or event.get("source_url"),
                        "published_at": event.get("published_at") or event.get("event_time") or datetime.utcnow().isoformat(),
                        "confidence": target["confidence"],
                        "note": "新聞文字抽取值，非正式法人共識資料；正式數據需接 CMoney/TEJ/FactSet/LSEG/Bloomberg 等授權來源。",
                    }
                )
        return extracted


def normalize_fmp_target_price(symbol: str, row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbol": symbol,
        "target_price_mean": _number(row.get("targetConsensus") or row.get("targetPrice")),
        "target_price_high": _number(row.get("targetHigh")),
        "target_price_low": _number(row.get("targetLow")),
        "analyst_count": _number(row.get("numberOfAnalystOpinions") or row.get("analystCount")),
        "currency": row.get("currency") or "USD",
        "source": "FMP price target consensus",
        "source_type": "licensed_or_keyed_api",
        "published_at": row.get("date") or datetime.utcnow().isoformat(),
        "confidence": 0.72,
    }


def extract_target_price_mentions(text: str) -> List[Dict[str, Any]]:
    """Extract broker target-price mentions from short licensed/news snippets."""

    broker_pattern = r"(?:摩根士丹利|高盛|花旗|麥格理|里昂|大摩|小摩|美銀|瑞銀|野村|元大|富邦|國泰|群益|凱基|統一|永豐|玉山|中信|法人|投顧|券商)"
    rating_pattern = r"(?:買進|中立|加碼|減碼|優於大盤|劣於大盤|持有|Buy|Hold|Neutral|Overweight|Underweight)"
    price_pattern = r"(?:目標價|合理價|上看|喊到|調升至|調降至)\s*(?:新台幣|台幣|NT\$|\$)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:元)?"
    range_pattern = r"(?:區間|目標區間)\s*(?:新台幣|台幣|NT\$|\$)?\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:至|-|~)\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*(?:元)?"
    mentions: List[Dict[str, Any]] = []

    for match in re.finditer(price_pattern, text, flags=re.I):
        window = text[max(0, match.start() - 30) : min(len(text), match.end() + 30)]
        broker = re.search(broker_pattern, window, flags=re.I)
        rating = re.search(rating_pattern, window, flags=re.I)
        mentions.append(
            {
                "broker": broker.group(0) if broker else None,
                "rating": rating.group(0) if rating else None,
                "target_price": _number(match.group(1)),
                "confidence": 0.58 if broker else 0.42,
            }
        )

    for match in re.finditer(range_pattern, text, flags=re.I):
        low = _number(match.group(1))
        high = _number(match.group(2))
        if low is None or high is None:
            continue
        mentions.append(
            {
                "broker": None,
                "rating": None,
                "target_price": round((low + high) / 2, 2),
                "target_price_low": min(low, high),
                "target_price_high": max(low, high),
                "confidence": 0.5,
            }
        )
    return [mention for mention in mentions if mention.get("target_price") is not None]


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
