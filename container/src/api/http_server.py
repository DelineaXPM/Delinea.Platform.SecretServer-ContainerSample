"""Simple HTTP server to expose sidecar secrets via a tiny API.

Provides a minimal HTTP handler with endpoints for health and secret
retrieval.
"""

import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import re

logger = logging.getLogger(__name__)

class SidecarHTTPHandler(BaseHTTPRequestHandler):
    """HTTP API handler for the sidecar.

    Endpoints:
      - GET /health -> health status, secret count, last update
      - GET /secrets -> list of configured secret names
      - GET /secrets/<name> -> secret fields (masked unless API_KEY provided)
      - GET /secrets/<ID> -> secret fields by ID (masked unless API_KEY provided
    """

    def _send_json(self, data, status=200):
        """Send JSON response with the given HTTP status."""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        """Handle GET requests for health and secrets endpoints."""
        sidecar = self.server.sidecar
        path = urllib.parse.urlparse(self.path).path
        try:
            if path == "/health":
                self._send_json({
                    "status": "healthy",
                    "secrets_count": len(sidecar.secrets_cache),
                    "last_update": sidecar.last_update
                })
            elif path == "/secrets":
                self._send_json({
                    "secrets": list(sidecar.secrets_cache.keys()),
                    "last_update": sidecar.last_update
                })
            elif path.startswith("/secrets/"):
                identifier = path.split("/")[-1]
                # Try direct cache lookup first (works for both name and id keys)
                data = sidecar.secrets_cache.get(identifier)
                if data:
                    self._send_json(data)
                    return
                # Fallback: look for secret where _secret_id matches
                found = None
                for _, secret_data in sidecar.secrets_cache.items():
                    if secret_data.get("_secret_id") == identifier:
                        found = secret_data
                        break

                if found:
                    self._send_json(found)
                else:
                    self._send_json({"error": "Secret not found"}, 404)
            else:
                self._send_json({"error": "Not found"}, 404)
        except Exception as e:
            logger.error(f"API error: {e}")
            self._send_json({"error": "Internal error"}, 500)

    def log_message(self, format, *args):
        """Override default logging to keep output quiet during requests."""
        pass

class SidecarHTTPServer(HTTPServer):
    """Small HTTPServer subclass that carries a reference to the sidecar.

    The server instance stores the `sidecar` object so request handlers can
    access runtime state (cache, last_update, etc.).
    """

    def __init__(self, address, handler_class, sidecar):
        super().__init__(address, handler_class)
        self.sidecar = sidecar
