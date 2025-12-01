from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LinkDirection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTGOING: _ClassVar[LinkDirection]
    INCOMING: _ClassVar[LinkDirection]
    BOTH: _ClassVar[LinkDirection]
OUTGOING: LinkDirection
INCOMING: LinkDirection
BOTH: LinkDirection

class Kref(_message.Message):
    __slots__ = ("uri",)
    URI_FIELD_NUMBER: _ClassVar[int]
    uri: str
    def __init__(self, uri: _Optional[str] = ...) -> None: ...

class Link(_message.Message):
    __slots__ = ("source_kref", "target_kref", "link_type", "metadata", "created_at", "author", "username")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SOURCE_KREF_FIELD_NUMBER: _ClassVar[int]
    TARGET_KREF_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    source_kref: Kref
    target_kref: Kref
    link_type: str
    metadata: _containers.ScalarMap[str, str]
    created_at: str
    author: str
    username: str
    def __init__(self, source_kref: _Optional[_Union[Kref, _Mapping]] = ..., target_kref: _Optional[_Union[Kref, _Mapping]] = ..., link_type: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[str] = ..., author: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...

class StatusResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class KrefRequest(_message.Message):
    __slots__ = ("kref",)
    KREF_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ...) -> None: ...

class ResolveKrefRequest(_message.Message):
    __slots__ = ("kref", "tag", "time")
    KREF_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    kref: str
    tag: str
    time: str
    def __init__(self, kref: _Optional[str] = ..., tag: _Optional[str] = ..., time: _Optional[str] = ...) -> None: ...

class ResolveLocationRequest(_message.Message):
    __slots__ = ("kref", "tag", "time")
    KREF_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    kref: str
    tag: str
    time: str
    def __init__(self, kref: _Optional[str] = ..., tag: _Optional[str] = ..., time: _Optional[str] = ...) -> None: ...

class ResolveLocationResponse(_message.Message):
    __slots__ = ("location", "resolved_kref", "resource_name")
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_KREF_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    location: str
    resolved_kref: Kref
    resource_name: str
    def __init__(self, location: _Optional[str] = ..., resolved_kref: _Optional[_Union[Kref, _Mapping]] = ..., resource_name: _Optional[str] = ...) -> None: ...

class CreateGroupRequest(_message.Message):
    __slots__ = ("parent_path", "group_name", "exists_error")
    PARENT_PATH_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    EXISTS_ERROR_FIELD_NUMBER: _ClassVar[int]
    parent_path: str
    group_name: str
    exists_error: bool
    def __init__(self, parent_path: _Optional[str] = ..., group_name: _Optional[str] = ..., exists_error: bool = ...) -> None: ...

class GroupResponse(_message.Message):
    __slots__ = ("path", "created_at", "modified_at", "author", "metadata", "username", "name", "type")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PATH_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    path: str
    created_at: str
    modified_at: str
    author: str
    metadata: _containers.ScalarMap[str, str]
    username: str
    name: str
    type: str
    def __init__(self, path: _Optional[str] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ..., author: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class GetGroupRequest(_message.Message):
    __slots__ = ("path_or_kref",)
    PATH_OR_KREF_FIELD_NUMBER: _ClassVar[int]
    path_or_kref: str
    def __init__(self, path_or_kref: _Optional[str] = ...) -> None: ...

class DeleteGroupRequest(_message.Message):
    __slots__ = ("path", "force")
    PATH_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    path: str
    force: bool
    def __init__(self, path: _Optional[str] = ..., force: bool = ...) -> None: ...

class GetChildGroupsRequest(_message.Message):
    __slots__ = ("parent_path", "recursive")
    PARENT_PATH_FIELD_NUMBER: _ClassVar[int]
    RECURSIVE_FIELD_NUMBER: _ClassVar[int]
    parent_path: str
    recursive: bool
    def __init__(self, parent_path: _Optional[str] = ..., recursive: bool = ...) -> None: ...

class GetChildGroupsResponse(_message.Message):
    __slots__ = ("groups",)
    GROUPS_FIELD_NUMBER: _ClassVar[int]
    groups: _containers.RepeatedCompositeFieldContainer[GroupResponse]
    def __init__(self, groups: _Optional[_Iterable[_Union[GroupResponse, _Mapping]]] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ("parent_path", "product_name", "product_type", "exists_error")
    PARENT_PATH_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXISTS_ERROR_FIELD_NUMBER: _ClassVar[int]
    parent_path: str
    product_name: str
    product_type: str
    exists_error: bool
    def __init__(self, parent_path: _Optional[str] = ..., product_name: _Optional[str] = ..., product_type: _Optional[str] = ..., exists_error: bool = ...) -> None: ...

class GetProductRequest(_message.Message):
    __slots__ = ("parent_path", "product_name", "product_type")
    PARENT_PATH_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_FIELD_NUMBER: _ClassVar[int]
    parent_path: str
    product_name: str
    product_type: str
    def __init__(self, parent_path: _Optional[str] = ..., product_name: _Optional[str] = ..., product_type: _Optional[str] = ...) -> None: ...

class ProductResponse(_message.Message):
    __slots__ = ("kref", "name", "product_name", "product_type", "created_at", "modified_at", "author", "metadata", "deprecated", "username")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    KREF_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    name: str
    product_name: str
    product_type: str
    created_at: str
    modified_at: str
    author: str
    metadata: _containers.ScalarMap[str, str]
    deprecated: bool
    username: str
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., name: _Optional[str] = ..., product_name: _Optional[str] = ..., product_type: _Optional[str] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ..., author: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., deprecated: bool = ..., username: _Optional[str] = ...) -> None: ...

class DeleteProductRequest(_message.Message):
    __slots__ = ("kref", "force")
    KREF_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    force: bool
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., force: bool = ...) -> None: ...

class GetProductsRequest(_message.Message):
    __slots__ = ("parent_path", "product_name_filter", "product_type_filter")
    PARENT_PATH_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FILTER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    parent_path: str
    product_name_filter: str
    product_type_filter: str
    def __init__(self, parent_path: _Optional[str] = ..., product_name_filter: _Optional[str] = ..., product_type_filter: _Optional[str] = ...) -> None: ...

class GetProductsResponse(_message.Message):
    __slots__ = ("products",)
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[ProductResponse]
    def __init__(self, products: _Optional[_Iterable[_Union[ProductResponse, _Mapping]]] = ...) -> None: ...

class ProductSearchRequest(_message.Message):
    __slots__ = ("context_filter", "product_name_filter", "product_type_filter")
    CONTEXT_FILTER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FILTER_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    context_filter: str
    product_name_filter: str
    product_type_filter: str
    def __init__(self, context_filter: _Optional[str] = ..., product_name_filter: _Optional[str] = ..., product_type_filter: _Optional[str] = ...) -> None: ...

class CreateVersionRequest(_message.Message):
    __slots__ = ("product_kref", "metadata", "number", "exists_error")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    EXISTS_ERROR_FIELD_NUMBER: _ClassVar[int]
    product_kref: Kref
    metadata: _containers.ScalarMap[str, str]
    number: int
    exists_error: bool
    def __init__(self, product_kref: _Optional[_Union[Kref, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ..., number: _Optional[int] = ..., exists_error: bool = ...) -> None: ...

class VersionResponse(_message.Message):
    __slots__ = ("kref", "product_kref", "number", "tags", "metadata", "created_at", "modified_at", "author", "deprecated", "published", "latest", "username", "default_resource", "name")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    KREF_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    PUBLISHED_FIELD_NUMBER: _ClassVar[int]
    LATEST_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_RESOURCE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    product_kref: Kref
    number: int
    tags: _containers.RepeatedScalarFieldContainer[str]
    metadata: _containers.ScalarMap[str, str]
    created_at: str
    modified_at: str
    author: str
    deprecated: bool
    published: bool
    latest: bool
    username: str
    default_resource: str
    name: str
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., product_kref: _Optional[_Union[Kref, _Mapping]] = ..., number: _Optional[int] = ..., tags: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ..., author: _Optional[str] = ..., deprecated: bool = ..., published: bool = ..., latest: bool = ..., username: _Optional[str] = ..., default_resource: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class DeleteVersionRequest(_message.Message):
    __slots__ = ("kref", "force")
    KREF_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    force: bool
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., force: bool = ...) -> None: ...

class GetVersionsRequest(_message.Message):
    __slots__ = ("product_kref",)
    PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    product_kref: Kref
    def __init__(self, product_kref: _Optional[_Union[Kref, _Mapping]] = ...) -> None: ...

class GetVersionsResponse(_message.Message):
    __slots__ = ("versions",)
    VERSIONS_FIELD_NUMBER: _ClassVar[int]
    versions: _containers.RepeatedCompositeFieldContainer[VersionResponse]
    def __init__(self, versions: _Optional[_Iterable[_Union[VersionResponse, _Mapping]]] = ...) -> None: ...

class CreateResourceRequest(_message.Message):
    __slots__ = ("version_kref", "name", "location", "exists_error")
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    EXISTS_ERROR_FIELD_NUMBER: _ClassVar[int]
    version_kref: Kref
    name: str
    location: str
    exists_error: bool
    def __init__(self, version_kref: _Optional[_Union[Kref, _Mapping]] = ..., name: _Optional[str] = ..., location: _Optional[str] = ..., exists_error: bool = ...) -> None: ...

class ResourceResponse(_message.Message):
    __slots__ = ("kref", "location", "version_kref", "product_kref", "created_at", "modified_at", "author", "metadata", "deprecated", "username", "name")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    KREF_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    location: str
    version_kref: Kref
    product_kref: Kref
    created_at: str
    modified_at: str
    author: str
    metadata: _containers.ScalarMap[str, str]
    deprecated: bool
    username: str
    name: str
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., location: _Optional[str] = ..., version_kref: _Optional[_Union[Kref, _Mapping]] = ..., product_kref: _Optional[_Union[Kref, _Mapping]] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ..., author: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., deprecated: bool = ..., username: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class GetResourceRequest(_message.Message):
    __slots__ = ("version_kref", "name")
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    version_kref: Kref
    name: str
    def __init__(self, version_kref: _Optional[_Union[Kref, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...

class GetResourcesRequest(_message.Message):
    __slots__ = ("version_kref",)
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    version_kref: Kref
    def __init__(self, version_kref: _Optional[_Union[Kref, _Mapping]] = ...) -> None: ...

class GetResourcesResponse(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[ResourceResponse]
    def __init__(self, resources: _Optional[_Iterable[_Union[ResourceResponse, _Mapping]]] = ...) -> None: ...

class DeleteResourceRequest(_message.Message):
    __slots__ = ("kref", "force")
    KREF_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    force: bool
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., force: bool = ...) -> None: ...

class GetResourcesByLocationRequest(_message.Message):
    __slots__ = ("location",)
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    location: str
    def __init__(self, location: _Optional[str] = ...) -> None: ...

class GetResourcesByLocationResponse(_message.Message):
    __slots__ = ("resources",)
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    resources: _containers.RepeatedCompositeFieldContainer[ResourceResponse]
    def __init__(self, resources: _Optional[_Iterable[_Union[ResourceResponse, _Mapping]]] = ...) -> None: ...

class TagVersionRequest(_message.Message):
    __slots__ = ("kref", "tag")
    KREF_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    tag: str
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., tag: _Optional[str] = ...) -> None: ...

class UnTagVersionRequest(_message.Message):
    __slots__ = ("kref", "tag")
    KREF_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    tag: str
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., tag: _Optional[str] = ...) -> None: ...

class HasTagRequest(_message.Message):
    __slots__ = ("kref", "tag")
    KREF_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    tag: str
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., tag: _Optional[str] = ...) -> None: ...

class HasTagResponse(_message.Message):
    __slots__ = ("has_tag",)
    HAS_TAG_FIELD_NUMBER: _ClassVar[int]
    has_tag: bool
    def __init__(self, has_tag: bool = ...) -> None: ...

class WasTaggedRequest(_message.Message):
    __slots__ = ("kref", "tag")
    KREF_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    tag: str
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., tag: _Optional[str] = ...) -> None: ...

class WasTaggedResponse(_message.Message):
    __slots__ = ("was_tagged",)
    WAS_TAGGED_FIELD_NUMBER: _ClassVar[int]
    was_tagged: bool
    def __init__(self, was_tagged: bool = ...) -> None: ...

class SetDefaultResourceRequest(_message.Message):
    __slots__ = ("version_kref", "resource_name")
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_NAME_FIELD_NUMBER: _ClassVar[int]
    version_kref: Kref
    resource_name: str
    def __init__(self, version_kref: _Optional[_Union[Kref, _Mapping]] = ..., resource_name: _Optional[str] = ...) -> None: ...

class CreateLinkRequest(_message.Message):
    __slots__ = ("source_version_kref", "target_version_kref", "link_type", "metadata", "exists_error")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SOURCE_VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    TARGET_VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    EXISTS_ERROR_FIELD_NUMBER: _ClassVar[int]
    source_version_kref: Kref
    target_version_kref: Kref
    link_type: str
    metadata: _containers.ScalarMap[str, str]
    exists_error: bool
    def __init__(self, source_version_kref: _Optional[_Union[Kref, _Mapping]] = ..., target_version_kref: _Optional[_Union[Kref, _Mapping]] = ..., link_type: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ..., exists_error: bool = ...) -> None: ...

class UpdateMetadataRequest(_message.Message):
    __slots__ = ("kref", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    KREF_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PeekNextVersionRequest(_message.Message):
    __slots__ = ("product_kref",)
    PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    product_kref: Kref
    def __init__(self, product_kref: _Optional[_Union[Kref, _Mapping]] = ...) -> None: ...

class PeekNextVersionResponse(_message.Message):
    __slots__ = ("number",)
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    number: int
    def __init__(self, number: _Optional[int] = ...) -> None: ...

class GetLinksRequest(_message.Message):
    __slots__ = ("kref", "link_type_filter", "direction")
    KREF_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    link_type_filter: str
    direction: LinkDirection
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., link_type_filter: _Optional[str] = ..., direction: _Optional[_Union[LinkDirection, str]] = ...) -> None: ...

class GetLinksResponse(_message.Message):
    __slots__ = ("links", "version_krefs")
    LINKS_FIELD_NUMBER: _ClassVar[int]
    VERSION_KREFS_FIELD_NUMBER: _ClassVar[int]
    links: _containers.RepeatedCompositeFieldContainer[Link]
    version_krefs: _containers.RepeatedCompositeFieldContainer[Kref]
    def __init__(self, links: _Optional[_Iterable[_Union[Link, _Mapping]]] = ..., version_krefs: _Optional[_Iterable[_Union[Kref, _Mapping]]] = ...) -> None: ...

class DeleteLinkRequest(_message.Message):
    __slots__ = ("source_kref", "target_kref", "link_type")
    SOURCE_KREF_FIELD_NUMBER: _ClassVar[int]
    TARGET_KREF_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FIELD_NUMBER: _ClassVar[int]
    source_kref: Kref
    target_kref: Kref
    link_type: str
    def __init__(self, source_kref: _Optional[_Union[Kref, _Mapping]] = ..., target_kref: _Optional[_Union[Kref, _Mapping]] = ..., link_type: _Optional[str] = ...) -> None: ...

class PathStep(_message.Message):
    __slots__ = ("version_kref", "link_type", "depth")
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    version_kref: Kref
    link_type: str
    depth: int
    def __init__(self, version_kref: _Optional[_Union[Kref, _Mapping]] = ..., link_type: _Optional[str] = ..., depth: _Optional[int] = ...) -> None: ...

class VersionPath(_message.Message):
    __slots__ = ("steps", "total_depth")
    STEPS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_DEPTH_FIELD_NUMBER: _ClassVar[int]
    steps: _containers.RepeatedCompositeFieldContainer[PathStep]
    total_depth: int
    def __init__(self, steps: _Optional[_Iterable[_Union[PathStep, _Mapping]]] = ..., total_depth: _Optional[int] = ...) -> None: ...

class TraverseLinksRequest(_message.Message):
    __slots__ = ("origin_kref", "direction", "link_type_filter", "max_depth", "limit", "include_path")
    ORIGIN_KREF_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PATH_FIELD_NUMBER: _ClassVar[int]
    origin_kref: Kref
    direction: LinkDirection
    link_type_filter: _containers.RepeatedScalarFieldContainer[str]
    max_depth: int
    limit: int
    include_path: bool
    def __init__(self, origin_kref: _Optional[_Union[Kref, _Mapping]] = ..., direction: _Optional[_Union[LinkDirection, str]] = ..., link_type_filter: _Optional[_Iterable[str]] = ..., max_depth: _Optional[int] = ..., limit: _Optional[int] = ..., include_path: bool = ...) -> None: ...

class TraverseLinksResponse(_message.Message):
    __slots__ = ("paths", "version_krefs", "links", "total_count", "truncated")
    PATHS_FIELD_NUMBER: _ClassVar[int]
    VERSION_KREFS_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    paths: _containers.RepeatedCompositeFieldContainer[VersionPath]
    version_krefs: _containers.RepeatedCompositeFieldContainer[Kref]
    links: _containers.RepeatedCompositeFieldContainer[Link]
    total_count: int
    truncated: bool
    def __init__(self, paths: _Optional[_Iterable[_Union[VersionPath, _Mapping]]] = ..., version_krefs: _Optional[_Iterable[_Union[Kref, _Mapping]]] = ..., links: _Optional[_Iterable[_Union[Link, _Mapping]]] = ..., total_count: _Optional[int] = ..., truncated: bool = ...) -> None: ...

class ShortestPathRequest(_message.Message):
    __slots__ = ("source_kref", "target_kref", "link_type_filter", "max_depth", "all_shortest")
    SOURCE_KREF_FIELD_NUMBER: _ClassVar[int]
    TARGET_KREF_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    ALL_SHORTEST_FIELD_NUMBER: _ClassVar[int]
    source_kref: Kref
    target_kref: Kref
    link_type_filter: _containers.RepeatedScalarFieldContainer[str]
    max_depth: int
    all_shortest: bool
    def __init__(self, source_kref: _Optional[_Union[Kref, _Mapping]] = ..., target_kref: _Optional[_Union[Kref, _Mapping]] = ..., link_type_filter: _Optional[_Iterable[str]] = ..., max_depth: _Optional[int] = ..., all_shortest: bool = ...) -> None: ...

class ShortestPathResponse(_message.Message):
    __slots__ = ("paths", "path_exists", "path_length")
    PATHS_FIELD_NUMBER: _ClassVar[int]
    PATH_EXISTS_FIELD_NUMBER: _ClassVar[int]
    PATH_LENGTH_FIELD_NUMBER: _ClassVar[int]
    paths: _containers.RepeatedCompositeFieldContainer[VersionPath]
    path_exists: bool
    path_length: int
    def __init__(self, paths: _Optional[_Iterable[_Union[VersionPath, _Mapping]]] = ..., path_exists: bool = ..., path_length: _Optional[int] = ...) -> None: ...

class ImpactAnalysisRequest(_message.Message):
    __slots__ = ("version_kref", "link_type_filter", "max_depth", "limit")
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    LINK_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    MAX_DEPTH_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    version_kref: Kref
    link_type_filter: _containers.RepeatedScalarFieldContainer[str]
    max_depth: int
    limit: int
    def __init__(self, version_kref: _Optional[_Union[Kref, _Mapping]] = ..., link_type_filter: _Optional[_Iterable[str]] = ..., max_depth: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class ImpactedVersion(_message.Message):
    __slots__ = ("version_kref", "product_kref", "impact_depth", "impact_path_types")
    VERSION_KREF_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    IMPACT_DEPTH_FIELD_NUMBER: _ClassVar[int]
    IMPACT_PATH_TYPES_FIELD_NUMBER: _ClassVar[int]
    version_kref: Kref
    product_kref: Kref
    impact_depth: int
    impact_path_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, version_kref: _Optional[_Union[Kref, _Mapping]] = ..., product_kref: _Optional[_Union[Kref, _Mapping]] = ..., impact_depth: _Optional[int] = ..., impact_path_types: _Optional[_Iterable[str]] = ...) -> None: ...

class ImpactAnalysisResponse(_message.Message):
    __slots__ = ("impacted_versions", "total_impacted", "truncated")
    IMPACTED_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_IMPACTED_FIELD_NUMBER: _ClassVar[int]
    TRUNCATED_FIELD_NUMBER: _ClassVar[int]
    impacted_versions: _containers.RepeatedCompositeFieldContainer[ImpactedVersion]
    total_impacted: int
    truncated: bool
    def __init__(self, impacted_versions: _Optional[_Iterable[_Union[ImpactedVersion, _Mapping]]] = ..., total_impacted: _Optional[int] = ..., truncated: bool = ...) -> None: ...

class CreateCollectionRequest(_message.Message):
    __slots__ = ("parent_path", "collection_name", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PARENT_PATH_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    parent_path: str
    collection_name: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, parent_path: _Optional[str] = ..., collection_name: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CollectionMember(_message.Message):
    __slots__ = ("product_kref", "added_at", "added_by", "added_by_username", "added_in_version")
    PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    ADDED_AT_FIELD_NUMBER: _ClassVar[int]
    ADDED_BY_FIELD_NUMBER: _ClassVar[int]
    ADDED_BY_USERNAME_FIELD_NUMBER: _ClassVar[int]
    ADDED_IN_VERSION_FIELD_NUMBER: _ClassVar[int]
    product_kref: Kref
    added_at: str
    added_by: str
    added_by_username: str
    added_in_version: int
    def __init__(self, product_kref: _Optional[_Union[Kref, _Mapping]] = ..., added_at: _Optional[str] = ..., added_by: _Optional[str] = ..., added_by_username: _Optional[str] = ..., added_in_version: _Optional[int] = ...) -> None: ...

class AddCollectionMemberRequest(_message.Message):
    __slots__ = ("collection_kref", "member_product_kref", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COLLECTION_KREF_FIELD_NUMBER: _ClassVar[int]
    MEMBER_PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    collection_kref: Kref
    member_product_kref: Kref
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, collection_kref: _Optional[_Union[Kref, _Mapping]] = ..., member_product_kref: _Optional[_Union[Kref, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class AddCollectionMemberResponse(_message.Message):
    __slots__ = ("success", "message", "new_version")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NEW_VERSION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    new_version: VersionResponse
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., new_version: _Optional[_Union[VersionResponse, _Mapping]] = ...) -> None: ...

class RemoveCollectionMemberRequest(_message.Message):
    __slots__ = ("collection_kref", "member_product_kref", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COLLECTION_KREF_FIELD_NUMBER: _ClassVar[int]
    MEMBER_PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    collection_kref: Kref
    member_product_kref: Kref
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, collection_kref: _Optional[_Union[Kref, _Mapping]] = ..., member_product_kref: _Optional[_Union[Kref, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RemoveCollectionMemberResponse(_message.Message):
    __slots__ = ("success", "message", "new_version")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NEW_VERSION_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    new_version: VersionResponse
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., new_version: _Optional[_Union[VersionResponse, _Mapping]] = ...) -> None: ...

class GetCollectionMembersRequest(_message.Message):
    __slots__ = ("collection_kref", "version_number")
    COLLECTION_KREF_FIELD_NUMBER: _ClassVar[int]
    VERSION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    collection_kref: Kref
    version_number: int
    def __init__(self, collection_kref: _Optional[_Union[Kref, _Mapping]] = ..., version_number: _Optional[int] = ...) -> None: ...

class GetCollectionMembersResponse(_message.Message):
    __slots__ = ("members", "version_number", "total_count")
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    VERSION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[CollectionMember]
    version_number: int
    total_count: int
    def __init__(self, members: _Optional[_Iterable[_Union[CollectionMember, _Mapping]]] = ..., version_number: _Optional[int] = ..., total_count: _Optional[int] = ...) -> None: ...

class CollectionVersionHistory(_message.Message):
    __slots__ = ("version_number", "action", "member_product_kref", "author", "username", "created_at", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    VERSION_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    MEMBER_PRODUCT_KREF_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    version_number: int
    action: str
    member_product_kref: Kref
    author: str
    username: str
    created_at: str
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, version_number: _Optional[int] = ..., action: _Optional[str] = ..., member_product_kref: _Optional[_Union[Kref, _Mapping]] = ..., author: _Optional[str] = ..., username: _Optional[str] = ..., created_at: _Optional[str] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetCollectionHistoryRequest(_message.Message):
    __slots__ = ("collection_kref",)
    COLLECTION_KREF_FIELD_NUMBER: _ClassVar[int]
    collection_kref: Kref
    def __init__(self, collection_kref: _Optional[_Union[Kref, _Mapping]] = ...) -> None: ...

class GetCollectionHistoryResponse(_message.Message):
    __slots__ = ("history",)
    HISTORY_FIELD_NUMBER: _ClassVar[int]
    history: _containers.RepeatedCompositeFieldContainer[CollectionVersionHistory]
    def __init__(self, history: _Optional[_Iterable[_Union[CollectionVersionHistory, _Mapping]]] = ...) -> None: ...

class EventStreamRequest(_message.Message):
    __slots__ = ("routing_key_filter", "kref_filter")
    ROUTING_KEY_FILTER_FIELD_NUMBER: _ClassVar[int]
    KREF_FILTER_FIELD_NUMBER: _ClassVar[int]
    routing_key_filter: str
    kref_filter: str
    def __init__(self, routing_key_filter: _Optional[str] = ..., kref_filter: _Optional[str] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("routing_key", "kref", "timestamp", "author", "tenant_id", "details", "username")
    class DetailsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ROUTING_KEY_FIELD_NUMBER: _ClassVar[int]
    KREF_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    routing_key: str
    kref: Kref
    timestamp: str
    author: str
    tenant_id: str
    details: _containers.ScalarMap[str, str]
    username: str
    def __init__(self, routing_key: _Optional[str] = ..., kref: _Optional[_Union[Kref, _Mapping]] = ..., timestamp: _Optional[str] = ..., author: _Optional[str] = ..., tenant_id: _Optional[str] = ..., details: _Optional[_Mapping[str, str]] = ..., username: _Optional[str] = ...) -> None: ...

class CreateProjectRequest(_message.Message):
    __slots__ = ("name", "description")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class ProjectResponse(_message.Message):
    __slots__ = ("project_id", "name", "description", "created_at", "updated_at", "deprecated", "allow_public")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    deprecated: bool
    allow_public: bool
    def __init__(self, project_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., deprecated: bool = ..., allow_public: bool = ...) -> None: ...

class GetProjectsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProjectsResponse(_message.Message):
    __slots__ = ("projects",)
    PROJECTS_FIELD_NUMBER: _ClassVar[int]
    projects: _containers.RepeatedCompositeFieldContainer[ProjectResponse]
    def __init__(self, projects: _Optional[_Iterable[_Union[ProjectResponse, _Mapping]]] = ...) -> None: ...

class DeleteProjectRequest(_message.Message):
    __slots__ = ("project_id", "force")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    force: bool
    def __init__(self, project_id: _Optional[str] = ..., force: bool = ...) -> None: ...

class UpdateProjectRequest(_message.Message):
    __slots__ = ("project_id", "allow_public", "description")
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    ALLOW_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    allow_public: bool
    description: str
    def __init__(self, project_id: _Optional[str] = ..., allow_public: bool = ..., description: _Optional[str] = ...) -> None: ...

class SetDeprecatedRequest(_message.Message):
    __slots__ = ("kref", "deprecated")
    KREF_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    kref: Kref
    deprecated: bool
    def __init__(self, kref: _Optional[_Union[Kref, _Mapping]] = ..., deprecated: bool = ...) -> None: ...

class GetTenantUsageRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TenantUsageResponse(_message.Message):
    __slots__ = ("node_count", "node_limit", "tenant_id")
    NODE_COUNT_FIELD_NUMBER: _ClassVar[int]
    NODE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    node_count: int
    node_limit: int
    tenant_id: str
    def __init__(self, node_count: _Optional[int] = ..., node_limit: _Optional[int] = ..., tenant_id: _Optional[str] = ...) -> None: ...
