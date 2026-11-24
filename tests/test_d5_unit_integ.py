
import logging
from fastapi.testclient import TestClient
from app.main import app

def test_health_response_id_matches_completion_log(caplog):
    with caplog.at_level(logging.INFO):
        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert request_id.strip()

    assert any(
        getattr(record, "request_id", None) == request_id
        and 
        getattr(record, "status_code", None) == 200
        for record in caplog.records
    )

def test_health_preserves_supplied_request_id():
    with TestClient(app) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": "day-5-test-001"},
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "day-5-test-001"