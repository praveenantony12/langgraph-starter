# langgraph-starter

A minimal, production-ready LangGraph starter project.
Copy this folder to start any new agentic app — the graph infrastructure,
tests, and CI/CD config are already in place. All you add is business logic.

---

## What it does out of the box

```
[START] → greet_node → respond_node → [END]
```

- **greet_node** — formats the user message (no LLM)
- **respond_node** — calls the LLM chain and returns the reply

---

## Project structure

```
langgraph-starter/
├── main.py                          ← entry point
├── pyproject.toml                   ← uv project config + dependencies
├── .python-version                  ← Python 3.11
├── .env.example                     ← copy to .env, add your key
├── render.yaml                      ← Render auto-deploy config
│
├── graph/                           ← all LangGraph logic lives here
│   ├── state.py                     ← AgentState TypedDict
│   ├── consts.py                    ← model name, prompts, node names
│   ├── graph.py                     ← StateGraph wiring (pure structure)
│   ├── nodes/
│   │   ├── greet_node.py            ← thin orchestrator, no LLM
│   │   └── respond_node.py          ← thin orchestrator, calls chain
│   ├── edges/
│   │   └── routing.py               ← all conditional routing functions
│   └── chains/
│       ├── llm_chain.py             ← LLM logic (all LLM calls go here)
│       └── tests/                   ← co-located tests for chains
│           └── test_llm_chain.py
│
├── api/
│   └── runner.py                    ← run(message, thread_id) — public API
│
└── tests/                           ← integration + api tests
    ├── conftest.py                  ← shared fixtures (available everywhere)
    ├── test_graph.py                ← full pipeline integration tests
    └── test_api.py                  ← runner layer tests
```

### Why this structure?

- `graph/state.py` and `graph/consts.py` live inside `graph/` — state and
  constants are graph concepts, not application concepts (Eden Marco's insight)
- `graph/chains/tests/` — tests live next to chain logic because that's where
  the LLM logic is concentrated (co-location pattern)
- `tests/` at root — integration and api tests follow Python CI convention
- `graph/edges/` — routing functions get their own folder so `graph.py` stays
  pure structure and routing stays independently readable

---

## Prerequisites

- Python 3.11+
- uv — install it once: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A Groq API key — free at https://console.groq.com

---

## Local setup

```bash
cd langgraph-starter
```

```bash
uv sync
```

```bash
uv sync --extra dev
```

```bash
cp .env.example .env
```

Open `.env` and set `GROQ_API_KEY=your_key_here`

```bash
uv run python main.py
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

Run only the co-located chain tests:

```bash
uv run pytest graph/chains/tests/ -v
```

Run only the root integration tests:

```bash
uv run pytest tests/ -v
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

The pipeline runs automatically on every push and pull request.

```
lint → unit-tests (80% coverage gate) → integration-tests → build-check
```

Add this one secret in GitHub before pushing:

```
Repository → Settings → Secrets and variables → Actions → New repository secret
Name:  GROQ_API_KEY
Value: your_groq_api_key_here
```

Unit tests and the smoke test run without the secret.
Integration tests are skipped automatically if the secret is absent.

---

## Deploying to Render

```bash
# Push this repo to GitHub first, then:
```

1. Go to https://dashboard.render.com
2. New → Web Service → connect your GitHub repo
3. Render detects `render.yaml` automatically

```
Build command:  curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="/opt/render/.local/bin:$PATH" && uv sync --group dev
Start command:  ./.venv/bin/python main.py
```

Add one environment variable in the Render dashboard:

```
Key:   GROQ_API_KEY
Value: your_groq_api_key_here
```

Render auto-deploys on every push to `main` after that.

---

## Building your own app from this starter

```bash
# 1. Add your domain fields
#    edit graph/state.py

# 2. Add your LLM logic as chains
#    create graph/chains/my_chain.py
#    create graph/chains/tests/test_my_chain.py

# 3. Add nodes that call your chains
#    create graph/nodes/my_node.py

# 4. Add routing if needed
#    edit graph/edges/routing.py

# 5. Wire everything together
#    edit graph/graph.py

# 6. Add integration tests
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
