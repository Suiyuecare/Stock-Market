from decimal import Decimal

from app.schemas import FeatureSnapshotRequest, FeatureSnapshotResult, FeatureStoreDailyRecord


class FeatureSnapshotEngine:
    """Create point-in-time feature records for a signal date."""

    def build_snapshot(self, request: FeatureSnapshotRequest) -> FeatureSnapshotResult:
        records = [
            FeatureStoreDailyRecord(
                trade_date=request.trade_date,
                stock_id=request.stock_id,
                feature_group=request.feature_group,
                feature_name=name,
                feature_value=self._to_decimal(value),
                feature_version=request.feature_version,
                calculated_at=request.calculated_at,
                available_for_signal_at=request.available_for_signal_at,
            )
            for name, value in sorted(request.features.items())
        ]
        return FeatureSnapshotResult(records=records)

    def _to_decimal(self, value: Decimal) -> Decimal:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
