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
# Legacy env var for token file is removed
REPO_ROOT_ENV = "KUMIHO_WORKSPACE_ROOT"
ENV_FILE_ENV = "KUMIHO_ENV_FILE"
TOKEN_GRACE_ENV = "KUMIHO_AUTH_TOKEN_GRACE_SECONDS"
CONTROL_PLANE_API_ENV = "KUMIHO_CONTROL_PLANE_API_URL"
DEFAULT_TOKEN_GRACE_SECONDS = 300
DEFAULT_CONTROL_PLANE_API_URL = "https://kumiho.io"
DEFAULT_FIREBASE_API_KEY = "AIzaSyBFAo7Nv48xAvbN18rL-3W41Dqheporh8E"


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
    control_plane_token: Optional[str] = None
    cp_expires_at: Optional[int] = None

    def is_valid(self) -> bool:
        remaining = self.expires_at - int(time.time())
        grace = int(os.getenv(TOKEN_GRACE_ENV, DEFAULT_TOKEN_GRACE_SECONDS))
        return bool(self.id_token) and remaining > grace

    def is_cp_valid(self) -> bool:
        if not self.control_plane_token or not self.cp_expires_at:
            return False
        remaining = self.cp_expires_at - int(time.time())
        grace = int(os.getenv(TOKEN_GRACE_ENV, DEFAULT_TOKEN_GRACE_SECONDS))
        return remaining > grace


def _config_dir() -> Path:
    base = os.getenv(CONFIG_ENV)
    if base:
        return Path(base).expanduser()
    return Path.home() / ".kumiho"


def _credentials_path() -> Path:
    return _config_dir() / "kumiho_authentication.json"


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
            control_plane_token=data.get("control_plane_token"),
            cp_expires_at=int(data.get("cp_expires_at")) if data.get("cp_expires_at") else None,
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
        "control_plane_token": creds.control_plane_token,
        "cp_expires_at": creds.cp_expires_at,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.chmod(path, 0o600)


def _token_preview(token: str) -> str:
    if not token:
        return "<empty>"
    if len(token) <= 16:
        return f"{token} (len={len(token)})"
    return f"{token[:8]}...{token[-6:]} (len={len(token)})"


def _log_token(token: str, source: str) -> None:
    # Do not log tokens in production
    pass


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


def _exchange_for_control_plane_token(firebase_token: str) -> Tuple[Optional[str], Optional[int]]:
    base_url = os.getenv(CONTROL_PLANE_API_ENV, DEFAULT_CONTROL_PLANE_API_URL).rstrip("/")
    url = f"{base_url}/api/control-plane/token"
    
    try:
        resp = requests.post(
            url, 
            headers={"Authorization": f"Bearer {firebase_token}"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return data["token"], int(data["expires_at"])
    except requests.RequestException as exc:
        # Fallback: if CP exchange fails, we just return empty (client will use Firebase token)
        # But we should log it.
        print(f"[kumiho-auth] Warning: Failed to exchange for Control Plane JWT: {exc}")
        return None, None


def _prompt(prompt_text: str) -> str:
    return input(prompt_text).strip()


def _prompt_password(prompt_text: str = "KumihoClouds password: ") -> str:
    return getpass.getpass(prompt_text)


def _resolve_api_key(existing: Optional[str]) -> str:
    if existing:
        return existing
    env_key = os.getenv(API_KEY_ENV)
    if env_key:
        return env_key
    return DEFAULT_FIREBASE_API_KEY


def _resolve_project_id(existing: Optional[str]) -> Optional[str]:
    return existing or os.getenv(PROJECT_ENV)


def _interactive_login(api_key: str, project_id: Optional[str]) -> Credentials:
    print("[kumiho-auth] No cached credentials found. Please log in with your KumihoClouds credentials.")
    email = _prompt("KumihoClouds email: ")
    if not email:
        raise TokenAcquisitionError("KumihoClouds email is required")
    password = _prompt_password()
    if not password:
        raise TokenAcquisitionError("KumihoClouds password is required")

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
    interactive: bool = True,
) -> Tuple[str, str]:
    """Ensure a usable Firebase ID token exists.

    Returns the token and a short description of the source.
    """

    creds = _load_credentials()
    if creds and creds.is_valid():
        _log_token(creds.id_token, "cached")
        
        # Check if we need to refresh CP token
        if not creds.is_cp_valid():
             cp_token, cp_exp = _exchange_for_control_plane_token(creds.id_token)
             if cp_token:
                 creds.control_plane_token = cp_token
                 creds.cp_expires_at = cp_exp
                 _save_credentials(creds)

        return creds.control_plane_token or creds.id_token, "cached credentials"

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
            
            # Exchange for CP token
            cp_token, cp_exp = _exchange_for_control_plane_token(id_token)
            updated.control_plane_token = cp_token
            updated.cp_expires_at = cp_exp

            _save_credentials(updated)
            _log_token(updated.id_token, "refreshed")
            return updated.control_plane_token or updated.id_token, "refreshed credentials"
        except requests.HTTPError as exc:
            print(f"[kumiho-auth] Refresh failed: {exc}")

    if not interactive:
        raise TokenAcquisitionError("No KumihoClouds token available and interactive mode disabled")

    api_key = _resolve_api_key(creds.api_key if creds else None)
    project_id = _resolve_project_id(creds.project_id if creds else None)
    new_creds = _interactive_login(api_key, project_id)
    
    # Exchange for CP token
    cp_token, cp_exp = _exchange_for_control_plane_token(new_creds.id_token)
    new_creds.control_plane_token = cp_token
    new_creds.cp_expires_at = cp_exp
    
    _save_credentials(new_creds)
    _log_token(new_creds.id_token, "interactive")
    return new_creds.control_plane_token or new_creds.id_token, "interactive login"


def cmd_login(args: argparse.Namespace) -> None:
    api_key = args.api_key or _resolve_api_key(None)
    project_id = args.project_id or _resolve_project_id(None)

    creds = _interactive_login(api_key, project_id)
    
    # Exchange for CP token
    cp_token, cp_exp = _exchange_for_control_plane_token(creds.id_token)
    creds.control_plane_token = cp_token
    creds.cp_expires_at = cp_exp

    _save_credentials(creds)
    _log_token(creds.id_token, "login")
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
    _log_token(updated.id_token, "refresh")
    print("[kumiho-auth] Token refreshed.")


def cmd_inspect(args: argparse.Namespace) -> None:
    try:
        import kumiho
        from kumiho.kref import Kref
    except ImportError:
        print("Error: 'kumiho' package is required for inspect command. Please install it.")
        return

    # Configure client
    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    target = args.target
    
    if target.startswith("kref://"):
        try:
            kref = Kref(target)
            
            if kref.get_artifact_name():
                rev_kref_str = f"kref://{kref.get_path()}?r={kref.get_revision()}"
                revision = kumiho.get_revision(rev_kref_str)
                if not revision:
                    print(f"Revision not found: {rev_kref_str}")
                    return
                
                artifact = None
                for art in revision.get_artifacts():
                    if art.name == kref.get_artifact_name():
                        artifact = art
                        break
                
                if artifact:
                    print(f"Type: Artifact")
                    print(f"Kref: {target}")
                    print(f"Name: {artifact.name}")
                    print(f"Location: {artifact.location}")
                    print(f"Metadata: {artifact.metadata}")
                    print(f"Node Object: {artifact}")
                else:
                    print(f"Artifact '{kref.get_artifact_name()}' not found in revision {rev_kref_str}")
                return

            if "?r=" in target or "&r=" in target:
                revision = kumiho.get_revision(target)
                if revision:
                    print(f"Type: Revision")
                    print(f"Kref: {revision.kref}")
                    print(f"Metadata: {revision.metadata}")
                    print(f"Node Object: {revision}")
                else:
                    print(f"Revision not found: {target}")
                return

            item = kumiho.get_item(target)
            if item:
                print(f"Type: Item")
                print(f"Kref: {item.kref}")
                print(f"Metadata: {item.metadata}")
                print(f"Node Object: {item}")
            else:
                print(f"Item not found: {target}")

        except Exception as e:
            print(f"Error resolving kref: {e}")

    else:
        try:
            artifacts = kumiho.get_artifacts_by_location(target)
            if not artifacts:
                print(f"No artifacts found for location: {target}")
                return
                
            print(f"Found {len(artifacts)} artifacts:")
            for art in artifacts:
                print(f"- {art.name} (Revision: {art.revision.kref})")
                print(f"  Metadata: {art.metadata}")
        except Exception as e:
            print(f"Error searching by location: {e}")


def cmd_whoami(args: argparse.Namespace) -> None:
    creds = _load_credentials()
    if not creds:
        print("Not logged in.")
        return

    print(f"Email: {creds.email}")
    print(f"Project ID: {creds.project_id or '<not set>'}")
    print(f"Expires At: {time.ctime(creds.expires_at)}")
    print(f"Credentials Path: {_credentials_path()}")


def cmd_config(args: argparse.Namespace) -> None:
    print("Kumiho Configuration:")
    print(f"  Config Dir: {_config_dir()}")
    print(f"  Credentials Path: {_credentials_path()}")
    print(f"  Workspace Root: {_default_repo_root()}")
    
    # Print relevant environment variables
    env_vars = [
        CONFIG_ENV, API_KEY_ENV, PROJECT_ENV, REPO_ROOT_ENV, 
        ENV_FILE_ENV, TOKEN_GRACE_ENV, CONTROL_PLANE_API_ENV
    ]
    
    print("\nEnvironment Variables:")
    for var in env_vars:
        val = os.getenv(var)
        if val:
            print(f"  {var}: {val}")
        else:
            print(f"  {var}: <not set>")


def cmd_search(args: argparse.Namespace) -> None:
    try:
        import kumiho
    except ImportError:
        print("Error: 'kumiho' package is required. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    try:
        results = kumiho.item_search(
            context_filter=args.project,
            kind_filter=args.kind,
            name_filter=args.name
        )
        
        if not results:
            print("No items found.")
            return

        print(f"Found {len(results)} items:")
        for item in results:
            print(f"- {item.kref} (Type: {item.type})")
            
    except Exception as e:
        print(f"Search failed: {e}")


def cmd_tree(args: argparse.Namespace) -> None:
    try:
        import kumiho
    except ImportError:
        print("Error: 'kumiho' package is required. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    target = args.target
    
    try:
        if not target:
            # List projects
            projects = kumiho.get_projects()
            print("Projects:")
            for p in projects:
                print(f"├── {p.name} ({p.project_id})")
            return

        # Check if target is a project
        project = kumiho.get_project(target)
        if project:
            print(f"Project: {project.name}")
            _print_space_tree(project.get_spaces(recursive=True))
            return

        # Check if target is a space (needs full path usually, but let's try)
        # This part is tricky without a direct "get_space_by_path" that doesn't require project context
        # Assuming target is like "project/space"
        if "/" in target:
            parts = target.split("/", 1)
            proj_name = parts[0]
            space_path = parts[1]
            project = kumiho.get_project(proj_name)
            if project:
                space = project.get_space(space_path)
                if space:
                    print(f"Space: {space.path}")
                    # We need a way to get children of a space. 
                    # The SDK has get_spaces(recursive=True) on project, but maybe not on space?
                    # Let's just list items in this space for now.
                    items = space.get_items()
                    for item in items:
                        print(f"├── {item.name} ({item.type})")
                    return

        print(f"Target '{target}' not found or not supported for tree view.")

    except Exception as e:
        print(f"Tree failed: {e}")

def _print_space_tree(spaces):
    # Simple flat list print for now, could be improved to show hierarchy
    for space in spaces:
        indent = "  " * (space.path.count("/") - 1)
        print(f"{indent}├── {space.name}/")


def cmd_lineage(args: argparse.Namespace) -> None:
    try:
        import kumiho
        from kumiho.kref import Kref
    except ImportError:
        print("Error: 'kumiho' package is required. Please install it.")
        return

    try:
        kumiho.auto_configure_from_discovery()
    except Exception as e:
        print(f"Warning: Auto-configuration failed: {e}")

    target = args.target
    if not target.startswith("kref://"):
        print("Error: Target must be a valid kref URI.")
        return

    try:
        # Ensure we have a revision kref
        if "?r=" not in target:
             # If item kref, get latest revision
             item = kumiho.get_item(target)
             if not item:
                 print(f"Item not found: {target}")
                 return
             # This is a bit of a guess, assuming we want the latest revision
             # The SDK doesn't seem to have a direct "get_latest_revision" on item easily accessible here
             # without listing all. Let's just ask the user for a revision or default to r=1 if not present?
             # Or better, fetch the item and list revisions.
             print("Please specify a revision (e.g. ?r=1) for lineage analysis.")
             return

        revision = kumiho.get_revision(target)
        if not revision:
            print(f"Revision not found: {target}")
            return

        print(f"Lineage for: {revision.kref}")
        
        if args.direction in ["upstream", "both"]:
            print("\nUpstream Dependencies (Depends On):")
            deps = revision.get_all_dependencies(max_depth=args.depth)
            for kref in deps.revision_krefs:
                print(f"  <- {kref}")

        if args.direction in ["downstream", "both"]:
            print("\nDownstream Dependents (Used By):")
            deps = revision.get_all_dependents(max_depth=args.depth)
            for kref in deps.revision_krefs:
                print(f"  -> {kref}")

    except Exception as e:
        print(f"Lineage analysis failed: {e}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="KumihoClouds token helper")
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login", help="Obtain and store a KumihoClouds ID token using email/password")
    login.add_argument("--api-key", help="KumihoClouds API key (defaults to KUMIHO_FIREBASE_API_KEY)")
    login.add_argument("--project-id", help="KumihoClouds project ID (optional)")
    login.set_defaults(func=cmd_login)

    refresh = sub.add_parser("refresh", help="Refresh the cached KumihoClouds ID token using the stored refresh token")
    refresh.set_defaults(func=cmd_refresh)

    inspect = sub.add_parser("inspect", help="Inspect a Kumiho object by Kref or file path")
    inspect.add_argument("target", help="Kref URI or file path to inspect")
    inspect.set_defaults(func=cmd_inspect)

    whoami = sub.add_parser("whoami", help="Display current user and session info")
    whoami.set_defaults(func=cmd_whoami)

    config = sub.add_parser("config", help="Display configuration and environment variables")
    config.set_defaults(func=cmd_config)

    search = sub.add_parser("search", help="Search for items")
    search.add_argument("--project", help="Filter by project name")
    search.add_argument("--kind", help="Filter by item kind")
    search.add_argument("name", nargs="?", help="Filter by item name (wildcards supported)")
    search.set_defaults(func=cmd_search)

    tree = sub.add_parser("tree", help="Visualize project or space hierarchy")
    tree.add_argument("target", nargs="?", help="Project name or space path (optional)")
    tree.set_defaults(func=cmd_tree)

    lineage = sub.add_parser("lineage", help="Analyze revision lineage")
    lineage.add_argument("target", help="Kref URI of the revision")
    lineage.add_argument("--depth", type=int, default=5, help="Traversal depth (default: 5)")
    lineage.add_argument("--direction", choices=["upstream", "downstream", "both"], default="both", help="Direction of analysis")
    lineage.set_defaults(func=cmd_lineage)

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except TokenAcquisitionError as exc:
        parser.error(str(exc))
    except requests.HTTPError as exc:
        parser.error(f"KumihoClouds request failed: {exc}")


if __name__ == "__main__":
    main()
