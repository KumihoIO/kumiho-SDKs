"""Tests for kumiho_cli package."""
import pytest
from kumiho_cli import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ == "1.0.0"


def test_imports():
    """Test that main exports are available."""
    from kumiho_cli import ensure_token, TokenAcquisitionError, Credentials
    
    assert ensure_token is not None
    assert TokenAcquisitionError is not None
    assert Credentials is not None
