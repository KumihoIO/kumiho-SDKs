"""Regressions from the adversarial review of the browser OAuth sign-in.

Reuses the fake authorization server and helpers of ``test_oauth_login``.
"""
from __future__ import annotations

import json
import socket
import threading
import time
from urllib.parse import parse_qs, urlencode, urlsplit

import grpc
import pytest
import requests

from kumiho import auth_cli, oauth_login
from kumiho import client as client_mod
from test_oauth_login import _browser, _expire, _login, cred_path, fake_as  # noqa: F401


def test_missing_iss_is_rejected_when_the_server_advertises_it(fake_as):
    metadata = oauth_login.fetch_server_metadata(fake_as.base)
    assert metadata.iss_parameter_supported
    client_id = oauth_login.register_client(metadata, "Test client")

    def strip_iss(message: str) -> None:
        url = message.split("\n", 1)[1]
        parts = urlsplit(fake_as.authorize(url))
        params = {k: v[0] for k, v in parse_qs(parts.query).items() if k != "iss"}
        stripped = f"{parts.scheme}://{parts.netloc}{parts.path}?{urlencode(params)}"
        threading.Thread(target=lambda: requests.get(stripped, timeout=5), daemon=True).start()

    with pytest.raises(oauth_login.OAuthLoginError, match="missing the iss"):
        oauth_login.browser_login(
            metadata, client_id, open_browser=False, timeout=10, announce=strip_iss
        )


def test_a_stalled_local_connection_does_not_block_the_redirect(fake_as, cred_path):
    stalled: list[socket.socket] = []

    def stall_then_visit(message: str) -> None:
        url = message.split("\n", 1)[1]
        port = urlsplit(parse_qs(urlsplit(url).query)["redirect_uri"][0]).port
        conn = socket.create_connection(("127.0.0.1", port))
        conn.sendall(b"GET /callback?state=")  # never finishes the request line
        stalled.append(conn)
        redirect = fake_as.authorize(url)
        threading.Thread(target=lambda: requests.get(redirect, timeout=5), daemon=True).start()

    started = time.monotonic()
    try:
        payload = _login(fake_as, cred_path, announce=stall_then_visit)
    finally:
        for conn in stalled:
            conn.close()
    assert payload["oauth"]["refresh_token"].startswith("rt_")
    assert time.monotonic() - started < 4


def test_a_rejected_code_is_a_failed_login_not_a_revoked_grant(fake_as):
    metadata = oauth_login.fetch_server_metadata(fake_as.base)
    client_id = oauth_login.register_client(metadata, "Test client")

    def lose_the_code(message: str) -> None:
        redirect = fake_as.authorize(message.split("\n", 1)[1])
        fake_as.codes.clear()  # the server no longer knows the code
        threading.Thread(target=lambda: requests.get(redirect, timeout=5), daemon=True).start()

    with pytest.raises(oauth_login.OAuthLoginError) as exc:
        oauth_login.browser_login(
            metadata, client_id, open_browser=False, timeout=10, announce=lose_the_code
        )
    assert not isinstance(exc.value, oauth_login.OAuthGrantRevoked)


def test_requests_never_carry_netrc_credentials(fake_as, monkeypatch):
    seen = []
    real_get = requests.get

    def spy_get(url, **kwargs):
        seen.append(kwargs.get("auth"))
        return real_get(url, **kwargs)

    monkeypatch.setattr(oauth_login.requests, "get", spy_get)
    oauth_login.fetch_server_metadata(fake_as.base)
    # A callable auth stops requests from falling back to ~/.netrc Basic auth.
    assert seen and all(callable(auth) for auth in seen)
    prepared = requests.Request("POST", fake_as.base, auth=seen[0]).prepare()
    assert "Authorization" not in prepared.headers


def test_forced_refresh_rotates_only_the_token_the_server_rejected(fake_as, cred_path):
    _login(fake_as, cred_path, announce=_browser(fake_as))
    data = json.loads(cred_path.read_text())
    data["cp_issued_at"] = int(time.time()) - 600  # outside the recent window
    cred_path.write_text(json.dumps(data))
    current = data["control_plane_token"]

    # A stale token from an old channel was rejected; the file already holds a
    # newer one, so nothing rotates.
    token, _ = auth_cli.ensure_token(
        interactive=False, force_refresh=True, rejected_token="stale.jwt.token"
    )
    assert token == current
    assert fake_as.refresh_calls == 0

    # The stored token itself was rejected: rotate.
    token, _ = auth_cli.ensure_token(
        interactive=False, force_refresh=True, rejected_token=current
    )
    assert token != current
    assert fake_as.refresh_calls == 1


def test_a_blocked_replace_falls_back_to_an_in_place_write(tmp_path, monkeypatch):
    path = tmp_path / "kumiho_authentication.json"
    path.write_text("{}")

    def refuse(*_a, **_k):
        raise PermissionError("held open by another process")

    monkeypatch.setattr(oauth_login.os, "replace", refuse)
    monkeypatch.setattr(oauth_login.time, "sleep", lambda _s: None)
    oauth_login.write_credentials_file(path, {"auth_type": "oauth", "x": 1})
    assert json.loads(path.read_text()) == {"auth_type": "oauth", "x": 1}
    assert [p.name for p in tmp_path.iterdir()] == ["kumiho_authentication.json"]


def test_an_unwritable_store_surfaces_as_token_acquisition_error(fake_as, cred_path, monkeypatch):
    _login(fake_as, cred_path, announce=_browser(fake_as))
    _expire(cred_path)

    def unwritable(*_a, **_k):
        raise oauth_login.OAuthLoginError("cannot write: disk full")

    monkeypatch.setattr(oauth_login, "write_credentials_file", unwritable)
    with pytest.raises(auth_cli.TokenAcquisitionError):
        auth_cli.ensure_token(interactive=False)


def test_interactive_relogin_uses_the_stored_issuer_and_wraps_failures(
    fake_as, cred_path, monkeypatch
):
    _login(fake_as, cred_path, announce=_browser(fake_as))
    fake_as.revoked_families.update(row["family"] for row in fake_as.refresh.values())
    _expire(cred_path)
    monkeypatch.setenv("KUMIHO_CONTROL_PLANE_API_URL", "https://elsewhere.invalid")
    seen = {}

    def failing_login(path, issuer, **kwargs):
        seen["issuer"] = issuer
        raise oauth_login.OAuthLoginError("timed out waiting for the browser sign-in")

    monkeypatch.setattr(oauth_login, "login", failing_login)
    with pytest.raises(auth_cli.TokenAcquisitionError, match="sign-in failed"):
        auth_cli.ensure_token(interactive=True)
    assert seen["issuer"] == fake_as.base


def test_password_login_replaces_the_file_atomically_and_retires_the_grant(
    fake_as, cred_path, monkeypatch
):
    first = _login(fake_as, cred_path, announce=_browser(fake_as))
    locked = []
    real_lock = oauth_login.credentials_lock

    def spy_lock(path, *args, **kwargs):
        locked.append(path)
        return real_lock(path, *args, **kwargs)

    monkeypatch.setattr(oauth_login, "credentials_lock", spy_lock)
    creds = auth_cli.Credentials(
        api_key="k",
        email="fox@example.com",
        refresh_token="fb",
        id_token="a.b.c",
        expires_at=int(time.time()) + 3600,
    )
    auth_cli._save_credentials(creds)

    assert locked == [cred_path]
    assert json.loads(cred_path.read_text())["api_key"] == "k"
    assert fake_as.revocations == [first["oauth"]["refresh_token"]]


def test_fixed_port_is_used_for_the_redirect(fake_as, cred_path):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    seen = {}

    def visit(message: str) -> None:
        url = message.split("\n", 1)[1]
        seen["redirect_uri"] = parse_qs(urlsplit(url).query)["redirect_uri"][0]
        _browser(fake_as)(message)

    _login(fake_as, cred_path, announce=visit, port=port)
    assert seen["redirect_uri"] == f"http://127.0.0.1:{port}/callback"


def test_auto_login_names_the_rejected_token_and_updates_the_channel(monkeypatch):
    class Response:
        def __init__(self, code):
            self._code = code

        def code(self):
            return self._code

        def details(self):
            return ""

    injector = client_mod._MetadataInjector(
        [("authorization", "Bearer old.jwt.token"), ("x-tenant", "t1")]
    )
    interceptor = client_mod._AutoLoginInterceptor(injector)
    calls = []

    def continuation(details, request):
        calls.append(dict(details.metadata))
        return Response(
            grpc.StatusCode.UNAUTHENTICATED if len(calls) == 1 else grpc.StatusCode.OK
        )

    seen = {}
    monkeypatch.setattr(
        auth_cli,
        "ensure_token",
        lambda **kw: seen.update(kw) or ("new.jwt.token", "refreshed"),
    )
    monkeypatch.setattr(client_mod, "_interactive_login_allowed", lambda: False)
    details = client_mod._ClientCallDetails(
        method="/m",
        timeout=None,
        metadata=list(injector._metadata),
        credentials=None,
        wait_for_ready=None,
        compression=None,
    )
    interceptor.intercept_unary_unary(continuation, details, object())

    assert seen["rejected_token"] == "old.jwt.token"
    assert calls[1]["authorization"] == "Bearer new.jwt.token"
    assert dict(injector._metadata) == {
        "authorization": "Bearer new.jwt.token",
        "x-tenant": "t1",
    }
