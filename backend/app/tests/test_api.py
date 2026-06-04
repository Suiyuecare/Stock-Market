from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_prediction_signals() -> None:
    response = client.get("/api/predictions/signals")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert "probability_up" in response.json()[0]


def test_stock_ranking() -> None:
    response = client.get("/api/stocks/ranking")
    assert response.status_code == 200
    payload = response.json()
    assert "research and education" in payload["disclaimer"]
    assert len(payload["signals"]) >= 1


def test_stock_detail() -> None:
    response = client.get("/api/stocks/2330")
    assert response.status_code == 200
    payload = response.json()
    assert payload["signal"]["symbol"] == "2330"
    assert len(payload["signal"]["factor_scores"]) >= 5


def test_stocks_list() -> None:
    response = client.get("/api/stocks")
    assert response.status_code == 200
    payload = response.json()
    assert "research and education" in payload["disclaimer"]
    assert len(payload["stocks"]) >= 1
    assert payload["stocks"][0]["symbol"]


def test_stock_scores_endpoint() -> None:
    response = client.get("/api/stocks/2330/scores")
    assert response.status_code == 200
    payload = response.json()
    assert payload["stock_id"] == "2330"
    assert "BullishScore" in payload
    assert "RiskAdjustedScore" in payload
    assert 0 <= payload["probability_up_1d"] <= 1


def test_stock_technical_endpoint() -> None:
    response = client.get("/api/stocks/2330/technical")
    assert response.status_code == 200
    payload = response.json()
    assert payload["stock_id"] == "2330"
    assert "macd" in payload["signals"]
    assert "volume_price_divergence" in payload["signals"]
    assert "technical_score" in payload


def test_stock_institutional_endpoint() -> None:
    response = client.get("/api/stocks/2330/institutional")
    assert response.status_code == 200
    payload = response.json()
    assert payload["stock_id"] == "2330"
    assert "chip_score" in payload
    assert "institutional_net_ratio" in payload["summary"]


def test_stock_news_endpoint() -> None:
    response = client.get("/api/stocks/2330/news")
    assert response.status_code == 200
    payload = response.json()
    assert payload["stock_id"] == "2330"
    assert len(payload["news"]) >= 1


def test_stock_not_found() -> None:
    response = client.get("/api/stocks/9999")
    assert response.status_code == 404


def test_top_probability_ranking() -> None:
    response = client.get("/api/rankings/top-probability")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["signals"]) >= 1
    assert payload["candidate_count"] >= len(payload["signals"])
    assert payload["method"] == "dynamic-public-instrument-pool"


def test_institutional_buying_ranking() -> None:
    response = client.get("/api/rankings/institutional-buying")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["ranking"]) >= 1
    assert "institutional_net_ratio" in payload["ranking"][0]


def test_macd_golden_cross_ranking() -> None:
    response = client.get("/api/rankings/macd-golden-cross")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["ranking"]) >= 1
    assert "macd_golden_cross" in payload["ranking"][0]


def test_volume_price_divergence_ranking() -> None:
    response = client.get("/api/rankings/volume-price-divergence")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["ranking"]) >= 1
    assert "states" in payload["ranking"][0]


def test_us_market_radar() -> None:
    response = client.get("/api/us-market/radar")
    assert response.status_code == 200
    payload = response.json()
    assert "SOX" in payload["linkage"]
    assert len(payload["stocks"]) >= 1


def test_high_risk_endpoint() -> None:
    response = client.get("/api/risk/high-risk")
    assert response.status_code == 200
    payload = response.json()
    assert "signals" in payload
