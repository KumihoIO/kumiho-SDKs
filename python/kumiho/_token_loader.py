"""Helpers for locating Firebase ID tokens for the Python client."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Optional

_TOKEN_ENV = "KUMIHO_AUTH_TOKEN"
_TOKEN_FILE_ENV = "KUMIHO_AUTH_TOKEN_FILE"
_WORKSPACE_ENV = "KUMIHO_WORKSPACE_ROOT"
_DEFAULT_FILENAME = "firebase_token.txt"


def _unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    ordered: List[Path] = []
    for path in paths:
        resolved = path.expanduser()
        key = resolved.resolve() if resolved.exists() else resolved
        if key in seen:
            continue
        seen.add(key)
        ordered.append(resolved)
    return ordered


def _candidate_token_files() -> List[Path]:
    candidates: List[Path] = []

    env_file = os.getenv(_TOKEN_FILE_ENV)
    if env_file:
        candidates.append(Path(env_file))

    workspace_root = os.getenv(_WORKSPACE_ENV)
    if workspace_root:
        candidates.append(Path(workspace_root) / _DEFAULT_FILENAME)

    search_roots = [Path.cwd(), Path(__file__).resolve()]
    for origin in search_roots:
        for candidate_root in [origin, *origin.parents]:
            candidate = candidate_root / _DEFAULT_FILENAME
            if candidate.exists():
                candidates.append(candidate)
                break

    return _unique_paths(candidates)


def load_bearer_token() -> Optional[str]:
    """Return a bearer token from env vars or helper files, if available."""

    env_token = os.getenv(_TOKEN_ENV)
    if env_token:
        stripped = env_token.strip()
        if stripped:
            return stripped

    for token_file in _candidate_token_files():
        try:
            contents = token_file.read_text(encoding="utf-8").strip()
        except FileNotFoundError:
            continue
        except OSError:
            continue
        if contents:
            return contents
    return None
