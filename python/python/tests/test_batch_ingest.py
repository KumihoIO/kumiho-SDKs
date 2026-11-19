"""BatchIngest and GetMutationCapabilities.

Most tests run against a real in-process gRPC server (a servicer on a loopback
port) so the request is built, serialized, sent through the SDK's interceptors
and parsed back exactly as it would be against kumiho-db. A servicer that does
not override an RPC answers UNIMPLEMENTED, which is what kumiho-server (CE)
does for BatchIngest.
"""

from concurrent import futures

import grpc
import pytest

import kumiho
from kumiho.proto import kumiho_pb2 as pb
from kumiho.proto import kumiho_pb2_grpc as pb_grpc


def revision_pb(item, number, *, tags=(), latest=True, published=False):
    return pb.RevisionResponse(
        kref=pb.Kref(uri=f"{item}?r={number}"),
        item_kref=pb.Kref(uri=item),
        number=number,
        tags=list(tags),
        latest=latest,
        published=published,
    )


class OldServicer(pb_grpc.KumihoServiceServicer):
    """A server that predates BatchIngest: every unknown RPC is UNIMPLEMENTED."""


class IngestServicer(pb_grpc.KumihoServiceServicer):
    def __init__(self):
        self.requests = []
        self.capabilities_requests = 0
        self.ingest_response = None

    def GetMutationCapabilities(self, request, context):
        self.capabilities_requests += 1
        return pb.MutationCapabilities(
            batch_ingest=True,
            batch_expected_latest_revision=True,
            transactional_idempotency_fingerprint=True,
            atomic_derived_from_edges=False,
            contract_version="2026-11",
        )

    def BatchIngest(self, request, context):
        self.requests.append(request)
        if self.ingest_response is not None:
            return self.ingest_response
        results = [
            revision_pb(row.revision.item_kref.uri, i + 1)
            for i, row in enumerate(request.revisions)
        ]
        return pb.BatchIngestResponse(
            results=results,
            edges=[
                pb.IngestEdgeResult(succeeded=True, created=True)
                for _ in request.edges
            ],
            tags=[
                pb.IngestTagResult(
                    succeeded=True, revision_number=t.row_index + 1, tag_version=1,
                    changed=True,
                )
                for t in request.tags
            ],
            requested_count=len(results),
            succeeded_count=len(results),
            edges_succeeded_count=len(request.edges),
            tags_succeeded_count=len(request.tags),
        )


def serve(servicer, monkeypatch):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    pb_grpc.add_KumihoServiceServicer_to_server(servicer, server)
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    # The client must not look up or log in anywhere.
    monkeypatch.setenv("KUMIHO_DISABLE_AUTO_DISCOVERY", "1")
    client = kumiho.connect(
        endpoint=f"localhost:{port}", token="test-token", enable_auto_login=False
    )
    return server, client


@pytest.fixture
def ingest(monkeypatch):
    servicer = IngestServicer()
    server, client = serve(servicer, monkeypatch)
    yield servicer, client
    client.channel.close()
    server.stop(0)


@pytest.fixture
def old_server(monkeypatch):
    server, client = serve(OldServicer(), monkeypatch)
    yield client
    client.channel.close()
    server.stop(0)


A = "kref://p/mem/a.memory"
B = "kref://p/mem/b.memory"
OLD = "kref://p/mem/old.memory?r=3"


# --- request building --------------------------------------------------------


def test_request_field_mapping(ingest):
    servicer, client = ingest
    result = client.batch_ingest(
        revisions=[
            kumiho.RevisionInput(
                A,
                {"title": "A"},
                embedding_text="about a",
                artifacts=[
                    kumiho.ArtifactInput(
                        "transcript", "s3://b/a.md", {"mime": "text/markdown"},
                        is_default=True,
                    ),
                    kumiho.ArtifactInput("raw.json", "s3://b/a.json"),
                ],
            ),
            kumiho.RevisionInput(kumiho.Kref(B)),
        ],
        edges=[
            kumiho.IngestEdge(kumiho.RowRef(0), kumiho.RowRef(1), "DERIVED_FROM",
                              {"why": "summary"}),
            kumiho.IngestEdge(1, kumiho.KrefRef(OLD), "DEPENDS_ON"),
            kumiho.IngestEdge(kumiho.Kref(OLD), 0, "REFERENCED"),
        ],
        tags=[kumiho.IngestTag(0, "published"), kumiho.IngestTag(1, "reviewed")],
        idempotency_prefix="import-1",
    )
    assert result.ok

    (req,) = servicer.requests
    assert req.idempotency_prefix == "import-1"
    assert [r.revision.item_kref.uri for r in req.revisions] == [A, B]
    row = req.revisions[0]
    assert row.revision.metadata["title"] == "A"
    assert row.revision.embedding_text == "about a"
    assert [a.name for a in row.artifacts] == ["transcript", "raw.json"]
    assert row.artifacts[0].is_default and not row.artifacts[1].is_default
    assert row.artifacts[0].location == "s3://b/a.md"
    assert row.artifacts[0].metadata["mime"] == "text/markdown"
    assert not req.revisions[1].artifacts

    e0, e1, e2 = req.edges
    assert e0.source.WhichOneof("target") == "row_index" and e0.source.row_index == 0
    assert e0.target.row_index == 1
    assert e0.edge_type == "DERIVED_FROM" and e0.metadata["why"] == "summary"
    assert e1.source.row_index == 1
    assert e1.target.WhichOneof("target") == "revision_kref"
    assert e1.target.revision_kref.uri == OLD
    assert e2.source.revision_kref.uri == OLD and e2.target.row_index == 0

    assert [(t.row_index, t.tag) for t in req.tags] == [(0, "published"), (1, "reviewed")]


def test_row_index_zero_is_sent_as_a_row_ref(ingest):
    # row_index 0 is the proto default; it must still select the oneof arm.
    servicer, client = ingest
    client.batch_ingest(
        revisions=[kumiho.RevisionInput(A), kumiho.RevisionInput(B)],
        edges=[kumiho.IngestEdge(0, 1, "DEPENDS_ON")],
        idempotency_prefix="p",
    )
    edge = servicer.requests[0].edges[0]
    assert edge.source.WhichOneof("target") == "row_index"
    assert edge.source.row_index == 0


def test_dict_rows_match_batch_create_revisions_shape(ingest):
    servicer, client = ingest
    client.batch_ingest(
        revisions=[
            {"item_kref": A, "metadata": {"t": "1"}, "embedding_text": "x",
             "artifacts": [{"name": "n", "location": "s3://x", "default": True}]},
        ],
        idempotency_prefix="p",
    )
    row = servicer.requests[0].revisions[0]
    assert row.revision.item_kref.uri == A
    assert row.revision.embedding_text == "x"
    assert row.artifacts[0].is_default


def test_module_level_wrappers_use_the_default_client(ingest):
    servicer, client = ingest
    original = kumiho._default_client
    kumiho.configure_default_client(client)
    try:
        caps = kumiho.get_mutation_capabilities()
        assert caps.batch_ingest
        result = kumiho.batch_ingest(
            revisions=[kumiho.RevisionInput(A)], idempotency_prefix="mod"
        )
    finally:
        kumiho._default_client = original
    assert result.ok
    assert servicer.requests[0].idempotency_prefix == "mod"


# --- receipts ----------------------------------------------------------------


def test_receipts_are_positional_sdk_objects(ingest):
    servicer, client = ingest
    servicer.ingest_response = pb.BatchIngestResponse(
        results=[
            revision_pb(A, 1, tags=["published"], published=True),
            revision_pb(B, 4),
        ],
        edges=[
            pb.IngestEdgeResult(succeeded=True, created=True),
            pb.IngestEdgeResult(succeeded=True, created=False, replayed=True),
        ],
        tags=[
            pb.IngestTagResult(succeeded=True, revision_number=1, tag_version=7,
                               changed=True),
            pb.IngestTagResult(succeeded=True, revision_number=4, tag_version=2,
                               changed=False, replayed=True),
        ],
        requested_count=2, succeeded_count=2,
    )
    result = client.batch_ingest(
        revisions=[kumiho.RevisionInput(A), kumiho.RevisionInput(B)],
        edges=[kumiho.IngestEdge(0, 1, "DEPENDS_ON"),
               kumiho.IngestEdge(1, 0, "REFERENCED")],
        tags=[kumiho.IngestTag(0, "published"), kumiho.IngestTag(1, "x")],
        idempotency_prefix="p",
    )
    assert result.ok and result.failures == []
    first, second = result.revisions
    assert isinstance(first, kumiho.Revision)
    assert first.kref.uri == f"{A}?r=1" and first.number == 1
    assert second.number == 4
    assert result.edges == [
        kumiho.EdgeReceipt(created=True, replayed=False),
        kumiho.EdgeReceipt(created=False, replayed=True),
    ]
    assert result.tags[0] == kumiho.TagReceipt(
        revision_number=1, tag_version=7, changed=True, replayed=False
    )
    assert result.tags[1].replayed and not result.tags[1].changed


def test_partial_failures_are_none_and_listed(ingest):
    servicer, client = ingest
    servicer.ingest_response = pb.BatchIngestResponse(
        results=[revision_pb(A, 1), pb.RevisionResponse()],  # failed row = empty stub
        failures=[pb.BatchRevisionFailure(index=1, reason="Parent space not found")],
        edges=[pb.IngestEdgeResult(succeeded=False)],
        edge_failures=[pb.BatchRevisionFailure(index=0, reason="row 1 was rejected")],
        tags=[pb.IngestTagResult(succeeded=False)],
        tag_failures=[pb.BatchRevisionFailure(index=0, reason="tag refused")],
    )
    result = client.batch_ingest(
        revisions=[kumiho.RevisionInput(A), kumiho.RevisionInput("kref://p/nope/x.memory")],
        edges=[kumiho.IngestEdge(0, 1, "DEPENDS_ON")],
        tags=[kumiho.IngestTag(1, "t")],
        idempotency_prefix="p",
    )
    assert not result.ok
    assert result.revisions[0] is not None and result.revisions[1] is None
    assert result.edges == [None] and result.tags == [None]
    assert [(f.kind, f.index, f.reason) for f in result.failures] == [
        ("revision", 1, "Parent space not found"),
        ("edge", 0, "row 1 was rejected"),
        ("tag", 0, "tag refused"),
    ]


def test_element_without_receipt_or_reason_is_still_a_failure(ingest):
    servicer, client = ingest
    servicer.ingest_response = pb.BatchIngestResponse(
        results=[pb.RevisionResponse()],
        edges=[],
        tags=[pb.IngestTagResult(succeeded=False)],
    )
    result = client.batch_ingest(
        revisions=[kumiho.RevisionInput(A)],
        tags=[kumiho.IngestTag(0, "t")],
        idempotency_prefix="p",
    )
    assert not result.ok
    assert {(f.kind, f.index) for f in result.failures} == {("revision", 0), ("tag", 0)}


# --- capabilities and UNIMPLEMENTED ------------------------------------------


def test_get_mutation_capabilities(ingest):
    servicer, client = ingest
    caps = client.get_mutation_capabilities()
    assert caps == kumiho.MutationCapabilities(
        batch_ingest=True,
        batch_expected_latest_revision=True,
        transactional_idempotency_fingerprint=True,
        atomic_derived_from_edges=False,
        contract_version="2026-11",
    )
    assert servicer.capabilities_requests == 1


def test_capabilities_on_a_server_without_the_rpc_are_all_false(old_server):
    caps = old_server.get_mutation_capabilities()
    assert caps == kumiho.MutationCapabilities()
    assert not caps.batch_ingest and caps.contract_version == ""


def test_batch_ingest_unimplemented_is_a_descriptive_error(old_server):
    with pytest.raises(kumiho.BatchIngestUnsupportedError) as info:
        old_server.batch_ingest(
            revisions=[kumiho.RevisionInput(A)], idempotency_prefix="p"
        )
    err = info.value
    assert "BatchIngest" in str(err) and "get_mutation_capabilities" in str(err)
    assert isinstance(err, grpc.RpcError)  # existing `except grpc.RpcError` still works
    assert err.code() == grpc.StatusCode.UNIMPLEMENTED
    assert isinstance(err.__cause__, grpc.RpcError)


def test_other_rpc_errors_are_not_remapped(monkeypatch):
    class Denied(pb_grpc.KumihoServiceServicer):
        def BatchIngest(self, request, context):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "no write access")

        def GetMutationCapabilities(self, request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "bad token")

    server, client = serve(Denied(), monkeypatch)
    try:
        with pytest.raises(grpc.RpcError) as info:
            client.batch_ingest(
                revisions=[kumiho.RevisionInput(A)], idempotency_prefix="p"
            )
        assert not isinstance(info.value, kumiho.BatchIngestUnsupportedError)
        assert info.value.code() == grpc.StatusCode.PERMISSION_DENIED
        with pytest.raises(grpc.RpcError) as info:
            client.get_mutation_capabilities()
        assert info.value.code() == grpc.StatusCode.UNAUTHENTICATED
    finally:
        client.channel.close()
        server.stop(0)


# --- client-side checks (nothing is sent) ------------------------------------


@pytest.fixture
def no_network(ingest):
    servicer, client = ingest
    yield client, servicer
    assert servicer.requests == [], "a refused request must not reach the server"


def rows(n):
    return [kumiho.RevisionInput(f"kref://p/mem/m{i}.memory") for i in range(n)]


def test_prefix_is_required(no_network):
    client, _ = no_network
    for prefix in ("", "   "):
        with pytest.raises(kumiho.BatchIngestValidationError, match="idempotency_prefix"):
            client.batch_ingest(revisions=rows(1), idempotency_prefix=prefix)
    with pytest.raises(TypeError):
        client.batch_ingest(revisions=rows(1))  # keyword-only and required


def test_count_limits(no_network):
    client, _ = no_network
    with pytest.raises(kumiho.BatchIngestValidationError, match="revisions is 201.*200"):
        client.batch_ingest(revisions=rows(201), idempotency_prefix="p")
    edges = [kumiho.IngestEdge(0, 1, "DEPENDS_ON")] * 501
    with pytest.raises(kumiho.BatchIngestValidationError, match="edges is 501.*500"):
        client.batch_ingest(revisions=rows(2), edges=edges, idempotency_prefix="p")
    tags = [kumiho.IngestTag(0, "t")] * 501
    with pytest.raises(kumiho.BatchIngestValidationError, match="tags is 501.*500"):
        client.batch_ingest(revisions=rows(1), tags=tags, idempotency_prefix="p")


def test_read_budget_limit(no_network):
    # Each count is within its own cap, but 200 revisions + 500 edges + 500 tags
    # is 12,000 + 32,000 estimated reads, over the 32,000 budget.
    client, _ = no_network
    edges = [kumiho.IngestEdge(0, 1, "DEPENDS_ON")] * 500
    tags = [kumiho.IngestTag(0, "t")] * 500
    with pytest.raises(kumiho.BatchIngestValidationError, match="budget of 32000"):
        client.batch_ingest(
            revisions=rows(200), edges=edges, tags=tags, idempotency_prefix="p"
        )


def test_custom_limits(no_network):
    client, _ = no_network
    with pytest.raises(kumiho.BatchIngestValidationError, match="revisions is 3.*2"):
        client.batch_ingest(
            revisions=rows(3),
            idempotency_prefix="p",
            limits=kumiho.BatchIngestLimits(max_revisions=2),
        )


def test_the_documented_maximum_is_accepted(ingest):
    servicer, client = ingest
    result = client.batch_ingest(
        revisions=rows(200),
        edges=[kumiho.IngestEdge(0, 1, "DEPENDS_ON")] * 500,
        tags=[kumiho.IngestTag(0, "t")] * 125,
        idempotency_prefix="p",
    )
    assert result.ok
    assert len(servicer.requests[0].edges) == 500


def test_latest_tag_is_refused(no_network):
    client, _ = no_network
    with pytest.raises(kumiho.BatchIngestValidationError, match="latest"):
        client.batch_ingest(
            revisions=rows(1), tags=[kumiho.IngestTag(0, "latest")],
            idempotency_prefix="p",
        )


def test_tags_attach_only_to_rows_in_the_request(no_network):
    client, _ = no_network
    for bad in (1, -1):
        with pytest.raises(kumiho.BatchIngestValidationError, match="not in the request"):
            client.batch_ingest(
                revisions=rows(1), tags=[kumiho.IngestTag(bad, "t")],
                idempotency_prefix="p",
            )
    with pytest.raises(kumiho.BatchIngestValidationError, match="empty"):
        client.batch_ingest(
            revisions=rows(1), tags=[kumiho.IngestTag(0, "")], idempotency_prefix="p"
        )


def test_edge_ends_are_checked(no_network):
    client, _ = no_network

    def refused(edge, match):
        with pytest.raises(kumiho.BatchIngestValidationError, match=match):
            client.batch_ingest(revisions=rows(2), edges=[edge], idempotency_prefix="p")

    refused(kumiho.IngestEdge(0, 2, "DEPENDS_ON"), "row 2.*not in the request")
    refused(kumiho.IngestEdge(-1, 0, "DEPENDS_ON"), "row -1")
    refused(kumiho.IngestEdge(0, 0, "DEPENDS_ON"), "itself")
    refused(kumiho.IngestEdge("kref://p/s/x.k?r=1", "kref://p/s/x.k?r=1", "DEPENDS_ON"),
            "itself")
    # an item kref, a tag selector and an artifact are not revisions named by number
    refused(kumiho.IngestEdge(0, "kref://p/s/x.k", "DEPENDS_ON"), "by number")
    refused(kumiho.IngestEdge(0, "kref://p/s/x.k?t=latest", "DEPENDS_ON"), "by number")
    refused(kumiho.IngestEdge(0, "kref://p/s/x.k?r=0", "DEPENDS_ON"), "by number")
    refused(kumiho.IngestEdge(0, "kref://p/s/x.k?r=1&a=main", "DEPENDS_ON"), "by number")
    refused(kumiho.IngestEdge(0, True, "DEPENDS_ON"), "bool")


def test_edge_names_are_checked(no_network):
    client, _ = no_network
    for name in ("depends_on", "", "1ABC", "A" * 51, "A-B"):
        with pytest.raises(kumiho.BatchIngestValidationError, match="edge_type"):
            client.batch_ingest(
                revisions=rows(2), edges=[kumiho.IngestEdge(0, 1, name)],
                idempotency_prefix="p",
            )


def test_row_checks(no_network):
    client, _ = no_network

    def refused(spec, match):
        with pytest.raises(kumiho.BatchIngestValidationError, match=match):
            client.batch_ingest(revisions=[spec], idempotency_prefix="p")

    refused({"metadata": {}}, r"revisions\[0\] is missing 'item_kref'")
    refused(kumiho.RevisionInput("p/s/x.k"), "item kref")
    refused(kumiho.RevisionInput("kref://p/s/x.k?r=1"), "without a selector")
    art = kumiho.ArtifactInput
    refused(kumiho.RevisionInput(A, artifacts=[art("bad name", "s3://x")]), "kref-safe")
    refused(kumiho.RevisionInput(A, artifacts=[art("a", "")]), "location")
    refused(kumiho.RevisionInput(A, artifacts=[art("a", "x"), art("a", "y")]), "duplicate")
    refused(
        kumiho.RevisionInput(
            A, artifacts=[art("a", "x", is_default=True), art("b", "y", is_default=True)]
        ),
        "more than one",
    )


def test_empty_request_is_valid_and_sent(ingest):
    servicer, client = ingest
    result = client.batch_ingest(idempotency_prefix="p")
    assert result.ok and result.revisions == [] and len(servicer.requests) == 1
