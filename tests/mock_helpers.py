"""
Helper module for mocking Kumiho gRPC responses in tests.
This abstracts away the direct usage of kumiho_pb2 in test files.
"""

from kumiho.proto import kumiho_pb2

def mock_project_response(
    project_id="p1",
    name="demo",
    description="",
    created_at="now",
    updated_at="now",
    deprecated=False,
    allow_public=False,
):
    return kumiho_pb2.ProjectResponse(
        project_id=project_id,
        name=name,
        description=description,
        created_at=created_at,
        updated_at=updated_at,
        deprecated=deprecated,
        allow_public=allow_public,
    )

def mock_get_projects_response(projects=None):
    return kumiho_pb2.GetProjectsResponse(projects=projects or [])

def mock_status_response(success=True, message="ok"):
    return kumiho_pb2.StatusResponse(success=success, message=message)

def mock_space_response(path, **kwargs):
    return kumiho_pb2.SpaceResponse(path=path, **kwargs)

# Backwards compatibility alias
mock_group_response = mock_space_response

def mock_kref(uri):
    return kumiho_pb2.Kref(uri=uri)

def mock_revision_response(
    kref_uri,
    item_kref_uri,
    number=1,
    latest=True,
    tags=None,
    metadata=None,
    author="test_author",
    username="test_user",
    deprecated=False,
    published=False,
    default_artifact=None,
):
    resp = kumiho_pb2.RevisionResponse(
        kref=kumiho_pb2.Kref(uri=kref_uri),
        item_kref=kumiho_pb2.Kref(uri=item_kref_uri),
        number=number,
        latest=latest,
        tags=tags or [],
        metadata=metadata or {},
        author=author,
        username=username,
        deprecated=deprecated,
        published=published
    )

    # Optional field (protobuf3); only set when provided.
    if default_artifact is not None:
        resp.default_artifact = default_artifact
    return resp

# Backwards compatibility alias
mock_version_response = mock_revision_response


def mock_artifact_response(
    kref_uri,
    revision_kref_uri,
    item_kref_uri,
    name="main",
    location="/path/to/file",
    author="test_author",
    username="test_user",
    deprecated=False,
    metadata=None,
    created_at="now",
    modified_at="now",
):
    return kumiho_pb2.ArtifactResponse(
        kref=kumiho_pb2.Kref(uri=kref_uri),
        revision_kref=kumiho_pb2.Kref(uri=revision_kref_uri),
        item_kref=kumiho_pb2.Kref(uri=item_kref_uri),
        name=name,
        location=location,
        author=author,
        username=username,
        deprecated=deprecated,
        metadata=metadata or {},
        created_at=created_at,
        modified_at=modified_at,
    )

def mock_item_response(
    kref_uri,
    name,
    item_name,
    kind,
    author="test_author",
    username="test_user",
    deprecated=False,
    metadata=None
):
    return kumiho_pb2.ItemResponse(
        kref=kumiho_pb2.Kref(uri=kref_uri),
        name=name,
        item_name=item_name,
        kind=kind,
        author=author,
        username=username,
        deprecated=deprecated,
        metadata=metadata or {}
    )

# Backwards compatibility alias
mock_product_response = mock_item_response

def mock_get_items_response(items=None, next_cursor="", total_count=0):
    pagination = kumiho_pb2.PaginationResponse(
        next_cursor=next_cursor,
        total_count=total_count,
        has_more=bool(next_cursor)
    )
    return kumiho_pb2.GetItemsResponse(items=items or [], pagination=pagination)

# Backwards compatibility alias
mock_get_products_response = mock_get_items_response

def mock_create_space_request(parent_path, space_name):
    return kumiho_pb2.CreateSpaceRequest(parent_path=parent_path, space_name=space_name)

# Backwards compatibility alias
mock_create_group_request = mock_create_space_request

def mock_get_space_request(path_or_kref):
    return kumiho_pb2.GetSpaceRequest(path_or_kref=path_or_kref)

# Backwards compatibility alias
mock_get_group_request = mock_get_space_request

def mock_kref_request(uri):
    return kumiho_pb2.KrefRequest(kref=kumiho_pb2.Kref(uri=uri))

def mock_get_item_request(parent_path, item_name, kind):
    return kumiho_pb2.GetItemRequest(
        parent_path=parent_path,
        item_name=item_name,
        kind=kind
    )

# Backwards compatibility alias
mock_get_product_request = mock_get_item_request

def mock_item_search_request(context_filter, item_name_filter="", kind_filter=""):
    return kumiho_pb2.ItemSearchRequest(
        context_filter=context_filter,
        item_name_filter=item_name_filter,
        kind_filter=kind_filter
    )

# Backwards compatibility alias
mock_product_search_request = mock_item_search_request
