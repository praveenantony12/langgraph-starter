"""
graph/consts.py — Graph-specific constants.

WHY THIS FILE EXISTS:
  There are two kinds of settings in any project:

  1. Application config  — API keys, ports, env vars.
     These are infrastructure concerns shared across the whole app.

  2. Graph constants — model name, prompts, node name strings,
     iteration limits, thresholds. These are specific to how THIS
     graph behaves and belong inside graph/ next to the code
     that uses them. (Eden Marco's insight, adopted here.)

  Keeping them separate means graph/ is self-contained — you can
  copy it into a new project and it carries its own constants.

HOW TO EXTEND:
  Add your own constants as you add nodes and chains:

    RETRIEVAL_K          = 4       # number of docs to retrieve (RAG)
    RELEVANCE_THRESHOLD  = 0.7     # grader cutoff score
    MAX_RETRIES          = 2       # regeneration attempts before giving up
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ── API keys ───────────────────────────────────────────────────────────────────
# Centralised here so all graph code imports from one place.
GROQ_API_KEY      = os.environ.get("GROQ_API_KEY",      "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── LLM ────────────────────────────────────────────────────────────────────────
# Change MODEL_NAME here and every node/chain picks it up automatically.
MODEL_NAME  = os.environ.get("MODEL_NAME",  "llama-3.3-70b-versatile")
MAX_TOKENS  = int(os.environ.get("MAX_TOKENS",  "1024"))
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))

# ── Graph behaviour ────────────────────────────────────────────────────────────
# Maximum times a looping node runs before routing forces an exit.
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "5"))

# ── Developer experience ───────────────────────────────────────────────────────
VERBOSE = os.environ.get("VERBOSE", "true").lower() == "true"

# ── Node name strings ──────────────────────────────────────────────────────────
# Single source of truth for node names used in graph.py and routing.py.
# Prevents typos from repeating string literals in multiple places.
ECHO_NODE = "echo_node"
