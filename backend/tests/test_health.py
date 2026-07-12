from fastapi.testclient import TestClient

from src.core.config import get_settings
from src.main import create_app


def test_health_endpoint(monkeypatch) -> None:
    monkeypatch.setenv("MONGO_ENABLED", "false")
    get_settings.cache_clear()

    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    payload = response.json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["status"] == "ok"
