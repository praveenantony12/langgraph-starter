"""
tests/conftest.py — Shared pytest fixtures (available to all tests).

Fixtures defined here are automatically available to:
  tests/              (root integration tests)
  graph/chains/tests/ (co-located chain tests)
  graph/nodes/        (node tests)

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
    Patches call_llm() directly so no real API call is ever made.

    Used by chain unit tests AND graph integration tests.
    Default return value is "Mocked LLM reply." — override in each test:

        def test_something(mock_llm_chain):
            mock_llm_chain.return_value = "My specific reply."

    WHY patch call_llm and not _client.chat.completions.create?
      Patching at the Groq client level requires carefully constructing
      a mock with .choices[0].message.content set up — and it breaks
      the moment you swap Groq for Anthropic. Patching call_llm() tests
      the behaviour (what the chain returns) not the implementation
      (how it calls Groq internally). That's the right boundary.
    """
    with patch("graph.chains.llm_chain.call_llm") as mock:
        mock.return_value = "Mocked LLM reply."
        yield mock


@pytest.fixture
def mock_call_llm():
    """
    Patches call_llm in echo_node — used by node tests and graph tests.

        def test_something(mock_call_llm):
            mock_call_llm.return_value = "Reply."
    """
    with patch("graph.nodes.echo_node.call_llm") as mock:
        mock.return_value = "Mocked reply."
        yield mock


@pytest.fixture
def mock_call_llm_error():
    """Patches call_llm in echo_node to raise — tests error-handling paths."""
    with patch("graph.nodes.echo_node.call_llm") as mock:
        mock.side_effect = Exception("Simulated API failure")
        yield mock
