from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
import kumiho
from kumiho import mcp_server as m


@pytest.fixture(autouse=True)
def isolated_client(monkeypatch):
    class Client:
        pass
    client = Client()
    monkeypatch.setattr(kumiho, 'get_client', lambda: client)


def rev(item, number=1, **metadata):
    return NS(kref=NS(uri=item+'?r='+str(number)), metadata=metadata,
              created_at='2026-09-21T00:00:00Z', tags=['published'])


def test_batch_chunks_and_only_missing_fall_back(monkeypatch):
    keys = ['kref://p/s/item%d.conversation' % i for i in range(205)]
    calls=[]
    def batch(*, item_krefs, tag, allow_partial):
        calls.append((list(item_krefs),tag))
        if tag == 'published':
            return [rev(k) for k in reversed(item_krefs[1:])], [item_krefs[0]]
        return [rev(k,2) for k in item_krefs], []
    monkeypatch.setattr(kumiho,'batch_get_revisions',batch)
    result=m._batch_resolve_memory_tags(keys)
    assert set(result)==set(keys)
    assert [len(ks) for ks,t in calls]==[100,1,100,1,5,1]
    assert result[keys[0]].kref.uri.endswith('?r=2')


def test_retrieve_batch_preserves_order_types_and_reuses_metadata(monkeypatch):
    keys=['kref://p/s/a.conversation','kref://p/s/b.conversation','kref://p/s/c.conversation']
    hits=[NS(item=NS(kref=NS(uri=k)),score=1-i*.1) for i,k in enumerate(keys)]
    monkeypatch.setattr(m,'_ensure_configured',lambda:None)
    monkeypatch.setattr(kumiho,'get_project',lambda name:NS())
    monkeypatch.setattr(kumiho,'search',lambda *a,**kw:hits)
    calls=[]
    def batch(*,item_krefs,tag,allow_partial):
        calls.append((item_krefs,tag))
        if tag=='published':
            return [rev(keys[2],memory_type='fact',summary='third'),rev(keys[0],memory_type='fact',summary='first')],[keys[1]]
        return [rev(keys[1],2,memory_type='preference',summary='second')],[]
    monkeypatch.setattr(kumiho,'batch_get_revisions',batch)
    result=m.tool_memory_retrieve(project='p',query='test',limit=3,include_resolved_metadata=True,memory_types=['fact'])
    assert result['item_krefs']==[keys[0],keys[2]]
    assert result['scores']==[1,.8]
    assert len(result['resolved_metadata'])==2
    assert result['resolved_metadata'][keys[0]+'?r=1']['metadata']['summary']=='first'
    assert calls==[(keys,'published'),([keys[1]],'latest')]


def test_batch_failure_restores_individual_resolution(monkeypatch):
    key='kref://p/s/a.conversation'
    item=NS(kref=NS(uri=key),get_revision_by_tag=Mock(return_value=rev(key,summary='safe')))
    monkeypatch.setattr(m,'_ensure_configured',lambda:None)
    monkeypatch.setattr(kumiho,'get_project',lambda name:NS())
    monkeypatch.setattr(kumiho,'search',lambda *a,**kw:[NS(item=item,score=.9)])
    monkeypatch.setattr(kumiho,'batch_get_revisions',Mock(side_effect=RuntimeError('old server')))
    result=m.tool_memory_retrieve(project='p',query='test',include_resolved_metadata=True)
    assert result['revision_krefs']==[key+'?r=1']
    item.get_revision_by_tag.assert_called_once_with('published')


def test_batch_failure_backoff_is_per_client(monkeypatch):
    failed = Mock(side_effect=RuntimeError('unsupported'))
    monkeypatch.setattr(kumiho, 'batch_get_revisions', failed)
    assert m._batch_memory_tags_or_fallback(['kref://p/s/a.kind']) is None
    assert m._batch_memory_tags_or_fallback(['kref://p/s/a.kind']) is None
    assert failed.call_count == 1
    class OtherClient:
        pass
    other = OtherClient()
    monkeypatch.setattr(kumiho, 'get_client', lambda: other)
    assert m._batch_memory_tags_or_fallback(['kref://p/s/a.kind']) is None
    assert failed.call_count == 2
