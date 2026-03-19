"""
graph/edges/routing.py — All conditional routing functions.

THE RULE: routing functions never do work.
  They only read state and return a node name string.
  All logic lives in nodes and chains.

THE PATTERN:
  def route_after_X(state: AgentState) -> str:
      if state.get("needs_retry"):
          return "echo_node"      # loop back
      return END                  # finish

  Wired in graph.py:
      graph.add_conditional_edges("x_node", route_after_x, {
          "echo_node": "echo_node",
          END: END,
      })

TO ADD YOUR OWN ROUTING:
  Add a new function below following the same pattern.
  Name it route_after_<source_node_name>.
"""

from langgraph.graph import END

from graph.consts import MAX_ITERATIONS, VERBOSE
from graph.state import AgentState


def route_after_echo(state: AgentState) -> str:
    """
    Routing function called after echo_node.

    Current logic (single-node linear graph):
      error present      → END
      max iterations hit → END
      success            → END

    Replace with real routing as your graph grows:
      if state.get("grade") == "bad":      return "echo_node"   # retry
      if state.get("needs_search"):        return "search_node"
      if state.get("tool_call"):           return "tool_node"
    """
    if state.get("error"):
        if VERBOSE:
            print("\n🔀 [router] Error detected → END")
        return END

    if state.get("iteration", 0) >= MAX_ITERATIONS:
        if VERBOSE:
            print("\n🔀 [router] Max iterations reached → END")
        return END

    if VERBOSE:
        print("\n🔀 [router] Response complete → END")
    return END
