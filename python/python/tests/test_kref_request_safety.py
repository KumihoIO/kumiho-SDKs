"""A kref never raises in the parser and never reaches a different node than a7f155e.

Three guarantees, each pinned here:

* ``parse_kref`` is total. Its kernel reading is computed lazily, and it never
  converts a digit string to an ``int`` that the kernel would refuse anyway, so
  a revision of 4301 or more digits (which ``int()`` rejects) is just a refused
  revision, not an exception on the request path.
* The ``GetItem`` request built from a kref names, on kumiho-server, the node
  that a7f155e's request named. kumiho-server builds the key it matches as
  ``normalize_space_path(parent_path)`` + ``/`` + ``item_name`` + ``.`` + ``kind``
  (``src/item.rs:14-31`` and ``:443-449``), where ``normalize_space_path`` trims
  whitespace and ``/``. A parent that ends in whitespace or in an empty
  segment would be normalized to a different space, so for those krefs the
  request keeps the shape a7f155e used.
* A kind that contains ``/`` is not valid: ``Project.get_item`` refuses it before
  sending (owner decision 2026-10-29).
"""

import pytest
from unittest.mock import MagicMock

import kumiho
import mock_helpers
from kumiho import kref as kref_module
from kumiho.kref import Kref, parse_kref

# Rust's char::is_whitespace, which is what kumiho-server trims.
RUST_WHITESPACE = (
    "\t\n\x0b\x0c\r \x85\xa0        "
    "        　"
)


def server_normalize_space_path(path):
    """kumiho-server ``normalize_space_path`` (src/item.rs:14-31)."""
    trimmed = path.strip(RUST_WHITESPACE)
    if not trimmed:
        return "/"
    without_trailing = trimmed.rstrip("/")
    if not without_trailing:
        return "/"
    without_leading = without_trailing.lstrip("/")
    if not without_leading:
        return "/"
    return "/" + without_leading


def server_key(request):
    """The kref string kumiho-server matches for a GetItem request (item.rs:443-449)."""
    parent, name, kind = request
    base = server_normalize_space_path(parent).lstrip("/")
    return f"kref://{name}.{kind}" if not base else f"kref://{base}/{name}.{kind}"


def a7f155e_request(uri):
    """The GetItem request a7f155e sent: split at the first '/' and the first '.'."""
    path = uri.split("://", 1)[1].split("?", 1)[0]
    project, rest = path.split("/", 1)
    name, kind = rest.split(".", 1)
    return f"/{project}", name, kind


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


def _item_response(kref_uri, item_name, kind):
    return mock_helpers.mock_item_response(
        kref_uri=kref_uri, name=f"{item_name}.{kind}", item_name=item_name, kind=kind
    )


def _revision_for(item_kref):
    return mock_helpers.mock_revision_response(
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


def _sent_requests(stub):
    return [
        (c.args[0].parent_path, c.args[0].item_name, c.args[0].kind)
        for c in stub.GetItem.call_args_list
    ]


# --------------------------------------------------------------------------
# parse_kref is total.
# --------------------------------------------------------------------------

HUGE_REVISION = "kref://p/s/x.k?r=" + "1" * 4301


def test_parse_kref_of_a_4301_digit_revision_does_not_raise():
    parts = parse_kref(HUGE_REVISION)

    assert parts.valid is False
    assert parts.error_class == "revision_number"
    assert parts.revision is None
    assert parts.get_item_tuple() == ("/p/s", "x", "k")


@pytest.mark.parametrize("digits", [20, 21, 4300, 4301, 100000])
def test_a_digit_string_past_u64_is_a_refused_revision(digits):
    parts = parse_kref("kref://p/s/x.k?r=" + "9" * digits)

    assert parts.error_class == "revision_number"
    assert parts.revision is None


def test_the_u64_boundary_is_exact():
    assert parse_kref("kref://p/s/x.k?r=18446744073709551615").revision == 2**64 - 1
    assert parse_kref("kref://p/s/x.k?r=18446744073709551616").revision is None
    # 20 digits that are still past u64::MAX are refused, 21 never get converted.
    assert parse_kref("kref://p/s/x.k?r=99999999999999999999").error_class == "revision_number"
    assert parse_kref("kref://p/s/x.k?r=100000000000000000000").error_class == "revision_number"
    # A leading zero is refused whatever its length.
    assert parse_kref("kref://p/s/x.k?r=0" + "1" * 5000).error_class == "revision_number"


@pytest.mark.parametrize(
    "uri",
    [
        "",
        "kref://",
        "kref://?r=" + "1" * 5000,
        "kref://p/s/x.k?r=" + "1" * 5000 + "&a=mesh",
        "kref://p/s/x.k?t=" + "t" * 5000,
        "kref://" + "a/" * 5000 + "x.k",
        "kref://p/s/\ud800.k",
        "kref://p/s/x.k?r=1&a=\udfff",
        "\x00",
        "kref://p/s/x.k?" + "&" * 3000,
        "kref://" + "　" * 100,
    ],
)
def test_parse_kref_never_raises(uri):
    parts = parse_kref(uri)

    assert isinstance(parts.valid, bool)
    assert parts.uri == uri
    # Every part of the reading is reachable without raising, too.
    for name in (
        "error_class", "base", "shapes", "project", "space_path", "item_name",
        "kind", "is_project_root_item", "revision", "tag", "artifact",
    ):
        getattr(parts, name)


def test_the_kernel_reading_is_lazy(monkeypatch):
    def refuse(_uri):
        raise AssertionError("the kernel reading was computed")

    monkeypatch.setattr(kref_module, "_read", refuse)

    parts = parse_kref("kref://p/a/b/my.file.k?r=2")

    # The request tuple comes from the textual split alone.
    assert parts.get_item_tuple() == ("/p/a/b", "my.file", "k")
    assert parts.get_item_request() == ("/p/a/b", "my.file", "k")


def test_the_kernel_reading_is_computed_once(monkeypatch):
    calls = []
    real = kref_module._read

    def counting(uri):
        calls.append(uri)
        return real(uri)

    monkeypatch.setattr(kref_module, "_read", counting)

    parts = parse_kref("kref://p/s/x.k?r=2")
    assert parts.revision == 2 and parts.kind == "k" and parts.valid

    assert len(calls) == 1


@pytest.mark.parametrize(
    "call",
    [
        lambda c, k: c.get_item_by_kref(k),
        lambda c, k: c.get_bundle_by_kref(k),
        lambda c, k: kumiho.get_item(k),
        lambda c, k: kumiho.get_bundle(k),
    ],
    ids=["get_item_by_kref", "get_bundle_by_kref", "kumiho.get_item", "kumiho.get_bundle"],
)
def test_a_huge_revision_still_looks_the_item_up(mock_client, call):
    client, mock_stub = mock_client
    mock_stub.GetItem.return_value = _item_response(
        "kref://p/s/x.bundle", "x", "bundle"
    )
    uri = "kref://p/s/x.bundle?r=" + "1" * 4301

    call(client, uri)

    assert _sent_requests(mock_stub)[0] == ("/p/s", "x", "bundle")


def test_a_huge_revision_still_looks_the_item_up_from_a_revision(mock_client):
    client, mock_stub = mock_client
    item_kref = "kref://p/s/x.k"
    mock_stub.GetRevision.return_value = _revision_for(item_kref)
    mock_stub.GetItem.return_value = _item_response(item_kref, "x", "k")

    client.get_item_from_revision(item_kref + "?r=" + "1" * 4301)

    assert _sent_requests(mock_stub) == [("/p/s", "x", "k")]


# --------------------------------------------------------------------------
# The request reaches the node a7f155e's request reached.
# --------------------------------------------------------------------------

# Server-returned item krefs are not validated, so they can end a space segment
# in whitespace or hold an empty segment. For these, normalize_space_path would
# turn the new parent into a different space.
ALTERED_PARENTS = [
    pytest.param("kref://p/s /x.k", id="trailing-space"),
    pytest.param("kref://p/s\t/x.k", id="trailing-tab"),
    pytest.param("kref://p/s /x.k", id="trailing-nbsp"),
    pytest.param("kref://p/s　/x.k", id="trailing-ideographic-space"),
    pytest.param("kref://p/s /x.k", id="trailing-em-space"),
    pytest.param("kref://p/a/b /x.k", id="trailing-space-nested"),
    pytest.param("kref://p//x.k", id="empty-trailing-segment"),
    pytest.param("kref://p/s//x.k", id="empty-trailing-segment-nested"),
    pytest.param("kref://p /s/x.k", id="project-ends-in-space"),
    pytest.param("kref:// /s/x.k", id="project-is-a-space"),
]

# Parents the server leaves alone (or alters in a way that reaches the same
# node as a7f155e's request): the corpus split is sent unchanged.
UNALTERED_PARENTS = [
    pytest.param("kref://p/s/x.k", "/p/s", "x", "k", id="space"),
    pytest.param("kref://p/a/b/c/x.k", "/p/a/b/c", "x", "k", id="deep"),
    pytest.param("kref://p/x.k", "/p", "x", "k", id="root"),
    pytest.param("kref://p/ s/x.k", "/p/ s", "x", "k", id="leading-space-in-segment"),
    pytest.param("kref://p/a//b/x.k", "/p/a//b", "x", "k", id="empty-middle-segment"),
    pytest.param("kref://p/s/my.file.k", "/p/s", "my.file", "k", id="dotted-name"),
    pytest.param("kref://p/s/x.k?r=3", "/p/s", "x", "k", id="revision"),
    pytest.param("kref:///s/x.k", "//s", "x", "k", id="legacy-leading-slash"),
    pytest.param("kref:///s/t/x.k", "//s/t", "x", "k", id="legacy-nested"),
    pytest.param("kref:///x.k", "/", "x", "k", id="legacy-root"),
]


@pytest.mark.parametrize("uri", ALTERED_PARENTS)
def test_get_item_from_revision_keeps_a7f155e_shape_where_the_parent_would_change(
    mock_client, uri
):
    client, mock_stub = mock_client
    mock_stub.GetRevision.return_value = _revision_for(uri)
    mock_stub.GetItem.return_value = _item_response(uri, "x", "k")

    client.get_item_from_revision(uri + "?r=1")

    (sent,) = _sent_requests(mock_stub)
    assert sent == a7f155e_request(uri)
    assert server_key(sent) == server_key(a7f155e_request(uri))


def test_the_fallback_shape_is_project_then_text_up_to_the_last_dot():
    assert parse_kref("kref://p/s /x.k").get_item_request() == ("/p", "s /x", "k")
    assert parse_kref("kref://p//x.k").get_item_request() == ("/p", "/x", "k")
    # A dotted name keeps its dots: kinds never contain one.
    assert parse_kref("kref://p/s /my.file.k").get_item_request() == (
        "/p",
        "s /my.file",
        "k",
    )
    assert parse_kref("kref://p/a/b /x.k?r=2").get_item_request() == (
        "/p",
        "a/b /x",
        "k",
    )


@pytest.mark.parametrize("uri", ALTERED_PARENTS)
def test_get_item_request_resolves_where_a7f155e_resolved(uri):
    request = parse_kref(uri).get_item_request()

    assert server_key(request) == server_key(a7f155e_request(uri))


@pytest.mark.parametrize("uri,parent,name,kind", UNALTERED_PARENTS)
def test_unaltered_parents_use_the_corpus_split(uri, parent, name, kind):
    parts = parse_kref(uri)

    assert parts.get_item_tuple() == (parent, name, kind)
    assert parts.get_item_request() == (parent, name, kind)
    assert server_key(parts.get_item_request()) == server_key(a7f155e_request(uri))


@pytest.mark.parametrize("uri", [u.values[0] for u in ALTERED_PARENTS])
def test_the_corpus_tuple_stays_the_pure_grammar_split(uri):
    # get_item_tuple is the corpus field; only get_item_request guards.
    parts = parse_kref(uri)
    parent, name, kind = parts.get_item_tuple()

    assert parent == "/" + parts.parent
    assert (name, kind) == (parts.leaf_name, parts.leaf_kind)


@pytest.mark.parametrize(
    "uri", ["kref://p/s /x", "kref://p/s/x.k/", "kref://p", "kref://p//x"]
)
def test_the_guard_does_not_swallow_the_malformed_kref_errors(uri):
    with pytest.raises(ValueError):
        parse_kref(uri).get_item_request()


@pytest.mark.parametrize(
    "call",
    [
        lambda c, k: c.get_item_from_revision(k + "?r=1"),
    ],
    ids=["get_item_from_revision"],
)
@pytest.mark.parametrize("uri", ["kref://p/s/x.k", "kref://p/a/b/x.k", "kref://p/x.k"])
def test_ordinary_item_krefs_still_send_the_split_request(mock_client, call, uri):
    client, mock_stub = mock_client
    mock_stub.GetRevision.return_value = _revision_for(uri)
    mock_stub.GetItem.return_value = _item_response(uri, "x", "k")

    call(client, uri)

    (sent,) = _sent_requests(mock_stub)
    assert sent == parse_kref(uri).get_item_tuple()


def test_bundles_in_validated_krefs_still_fetch_the_bundle_they_name(mock_client):
    client, mock_stub = mock_client
    uri = "kref://p/a/b/set.v2.bundle"
    mock_stub.GetItem.return_value = _item_response(uri, "set.v2", "bundle")

    client.get_bundle_by_kref(uri)

    assert _sent_requests(mock_stub) == [("/p/a/b", "set.v2", "bundle")] * 2


# --------------------------------------------------------------------------
# A kind that contains '/' is refused before sending.
# --------------------------------------------------------------------------


@pytest.fixture
def project(mock_client):
    client, mock_stub = mock_client
    mock_stub.GetProjects.return_value = mock_helpers.mock_get_projects_response(
        [mock_helpers.mock_project_response(project_id="p1", name="proj")]
    )
    return kumiho.get_project("proj"), mock_stub


@pytest.mark.parametrize("kind", ["image/png", "a/b", "k/"])
def test_project_get_item_refuses_a_kind_containing_a_slash(project, kind):
    proj, mock_stub = project

    with pytest.raises(ValueError):
        proj.get_item("x", kind)

    mock_stub.GetItem.assert_not_called()


def test_project_get_item_still_takes_an_ordinary_kind(project):
    proj, mock_stub = project
    mock_stub.GetItem.return_value = _item_response("kref://proj/x.model", "x", "model")

    proj.get_item("x", "model")

    assert _sent_requests(mock_stub) == [("/proj", "x", "model")]


def test_kref_accessors_never_raise_on_a_huge_revision_in_other_places():
    # get_item_name/get_kind read the textual split only.
    kref = Kref(HUGE_REVISION)
    assert kref.get_item_name() == "x.k"
    assert kref.get_kind() == "k"


# kumiho-server trims with Rust `str::trim`, i.e. the Unicode White_Space
# property. Pin the whole table so a later edit cannot drop one silently.
RUST_WHITE_SPACE = (
    [0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x20, 0x85, 0xA0, 0x1680]
    + list(range(0x2000, 0x200B))
    + [0x2028, 0x2029, 0x202F, 0x205F, 0x3000]
)


def test_the_server_whitespace_table_is_rusts_white_space():
    assert len(RUST_WHITE_SPACE) == 25
    assert set(kref_module._SERVER_WHITESPACE) == {chr(c) for c in RUST_WHITE_SPACE}


@pytest.mark.parametrize("code", RUST_WHITE_SPACE, ids=lambda c: f"U+{c:04X}")
def test_every_server_whitespace_keeps_the_a7f155e_node(code):
    uri = f"kref://p/s{chr(code)}/x.k"
    request = parse_kref(uri).get_item_request()
    assert server_key(request) == server_key(a7f155e_request(uri))
