
import logging
import re
import json
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import app
from app.logging_config import JSONFormatter
from app.middleware import RequestLoggingMiddleware

def test_inspect_middlewares():
    print("\n--- app.user_middleware (registration order) ---")
    for idx, mw in enumerate(app.user_middleware):
        print(f"{idx}: cls={mw.cls}, args={mw.args}, kwargs={mw.kwargs}")

    with TestClient(app):
        print("\n--- middleware_stack (outermost -> innermost execution order) ---")
        node = app.middleware_stack
        depth = 0
        seen_ids = set()
        while node is not None and id(node) not in seen_ids:
            seen_ids.add(id(node))
            print(f"{depth}: {type(node).__name__} ({node})")
            node = getattr(node, "app", None)
            depth += 1

def test_debug_request_id_header(monkeypatch):
    seen = {}
    orig_dispatch = RequestLoggingMiddleware.dispatch

    async def debug_dispatch(self, request, call_next):
        seen["header"] = request.headers.get("x-request-id")
        seen["all_headers"] = dict(request.headers)
        return await orig_dispatch(self, request, call_next)

    monkeypatch.setattr(RequestLoggingMiddleware, "dispatch", debug_dispatch)

    with TestClient(app) as client:
        response = client.get("/health", headers={"X-Request-ID": "test-123"})

    print("Seen header:", repr(seen.get("header")))
    print("Seen all headers:", seen.get("all_headers"))
    print("Response X-Request-ID:", response.headers.get("X-Request-ID"))

client = TestClient(app)

def test_request_id_generated():
    #with TestClient(app) as client:
    response = client.get("/health")

    request_id = response.headers["X-Request-ID"]

    assert re.fullmatch(
        r"[0-9a-f-]{36}",
        request_id,
    )

def test_invalid_request_id_replaced():
    #with TestClient(app) as client:
    response = client.get(
        "/health",
        headers={"X-Request-ID": "invalid id!"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "invalid id!"





def test_log_contain_correct_request_id(caplog):
    expected_request_id = "test-123"
    response = client.post(
    "/chat",
    headers={"X-Request-ID": expected_request_id},
    json={"message": "Hello"},
)



def test_request_logging(caplog):
    logger = logging.getLogger("app")

    logger.addHandler(caplog.handler)

    try:
        with TestClient(app) as client:
            response = client.get(
                "/health",
                headers={"X-Request-ID": "test-123"},
            )

        assert response.status_code == 200

        completed = [
            record
            for record in caplog.records
            if record.getMessage() == "request_completed"
        ]

        assert len(completed) == 1

    finally:
        logger.removeHandler(caplog.handler)


def test_json_formatter():
    formatter = JSONFormatter()

    record = logging.LogRecord(
        name="app.http",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )

    record.status_code = 200
    record.duration_ms = 15.5

    output = formatter.format(record)
    data = json.loads(output)

    assert data["event"] == "request_completed"
    assert data["level"] == "INFO"
    assert data["status_code"] == 200
    assert data["duration_ms"] == 15.5