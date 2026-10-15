"""Minimal test-only HTTP upstream used to verify Nginx forwarding behaviour."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/api/ci-edge-passthrough":
            # Stands in for an API-level refusal (for example TALIMGO's own rate limit). The edge must
            # hand this response, its body and its Retry-After header to the client unchanged.
            body = json.dumps({"detail": "api-level limit reached"}).encode("utf-8")
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", "7")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
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
