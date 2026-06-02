from datetime import date

from app.schemas import Instrument, MarketSummary, PredictionSignal


def get_market_summary() -> MarketSummary:
    return MarketSummary(
        session_date=date.today(),
        tw_status="after-close-ready",
        us_premarket_status="pending",
        instruments=[
            Instrument(symbol="2330", market="TW", name="台積電", sector="半導體", currency="TWD"),
            Instrument(symbol="2454", market="TW", name="聯發科", sector="半導體", currency="TWD"),
            Instrument(symbol="NVDA", market="US", name="NVIDIA", sector="AI / Semiconductors", currency="USD"),
            Instrument(symbol="AAPL", market="US", name="Apple", sector="Consumer Technology", currency="USD"),
        ],
    )


def get_prediction_signals() -> list[PredictionSignal]:
    return [
        PredictionSignal(
            symbol="2330",
            signal_date=date.today(),
            horizon="next-session",
            score=0.68,
            confidence=0.61,
            drivers=[
                {"type": "us-tech", "label": "NASDAQ futures positive", "weight": 0.28},
                {"type": "adr", "label": "TSM ADR relative strength", "weight": 0.22},
                {"type": "news", "label": "AI supply chain demand remains firm", "weight": 0.18},
            ],
        ),
        PredictionSignal(
            symbol="2454",
            signal_date=date.today(),
            horizon="next-session",
            score=0.57,
            confidence=0.54,
            drivers=[
                {"type": "sector", "label": "Semiconductor sector mildly positive", "weight": 0.2},
                {"type": "fx", "label": "TWD volatility watch", "weight": -0.08},
            ],
        ),
    ]
