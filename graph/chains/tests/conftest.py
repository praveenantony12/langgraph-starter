"""
Pytest fixtures scoped to chain unit tests.

This folder is intentionally isolated from `tests/conftest.py` so that
`mock_llm_chain` is available when running:
  pytest graph/chains/tests/ -v -m unit
"""

from unittest.mock import patch

import pytest


@pytest.fixture
def mock_llm_chain():
    """
    Patches the Groq client's `create()` call.

    Unit tests treat the mocked return value as a plain string, so the
    default mock return is a string (tests can override `return_value`).
    """

    with patch("graph.chains.llm_chain._client.chat.completions.create") as mock:
        mock.return_value = "Mocked LLM reply."
        yield mock

