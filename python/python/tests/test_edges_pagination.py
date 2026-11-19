"""Pagination for GetEdges and GetRevisions.

Runs against a real in-process gRPC server (see test_batch_ingest.py) so the
PaginationRequest the SDK builds is serialized, sent and parsed as it would be
against kumiho-db.
"""

from concurrent import futures

import grpc
import pytest

import kumiho
from kumiho.base import PagedList
from kumiho.proto import kumiho_pb2 as pb
from kumiho.proto import kumiho_pb2_grpc as pb_grpc

SRC = kumiho.Kref("kref://p/s/src.model?r=1")
ITEM = kumiho.Kref("kref://p/s/src.model")


def edge_pb(i):
    return pb.Edge(
        source_kref=pb.Kref(uri=SRC.uri),
        target_kref=pb.Kref(uri=f"kref://p/s/t{i}.model?r=1"),
        edge_type="DEPENDS_ON",
    )


def revision_pb(n):
    return pb.RevisionResponse(
        kref=pb.Kref(uri=f"{ITEM.uri}?r={n}"),
        item_kref=pb.Kref(uri=ITEM.uri),
        number=n,
    )


class PagingServicer(pb_grpc.KumihoServiceServicer):
    """Serves ``total`` rows with opaque cursors ("c<offset>")."""

    def __init__(self, total=25, default_page=10, paginate=True):
        self.total = total
        self.default_page = default_page
        self.paginate = paginate
        self.edge_requests = []
        self.revision_requests = []

    def _slice(self, request):
        size, start = self.default_page, 0
        if request.HasField("pagination"):
            size = request.pagination.page_size or size
            if request.pagination.cursor:
                start = int(request.pagination.cursor[1:])
        end = min(start + size, self.total)
        info = pb.PaginationResponse(
            next_cursor=f"c{end}" if end < self.total else "",
            has_more=end < self.total,
            total_count=self.total,
        )
        return start, end, info

    def GetEdges(self, request, context):
        self.edge_requests.append(request)
        if not self.paginate:
            return pb.GetEdgesResponse(edges=[edge_pb(i) for i in range(self.total)])
        start, end, info = self._slice(request)
        return pb.GetEdgesResponse(
            edges=[edge_pb(i) for i in range(start, end)], pagination=info
        )

    def GetRevisions(self, request, context):
        self.revision_requests.append(request)
        if not self.paginate:
            return pb.GetRevisionsResponse(
                revisions=[revision_pb(i + 1) for i in range(self.total)]
            )
        start, end, info = self._slice(request)
        return pb.GetRevisionsResponse(
            revisions=[revision_pb(i + 1) for i in range(start, end)], pagination=info
        )


class StuckServicer(pb_grpc.KumihoServiceServicer):
    """Always claims more results and hands back the same cursor."""

    def __init__(self):
        self.calls = 0

    def GetEdges(self, request, context):
        self.calls += 1
        return pb.GetEdgesResponse(
            edges=[edge_pb(self.calls)],
            pagination=pb.PaginationResponse(next_cursor="same", has_more=True),
        )

    def GetRevisions(self, request, context):
        self.calls += 1
        return pb.GetRevisionsResponse(
            revisions=[revision_pb(self.calls)],
            pagination=pb.PaginationResponse(next_cursor="same", has_more=True),
        )


def serve(servicer, monkeypatch):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    pb_grpc.add_KumihoServiceServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    monkeypatch.setenv("KUMIHO_DISABLE_AUTO_DISCOVERY", "1")
    client = kumiho.connect(
        endpoint=f"localhost:{port}", token="test-token", enable_auto_login=False
    )
    return server, client


@pytest.fixture
def paged(monkeypatch):
    servicer = PagingServicer()
    server, client = serve(servicer, monkeypatch)
    yield servicer, client
    client.channel.close()
    server.stop(0)


@pytest.fixture
def big(monkeypatch):
    # 250 rows: follow-up requests ask for 100 per page, so three pages.
    servicer = PagingServicer(total=250)
    server, client = serve(servicer, monkeypatch)
    yield servicer, client
    client.channel.close()
    server.stop(0)


@pytest.fixture
def unpaged(monkeypatch):
    servicer = PagingServicer(paginate=False)
    server, client = serve(servicer, monkeypatch)
    yield servicer, client
    client.channel.close()
    server.stop(0)


@pytest.fixture
def stuck(monkeypatch):
    servicer = StuckServicer()
    server, client = serve(servicer, monkeypatch)
    yield servicer, client
    client.channel.close()
    server.stop(0)


def targets(edges):
    return [e.target_kref.uri for e in edges]


# --- get_edges follows the cursor -------------------------------------------


def test_get_edges_returns_every_page(big):
    servicer, client = big
    edges = client.get_edges(SRC, "DEPENDS_ON", kumiho.OUTGOING)
    assert len(edges) == 250
    assert targets(edges) == [f"kref://p/s/t{i}.model?r=1" for i in range(250)]
    # First request is unpaged (server default), then the cursors chain.
    assert not servicer.edge_requests[0].HasField("pagination")
    assert [r.pagination.cursor for r in servicer.edge_requests[1:]] == ["c10", "c110", "c210"]
    assert len(servicer.edge_requests) == 4
    assert servicer.edge_requests[0].edge_type_filter == "DEPENDS_ON"
    assert servicer.edge_requests[2].edge_type_filter == "DEPENDS_ON"


def test_revision_get_edges_returns_every_page(big):
    _, client = big
    revision = kumiho.Revision(revision_pb(1), client)
    assert len(revision.get_edges()) == 250


# --- page API ----------------------------------------------------------------


def test_get_edges_page_exposes_cursor(paged):
    servicer, client = paged
    first = client.get_edges_page(SRC, page_size=10)
    assert isinstance(first, PagedList)
    assert len(first) == 10
    assert first.has_more is True and first.next_cursor == "c10"
    assert first.total_count == 25
    assert servicer.edge_requests[0].pagination.page_size == 10

    second = client.get_edges_page(SRC, page_size=10, cursor=first.next_cursor)
    assert targets(second)[0] == "kref://p/s/t10.model?r=1"

    last = client.get_edges_page(SRC, page_size=10, cursor=second.next_cursor)
    assert len(last) == 5
    assert last.has_more is False and last.next_cursor == ""


def test_revision_get_edges_page(paged):
    servicer, client = paged
    revision = kumiho.Revision(revision_pb(1), client)
    page = revision.get_edges_page(
        kumiho.DEPENDS_ON, kumiho.INCOMING, page_size=7
    )
    assert len(page) == 7 and page.has_more is True
    req = servicer.edge_requests[0]
    assert req.edge_type_filter == kumiho.DEPENDS_ON
    assert req.direction == kumiho.INCOMING
    assert req.pagination.page_size == 7


# --- servers without pagination info -----------------------------------------


def test_get_edges_old_server_without_pagination(unpaged):
    servicer, client = unpaged
    assert len(client.get_edges(SRC)) == 25
    assert len(servicer.edge_requests) == 1


def test_get_edges_page_old_server_reports_unknown(unpaged):
    _, client = unpaged
    page = client.get_edges_page(SRC)
    assert len(page) == 25
    assert page.pagination_present is False
    assert page.has_more is None and page.next_cursor is None


# --- non-advancing cursor ----------------------------------------------------


def test_get_edges_non_advancing_cursor_raises(stuck):
    servicer, client = stuck
    with pytest.raises(RuntimeError, match="did not advance"):
        client.get_edges(SRC)
    assert servicer.calls <= 3


def test_get_edges_cursor_cycle_raises(monkeypatch):
    class Cycle(pb_grpc.KumihoServiceServicer):
        def GetEdges(self, request, context):
            cur = request.pagination.cursor if request.HasField("pagination") else ""
            nxt = {"": "a", "a": "b", "b": "a"}[cur]
            return pb.GetEdgesResponse(
                edges=[edge_pb(0)],
                pagination=pb.PaginationResponse(next_cursor=nxt, has_more=True),
            )

    server, client = serve(Cycle(), monkeypatch)
    try:
        with pytest.raises(RuntimeError, match="did not advance"):
            client.get_edges(SRC)
    finally:
        client.channel.close()
        server.stop(0)


def test_has_more_without_cursor_stops(monkeypatch):
    class NoCursor(pb_grpc.KumihoServiceServicer):
        def GetEdges(self, request, context):
            return pb.GetEdgesResponse(
                edges=[edge_pb(0)],
                pagination=pb.PaginationResponse(next_cursor="", has_more=True),
            )

    server, client = serve(NoCursor(), monkeypatch)
    try:
        assert len(client.get_edges(SRC)) == 1
    finally:
        client.channel.close()
        server.stop(0)


# --- get_revisions -----------------------------------------------------------


def test_get_revisions_returns_every_page(big):
    servicer, client = big
    revisions = client.get_revisions(ITEM)
    assert [r.number for r in revisions] == list(range(1, 251))
    assert [r.pagination.cursor for r in servicer.revision_requests[1:]] == ["c10", "c110", "c210"]
    assert len(servicer.revision_requests) == 4


def test_get_revisions_page_and_item_convenience(paged):
    servicer, client = paged
    page = client.get_revisions_page(ITEM, page_size=4)
    assert len(page) == 4 and page.has_more is True and page.next_cursor == "c4"
    item = kumiho.Item(
        pb.ItemResponse(kref=pb.Kref(uri=ITEM.uri), name="src", kind="model"), client
    )
    page2 = item.get_revisions_page(page_size=4, cursor=page.next_cursor)
    assert page2[0].number == 5
    assert len(item.get_revisions()) == 25


def test_get_revisions_old_server_and_stuck_cursor(unpaged, stuck):
    _, client = unpaged
    assert len(client.get_revisions(ITEM)) == 25
    _, stuck_client = stuck
    with pytest.raises(RuntimeError, match="did not advance"):
        stuck_client.get_revisions(ITEM)
