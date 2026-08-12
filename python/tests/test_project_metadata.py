from __future__ import annotations

from unittest.mock import MagicMock

import kumiho
import pytest

import mock_helpers
from kumiho.proto import kumiho_pb2


@pytest.fixture
def mock_client(monkeypatch):
    original_client = kumiho._default_client
    stub = MagicMock()
    monkeypatch.setattr(
        "kumiho.client.kumiho_pb2_grpc.KumihoServiceStub",
        lambda channel: stub,
    )
    client = kumiho.connect(endpoint="localhost:50051", token="mock-token")
    kumiho.configure_default_client(client)
    try:
        yield client, stub
    finally:
        kumiho._default_client = original_client


def test_project_metadata_survives_protobuf_round_trip() -> None:
    original = mock_helpers.mock_project_response(
        name="film-one",
        description="Feature film",
        metadata={"display_label": "Film One", "department": "VFX"},
    )

    restored = kumiho_pb2.ProjectResponse.FromString(original.SerializeToString())

    assert dict(restored.metadata) == {
        "display_label": "Film One",
        "department": "VFX",
    }
    assert restored.name == "film-one"
    assert restored.description == "Feature film"


def test_project_metadata_round_trips_through_create_read_and_update(
    mock_client,
) -> None:
    client, stub = mock_client
    created_pb = mock_helpers.mock_project_response(
        project_id="project-1",
        name="film-one",
        description="Feature film",
        metadata={"display_label": "Film One"},
    )
    stub.CreateProject.return_value = created_pb

    created = kumiho.create_project(
        "film-one",
        "Feature film",
        metadata={"display_label": "Film One"},
    )

    create_request = stub.CreateProject.call_args.args[0]
    assert dict(create_request.metadata) == {"display_label": "Film One"}
    assert created.metadata == {"display_label": "Film One"}

    stub.GetProjects.return_value = mock_helpers.mock_get_projects_response([created_pb])
    loaded = client.get_project("film-one")
    assert loaded is not None
    assert loaded.metadata == {"display_label": "Film One"}

    stub.UpdateProject.return_value = mock_helpers.mock_project_response(
        project_id="project-1",
        name="film-one",
        description="Feature film",
        metadata={"display_label": "Film One — Final", "department": "VFX"},
    )
    updated = loaded.set_metadata(
        {"display_label": "Film One — Final", "department": "VFX"}
    )

    update_request = stub.UpdateProject.call_args.args[0]
    assert dict(update_request.metadata) == {
        "display_label": "Film One — Final",
        "department": "VFX",
    }
    assert updated.name == "film-one"
    assert updated.description == "Feature film"
    assert updated.metadata["display_label"] == "Film One — Final"


def test_project_metadata_update_sends_only_the_requested_patch(mock_client) -> None:
    client, stub = mock_client
    stale_pb = mock_helpers.mock_project_response(
        project_id="project-1",
        name="film-one",
        metadata={"display_label": "Old label", "department": "VFX"},
    )
    stub.GetProjects.return_value = mock_helpers.mock_get_projects_response([stale_pb])
    project = client.get_project("film-one")
    assert project is not None
    stub.UpdateProject.return_value = mock_helpers.mock_project_response(
        project_id="project-1",
        name="film-one",
        metadata={"display_label": "New label", "department": "Animation"},
    )

    project.set_metadata({"display_label": "New label"})

    request = stub.UpdateProject.call_args.args[0]
    assert dict(request.metadata) == {"display_label": "New label"}


def test_project_metadata_rejects_non_string_values_before_rpc(mock_client) -> None:
    _client, stub = mock_client

    with pytest.raises(TypeError):
        kumiho.create_project("film", metadata={"display_label": 7})  # type: ignore[dict-item]

    stub.CreateProject.assert_not_called()


def test_project_archive_and_restore_use_explicit_update_field(mock_client) -> None:
    client, stub = mock_client
    stub.GetProjects.return_value = mock_helpers.mock_get_projects_response(
        [mock_helpers.mock_project_response(project_id="project-1", name="film-one")]
    )
    project = client.get_project("film-one")
    assert project is not None
    stub.UpdateProject.side_effect = [
        mock_helpers.mock_project_response(
            project_id="project-1", name="film-one", deprecated=True
        ),
        mock_helpers.mock_project_response(
            project_id="project-1", name="film-one", deprecated=False
        ),
    ]

    archived = project.deprecate()
    restored = project.restore()

    requests = [call.args[0] for call in stub.UpdateProject.call_args_list]
    assert requests[0].deprecated is True
    assert requests[1].deprecated is False
    assert archived.project_id == restored.project_id == "project-1"
    assert archived.name == restored.name == "film-one"


def test_get_projects_can_include_archive(mock_client) -> None:
    client, stub = mock_client
    stub.GetProjects.return_value = mock_helpers.mock_get_projects_response([])
    client.get_projects(include_deprecated=True)
    assert stub.GetProjects.call_args.args[0].include_deprecated is True


def test_revision_creation_forwards_tenant_scoped_idempotency_key(mock_client) -> None:
    client, stub = mock_client
    item_kref = kumiho.Kref("kref://film/assets/hero.flowrun")
    stub.CreateRevision.return_value = mock_helpers.mock_revision_response(
        "kref://film/assets/hero.flowrun?r=1",
        str(item_kref),
        metadata={"execution_id": "run-1", "request_hash": "sha256:abc"},
    )

    revision = client.create_revision(
        item_kref,
        {"execution_id": "run-1", "request_hash": "sha256:abc"},
        idempotency_key="9miho-execution-run-1",
    )

    assert revision.metadata["execution_id"] == "run-1"
    assert stub.CreateRevision.call_args.kwargs["metadata"] == (
        ("x-idempotency-key", "9miho-execution-run-1"),
    )


def test_project_hard_delete_requires_and_forwards_server_impact_snapshot(
    mock_client,
) -> None:
    client, stub = mock_client
    stub.GetProjects.return_value = mock_helpers.mock_get_projects_response(
        [
            mock_helpers.mock_project_response(
                project_id="project-1", name="film-one", deprecated=True
            )
        ]
    )
    project = client.get_project("film-one", include_deprecated=True)
    assert project is not None

    with pytest.raises(ValueError, match="impact snapshot"):
        client.delete_project("project-1", force=True)
    stub.DeleteProject.assert_not_called()

    stub.AnalyzeProjectDeletion.return_value = (
        kumiho_pb2.ProjectDeletionImpactResponse(
            impact_snapshot_id="019c0000-0000-7000-8000-000000000001",
            impact_snapshot_hash="sha256:" + "a" * 64,
            project_id="project-1",
            project_name="film-one",
            descendants=["kref://film-one/assets"],
            created_at="2026-08-11T00:00:00Z",
        )
    )
    stub.DeleteProject.return_value = kumiho_pb2.StatusResponse(
        success=True, message="Project permanently deleted"
    )

    impact = project.analyze_deletion()
    response = project.hard_delete(impact, confirmed=True)

    analyze_request = stub.AnalyzeProjectDeletion.call_args.args[0]
    delete_request = stub.DeleteProject.call_args.args[0]
    assert analyze_request.project_id == "project-1"
    assert delete_request.force is True
    assert delete_request.confirmed is True
    assert delete_request.impact_snapshot_id == impact.impact_snapshot_id
    assert delete_request.impact_snapshot_hash == impact.impact_snapshot_hash
    assert response.success is True
