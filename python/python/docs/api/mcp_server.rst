MCP Server
==========

The MCP (Model Context Protocol) server module enables AI assistants to interact
with Kumiho Cloud.

For usage documentation, see :doc:`/mcp`.

.. automodule:: kumiho.mcp_server
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: TOOLS, TOOL_HANDLERS

Tool Definitions
----------------

The MCP server exposes 39 tools for interacting with Kumiho Cloud:

**Read Operations:**

- ``kumiho_list_projects`` - List all accessible projects
- ``kumiho_get_project`` - Get project by name
- ``kumiho_get_spaces`` - Get spaces in a project
- ``kumiho_get_space`` - Get a space by path
- ``kumiho_get_item`` - Get item by kref
- ``kumiho_search_items`` - Search items with filters
- ``kumiho_get_item_revisions`` - Get all revisions for an item
- ``kumiho_get_revision`` - Get revision by kref
- ``kumiho_get_revision_by_tag`` - Get revision by tag
- ``kumiho_get_artifacts`` - Get artifacts for a revision
- ``kumiho_get_artifact`` - Get artifact by kref
- ``kumiho_get_bundle`` - Get bundle by kref
- ``kumiho_resolve_kref`` - Resolve kref to file location
- ``kumiho_get_artifacts_by_location`` - Reverse lookup by file path

**Graph Operations:**

- ``kumiho_get_dependencies`` - Get what a revision depends on
- ``kumiho_get_dependents`` - Get what depends on a revision
- ``kumiho_analyze_impact`` - Analyze downstream impact
- ``kumiho_find_path`` - Find path between revisions
- ``kumiho_get_edges`` - Get edges for a revision

**Create Operations:**

- ``kumiho_create_project`` - Create a new project
- ``kumiho_create_space`` - Create a space
- ``kumiho_create_item`` - Create an item
- ``kumiho_create_revision`` - Create a revision
- ``kumiho_create_artifact`` - Create an artifact
- ``kumiho_create_bundle`` - Create a bundle
- ``kumiho_create_edge`` - Create a relationship
- ``kumiho_tag_revision`` - Tag a revision

**Delete Operations:**

- ``kumiho_delete_project`` - Delete a project
- ``kumiho_delete_space`` - Delete a space
- ``kumiho_delete_item`` - Delete an item
- ``kumiho_delete_revision`` - Delete a revision
- ``kumiho_delete_artifact`` - Delete an artifact
- ``kumiho_delete_edge`` - Delete a relationship

**Update Operations:**

- ``kumiho_untag_revision`` - Remove a tag
- ``kumiho_set_metadata`` - Set metadata
- ``kumiho_deprecate_item`` - Deprecate an item
- ``kumiho_add_bundle_member`` - Add item to bundle
- ``kumiho_remove_bundle_member`` - Remove item from bundle
- ``kumiho_get_bundle_members`` - List bundle members
