""" A base class for objects that are uniquely based on a file or path"""
from __future__ import annotations

from pathlib import Path


class UniquePathException(Exception):
    """TcLibrary exception base class"""


class UniquePath:
    """A base class for objects that are uniquely based on an existing path.

    The derived class can optionally fill the `_allowed_types` list
    to check for valid path types.

    An empty list (the default) will check if the path points to a file.

    A `None` in the list will check if the path is a valid directory.

    """

    _allowed_types: list[str | None] = []

    def __init__(self, filepath: Path):
        self.filepath = filepath.resolve()
        if not self.filepath.exists():
            raise FileNotFoundError(f"'{self.filepath}' does not exist")
        extension_ok = (len(self._allowed_types) == 0) and self.filepath.is_file()
        for suffix in self._allowed_types:
            if (suffix is None and self.filepath.is_dir()) or (
                self.filepath.suffix in self._allowed_types
            ):
                extension_ok = True
                break
        if not extension_ok:
            type_string = ""
            for allowed_type in self._allowed_types:
                type_string += (
                    "Directory" if allowed_type is None else f'"{allowed_type}"'
                )
            raise UniquePathException(
                f"'{self.filepath}' does not match expected type: {type_string}"
            )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UniquePath):
            return NotImplemented
        return self.filepath == other.filepath

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.filepath}")'

    def __hash__(self) -> int:
        return hash(self.filepath)
