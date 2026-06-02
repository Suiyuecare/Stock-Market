from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from app.models import (
    Base,
    DataAvailabilityLedger,
    FactorScoresDaily,
    FeatureStoreDaily,
    InstitutionalTradingDaily,
    LabelsDaily,
    NewsEvent,
    PriceDaily,
    Signal,
    SignalOutcome,
    SignalPerformanceStats,
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
    "data_availability_ledger",
    "feature_store_daily",
    "labels_daily",
    "signals",
    "signal_outcomes",
    "signal_performance_stats",
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


def test_data_availability_ledger_enforces_point_in_time_usage() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    signal_generated_at = datetime(2026, 6, 5, 9, 0, tzinfo=timezone.utc)

    with Session(engine) as session:
        early_revenue = DataAvailabilityLedger(
            source="TWSE",
            dataset_name="price_daily",
            symbol="2330",
            data_date=date(2026, 6, 4),
            published_at=datetime(2026, 6, 4, 14, 40, tzinfo=timezone.utc),
            ingested_at=datetime(2026, 6, 4, 15, 1, tzinfo=timezone.utc),
            available_for_signal_at=datetime(2026, 6, 4, 15, 5, tzinfo=timezone.utc),
            revision_number=1,
            checksum="price-v1",
            raw_payload_path="raw/twse/price_daily/2026-06-04.json",
        )
        future_revenue = DataAvailabilityLedger(
            source="MOPS",
            dataset_name="fundamental_monthly",
            symbol="2330",
            data_date=date(2026, 5, 31),
            published_at=datetime(2026, 6, 10, 10, 0, tzinfo=timezone.utc),
            ingested_at=datetime(2026, 6, 10, 10, 5, tzinfo=timezone.utc),
            available_for_signal_at=datetime(2026, 6, 10, 10, 10, tzinfo=timezone.utc),
            revision_number=1,
            checksum="revenue-v1",
            raw_payload_path="raw/mops/fundamental_monthly/2026-05.json",
        )
        session.add_all([early_revenue, future_revenue])
        session.commit()

        usable_rows = session.scalars(
            select(DataAvailabilityLedger).where(DataAvailabilityLedger.available_for_signal_at <= signal_generated_at)
        ).all()

        assert [row.dataset_name for row in usable_rows] == ["price_daily"]


def test_feature_store_daily_preserves_point_in_time_feature_versions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    signal_generated_at = datetime(2026, 6, 5, 9, 0, tzinfo=timezone.utc)

    with Session(engine) as session:
        session.add(StockMaster(stock_id="2330", stock_name="台積電", market_type="TWSE", is_listed=True, is_otc=False))
        session.add_all(
            [
                FeatureStoreDaily(
                    trade_date=date(2026, 6, 4),
                    stock_id="2330",
                    feature_group="technical",
                    feature_name="rsi14",
                    feature_value=61.25,
                    feature_version="technical-v1",
                    calculated_at=datetime(2026, 6, 4, 15, 0, tzinfo=timezone.utc),
                    available_for_signal_at=datetime(2026, 6, 4, 15, 5, tzinfo=timezone.utc),
                ),
                FeatureStoreDaily(
                    trade_date=date(2026, 6, 4),
                    stock_id="2330",
                    feature_group="technical",
                    feature_name="rsi14",
                    feature_value=63.75,
                    feature_version="technical-v2",
                    calculated_at=datetime(2026, 6, 6, 15, 0, tzinfo=timezone.utc),
                    available_for_signal_at=datetime(2026, 6, 6, 15, 5, tzinfo=timezone.utc),
                ),
            ]
        )
        session.commit()

        usable_features = session.scalars(
            select(FeatureStoreDaily).where(
                FeatureStoreDaily.stock_id == "2330",
                FeatureStoreDaily.trade_date == date(2026, 6, 4),
                FeatureStoreDaily.available_for_signal_at <= signal_generated_at,
            )
        ).all()

        assert len(usable_features) == 1
        assert usable_features[0].feature_version == "technical-v1"


def test_labels_daily_can_store_multiple_label_targets() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(StockMaster(stock_id="2330", stock_name="台積電", market_type="TWSE", is_listed=True, is_otc=False))
        session.add_all(
            [
                LabelsDaily(
                    trade_date=date(2026, 6, 4),
                    stock_id="2330",
                    label_name="up_5d_absolute",
                    label_value=1,
                    horizon_days=5,
                    label_version="label-v1",
                    forward_return=0.04,
                    calculated_at=datetime(2026, 6, 11, 15, 0, tzinfo=timezone.utc),
                    available_for_signal_at=datetime(2026, 6, 11, 15, 5, tzinfo=timezone.utc),
                ),
                LabelsDaily(
                    trade_date=date(2026, 6, 4),
                    stock_id="2330",
                    label_name="up_5d_relative",
                    label_value=1,
                    horizon_days=5,
                    label_version="label-v1",
                    forward_return=0.04,
                    benchmark_return=0.01,
                    excess_return=0.03,
                    calculated_at=datetime(2026, 6, 11, 15, 0, tzinfo=timezone.utc),
                    available_for_signal_at=datetime(2026, 6, 11, 15, 5, tzinfo=timezone.utc),
                ),
            ]
        )
        session.commit()

        labels = session.scalars(select(LabelsDaily).where(LabelsDaily.stock_id == "2330")).all()

        assert {label.label_name for label in labels} == {"up_5d_absolute", "up_5d_relative"}


def test_signal_tables_store_generated_signals_outcomes_and_stats() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(StockMaster(stock_id="2330", stock_name="台積電", market_type="TWSE", is_listed=True, is_otc=False))
        session.add(
            Signal(
                signal_id="sig-2330-20260605-5d",
                generated_at=datetime(2026, 6, 4, 15, 10, tzinfo=timezone.utc),
                trade_date=date(2026, 6, 5),
                stock_id="2330",
                horizon_days=5,
                probability_up=0.64,
                bullish_score=72,
                risk_score=35,
                risk_adjusted_score=59.75,
                confidence=0.7,
                signal_rank=1,
                selected_for_watchlist=True,
                model_version="model-v1",
                feature_version="feature-v1",
            )
        )
        session.add(
            SignalOutcome(
                signal_id="sig-2330-20260605-5d",
                entry_date=date(2026, 6, 5),
                entry_price=100,
                exit_date=date(2026, 6, 12),
                exit_price=104,
                gross_return=0.04,
                net_return=0.035,
                benchmark_return=0.01,
                excess_return=0.025,
                win_absolute=True,
                win_relative=True,
                hit_take_profit=False,
                hit_stop_loss=False,
                max_favorable_excursion=0.05,
                max_adverse_excursion=-0.01,
                holding_days=5,
            )
        )
        session.add(
            SignalPerformanceStats(
                model_version="model-v1",
                strategy_version="mvp-default-v1",
                horizon_days=5,
                market_regime="bull_market",
                industry="semiconductor",
                probability_bucket="0.60-0.65",
                risk_bucket="30-40",
                trade_count=120,
                win_rate=0.62,
                win_rate_lower_bound=0.53,
                avg_net_return=0.018,
                median_net_return=0.011,
                profit_factor=1.45,
                max_drawdown=-0.08,
                sharpe=1.2,
                calibration_error=0.03,
            )
        )
        session.commit()

        assert session.query(Signal).count() == 1
        assert session.query(SignalOutcome).count() == 1
        assert session.query(SignalPerformanceStats).count() == 1
