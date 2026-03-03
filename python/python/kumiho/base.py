"""Base classes and utilities for Kumiho objects.

This module provides the base classes used by all Kumiho domain objects,
including :class:`KumihoObject` (the base for all high-level objects) and
:class:`KumihoError` (the base exception class).
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar, List, Optional

if TYPE_CHECKING:
    from .client import _Client
    from .item import Item

T = TypeVar('T')


class PagedList(List[T]):
    """A list that also contains pagination information.

    Attributes:
        next_cursor (Optional[str]): The cursor for the next page of results.
        total_count (Optional[int]): The total number of items available.
    """
    def __init__(self, items: List[T], next_cursor: Optional[str] = None, total_count: Optional[int] = None):
        super().__init__(items)
        self.next_cursor = next_cursor
        self.total_count = total_count


@dataclass
class SearchResult:
    """A single search result with relevance score.

    Attributes:
        item: The matched Item object.
        score: Relevance score from 0.0 to 1.0+ (higher is better match).
        matched_in: Where the match was found ("item", "revision", "artifact").

    Example:
        >>> results = client.search("hero model")
        >>> for result in results:
        ...     print(f"{result.item.name}: {result.score:.2f}")
        ...     print(f"  Matched in: {', '.join(result.matched_in)}")
    """
    item: "Item"
    score: float
    matched_in: List[str]

    def __repr__(self) -> str:
        return f"SearchResult(item={self.item.name!r}, score={self.score:.3f}, matched_in={self.matched_in})"


class KumihoError(Exception):
    """Base exception class for all Kumiho errors.

    All custom exceptions raised by the Kumiho SDK inherit from this class,
    making it easy to catch all Kumiho-related errors.

    Example::

        import kumiho

        try:
            project = kumiho.get_project("nonexistent")
        except kumiho.KumihoError as e:
            print(f"Kumiho error: {e}")
    """


class KumihoObject:
    """Base class for all high-level Kumiho domain objects.

    This abstract base class provides common functionality shared by all
    Kumiho objects, including access to the client for making API calls.

    All domain objects (:class:`Project`, :class:`Space`, :class:`Item`,
    :class:`Revision`, :class:`Artifact`, :class:`Edge`) inherit from this class.

    Attributes:
        _client: The client instance for making API calls (internal).

    Note:
        This is an internal base class. Users typically interact with
        concrete subclasses like :class:`Project` or :class:`Version`.
    """

    def __init__(self, client: '_Client') -> None:
        """Initialize the Kumiho object with a client reference.

        Args:
            client: The client instance for making API calls.
        """
        self._client = client

