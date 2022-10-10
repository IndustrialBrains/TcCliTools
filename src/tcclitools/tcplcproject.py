"""A TwinCAT PLC Project"""
from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree

from .tclibrary import TcLibraryReference
from .uniquepath import UniquePath


class TcPlcProject(UniquePath):
    """A TwinCAT PLC Project"""

    def __init__(self, path: Path):
        self._allowed_types = [".plcproj"]
        super().__init__(path)
        self.xmlroot = ElementTree.parse(path).getroot()
        self._library_references: set[TcLibraryReference] | None = None

    @property
    def library_references(self) -> set[TcLibraryReference]:
        """Libraries referenced by the PLC project"""
        if self._library_references is None:
            self._library_references = {
                TcLibraryReference.from_string(
                    placeholder.find("{*}DefaultResolution").text  # type:ignore
                )
                for placeholder in self.xmlroot.findall(".//{*}PlaceholderReference")
            }
        return self._library_references  # type:ignore
