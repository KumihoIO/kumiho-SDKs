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
    deprecated=False
):
    return kumiho_pb2.ProjectResponse(
        project_id=project_id,
        name=name,
        description=description,
        created_at=created_at,
        updated_at=updated_at,
        deprecated=deprecated
    )

def mock_get_projects_response(projects=None):
    return kumiho_pb2.GetProjectsResponse(projects=projects or [])

def mock_status_response(success=True, message="ok"):
    return kumiho_pb2.StatusResponse(success=success, message=message)

def mock_group_response(path, **kwargs):
    return kumiho_pb2.GroupResponse(path=path, **kwargs)

def mock_kref(uri):
    return kumiho_pb2.Kref(uri=uri)

def mock_version_response(
    kref_uri,
    product_kref_uri,
    number=1,
    latest=True,
    tags=None,
    metadata=None,
    author="test_author",
    username="test_user",
    deprecated=False,
    published=False
):
    return kumiho_pb2.VersionResponse(
        kref=kumiho_pb2.Kref(uri=kref_uri),
        product_kref=kumiho_pb2.Kref(uri=product_kref_uri),
        number=number,
        latest=latest,
        tags=tags or [],
        metadata=metadata or {},
        author=author,
        username=username,
        deprecated=deprecated,
        published=published
    )

def mock_product_response(
    kref_uri,
    name,
    product_name,
    product_type,
    author="test_author",
    username="test_user",
    deprecated=False,
    metadata=None
):
    return kumiho_pb2.ProductResponse(
        kref=kumiho_pb2.Kref(uri=kref_uri),
        name=name,
        product_name=product_name,
        product_type=product_type,
        author=author,
        username=username,
        deprecated=deprecated,
        metadata=metadata or {}
    )

def mock_get_products_response(products=None):
    return kumiho_pb2.GetProductsResponse(products=products or [])

def mock_create_group_request(parent_path, group_name):
    return kumiho_pb2.CreateGroupRequest(parent_path=parent_path, group_name=group_name)

def mock_get_group_request(path_or_kref):
    return kumiho_pb2.GetGroupRequest(path_or_kref=path_or_kref)

def mock_kref_request(uri):
    return kumiho_pb2.KrefRequest(kref=kumiho_pb2.Kref(uri=uri))

def mock_get_product_request(parent_path, product_name, product_type):
    return kumiho_pb2.GetProductRequest(
        parent_path=parent_path,
        product_name=product_name,
        product_type=product_type
    )

def mock_product_search_request(context_filter, product_name_filter="", product_type_filter=""):
    return kumiho_pb2.ProductSearchRequest(
        context_filter=context_filter,
        product_name_filter=product_name_filter,
        product_type_filter=product_type_filter
    )
