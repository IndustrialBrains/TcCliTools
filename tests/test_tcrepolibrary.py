"""Tests for the tcclitools TcLibrary class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

from packaging.version import parse

from tcclitools.tcrepolibrary import TcRepoLibrary, get_library_repository

RESOURCE_PATH = Path(".") / "tests" / "resources" / "Managed Libraries"


def test_library_from_repository() -> None:
    company = "Beckhoff Automation GmbH"
    title = "Tc2_Standard"
    version_str = "3.3.3.0"

    path = RESOURCE_PATH / company / title / version_str
    lib = TcRepoLibrary(path)

    assert lib.company == company
    assert lib.title == title
    assert lib.version == parse(version_str)


def test_all_libraries_in_repository() -> None:
    assert len(list(get_library_repository(RESOURCE_PATH))) == 2
