"""
tests/test_graph.py — Integration tests for the full graph pipeline.

WHAT THESE TEST:
  The graph as a whole — does it compile, wire, and run correctly?
  Does state flow through correctly from input to output?
  Do errors propagate cleanly without crashing the graph?

  These complement the co-located chain tests in graph/chains/tests/.
  Chain tests verify the LLM logic in isolation.
  Graph tests verify the plumbing that connects everything.

RUN:
  pytest tests/test_graph.py -v
  pytest tests/ -v -m integration
"""

import os
from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestGraphCompilation:

    def test_builds_without_error(self):
        from graph.graph import build_graph
        assert build_graph() is not None

    def test_compiled_graph_is_invokable(self):
        from graph.graph import build_graph
        assert callable(getattr(build_graph(), "invoke", None))


@pytest.mark.integration
class TestFullPipelineMocked:

    def test_response_present_on_success(self, mock_call_llm):
        from api.runner import run
        mock_call_llm.return_value = "Mocked reply."
        result = run("Hello")
        assert result["response"] == "Mocked reply."
        assert result["error"] is None

    def test_user_message_preserved_in_final_state(self, mock_call_llm):
        from api.runner import run
        result = run("Preserve this.")
        assert result["user_message"] == "Preserve this."

    def test_empty_message_does_not_crash(self, mock_call_llm):
        from api.runner import run
        result = run("")
        assert "response" in result

    def test_llm_error_captured_in_state(self, mock_call_llm_error):
        from api.runner import run
        result = run("This will fail.")
        assert result["error"] is not None
        assert "LLM call failed" in result["error"]
        assert result["response"] == ""

    def test_independent_threads_do_not_share_state(self):
        with patch("graph.nodes.echo_node.call_llm", return_value="Reply A"):
            from api.runner import run
            r1 = run("Message A", thread_id="t-a")
        with patch("graph.nodes.echo_node.call_llm", return_value="Reply B"):
            r2 = run("Message B", thread_id="t-b")
        assert r1["response"] == "Reply A"
        assert r2["response"] == "Reply B"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set — skipping real LLM test",
)
class TestFullPipelineReal:

    def test_real_response_is_non_empty(self):
        from api.runner import run
        result = run("Reply with exactly the word: hello")
        assert result.get("response")
        assert result.get("error") is None

    def test_real_response_is_string(self):
        from api.runner import run
        assert isinstance(run("What is 1+1?").get("response"), str)
