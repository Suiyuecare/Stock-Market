import os
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional
from xml.etree import ElementTree

import httpx

from app.config import get_settings
from app.services.data_providers.base import NewsDataProvider

NEWS_ENDPOINTS = {
    "cna_rss_documentation": "https://www.cna.com.tw/about/rss.aspx",
    "cna_finance_rss": "https://feeds.feedburner.com/rsscna/finance",
    "cna_technology_rss": "https://feeds.feedburner.com/rsscna/technology",
    "twse_material_information": "https://openapi.twse.com.tw/v1/opendata/t187ap04_L",
    "twse_exchange_news": "https://openapi.twse.com.tw/v1/news/newsList",
    "twse_exchange_events": "https://openapi.twse.com.tw/v1/news/eventList",
    "chinatimes_rss_documentation": "https://www.chinatimes.com/realtimenews/20150107004152-260401",
    "wantrich_stock_news": "https://wantrich.chinatimes.com/",
    "ctee_news": "https://www.ctee.com.tw/",
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
    """News provider with official open feeds plus keyed/commercial adapters.

    No-key feeds are fetched directly: TWSE/MOPS material information, TWSE
    exchange news/events, and CNA finance/technology RSS. NewsAPI and commercial
    feeds are enabled only when credentials are provided in environment
    variables. WantRich/CTEE are tracked as sources requiring a stable public
    feed or commercial authorization; the provider intentionally does not scrape
    article pages.
    """

    endpoints = NEWS_ENDPOINTS
    normalized_fields = NEWS_NORMALIZED_FIELDS
    event_types = NEWS_EVENT_TYPES

    def __init__(
        self,
        client: Optional[httpx.Client] = None,
        timeout: float = 10.0,
        extra_rss_urls: Optional[List[str]] = None,
    ) -> None:
        self.client = client or httpx.Client(timeout=timeout, follow_redirects=True)
        self.settings = get_settings()
        env_rss_urls = [url.strip() for url in os.getenv("NEWS_RSS_URLS", "").split(",") if url.strip()]
        self.extra_rss_urls = extra_rss_urls if extra_rss_urls is not None else env_rss_urls

    def get_news(self, symbol: str) -> List[Dict[str, Any]]:
        events = self.get_latest_news()
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

    def get_latest_news(self, limit: int = 60, query: str = "台股 OR 半導體 OR AI OR 法人 目標價") -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for loader in (self.get_latest_twse_news, self.get_latest_rss_news):
            try:
                events.extend(loader(limit=limit))
            except (httpx.HTTPError, ElementTree.ParseError, ValueError):
                continue
        if self.settings.newsapi_key:
            try:
                events.extend(self.get_newsapi_everything(query=query, limit=limit))
            except httpx.HTTPError:
                pass
        return dedupe_news(events)[:limit]

    def get_latest_rss_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        rss_sources = [
            ("CNA Finance RSS", self.endpoints["cna_finance_rss"]),
            ("CNA Technology RSS", self.endpoints["cna_technology_rss"]),
            *[(f"Configured RSS {index + 1}", url) for index, url in enumerate(self.extra_rss_urls)],
        ]
        for source_name, url in rss_sources:
            response = self.client.get(url)
            response.raise_for_status()
            events.extend(parse_rss_feed(response.text, source_name))
        return events[:limit]

    def get_latest_twse_news(self, limit: int = 40) -> List[Dict[str, Any]]:
        events: List[Dict[str, Any]] = []
        for endpoint_key, normalizer in (
            ("twse_material_information", normalize_twse_material_information),
            ("twse_exchange_news", normalize_twse_exchange_news),
            ("twse_exchange_events", normalize_twse_exchange_event),
        ):
            response = self.client.get(self.endpoints[endpoint_key])
            response.raise_for_status()
            payload = response.json()
            rows = payload if isinstance(payload, list) else payload.get("data", [])
            events.extend([event for row in rows if (event := normalizer(row, self.endpoints[endpoint_key])) is not None])
        return events[:limit]

    def get_newsapi_everything(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.settings.newsapi_key:
            return []
        response = self.client.get(
            self.endpoints["newsapi_everything_endpoint"],
            params={
                "apiKey": self.settings.newsapi_key,
                "q": query,
                "language": "zh",
                "sortBy": "publishedAt",
                "pageSize": min(limit, 100),
            },
        )
        response.raise_for_status()
        payload = response.json()
        return [normalize_newsapi_article(article) for article in payload.get("articles", [])][:limit]


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
        image_url = _rss_image(item, summary)
        if not title:
            continue
        sentiment = classify_sentiment(f"{title}\n{summary}")
        events.append(
            {
                "event_time": published_at.isoformat(),
                "published_at": published_at.isoformat(),
                "market": "TW",
                "stock_id": None,
                "related_symbol": None,
                "related_symbols": infer_related_symbols(f"{title}\n{summary}"),
                "related_industry": None,
                "source": source,
                "title": title,
                "summary": _strip_cdata(summary),
                "url": url,
                "image_url": image_url,
                "sentiment_score": sentiment["score"],
                "sentiment": sentiment["label"],
                "event_type": infer_event_type(f"{title}\n{summary}"),
                "impact_score": sentiment["impact"],
                "confidence": 0.55,
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


def _rss_image(item: ElementTree.Element, summary: str) -> Optional[str]:
    for node in item.iter():
        tag = str(node.tag).lower()
        if tag.endswith("content") or tag.endswith("thumbnail") or tag.endswith("enclosure"):
            candidate = node.attrib.get("url")
            if candidate and candidate.startswith("http"):
                return candidate
    match = re.search(r"<img[^>]+src=[\"']([^\"']+)[\"']", summary, flags=re.I)
    if match and match.group(1).startswith("http"):
        return match.group(1)
    return None


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
    cleaned = value.replace("<![CDATA[", "").replace("]]>", "").strip()
    return re.sub(r"<[^>]+>", "", cleaned).strip()


def normalize_twse_material_information(row: Dict[str, Any], source_url: str) -> Optional[Dict[str, Any]]:
    stock_id = str(row.get("公司代號") or row.get("公司代碼") or "").strip()
    company_name = str(row.get("公司名稱") or row.get("公司簡稱") or stock_id).strip()
    title = str(row.get("主旨 ") or row.get("主旨") or row.get("title") or "").strip()
    if not stock_id or not title:
        return None
    summary = str(row.get("說明") or row.get("符合條款") or title).strip()
    event_time = _twse_datetime(row.get("發言日期"), row.get("發言時間"))
    sentiment = classify_sentiment(f"{title}\n{summary}")
    return {
        "event_time": event_time,
        "published_at": event_time,
        "market": "TW",
        "stock_id": stock_id,
        "related_symbol": stock_id,
        "related_symbols": [stock_id],
        "related_industry": None,
        "source": "TWSE/MOPS material information",
        "source_url": source_url,
        "title": f"{company_name}：{title}",
        "summary": summary,
        "url": source_url,
        "sentiment_score": sentiment["score"],
        "sentiment": sentiment["label"],
        "event_type": infer_event_type(f"{title}\n{summary}"),
        "impact_score": sentiment["impact"],
        "confidence": 0.82,
    }


def normalize_twse_exchange_news(row: Dict[str, Any], source_url: str) -> Optional[Dict[str, Any]]:
    title = str(row.get("Title") or row.get("title") or "").strip()
    if not title:
        return None
    sentiment = classify_sentiment(title)
    event_time = _parse_twse_date(str(row.get("Date") or ""))
    return {
        "event_time": event_time,
        "published_at": event_time,
        "market": "TW",
        "stock_id": None,
        "related_symbol": None,
        "related_symbols": infer_related_symbols(title),
        "related_industry": None,
        "source": "TWSE exchange news",
        "source_url": source_url,
        "title": title,
        "summary": title,
        "url": str(row.get("Url") or "").strip() or source_url,
        "sentiment_score": sentiment["score"],
        "sentiment": sentiment["label"],
        "event_type": infer_event_type(title),
        "impact_score": sentiment["impact"],
        "confidence": 0.68,
    }


def normalize_twse_exchange_event(row: Dict[str, Any], source_url: str) -> Optional[Dict[str, Any]]:
    title = str(row.get("Title") or row.get("title") or "").strip()
    if not title:
        return None
    return {
        "event_time": datetime.utcnow().isoformat(),
        "published_at": datetime.utcnow().isoformat(),
        "market": "TW",
        "stock_id": None,
        "related_symbol": None,
        "related_symbols": infer_related_symbols(title),
        "related_industry": None,
        "source": "TWSE exchange events",
        "source_url": source_url,
        "title": title,
        "summary": title,
        "url": str(row.get("Details") or row.get("Url") or "").strip() or source_url,
        "sentiment_score": 0,
        "sentiment": "neutral",
        "event_type": "market_event",
        "impact_score": 0.02,
        "confidence": 0.58,
    }


def normalize_newsapi_article(article: Dict[str, Any]) -> Dict[str, Any]:
    title = str(article.get("title") or "").strip()
    summary = str(article.get("description") or article.get("content") or title).strip()
    published_at = str(article.get("publishedAt") or datetime.utcnow().isoformat())
    sentiment = classify_sentiment(f"{title}\n{summary}")
    return {
        "event_time": published_at,
        "published_at": published_at,
        "market": "TW",
        "stock_id": None,
        "related_symbol": None,
        "related_symbols": infer_related_symbols(f"{title}\n{summary}"),
        "related_industry": None,
        "source": str((article.get("source") or {}).get("name") or "NewsAPI"),
        "title": title,
        "summary": summary,
        "url": str(article.get("url") or ""),
        "image_url": str(article.get("urlToImage") or "") or None,
        "sentiment_score": sentiment["score"],
        "sentiment": sentiment["label"],
        "event_type": infer_event_type(f"{title}\n{summary}"),
        "impact_score": sentiment["impact"],
        "confidence": 0.62,
    }


def dedupe_news(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []
    for event in events:
        key = event.get("url") or f"{event.get('title')}-{event.get('source')}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)
    return sorted(deduped, key=lambda event: str(event.get("published_at") or event.get("event_time") or ""), reverse=True)


def classify_sentiment(text: str) -> Dict[str, Any]:
    content = text.lower()
    positive_words = ["漲價", "上漲", "成長", "創高", "上修", "利多", "買超", "看好", "擴產", "得標", "獲利", "ai", "輝達", "配息"]
    negative_words = ["下跌", "降價", "下修", "利空", "衰退", "虧損", "賣超", "裁罰", "訴訟", "停工", "違約", "資安", "風險"]
    positive_hits = sum(1 for word in positive_words if word.lower() in content)
    negative_hits = sum(1 for word in negative_words if word.lower() in content)
    if positive_hits > negative_hits:
        impact = min(0.45, 0.08 + positive_hits * 0.05)
        return {"label": "positive", "score": round(impact, 3), "impact": impact}
    if negative_hits > positive_hits:
        impact = max(-0.45, -0.08 - negative_hits * 0.06)
        return {"label": "cautious", "score": round(impact, 3), "impact": impact}
    return {"label": "neutral", "score": 0, "impact": 0.02}


def infer_event_type(text: str) -> str:
    if re.search(r"營收|月營收|revenue", text, flags=re.I):
        return "revenue"
    if re.search(r"法說|展望|guidance|目標價", text, flags=re.I):
        return "guidance"
    if re.search(r"股利|配息|除權|除息", text):
        return "dividend"
    if re.search(r"資安|裁罰|訴訟|違約|風險", text):
        return "risk"
    if re.search(r"AI|輝達|NVIDIA|晶片|半導體|供應鏈", text, flags=re.I):
        return "supply_chain"
    return "industry"


def infer_related_symbols(text: str) -> List[str]:
    mapping = {
        "台積電": "2330",
        "聯電": "2303",
        "聯發科": "2454",
        "鴻海": "2317",
        "廣達": "2382",
        "緯創": "3231",
        "緯穎": "6669",
        "台達電": "2308",
        "智邦": "2345",
        "華碩": "2357",
        "南亞科": "2408",
        "智原": "3035",
        "欣興": "3037",
        "聯詠": "3034",
        "世芯": "3661",
        "日月光": "3711",
        "輝達": "NVDA",
        "NVIDIA": "NVDA",
        "超微": "AMD",
        "AMD": "AMD",
        "蘋果": "AAPL",
        "Apple": "AAPL",
        "博通": "AVGO",
        "美光": "MU",
    }
    return list({symbol for keyword, symbol in mapping.items() if keyword in text})


def _twse_datetime(date_value: Any, time_value: Any) -> str:
    date = _parse_twse_date(str(date_value or ""))
    digits = re.sub(r"\D", "", str(time_value or "")).zfill(6)[-6:]
    if "T" in date:
        return date
    return f"{date}T{digits[:2]}:{digits[2:4]}:{digits[4:6]}+08:00"


def _parse_twse_date(value: str) -> str:
    normalized = value.strip()
    if re.fullmatch(r"\d{7}", normalized):
        year = int(normalized[:3]) + 1911
        return f"{year}-{normalized[3:5]}-{normalized[5:7]}"
    return datetime.utcnow().date().isoformat()
