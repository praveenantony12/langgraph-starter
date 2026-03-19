# langgraph-starter

A minimal, production-ready LangGraph starter project.
Copy this folder to start any new agentic app — the graph infrastructure,
HTTP API, tests, and CI/CD config are already in place.
All you add is business logic.

---

## What it does out of the box

```
[START] → echo_node → [END]
```

- **echo_node** — receives a message, calls the LLM chain, returns the reply

Locally it prints the response. On Render it serves it over HTTP at `/chat`.

---

## Project structure

```
langgraph-starter/
├── main.py                          ← entry point (local dev + Render)
├── pyproject.toml                   ← uv project config + dependencies
├── .python-version                  ← Python 3.11
├── .env.example                     ← copy to .env, add your key
├── render.yaml                      ← Render auto-deploy config
│
├── graph/                           ← all LangGraph logic lives here
│   ├── state.py                     ← AgentState TypedDict
│   ├── consts.py                    ← model name, node names, constants
│   ├── graph.py                     ← StateGraph wiring (pure structure)
│   ├── nodes/
│   │   ├── echo_node.py             ← starter node: read → call chain → write
│   │   └── test_nodes.py            ← node error-contract tests
│   ├── edges/
│   │   └── routing.py               ← all conditional routing functions
│   └── chains/
│       ├── llm_chain.py             ← all LLM calls go through here
│       └── tests/
│           └── test_llm_chain.py    ← unit + integration tests for LLM logic
│
├── api/
│   ├── runner.py                    ← run(message, thread_id) — graph API
│   └── server.py                    ← FastAPI app: GET /health, POST /chat
│
└── tests/
    ├── conftest.py                  ← shared fixtures for all tests
    ├── test_graph.py                ← full pipeline integration tests
    └── test_api.py                  ← runner + HTTP endpoint tests
```

---

## Prerequisites

- Python 3.11+
- uv — install once: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A Groq API key — free at https://console.groq.com

---

## Local setup

```bash
cd langgraph-starter
```

```bash
uv sync --group dev
```

```bash
cp .env.example .env
```

Open `.env` and set `GROQ_API_KEY=your_key_here`

```bash
uv run python main.py
```

---

## HTTP API (local)

```bash
PORT=8000 uv run python main.py
```

```bash
curl http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello! What can you do?"}'
```

---

## Running tests

```bash
uv run pytest -v -m unit
```

```bash
uv run pytest -v -m integration
```

```bash
uv run pytest -v
```

```bash
uv run pytest -v --cov=. --cov-report=term-missing
```

---

## Linting and type checking

```bash
uv run ruff check .
```

```bash
uv run ruff check . --fix
```

```bash
uv run mypy . --ignore-missing-imports
```

---

## CI/CD — GitHub Actions

The pipeline runs on every push and pull request:

```
lint → unit-tests (80% coverage gate) → integration-tests → build-check
```

Add one secret in GitHub:

```
Repository → Settings → Secrets → Actions → New repository secret
Name:  GROQ_API_KEY
Value: your_groq_api_key_here
```

Unit tests and the smoke test run without the secret.
Integration tests are skipped if the secret is absent.

---

## Deploying to Render

1. Push this repo to GitHub
2. Go to https://dashboard.render.com → New → Web Service → connect your repo
3. Render detects `render.yaml` automatically
4. Add one environment variable in Render dashboard → Environment:

```
Key:   GROQ_API_KEY
Value: your_groq_api_key_here
```

Render auto-deploys on every push to `main`.

After deploy, your endpoints are live at:

```
GET  https://your-app.onrender.com/health
POST https://your-app.onrender.com/chat
```

---

## Building your own app from this starter

```bash
# 1. Add your domain fields to state
#    edit graph/state.py

# 2. Write LLM logic as a chain
#    create graph/chains/my_chain.py
#    create graph/chains/tests/test_my_chain.py

# 3. Write a node that calls your chain  (copy echo_node.py)
#    create graph/nodes/my_node.py
#    add tests to graph/nodes/test_nodes.py

# 4. Add routing if the graph branches
#    edit graph/edges/routing.py

# 5. Wire it all together
#    edit graph/graph.py

# 6. Expose it via HTTP if needed
#    edit api/server.py

# 7. Add integration tests
#    edit tests/test_graph.py
```

---

## Switching models

Edit `graph/consts.py` — one line, applies everywhere:

```python
MODEL_NAME = "llama-3.3-70b-versatile"   # Groq (default, free tier)
MODEL_NAME = "llama-3.1-8b-instant"      # Groq (faster, smaller)
MODEL_NAME = "claude-sonnet-4-6"          # Anthropic (higher quality)
```
