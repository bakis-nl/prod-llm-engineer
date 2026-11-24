
import asyncio
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.llm.mock import  FakeClient
from app.llm.provider import APIProvider, ModelTimeoutError
import pytest

testclient = TestClient(app)


def test_health():
    response = testclient.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.fixture(autouse=True)
def use_mock_llm(monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")

def test_chat_success(monkeypatch):
 
    response = testclient.post(
        "/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["response"] == (
        "Mock response to: Hello"
    )


def test_empty_message():
    response = testclient.post(
        "/chat",
        json={"message": ""},
    )

    assert response.status_code == 422, response.text



def test_long_message():
    #base_text = "This is a repeated sentence. "
    #long_text = base_text * 4001  # Repeats the string 100 times
    response = testclient.post(
        "/chat",
        json={"message": "A" * 4001},
    )

    assert response.status_code == 422, response.text

def test_max_allowed_message():
    response = testclient.post(
        "/chat",
        json={"message": "A" * 4000},
    )

    assert response.status_code == 200

def test_session_id_preservation():
    # Send a request with a specific session_id
    test_session_id = "sess_abc123"
    
    response = testclient.post(
        "/chat",
        json={
            "message": "Hello, maintain my session!",
            "session_id": test_session_id
        },
    )

    # Assert the request succeeded
    assert response.status_code == 200, response.text
    
    data = response.json()
    
    # Assert that the session_id is preserved in the response
    assert data["session_id"] == test_session_id



class FakeLLMProvider:
    async def generate(self, prompt: str) -> str:
        return "Test response"

from app.dependencies import get_llm_provider

def test_dependency_override():
    def override_provider():
        return FakeLLMProvider()

    app.dependency_overrides[get_llm_provider] = override_provider

    try:
        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"message": "Hello"}
            )

        assert response.status_code == 200, response.text
        assert response.json()["response"] == "Test response"

    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
class ForwardLLMProvider:
    async def generate(self, prompt: str) -> str:
        return f"TEST PROVIDER: {prompt}"

def test_dependency_override_update():
    def override_provider():
        return ForwardLLMProvider()

    app.dependency_overrides[get_llm_provider] = override_provider

    try:
        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"message": "Hello"}
            )
        print("response", response.json()["response"])  
        assert response.status_code == 200, response.text
        assert response.json()["response"] == "TEST PROVIDER: Hello"
          
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)

def test_missing_session_id():
    response = testclient.post(
        "/chat",
        json={"message": "Start a new session"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["session_id"] is None



def test_api_provider_calls_client():
    client = FakeClient()
    client.complete = AsyncMock(return_value="Hello from the model")
    provider = APIProvider(model="Model-1", client=client)

    answer = asyncio.run(provider.generate("Hello"))

    assert answer == "Hello from the model"
    client.complete.assert_awaited_once_with(model="Model-1", prompt="Hello")

def test_api_provider_times_out():
    async def slow_complete(*, model: str, prompt: str) -> str:
        await asyncio.sleep(1)
        return "Hello from the model"

    client = FakeClient()
    client.complete = AsyncMock(side_effect=slow_complete)
    provider = APIProvider(
        model="Model-1",
        client=client,
        timeout_seconds=0.01,
    )

    with pytest.raises(ModelTimeoutError, match="Model API timed out"):
        asyncio.run(provider.generate("Hello"))


def test_chat_returns_504_when_model_times_out(monkeypatch):
    class TimeoutProvider:
        async def generate(self, prompt: str) -> str:
            raise ModelTimeoutError("Model API timed out")

    monkeypatch.setitem(
        app.dependency_overrides,
        get_llm_provider,
        TimeoutProvider,
    )
    
    response = testclient.post("/chat", json={"message": "Hello"})

    assert response.status_code == 504, response.text