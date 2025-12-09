#!/usr/bin/env python3
"""Debug script to verify default_artifact is working correctly."""
import os
import sys
import uuid

# Add the python package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

import kumiho

def unique_name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def main():
    # Connect using environment token
    port = int(os.environ.get('KUMIHO_PORT', '8080'))
    kumiho.connect(endpoint=f'localhost:{port}')
    
    project_name = unique_name("debug_proj")
    print(f"Creating project: {project_name}")
    
    try:
        project = kumiho.create_project(project_name)
        space = project.create_space(name=project_name, parent_path="/")
        item = space.create_item(item_name="asset", kind="model")
        revision = item.create_revision()
        artifact = revision.create_artifact("main", "/path/to/file")
        
        print(f"\n=== Before setDefaultArtifact ===")
        print(f"revision.default_artifact = {repr(revision.default_artifact)}")
        
        print(f"\n=== Calling setDefaultArtifact('main') ===")
        revision.set_default_artifact("main")
        
        print(f"\n=== After setDefaultArtifact (before reload) ===")
        print(f"revision.default_artifact = {repr(revision.default_artifact)}")
        
        print(f"\n=== Reloading revision ===")
        reloaded = item.get_revision(revision.number)
        
        print(f"\n=== After reload ===")
        print(f"reloaded.default_artifact = {repr(reloaded.default_artifact)}")
        print(f"reloaded.kref.uri = {repr(reloaded.kref.uri)}")
        
        # Also fetch using the same kref that Dart uses
        print(f"\n=== Fetching by kref URI (like Dart) ===")
        kref_uri = revision.kref.uri
        print(f"Using kref: {kref_uri}")
        reloaded2 = kumiho.get_revision(kref_uri)
        print(f"reloaded2.default_artifact = {repr(reloaded2.default_artifact)}")
        
        print(f"\n=== RESULT ===")
        if reloaded.default_artifact == "main":
            print("SUCCESS: default_artifact is 'main'")
        else:
            print(f"FAILURE: default_artifact is {repr(reloaded.default_artifact)}")
            
    finally:
        print(f"\n=== Cleanup ===")
        try:
            kumiho.delete_project(project_name)
            print("Project deleted")
        except Exception as e:
            print(f"Failed to delete project: {e}")

if __name__ == '__main__':
    main()
