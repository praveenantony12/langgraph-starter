"""
main.py — Entry point.

LOCAL:   uv run python main.py           → runs one graph turn, prints result
RENDER:  PORT is set automatically       → starts FastAPI server on $PORT

The PORT check means the same file works for both local dev and deployment
without any changes.
"""

import os

from api.runner import run


def main() -> None:
    # Render (and all PaaS) sets PORT. When present, start the HTTP server.
    if os.environ.get("PORT"):
        from api.server import main as serve
        serve()
        return

    # Local dev — run one turn and print the result
    print("=" * 50)
    print("  langgraph-starter")
    print("=" * 50)

    result = run("Hello! What can you do?")

    if result.get("error"):
        print(f"\n❌ Error: {result['error']}")
        return

    print(f"\n🤖 {result.get('response', '(no response)')}")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
