"""Browser OAuth login (PKCE + loopback) and rotating-refresh behaviour.

A local fake authorization server stands in for control.kumiho.cloud. It
enforces what the real one does: S256 PKCE, exact state echo, loopback
redirect matching that ignores the port, one-time codes and rotating refresh
tokens whose reuse revokes the whole grant.
"""
from __future__ import annotations

import base64
import hashlib
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
import requests

from kumiho import auth_cli, oauth_login
from kumiho._token_loader import load_bearer_token


def _jwt(claims: dict) -> str:
    def enc(obj: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()

    return f"{enc({'alg': 'none'})}.{enc(claims)}.sig"


class FakeAuthorizationServer:
    def __init__(self) -> None:
        self.clients: dict[str, dict] = {}
        self.codes: dict[str, dict] = {}
        self.refresh: dict[str, dict] = {}  # token -> {"family", "rotated", "client_id"}
        self.revoked_families: set[str] = set()
        self.revocations: list[str] = []
        self.refresh_calls = 0
        self.issuer_override: str | None = None
        self.lock = threading.Lock()
        self._counter = 0
        server = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # silence
                pass

            def _json(self, status: int, body: dict) -> None:
                raw = json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _body(self) -> bytes:
                return self.rfile.read(int(self.headers.get("Content-Length") or 0))

            def do_GET(self):
                if self.path == "/.well-known/oauth-authorization-server":
                    base = server.base
                    self._json(
                        200,
                        {
                            "issuer": server.issuer_override or base,
                            "authorization_endpoint": f"{base}/oauth/authorize",
                            "token_endpoint": f"{base}/api/oauth/token",
                            "registration_endpoint": f"{base}/api/oauth/register",
                            "revocation_endpoint": f"{base}/api/oauth/revoke",
                            "code_challenge_methods_supported": ["S256"],
                            "authorization_response_iss_parameter_supported": True,
                        },
                    )
                else:
                    self._json(404, {"error": "not_found"})

            def do_POST(self):
                if self.path == "/api/oauth/register":
                    self._json(201, server.register(json.loads(self._body())))
                elif self.path == "/api/oauth/token":
                    form = {k: v[0] for k, v in parse_qs(self._body().decode()).items()}
                    status, body = server.token(form)
                    self._json(status, body)
                elif self.path == "/api/oauth/revoke":
                    form = {k: v[0] for k, v in parse_qs(self._body().decode()).items()}
                    server.revocations.append(form.get("token", ""))
                    self._json(200, {})
                else:
                    self._json(404, {"error": "not_found"})

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()

    def _next(self, prefix: str) -> str:
        with self.lock:
            self._counter += 1
            return f"{prefix}{self._counter}"

    def register(self, body: dict) -> dict:
        assert body["token_endpoint_auth_method"] == "none"
        client_id = self._next("dcr_")
        self.clients[client_id] = body
        return {"client_id": client_id, **body}

    def authorize(self, url: str) -> str:
        """Play the consent page: validate, then return the redirect URL."""
        params = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        client = self.clients[params["client_id"]]
        requested = urlsplit(params["redirect_uri"])
        registered = urlsplit(client["redirect_uris"][0])
        # Loopback match ignores the port (RFC 8252 §7.3).
        assert (requested.scheme, requested.hostname, requested.path) == (
            registered.scheme,
            registered.hostname,
            registered.path,
        )
        assert requested.port  # the client listens on a concrete port
        assert params["code_challenge_method"] == "S256"
        assert params["response_type"] == "code"
        code = self._next("code_")
        self.codes[code] = params
        query = urlencode({"code": code, "state": params["state"], "iss": self.base})
        return f"{params['redirect_uri']}?{query}"

    def _mint(self, client_id: str, family: str) -> dict:
        refresh = self._next("rt_")
        self.refresh[refresh] = {"family": family, "rotated": False, "client_id": client_id}
        access = _jwt(
            {"tenant_id": "t1", "email": "fox@example.com", "iss": self.base, "n": self._counter}
        )
        return {
            "access_token": access,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh,
            "scope": "memory offline_access",
        }

    def token(self, form: dict) -> tuple[int, dict]:
        if form["grant_type"] == "authorization_code":
            params = self.codes.pop(form["code"], None)
            if params is None:
                return 400, {"error": "invalid_grant"}
            digest = hashlib.sha256(form["code_verifier"].encode()).digest()
            challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
            if challenge != params["code_challenge"]:
                return 400, {"error": "invalid_grant", "error_description": "PKCE"}
            if form["redirect_uri"] != params["redirect_uri"]:
                return 400, {"error": "invalid_grant"}
            return 200, self._mint(form["client_id"], self._next("family_"))
        if form["grant_type"] == "refresh_token":
            with self.lock:
                self.refresh_calls += 1
                row = self.refresh.get(form["refresh_token"])
                if row is None or row["family"] in self.revoked_families:
                    return 400, {"error": "invalid_grant"}
                if row["rotated"]:
                    self.revoked_families.add(row["family"])
                    return 400, {"error": "invalid_grant", "error_description": "reused"}
                row["rotated"] = True
            return 200, self._mint(row["client_id"], row["family"])
        return 400, {"error": "unsupported_grant_type"}


@pytest.fixture
def fake_as():
    server = FakeAuthorizationServer()
    try:
        yield server
    finally:
        server.close()


@pytest.fixture
def cred_path(tmp_path, monkeypatch) -> Path:
    monkeypatch.setenv("KUMIHO_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("KUMIHO_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("KUMIHO_FIREBASE_ID_TOKEN", raising=False)
    return tmp_path / "kumiho_authentication.json"


def _browser(fake_as: FakeAuthorizationServer, *, tamper_state: bool = False):
    """An `announce` hook that follows the printed URL like a browser would."""

    def announce(message: str) -> None:
        url = message.split("\n", 1)[1]

        def visit() -> None:
            redirect = fake_as.authorize(url)
            if tamper_state:
                forged = redirect.replace("state=", "state=forged")
                requests.get(forged, timeout=5)
            requests.get(redirect, timeout=5)

        threading.Thread(target=visit, daemon=True).start()

    return announce


def _login(fake_as, cred_path, **kwargs):
    metadata = oauth_login.fetch_server_metadata(fake_as.base)
    client_id = oauth_login.register_client(metadata, "Test client")
    tokens = oauth_login.browser_login(
        metadata, client_id, open_browser=False, timeout=10, **kwargs
    )
    payload = oauth_login.build_credentials(metadata, client_id, "Test client", tokens)
    oauth_login.write_credentials_file(cred_path, payload)
    return payload


def test_pkce_pair_is_s256():
    verifier, challenge = oauth_login._pkce_pair()
    assert 43 <= len(verifier) <= 128
    digest = hashlib.sha256(verifier.encode()).digest()
    assert challenge == base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def test_metadata_rejects_mismatched_issuer(fake_as):
    fake_as.issuer_override = "https://evil.example"
    with pytest.raises(oauth_login.OAuthLoginError, match="does not match"):
        oauth_login.fetch_server_metadata(fake_as.base)


def test_metadata_rejects_plain_http_off_loopback():
    with pytest.raises(oauth_login.OAuthLoginError, match="https"):
        oauth_login.fetch_server_metadata("http://control.example.com")


def test_browser_login_round_trip_stores_oauth_credentials(fake_as, cred_path):
    payload = _login(fake_as, cred_path, announce=_browser(fake_as, tamper_state=True))

    stored = json.loads(cred_path.read_text())
    assert stored == payload
    assert stored["auth_type"] == "oauth"
    assert stored["email"] == "fox@example.com"
    assert stored["oauth"]["refresh_token"].startswith("rt_")
    assert stored["oauth"]["client_name"] == "Test client"
    # The SDK's bearer loader picks the OAuth access token with no id_token.
    assert load_bearer_token() == stored["control_plane_token"]
    # Firebase-only helpers ignore an OAuth login instead of misreading it.
    assert auth_cli._load_credentials() is None


def test_browser_login_reports_denied_consent(fake_as, cred_path):
    metadata = oauth_login.fetch_server_metadata(fake_as.base)
    client_id = oauth_login.register_client(metadata, "Test client")

    def deny(message: str) -> None:
        url = message.split("\n", 1)[1]
        params = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        query = urlencode(
            {"error": "access_denied", "state": params["state"], "iss": fake_as.base}
        )
        threading.Thread(
            target=lambda: requests.get(f"{params['redirect_uri']}?{query}", timeout=5),
            daemon=True,
        ).start()

    with pytest.raises(oauth_login.OAuthLoginError, match="access_denied"):
        oauth_login.browser_login(metadata, client_id, open_browser=False, timeout=10, announce=deny)


def test_browser_login_times_out(fake_as):
    metadata = oauth_login.fetch_server_metadata(fake_as.base)
    with pytest.raises(oauth_login.OAuthLoginError, match="timed out"):
        oauth_login.browser_login(
            metadata, "dcr_x", open_browser=False, timeout=1.5, announce=lambda _m: None
        )


def _expire(cred_path: Path) -> None:
    data = json.loads(cred_path.read_text())
    data["cp_expires_at"] = int(time.time()) - 10
    data["cp_issued_at"] = int(time.time()) - 4000
    cred_path.write_text(json.dumps(data))


def test_ensure_token_uses_fresh_oauth_token_without_network(fake_as, cred_path):
    payload = _login(fake_as, cred_path, announce=_browser(fake_as))
    token, source = auth_cli.ensure_token(interactive=False)
    assert token == payload["control_plane_token"]
    assert source == "cached oauth credentials"
    assert fake_as.refresh_calls == 0


def test_ensure_token_rotates_expired_oauth_token(fake_as, cred_path):
    payload = _login(fake_as, cred_path, announce=_browser(fake_as))
    _expire(cred_path)

    token, source = auth_cli.ensure_token(interactive=False)

    stored = json.loads(cred_path.read_text())
    assert source == "refreshed oauth credentials"
    assert token == stored["control_plane_token"] != payload["control_plane_token"]
    assert stored["oauth"]["refresh_token"] != payload["oauth"]["refresh_token"]
    assert stored["cp_expires_at"] > time.time() + 3000


def test_concurrent_refreshes_rotate_once(fake_as, cred_path):
    """Many processes hitting expiry together must not trip reuse detection."""
    _login(fake_as, cred_path, announce=_browser(fake_as))
    _expire(cred_path)

    results: list[str] = []
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            results.append(auth_cli.ensure_token(interactive=False)[0])
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert fake_as.refresh_calls == 1
    assert not fake_as.revoked_families
    assert len(set(results)) == 1


def test_forced_refresh_reuses_a_token_rotated_moments_ago(fake_as, cred_path):
    _login(fake_as, cred_path, announce=_browser(fake_as))
    _expire(cred_path)
    first, _ = auth_cli.ensure_token(interactive=False)
    # A second UNAUTHENTICATED retry right after must not rotate again.
    again, _ = auth_cli.ensure_token(interactive=False, force_refresh=True)
    assert again == first
    assert fake_as.refresh_calls == 1


def test_revoked_grant_asks_for_a_new_login(fake_as, cred_path):
    _login(fake_as, cred_path, announce=_browser(fake_as))
    fake_as.revoked_families.update(row["family"] for row in fake_as.refresh.values())
    _expire(cred_path)
    with pytest.raises(auth_cli.TokenAcquisitionError, match="login --oauth"):
        auth_cli.ensure_token(interactive=False)


def test_transient_refresh_failure_keeps_a_still_valid_token(fake_as, cred_path, monkeypatch):
    payload = _login(fake_as, cred_path, announce=_browser(fake_as))
    data = json.loads(cred_path.read_text())
    data["cp_expires_at"] = int(time.time()) + 60  # inside the refresh grace window
    cred_path.write_text(json.dumps(data))

    def offline(*_a, **_k):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(oauth_login.requests, "post", offline)
    token, source = auth_cli.ensure_token(interactive=False)
    assert token == payload["control_plane_token"]
    assert source == "cached oauth credentials"


def test_login_replaces_and_revokes_a_previous_oauth_grant(fake_as, cred_path, monkeypatch):
    first = _login(fake_as, cred_path, announce=_browser(fake_as))
    monkeypatch.setattr(
        oauth_login,
        "browser_login",
        lambda metadata, client_id, **kw: oauth_login.OAuthTokens(
            access_token=_jwt({"tenant_id": "t1"}),
            refresh_token="rt_new",
            expires_at=int(time.time()) + 3600,
            scope="memory offline_access",
        ),
    )
    payload = oauth_login.login(cred_path, fake_as.base, client_name="Kumiho for Tests")
    assert payload["oauth"]["refresh_token"] == "rt_new"
    assert payload["oauth"]["client_name"] == "Kumiho for Tests"
    assert fake_as.revocations == [first["oauth"]["refresh_token"]]


def test_cli_login_oauth_flag_runs_browser_login(fake_as, cred_path, monkeypatch, capsys):
    monkeypatch.setenv("KUMIHO_CONTROL_PLANE_API_URL", fake_as.base)
    seen = {}

    def fake_login(path, issuer, **kwargs):
        seen.update(path=path, issuer=issuer, **kwargs)
        return {"email": "fox@example.com"}

    monkeypatch.setattr(oauth_login, "login", fake_login)
    auth_cli.main(["login", "--oauth", "--no-browser", "--client-name", "Kumiho Memory for Codex"])
    assert seen["issuer"] == fake_as.base
    assert seen["open_browser"] is False
    assert seen["client_name"] == "Kumiho Memory for Codex"
    assert "Signed in with OAuth as fox@example.com" in capsys.readouterr().out
