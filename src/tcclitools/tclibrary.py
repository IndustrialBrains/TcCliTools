"""A TwinCAT library"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from defusedxml import ElementTree
from packaging import version as version_module

from tcclitools.uniquepath import UniquePath

from .exceptions import InvalidFileError
from .tclibraryreference import TcLibraryReference


class TcLibrary(TcLibraryReference, UniquePath):
    """A TwinCAT library"""

    def __init__(
        self,
        path: Path,
    ) -> None:
        """Initialize a TcLibrary from a PLC project file (`.plcproj`) or a folder
        in the Library Repository.

        The default Library Repository folder is
        `C:\\TwinCAT\\3.1\\Components\\Plc\\Managed Libraries`
        The specified folder must contain a `browsercache.` file which contains the
        library properties (name, version and company)."""

        self._allowed_types = [".plcproj", None]
        UniquePath.__init__(self, path)

        if path.is_dir():  # Must be a library repository folder
            self.path = path
            path_browsercache = path / "browsercache"
            if not path_browsercache.exists():
                raise FileNotFoundError(
                    f"Missing browsercache file in directory '{path}'"
                )
            try:
                full_name = (
                    ElementTree.parse(path_browsercache).getroot().attrib["Name"]
                )
                (title, version, company) = self.parse_string(full_name)
            except Exception as exc:
                raise InvalidFileError(
                    f'Invalid browsercache file: "{path_browsercache}"'
                ) from exc

        else:  # Must be a .plcproj file
            try:
                xmlroot = ElementTree.parse(path).getroot()
                (title, version, company) = [
                    xmlroot.find("./{*}PropertyGroup/{*}" + find_str).text
                    for find_str in ["Title", "ProjectVersion", "Company"]
                ]
                version = version_module.parse(version)  # type:ignore
            except Exception as exc:
                raise InvalidFileError(f'Not a valid library: "{path}"') from exc

        TcLibraryReference.__init__(
            self,
            title=title,
            version=version,
            company=company,
        )

    def as_reference(self) -> TcLibraryReference:
        """Return a TcLibraryReference instance"""
        return TcLibraryReference(self.title, self.version, self.company)

    def __hash__(self) -> int:  # pylint:disable=useless-parent-delegation
        # https://stackoverflow.com/questions/53518981/inheritance-hash-sets-to-none-in-a-subclass
        return super().__hash__()


def get_library_repository(
    tc_path: Path = Path("C:\\TwinCAT\\3.1\\Components\\Plc\\Managed Libraries"),
) -> Iterable[TcLibrary]:
    """Return libraries from a library repository.
    Defaults to the `C:\\TwinCAT\\3.1\\Components\\Plc\\Managed Libraries` folder."""
    if not tc_path.exists():
        raise FileNotFoundError(f"Path '{tc_path}' does not exist!")
    for path in tc_path.glob("**/browsercache"):
        yield TcLibrary(path.parent)
