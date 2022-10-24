"""A TwinCAT tree item"""

from __future__ import annotations


class TcTreeItem:  # pylint:disable=too-few-public-methods
    """A TwinCAT tree item"""

    def __init__(self, parent: TcTreeItem | None = None):
        self.parent = parent
