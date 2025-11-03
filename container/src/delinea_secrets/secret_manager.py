"""Core sidecar logic: loading credentials, fetching secrets, and polling.

This module provides the DelineaSidecar class which is responsible for
reading Docker-provided credentials, initializing the Delinea SDK client,
maintaining an in-memory secrets cache, and running a background polling
thread to refresh secrets on a configurable interval.
"""

import os
import time
import logging
import threading
from datetime import datetime
from delinea.secrets.server import SecretServerError
from auth.delinea_auth import create_client
from delinea_secrets.secret_config import parse_secrets_config

logger = logging.getLogger(__name__)

class DelineaSidecar:
    """Main sidecar class that manages secret retrieval and caching.

    The sidecar reads credentials from the Docker secrets file
    `/run/secrets/server_creds`, initializes a Secret Server client, and
    periodically refreshes configured secrets into an in-memory cache.

    Attributes:
        server_url (str): The Delinea Secret Server base URL.
        username (str): Username for password grant auth.
        password (str): Password for password grant auth.
        secrets_config (list): Parsed list of secrets to fetch.
        poll_interval (int): Polling interval in seconds.
        secrets_cache (dict): In-memory cache of the latest secrets.
        last_update (str|None): ISO timestamp of last update.
        running (bool): Flag used to stop the polling loop.
        ss_client: SDK client for interacting with Secret Server.
    """

    def __init__(self):
        # Load credentials from Docker secret file
        creds = {}
        try:
            with open("/run/secrets/server_creds", "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        creds[key] = value
        except FileNotFoundError:
            raise RuntimeError("❌ Secrets file not found at /run/secrets/server_creds")

        # Core config
        self.server_url = creds.get("SERVER_URL")
        self.username = creds.get("SERVER_USERNAME")
        self.password = creds.get("SERVER_PASSWORD")
        self.secrets_config = parse_secrets_config()
        self.poll_interval = int(os.getenv("POLL_INTERVAL", "60"))

        # Runtime state
        self.secrets_cache = {}
        self.last_update = None
        self.running = True

        # SDK client
        self.ss_client = create_client(self.server_url, self.username, self.password)

        # Validation
        self._validate_config()

        logger.info("🚀 Delinea Sidecar initialized")

    def _validate_config(self):
        """Validate initial configuration and credentials.

        Raises ValueError for missing required configuration or unsupported
        storage modes.
        """
        if not self.server_url or not self.username or not self.password:
            raise ValueError("Missing required server credentials")
        if not self.secrets_config:
            raise ValueError("At least one secret must be configured")

    def _fetch_secret(self, secret_id: str):
        """Retrieve a single secret by its secret_id using the SDK client.

        Args:
            secret_id (str): Identifier for the secret in Secret Server.

        Returns:
            dict: Mapping of field names to values for the secret. Returns an
            empty dict on error.
        """
        try:
            secret_data = self.ss_client.get_secret(secret_id)
            fields = {}
            for item in secret_data.get("items", []):
                field_name = item.get("slug", item.get("fieldName", ""))
                field_value = item.get("itemValue", "")
                if field_name:
                    fields[field_name] = field_value
            return fields
        except SecretServerError as e:
            logger.error(f"❌ Failed to fetch secret {secret_id}: {e}")
            return {}

    def _filter_fields(self, fields, requested_fields):
        """Return a subset of fields according to requested_fields config.

        Args:
            fields (dict): All fields fetched for a secret.
            requested_fields (str): Either '*' to keep all fields or a
                comma-separated list of field names to include.

        Returns:
            dict: Filtered mapping of fields.
        """
        if requested_fields == "*":
            return fields
        requested = set(field.strip() for field in requested_fields.split(','))
        return {k: v for k, v in fields.items() if k in requested}

    def _update_secrets(self):
        """Fetch and refresh all configured secrets into the cache.

        For each configured secret entry in `self.secrets_config`, fetch the
        secret, filter fields as configured, add metadata, and update the
        in-memory `secrets_cache` and `last_update` timestamp if new data is
        available.
        """
        updated_secrets = {}
        for sc in self.secrets_config:
            raw_fields = self._fetch_secret(sc["id"])
            if raw_fields:
                filtered = self._filter_fields(raw_fields, sc["fields"])
                filtered["_last_updated"] = datetime.now().isoformat()
                filtered["_secret_name"] = sc["name"]
                updated_secrets[sc["name"]] = filtered
        if updated_secrets:
            self.secrets_cache = updated_secrets
            self.last_update = datetime.now().isoformat()

    def _polling_loop(self):
        """Background polling loop.

        This method is intended to run in a daemon thread. It performs an
        initial update immediately and then sleeps for `poll_interval`
        seconds between refreshes while `self.running` is True.
        """
        self._update_secrets()
        while self.running:
            time.sleep(self.poll_interval)
            if self.running:
                self._update_secrets()

    def start_polling(self):
        """Start the background polling thread and return the Thread object.

        Returns:
            threading.Thread: The started daemon thread running the polling loop.
        """
        thread = threading.Thread(target=self._polling_loop, daemon=True)
        thread.start()
        return thread
