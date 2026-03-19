"""
api/runner.py — Public invocation interface for the graph.

This is the single place that knows how to invoke the graph.
Both main.py and the test suite call run() from here.

Adding an HTTP endpoint later is then one function call:
    @app.post("/chat")
    async def chat(body: ChatRequest):
        return run(body.message, thread_id=body.session_id)
"""

import uuid

from graph.graph import build_graph
from graph.state import AgentState

# Built once at import time. All mutable state lives in the MemorySaver
# checkpointer, not here, so this is safe and cheap.
_app = build_graph()


def run(user_message: str, thread_id: str | None = None) -> AgentState:
    """
    Invoke the full graph with a user message.

    Args:
        user_message: The input text.
        thread_id:    Conversation thread identifier. Auto-generated if None.

    Returns:
        Final AgentState. Access the reply with result["response"].
    """
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    initial_state: AgentState = {
        "user_message": user_message,
        "response":     "",
        "iteration":    0,
        "error":        None,
    }

    return _app.invoke(
        initial_state,
        config={"configurable": {"thread_id": thread_id}},
    )
