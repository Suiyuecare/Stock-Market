from app.services.data_providers.mock_provider import TW_INSTRUMENTS
from app.services.jobs.daily_after_market_job import run_tw_after_close_job
from app.services.jobs.news_ingestion_job import run_news_ingestion_job
from app.services.jobs.pre_open_us_market_job import run_us_premarket_job


def test_daily_after_market_job_updates_tw_artifacts() -> None:
    result = run_tw_after_close_job()

    assert result["status"] == "completed"
    assert result["updated_prices"] == len(TW_INSTRUMENTS)
    assert result["updated_institutional_rows"] == len(TW_INSTRUMENTS)
    assert result["calculated_technical_indicators"] == len(TW_INSTRUMENTS)
    assert result["calculated_factor_scores"] == len(TW_INSTRUMENTS)
    first_stock = result["stocks"][0]
    assert first_stock["latest_close"] > 0
    assert "ma_20" in first_stock["technical_indicators"]
    assert 0 <= first_stock["technical_score"]["score"] <= 100
    assert 0 <= first_stock["chip_score"]["score"] <= 100
    assert 0 <= first_stock["factor_score"]["probability_up_1d"] <= 1


def test_pre_open_us_market_job_generates_radar() -> None:
    result = run_us_premarket_job()

    assert result["status"] == "completed"
    assert result["updated_us_market_symbols"] >= 10
    assert result["updated_us_linkage_scores"] == len(TW_INSTRUMENTS)
    assert result["generated_pre_open_radar"] is True
    radar = result["radar"]
    assert len(radar) == len(TW_INSTRUMENTS)
    assert radar[0]["us_market_score"] >= radar[-1]["us_market_score"]
    assert "SOX" in result["linkage"]


def test_news_ingestion_job_classifies_events_and_updates_scores() -> None:
    result = run_news_ingestion_job()

    assert result["status"] == "completed"
    assert result["events_ingested"] == len(TW_INSTRUMENTS) * 2
    assert result["events_classified"] == result["events_ingested"]
    assert result["updated_news_scores"] == len(TW_INSTRUMENTS)
    first_stock = result["stocks"][0]
    assert len(first_stock["events"]) >= 1
    assert "classified_sentiment" in first_stock["events"][0]
    assert "parser_reasons" in first_stock["events"][0]
    assert "score" in first_stock["news_score"]
