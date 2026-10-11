"""Minimal test-only HTTP upstream used to verify Nginx forwarding behaviour."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if not self.path.startswith("/api/"):
            self.send_error(404)
            return
        payload = {
            "path": self.path,
            "headers": {
                name: self.headers.get(name)
                for name in ("Host", "X-Forwarded-Proto", "X-Forwarded-For", "Forwarded")
            },
        }
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
