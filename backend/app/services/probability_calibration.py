from statistics import mean
from typing import Dict, List, Optional

from app.schemas import CalibrationBucket, CalibrationResult, CalibrationSample


class ProbabilityCalibration:
    """Evaluate whether predicted probabilities match realized outcomes."""

    def evaluate(
        self,
        samples: List[CalibrationSample],
        horizon_days: int,
        bucket_size: float = 0.05,
        min_bucket_size: int = 1,
        sector: Optional[str] = None,
        market_state: Optional[str] = None,
    ) -> CalibrationResult:
        filtered = [
            sample
            for sample in samples
            if sample.horizon_days == horizon_days
            and (sector is None or sample.sector == sector)
            and (market_state is None or sample.market_state == market_state)
        ]
        buckets = self._build_buckets(filtered, bucket_size, min_bucket_size)
        brier_score = self.brier_score(filtered)
        weighted_error = sum(bucket.calibration_error * bucket.sample_count for bucket in buckets)
        expected_calibration_error = weighted_error / len(filtered) if filtered else 0.0
        max_calibration_error = max([bucket.calibration_error for bucket in buckets], default=0.0)

        return CalibrationResult(
            horizon_days=horizon_days,
            sample_count=len(filtered),
            brier_score=round(brier_score, 6),
            expected_calibration_error=round(expected_calibration_error, 6),
            max_calibration_error=round(max_calibration_error, 6),
            buckets=buckets,
        )

    def brier_score(self, samples: List[CalibrationSample]) -> float:
        if not samples:
            return 0.0
        errors = [(sample.predicted_probability - sample.actual_outcome) ** 2 for sample in samples]
        return round(mean(errors), 6)

    def _build_buckets(
        self,
        samples: List[CalibrationSample],
        bucket_size: float,
        min_bucket_size: int,
    ) -> List[CalibrationBucket]:
        if bucket_size <= 0 or bucket_size > 1:
            raise ValueError("bucket_size must be between 0 and 1")

        grouped: Dict[int, List[CalibrationSample]] = {}
        bucket_count = int(round(1 / bucket_size))
        for sample in samples:
            probability = min(max(sample.predicted_probability, 0.0), 1.0)
            bucket_index = min(int(probability / bucket_size), bucket_count - 1)
            grouped.setdefault(bucket_index, []).append(sample)

        buckets: List[CalibrationBucket] = []
        for bucket_index in sorted(grouped):
            bucket_samples = grouped[bucket_index]
            if len(bucket_samples) < min_bucket_size:
                continue
            average_probability = mean([sample.predicted_probability for sample in bucket_samples])
            actual_win_rate = mean([sample.actual_outcome for sample in bucket_samples])
            calibration_error = abs(average_probability - actual_win_rate)
            bucket_brier = self.brier_score(bucket_samples)
            lower_bound = round(bucket_index * bucket_size, 6)
            upper_bound = round(min(1.0, lower_bound + bucket_size), 6)

            buckets.append(
                CalibrationBucket(
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    sample_count=len(bucket_samples),
                    average_predicted_probability=round(average_probability, 6),
                    actual_win_rate=round(actual_win_rate, 6),
                    calibration_error=round(calibration_error, 6),
                    brier_score=bucket_brier,
                    reliability_status=self._reliability_status(average_probability, actual_win_rate),
                )
            )
        return buckets

    def _reliability_status(self, predicted_probability: float, actual_win_rate: float) -> str:
        gap = predicted_probability - actual_win_rate
        if abs(gap) <= 0.03:
            return "well_calibrated"
        if gap > 0:
            return "overconfident"
        return "underconfident"
