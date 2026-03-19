"""
api/server.py — FastAPI HTTP server.

WHY THIS FILE EXISTS:
  Render (and every other PaaS) requires a process that binds to $PORT.
  main.py detects the PORT env var and routes to this file automatically.
  Locally you run main.py directly; on Render this file serves requests.

ENDPOINTS:
  GET  /          → health check, confirms the service is alive
  GET  /health    → same, explicit health endpoint for Render's health check
  POST /chat      → invoke the graph with a message, return the response

HOW TO TEST LOCALLY:
  PORT=8000 uv run python main.py
  curl http://localhost:8000/health
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello!"}'

WHEN YOU BUILD YOUR OWN APP:
  Add your own endpoints here. The graph is invoked via api/runner.py —
  keep all HTTP routing in this file and all graph logic in runner.py.
"""

import os
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from api.runner import run

app = FastAPI(
    title="langgraph-starter",
    description="A minimal LangGraph API",
    version="0.1.0",
)


# ── Request / response models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    thread_id: str
    error: str | None = None


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Root endpoint — confirms the service is running."""
    return {"status": "ok", "service": "langgraph-starter"}


@app.get("/health")
async def health():
    """Health check endpoint — Render pings this to confirm liveness."""
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    """
    Invoke the LangGraph pipeline with a user message.

    Returns the agent's response and the thread_id used.
    Pass the same thread_id in subsequent requests to continue
    a conversation (the graph checkpointer keeps state per thread).
    """
    thread_id = body.thread_id or str(uuid.uuid4())

    result = run(body.message, thread_id=thread_id)

    if result.get("error"):
        # Return 200 with the error in the body — the graph ran, it just
        # encountered an error. Use 500 only for unhandled server crashes.
        return ChatResponse(
            response="",
            thread_id=thread_id,
            error=result["error"],
        )

    return ChatResponse(
        response=result.get("response", ""),
        thread_id=thread_id,
    )


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    """Called by main.py when PORT env var is detected."""
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
