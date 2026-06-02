from datetime import date

from app.schemas import ModelMonitoringInput, ModelMonitoringThresholds
from app.services.model_monitoring import ModelMonitoringEngine


def _input(**overrides: object) -> ModelMonitoringInput:
    values = {
        "monitoring_date": date(2026, 6, 2),
        "win_rate_20d": 0.56,
        "win_rate_60d": 0.58,
        "historical_win_rate_mean": 0.55,
        "historical_win_rate_std": 0.05,
        "average_return_20d": 0.012,
        "max_drawdown_20d": 0.06,
        "calibration_error": 0.04,
        "sector_win_rate_20d": {"semiconductor": 0.57, "ai_server": 0.6},
        "historical_sector_win_rate": {"semiconductor": 0.56, "ai_server": 0.58},
        "factor_contribution_20d": {"technical": 0.18, "chip": 0.16},
        "historical_factor_contribution": {"technical": 0.17, "chip": 0.15},
        "data_latency_minutes": 5.0,
        "api_failure_rate": 0.01,
        "news_parse_error_rate": 0.02,
    }
    values.update(overrides)
    return ModelMonitoringInput(**values)


def test_model_monitoring_returns_healthy_when_metrics_are_normal() -> None:
    result = ModelMonitoringEngine().evaluate(_input())

    assert result.health_status == "healthy"
    assert result.signal_strength_multiplier == 1.0
    assert result.alerts == []
    assert result.metrics["win_rate_20d"] == 0.56


def test_model_monitoring_flags_possible_model_decay_below_two_std() -> None:
    result = ModelMonitoringEngine().evaluate(_input(win_rate_20d=0.43))

    assert result.health_status == "critical"
    assert result.signal_strength_multiplier == 0.5
    assert result.alerts[0].code == "possible_model_decay"
    assert "retraining" in result.alerts[0].recommended_action


def test_model_monitoring_flags_calibration_drawdown_and_operations() -> None:
    result = ModelMonitoringEngine().evaluate(
        _input(
            max_drawdown_20d=0.15,
            calibration_error=0.1,
            data_latency_minutes=45,
            api_failure_rate=0.08,
            news_parse_error_rate=0.09,
        )
    )
    codes = {alert.code for alert in result.alerts}

    assert result.health_status == "degraded"
    assert "drawdown_limit_breached" in codes
    assert "probability_calibration_drift" in codes
    assert "data_latency_high" in codes
    assert "api_failure_rate_high" in codes
    assert "news_parse_error_rate_high" in codes
    assert result.signal_strength_multiplier < 1.0


def test_model_monitoring_flags_sector_and_factor_drift() -> None:
    result = ModelMonitoringEngine().evaluate(
        _input(
            sector_win_rate_20d={"semiconductor": 0.40},
            historical_sector_win_rate={"semiconductor": 0.56},
            factor_contribution_20d={"technical": 0.35},
            historical_factor_contribution={"technical": 0.17},
        )
    )
    codes = {alert.code for alert in result.alerts}

    assert "sector_win_rate_drop:semiconductor" in codes
    assert "factor_contribution_drift:technical" in codes


def test_model_monitoring_thresholds_can_be_tuned() -> None:
    result = ModelMonitoringEngine().evaluate(
        _input(calibration_error=0.07),
        ModelMonitoringThresholds(calibration_error_threshold=0.06),
    )

    assert {alert.code for alert in result.alerts} == {"probability_calibration_drift"}
