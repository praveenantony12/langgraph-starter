"""
main.py — Entry point.

  python main.py
"""

import os

from api.runner import run


def main() -> None:
    print("=" * 50)
    print("  langgraph-starter")
    print("=" * 50)

    # Render (and most PaaS) sets `PORT`. When present, we should run a web
    # server so the platform can detect open ports and keep the process alive.
    if os.environ.get("PORT"):
        from api.server import main as serve

        serve()
        return

    result = run("Hello! What can you do?")

    if result.get("error"):
        print(f"\n❌ Error: {result['error']}")
        return

    print(f"\n🤖 {result.get('response', '(no response)')}")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
