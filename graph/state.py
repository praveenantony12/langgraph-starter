"""
graph/state.py — The shared AgentState TypedDict.

WHY STATE LIVES INSIDE graph/:
  State is a LangGraph concept — it describes what flows between nodes.
  It belongs here next to the code that uses it, not at the project root.
  (Eden Marco's structural insight, adopted here.)

THE PATTERN:
  Every field has a clear owner:
    user_message  — set by the caller (main.py / runner.py) before invoke
    response      — set by the node that calls the LLM
    iteration     — incremented by looping nodes, read by routing functions
    error         — set by any node that catches an exception

HOW TO EXTEND FOR YOUR OWN APP:
  Add your domain fields below. Examples:

    # RAG
    documents:     List[str]
    generation:    str

    # Tool use / ReAct
    tool_calls:    List[dict]
    tool_results:  List[dict]

    # Multi-agent
    next_agent:    str

    # Classification / grading
    grade:         str      # "relevant" | "irrelevant"
    needs_rewrite: bool
"""

from typing import Optional, TypedDict


class AgentState(TypedDict, total=False):

    # ── Input ─────────────────────────────────────────────────────────────────
    # The raw message or request entering the graph.
    # Set once before graph.invoke() — nodes read it, never overwrite it.
    user_message: str

    # ── Output ────────────────────────────────────────────────────────────────
    # The final reply produced by the LLM node.
    response: str

    # ── Control ───────────────────────────────────────────────────────────────
    # Counts how many times a looping node has run.
    # Routing functions compare this against consts.MAX_ITERATIONS.
    iteration: int

    # Set by any node that catches an exception.
    # Routing can check this to short-circuit to an error handler node.
    error: Optional[str]
