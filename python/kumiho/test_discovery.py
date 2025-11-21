import os
import sys
import json
import requests
from pathlib import Path

# Add the parent directory to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from kumiho.discovery import client_from_discovery
from kumiho._token_loader import load_bearer_token

TENANT_ID = "22fac7c8-5daf-4ad6-9b7e-70606b1d0c92"
REGION_CODE = "us-central" # Correct code per dashboard

def set_tenant_region(token, tenant_id, region_code):
    print(f"Attempting to set tenant region for {tenant_id} to '{region_code}'...")
    url = "https://kumiho.io/api/onboarding/tenant-region"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "tenant_id": tenant_id,
        "region_code": region_code
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            print("✅ Successfully set tenant region!")
            print(f"Response: {resp.text}")
            return True
        else:
            print(f"❌ Failed to set region: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Exception setting region: {e}")
        return False

def test_discovery():
    print("Testing Control Plane Discovery...")
    
    token = load_bearer_token()
    if not token:
        print(f"Error: No token found. Please run 'python auth_cli.py login' first.")
        return

    # 1. Try to set the region explicitly
    if set_tenant_region(token, TENANT_ID, REGION_CODE):
        print("Region set. Retrying discovery...")
        try:
            client = client_from_discovery(
                force_refresh=True,
                tenant_hint=TENANT_ID
            )
            print(f"✅ Discovery Successful!")
            print(f"✅ Discovery Successful!")
            # Try a simple API call to verify connectivity
            try:
                print("Attempting API call (get_child_groups)...")
                groups = client.get_child_groups("/")
                print(f"✅ API Call Successful! Found {len(groups)} root groups.")
            except Exception as api_e:
                print(f"❌ API Call Failed: {api_e}")
        except Exception as e:
            print(f"❌ Discovery Failed: {e}")
    else:
        print("Skipping discovery retry due to region set failure.")

if __name__ == "__main__":
    test_discovery()
