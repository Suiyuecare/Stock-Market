import pytest

from app.schemas import CalibrationSample
from app.services.probability_calibration import ProbabilityCalibration


def _sample(probability: float, outcome: int, horizon_days: int = 5) -> CalibrationSample:
    return CalibrationSample(
        predicted_probability=probability,
        actual_outcome=outcome,
        horizon_days=horizon_days,
        sector="semiconductor",
        market_state="bull",
    )


def test_probability_calibration_builds_bucket_backtest_and_curve() -> None:
    samples = [
        _sample(0.61, 1),
        _sample(0.62, 1),
        _sample(0.63, 0),
        _sample(0.66, 1),
        _sample(0.67, 1),
        _sample(0.69, 0),
        _sample(0.71, 1),
        _sample(0.73, 1),
        _sample(0.74, 0),
    ]

    result = ProbabilityCalibration().evaluate(samples, horizon_days=5, bucket_size=0.05)

    assert result.sample_count == 9
    assert result.horizon_days == 5
    assert len(result.buckets) == 3
    assert result.buckets[0].lower_bound == 0.6
    assert result.buckets[0].upper_bound == 0.65
    assert result.buckets[0].average_predicted_probability == 0.62
    assert result.buckets[0].actual_win_rate == pytest.approx(0.666667)
    assert result.buckets[1].lower_bound == 0.65
    assert result.buckets[2].lower_bound == 0.7
    assert result.expected_calibration_error > 0


def test_brier_score_penalizes_overconfident_wrong_predictions() -> None:
    calibrator = ProbabilityCalibration()
    reasonable = [_sample(0.60, 1), _sample(0.40, 0)]
    overconfident_wrong = [_sample(0.90, 0), _sample(0.10, 1)]

    assert calibrator.brier_score(reasonable) == pytest.approx(0.16)
    assert calibrator.brier_score(overconfident_wrong) == pytest.approx(0.81)


def test_probability_calibration_marks_overconfident_bucket() -> None:
    samples = [_sample(0.80, 1), _sample(0.82, 0), _sample(0.83, 0), _sample(0.84, 0)]

    result = ProbabilityCalibration().evaluate(samples, horizon_days=5, bucket_size=0.05)

    assert result.buckets[0].actual_win_rate == 0.25
    assert result.buckets[0].reliability_status == "overconfident"
    assert result.max_calibration_error > 0.5


def test_probability_calibration_can_filter_by_horizon_and_segment() -> None:
    samples = [
        _sample(0.70, 1, horizon_days=5),
        _sample(0.70, 0, horizon_days=20),
        CalibrationSample(
            predicted_probability=0.70,
            actual_outcome=0,
            horizon_days=5,
            sector="financial",
            market_state="bear",
        ),
    ]

    result = ProbabilityCalibration().evaluate(
        samples,
        horizon_days=5,
        bucket_size=0.1,
        sector="semiconductor",
        market_state="bull",
    )

    assert result.sample_count == 1
    assert result.buckets[0].actual_win_rate == 1.0
