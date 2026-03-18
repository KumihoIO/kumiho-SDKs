"""Tests for kumiho_cli package."""
from kumiho.auth_cli import ensure_token as auth_ensure_token

import pytest
from kumiho_cli import __version__
from kumiho_cli import ensure_token


def test_version():
    """Test that version is defined."""
    assert __version__ == "1.1.0"


def test_imports():
    """Test that main exports are available."""
    from kumiho_cli import ensure_token, TokenAcquisitionError, Credentials
    
    assert ensure_token is not None
    assert TokenAcquisitionError is not None
    assert Credentials is not None


def test_auth_helpers_delegate_to_sdk():
    """kumiho-cli should reuse the canonical auth implementation from kumiho."""
    assert ensure_token is auth_ensure_token
