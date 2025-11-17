import os
from pathlib import Path
from typing import Optional, Tuple

import pytest
import kumiho

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TOKEN_FILE = REPO_ROOT / "firebase_token.txt"


def _load_token() -> Tuple[Optional[str], Optional[str]]:
    """Resolve the Firebase ID token from env vars or the helper file."""

    env_token = os.getenv("KUMIHO_AUTH_TOKEN")
    if env_token:
        return env_token.strip(), "KUMIHO_AUTH_TOKEN"

    token_file = os.getenv("KUMIHO_AUTH_TOKEN_FILE")
    candidate_paths = []
    if token_file:
        candidate_paths.append(Path(token_file))
    candidate_paths.append(DEFAULT_TOKEN_FILE)

    for candidate in candidate_paths:
        if not candidate:
            continue
        try:
            contents = candidate.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            continue
        if contents:
            return contents, str(candidate)
    return None, None


@pytest.fixture(scope="session")
def _firebase_token() -> str:
    token, source = _load_token()
    if not token:
        pytest.skip(
            "Configure KUMIHO_AUTH_TOKEN or KUMIHO_AUTH_TOKEN_FILE (see "
            "kumiho-python/README.md for Firebase/Supabase setup) to run live tests."
        )
    if source:
        print(f"[kumiho-tests] Using Firebase token from {source}")
    return token

@pytest.fixture(scope="function", autouse=True)
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
def live_client(_firebase_token):
    """Provides a client connected to the live gRPC server with auth metadata."""

    tenant_hint = os.getenv("KUMIHO_TENANT_HINT")
    if tenant_hint:
        print(f"[kumiho-tests] Tenant hint set to {tenant_hint}")

    return kumiho.Client(auth_token=_firebase_token)