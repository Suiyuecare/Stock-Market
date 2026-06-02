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
