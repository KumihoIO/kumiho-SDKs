"""Interactive helpers for acquiring Firebase ID tokens for Kumiho tests."""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import requests

CONFIG_ENV = "KUMIHO_CONFIG_DIR"
API_KEY_ENV = "KUMIHO_FIREBASE_API_KEY"
PROJECT_ENV = "KUMIHO_FIREBASE_PROJECT_ID"
TOKEN_FILE_ENV = "KUMIHO_AUTH_TOKEN_FILE"
REPO_ROOT_ENV = "KUMIHO_WORKSPACE_ROOT"
ENV_FILE_ENV = "KUMIHO_ENV_FILE"


class TokenAcquisitionError(RuntimeError):
    """Raised when we cannot obtain or refresh a Firebase ID token."""


@dataclass
class Credentials:
    api_key: str
    email: str
    refresh_token: str
    id_token: str
    expires_at: int
    project_id: Optional[str] = None

    def is_valid(self) -> bool:
        return self.id_token and (self.expires_at - int(time.time())) > 60


def _config_dir() -> Path:
    base = os.getenv(CONFIG_ENV)
    if base:
        return Path(base).expanduser()
    return Path.home() / ".kumiho"


def _credentials_path() -> Path:
    return _config_dir() / "credentials.json"


def _default_repo_root() -> Path:
    env_root = os.getenv(REPO_ROOT_ENV)
    if env_root:
        return Path(env_root).expanduser()

    search_paths = [Path.cwd(), Path(__file__).resolve()]
    visited = set()
    for origin in search_paths:
        for candidate in [origin, *origin.parents]:
            if candidate in visited:
                continue
            visited.add(candidate)
            if (candidate / ".env.local").exists() and (candidate / "kumiho-python").exists():
                return candidate
            if (candidate / "Cargo.toml").exists() and (candidate / "kumiho-python").exists():
                return candidate
    return Path.cwd()


def _env_file_path(repo_root: Path) -> Path:
    env_override = os.getenv(ENV_FILE_ENV)
    if env_override:
        return Path(env_override).expanduser()
    return repo_root / ".env.local"


def _token_file_path(repo_root: Path) -> Path:
    token_override = os.getenv(TOKEN_FILE_ENV)
    if token_override:
        return Path(token_override).expanduser()
    return repo_root / "firebase_token.txt"


def _load_credentials() -> Optional[Credentials]:
    try:
        data = json.loads(_credentials_path().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

    try:
        return Credentials(
            api_key=data["api_key"],
            email=data["email"],
            refresh_token=data["refresh_token"],
            id_token=data["id_token"],
            expires_at=int(data["expires_at"]),
            project_id=data.get("project_id"),
        )
    except KeyError:
        return None


def _save_credentials(creds: Credentials) -> None:
    path = _credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "api_key": creds.api_key,
        "email": creds.email,
        "refresh_token": creds.refresh_token,
        "id_token": creds.id_token,
        "expires_at": creds.expires_at,
        "project_id": creds.project_id,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_token_file(token_file: Path, token: str) -> None:
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(token.strip() + "\n", encoding="utf-8")


def _token_preview(token: str) -> str:
    if not token:
        return "<empty>"
    if len(token) <= 16:
        return f"{token} (len={len(token)})"
    return f"{token[:8]}...{token[-6:]} (len={len(token)})"


def _log_token(token: str, source: str, token_path: Path) -> None:
    preview = _token_preview(token)
    print(f"[kumiho-auth] {source} token -> {preview} [file: {token_path}]")


def _ensure_env_hint(env_file: Path, token_file: Path) -> None:
    line = f"KUMIHO_AUTH_TOKEN_FILE={token_file.as_posix()}"
    try:
        if env_file.exists():
            contents = env_file.read_text(encoding="utf-8").splitlines()
        else:
            contents = []
    except FileNotFoundError:
        contents = []

    for idx, entry in enumerate(contents):
        if entry.startswith("KUMIHO_AUTH_TOKEN_FILE"):
            if entry == line:
                return
            contents[idx] = line
            env_file.write_text("\n".join(contents) + "\n", encoding="utf-8")
            return

    contents.append(line)
    env_file.write_text("\n".join(contents) + "\n", encoding="utf-8")


def _fetch_with_password(api_key: str, email: str, password: str) -> Tuple[str, str, int]:
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data["idToken"], data["refreshToken"], int(data.get("expiresIn", "3600"))


def _refresh_with_token(api_key: str, refresh_token: str) -> Tuple[str, str, int]:
    url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    resp = requests.post(url, data=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data["id_token"], data["refresh_token"], int(data.get("expires_in", "3600"))


def _prompt(prompt_text: str) -> str:
    return input(prompt_text).strip()


def _prompt_password(prompt_text: str = "Firebase password: ") -> str:
    return getpass.getpass(prompt_text)


def _resolve_api_key(existing: Optional[str]) -> str:
    if existing:
        return existing
    env_key = os.getenv(API_KEY_ENV)
    if env_key:
        return env_key
    key = _prompt("Firebase Web API key (see Firebase console): ")
    if not key:
        raise TokenAcquisitionError("Firebase Web API key is required")
    return key


def _resolve_project_id(existing: Optional[str]) -> Optional[str]:
    return existing or os.getenv(PROJECT_ENV)


def _interactive_login(api_key: str, project_id: Optional[str]) -> Credentials:
    print("[kumiho-auth] No cached credentials found. Please log in with your Firebase email.")
    email = _prompt("Firebase email: ")
    if not email:
        raise TokenAcquisitionError("Firebase email is required")
    password = _prompt_password()
    if not password:
        raise TokenAcquisitionError("Firebase password is required")

    id_token, refresh_token, expires_in = _fetch_with_password(api_key, email, password)
    expires_at = int(time.time()) + expires_in
    return Credentials(
        api_key=api_key,
        email=email,
        refresh_token=refresh_token,
        id_token=id_token,
        expires_at=expires_at,
        project_id=project_id,
    )


def ensure_token(
    *,
    token_file: Optional[Path] = None,
    interactive: bool = True,
) -> Tuple[str, str]:
    """Ensure a usable Firebase ID token exists.

    Returns the token and a short description of the source.
    """

    repo_root = _default_repo_root()
    token_path = token_file or _token_file_path(repo_root)

    creds = _load_credentials()
    if creds and creds.is_valid():
        _write_token_file(token_path, creds.id_token)
        _ensure_env_hint(_env_file_path(repo_root), token_path)
        _log_token(creds.id_token, "cached", token_path)
        return creds.id_token, "cached credentials"

    if creds and creds.refresh_token:
        try:
            id_token, refresh_token, expires_in = _refresh_with_token(creds.api_key, creds.refresh_token)
            updated = Credentials(
                api_key=creds.api_key,
                email=creds.email,
                refresh_token=refresh_token,
                id_token=id_token,
                expires_at=int(time.time()) + expires_in,
                project_id=creds.project_id,
            )
            _save_credentials(updated)
            _write_token_file(token_path, updated.id_token)
            _ensure_env_hint(_env_file_path(repo_root), token_path)
            _log_token(updated.id_token, "refreshed", token_path)
            return updated.id_token, "refreshed credentials"
        except requests.HTTPError as exc:
            print(f"[kumiho-auth] Refresh failed: {exc}")

    if not interactive:
        raise TokenAcquisitionError("No Firebase token available and interactive mode disabled")

    api_key = _resolve_api_key(creds.api_key if creds else None)
    project_id = _resolve_project_id(creds.project_id if creds else None)
    new_creds = _interactive_login(api_key, project_id)
    _save_credentials(new_creds)
    _write_token_file(token_path, new_creds.id_token)
    _ensure_env_hint(_env_file_path(repo_root), token_path)
    _log_token(new_creds.id_token, "interactive", token_path)
    return new_creds.id_token, "interactive login"


def cmd_login(args: argparse.Namespace) -> None:
    repo_root = _default_repo_root()
    token_path = Path(args.token_file).expanduser() if args.token_file else _token_file_path(repo_root)
    api_key = args.api_key or _resolve_api_key(None)
    project_id = args.project_id or _resolve_project_id(None)

    creds = _interactive_login(api_key, project_id)
    _save_credentials(creds)
    _write_token_file(token_path, creds.id_token)
    _ensure_env_hint(_env_file_path(repo_root), token_path)
    _log_token(creds.id_token, "login", token_path)
    print(f"[kumiho-auth] Token written to {token_path}")
    print(f"[kumiho-auth] Credentials cached at {_credentials_path()}")


def cmd_refresh(args: argparse.Namespace) -> None:
    creds = _load_credentials()
    if not creds:
        raise TokenAcquisitionError("No cached credentials to refresh. Run 'kumiho-auth login' first.")
    id_token, refresh_token, expires_in = _refresh_with_token(creds.api_key, creds.refresh_token)
    updated = Credentials(
        api_key=creds.api_key,
        email=creds.email,
        refresh_token=refresh_token,
        id_token=id_token,
        expires_at=int(time.time()) + expires_in,
        project_id=creds.project_id,
    )
    _save_credentials(updated)
    token_path = Path(args.token_file).expanduser() if args.token_file else _token_file_path(_default_repo_root())
    _write_token_file(token_path, updated.id_token)
    _ensure_env_hint(_env_file_path(_default_repo_root()), token_path)
    _log_token(updated.id_token, "refresh", token_path)
    print("[kumiho-auth] Token refreshed.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kumiho Firebase token helper")
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login", help="Obtain and store a Firebase ID token using email/password")
    login.add_argument("--api-key", help="Firebase Web API key (defaults to KUMIHO_FIREBASE_API_KEY)")
    login.add_argument("--project-id", help="Firebase project ID (optional)")
    login.add_argument("--token-file", help="Path to firebase_token.txt to update")
    login.set_defaults(func=cmd_login)

    refresh = sub.add_parser("refresh", help="Refresh the cached Firebase ID token using the stored refresh token")
    refresh.add_argument("--token-file", help="Path to firebase_token.txt to update")
    refresh.set_defaults(func=cmd_refresh)
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except TokenAcquisitionError as exc:
        parser.error(str(exc))
    except requests.HTTPError as exc:
        parser.error(f"Firebase request failed: {exc}")


if __name__ == "__main__":
    main()
