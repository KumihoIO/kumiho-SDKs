"""Metadata presence and direct-list convenience regression coverage."""
from unittest.mock import MagicMock
import pytest
import kumiho
from kumiho.base import PagedList
from kumiho.proto import kumiho_pb2 as pb
from kumiho.space import Space

@pytest.fixture
def inventory_client(monkeypatch):
    stub=MagicMock()
    monkeypatch.setattr("kumiho.client.kumiho_pb2_grpc.KumihoServiceStub",lambda channel:stub)
    client=kumiho.connect(endpoint="127.0.0.1:1",token="",enable_auto_login=False,use_discovery=False)
    yield client,stub
    client.close()

@pytest.mark.parametrize("method,request_field,response_type",[
    ("get_child_spaces","GetChildSpaces",pb.GetChildSpacesResponse),
    ("get_items","GetItems",pb.GetItemsResponse),
])
def test_empty_final_page_is_distinct_from_missing_metadata(inventory_client,method,request_field,response_type):
    client,stub=inventory_client
    rpc=getattr(stub,request_field)
    rpc.return_value=response_type(pagination=pb.PaginationResponse(total_count=0,has_more=False,next_cursor=""))
    page=getattr(client,method)("/p")
    assert isinstance(page,list) and isinstance(page,PagedList) and not page
    assert page.pagination_present and page.has_more is False and page.total_count==0 and page.next_cursor==""
    request=rpc.call_args.args[0]
    assert not request.HasField("pagination"),"default calls must retain unpaged behavior"
    rpc.return_value=response_type()
    legacy=getattr(client,method)("/p")
    assert type(legacy) is list,"preserve the legacy return when server omits metadata"

def test_space_forwards_recursion_cursor_and_deprecated(inventory_client):
    client,stub=inventory_client
    stub.GetChildSpaces.return_value=pb.GetChildSpacesResponse(pagination=pb.PaginationResponse(total_count=8,has_more=True,next_cursor="opaque-next"))
    stub.GetItems.return_value=pb.GetItemsResponse(pagination=pb.PaginationResponse(total_count=8,has_more=True,next_cursor="opaque-next"))
    space=Space(pb.SpaceResponse(path="/p"),client)
    page=space.get_child_spaces(recursive=True,page_size=2,cursor="opaque-before")
    request=stub.GetChildSpaces.call_args.args[0]
    assert request.recursive and request.pagination.cursor=="opaque-before" and request.pagination.page_size==2
    assert page.has_more is True and page.next_cursor=="opaque-next" and page.total_count==8
    page=space.get_items(page_size=2,cursor="opaque-before",include_deprecated=True)
    request=stub.GetItems.call_args.args[0]
    assert request.include_deprecated and request.pagination.cursor=="opaque-before"
    assert page.pagination_present and page.has_more is True

def test_paged_list_old_constructor_remains_list_compatible():
    page=PagedList([1,2],"cursor",5)
    assert list(page)==[1,2] and page.next_cursor=="cursor" and page.total_count==5
    assert page.pagination_present and page.has_more is None
    assert not PagedList([]).pagination_present
