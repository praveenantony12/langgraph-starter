"""
main.py — Entry point.

  python main.py
"""

from api.runner import run


def main() -> None:
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
