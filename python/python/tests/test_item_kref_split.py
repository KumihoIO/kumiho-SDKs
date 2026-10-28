"""Item krefs are split at the LAST '/' and the LAST '.'.

A kref path is ``project[/space...]/name.kind``. Everything before the last
``/`` (project plus any nested spaces) is the parent path, and the leaf after
it is ``<item name>.<kind>``. Item names may contain dots, kinds never do, so
the leaf is split at its last ``.``.

Splitting at the first ``/`` sent ``characters/hero`` as the item name for an
item in a nested space (a name the server rightly refuses, since item names
never contain ``/``), and splitting at the first ``.`` turned ``a.b.c`` into
name ``a`` and kind ``b.c``.
"""

import pytest
from unittest.mock import MagicMock

import kumiho
import mock_helpers
from kumiho.kref import Kref


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


def _item_response(kref_uri: str, item_name: str, kind: str):
    return mock_helpers.mock_item_response(
        kref_uri=kref_uri,
        name=f"{item_name}.{kind}",
        item_name=item_name,
        kind=kind,
    )


# (kref, parent_path, item_name, kind)
SPLIT_CASES = [
    pytest.param(
        "kref://projectA/modelA.asset",
        "/projectA",
        "modelA",
        "asset",
        id="root-level",
    ),
    pytest.param(
        "kref://proj/characters/hero.model",
        "/proj/characters",
        "hero",
        "model",
        id="nested-space",
    ),
    pytest.param(
        "kref://proj/a/b/c/hero.model",
        "/proj/a/b/c",
        "hero",
        "model",
        id="deeply-nested-space",
    ),
    pytest.param(
        "kref://proj/rootitem.v2.model",
        "/proj",
        "rootitem.v2",
        "model",
        id="dotted-name-at-root",
    ),
    pytest.param(
        "kref://proj/characters/a.b.c.model",
        "/proj/characters",
        "a.b.c",
        "model",
        id="nested-and-dotted",
    ),
    pytest.param(
        "kref://proj/characters/hero.model?r=3",
        "/proj/characters",
        "hero",
        "model",
        id="revision-suffix-ignored",
    ),
]


@pytest.mark.parametrize("kref,parent_path,item_name,kind", SPLIT_CASES)
def test_get_item_by_kref_splits_at_last_slash_and_last_dot(
    mock_client, kref, parent_path, item_name, kind
):
    client, mock_stub = mock_client
    mock_stub.GetItem.return_value = _item_response(
        kref.split("?", 1)[0], item_name, kind
    )

    item = client.get_item_by_kref(kref)

    mock_stub.GetItem.assert_called_once_with(
        mock_helpers.mock_get_item_request(
            parent_path=parent_path, item_name=item_name, kind=kind
        )
    )
    assert item.item_name == item_name
    assert item.kind == kind


@pytest.mark.parametrize("kref,parent_path,item_name,kind", SPLIT_CASES)
def test_get_item_from_revision_splits_at_last_slash_and_last_dot(
    mock_client, kref, parent_path, item_name, kind
):
    client, mock_stub = mock_client
    item_kref = kref.split("?", 1)[0]
    mock_stub.GetRevision.return_value = mock_helpers.mock_revision_response(
        kref_uri=f"{item_kref}?r=1",
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
    mock_stub.GetItem.return_value = _item_response(item_kref, item_name, kind)

    item = client.get_item_from_revision(f"{item_kref}?r=1")

    mock_stub.GetItem.assert_called_once_with(
        mock_helpers.mock_get_item_request(
            parent_path=parent_path, item_name=item_name, kind=kind
        )
    )
    assert item.item_name == item_name


@pytest.mark.parametrize(
    "kref,parent_path,bundle_name",
    [
        pytest.param(
            "kref://proj/mybundle.bundle", "/proj", "mybundle", id="root-level"
        ),
        pytest.param(
            "kref://proj/sets/mybundle.bundle", "/proj/sets", "mybundle", id="nested"
        ),
        pytest.param(
            "kref://proj/sets/my.bundle.v2.bundle",
            "/proj/sets",
            "my.bundle.v2",
            id="nested-and-dotted",
        ),
    ],
)
def test_get_bundle_by_kref_splits_at_last_slash_and_last_dot(
    mock_client, kref, parent_path, bundle_name
):
    client, mock_stub = mock_client
    mock_stub.GetItem.return_value = _item_response(kref, bundle_name, "bundle")

    bundle = client.get_bundle_by_kref(kref)

    expected = mock_helpers.mock_get_item_request(
        parent_path=parent_path, item_name=bundle_name, kind="bundle"
    )
    # One GetItem to verify the kind, one to re-fetch the Bundle wrapper.
    assert mock_stub.GetItem.call_count == 2
    for call in mock_stub.GetItem.call_args_list:
        assert call.args == (expected,)
    assert bundle.item_name == bundle_name


def test_project_get_item_in_nested_space_with_dotted_name(mock_client):
    client, mock_stub = mock_client
    mock_stub.GetProjects.return_value = mock_helpers.mock_get_projects_response(
        [mock_helpers.mock_project_response(project_id="p1", name="proj")]
    )
    mock_stub.GetItem.return_value = _item_response(
        "kref://proj/characters/a.b.model", "a.b", "model"
    )

    project = kumiho.get_project("proj")
    item = project.get_item("a.b", "model", parent_path="/proj/characters")

    mock_stub.GetItem.assert_called_once_with(
        mock_helpers.mock_get_item_request(
            parent_path="/proj/characters", item_name="a.b", kind="model"
        )
    )
    assert item.kind == "model"


def test_kref_get_kind_is_the_text_after_the_last_dot() -> None:
    assert Kref("kref://proj/characters/hero.model").get_kind() == "model"
    assert Kref("kref://proj/characters/a.b.c.model").get_kind() == "model"
    assert Kref("kref://proj/characters/a.b.c.model").get_item_name() == "a.b.c.model"
    assert Kref("kref://proj/characters/noext").get_kind() == ""


@pytest.mark.parametrize(
    "call",
    [
        lambda c, k: c.get_item_by_kref(k),
        lambda c, k: c.get_bundle_by_kref(k),
    ],
    ids=["get_item_by_kref", "get_bundle_by_kref"],
)
def test_malformed_item_kref_messages_are_unchanged(mock_client, call):
    client, mock_stub = mock_client

    with pytest.raises(ValueError, match=r"Invalid item kref format: kref://proj"):
        call(client, "kref://proj")
    with pytest.raises(ValueError, match=r"Invalid item name\.kind format: noext"):
        call(client, "kref://proj/noext")
    with pytest.raises(ValueError, match=r"Invalid item name\.kind format: "):
        call(client, "kref://proj/space/noext")

    mock_stub.GetItem.assert_not_called()
