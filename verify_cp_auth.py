import os
import sys
from pathlib import Path

# Add python/ to path
sys.path.insert(0, str(Path.cwd() / "python"))

from kumiho.auth_cli import ensure_token, _load_credentials, _credentials_path

def verify_cp_token():
    print("--- Verifying Control Plane JWT Acquisition ---")
    
    # 1. Ensure we have a token (this should trigger the exchange if configured)
    # Note: This requires the Control Plane API to be running locally or accessible.
    # If running locally, ensure KUMIHO_CONTROL_PLANE_API_URL is set.
    
    print(f"Credentials path: {_credentials_path()}")
    
    try:
        token, source = ensure_token(interactive=False)
        print(f"Token acquired: {token[:10]}... (Source: {source})")
        
        creds = _load_credentials()
        if creds:
            print(f"Firebase Token: {creds.id_token[:10]}...")
            if creds.control_plane_token:
                print(f"Control Plane Token: {creds.control_plane_token[:10]}...")
                print(f"CP Expires At: {creds.cp_expires_at}")
                print("SUCCESS: Control Plane Token acquired and stored!")
            else:
                print("WARNING: Control Plane Token NOT found in credentials.")
                print("Ensure the Control Plane API is running and accessible.")
        else:
            print("ERROR: No credentials loaded.")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_cp_token()
