"""Base classes and utilities for Kumiho objects."""

import getpass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client


class KumihoObject:
    """Base class for high-level Kumiho objects.

    This class provides common functionality for all Kumiho domain objects,
    including access to the client and user identification.
    """

    def __init__(self, client: 'Client') -> None:
        """Initialize the Kumiho object with a client reference.

        Args:
            client: The client instance for making API calls.
        """
        self._client = client

    def _get_current_user(self) -> str:
        """Get the current username.

        Returns:
            The username of the current user.
        """
        return getpass.getuser()