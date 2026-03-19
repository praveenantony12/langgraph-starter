"""
graph/chains/tests/test_llm_chain.py — Unit tests for llm_chain.py.

WHAT THESE TEST:
  The behaviour of call_llm() — what it returns, how it handles errors,
  what it does when the API key is missing.

WHAT THESE DO NOT TEST:
  The Groq client's internal call structure (messages format, model param).
  That's implementation detail — it breaks whenever you swap LLM providers.
  Test behaviour, not implementation.

MARKS:
  @pytest.mark.unit        — no real LLM call, runs offline
  @pytest.mark.integration — real LLM call, requires GROQ_API_KEY

RUN:
  pytest graph/chains/tests/ -v
  pytest graph/chains/tests/ -v -m unit
"""

import os
from unittest.mock import patch

import pytest

# ── Unit tests — mock the Groq client at the lowest possible level ─────────────
# We patch _client.chat.completions.create and build a proper mock response
# object so call_llm's internal .choices[0].message.content.strip() works.


def _make_groq_response(content: str):
    """Build a minimal mock that mirrors the Groq response structure."""
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.choices[0].message.content = content
    return mock_response


@pytest.mark.unit
class TestCallLlmUnit:

    def test_returns_string(self):
        """call_llm must always return a plain string."""
        from graph.chains.llm_chain import call_llm

        with patch(
            "graph.chains.llm_chain._client.chat.completions.create",
            return_value=_make_groq_response("hello"),
        ):
            result = call_llm(system="You are helpful.", user="Hello")
        assert isinstance(result, str)

    def test_returns_llm_content(self):
        """call_llm returns the content string from the LLM response."""
        from graph.chains.llm_chain import call_llm

        with patch(
            "graph.chains.llm_chain._client.chat.completions.create",
            return_value=_make_groq_response("Paris"),
        ):
            result = call_llm(system="sys", user="Capital of France?")
        assert result == "Paris"

    def test_strips_whitespace_from_response(self):
        """Responses with leading/trailing whitespace are stripped."""
        from graph.chains.llm_chain import call_llm

        with patch(
            "graph.chains.llm_chain._client.chat.completions.create",
            return_value=_make_groq_response("  reply with spaces  "),
        ):
            result = call_llm(system="sys", user="q")
        assert result == "reply with spaces"

    def test_raises_when_api_key_missing(self):
        """call_llm must raise RuntimeError if GROQ_API_KEY is not set."""
        with patch("graph.chains.llm_chain.GROQ_API_KEY", ""):
            from graph.chains import llm_chain

            with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
                llm_chain.call_llm(system="sys", user="hello")

    def test_groq_client_is_called_once(self):
        """call_llm must call the Groq client exactly once per invocation."""
        from graph.chains.llm_chain import call_llm

        with patch(
            "graph.chains.llm_chain._client.chat.completions.create",
            return_value=_make_groq_response("ok"),
        ) as mock_create:
            call_llm(system="sys", user="user")
        mock_create.assert_called_once()

    def test_groq_exception_propagates(self):
        """Exceptions from the Groq client propagate to the caller."""
        from graph.chains.llm_chain import call_llm

        with patch(
            "graph.chains.llm_chain._client.chat.completions.create",
            side_effect=Exception("rate limit hit"),
        ):
            with pytest.raises(Exception, match="rate limit hit"):
                call_llm(system="sys", user="user")

    def test_none_content_returns_empty_string(self):
        """When model returns None content (e.g. content filter), return empty string."""
        from graph.chains.llm_chain import call_llm

        mock_resp = MagicMock()
        mock_resp.choices[0].message.content = None
        with patch(
            "graph.chains.llm_chain._client.chat.completions.create",
            return_value=mock_resp,
        ):
            result = call_llm(system="sys", user="user")
        assert result == ""
        assert isinstance(result, str)


# ── Integration tests — real LLM call ─────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping real LLM test",
)
class TestCallLlmIntegration:

    def test_real_call_returns_non_empty_string(self):
        """End-to-end: the real Groq API must return a non-empty string."""
        from graph.chains.llm_chain import call_llm

        result = call_llm(
            system="You are a helpful assistant.",
            user="Reply with exactly the word: hello",
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_real_call_respects_system_prompt(self):
        """The LLM should follow a clear instruction in the system prompt."""
        from graph.chains.llm_chain import call_llm

        result = call_llm(
            system="Always reply with exactly the word PONG and nothing else.",
            user="PING",
            temperature=0.0,
        )
        assert "PONG" in result.upper()
