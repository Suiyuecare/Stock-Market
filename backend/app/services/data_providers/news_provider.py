from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import httpx

from app.services.data_providers.base import NewsDataProvider

NEWS_ENDPOINTS = {
    "cna_rss_documentation": "https://www.cna.com.tw/about/rss.aspx",
    "cna_finance_rss": "https://feeds.feedburner.com/rsscna/finance",
    "cna_technology_rss": "https://feeds.feedburner.com/rsscna/technology",
    "cnyes_openapi_documentation": "https://openapi.api.cnyes.com/swagger-ui.html",
    "cnyes_openapi_base": "https://openapi.api.cnyes.com/",
    "newsapi_documentation": "https://newsapi.org/docs",
    "newsapi_rest_base": "https://newsapi.org/v2",
    "newsapi_everything_endpoint": "https://newsapi.org/v2/everything",
    "reuters_api_integrations": "https://reutersagency.com/content-delivery-platforms/api-integrations/",
    "lseg_news_api": "https://developers.lseg.com/en/api-catalog/refinitiv-data-platform/news-API",
    "thomson_reuters_developer_portal": "https://developers.thomsonreuters.com/",
    "newsdata_io_documentation": "https://newsdata.io/documentation",
    "thenewsapi_documentation": "https://www.thenewsapi.com/documentation",
}

NEWS_NORMALIZED_FIELDS = [
    "event_time",
    "market",
    "stock_id",
    "related_symbol",
    "related_industry",
    "source",
    "title",
    "summary",
    "url",
    "sentiment_score",
    "event_type",
    "impact_score",
    "confidence",
]

NEWS_EVENT_TYPES = [
    "earnings",
    "revenue",
    "guidance",
    "material_information",
    "industry",
    "supply_chain",
    "macro",
    "regulatory",
    "geopolitical",
    "risk",
]


class NewsProvider(NewsDataProvider):
    """News provider with CNA RSS support and licensed-source endpoint registry.

    CNA RSS can seed MVP news events when terms allow. Cnyes, NewsAPI,
    Reuters/LSEG, NewsData.io, and TheNewsAPI remain disabled until API keys,
    commercial rights, and redistribution/display rules are configured outside
    this repository.
    """

    endpoints = NEWS_ENDPOINTS
    normalized_fields = NEWS_NORMALIZED_FIELDS
    event_types = NEWS_EVENT_TYPES

    def __init__(self, client: Optional[httpx.Client] = None, timeout: float = 10.0) -> None:
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)

    def get_news(self, symbol: str) -> List[Dict[str, Any]]:
        events = self.get_latest_rss_news()
        if not symbol:
            return events
        normalized = symbol.upper()
        return [
            event
            for event in events
            if normalized in event["title"].upper()
            or normalized in event["summary"].upper()
            or normalized in [item.upper() for item in event.get("related_symbols", [])]
        ]

    def get_latest_rss_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for source_name, endpoint_key in (("CNA Finance RSS", "cna_finance_rss"), ("CNA Technology RSS", "cna_technology_rss")):
            response = self.client.get(self.endpoints[endpoint_key])
            response.raise_for_status()
            events.extend(parse_rss_feed(response.text, source_name))
        return events[:limit]


def parse_rss_feed(xml_text: str, source: str) -> List[Dict[str, Any]]:
    root = ElementTree.fromstring(xml_text)
    items = root.findall("./channel/item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    events = []
    for item in items:
        title = _text(item, "title")
        summary = _text(item, "description") or _text(item, "summary") or title
        url = _text(item, "link") or _atom_link(item)
        published_raw = _text(item, "pubDate") or _text(item, "published") or _text(item, "updated")
        published_at = _parse_datetime(published_raw)
        if not title:
            continue
        events.append(
            {
                "event_time": published_at.isoformat(),
                "market": "TW",
                "stock_id": None,
                "related_symbol": None,
                "related_symbols": [],
                "related_industry": None,
                "source": source,
                "title": title,
                "summary": _strip_cdata(summary),
                "url": url,
                "sentiment_score": 0,
                "event_type": "industry",
                "impact_score": 0,
                "confidence": 0.5,
            }
        )
    return events


def _text(item: ElementTree.Element, tag: str) -> str:
    node = item.find(tag)
    if node is None:
        node = item.find(f"{{http://www.w3.org/2005/Atom}}{tag}")
    return (node.text or "").strip() if node is not None else ""


def _atom_link(item: ElementTree.Element) -> str:
    link = item.find("{http://www.w3.org/2005/Atom}link")
    if link is None:
        return ""
    return link.attrib.get("href", "")


def _parse_datetime(value: str) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime.utcnow()


def _strip_cdata(value: str) -> str:
    return value.replace("<![CDATA[", "").replace("]]>", "").strip()
