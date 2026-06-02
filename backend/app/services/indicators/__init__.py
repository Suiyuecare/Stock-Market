from app.services.indicators.kd import analyze_kd, stochastic_kd
from app.services.indicators.macd import analyze_macd, ema, macd, macd_series
from app.services.indicators.moving_average import analyze_moving_averages, moving_average
from app.services.indicators.obv import analyze_obv, obv, obv_series
from app.services.indicators.rsi import analyze_rsi, rsi
from app.services.indicators.volume_price_divergence import analyze_volume_price_divergence, volume_price_divergence

__all__ = [
    "analyze_macd",
    "analyze_kd",
    "analyze_moving_averages",
    "analyze_obv",
    "analyze_rsi",
    "analyze_volume_price_divergence",
    "build_technical_indicators",
    "ema",
    "macd",
    "macd_series",
    "moving_average",
    "obv",
    "obv_series",
    "rsi",
    "stochastic_kd",
    "volume_price_divergence",
]


def build_technical_indicators(highs, lows, closes, volumes) -> dict:
    close_series = list(closes)
    high_series = list(highs)
    low_series = list(lows)
    volume_series = list(volumes)
    k, d = stochastic_kd(high_series, low_series, close_series)
    macd_line, signal_line, histogram = macd(close_series)
    macd_analysis = analyze_macd(close_series)
    volume_price_analysis = analyze_volume_price_divergence(close_series, volume_series, macd_series(close_series)["macd_hist"])

    return {
        "ma_5": moving_average(close_series, 5),
        "ma_20": moving_average(close_series, 20),
        "ma_60": moving_average(close_series, 60),
        "rsi_14": rsi(close_series, 14),
        "k_9": k,
        "d_9": d,
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_histogram": histogram,
        "obv": obv(close_series, volume_series),
        "volume_price_divergence": volume_price_divergence(close_series, volume_series),
        "signals": {
            "moving_average": analyze_moving_averages(close_series),
            "rsi": analyze_rsi(close_series, 14),
            "kd": analyze_kd(high_series, low_series, close_series),
            "obv": analyze_obv(close_series, volume_series),
            "macd": macd_analysis,
            "volume_price_divergence": volume_price_analysis,
        },
    }
