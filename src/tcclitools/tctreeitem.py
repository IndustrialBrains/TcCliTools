"""A TwinCAT tree item"""

from __future__ import annotations

from typing import Any, Iterable

from anytree import NodeMixin


class TcTreeItem(
    NodeMixin  # type:ignore
):  # pylint:disable=too-few-public-methods
    """A TwinCAT tree item"""

    def __init__(
        self, parent: TcTreeItem | None = None, children: Iterable[Any] | None = None
    ):
        self.parent = parent
        if children:
            self.children = children
