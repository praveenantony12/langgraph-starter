"""
tests/test_api.py — Tests for api/runner.py.

Verifies the public contract of run() — the boundary between the graph
and the outside world.

RUN:
  pytest tests/test_api.py -v
"""

from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestRunner:

    def test_returns_dict(self, mock_call_llm):
        from api.runner import run
        assert isinstance(run("Test"), dict)

    def test_required_keys_present(self, mock_call_llm):
        from api.runner import run
        result = run("Check keys")
        for key in ("user_message", "response", "iteration"):
            assert key in result, f"Missing key: {key}"

    def test_user_message_preserved(self, mock_call_llm):
        from api.runner import run
        msg = "Preserve this exact string."
        assert run(msg)["user_message"] == msg

    def test_explicit_thread_id_accepted(self, mock_call_llm):
        from api.runner import run
        assert run("With thread", thread_id="explicit-42") is not None

    def test_auto_thread_id_when_none_given(self, mock_call_llm):
        from api.runner import run
        assert run("No thread") is not None

    def test_sequential_runs_independent(self):
        with patch("graph.nodes.echo_node.call_llm", return_value="First"):
            from api.runner import run
            r1 = run("A", thread_id="seq-1")
        with patch("graph.nodes.echo_node.call_llm", return_value="Second"):
            r2 = run("B", thread_id="seq-2")
        assert r1["response"] == "First"
        assert r2["response"] == "Second"
