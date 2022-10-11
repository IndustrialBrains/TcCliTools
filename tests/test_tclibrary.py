"""Tests for the tcclitools TcLibrary class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

from packaging import version as version_module

from tcclitools.tclibrary import TcLibrary
from tcclitools.tclibrary.tclibraryreference import TcLibraryReference

RESOURCE_PATH = Path(".") / "tests" / "resources"


def test_library_from_project() -> None:
    path = (
        RESOURCE_PATH
        / "PlcLibrary"
        / "PlcLibrary"
        / "EmptyPlcProject"
        / "EmptyPlcProject.plcproj"
    )
    lib = TcLibrary(path)
    assert lib.title == "Empty test library"
    assert lib.version == version_module.parse("0.0")
    assert lib.company == "Industrial Brains B.V."


def test_as_reference() -> None:
    path = (
        RESOURCE_PATH
        / "PlcLibrary"
        / "PlcLibrary"
        / "EmptyPlcProject"
        / "EmptyPlcProject.plcproj"
    )
    lib = TcLibrary(path)
    assert lib.as_reference() == TcLibraryReference(lib.title, lib.version, lib.company)


def test_library_from_repository() -> None:
    company = "Beckhoff Automation GmbH"
    title = "Tc2_Standard"
    version_str = "3.3.3.0"

    path = RESOURCE_PATH / "Managed Libraries" / company / title / version_str
    lib = TcLibrary(path)

    assert lib.company == company
    assert lib.title == title
    assert lib.version == version_module.parse(version_str)


def test_all_libraries_in_repository() -> None:
    path = RESOURCE_PATH / "Managed Libraries"
    assert len(TcLibrary.get_library_repository(path)) == 2
