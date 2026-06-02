from pathlib import Path

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from app.models import (
    Base,
    FactorScoresDaily,
    InstitutionalTradingDaily,
    NewsEvent,
    PriceDaily,
    StockMaster,
    USMarketDailyORM,
)
from app.services.data_providers.csv_seed_loader import seed_from_sample_data


EXPECTED_TABLES = {
    "stock_master",
    "price_daily",
    "fundamental_monthly",
    "fundamental_quarterly",
    "institutional_trading_daily",
    "technical_indicators_daily",
    "us_market_daily",
    "us_tw_supply_chain_map",
    "news_events",
    "factor_scores_daily",
}


def test_sqlalchemy_models_create_expected_tables() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    tables = set(inspect(engine).get_table_names())

    assert EXPECTED_TABLES.issubset(tables)


def test_sample_csv_seed_data_can_be_inserted() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    sample_data_dir = Path(__file__).resolve().parents[3] / "sample_data"

    with Session(engine) as session:
        seed_from_sample_data(session, sample_data_dir)

        assert session.scalar(select(StockMaster).where(StockMaster.stock_id == "2330")).stock_name == "台積電"
        assert session.query(PriceDaily).count() == 4
        assert session.query(InstitutionalTradingDaily).count() == 4
        assert session.query(USMarketDailyORM).count() == 14
        assert session.query(NewsEvent).count() == 2
        assert session.query(FactorScoresDaily).count() == 1

        institutional = session.scalar(select(InstitutionalTradingDaily).where(InstitutionalTradingDaily.stock_id == "2330"))
        assert institutional.foreign_net == 5_200_000
        assert institutional.total_institutional_net == 5_700_000
        assert institutional.foreign_net_ratio is not None

        factor_score = session.scalar(select(FactorScoresDaily).where(FactorScoresDaily.stock_id == "2330"))
        assert factor_score.fundamental_score is not None
        assert factor_score.top_positive_factors
