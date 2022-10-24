"""Tests for the tcclitools TcPlcProject class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

from tcclitools.tclibraryreference import TcLibraryReference
from tcclitools.tcplcproject import TcPlcProject

RESOURCE_PATH = Path(".") / "tests" / "resources"


def test_get_libraries() -> None:
    plcproject = TcPlcProject(
        RESOURCE_PATH
        / "PlcDefault"
        / "PlcDefault"
        / "StandardPlcProject"
        / "StandardPlcProject.plcproj"
    )
    version = "*"
    company = "Beckhoff Automation GmbH"
    expected_libraries = {
        TcLibraryReference("Tc2_Standard", version, company),
        TcLibraryReference("Tc2_System", version, company),
        TcLibraryReference("Tc3_Module", version, company),
    }
    assert expected_libraries == set(plcproject.library_references)


def test_as_library() -> None:
    plcproject = TcPlcProject(
        RESOURCE_PATH
        / "PlcLibrary"
        / "PlcLibrary"
        / "EmptyPlcProject"
        / "EmptyPlcProject.plcproj"
    )
    assert plcproject.as_reference() is not None


def test_as_library_fail() -> None:
    plcproject = TcPlcProject(
        RESOURCE_PATH
        / "PlcDefault"
        / "PlcDefault"
        / "StandardPlcProject"
        / "StandardPlcProject.plcproj"
    )
    assert plcproject.as_reference() is None
