"""Opt-in real CE probe; arguments are the isolated endpoint and fixture root."""
import json
import sys
import kumiho
from kumiho.base import PagedList

client=kumiho.connect(endpoint=sys.argv[1],token="",enable_auto_login=False,use_discovery=False)
try:
    root=sys.argv[2]
    for label,fetch,key in (
        ("spaces",lambda **kw:client.get_child_spaces(root,recursive=True,**kw),lambda row:row.path),
        ("items",lambda **kw:client.get_items(root,include_deprecated=True,**kw),lambda row:row.kref.uri)):
        all_rows=fetch()
        assert isinstance(all_rows,list) and isinstance(all_rows,PagedList)
        assert len(all_rows)==all_rows.total_count==1004 and all_rows.pagination_present
        assert all_rows.has_more is False and all_rows.next_cursor==""
        expected={key(row) for row in all_rows}; ids=[]; cursor=None
        for _ in range(10):
            page=fetch(page_size=251,cursor=cursor)
            assert page.pagination_present and page.total_count==1004 and len(page)==251
            ids.extend(key(row) for row in page)
            assert page.has_more==bool(page.next_cursor)
            if not page.has_more: break
            cursor=page.next_cursor
        assert len(ids)==len(set(ids))==1004 and set(ids)==expected
    space=client.get_space(root)
    assert len(space.get_items())==1003
    assert len(space.get_items(include_deprecated=True))==1004
    assert space.get_child_spaces(recursive=True,page_size=251).total_count==1004
    print(json.dumps({"sdk":"Python fixed","unpaged":1004,"pages":[251]*4,"metadata_present":True,"deprecated_forwarded":True,"result":"PASS"}))
finally:
    client.close()
