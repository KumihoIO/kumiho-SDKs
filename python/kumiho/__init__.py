"""
Kumiho Python Client Library
"""

__version__ = "0.3.0"

import grpc
from typing import Dict, List, Optional, Iterator

# Import the main classes to make them available at the package level.
from .base import KumihoObject
from .client import Client
from .event import Event
from .group import Group
from .kref import Kref
from .link import Link
from .product import Product
from .resource import Resource
from .version import Version
from .discovery import client_from_discovery
from ._bootstrap import bootstrap_default_client

# Add constants for reserved tags, permissions, and common link types
LATEST_TAG = "latest"
PUBLISHED_TAG = "published"
OUTPUT_LINK = "Output"
INPUT_LINK = "Input"
REFERENCE_LINK = "Reference"


# Instantiate a default client instance for convenience.
_default_client: Optional[Client] = None

def get_client() -> Client:
    """Gets the global client instance, creating it if it doesn't exist."""
    global _default_client
    if _default_client is None:
        _default_client = bootstrap_default_client()
    return _default_client


def configure_default_client(client: Client) -> Client:
    """Override the lazily created default client used by top-level helpers."""

    global _default_client
    _default_client = client
    return _default_client

# Expose methods from the default client as top-level package functions.
def create_group(path: str) -> 'Group':
    """
    Create a group at the specified path. Supports nested paths (e.g., "projectA/seqA/shot100").
    Uses 'create or get' logic by default.
    """
    parts = path.split('/')
    if len(parts) == 1:
        # Top-level group
        return get_client().create_group(parent_path="/", group_name=parts[0])
    else:
        # Nested groups: create intermediates if needed
        current_path = "/"
        created_groups = []
        for part in parts:
            current_path = f"{current_path.rstrip('/')}/{part}"
            try:
                group = get_client().create_group(parent_path="/".join(current_path.split('/')[:-1]) or "/", group_name=part)
                created_groups.append(group)
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                    group = get_client().get_group(current_path)
                else:
                    raise
        return group

def get_group(path: str) -> 'Group':
    return get_client().get_group(path)

def get_child_groups(parent_path: str = "") -> List['Group']:
    """
    Get child groups of a parent group.

    Args:
        parent_path: The path of the parent group. If empty or "/",
                     returns root-level groups.

    Returns:
        A list of Group objects that are direct children of the parent.
    """
    return get_client().get_child_groups(parent_path)

def delete_group(path: str, force: bool = False):
    return get_client().delete_group(path, force)

def create_product(parent_path: str, name: str, ptype: str) -> 'Product':
    return get_client().create_product(parent_path, name, ptype)

def get_product(kref: str) -> 'Product':
    return get_client().get_product_by_kref(kref)

def get_product_by_context(parent_path: str, name: str, ptype: str) -> 'Product':
    return get_client().get_product(parent_path, name, ptype)

def get_version(kref: str) -> 'Version':
    return get_client().get_version(kref)

def product_search(context_filter: str = "", name_filter: str = "", ptype_filter: str = "") -> List['Product']:
    return get_client().product_search(context_filter, name_filter, ptype_filter)

def create_version(product_kref: 'Kref', metadata: Optional[Dict[str, str]] = None, version_number: int = 0) -> 'Version':
    return get_client().create_version(product_kref, metadata, version_number)

def get_resources_by_location(location: str) -> List['Resource']:
    return get_client().get_resources_by_location(location)

def create_link(source_version: 'Version', target_version: 'Version', link_type: str, metadata: Optional[Dict[str, str]] = None) -> 'Link':
    """Creates a directed, typed link from a source version to a target version."""
    return get_client().create_link(source_version, target_version, link_type, metadata)

def get_links(version: 'Version', link_type_filter: str = "") -> List['Link']:
    """Retrieves all links associated with a given version."""
    return get_client().get_links(version.kref, link_type_filter)

def event_stream(routing_key_filter: str = "", kref_filter: str = "") -> Iterator[Event]:
    """
    Subscribes to the event stream from the Kumiho server.

    Args:
        routing_key_filter (str): A filter for the events to receive.
                                  Supports wildcards, e.g., "product.model.*"
        kref_filter (str): A filter for the kref URIs to receive events for.
                          Supports wildcards, e.g., "kref://projectA/**/*.model"

    Yields:
        Event: An event object representing a change in the database.
    """
    return get_client().event_stream(routing_key_filter, kref_filter)


def resolve(kref: str) -> Optional[str]:
    """
    Resolve a KREF URI to a file location.

    Supports extended KREF parameters:
    - Product KREF: resolves to latest version → default resource → location
    - Version KREF: resolves to default resource → location  
    - Resource KREF: returns the resource location directly
    - &r=resource_name parameter: specifies which resource to use instead of default

    Args:
        kref: The KREF URI to resolve.

    Returns:
        The file location string, or None if resolution fails.
    """
    return get_client().resolve(kref)

__all__ = [
    "KumihoObject",
    "Client",
    "client_from_discovery",
    "Group",
    "Product",
    "Version",
    "Resource",
    "Link",
    "Kref",
    "Event",
    # Constants
    "LATEST_TAG",
    "PUBLISHED_TAG",
    "OUTPUT_LINK",
    "INPUT_LINK",
    "REFERENCE_LINK",
    # Functions
    "create_group",
    "get_group",
    "delete_group",
    "create_product",
    "get_product",
    "get_product_by_context",
    "get_version",
    "product_search",
    "create_version",
    "get_resources_by_location",
    "create_link",
    "get_links",
    "event_stream",
    "resolve",
]
