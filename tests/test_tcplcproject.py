"""Tests for the tcclitools TcPlcProject class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

from tcclitools.tclibrary import TcLibraryReference
from tcclitools.tcplcproject import TcPlcProject

RESOURCE_PATH = (
    Path(".")
    / "tests"
    / "resources"
    / "PlcDefault"
    / "PlcDefault"
    / "StandardPlcProject"
    / "StandardPlcProject.plcproj"
)


def test_get_libraries() -> None:
    plcproject = TcPlcProject(RESOURCE_PATH)
    version = "*"
    company = "Beckhoff Automation GmbH"
    expected_libraries = {
        TcLibraryReference("Tc2_Standard", version, company),
        TcLibraryReference("Tc2_System", version, company),
        TcLibraryReference("Tc3_Module", version, company),
    }
    assert expected_libraries == plcproject.library_references
