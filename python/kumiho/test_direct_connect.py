import os
import sys
from pathlib import Path

# Add the parent directory to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from kumiho.client import Client
from kumiho._token_loader import load_bearer_token

# Constants from Dashboard/Deployment
TARGET = "us-central.kumiho.cloud:8080"
TENANT_ID = "22fac7c8-5daf-4ad6-9b7e-70606b1d0c92"

def test_direct_connection():
    print(f"Testing Direct Connection to {TARGET}...")
    
    token = load_bearer_token()
    if not token:
        print(f"Error: No token found. Please run 'python auth_cli.py login' first.")
        return

    print(f"Token found (len={len(token)})")
    print(f"Using Tenant ID: {TENANT_ID}")

    try:
        # Manually configure client, bypassing discovery
        # We need to inject the tenant ID manually since discovery usually does this
        client = Client(
            target=TARGET,
            auth_token=token,
            default_metadata=[("x-tenant-id", TENANT_ID)]
        )
        
        print("Client initialized. Attempting gRPC call (GetChildGroups)...")
        
        # Try a simple read operation
        groups = client.get_child_groups("/")
        
        print(f"✅ Connection Successful!")
        print(f"Found {len(groups)} root groups.")
        for g in groups:
            print(f" - {g.name} ({g.path})")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_connection()
