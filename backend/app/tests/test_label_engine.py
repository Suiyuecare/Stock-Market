from datetime import date, datetime, timezone
from decimal import Decimal

from app.services.label_engine import LabelEngine


def _label(labels, name: str):
    return next(label for label in labels if label.label_name == name)


def test_label_engine_builds_absolute_relative_and_tp_sl_labels() -> None:
    labels = LabelEngine().build_labels(
        trade_date=date(2026, 6, 4),
        stock_id="2330",
        closes=[100, 101, 102, 103, 104, 105],
        benchmark_closes=[100, 100.2, 100.4, 100.6, 100.8, 101],
        horizons=[5],
        transaction_cost=Decimal("0.001"),
        minimum_excess_return=Decimal("0.002"),
        take_profit=Decimal("0.03"),
        stop_loss=Decimal("0.02"),
        available_for_signal_at=datetime(2026, 6, 11, 15, 5, tzinfo=timezone.utc),
    )

    assert _label(labels, "up_5d_absolute").label_value == 1
    assert _label(labels, "up_5d_relative").label_value == 1
    assert _label(labels, "up_5d_tp_sl").label_value == 1
    assert _label(labels, "up_5d_absolute").forward_return == Decimal("0.05")
    assert _label(labels, "up_5d_relative").excess_return == Decimal("0.04")


def test_label_engine_marks_relative_label_false_after_cost_and_minimum_excess() -> None:
    labels = LabelEngine().build_labels(
        trade_date=date(2026, 6, 4),
        stock_id="2330",
        closes=[100, 100.3, 100.4, 100.5, 100.6, 101.1],
        benchmark_closes=[100, 100.2, 100.4, 100.6, 100.8, 101],
        horizons=[5],
        transaction_cost=Decimal("0.001"),
        minimum_excess_return=Decimal("0.002"),
        available_for_signal_at=datetime(2026, 6, 11, 15, 5, tzinfo=timezone.utc),
    )

    assert _label(labels, "up_5d_absolute").label_value == 1
    assert _label(labels, "up_5d_relative").label_value == 0


def test_label_engine_tp_sl_respects_path_order() -> None:
    labels = LabelEngine().build_labels(
        trade_date=date(2026, 6, 4),
        stock_id="2330",
        closes=[100, 98, 104, 105, 106, 107],
        horizons=[5],
        take_profit=Decimal("0.03"),
        stop_loss=Decimal("0.02"),
        available_for_signal_at=datetime(2026, 6, 11, 15, 5, tzinfo=timezone.utc),
    )

    assert _label(labels, "up_5d_absolute").label_value == 1
    assert _label(labels, "up_5d_tp_sl").label_value == 0


def test_label_engine_risk_adjusted_label_uses_downside() -> None:
    labels = LabelEngine().build_labels(
        trade_date=date(2026, 6, 4),
        stock_id="2330",
        closes=[100, 99, 101, 102, 103, 104],
        horizons=[5],
        available_for_signal_at=datetime(2026, 6, 11, 15, 5, tzinfo=timezone.utc),
    )

    risk_adjusted = _label(labels, "up_5d_risk_adjusted")

    assert risk_adjusted.label_value == 1
    assert risk_adjusted.max_adverse_excursion == Decimal("-0.01")
