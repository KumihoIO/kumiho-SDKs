"""Browser OAuth login for Kumiho Cloud (authorization code + PKCE, loopback).

``kumiho-auth login --oauth`` signs in through the control plane's OAuth
authorization server — the same consent page the hosted MCP connector at
``https://mcp.kumiho.cloud/mcp`` uses — instead of typing a password into the
terminal. The flow follows RFC 8252 for native apps:

1. Read the authorization server metadata (RFC 8414) and check its issuer.
2. Register a public client once via dynamic client registration (RFC 7591)
   with the loopback redirect ``http://127.0.0.1/callback``; the server ignores
   the port when matching loopback redirects (RFC 8252 §7.3).
3. Listen on an ephemeral ``127.0.0.1`` port, open the consent page with a
   PKCE S256 challenge and a random ``state``, and wait for the redirect.
4. Exchange the code for an access token (a control-plane JWT that discovery
   and kumiho-server accept directly) and a rotating refresh token.

The result is stored in ``kumiho_authentication.json`` with
``"auth_type": "oauth"``. :func:`kumiho.auth_cli.ensure_token` refreshes it.
Refresh tokens rotate and a reused one revokes the whole grant, so every
refresh happens under a cross-process lock and always presents the newest
refresh token on disk: the MCP server, hooks and other hosts share this file.
"""
from __future__ import annotations

import base64
import contextlib
import hashlib
import html
import http.server
import json
import os
import secrets
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, Optional
from urllib.parse import parse_qs, urlencode, urlsplit

import requests

AUTH_TYPE_OAUTH = "oauth"
DEFAULT_SCOPE = "memory offline_access"
DEFAULT_CLIENT_NAME = "Kumiho SDK"
REDIRECT_PATH = "/callback"
REGISTERED_REDIRECT_URI = f"http://127.0.0.1{REDIRECT_PATH}"
DEFAULT_LOGIN_TIMEOUT_SECONDS = 300
LOCK_TIMEOUT_SECONDS = 30.0
HTTP_TIMEOUT_SECONDS = 15
#: A token another process minted this recently is reused by a forced refresh
#: instead of rotating again (see :func:`refresh_access_token`).
RECENT_REFRESH_SECONDS = 30


class OAuthLoginError(RuntimeError):
    """Raised when the browser login or a token refresh cannot complete."""


class OAuthGrantRevoked(OAuthLoginError):
    """The refresh token was rejected; the user must sign in again."""


@dataclass(frozen=True)
class ServerMetadata:
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    registration_endpoint: Optional[str]
    revocation_endpoint: Optional[str]


@dataclass(frozen=True)
class OAuthTokens:
    access_token: str
    refresh_token: str
    expires_at: int
    scope: str


# ---------------------------------------------------------------------------
# Metadata and client registration
# ---------------------------------------------------------------------------


def _is_loopback_host(host: Optional[str]) -> bool:
    return (host or "").lower() in {"localhost", "127.0.0.1", "::1", "[::1]"}


def _require_secure_url(url: str, field: str) -> str:
    parts = urlsplit(url)
    if parts.scheme == "https" and parts.hostname:
        return url
    if parts.scheme == "http" and _is_loopback_host(parts.hostname):
        # Only a local test authorization server may use plain http.
        return url
    raise OAuthLoginError(f"authorization server {field} must use https: {url!r}")


def fetch_server_metadata(issuer: str) -> ServerMetadata:
    """Fetch RFC 8414 metadata for *issuer* and verify it names itself."""
    issuer = _require_secure_url(issuer.rstrip("/"), "issuer")
    url = f"{issuer}/.well-known/oauth-authorization-server"
    try:
        resp = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise OAuthLoginError(f"could not read OAuth metadata from {url}: {exc}") from exc
    if not isinstance(data, dict):
        raise OAuthLoginError("OAuth metadata is not a JSON object")

    # RFC 8414 §3.3: the metadata must name the issuer it was fetched for.
    if str(data.get("issuer", "")).rstrip("/") != issuer:
        raise OAuthLoginError(
            f"OAuth metadata issuer {data.get('issuer')!r} does not match {issuer!r}"
        )
    methods = data.get("code_challenge_methods_supported") or []
    if "S256" not in methods:
        raise OAuthLoginError("authorization server does not support PKCE S256")

    def endpoint(name: str, required: bool) -> Optional[str]:
        value = data.get(name)
        if not value:
            if required:
                raise OAuthLoginError(f"OAuth metadata is missing {name}")
            return None
        return _require_secure_url(str(value), name)

    return ServerMetadata(
        issuer=issuer,
        authorization_endpoint=endpoint("authorization_endpoint", True) or "",
        token_endpoint=endpoint("token_endpoint", True) or "",
        registration_endpoint=endpoint("registration_endpoint", False),
        revocation_endpoint=endpoint("revocation_endpoint", False),
    )


def register_client(metadata: ServerMetadata, client_name: str) -> str:
    """Register a public loopback client (RFC 7591) and return its client_id."""
    if not metadata.registration_endpoint:
        raise OAuthLoginError("authorization server does not offer client registration")
    body = {
        "client_name": client_name,
        "redirect_uris": [REGISTERED_REDIRECT_URI],
        "token_endpoint_auth_method": "none",
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "scope": DEFAULT_SCOPE,
    }
    try:
        resp = requests.post(
            metadata.registration_endpoint, json=body, timeout=HTTP_TIMEOUT_SECONDS
        )
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise OAuthLoginError(f"client registration failed: {exc}") from exc
    if resp.status_code >= 400 or not isinstance(data, dict) or not data.get("client_id"):
        raise OAuthLoginError(f"client registration failed: {_describe_error(resp, data)}")
    return str(data["client_id"])


# ---------------------------------------------------------------------------
# PKCE and the loopback redirect
# ---------------------------------------------------------------------------


def _pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)  # 86 chars, within RFC 7636's 43..128
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


_PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Kumiho</title>
<style>body{{font-family:system-ui,sans-serif;max-width:32rem;margin:15vh auto;
padding:0 1rem;color:#222}}</style></head><body><h1>{title}</h1><p>{body}</p>
</body></html>"""


class _CallbackServer(http.server.HTTPServer):
    """Loopback listener that captures exactly one matching redirect."""

    def __init__(self, expected_state: str) -> None:
        super().__init__(("127.0.0.1", 0), _CallbackHandler)
        self.expected_state = expected_state
        self.result: Optional[Dict[str, str]] = None
        self.done = threading.Event()

    @property
    def redirect_uri(self) -> str:
        return f"http://127.0.0.1:{self.server_address[1]}{REDIRECT_PATH}"


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    server: _CallbackServer
    # Drop idle connections (browser preconnects) instead of blocking the loop.
    timeout = 5

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        parts = urlsplit(self.path)
        if parts.path != REDIRECT_PATH or self.server.done.is_set():
            self._reply(404, "Not found", "This address only accepts the Kumiho sign-in redirect.")
            return
        params = {k: v[0] for k, v in parse_qs(parts.query).items() if v}
        if params.get("state") != self.server.expected_state:
            # A redirect without our state is not ours; keep waiting for it.
            self._reply(400, "Sign-in not recognised", "This redirect does not match the sign-in in progress.")
            return
        self.server.result = params
        self.server.done.set()
        if "error" in params:
            self._reply(400, "Sign-in was not completed", "You can close this window and return to the terminal.")
        else:
            self._reply(200, "Kumiho is connected", "You can close this window and return to the terminal.")

    def _reply(self, status: int, title: str, body: str) -> None:
        page = _PAGE.format(title=html.escape(title), body=html.escape(body)).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        # The query string carries the authorization code; never log it.
        pass


def _describe_error(resp: Optional[requests.Response], data: Any) -> str:
    if isinstance(data, dict) and data.get("error"):
        desc = data.get("error_description")
        return f"{data['error']}: {desc}" if desc else str(data["error"])
    return f"HTTP {resp.status_code}" if resp is not None else "no response"


def _token_request(metadata_token_endpoint: str, form: Dict[str, str]) -> OAuthTokens:
    try:
        resp = requests.post(
            metadata_token_endpoint,
            data=form,
            headers={"Accept": "application/json"},
            timeout=HTTP_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise OAuthLoginError(f"token request failed: {exc}") from exc
    try:
        data = resp.json()
    except ValueError:
        data = None
    if resp.status_code >= 400 or not isinstance(data, dict):
        if isinstance(data, dict) and data.get("error") == "invalid_grant":
            raise OAuthGrantRevoked(_describe_error(resp, data))
        raise OAuthLoginError(f"token request failed: {_describe_error(resp, data)}")
    access = data.get("access_token")
    refresh = data.get("refresh_token") or form.get("refresh_token")
    if not access or not refresh:
        raise OAuthLoginError("token response is missing access_token or refresh_token")
    expires_in = int(data.get("expires_in") or 3600)
    return OAuthTokens(
        access_token=str(access),
        refresh_token=str(refresh),
        expires_at=int(time.time()) + expires_in,
        scope=str(data.get("scope") or form.get("scope") or DEFAULT_SCOPE),
    )


def browser_login(
    metadata: ServerMetadata,
    client_id: str,
    *,
    open_browser: bool = True,
    timeout: float = DEFAULT_LOGIN_TIMEOUT_SECONDS,
    announce: Callable[[str], None] = lambda message: print(message, file=sys.stderr, flush=True),
) -> OAuthTokens:
    """Run the consent-page round trip and return the issued tokens."""
    verifier, challenge = _pkce_pair()
    state = secrets.token_urlsafe(32)
    server = _CallbackServer(state)
    server.timeout = 1.0
    try:
        redirect_uri = server.redirect_uri
        query = urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": DEFAULT_SCOPE,
                "state": state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            }
        )
        authorize_url = f"{metadata.authorization_endpoint}?{query}"
        announce(
            "[kumiho-auth] Sign in to Kumiho Cloud in your browser. If it does not open, "
            f"visit:\n{authorize_url}"
        )
        if open_browser:
            with contextlib.suppress(Exception):
                webbrowser.open(authorize_url, new=1, autoraise=True)

        deadline = time.monotonic() + timeout
        while not server.done.is_set():
            if time.monotonic() >= deadline:
                raise OAuthLoginError(
                    f"timed out after {int(timeout)}s waiting for the browser sign-in"
                )
            server.handle_request()
        result = server.result or {}
    finally:
        server.server_close()

    if "error" in result:
        desc = result.get("error_description")
        raise OAuthLoginError(
            f"sign-in was not completed: {result['error']}" + (f" ({desc})" if desc else "")
        )
    # RFC 9207: when the server reports its issuer, it must be the one we asked.
    iss = result.get("iss")
    if iss is not None and iss.rstrip("/") != metadata.issuer:
        raise OAuthLoginError("authorization response came from an unexpected issuer")
    code = result.get("code")
    if not code:
        raise OAuthLoginError("authorization response did not include a code")

    return _token_request(
        metadata.token_endpoint,
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": verifier,
        },
    )


# ---------------------------------------------------------------------------
# Credential file: locking, persistence, refresh
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def credentials_lock(path: Path, timeout: float = LOCK_TIMEOUT_SECONDS) -> Iterator[None]:
    """Hold an exclusive cross-process lock beside the credential file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o600)
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                _lock_fd(fd)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise OAuthLoginError(f"timed out waiting for {lock_path}")
                time.sleep(0.05)
        try:
            yield
        finally:
            _unlock_fd(fd)
    finally:
        os.close(fd)


if os.name == "nt":
    import msvcrt

    def _lock_fd(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)

    def _unlock_fd(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _lock_fd(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock_fd(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)


def read_credentials_file(path: Path) -> Optional[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def write_credentials_file(path: Path, payload: Dict[str, Any]) -> None:
    """Replace the credential file atomically with owner-only permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{secrets.token_hex(4)}.tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        # Windows refuses to replace a file another process has open for a
        # moment (a plain reader). Losing a rotated refresh token here would
        # break the grant, so wait that reader out.
        for attempt in range(40):
            try:
                os.replace(tmp, path)
                break
            except PermissionError:
                if os.name != "nt" or attempt == 39:
                    raise
                time.sleep(0.05)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise
    with contextlib.suppress(OSError):
        os.chmod(path, 0o600)


def is_oauth_credentials(data: Optional[Dict[str, Any]]) -> bool:
    return bool(
        data
        and data.get("auth_type") == AUTH_TYPE_OAUTH
        and isinstance(data.get("oauth"), dict)
        and data["oauth"].get("refresh_token")
        and data["oauth"].get("token_endpoint")
        and data["oauth"].get("client_id")
    )


def _jwt_claims(token: str) -> Dict[str, Any]:
    try:
        payload = token.split(".")[1]
        decoded = base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4))
        claims = json.loads(decoded)
    except (IndexError, ValueError):
        return {}
    return claims if isinstance(claims, dict) else {}


def build_credentials(
    metadata: ServerMetadata, client_id: str, client_name: str, tokens: OAuthTokens
) -> Dict[str, Any]:
    claims = _jwt_claims(tokens.access_token)
    return {
        "auth_type": AUTH_TYPE_OAUTH,
        "email": claims.get("email"),
        "project_id": None,
        "control_plane_token": tokens.access_token,
        "cp_expires_at": tokens.expires_at,
        "cp_issued_at": int(time.time()),
        "oauth": {
            "issuer": metadata.issuer,
            "token_endpoint": metadata.token_endpoint,
            "revocation_endpoint": metadata.revocation_endpoint,
            "client_id": client_id,
            "client_name": client_name,
            "refresh_token": tokens.refresh_token,
            "scope": tokens.scope,
        },
    }


def access_token_is_fresh(data: Dict[str, Any], grace_seconds: int) -> bool:
    token = data.get("control_plane_token")
    try:
        expires_at = int(data.get("cp_expires_at") or 0)
    except (TypeError, ValueError):
        return False
    return bool(token) and expires_at - int(time.time()) > grace_seconds


def refresh_access_token(
    path: Path,
    *,
    grace_seconds: int,
    force_refresh: bool = False,
    seen_access_token: Optional[str] = None,
) -> str:
    """Return a usable access token, rotating the refresh token if needed.

    Runs under :func:`credentials_lock` and re-reads the file inside it, so a
    refresh another process just completed is reused instead of repeated with
    an already-rotated refresh token (which would revoke the whole grant).
    """
    with credentials_lock(path):
        data = read_credentials_file(path)
        if not is_oauth_credentials(data):
            raise OAuthGrantRevoked("OAuth credentials are no longer on file")
        assert data is not None
        current = data.get("control_plane_token")
        if access_token_is_fresh(data, grace_seconds):
            if not force_refresh:
                return str(current)
            # A forced refresh reuses a token another process rotated in
            # after the caller last looked, or one minted moments ago.
            issued_at = int(data.get("cp_issued_at") or 0)
            if (seen_access_token and current != seen_access_token) or (
                time.time() - issued_at < RECENT_REFRESH_SECONDS
            ):
                return str(current)

        oauth = data["oauth"]
        _require_secure_url(str(oauth["token_endpoint"]), "token_endpoint")
        form = {
            "grant_type": "refresh_token",
            "refresh_token": str(oauth["refresh_token"]),
            "client_id": str(oauth["client_id"]),
        }
        tokens = _token_request(str(oauth["token_endpoint"]), form)
        # Persist the rotated refresh token before anything else can fail.
        data["control_plane_token"] = tokens.access_token
        data["cp_expires_at"] = tokens.expires_at
        data["cp_issued_at"] = int(time.time())
        oauth["refresh_token"] = tokens.refresh_token
        oauth["scope"] = tokens.scope
        write_credentials_file(path, data)
        return tokens.access_token


def login(
    path: Path,
    issuer: str,
    *,
    client_name: str = DEFAULT_CLIENT_NAME,
    open_browser: bool = True,
    timeout: float = DEFAULT_LOGIN_TIMEOUT_SECONDS,
) -> Dict[str, Any]:
    """Sign in through the browser and store OAuth credentials at *path*."""
    metadata = fetch_server_metadata(issuer)
    # A fresh registration per login: a cached client_id the server has since
    # dropped would fail on the consent page, where this process cannot see it.
    client_id = register_client(metadata, client_name)
    tokens = browser_login(metadata, client_id, open_browser=open_browser, timeout=timeout)
    payload = build_credentials(metadata, client_id, client_name, tokens)
    with credentials_lock(path):
        previous = read_credentials_file(path)
        write_credentials_file(path, payload)
    if is_oauth_credentials(previous):
        assert previous is not None
        revoke_refresh_token(previous["oauth"])
    return payload


def revoke_refresh_token(oauth: Dict[str, Any]) -> bool:
    """Best-effort RFC 7009 revocation of a stored grant; True when accepted."""
    endpoint = oauth.get("revocation_endpoint")
    if not endpoint or not oauth.get("refresh_token"):
        return False
    try:
        _require_secure_url(str(endpoint), "revocation_endpoint")
        resp = requests.post(
            str(endpoint),
            data={
                "token": str(oauth["refresh_token"]),
                "token_type_hint": "refresh_token",
                "client_id": str(oauth.get("client_id") or ""),
            },
            timeout=HTTP_TIMEOUT_SECONDS,
        )
    except (OAuthLoginError, requests.RequestException):
        return False
    return resp.status_code < 400
