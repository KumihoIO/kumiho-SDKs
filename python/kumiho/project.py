"""Project module for Kumiho asset management.

This module provides the :class:`Project` class, which represents the top-level
container for organizing assets in Kumiho. Projects serve as namespaces that
contain groups, products, versions, and resources.

Example:
    Creating and working with projects::

        import kumiho

        # Create a new project
        project = kumiho.create_project("film-2024", "Feature film VFX assets")

        # Create group structure
        chars = project.create_group("characters")
        envs = project.create_group("environments")

        # Create products within groups
        hero = chars.create_product("hero", "model")

        # List all groups
        for group in project.get_groups(recursive=True):
            print(group.path)
"""

from typing import TYPE_CHECKING, List, Optional

from .base import KumihoObject
from .group import Group
from .proto.kumiho_pb2 import ProjectResponse

if TYPE_CHECKING:
    from .client import _Client


class Project(KumihoObject):
    """A Kumiho project—the top-level container for assets.

    Projects are the root of the Kumiho hierarchy. Each project has its own
    namespace for groups and products, and manages access control and settings
    independently.

    Projects support both public and private access modes, allowing you to
    share assets publicly or restrict them to authenticated users.

    Attributes:
        project_id (str): The unique identifier for this project.
        name (str): The URL-safe name of the project (e.g., "film-2024").
        description (str): Human-readable description of the project.
        created_at (Optional[str]): ISO timestamp when the project was created.
        updated_at (Optional[str]): ISO timestamp of the last update.
        deprecated (bool): Whether the project is deprecated (soft-deleted).
        allow_public (bool): Whether anonymous read access is enabled.

    Example:
        Basic project operations::

            import kumiho

            # Get existing project
            project = kumiho.get_project("my-project")

            # Create groups
            assets = project.create_group("assets")
            shots = project.create_group("shots")

            # Navigate to nested groups
            char_group = project.get_group("assets/characters")

            # List all groups recursively
            for group in project.get_groups(recursive=True):
                print(f"  {group.path}")

            # Update project settings
            project.set_public(True)  # Enable public access
            project.update(description="Updated description")

            # Soft delete (deprecate)
            project.delete()

            # Hard delete (permanent)
            project.delete(force=True)
    """

    def __init__(self, pb: ProjectResponse, client: "_Client") -> None:
        """Initialize a Project from a protobuf response.

        Args:
            pb: The protobuf ProjectResponse message.
            client: The client instance for making API calls.
        """
        super().__init__(client)
        self.project_id = pb.project_id
        self.name = pb.name
        self.description = pb.description
        self.created_at = pb.created_at or None
        self.updated_at = pb.updated_at or None
        self.deprecated = pb.deprecated
        self.allow_public = pb.allow_public

    def __repr__(self) -> str:
        """Return a string representation of the Project."""
        return f"<kumiho.Project id='{self.project_id}' name='{self.name}'>"

    def create_group(self, name: str, parent_path: Optional[str] = None) -> Group:
        """Create a group within this project.

        Args:
            name: The name of the group to create.
            parent_path: Optional parent path. If not provided, creates
                the group at the project root (e.g., "/project-name").

        Returns:
            Group: The newly created Group object.

        Example:
            >>> project = kumiho.get_project("film-2024")
            >>> # Create at root
            >>> chars = project.create_group("characters")
            >>> # Create nested group
            >>> heroes = project.create_group("heroes", parent_path="/film-2024/characters")
        """
        base_parent = parent_path or f"/{self.name}"
        return self._client.create_group(parent_path=base_parent, group_name=name)

    def delete(self, force: bool = False):
        """Delete or deprecate this project.

        Args:
            force: If True, permanently delete the project and all its
                contents. If False (default), mark as deprecated.

        Returns:
            StatusResponse: Response indicating success or failure.

        Warning:
            Force deletion is irreversible and removes all groups, products,
            versions, resources, and links within the project.

        Example:
            >>> project = kumiho.get_project("old-project")
            >>> # Soft delete (can be recovered)
            >>> project.delete()
            >>> # Hard delete (permanent)
            >>> project.delete(force=True)
        """
        return self._client.delete_project(project_id=self.project_id, force=force)

    def set_public(self, public: bool):
        """Set whether this project allows anonymous read access.

        Args:
            public: True to enable public access, False to require
                authentication for all access.

        Returns:
            Project: The updated Project object.

        Example:
            >>> project.set_public(True)  # Enable public access
            >>> project.set_public(False)  # Require authentication
        """
        return self._client.update_project(project_id=self.project_id, allow_public=public)

    def update(
        self,
        description: Optional[str] = None,
        allow_public: Optional[bool] = None
    ):
        """Update project properties.

        Args:
            description: New description for the project.
            allow_public: New public access setting.

        Returns:
            Project: The updated Project object.

        Example:
            >>> project.update(
            ...     description="Updated project description",
            ...     allow_public=True
            ... )
        """
        return self._client.update_project(
            project_id=self.project_id,
            description=description,
            allow_public=allow_public
        )

    def get_group(self, name: str, parent_path: Optional[str] = None) -> Group:
        """Get an existing group within this project.

        Args:
            name: The name of the group, or an absolute path starting with "/".
            parent_path: Optional parent path if name is a relative name.

        Returns:
            Group: The Group object.

        Raises:
            grpc.RpcError: If the group is not found.

        Example:
            >>> # Get by absolute path
            >>> group = project.get_group("/film-2024/characters")

            >>> # Get by relative name (from project root)
            >>> group = project.get_group("characters")

            >>> # Get nested group with parent path
            >>> heroes = project.get_group("heroes", parent_path="/film-2024/characters")
        """
        if name.startswith("/"):
            path = name
        else:
            base_parent = parent_path or f"/{self.name}"
            path = f"{base_parent.rstrip('/')}/{name}"
        return self._client.get_group(path)

    def get_groups(
        self,
        parent_path: Optional[str] = None,
        recursive: bool = False
    ) -> List[Group]:
        """List groups within this project.

        Args:
            parent_path: Optional path to start from. Defaults to project root.
            recursive: If True, include all nested groups. If False (default),
                only direct children.

        Returns:
            List[Group]: A list of Group objects.

        Example:
            >>> # List direct children only
            >>> groups = project.get_groups()
            >>> for g in groups:
            ...     print(g.name)

            >>> # List all groups recursively
            >>> all_groups = project.get_groups(recursive=True)
            >>> for g in all_groups:
            ...     print(g.path)
        """
        base_parent = parent_path or f"/{self.name}"
        return self._client.get_child_groups(base_parent, recursive=recursive)
