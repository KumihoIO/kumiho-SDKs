import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import pytest
import kumiho
from kumiho.auth_cli import TokenAcquisitionError, ensure_token

REPO_ROOT = Path(__file__).resolve().parents[2]


from kumiho._token_loader import load_bearer_token

def _load_token() -> Tuple[Optional[str], Optional[str]]:
    """Resolve the auth token (Firebase or CP) from env vars, files, or interactive login."""
    
    # 1. Try the SDK's standard loader (respects env vars and preferences)
    token = load_bearer_token()
    if token:
        return token, "SDK load_bearer_token"

    # 2. Fallback to interactive login if TTY
    if sys.stdin.isatty():
        try:
            token, source = ensure_token(interactive=True)
            return token, source
        except TokenAcquisitionError as exc:
            print(f"[kumiho-tests] Interactive login failed: {exc}")
        except Exception as exc:  # pragma: no cover - defensive logging
            print(f"[kumiho-tests] Unexpected error retrieving token: {exc}")
    else:
        print("[kumiho-tests] No token found and stdin is not a TTY; skipping interactive login.")
    return None, None


@pytest.fixture(scope="session")
def _auth_token() -> str:
    token, source = _load_token()
    if not token:
        pytest.skip(
            "Configure KUMIHO_AUTH_TOKEN / KUMIHO_AUTH_TOKEN_FILE or run 'kumiho-auth login' "
            "(see kumiho-python/README.md) to run live tests."
        )
    if source:
        print(f"[kumiho-tests] Using auth token from {source}")
    # Ensure the env var is set so subprocesses or other libs can find it
    os.environ["KUMIHO_AUTH_TOKEN"] = token
    return token

@pytest.fixture(scope="function")
def cleanup_test_data(live_client):
    """Clean up test data after each test."""
    # Store created objects for cleanup
    created_objects = []

    # This will run before the test
    yield created_objects

    # This will run after the test for cleanup
    # Delete objects in reverse dependency order: links -> resources -> versions -> products -> groups
    print(f"\nCleaning up {len(created_objects)} objects...")
    for obj in reversed(created_objects):
        try:
            obj_type = type(obj).__name__
            print(f"Deleting {obj_type}: {getattr(obj, 'kref', getattr(obj, 'path', 'unknown'))}")
            obj.delete(force=True)
            print(f"Successfully deleted {obj_type}")
        except Exception as e:
            # Log cleanup errors but don't fail the test
            print(f"Warning: Failed to cleanup {type(obj).__name__}: {obj} - Error: {e}")
            pass

@pytest.fixture(scope="session")
def live_client(_auth_token):
    """Provides a client connected to the live gRPC server with auth metadata."""

    # Pass the resolved token (which might be a CP token) to the discovery helper.
    # The helper handles swapping it for a Firebase token for the discovery call if needed.
    client = kumiho.client_from_discovery(id_token=_auth_token, force_refresh=True)
    kumiho.configure_default_client(client)
    return client
