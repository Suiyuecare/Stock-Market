import csv
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from app.models import (
    FactorScoresDaily,
    InstitutionalTradingDaily,
    NewsEvent,
    PriceDaily,
    StockMaster,
    USMarketDailyORM,
)

STOCK_NAMES = {
    "2330": ("台積電", "半導體", "晶圓代工", ["semiconductor", "foundry", "AI", "TSM_ADR"]),
    "2454": ("聯發科", "半導體", "IC設計", ["semiconductor", "IC design", "edge-ai"]),
    "2317": ("鴻海", "電子代工", "EMS", ["AI-server", "Apple", "EMS"]),
    "2308": ("台達電", "電源管理", "電源供應器", ["AI-server", "energy", "power"]),
}


def _read_csv(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def _decimal(value: object, default: str = "0") -> Decimal:
    if value is None or value == "":
        return Decimal(default)
    return Decimal(str(value))


def _int(value: object, default: int = 0) -> int:
    if value is None or value == "":
        return default
    return int(Decimal(str(value)))


def _date(value: str) -> date:
    return date.fromisoformat(value)


def _datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _ratio(numerator: int, volume: int) -> Optional[Decimal]:
    if volume <= 0:
        return None
    return (Decimal(numerator) / Decimal(volume)).quantize(Decimal("0.0001"))


def seed_from_sample_data(session: Session, sample_data_dir: Path) -> None:
    price_rows = _read_csv(sample_data_dir / "tw_prices.csv")
    price_lookup = {(row["symbol"], row["trade_date"]): row for row in price_rows}

    _seed_stock_master(session, (row["symbol"] for row in price_rows))
    _seed_prices(session, price_rows)
    _seed_institutional_trading(session, _read_csv(sample_data_dir / "institutional_trading.csv"), price_lookup)
    _seed_us_market(session, _read_csv(sample_data_dir / "us_market.csv"))
    _seed_news(session, _read_csv(sample_data_dir / "news_events.csv"))
    _seed_factor_scores(session, _read_csv(sample_data_dir / "factor_scores.csv"))
    session.commit()


def _seed_stock_master(session: Session, symbols: Iterable[str]) -> None:
    for symbol in sorted(set(symbols)):
        stock_name, industry, sub_industry, tags = STOCK_NAMES.get(symbol, (symbol, "unknown", None, []))
        session.merge(
            StockMaster(
                stock_id=symbol,
                stock_name=stock_name,
                market_type="TWSE",
                industry=industry,
                sub_industry=sub_industry,
                supply_chain_tags=tags,
                is_listed=True,
                is_otc=False,
            )
        )


def _seed_prices(session: Session, rows: List[dict]) -> None:
    for row in rows:
        close = _decimal(row["close"])
        volume = _int(row["volume"])
        session.merge(
            PriceDaily(
                trade_date=_date(row["trade_date"]),
                stock_id=row["symbol"],
                open=_decimal(row["open"]),
                high=_decimal(row["high"]),
                low=_decimal(row["low"]),
                close=close,
                volume=volume,
                turnover_value=close * Decimal(volume),
            )
        )


def _seed_institutional_trading(session: Session, rows: List[dict], price_lookup: Dict[tuple, dict]) -> None:
    for row in rows:
        price = price_lookup.get((row["symbol"], row["trade_date"]), {})
        volume = _int(price.get("volume"))
        foreign_net = _int(row["foreign_net_buy"])
        trust_net = _int(row["investment_trust_net_buy"])
        dealer_net = _int(row["dealer_net_buy"])
        total = foreign_net + trust_net + dealer_net
        session.merge(
            InstitutionalTradingDaily(
                trade_date=_date(row["trade_date"]),
                stock_id=row["symbol"],
                foreign_net=foreign_net,
                investment_trust_net=trust_net,
                dealer_net=dealer_net,
                dealer_self_net=dealer_net,
                dealer_hedge_net=0,
                total_institutional_net=total,
                foreign_net_ratio=_ratio(foreign_net, volume),
                investment_trust_net_ratio=_ratio(trust_net, volume),
                dealer_net_ratio=_ratio(dealer_net, volume),
            )
        )


def _seed_us_market(session: Session, rows: List[dict]) -> None:
    symbol_map = {
        "nasdaq": ("NASDAQ", "index"),
        "sox": ("SOX", "index"),
        "sp500": ("S&P500", "index"),
        "vix": ("VIX", "risk"),
        "tsm_adr": ("TSM_ADR", "stock"),
        "nvda": ("NVDA", "stock"),
        "amd": ("AMD", "stock"),
        "aapl": ("AAPL", "stock"),
        "avgo": ("AVGO", "stock"),
        "mu": ("MU", "stock"),
        "msft": ("MSFT", "stock"),
        "meta": ("META", "stock"),
        "googl": ("GOOGL", "stock"),
        "amzn": ("AMZN", "stock"),
    }
    for row in rows:
        trade_date = _date(row["session_date"])
        for source_key, (symbol, symbol_type) in symbol_map.items():
            return_1d = _decimal(row[source_key])
            close = Decimal("100") * (Decimal("1") + return_1d)
            session.merge(
                USMarketDailyORM(
                    trade_date=trade_date,
                    symbol=symbol,
                    symbol_type=symbol_type,
                    open=None,
                    high=None,
                    low=None,
                    close=close,
                    volume=None,
                    return_1d=return_1d,
                )
            )


def _seed_news(session: Session, rows: List[dict]) -> None:
    sentiment_scores = {"positive": Decimal("0.7000"), "cautious": Decimal("0.4200"), "negative": Decimal("0.2500")}
    for row in rows:
        related_symbols = [symbol for symbol in row["related_symbols"].split(";") if symbol]
        stock_id = next((symbol for symbol in related_symbols if symbol.isdigit()), None)
        session.add(
            NewsEvent(
                event_time=_datetime(row["published_at"]),
                market="TW",
                stock_id=stock_id,
                related_symbol=";".join(related_symbols),
                related_industry=None,
                source=row["source"],
                title=row["title"],
                summary=row["title"],
                sentiment_score=sentiment_scores.get(row["sentiment"], Decimal("0.5000")),
                event_type="sample",
                impact_score=_decimal(row["impact_score"]),
                confidence=Decimal("0.6000"),
            )
        )


def _seed_factor_scores(session: Session, rows: List[dict]) -> None:
    grouped: Dict[tuple, List[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["symbol"], row["signal_date"])].append(row)

    category_columns = {
        "fundamental": "fundamental_score",
        "chip": "chip_score",
        "technical": "technical_score",
        "us-linkage": "us_market_score",
        "news": "news_score",
    }
    for (symbol, signal_date), factor_rows in grouped.items():
        values = {column: None for column in category_columns.values()}
        positive = []
        negative = []
        weighted_sum = Decimal("0")
        total_weight = Decimal("0")
        for factor in factor_rows:
            score = _decimal(factor["score"])
            weight = _decimal(factor["weight"])
            category = factor["category"]
            column = category_columns.get(category)
            if column:
                values[column] = score
            weighted_sum += score * weight
            total_weight += weight
            target = positive if score >= Decimal("0.2") else negative
            target.append(factor["factor_name"])
        bullish = weighted_sum / total_weight if total_weight else None
        risk = Decimal("0.3000")
        risk_adjusted = bullish - risk * Decimal("0.35") if bullish is not None else None
        session.merge(
            FactorScoresDaily(
                trade_date=_date(signal_date),
                stock_id=symbol,
                macro_score=None,
                target_price_score=None,
                risk_score=risk,
                bullish_score=bullish,
                risk_adjusted_score=risk_adjusted,
                probability_up_1d=Decimal("0.5000") + (risk_adjusted or Decimal("0")) * Decimal("0.3200"),
                probability_up_5d=None,
                probability_up_20d=None,
                top_positive_factors=positive,
                top_negative_factors=negative,
                top_risk_factors=[],
                confidence=Decimal("0.6000"),
                **values,
            )
        )
