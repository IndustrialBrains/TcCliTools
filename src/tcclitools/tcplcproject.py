"""A TwinCAT PLC Project"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from defusedxml import ElementTree
from packaging.version import InvalidVersion, parse

from .tclibraryreference import TcLibraryReference
from .tctreeitem import TcTreeItem
from .uniquepath import UniquePath


class TcPlcProject(UniquePath, TcTreeItem):  # pylint:disable=too-few-public-methods
    """A TwinCAT PLC Project"""

    def __init__(
        self, path: Path, parent: Any = None, children: Iterable[Any] | None = None
    ):
        self._allowed_types = [".plcproj"]
        UniquePath.__init__(self, path)
        TcTreeItem.__init__(self, parent=parent, children=children)
        self.xmlroot = ElementTree.parse(path).getroot()
        self._library_references: set[TcLibraryReference] | None = None

    @property
    def library_references(self) -> Iterable[TcLibraryReference]:
        """Libraries referenced by the PLC project"""
        if self._library_references is None:
            self._library_references = {
                TcLibraryReference.from_string(
                    placeholder.find("{*}DefaultResolution").text
                )
                for placeholder in self.xmlroot.findall(".//{*}PlaceholderReference")
            }
        return iter(self._library_references)

    def as_reference(self) -> TcLibraryReference | None:
        """Return a TcLibraryReference object if the PLC project
        can be installed as a library, else return None"""
        try:
            (title, version, company) = [
                self.xmlroot.find("./{*}PropertyGroup/{*}" + find_str).text
                for find_str in ["Title", "ProjectVersion", "Company"]
            ]
            version = parse(version)
        except (AttributeError, InvalidVersion):
            return None

        return TcLibraryReference(
            title=title,
            version=version,
            company=company,
        )
