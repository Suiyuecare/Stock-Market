from datetime import datetime, timedelta
from typing import Dict, List


TW_INSTRUMENTS = [
    {"symbol": "2330", "market": "TW", "name": "台積電", "sector": "半導體", "currency": "TWD", "supply_chain_tags": ["semiconductor", "foundry", "AI", "TSM_ADR"]},
    {"symbol": "2454", "market": "TW", "name": "聯發科", "sector": "半導體", "currency": "TWD", "supply_chain_tags": ["semiconductor", "IC design", "edge-ai"]},
    {"symbol": "2317", "market": "TW", "name": "鴻海", "sector": "電子代工", "currency": "TWD", "supply_chain_tags": ["AI-server", "Apple", "EMS"]},
    {"symbol": "2308", "market": "TW", "name": "台達電", "sector": "電源管理", "currency": "TWD", "supply_chain_tags": ["AI-server", "energy", "power"]},
]

US_LINKAGE_SYMBOLS = [
    "NASDAQ",
    "SOX",
    "S&P500",
    "QQQ",
    "SMH",
    "VIX",
    "TSM_ADR",
    "TSM_ADR_PREMIUM",
    "NVDA",
    "AMD",
    "AAPL",
    "AVGO",
    "MU",
    "MSFT",
    "META",
    "GOOGL",
    "AMZN",
]


def get_mock_price_series(symbol: str, days: int = 80) -> Dict[str, List[float]]:
    seed = sum(ord(char) for char in symbol)
    base = 80 + (seed % 500)
    highs: List[float] = []
    lows: List[float] = []
    closes: List[float] = []
    volumes: List[float] = []

    for index in range(days):
        drift = (index * (seed % 7 + 1)) * 0.13
        cycle = ((index % 9) - 4) * 0.7
        close = round(base + drift + cycle, 2)
        high = round(close + 1.8 + (index % 3) * 0.25, 2)
        low = round(close - 1.6 - (index % 2) * 0.2, 2)
        volume = float(2000 + (seed % 1000) + index * 35 + (index % 5) * 120)
        highs.append(high)
        lows.append(low)
        closes.append(close)
        volumes.append(volume)

    return {"highs": highs, "lows": lows, "closes": closes, "volumes": volumes}


def get_mock_us_linkage() -> Dict[str, float]:
    return {
        "NASDAQ": 0.42,
        "QQQ": 0.38,
        "SOX": 0.55,
        "SMH": 0.46,
        "S&P500": 0.24,
        "VIX": -0.31,
        "TSM_ADR": 0.48,
        "TSM_ADR_PREMIUM": 0.08,
        "NVDA": 0.62,
        "AMD": 0.34,
        "AAPL": 0.18,
        "AVGO": 0.47,
        "MU": 0.22,
        "MSFT": 0.19,
        "META": 0.12,
        "GOOGL": 0.16,
        "AMZN": 0.15,
        "US_FUTURES": 0.12,
        "US_NEWS_SENTIMENT": 0.2,
    }


def get_mock_news(symbol: str) -> List[dict]:
    now = datetime.utcnow()
    return [
        {
            "title": f"{symbol} supply-chain demand remains resilient",
            "source": "mock-news",
            "published_at": now - timedelta(hours=5),
            "sentiment": "positive",
            "impact_score": 0.28,
            "related_symbols": [symbol, "NVDA", "TSM_ADR"],
        },
        {
            "title": "FX volatility remains a near-term risk for Taiwan exporters",
            "source": "mock-macro",
            "published_at": now - timedelta(hours=9),
            "sentiment": "cautious",
            "impact_score": -0.12,
            "related_symbols": [symbol],
        },
    ]
