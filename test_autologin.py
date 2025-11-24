"""Simple script to test auto-login functionality."""
import kumiho

print("Creating client...")
client = kumiho.Client()

print("Attempting to create a group (this should trigger auto-login if needed)...")
try:
    group = client.create_group("/", "test_autologin")
    print(f"✓ Successfully created group: {group.path}")
    print("Now deleting the group...")
    group.delete(force=True)
    print("✓ Test complete!")
except Exception as e:
    print(f"✗ Error: {e}")
