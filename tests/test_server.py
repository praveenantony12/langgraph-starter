"""
tests/test_server.py — Tests for the FastAPI HTTP endpoints.

WHAT THESE TEST:
  The HTTP contract — status codes, response shapes, and that the
  /health and /chat endpoints behave correctly.

  Uses FastAPI's TestClient (backed by httpx) so no real server
  needs to be running. The LLM is mocked so no API key is needed.

RUN:
  pytest tests/test_server.py -v
"""


import pytest
from fastapi.testclient import TestClient

from api.server import app

client = TestClient(app)


@pytest.mark.unit
class TestHealthEndpoints:

    def test_root_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_status_ok(self):
        data = client.get("/").json()
        assert data["status"] == "ok"

    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy(self):
        data = client.get("/health").json()
        assert data["status"] == "healthy"


@pytest.mark.unit
class TestChatEndpoint:

    def test_chat_returns_200_on_success(self, mock_call_llm):
        mock_call_llm.return_value = "Hello! I can help you."
        response = client.post("/chat", json={"message": "Hello!"})
        assert response.status_code == 200

    def test_chat_returns_response_field(self, mock_call_llm):
        mock_call_llm.return_value = "Here is my reply."
        data = client.post("/chat", json={"message": "Hi"}).json()
        assert data["response"] == "Here is my reply."

    def test_chat_returns_thread_id(self, mock_call_llm):
        data = client.post("/chat", json={"message": "Hi"}).json()
        assert "thread_id" in data
        assert len(data["thread_id"]) > 0

    def test_chat_accepts_explicit_thread_id(self, mock_call_llm):
        data = client.post("/chat", json={
            "message": "Hi",
            "thread_id": "my-session-123"
        }).json()
        assert data["thread_id"] == "my-session-123"

    def test_chat_error_captured_not_500(self, mock_call_llm_error):
        """LLM failure returns 200 with error field, not a 500 crash."""
        data = client.post("/chat", json={"message": "Hi"}).json()
        assert "error" in data
        assert data["error"] is not None
        assert data["response"] == ""

    def test_chat_missing_message_returns_422(self):
        """FastAPI validates the request body — missing message = 422."""
        response = client.post("/chat", json={})
        assert response.status_code == 422
