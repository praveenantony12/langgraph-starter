"""
graph/chains/llm_chain.py — Reusable LLM call wrapper.

WHY CHAINS, NOT NODES?
  Eden Marco's structure makes a clear distinction:
    - chains/  = where the actual LLM logic lives (prompt + model + parser)
    - nodes/   = thin orchestrators that call chains and update state

  This separation matters because:
  1. Chains are independently testable without the graph running
  2. Multiple nodes can share the same chain
  3. You can swap chain implementations without touching node logic

  The tests/ folder inside chains/ reflects this:
  chains contain the logic worth unit-testing in isolation.

HOW TO ADD A NEW CHAIN:
  Create a new file in graph/chains/:
    graph/chains/my_grader.py    → wraps an LLM call that grades something
    graph/chains/my_parser.py    → wraps an LLM call with structured output

  Then call it from a node:
    from graph.chains.my_grader import run_grader
    result = run_grader(document, question)

USAGE:
  from graph.chains.llm_chain import call_llm

  text = call_llm(
      system="You are a concise assistant.",
      user="What is the capital of France?",
  )
  # Returns plain string: "Paris"
"""

from groq import Groq

from graph.consts import GROQ_API_KEY, MAX_TOKENS, MODEL_NAME, TEMPERATURE, VERBOSE

# One client instance shared across all calls in this process.
_client = Groq(api_key=GROQ_API_KEY)


def call_llm(
    system: str,
    user: str,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_TOKENS,
) -> str:
    """
    Single chat-completion call. Returns the response as a plain string.

    Args:
        system:      System prompt — LLM role and behaviour.
        user:        User prompt — the actual query or input.
        temperature: 0.0 = deterministic, 1.0 = creative.
        max_tokens:  Response length cap.

    Returns:
        Stripped response string. Empty string if the model returns no content.

    Raises:
        RuntimeError: GROQ_API_KEY is not set.
        groq.APIError: Propagated from the Groq client.
    """
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set.\n" "Add it to .env:  GROQ_API_KEY=your_key_here"
        )

    if VERBOSE:
        preview = user[:80] + "..." if len(user) > 80 else user
        print(f"      🤖 [LLM] {MODEL_NAME} ← '{preview}'")

    completion = _client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # The Groq SDK types content as str | None — the model can theoretically
    # return an empty message (e.g. on a content filter hit). We normalise
    # None to an empty string so callers always receive a str, never None.
    content = completion.choices[0].message.content
    return content.strip() if content is not None else ""
