from datetime import date, datetime, timezone
from decimal import Decimal
from hashlib import sha256
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DataAvailabilityLedger,
    FactorScoresDaily,
    InstitutionalTradingDaily,
    NewsEvent,
    PriceDaily,
    StockMaster,
    TechnicalIndicatorsDaily,
    USMarketDailyORM,
)


def persist_tw_after_close_result(session: Session, result: Dict[str, Any], trade_date: Optional[date] = None) -> Dict[str, int]:
    """Persist after-close price, technical, chip, factor, and availability artifacts."""
    effective_date = trade_date or _date_from_iso(result.get("completed_at")) or date.today()
    counts = {"stock_master": 0, "price_daily": 0, "institutional": 0, "technical": 0, "factor_scores": 0, "ledger": 0}

    for stock in result.get("stocks", []):
        stock_id = str(stock["stock_id"])
        _merge_stock(session, stock)
        counts["stock_master"] += 1

        session.merge(
            PriceDaily(
                trade_date=effective_date,
                stock_id=stock_id,
                open=_decimal(stock.get("latest_open", stock.get("latest_close"))),
                high=_decimal(stock.get("latest_high", stock.get("latest_close"))),
                low=_decimal(stock.get("latest_low", stock.get("latest_close"))),
                close=_decimal(stock.get("latest_close")) or Decimal("0"),
                volume=_int(stock.get("latest_volume")),
                turnover_value=_decimal(stock.get("turnover_value")),
            )
        )
        counts["price_daily"] += 1

        chip_score = stock.get("chip_score", {})
        volume = _int(stock.get("latest_volume")) or 0
        session.merge(
            InstitutionalTradingDaily(
                trade_date=effective_date,
                stock_id=stock_id,
                foreign_net=_ratio_to_volume(chip_score.get("foreign_net_ratio"), volume),
                investment_trust_net=_ratio_to_volume(chip_score.get("investment_trust_net_ratio"), volume),
                dealer_net=_ratio_to_volume(chip_score.get("dealer_net_ratio"), volume),
                dealer_self_net=0,
                dealer_hedge_net=0,
                total_institutional_net=_ratio_to_volume(chip_score.get("institutional_net_ratio"), volume),
                foreign_net_ratio=_decimal(chip_score.get("foreign_net_ratio")),
                investment_trust_net_ratio=_decimal(chip_score.get("investment_trust_net_ratio")),
                dealer_net_ratio=_decimal(chip_score.get("dealer_net_ratio")),
            )
        )
        counts["institutional"] += 1

        indicators = stock.get("technical_indicators", {})
        signals = stock.get("technical_signals", {})
        technical_score = stock.get("technical_score", {})
        macd = signals.get("macd", {})
        divergence = signals.get("volume_price_divergence", {})
        session.merge(
            TechnicalIndicatorsDaily(
                trade_date=effective_date,
                stock_id=stock_id,
                ma5=_decimal(indicators.get("ma_5")),
                ma20=_decimal(indicators.get("ma_20")),
                ma60=_decimal(indicators.get("ma_60")),
                rsi14=_decimal(indicators.get("rsi_14")),
                k_value=_decimal(indicators.get("k_9")),
                d_value=_decimal(indicators.get("d_9")),
                ema12=_decimal(macd.get("ema12")),
                ema26=_decimal(macd.get("ema26")),
                dif=_decimal(macd.get("dif", indicators.get("macd"))),
                dea=_decimal(macd.get("dea", indicators.get("macd_signal"))),
                macd_hist=_decimal(macd.get("macd_hist", indicators.get("macd_histogram"))),
                macd_bar_tw=_decimal(macd.get("macd_bar_tw")),
                obv=_decimal(indicators.get("obv")),
                volume_ma5=_decimal(stock.get("volume_ma5")),
                volume_ma20=_decimal(stock.get("volume_ma20")),
                bearish_volume_divergence=bool(divergence.get("bearish_divergence", False)),
                bullish_volume_divergence=bool(divergence.get("bullish_divergence", False)),
                volume_price_score=_decimal(technical_score.get("volume_price_score", indicators.get("volume_price_divergence"))),
                macd_score=_decimal(technical_score.get("macd_score")),
                technical_score=_decimal(technical_score.get("score")),
            )
        )
        counts["technical"] += 1

        factor_score = stock.get("factor_score", {})
        explanation = factor_score.get("explanation", {})
        components = explanation.get("component_scores", {})
        session.merge(
            FactorScoresDaily(
                trade_date=effective_date,
                stock_id=stock_id,
                fundamental_score=_decimal(components.get("fundamental")),
                chip_score=_decimal(components.get("chip")),
                macro_score=_decimal(components.get("macro")),
                technical_score=_decimal(components.get("technical")),
                news_score=_decimal(components.get("news")),
                us_market_score=_decimal(components.get("us_market")),
                target_price_score=_decimal(components.get("target_price")),
                risk_score=_decimal(factor_score.get("RiskScore")),
                bullish_score=_decimal(factor_score.get("BullishScore")),
                risk_adjusted_score=_decimal(factor_score.get("RiskAdjustedScore")),
                probability_up_1d=_decimal(factor_score.get("probability_up_1d")),
                probability_up_5d=_decimal(factor_score.get("probability_up_5d")),
                probability_up_20d=_decimal(factor_score.get("probability_up_20d")),
                top_positive_factors=explanation.get("top_positive_factors", []),
                top_negative_factors=explanation.get("top_negative_factors", []),
                top_risk_factors=explanation.get("top_risk_factors", []),
                confidence=_decimal(factor_score.get("confidence")),
            )
        )
        counts["factor_scores"] += 1
        counts["ledger"] += _add_ledger(session, "mock-after-close", "factor_scores_daily", stock_id, effective_date, result)

    session.commit()
    return counts


def persist_us_premarket_result(session: Session, result: Dict[str, Any], trade_date: Optional[date] = None) -> Dict[str, int]:
    """Persist US linkage proxy rows and availability records for pre-open radar jobs."""
    effective_date = trade_date or _date_from_iso(result.get("completed_at")) or date.today()
    counts = {"us_market_daily": 0, "ledger": 0}
    for symbol, value in result.get("linkage", {}).items():
        session.merge(
            USMarketDailyORM(
                trade_date=effective_date,
                symbol=symbol,
                symbol_type="linkage_proxy",
                open=_decimal(100),
                high=_decimal(100 + abs(float(value))),
                low=_decimal(100 - abs(float(value))),
                close=_decimal(100 + float(value)),
                volume=None,
                return_1d=_decimal(value),
            )
        )
        counts["us_market_daily"] += 1
        counts["ledger"] += _add_ledger(session, "mock-us-linkage", "us_market_daily", symbol, effective_date, result)
    session.commit()
    return counts


def persist_news_ingestion_result(session: Session, result: Dict[str, Any]) -> Dict[str, int]:
    """Persist classified news events and source availability rows."""
    counts = {"news_events": 0, "ledger": 0}
    for stock in result.get("stocks", []):
        _merge_stock(session, stock)
        stock_id = str(stock["stock_id"])
        for event in stock.get("events", []):
            event_time = _datetime_from_value(event.get("published_at")) or datetime.now(timezone.utc)
            existing = session.scalar(
                select(NewsEvent).where(
                    NewsEvent.stock_id == stock_id,
                    NewsEvent.source == str(event.get("source", "unknown")),
                    NewsEvent.title == str(event.get("title", "")),
                    NewsEvent.event_time == event_time,
                )
            )
            if existing is None:
                session.add(
                    NewsEvent(
                        event_time=event_time,
                        market="TW",
                        stock_id=stock_id,
                        related_symbol=_first_related_symbol(event.get("related_symbols", [])),
                        related_industry=None,
                        source=str(event.get("source", "unknown")),
                        title=str(event.get("title", "")),
                        summary=str(event.get("summary", "")),
                        sentiment_score=_decimal(event.get("classified_impact_score", event.get("impact_score"))),
                        event_type=str(event.get("event_type", "news")),
                        impact_score=_decimal(event.get("classified_impact_score", event.get("impact_score"))),
                        confidence=_decimal(event.get("confidence", 0.5)),
                    )
                )
                counts["news_events"] += 1
        counts["ledger"] += _add_ledger(session, "mock-news", "news_events", stock_id, date.today(), stock)
    session.commit()
    return counts


def _merge_stock(session: Session, stock: Dict[str, Any]) -> None:
    session.merge(
        StockMaster(
            stock_id=str(stock["stock_id"]),
            stock_name=str(stock.get("stock_name") or stock.get("name") or stock["stock_id"]),
            market_type=str(stock.get("market_type", "TWSE")),
            industry=stock.get("industry"),
            sub_industry=stock.get("sub_industry"),
            supply_chain_tags=list(stock.get("supply_chain_tags", [])),
            is_listed=bool(stock.get("is_listed", True)),
            is_otc=bool(stock.get("is_otc", False)),
        )
    )


def _add_ledger(
    session: Session,
    source: str,
    dataset_name: str,
    symbol: str,
    data_date: date,
    payload: Dict[str, Any],
) -> int:
    existing = session.scalar(
        select(DataAvailabilityLedger).where(
            DataAvailabilityLedger.source == source,
            DataAvailabilityLedger.dataset_name == dataset_name,
            DataAvailabilityLedger.symbol == symbol,
            DataAvailabilityLedger.data_date == data_date,
            DataAvailabilityLedger.revision_number == 1,
        )
    )
    if existing is not None:
        return 0
    now = datetime.now(timezone.utc)
    session.add(
        DataAvailabilityLedger(
            source=source,
            dataset_name=dataset_name,
            symbol=symbol,
            data_date=data_date,
            published_at=now,
            ingested_at=now,
            available_for_signal_at=now,
            revision_number=1,
            checksum=_checksum(payload),
            raw_payload_path=None,
        )
    )
    return 1


def _decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value))


def _int(value: Any) -> Optional[int]:
    if value is None:
        return None
    return int(float(value))


def _ratio_to_volume(value: Any, volume: int) -> int:
    ratio = _decimal(value)
    if ratio is None:
        return 0
    return int(ratio * volume)


def _date_from_iso(value: Any) -> Optional[date]:
    parsed = _datetime_from_value(value)
    return parsed.date() if parsed else None


def _datetime_from_value(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _first_related_symbol(values: Iterable[Any]) -> Optional[str]:
    for value in values:
        return str(value)
    return None


def _checksum(payload: Dict[str, Any]) -> str:
    return sha256(repr(payload).encode("utf-8")).hexdigest()
