"""Entry point for starting the DelineaPlatformSecretServer sidecar.

This module initializes the sidecar, starts the background polling
for secrets, and runs the HTTP API server exposing simple endpoints
for health and secrets access.

Usage: run this module as the application entrypoint.
"""

import os
import sys
import logging
from api.http_server import SidecarHTTPServer, SidecarHTTPHandler
from delinea_secrets.secret_manager import DelineaSidecar

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Initialize and run the sidecar.

    This will create the core DelineaSidecar instance, start its
    background polling thread, then start the HTTP server which
    serves the /health and /secrets endpoints.

    Exits with code 1 on unexpected exceptions.
    """
    try:
        # Initialize sidecar core logic
        sidecar = DelineaSidecar()
        sidecar.start_polling()

        # Start HTTP server
        port = int(os.getenv("HTTP_PORT", "8080"))
        bind_host = os.getenv("BIND_HOST", "127.0.0.1")
        server = SidecarHTTPServer((bind_host, port), SidecarHTTPHandler, sidecar)

        logger.info(f"🌐 HTTP API server running on {bind_host}:{port}")
        logger.info("📋 Endpoints: /health, /secrets, /secrets/<name>")
        server.serve_forever()

    except KeyboardInterrupt:
        logger.info("🛑 Sidecar stopped by user")
    except Exception as e:
        logger.error(f"❌ Sidecar failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
