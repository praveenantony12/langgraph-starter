"""
api/server.py — Minimal HTTP server for Render.

Render marks deployments as failed when it can't detect a process listening
on the allocated $PORT. This server keeps the process alive and exposes:
  - GET  /healthz
  - POST /chat  (JSON body: {"message": "...", "session_id": "...optional"})

It reuses `api.runner.run()` as the single graph invocation boundary.
"""

from __future__ import annotations

import json
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from api.runner import run


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "langgraph-starter/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        # Keep logs readable in Render; don't spam default BaseHTTPRequestHandler logs.
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            _json_response(self, HTTPStatus.OK, {"status": "ok"})
            return

        _json_response(self, HTTPStatus.NOT_FOUND, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/chat":
            _json_response(self, HTTPStatus.NOT_FOUND, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "invalid Content-Length"})
            return

        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "invalid JSON"})
            return

        message = (body.get("message") or body.get("user_message") or "").strip()
        session_id = body.get("session_id") or body.get("thread_id")

        if not message:
            _json_response(self, HTTPStatus.BAD_REQUEST, {"error": "message is required"})
            return

        try:
            result = run(message, thread_id=session_id)
        except Exception as exc:
            _json_response(
                self,
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"user_message": message, "response": "", "iteration": 0, "error": str(exc)},
            )
            return

        # `result` is AgentState TypedDict; return what the caller needs.
        _json_response(self, HTTPStatus.OK, dict(result))


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")

    httpd = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"Starting server on {host}:{port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

