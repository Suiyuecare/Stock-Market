from datetime import datetime, timezone

from app.schemas import ExplainabilityDataSource, ExplainabilityReportInput
from app.services.explainability_report import ExplainabilityReportBuilder


def _report_input() -> ExplainabilityReportInput:
    return ExplainabilityReportInput(
        signal_id="sig-20260602-2330",
        stock_id="2330",
        stock_name="台積電",
        generated_at=datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
        model_version="mvp-factor-v1",
        scoring_version="final-score-v1",
        final_prediction={
            "BullishScore": 72.4,
            "RiskScore": 38.0,
            "RiskAdjustedScore": 59.1,
            "probability_up_1d": 0.66,
            "probability_up_5d": 0.69,
            "probability_up_20d": 0.71,
            "explanation": {
                "factor_weights": {"technical": 0.2, "chip": 0.18, "risk": 0.0},
                "risk_weight_multiplier": 1.0,
                "top_risk_factors": ["event_risk"],
            },
        },
        factor_scores={
            "technical": {
                "score": 82,
                "positive_factors": ["MACD golden cross", "price above MA20"],
                "negative_factors": [],
                "risk_factors": [],
                "data_sources": ["technical_indicators_daily"],
            },
            "chip": {
                "score": 42,
                "positive_factors": [],
                "negative_factors": ["Investment trust selling"],
                "risk_factors": ["chip_divergence"],
                "data_sources": ["institutional_trading_daily"],
            },
        },
        data_sources=[
            ExplainabilityDataSource(
                source="TWSE",
                dataset_name="price_daily",
                version="2026-06-02",
                available_for_signal_at=datetime(2026, 6, 2, 15, 5, tzinfo=timezone.utc),
                fields_used=["close", "volume"],
            )
        ],
        calibration_summary={"bucket": "65%-70%", "actual_win_rate": 0.67, "sample_count": 120},
        selection_decision={"decision": "primary_watchlist", "reasons": ["Probability passed the signal threshold."]},
        market_regime={"primary_regime": "bull_market"},
        portfolio_context={"weight": 0.08, "risk_flags": []},
    )


def test_explainability_report_preserves_audit_fields() -> None:
    report = ExplainabilityReportBuilder().build(_report_input())

    assert report.signal_id == "sig-20260602-2330"
    assert report.generated_at.isoformat() == "2026-06-02T15:05:00+00:00"
    assert report.model_version == "mvp-factor-v1"
    assert report.scoring_version == "final-score-v1"
    assert report.data_sources[0].dataset_name == "price_daily"
    assert report.score_calculation["RiskAdjustedScore"] == 59.1


def test_explainability_report_separates_positive_negative_and_risk_factors() -> None:
    report = ExplainabilityReportBuilder().build(_report_input())

    assert report.positive_factors[0].factor_name == "technical"
    assert report.positive_factors[0].explanation == "MACD golden cross; price above MA20"
    assert report.negative_factors[0].factor_name == "chip"
    assert "chip_divergence" in report.risk_factors
    assert "event_risk" in report.risk_factors


def test_explainability_report_includes_historical_selection_and_visible_text() -> None:
    report = ExplainabilityReportBuilder().build(_report_input())

    assert report.historical_win_rate_summary["actual_win_rate"] == 0.67
    assert report.selection_summary["decision"] == "primary_watchlist"
    assert "2330 台積電" in report.user_visible_text
    assert "本系統僅提供資料分析與研究用途" in report.user_visible_text
    assert "不構成個人化投資建議" in report.disclaimer
