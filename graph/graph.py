"""
graph/graph.py — Builds and compiles the LangGraph StateGraph.

THIS FILE IS PURE STRUCTURE — no logic, no LLM calls, no decisions.
  Nodes  → registered here
  Edges  → wired here
  Logic  → lives in graph/chains/ and graph/nodes/
  Routing decisions → live in graph/edges/routing.py

TO ADD A NEW NODE:
  1. Create graph/nodes/my_node.py
  2. Import it:  from graph.nodes.my_node import my_node
  3. Register:   graph.add_node("my_node", my_node)
  4. Wire edges: graph.add_edge(ECHO_NODE, "my_node")
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from graph.consts import ECHO_NODE
from graph.edges.routing import route_after_echo
from graph.nodes.echo_node import echo_node
from graph.state import AgentState


def build_graph():
    """
    Constructs and compiles the agent graph.

    Returns a compiled LangGraph app ready for .invoke() calls.

    MemorySaver keeps state in RAM per thread_id — perfect for local dev.
    For persistence across restarts swap to SqliteSaver or PostgresSaver.
    The rest of the code stays identical.
    """
    graph = StateGraph(AgentState)

    # ── Nodes ──────────────────────────────────────────────────────────────────
    graph.add_node(ECHO_NODE, echo_node)

    # ── Entry point ────────────────────────────────────────────────────────────
    graph.set_entry_point(ECHO_NODE)

    # ── Edges ──────────────────────────────────────────────────────────────────
    graph.add_conditional_edges(
        ECHO_NODE,
        route_after_echo,
        {END: END},
    )

    # ── Compile ────────────────────────────────────────────────────────────────
    return graph.compile(checkpointer=MemorySaver())
