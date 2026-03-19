"""
graph/nodes/test_nodes.py — Lightweight tests for node behaviour.

WHY THIS FILE EXISTS HERE:
  This is a deliberate middle ground between two approaches:
    - Eden's pattern: no node tests (nodes are too thin)
    - Having no coverage of node error-handling paths at all

  Nodes are thin, but they do own one important piece of logic:
  the error-handling contract. When call_llm raises, does the node
  write to state["error"] correctly? Does it return a dict rather
  than re-raising? That's worth a fast, mocked test.

  These tests run in milliseconds with no LLM calls — they just
  verify the node's error contract.

WHAT IS NOT TESTED HERE:
  - Whether the LLM response is good (that's a chain test)
  - Whether the graph routes correctly (that's test_graph.py)
  - Whether the API layer works (that's test_api.py)

RUN JUST THESE:
  pytest graph/nodes/test_nodes.py -v
"""

from unittest.mock import patch

import pytest

from graph.state import AgentState


@pytest.mark.unit
class TestEchoNode:

    def test_stores_llm_reply_in_response(self):
        from graph.nodes.echo_node import echo_node
        with patch("graph.nodes.echo_node.call_llm", return_value="Hello back."):
            result = echo_node(AgentState(user_message="Hello", iteration=0))
        assert result["response"] == "Hello back."
        assert result["error"] is None

    def test_empty_message_sets_error_without_calling_llm(self):
        from graph.nodes.echo_node import echo_node
        with patch("graph.nodes.echo_node.call_llm") as mock_llm:
            result = echo_node(AgentState(user_message="", iteration=0))
        mock_llm.assert_not_called()
        assert result["error"] is not None
        assert result["response"] == ""

    def test_llm_exception_captured_in_error_field(self):
        from graph.nodes.echo_node import echo_node
        with patch("graph.nodes.echo_node.call_llm", side_effect=Exception("boom")):
            result = echo_node(AgentState(user_message="Hi", iteration=0))
        assert "LLM call failed" in result["error"]
        assert result["response"] == ""

    def test_returns_dict_not_raises(self):
        """Node must never raise — always return state with error field set."""
        from graph.nodes.echo_node import echo_node
        with patch("graph.nodes.echo_node.call_llm", side_effect=RuntimeError("crash")):
            result = echo_node(AgentState(user_message="Hi", iteration=0))
        assert isinstance(result, dict)

    def test_other_state_fields_preserved(self):
        from graph.nodes.echo_node import echo_node
        with patch("graph.nodes.echo_node.call_llm", return_value="OK"):
            result = echo_node(AgentState(
                user_message="Hi", response="", iteration=2, error=None
            ))
        assert result["user_message"] == "Hi"
        assert result["iteration"] == 2
