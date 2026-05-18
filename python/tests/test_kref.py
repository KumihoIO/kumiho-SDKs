import pytest

from kumiho.artifact import Artifact
from kumiho.edge import Edge
from kumiho.event import Event
from kumiho.item import Item
from kumiho.kref import Kref, KrefValidationError, is_valid_kref, validate_kref
from kumiho.proto import kumiho_pb2
from kumiho.revision import Revision


def test_hangul_kref_is_valid() -> None:
    uri = "kref://CognitiveMemory/Skills/mg-char-이지수.skill"

    assert is_valid_kref(uri)
    validate_kref(uri)

    kref = Kref(uri)
    assert kref.get_item_name() == "mg-char-이지수.skill"
    assert kref.get_kind() == "skill"


def test_hangul_path_segments_are_valid() -> None:
    uri = "kref://프로젝트/스킬/이지수.skill?r=3"

    assert is_valid_kref(uri)
    assert Kref(uri).get_project() == "프로젝트"


def test_kref_still_rejects_unsafe_characters() -> None:
    unsafe_uris = [
        "kref://project/../item.skill",
        "kref://project/space bad/item.skill",
        "kref://project/space$/item.skill",
        "kref://project/space\x00/item.skill",
    ]

    for uri in unsafe_uris:
        with pytest.raises(KrefValidationError):
            validate_kref(uri)


def test_item_accepts_trusted_server_returned_unicode_kref() -> None:
    uri = "kref://CognitiveMemory/Skills/mg-char-이지수.skill"
    pb_item = kumiho_pb2.ItemResponse(
        kref=kumiho_pb2.Kref(uri=uri),
        name="mg-char-이지수.skill",
        item_name="mg-char-이지수",
        kind="skill",
    )

    item = Item(pb_item, client=None)

    assert item.kref.uri == uri
    assert item.item_name == "mg-char-이지수"


def test_related_objects_accept_trusted_server_returned_unicode_krefs() -> None:
    item_uri = "kref://CognitiveMemory/Skills/mg-char-이지수.skill"
    revision_uri = f"{item_uri}?r=1"
    artifact_uri = f"{revision_uri}&a=main"

    revision = Revision(
        kumiho_pb2.RevisionResponse(
            kref=kumiho_pb2.Kref(uri=revision_uri),
            item_kref=kumiho_pb2.Kref(uri=item_uri),
            number=1,
        ),
        client=None,
    )
    artifact = Artifact(
        kumiho_pb2.ArtifactResponse(
            kref=kumiho_pb2.Kref(uri=artifact_uri),
            revision_kref=kumiho_pb2.Kref(uri=revision_uri),
            item_kref=kumiho_pb2.Kref(uri=item_uri),
            name="main",
        ),
        client=None,
    )
    edge = Edge(
        kumiho_pb2.Edge(
            source_kref=kumiho_pb2.Kref(uri=revision_uri),
            target_kref=kumiho_pb2.Kref(uri=revision_uri),
            edge_type="DEPENDS_ON",
        ),
        client=None,
    )
    event = Event(
        kumiho_pb2.Event(
            routing_key="item.updated",
            kref=kumiho_pb2.Kref(uri=item_uri),
        )
    )

    assert revision.kref.uri == revision_uri
    assert revision.item_kref.uri == item_uri
    assert artifact.kref.uri == artifact_uri
    assert artifact.revision_kref.uri == revision_uri
    assert artifact.item_kref.uri == item_uri
    assert edge.source_kref.uri == revision_uri
    assert edge.target_kref.uri == revision_uri
    assert event.kref.uri == item_uri
