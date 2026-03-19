"""
graph/chains/tests/test_llm_chain.py — Unit tests for llm_chain.py.

WHY ARE TESTS CO-LOCATED INSIDE chains/?
  Eden Marco places tests next to the code they test — specifically
  inside the chains/ folder. This is the "co-location" pattern:

    graph/chains/llm_chain.py        ← the implementation
    graph/chains/tests/              ← tests for that implementation

  The reasoning:
  - chains/ contains the concentrated LLM logic worth unit-testing
  - When you open graph/chains/, you immediately see the tests
  - When you delete a chain, the tests travel with it — no orphans
  - Nodes are thin wrappers; chains are where the logic lives

  We adopt this for chains/ but NOT for nodes/ (which are too thin
  to warrant co-located tests) and NOT for edges/ (routing functions
  are tested at the integration level via test_graph.py).

  Root-level tests/ handles graph integration and api layer tests.

MARKS:
  @pytest.mark.unit        — no real LLM call (mock_llm fixture)
  @pytest.mark.integration — real LLM call (requires GROQ_API_KEY)

RUN JUST THESE:
  pytest graph/chains/tests/ -v
  pytest graph/chains/tests/ -v -m unit
"""

import os
from unittest.mock import patch

import pytest

# ── Unit tests (mocked LLM — no API key needed) ───────────────────────────────

@pytest.mark.unit
class TestCallLlmUnit:

    def test_returns_string(self, mock_llm_chain):
        """call_llm must always return a plain string."""
        from graph.chains.llm_chain import call_llm
        result = call_llm(system="You are helpful.", user="Hello")
        assert isinstance(result, str)

    def test_returns_mocked_value(self, mock_llm_chain):
        """Return value comes from the mock, not the real API."""
        from graph.chains.llm_chain import call_llm
        mock_llm_chain.return_value = "Mocked chain reply."
        result = call_llm(system="sys", user="user")
        assert result == "Mocked chain reply."

    def test_passes_system_prompt(self, mock_llm_chain):
        """call_llm forwards the system argument to the Groq client."""
        from graph.chains.llm_chain import call_llm
        call_llm(system="Custom system prompt.", user="question")
        call_args = mock_llm_chain.call_args
        messages = call_args.kwargs.get("messages") or call_args.args[0]
        system_msg = next(m for m in messages if m["role"] == "system")
        assert system_msg["content"] == "Custom system prompt."

    def test_passes_user_prompt(self, mock_llm_chain):
        """call_llm forwards the user argument to the Groq client."""
        from graph.chains.llm_chain import call_llm
        call_llm(system="sys", user="My specific question.")
        call_args = mock_llm_chain.call_args
        messages = call_args.kwargs.get("messages") or call_args.args[0]
        user_msg = next(m for m in messages if m["role"] == "user")
        assert "My specific question." in user_msg["content"]

    def test_raises_when_api_key_missing(self):
        """call_llm must raise RuntimeError if GROQ_API_KEY is not set."""
        with patch("graph.chains.llm_chain.GROQ_API_KEY", ""):
            from graph.chains.llm_chain import call_llm
            with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
                call_llm(system="sys", user="hello")

    def test_strips_whitespace_from_response(self, mock_llm_chain):
        """Responses with leading/trailing whitespace are stripped."""
        from graph.chains.llm_chain import call_llm
        mock_llm_chain.return_value = "  reply with spaces  "
        result = call_llm(system="sys", user="q")
        assert result == "reply with spaces"


# ── Integration tests (real LLM call) ─────────────────────────────────────────

@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping real LLM test",
)
class TestCallLlmIntegration:

    def test_real_call_returns_non_empty_string(self):
        """Real API call must return a non-empty string."""
        from graph.chains.llm_chain import call_llm
        result = call_llm(
            system="You are a helpful assistant.",
            user="Reply with exactly the word: hello",
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_real_call_respects_system_prompt(self):
        """The LLM should follow a simple instruction in the system prompt."""
        from graph.chains.llm_chain import call_llm
        result = call_llm(
            system="Always reply with exactly the word PONG and nothing else.",
            user="PING",
            temperature=0.0,
        )
        assert "PONG" in result.upper()
