"""The shared kref conformance corpus (``spec/kref/vectors.json``), case by case.

The corpus is the single source: this file reads it from the repository root and
runs every one of its cases through the structured parser and through the
client calls that turn a kref into a ``GetItem`` request. For each case it
checks

* the parse result (kernel verdict, ``error_class`` and every field),
* the ``GetItem`` tuple the parsed value produces,
* the bytes of the request the client sends, against the corpus's
  ``sdk_fix_request`` and, wherever decisions 1-3 do not touch the case,
  against ``sdk_current_request`` (the requests of the SDK at ``a7f155e``),
* that client-side validation accepts and refuses exactly what ``a7f155e`` did
  (``sdk_current_accepts``): no case becomes stricter, none is relaxed.

Owner decisions of 2026-10-29 that change requests:

1. ``get_bundle_by_kref`` fetches the bundle the kref names (dotted bundle names
   and dotted spaces included).
2. The new grammar is the only one: ``kref:///s/x.k`` maps to the server
   equivalent ``("//s", "x", "k")``; a leaf without ``.`` where an item is
   required is refused before sending.
3. ``Kref.get_kind()`` splits at the LAST ``.``.
"""

import json
import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

import kumiho
import mock_helpers
from kumiho.kref import Kref, KrefValidationError, is_valid_kref
from kumiho.proto import kumiho_pb2

VECTORS_PATH = Path(__file__).resolve().parents[3] / "spec" / "kref" / "vectors.json"
VECTORS = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
CASES = VECTORS["cases"]

# Cases whose GetItem request is allowed to change versus a7f155e, and why.
# Everything else must be byte-identical to ``sdk_current_request``.
#   - The request changes only where the corpus proves it server-equivalent
#     (``server_equivalent_old_new.get_item_by_kref.equivalent``).
#   - Decision 2: a leaf without '.' where an item is required is refused.
REFUSED_BY_DECISION_2 = {"dotted-space-leaf-without-dot"}
# Decision 1: these bundle re-fetches name a different node than a7f155e used.
BUNDLE_REFETCH_FIXED_BY_DECISION_1 = {"bundle-dotted-name", "bundle-in-dotted-space"}


def _case_id(case):
    return case["id"]


def _parse(uri):
    from kumiho.kref import parse_kref

    return parse_kref(uri)


@pytest.fixture
def mock_client(monkeypatch):
    """A Kumiho client over a mocked gRPC stub, restored after the test."""
    original_client = kumiho._default_client

    mock_stub = MagicMock()
    monkeypatch.setattr(
        "kumiho.client.kumiho_pb2_grpc.KumihoServiceStub", lambda channel: mock_stub
    )
    client = kumiho.connect(endpoint="localhost:50051", token="mock-token")
    kumiho.configure_default_client(client)

    yield client, mock_stub

    kumiho._default_client = original_client


def _get_item_bytes(request):
    return request.SerializeToString()


def _expected_get_item_bytes(expected):
    return kumiho_pb2.GetItemRequest(
        parent_path=expected["parent_path"],
        item_name=expected["item_name"],
        kind=expected["kind"],
    ).SerializeToString()


def _item_for(case_input, kind):
    return mock_helpers.mock_item_response(
        kref_uri=case_input.split("?", 1)[0],
        name=f"item.{kind}",
        item_name="item",
        kind=kind,
    )


def test_corpus_is_the_shared_one():
    assert VECTORS["schema"] == "kumiho-kref-vectors/1"
    assert len(CASES) == 133
    assert len({c["id"] for c in CASES}) == len(CASES)


# --------------------------------------------------------------------------
# The parser: one structured value per kref.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_parse_matches_the_kernel_reading(case):
    parts = _parse(case["input"])

    assert parts.valid is case["valid"]
    assert parts.error_class == case["error_class"]
    assert parts.base == case["base"]
    assert list(parts.shapes) == case["shapes"]
    assert parts.project == case["project"]
    assert (list(parts.space_path) if parts.space_path is not None else None) == case[
        "space_path"
    ]
    assert parts.item_name == case["item_name"]
    assert parts.kind == case["kind"]
    assert parts.is_project_root_item == case["is_project_root_item"]
    assert parts.revision == case["revision"]
    assert parts.tag == case["tag"]
    assert parts.artifact == case["artifact"]


@pytest.mark.parametrize(
    "case", [c for c in CASES if c["get_item_tuple"]], ids=_case_id
)
def test_get_item_tuple_matches_the_grammar(case):
    expected = case["get_item_tuple"]

    assert _parse(case["input"]).get_item_tuple() == (
        expected["parent_path"],
        expected["item_name"],
        expected["kind"],
    )


# --------------------------------------------------------------------------
# Client-side validation is unchanged: not stricter, not relaxed.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_validation_accepts_exactly_what_a7f155e_accepted(case):
    assert is_valid_kref(case["input"]) is case["sdk_current_accepts"]


@pytest.mark.parametrize(
    "case", [c for c in CASES if not c["sdk_current_accepts"]], ids=_case_id
)
def test_refused_krefs_are_still_refused_before_sending(mock_client, case):
    client, mock_stub = mock_client

    with pytest.raises(KrefValidationError):
        client.get_item_by_kref(case["input"])
    with pytest.raises(KrefValidationError):
        client.get_bundle_by_kref(case["input"])

    mock_stub.GetItem.assert_not_called()


# --------------------------------------------------------------------------
# The GetItem request the client sends.
# --------------------------------------------------------------------------

ACCEPTED = [c for c in CASES if c["sdk_current_accepts"]]


def _classify(current, expected):
    """How the request changed versus a7f155e: same | changed | refused | message."""
    current_error, expected_error = "error" in current, "error" in expected
    if current_error and expected_error:
        return "same" if current == expected else "message"
    if expected_error:
        return "refused"
    assert not current_error, "a request where a7f155e raised"
    return "same" if current == expected else "changed"


def _assert_item_request(case, call):
    """Run ``call()``, compare the GetItem bytes with the corpus, and check that
    every change versus a7f155e is one the owner decisions allow."""
    expected = case["sdk_fix_request"]["get_item_by_kref"]
    current = case["sdk_current_request"]["get_item_by_kref"]
    change = _classify(current, expected)

    if "error" in expected:
        with pytest.raises(ValueError) as caught:
            call()
        # The same exception type as a7f155e's malformed-kref error.
        assert type(caught.value) is ValueError
        assert str(caught.value) == expected["message"]
    else:
        sent = [_get_item_bytes(r) for r in call()]
        assert sent == [_expected_get_item_bytes(expected)]
        if change == "same":
            # Untouched: byte-identical to a7f155e (root-level items without a
            # dot in the name among them).
            assert sent == [_expected_get_item_bytes(current)]

    if change == "changed":
        # Every changed request must be one the corpus proves the server
        # resolves to the same node as a7f155e's request.
        equivalence = case["server_equivalent_old_new"]["get_item_by_kref"]
        assert equivalence["equivalent"] is True, case["id"]
    elif change == "refused":
        assert case["id"] in REFUSED_BY_DECISION_2, case["id"]
    return change


@pytest.mark.parametrize("case", ACCEPTED, ids=_case_id)
def test_get_item_by_kref_sends_the_corpus_request(mock_client, case):
    client, mock_stub = mock_client
    mock_stub.GetItem.return_value = _item_for(case["input"], "k")

    def call():
        mock_stub.GetItem.reset_mock()
        client.get_item_by_kref(case["input"])
        return [c.args[0] for c in mock_stub.GetItem.call_args_list]

    _assert_item_request(case, call)


@pytest.mark.parametrize("case", ACCEPTED, ids=_case_id)
def test_get_item_from_revision_sends_the_corpus_request(mock_client, case):
    client, mock_stub = mock_client
    item_kref = case["input"]
    mock_stub.GetRevision.return_value = mock_helpers.mock_revision_response(
        kref_uri=f"{item_kref.split('?', 1)[0]}?r=1",
        item_kref_uri=item_kref,
        number=1,
        latest=True,
        tags=[],
        metadata={},
        author="test_author",
        username="test_user",
        deprecated=False,
        published=False,
    )
    mock_stub.GetItem.return_value = _item_for(item_kref, "k")

    def call():
        mock_stub.GetItem.reset_mock()
        client.get_item_from_revision(f"{item_kref.split('?', 1)[0]}?r=1")
        return [c.args[0] for c in mock_stub.GetItem.call_args_list]

    _assert_item_request(case, call)


BUNDLES = [
    c
    for c in ACCEPTED
    if isinstance(c["sdk_fix_request"]["get_bundle_by_kref_refetch"], dict)
    and "rpc" in c["sdk_fix_request"]["get_bundle_by_kref_refetch"]
]


def test_the_corpus_has_bundle_cases():
    assert {c["id"] for c in BUNDLES} >= {
        "bundle",
        "bundle-root",
        "bundle-nested",
        "bundle-dotted-name",
        "bundle-in-dotted-space",
        "bundle-revision",
        "bundle-artifact-parses",
    }


@pytest.mark.parametrize("case", BUNDLES, ids=_case_id)
def test_get_bundle_by_kref_fetches_the_bundle_the_kref_names(mock_client, case):
    client, mock_stub = mock_client
    mock_stub.GetItem.return_value = _item_for(case["input"], "bundle")

    client.get_bundle_by_kref(case["input"])

    expected = case["sdk_fix_request"]["get_bundle_by_kref_refetch"]
    sent = [_get_item_bytes(c.args[0]) for c in mock_stub.GetItem.call_args_list]
    # One GetItem to look the item up and one to re-fetch the Bundle wrapper;
    # both name the bundle the kref names.
    assert sent == [_expected_get_item_bytes(expected)] * 2
    assert expected == case["sdk_fix_request"]["get_item_by_kref"]

    current = case["sdk_current_request"]["get_bundle_by_kref_refetch"]
    if case["id"] in BUNDLE_REFETCH_FIXED_BY_DECISION_1:
        # a7f155e re-fetched a different node; decision 1 fixes it.
        assert case["server_equivalent_old_new"]["get_bundle_by_kref_refetch"][
            "equivalent"
        ] is False
    else:
        equivalence = case["server_equivalent_old_new"]["get_bundle_by_kref_refetch"]
        assert equivalence["equivalent"] is True, case["id"]
        if current == expected:
            assert sent == [_expected_get_item_bytes(current)] * 2


@pytest.mark.parametrize(
    "case",
    [c for c in ACCEPTED if "rpc" not in c["sdk_fix_request"]["get_bundle_by_kref_refetch"]],
    ids=_case_id,
)
def test_get_bundle_by_kref_still_refuses_non_bundles(mock_client, case):
    client, mock_stub = mock_client
    expected = case["sdk_fix_request"]["get_item_by_kref"]
    if "error" in expected:
        with pytest.raises(ValueError):
            client.get_bundle_by_kref(case["input"])
        mock_stub.GetItem.assert_not_called()
        return

    mock_stub.GetItem.return_value = _item_for(case["input"], expected["kind"])
    with pytest.raises(ValueError, match="is not a bundle"):
        client.get_bundle_by_kref(case["input"])
    # No re-fetch: the lookup already showed the item is not a bundle.
    assert mock_stub.GetItem.call_count == 1


# --------------------------------------------------------------------------
# Requests the parser does not touch stay as they were.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_get_revision_and_resolve_requests_are_unchanged(mock_client, case):
    client, mock_stub = mock_client
    mock_stub.GetRevision.return_value = mock_helpers.mock_revision_response(
        kref_uri=case["input"], item_kref_uri=case["input"]
    )
    mock_stub.ResolveKref.return_value = mock_helpers.mock_revision_response(
        kref_uri=case["input"], item_kref_uri=case["input"]
    )
    mock_stub.ResolveLocation.return_value = kumiho_pb2.ResolveLocationResponse(
        location="loc"
    )

    expected = case["sdk_current_request"]["get_revision"]
    if "error" in expected:
        with pytest.raises(ValueError, match=re.escape(expected["message"])):
            client.get_revision(case["input"])
    else:
        client.get_revision(case["input"])
        if expected["rpc"] == "GetRevision":
            sent = mock_stub.GetRevision.call_args.args[0]
            assert sent.SerializeToString() == kumiho_pb2.KrefRequest(
                kref=kumiho_pb2.Kref(uri=expected["kref"])
            ).SerializeToString()
        else:
            sent = mock_stub.ResolveKref.call_args.args[0]
            assert sent.SerializeToString() == kumiho_pb2.ResolveKrefRequest(
                kref=expected["kref"], tag=expected["tag"], time=expected["time"]
            ).SerializeToString()

    expected = case["sdk_current_request"]["resolve"]
    client.resolve(case["input"])
    sent = mock_stub.ResolveLocation.call_args.args[0]
    assert sent.SerializeToString() == kumiho_pb2.ResolveLocationRequest(
        kref=expected["kref"], tag=expected["tag"], time=expected["time"]
    ).SerializeToString()


# --------------------------------------------------------------------------
# Public accessors: only get_kind() changes (decision 3).
# --------------------------------------------------------------------------

ACCESSORS = [
    "get_path",
    "get_project",
    "get_space",
    "get_item_name",
    "get_kind",
    "get_revision",
    "get_artifact_name",
]


@pytest.mark.parametrize("case", ACCEPTED, ids=_case_id)
def test_accessors_match_a7f155e_except_get_kind(case):
    kref = Kref(case["input"])
    expected = dict(case["sdk_current_accessors"])
    for name, change in (case["sdk_fix_accessor_changes"] or {}).items():
        assert name == "get_kind", f"{case['id']}: only get_kind may change"
        expected[name] = change["fix"]

    assert {name: getattr(kref, name)() for name in ACCESSORS} == expected


def test_get_kind_splits_at_the_last_dot():
    assert Kref("kref://p/s/my.file.v2.k").get_kind() == "k"
    assert Kref("kref://p/s/x.tar.gz").get_kind() == "gz"
    assert Kref("kref://p/s/x").get_kind() == ""
