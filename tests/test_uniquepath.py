"""Tests for the tcclitools TcSolution class"""
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods

from pathlib import Path

import pytest

from tcclitools.uniquepath import UniquePath, UniquePathException

RESOURCE_PATH = Path(".") / "tests" / "resources"


def test_no_file() -> None:
    with pytest.raises(UniquePathException):
        UniquePath(RESOURCE_PATH)


def test_any_extension() -> None:
    UniquePath(RESOURCE_PATH / "emptyfile")


def test_suffix() -> None:
    class DerivedClass(UniquePath):  # type:ignore
        def __init__(self, path: Path):
            self._allowed_types = [".extension"]
            super().__init__(path)

    DerivedClass(RESOURCE_PATH / "filewith.extension")


def test_directory() -> None:
    class DerivedClass(UniquePath):  # type:ignore
        def __init__(self, path: Path):
            self._allowed_types = [None]
            super().__init__(path)

    DerivedClass(RESOURCE_PATH)


def test_no_directory() -> None:
    class DerivedClass(UniquePath):  # type:ignore
        def __init__(self, path: Path):
            self._allowed_types = [None]
            super().__init__(path)

    with pytest.raises(Exception):
        DerivedClass(Path(__file__))
