from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import (
    Base,
    DataAvailabilityLedger,
    FactorScoresDaily,
    InstitutionalTradingDaily,
    NewsEvent,
    PriceDaily,
    StockMaster,
    TechnicalIndicatorsDaily,
    USMarketDailyORM,
)
from app.services.data_providers.mock_provider import TW_INSTRUMENTS
from app.services.jobs.daily_after_market_job import run_tw_after_close_job
from app.services.jobs.news_ingestion_job import run_news_ingestion_job
from app.services.jobs.pre_open_us_market_job import run_us_premarket_job


def _session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def test_after_close_job_persists_prices_indicators_factors_and_ledger() -> None:
    with _session() as session:
        result = run_tw_after_close_job(session=session)

        assert result["persisted"]["price_daily"] == len(TW_INSTRUMENTS)
        assert session.query(StockMaster).count() == len(TW_INSTRUMENTS)
        assert session.query(PriceDaily).count() == len(TW_INSTRUMENTS)
        assert session.query(InstitutionalTradingDaily).count() == len(TW_INSTRUMENTS)
        assert session.query(TechnicalIndicatorsDaily).count() == len(TW_INSTRUMENTS)
        assert session.query(FactorScoresDaily).count() == len(TW_INSTRUMENTS)
        assert session.query(DataAvailabilityLedger).filter_by(dataset_name="factor_scores_daily").count() == len(TW_INSTRUMENTS)


def test_us_premarket_job_persists_us_market_proxy_rows() -> None:
    with _session() as session:
        result = run_us_premarket_job(session=session)

        assert result["persisted"]["us_market_daily"] == len(result["linkage"])
        assert session.query(USMarketDailyORM).count() == len(result["linkage"])
        assert session.query(DataAvailabilityLedger).filter_by(dataset_name="us_market_daily").count() == len(result["linkage"])


def test_news_ingestion_job_persists_news_events_and_ledger() -> None:
    with _session() as session:
        result = run_news_ingestion_job(session=session)

        assert result["persisted"]["news_events"] == result["events_ingested"]
        assert session.query(NewsEvent).count() == result["events_ingested"]
        assert session.query(DataAvailabilityLedger).filter_by(dataset_name="news_events").count() == len(TW_INSTRUMENTS)
