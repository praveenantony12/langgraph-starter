"""
graph/nodes/echo_node.py — The starter node.

PURPOSE OF THIS FILE:
  This is the template you copy every time you need a new node.
  It demonstrates the exact pattern used in every real LangGraph app:

      read from state → call a chain → write result back to state

  That's it. That's the whole pattern. Every node you'll ever write
  is a variation of this.

WHAT IT DOES:
  Receives a message, calls the LLM chain, stores the reply.
  No greeting logic, no multi-step formatting — just the raw pattern.

HOW TO BUILD YOUR OWN NODE FROM THIS:
  1. Copy this file:         cp echo_node.py my_node.py
  2. Rename the function:    def my_node(state: AgentState)
  3. Read your inputs:       value = state.get("my_input_field")
  4. Call your chain:        result = my_chain(value)
  5. Write your outputs:     return {**state, "my_output_field": result}
  6. Register in graph.py:   graph.add_node("my_node", my_node)
  7. Wire an edge:           graph.add_edge("previous_node", "my_node")

WHY NODES DON'T HAVE CO-LOCATED TESTS:
  Nodes are intentionally thin — their only job is to read state,
  call a chain, and write state back. The logic worth testing lives
  in the chain (graph/chains/), which has its own tests/ folder.
  Nodes are covered by the full-pipeline tests in tests/test_graph.py.

  If a node grows complex enough that you want to test it in isolation,
  that complexity should move into a chain.
"""

from graph.chains.llm_chain import call_llm
from graph.consts import VERBOSE
from graph.state import AgentState


def echo_node(state: AgentState) -> AgentState:
    """
    Calls the LLM with the user's message and stores the reply.

    Reads:   state["user_message"]
    Writes:  state["response"]
             state["error"]      — set if the LLM call fails

    Replace the contents of this function with your own logic.
    Keep the signature (takes AgentState, returns AgentState) unchanged.
    """
    if VERBOSE:
        print("\n💬 [echo_node] Calling LLM chain...")

    user_message = (state.get("user_message") or "").strip()

    if not user_message:
        error = "echo_node: user_message is empty."
        if VERBOSE:
            print(f"   ❌ {error}")
        return {**state, "response": "", "error": error}

    try:
        response = call_llm(
            system="You are a helpful assistant. Reply concisely.",
            user=user_message,
        )

        if VERBOSE:
            preview = response[:80] + "..." if len(response) > 80 else response
            print(f"   ✅ response = '{preview}'")

        return {**state, "response": response, "error": None}

    except Exception as exc:
        # Always catch exceptions in nodes and write to state["error"].
        # This keeps the graph alive — the routing function decides what
        # to do next rather than the whole invocation crashing.
        error = f"LLM call failed: {exc}"
        if VERBOSE:
            print(f"   ❌ {error}")
        return {**state, "response": "", "error": error}
