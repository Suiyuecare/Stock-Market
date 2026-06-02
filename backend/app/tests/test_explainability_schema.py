from datetime import datetime, timezone

from app.schemas import (
    ExplainabilityDataSource,
    ExplainabilityFactorContribution,
    ExplainabilityReport,
    ExplainabilityReportInput,
)


def test_explainability_data_source_schema_tracks_point_in_time_source() -> None:
    source = ExplainabilityDataSource(
        source="TWSE",
        dataset_name="price_daily",
        version="2026-06-02",
        available_for_signal_at=datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
        fields_used=["close", "volume"],
    )

    assert source.source == "TWSE"
    assert source.fields_used == ["close", "volume"]


def test_explainability_report_input_schema_requires_traceability_fields() -> None:
    report_input = ExplainabilityReportInput(
        signal_id="sig-1",
        stock_id="2330",
        stock_name="台積電",
        generated_at=datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
        model_version="model-v1",
        scoring_version="score-v1",
        final_prediction={"RiskAdjustedScore": 60},
        factor_scores={},
        data_sources=[],
    )

    assert report_input.signal_id == "sig-1"
    assert report_input.model_version == "model-v1"


def test_explainability_report_schema_keeps_user_visible_text() -> None:
    report = ExplainabilityReport(
        signal_id="sig-1",
        stock_id="2330",
        stock_name="台積電",
        generated_at=datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
        model_version="model-v1",
        scoring_version="score-v1",
        data_sources=[],
        score_calculation={"RiskAdjustedScore": 60},
        positive_factors=[
            ExplainabilityFactorContribution(
                factor_name="technical",
                score=80,
                weight=0.2,
                contribution=16,
                direction="positive",
                explanation="Price above MA20.",
                data_sources=["technical_indicators_daily"],
            )
        ],
        negative_factors=[],
        risk_factors=["event_risk"],
        historical_win_rate_summary={"actual_win_rate": 0.67},
        selection_summary={"decision": "primary_watchlist"},
        market_regime_summary={"primary_regime": "bull_market"},
        portfolio_risk_summary={"weight": 0.08},
        user_visible_text="Research explanation text.",
        disclaimer="Research use only.",
    )

    assert report.user_visible_text == "Research explanation text."
    assert report.positive_factors[0].data_sources == ["technical_indicators_daily"]
