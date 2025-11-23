import os
import sys
import json
import base64
from pathlib import Path
from datetime import datetime

# Add python/ to path
sys.path.insert(0, str(Path.cwd() / "python"))

from kumiho.auth_cli import _load_credentials

def decode_jwt_without_verification(token):
    """Decode JWT without verifying signature to inspect claims."""
    try:
        # Split the JWT into parts
        parts = token.split('.')
        if len(parts) != 3:
            return None, "Invalid JWT format"
        
        # Decode header
        header_data = parts[0] + '=' * (4 - len(parts[0]) % 4)  # Add padding
        header = json.loads(base64.urlsafe_b64decode(header_data))
        
        # Decode payload
        payload_data = parts[1] + '=' * (4 - len(parts[1]) % 4)  # Add padding
        payload = json.loads(base64.urlsafe_b64decode(payload_data))
        
        return (header, payload), None
    except Exception as e:
        return None, str(e)

def main():
    print("=== Control Plane JWT Debug ===\n")
    
    creds = _load_credentials()
    if not creds:
        print("ERROR: No credentials found")
        return
    
    print(f"Firebase Token: {creds.id_token[:20]}...")
    
    if not creds.control_plane_token:
        print("ERROR: No Control Plane Token found")
        return
    
    print(f"Control Plane Token: {creds.control_plane_token[:20]}...\n")
    
    # Decode Control Plane JWT
    result, error = decode_jwt_without_verification(creds.control_plane_token)
    if error:
        print(f"ERROR decoding CP JWT: {error}")
        return
    
    header, payload = result
    
    print("=== JWT Header ===")
    print(json.dumps(header, indent=2))
    
    print("\n=== JWT Payload ===")
    print(json.dumps(payload, indent=2))
    
    # Check expiration
    if 'exp' in payload:
        exp_time = datetime.fromtimestamp(payload['exp'])
        now = datetime.now()
        print(f"\n=== Expiration Check ===")
        print(f"Expires at: {exp_time}")
        print(f"Current time: {now}")
        if exp_time > now:
            print(f"✅ Token is VALID (expires in {(exp_time - now).total_seconds():.0f} seconds)")
        else:
            print(f"❌ Token is EXPIRED (expired {(now - exp_time).total_seconds():.0f} seconds ago)")
    
    # Check kid
    if 'kid' in header:
        print(f"\n=== Key ID ===")
        print(f"kid: {header['kid']}")
        if header['kid'] == 'kumiho-cp-key-1':
            print("✅ Matches expected kid")
        else:
            print(f"❌ Does NOT match expected kid 'kumiho-cp-key-1'")

if __name__ == "__main__":
    main()
