"""Regression tests for issue #22: the auto-login interceptor must never
open an interactive prompt in headless processes, and must not treat
PERMISSION_DENIED (authorization/immutability) as a login problem."""

from unittest.mock import MagicMock, patch

import grpc

from kumiho.client import _AutoLoginInterceptor, _interactive_login_allowed


def _response_with(code, details=""):
    response = MagicMock()
    response.code.return_value = code
    response.details.return_value = details
    return response


def _call_details():
    details = MagicMock()
    details.metadata = []
    details.method = "/kumiho.Kumiho/TagRevision"
    details.timeout = None
    details.credentials = None
    return details


class TestInteractiveLoginAllowed:
    def test_false_when_stdin_not_a_tty(self):
        with patch("kumiho.client.sys") as mock_sys:
            mock_sys.stdin.isatty.return_value = False
            assert _interactive_login_allowed() is False

    def test_true_on_a_real_tty(self):
        with patch("kumiho.client.sys") as mock_sys, \
             patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop("KUMIHO_NO_INTERACTIVE_LOGIN", None)
            mock_sys.stdin.isatty.return_value = True
            assert _interactive_login_allowed() is True

    def test_env_override_wins_over_tty(self):
        with patch("kumiho.client.sys") as mock_sys, \
             patch.dict("os.environ", {"KUMIHO_NO_INTERACTIVE_LOGIN": "1"}):
            mock_sys.stdin.isatty.return_value = True
            assert _interactive_login_allowed() is False

    def test_false_when_stdin_missing(self):
        with patch("kumiho.client.sys") as mock_sys:
            mock_sys.stdin = None
            assert _interactive_login_allowed() is False


class TestAutoLoginInterceptor:
    def test_permission_denied_never_triggers_login(self):
        """PERMISSION_DENIED fires on immutable-revision tag rejections —
        prompting for login there hung MCP servers for 60s+ per call."""
        interceptor = _AutoLoginInterceptor()
        response = _response_with(grpc.StatusCode.PERMISSION_DENIED)

        with patch("kumiho.auth_cli.ensure_token") as mock_ensure:
            result = interceptor.intercept_unary_unary(
                lambda details, request: response, _call_details(), MagicMock(),
            )

        mock_ensure.assert_not_called()
        assert result is response

    def test_unauthenticated_refreshes_without_prompt_when_headless(self):
        interceptor = _AutoLoginInterceptor()
        response = _response_with(grpc.StatusCode.UNAUTHENTICATED)

        with patch("kumiho.client._interactive_login_allowed", return_value=False), \
             patch("kumiho.auth_cli.ensure_token", side_effect=RuntimeError("no creds")) as mock_ensure:
            result = interceptor.intercept_unary_unary(
                lambda details, request: response, _call_details(), MagicMock(),
            )

        mock_ensure.assert_called_once_with(interactive=False, force_refresh=True)
        # Failed silent refresh returns the original response instead of hanging.
        assert result is response

    def test_unauthenticated_retries_with_refreshed_token(self):
        interceptor = _AutoLoginInterceptor()
        bad = _response_with(grpc.StatusCode.UNAUTHENTICATED)
        good = _response_with(grpc.StatusCode.OK)
        calls = []

        def continuation(details, request):
            calls.append(details)
            return bad if len(calls) == 1 else good

        with patch("kumiho.client._interactive_login_allowed", return_value=False), \
             patch("kumiho.auth_cli.ensure_token", return_value=("new-token", "refreshed")):
            result = interceptor.intercept_unary_unary(
                continuation, _call_details(), MagicMock(),
            )

        assert result is good
        retried_metadata = dict(calls[1].metadata)
        assert retried_metadata.get("authorization") == "Bearer new-token"
