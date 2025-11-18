"""Authentication helper for creating a Secret Server client.

This module wraps creation of the SecretServer client using the
Password Grant authorizer provided by the Delinea SDK. It keeps a tiny
factory function to centralize client creation which makes testing and
future changes easier.
"""

from delinea.secrets.server import PasswordGrantAuthorizer, SecretServer


def create_client(server_url, username, password):
    """Create and return a SecretServer client using password grant auth.

    Args:
        server_url (str): Base URL of the Secret Server instance.
        username (str): Username for authentication.
        password (str): Password for authentication.

    Returns:
        SecretServer: Initialized SDK client instance.
    """
    authorizer = PasswordGrantAuthorizer(
        base_url=server_url,
        username=username,
        password=password
    )
    return SecretServer(base_url=server_url, authorizer=authorizer)
