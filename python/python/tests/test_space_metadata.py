from unittest.mock import MagicMock

from kumiho.client import _Client
from kumiho.project import Project
from kumiho.proto import kumiho_pb2


def test_project_create_space_sends_initial_metadata() -> None:
    client = MagicMock(spec=_Client)
    client.create_space.return_value = object()
    project = Project(
        kumiho_pb2.ProjectResponse(project_id="p1", name="film"), client
    )

    created = project.create_space(
        "assets", metadata={"display_label": "Production Assets"}
    )

    assert created is client.create_space.return_value
    client.create_space.assert_called_once_with(
        parent_path="/film",
        space_name="assets",
        metadata={"display_label": "Production Assets"},
    )


def test_client_create_space_encodes_metadata() -> None:
    client = object.__new__(_Client)
    client.stub = MagicMock()
    client.stub.CreateSpace.return_value = kumiho_pb2.SpaceResponse(
        path="/film/assets",
        name="assets",
        metadata={"display_label": "Production Assets"},
    )

    space = client.create_space(
        "/film", "assets", metadata={"display_label": "Production Assets"}
    )

    request = client.stub.CreateSpace.call_args.args[0]
    assert dict(request.metadata) == {"display_label": "Production Assets"}
    assert space.metadata == {"display_label": "Production Assets"}
