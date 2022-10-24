"""A TwinCAT library in the library repository"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from defusedxml import ElementTree

from .exceptions import InvalidLibraryError
from .tclibraryreference import TcLibraryReference
from .uniquepath import UniquePath


class TcRepoLibrary(TcLibraryReference, UniquePath):
    """A TwinCAT library in the library repository"""

    def __init__(self, path: Path) -> None:
        """Initialize a TcRepoLibrary from a folder in the Library Repository.
        The specified folder must contain a `browsercache.` file which contains the
        library properties (name, version and company)."""

        self._allowed_types = [None]
        UniquePath.__init__(self, path)

        path_browsercache = path / "browsercache"
        if not path_browsercache.exists():
            raise FileNotFoundError(f"Missing browsercache file in directory '{path}'")
        try:
            full_name = ElementTree.parse(path_browsercache).getroot().attrib["Name"]
            (title, version, company) = self.parse_string(full_name)
        except Exception as exc:
            raise InvalidLibraryError(
                f'Invalid browsercache file: "{path_browsercache}"'
            ) from exc

        TcLibraryReference.__init__(
            self,
            title=title,
            version=version,
            company=company,
        )

    def as_reference(self) -> TcLibraryReference:
        """Return a TcLibraryReference object"""
        return TcLibraryReference(self.title, self.version, self.company)

    def __hash__(self) -> int:  # pylint:disable=useless-parent-delegation
        # https://stackoverflow.com/questions/53518981/inheritance-hash-sets-to-none-in-a-subclass
        return super().__hash__()


def get_library_repository(
    tc_path: Path = Path("C:\\TwinCAT\\3.1\\Components\\Plc\\Managed Libraries"),
) -> Iterable[TcRepoLibrary]:
    """Return libraries from a library repository.
    Defaults to the `C:\\TwinCAT\\3.1\\Components\\Plc\\Managed Libraries` folder."""
    if not tc_path.exists():
        raise FileNotFoundError(f"Path '{tc_path}' does not exist!")
    for path in tc_path.glob("**/browsercache"):
        yield TcRepoLibrary(path.parent)
