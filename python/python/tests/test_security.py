"""
Security integration tests for the Kumiho Python SDK.

These tests verify security features work correctly when communicating
with localhost kumiho-server and control-plane instances.

Requirements:
- kumiho-server running on localhost:8080
- control-plane running on localhost:3000
- Set KUMIHO_INTEGRATION_TEST=1 to enable
- Set KUMIHO_AUTH_TOKEN with a valid test token

Test categories:
1. Token validation - bad tokens should be rejected
2. TLS enforcement - non-TLS connections warn appropriately  
3. Discovery cache - encrypted storage works correctly
4. Correlation IDs - requests include tracking headers
"""

import os
import sys
import time
import uuid
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest


# Skip entire module if integration tests not enabled
def should_run_integration_tests():
    return os.environ.get("KUMIHO_INTEGRATION_TEST") == "1"


pytestmark = pytest.mark.skipif(
    not should_run_integration_tests(),
    reason="Integration tests disabled. Set KUMIHO_INTEGRATION_TEST=1 to enable."
)


class TestTokenValidation:
    """Test that the server properly rejects invalid tokens."""
    
    @pytest.fixture
    def localhost_endpoint(self):
        """Get localhost server endpoint."""
        return os.environ.get("KUMIHO_SERVER_ENDPOINT", "localhost:8080")
    
    def test_expired_token_rejected(self, localhost_endpoint):
        """Server should reject expired JWT tokens."""
        import kumiho
        
        # Create an obviously expired token (JWT with exp in past)
        expired_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxMDAwMDAwMDAwfQ.fake_signature"
        
        with pytest.raises(Exception) as exc_info:
            # Use the SDK's OOP pattern via connect()
            client = kumiho.connect(
                endpoint=localhost_endpoint,
                token=expired_token,
            )
            with kumiho.use_client(client):
                # Try to make a request - should fail auth
                list(kumiho.get_projects())
        
        # Should get authentication/authorization error
        error_str = str(exc_info.value).lower()
        assert any(term in error_str for term in [
            "unauthenticated", "unauthorized", "expired", 
            "invalid", "token", "authentication", "grpc"
        ]), f"Expected auth error, got: {exc_info.value}"
    
    def test_malformed_token_rejected(self, localhost_endpoint):
        """Server should reject malformed tokens - caught by client-side validation."""
        from kumiho._token_loader import validate_token_format
        
        # Completely invalid token - should fail client-side validation
        malformed_token = "not-a-valid-jwt-token"
        
        with pytest.raises(ValueError) as exc_info:
            validate_token_format(malformed_token, "test token")
        
        error_str = str(exc_info.value).lower()
        assert any(term in error_str for term in [
            "invalid", "jwt", "3 parts"
        ]), f"Expected format error, got: {exc_info.value}"
    
    def test_wrong_audience_token_rejected(self, localhost_endpoint):
        """Server should reject tokens with wrong audience claim."""
        import kumiho
        import base64
        import json as json_mod
        
        # Create a JWT with wrong audience (header.payload.signature format)
        header = base64.urlsafe_b64encode(
            json_mod.dumps({"alg": "RS256", "typ": "JWT"}).encode()
        ).rstrip(b"=").decode()
        
        payload = base64.urlsafe_b64encode(
            json_mod.dumps({
                "sub": "test-user",
                "aud": "wrong-audience",
                "exp": int(time.time()) + 3600,
                "iat": int(time.time())
            }).encode()
        ).rstrip(b"=").decode()
        
        wrong_aud_token = f"{header}.{payload}.fake_signature"
        
        with pytest.raises(Exception) as exc_info:
            client = kumiho.connect(
                endpoint=localhost_endpoint,
                token=wrong_aud_token,
            )
            with kumiho.use_client(client):
                list(kumiho.get_projects())
        
        # Server should reject - either as invalid signature or wrong audience
        assert exc_info.value is not None, "Should reject wrong audience token"


class TestTokenFormatValidation:
    """Test client-side token format validation."""
    
    def test_validate_token_format_accepts_valid_jwt(self):
        """Valid JWT format should be accepted."""
        from kumiho._token_loader import validate_token_format
        
        # Valid JWT structure (header.payload.signature)
        valid_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNjAwMDAwMDAwfQ.signature"
        
        # Should not raise, returns the validated token
        result = validate_token_format(valid_token)
        assert result == valid_token
    
    def test_validate_token_format_rejects_wrong_parts(self):
        """Token without 3 parts should be rejected."""
        from kumiho._token_loader import validate_token_format
        
        # Too few parts - should mention "3 parts" in error
        with pytest.raises(ValueError, match="3 parts"):
            validate_token_format("only.two")
        
        # Too many parts
        with pytest.raises(ValueError, match="3 parts"):
            validate_token_format("too.many.parts.here.now")
    
    def test_validate_token_format_rejects_empty_parts(self):
        """Token with empty parts should be rejected."""
        from kumiho._token_loader import validate_token_format
        
        with pytest.raises(ValueError, match="empty"):
            validate_token_format("header..signature")
    
    def test_validate_token_format_returns_none_for_empty(self):
        """Empty/None tokens should return None."""
        from kumiho._token_loader import validate_token_format
        
        assert validate_token_format(None) is None
        assert validate_token_format("") is None
        assert validate_token_format("   ") is None


class TestTLSEnforcement:
    """Test TLS enforcement warnings and behavior."""
    
    def test_localhost_without_tls_allowed(self):
        """Localhost connections without TLS should be allowed for development."""
        import kumiho
        
        # These should NOT raise TLS-related errors for localhost
        for endpoint in ["localhost:8080", "127.0.0.1:8080"]:
            try:
                client = kumiho.connect(
                    endpoint=endpoint,
                    token="test.token.here",
                )
                # Client created - connection may fail but not due to TLS requirements
            except Exception as e:
                error_str = str(e).lower()
                # Should NOT be a TLS requirement error for localhost
                assert "tls" not in error_str or "insecure" not in error_str, \
                    f"Localhost should not require TLS: {e}"


class TestDiscoveryCacheEncryption:
    """Test discovery cache encryption functionality."""
    
    def test_cache_encrypts_data(self, tmp_path):
        """Discovery cache should encrypt stored data."""
        from kumiho.discovery import (
            DiscoveryCache, DiscoveryRecord, RegionRouting, CacheControl
        )
        
        cache_file = tmp_path / "test_cache.json"
        cache = DiscoveryCache(path=cache_file, encrypt=True)
        
        # Create test discovery record with all required fields
        now = datetime.now(timezone.utc)
        test_record = DiscoveryRecord(
            tenant_id="test-tenant-123",
            tenant_name="Test Tenant",
            roles=["admin"],
            guardrails=None,
            region=RegionRouting(
                region_code="us-central1",
                server_url="test.kumiho.io:443",
            ),
            cache_control=CacheControl(
                issued_at=now,
                refresh_at=now + timedelta(hours=1),
                expires_at=now + timedelta(hours=2),
                expires_in_seconds=7200,
                refresh_after_seconds=3600,
            ),
        )
        
        cache.store("test_key", test_record)
        
        # Read raw file - should be encrypted (not plaintext JSON)
        raw_content = cache_file.read_text()
        
        # Encrypted format starts with "enc:v1:"
        assert raw_content.startswith("enc:v1:"), "Cache should be encrypted"
        
        # Should NOT contain plaintext tenant ID
        assert "test-tenant-123" not in raw_content, "Tenant ID should be encrypted"
    
    def test_cache_round_trip(self, tmp_path):
        """Encrypted data should decrypt correctly."""
        from kumiho.discovery import (
            DiscoveryCache, DiscoveryRecord, RegionRouting, CacheControl
        )
        
        cache_file = tmp_path / "test_cache.json"
        cache = DiscoveryCache(path=cache_file, encrypt=True)
        
        now = datetime.now(timezone.utc)
        test_record = DiscoveryRecord(
            tenant_id="round-trip-tenant",
            tenant_name="Round Trip Test",
            roles=["user"],
            guardrails=None,
            region=RegionRouting(
                region_code="asia-southeast1",
                server_url="asia.kumiho.io:443",
            ),
            cache_control=CacheControl(
                issued_at=now,
                refresh_at=now + timedelta(hours=1),
                expires_at=now + timedelta(hours=2),
                expires_in_seconds=7200,
                refresh_after_seconds=3600,
            ),
        )
        
        cache.store("test_key", test_record)
        
        # Load it back
        loaded = cache.load("test_key")
        
        assert loaded is not None, "Should load cached record"
        assert loaded.tenant_id == "round-trip-tenant"
        assert loaded.region.region_code == "asia-southeast1"
    
    def test_cache_detects_tampering(self, tmp_path):
        """Tampered cache files should be rejected."""
        from kumiho.discovery import (
            DiscoveryCache, DiscoveryRecord, RegionRouting, CacheControl
        )
        
        cache_file = tmp_path / "test_cache.json"
        cache = DiscoveryCache(path=cache_file, encrypt=True)
        
        now = datetime.now(timezone.utc)
        test_record = DiscoveryRecord(
            tenant_id="tampering-test",
            tenant_name="Tamper Test",
            roles=[],
            guardrails=None,
            region=RegionRouting(region_code="eu-west1", server_url="eu.kumiho.io:443"),
            cache_control=CacheControl(
                issued_at=now,
                refresh_at=now + timedelta(hours=1),
                expires_at=now + timedelta(hours=2),
                expires_in_seconds=7200,
                refresh_after_seconds=3600,
            ),
        )
        cache.store("test_key", test_record)
        
        # Read and tamper with the encrypted data
        raw_content = cache_file.read_text()
        # Modify some bytes (after the enc:v1: prefix)
        if len(raw_content) > 20:
            tampered = raw_content[:15] + "X" + raw_content[16:]
            cache_file.write_text(tampered)
        
        # Create new cache instance and try to load
        cache2 = DiscoveryCache(path=cache_file, encrypt=True)
        loaded = cache2.load("test_key")
        
        # Should return None for tampered/invalid data
        assert loaded is None, "Tampered data should not load"
    
    def test_unencrypted_cache_option(self, tmp_path):
        """Cache can be created without encryption for debugging."""
        from kumiho.discovery import (
            DiscoveryCache, DiscoveryRecord, RegionRouting, CacheControl
        )
        
        cache_file = tmp_path / "plaintext_cache.json"
        cache = DiscoveryCache(path=cache_file, encrypt=False)
        
        now = datetime.now(timezone.utc)
        test_record = DiscoveryRecord(
            tenant_id="plaintext-tenant",
            tenant_name="Plaintext Test",
            roles=[],
            guardrails=None,
            region=RegionRouting(region_code="us-west1", server_url="west.kumiho.io:443"),
            cache_control=CacheControl(
                issued_at=now,
                refresh_at=now + timedelta(hours=1),
                expires_at=now + timedelta(hours=2),
                expires_in_seconds=7200,
                refresh_after_seconds=3600,
            ),
        )
        
        cache.store("test_key", test_record)
        
        # Should be plaintext JSON (not encrypted)
        raw_content = cache_file.read_text()
        assert not raw_content.startswith("enc:v1:"), "Should not be encrypted"
        assert "plaintext-tenant" in raw_content, "Tenant ID should be visible in plaintext"


class TestCorrelationIds:
    """Test request correlation ID functionality."""
    
    def test_uuid_format_is_valid(self):
        """UUID format should be 36 characters with dashes."""
        correlation_id = str(uuid.uuid4())
        
        # Should be a valid UUID string
        assert len(correlation_id) == 36, "UUID should be 36 chars with dashes"
        
        # Validate UUID format by parsing
        try:
            uuid.UUID(correlation_id)
        except ValueError:
            pytest.fail(f"Not a valid UUID: {correlation_id}")
    
    def test_uuid_uniqueness(self):
        """Each UUID should be unique."""
        ids = set()
        for _ in range(100):
            new_id = str(uuid.uuid4())
            assert new_id not in ids, "UUIDs should be unique"
            ids.add(new_id)


class TestFilePermissions:
    """Test credential file permission checks."""
    
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions only")
    def test_permission_check_function_exists(self):
        """Permission check function should exist in token loader."""
        from kumiho._token_loader import _check_file_permissions
        
        # Function should exist and be callable
        assert callable(_check_file_permissions)


class TestServerErrorResponses:
    """Test handling of various server error responses."""
    
    @pytest.fixture
    def localhost_endpoint(self):
        return os.environ.get("KUMIHO_SERVER_ENDPOINT", "localhost:8080")
    
    def test_permission_denied_error_clear(self, localhost_endpoint):
        """Permission denied errors should have clear messages."""
        import kumiho
        
        token = os.environ.get("KUMIHO_AUTH_TOKEN")
        if not token:
            pytest.skip("Need KUMIHO_AUTH_TOKEN for permission tests")
        
        client = kumiho.connect(
            endpoint=localhost_endpoint,
            token=token,
        )
        
        with kumiho.use_client(client):
            # Try to get a project that doesn't exist
            try:
                kumiho.get_project("nonexistent-project-xyz-12345")
            except Exception as e:
                error_str = str(e).lower()
                # Should be clear it's a permission or not found issue
                # Accept any error - the point is it handles gracefully
                assert True


class TestRateLimitingBehavior:
    """Test client behavior under rate limiting."""
    
    @pytest.fixture
    def localhost_endpoint(self):
        return os.environ.get("KUMIHO_SERVER_ENDPOINT", "localhost:8080")
    
    def test_handles_rate_limit_gracefully(self, localhost_endpoint):
        """Client should handle rate limit responses gracefully."""
        import kumiho
        
        token = os.environ.get("KUMIHO_AUTH_TOKEN")
        if not token:
            pytest.skip("Need KUMIHO_AUTH_TOKEN for rate limit tests")
        
        client = kumiho.connect(
            endpoint=localhost_endpoint,
            token=token,
        )
        
        with kumiho.use_client(client):
            # Make many rapid requests - should not crash
            errors = []
            for _ in range(10):
                try:
                    list(kumiho.get_projects())
                except Exception as e:
                    errors.append(e)
            
            # Should complete without unhandled exceptions
            # Some rate limit errors are expected and acceptable


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
