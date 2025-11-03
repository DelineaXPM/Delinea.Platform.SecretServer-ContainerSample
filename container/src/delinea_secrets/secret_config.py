"""Utilities to parse and validate the SECRETS_CONFIG environment var.

The sidecar supports two ways of specifying secrets via the
`SECRETS_CONFIG` environment variable:
  - A JSON array of objects describing secrets
  - A simple comma-separated list of secret IDs (falls back to building
    minimal entries from the IDs)

The parser returns a list of dicts with keys `id`, `name`, and `fields`.
"""

import os
import json


def parse_secrets_config():
    """Parse `SECRETS_CONFIG` into a structured list.

    Returns:
        list[dict]: Each dict contains at least the keys `id`, `name`, and
            `fields`.

    Raises:
        ValueError: If `SECRETS_CONFIG` is missing or malformed JSON.
    """
    config_str = os.getenv("SECRETS_CONFIG", "")
    if not config_str:
        raise ValueError("SECRETS_CONFIG is required")

    try:
        if config_str.strip().startswith('['):
            return json.loads(config_str)

        # Fallback: simple comma-separated IDs
        secret_ids = [sid.strip() for sid in config_str.split(',') if sid.strip()]
        return [{"id": sid, "name": f"secret-{sid}", "fields": "*"} for sid in secret_ids]

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid SECRETS_CONFIG format: {e}")
