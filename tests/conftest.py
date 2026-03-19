"""
tests/conftest.py — Shared pytest fixtures (available to all tests).

Fixtures defined here are automatically available to:
  tests/              (root integration tests)
  graph/chains/tests/ (co-located chain tests)

No import needed in test files — pytest discovers them by convention.
"""

from unittest.mock import patch

import pytest

from graph.state import AgentState

# ── State fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def minimal_state() -> AgentState:
    """Minimal valid state — just a user message."""
    return AgentState(
        user_message="Hello, world!",
        response="",
        iteration=0,
        error=None,
    )


@pytest.fixture
def state_with_error() -> AgentState:
    """State where a previous node set an error."""
    return AgentState(
        user_message="Hello",
        response="",
        iteration=0,
        error="Something went wrong.",
    )


@pytest.fixture
def state_at_max_iterations() -> AgentState:
    """State where the iteration cap has been reached."""
    from graph.consts import MAX_ITERATIONS
    return AgentState(
        user_message="Loop",
        response="",
        iteration=MAX_ITERATIONS,
        error=None,
    )


# ── LLM mock fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def mock_llm_chain():
    """
    Patches the Groq client create() call — no real API call made.
    Used by both chain unit tests and graph integration tests.

    Usage:
        def test_something(mock_llm_chain):
            mock_llm_chain.return_value = "Mocked reply."
    """
    with patch(
        "graph.chains.llm_chain._client.chat.completions.create"
    ) as mock:
        mock.return_value.choices[0].message.content = "Mocked LLM reply."
        yield mock


@pytest.fixture
def mock_call_llm():
    """
    Patches call_llm directly — simpler to use in node tests.

    Usage:
        def test_something(mock_call_llm):
            mock_call_llm.return_value = "Reply."
    """
    with patch("graph.nodes.echo_node.call_llm") as mock:
        mock.return_value = "Mocked reply."
        yield mock


@pytest.fixture
def mock_call_llm_error():
    """Patches call_llm to raise — tests error-handling paths."""
    with patch("graph.nodes.echo_node.call_llm") as mock:
        mock.side_effect = Exception("Simulated API failure")
        yield mock
