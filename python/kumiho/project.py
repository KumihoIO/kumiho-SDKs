"""Project-related helper object."""

from typing import Optional

from .base import KumihoObject
from .group import Group
from .proto.kumiho_pb2 import ProjectResponse


class Project(KumihoObject):
    """A high-level wrapper around ProjectResponse with helpers for nested actions."""

    def __init__(self, pb: ProjectResponse, client: "Client") -> None:  # type: ignore[name-defined]
        super().__init__(client)
        self.project_id = pb.project_id
        self.name = pb.name
        self.description = pb.description
        self.created_at = pb.created_at or None
        self.updated_at = pb.updated_at or None
        self.deprecated = pb.deprecated
        self.allow_public = pb.allow_public

    def __repr__(self) -> str:
        return f"<kumiho.Project id='{self.project_id}' name='{self.name}'>"

    def create_group(self, name: str, parent_path: Optional[str] = None) -> Group:
        """Create a group within this project (defaults to project root path)."""
        base_parent = parent_path or f"/{self.name}"
        return self._client.create_group(parent_path=base_parent, group_name=name)

    def delete(self, force: bool = False):
        """Delete or deprecate this project."""
        return self._client.delete_project(project_id=self.project_id, force=force)

    def set_public(self, public: bool):
        """Set whether this project is publicly accessible (anonymous read)."""
        return self._client.update_project(project_id=self.project_id, allow_public=public)

    def update(self, description: Optional[str] = None, allow_public: Optional[bool] = None):
        """Update project properties."""
        return self._client.update_project(
            project_id=self.project_id,
            description=description,
            allow_public=allow_public
        )

    def get_group(self, name: str, parent_path: Optional[str] = None) -> Group:
        """Fetch an existing group within this project."""
        base_parent = parent_path or f"/{self.name}"
        path = f"{base_parent.rstrip('/')}/{name}"
        return self._client.get_group(path)

    def get_groups(self, parent_path: Optional[str] = None, recursive: bool = False):
        """List child groups under a given parent (defaults to project root)."""
        base_parent = parent_path or f"/{self.name}"
        return self._client.get_child_groups(base_parent, recursive=recursive)
