"""Tests for the tcclitools TcXaeProject class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

from tcclitools.tcplcproject import TcPlcProject
from tcclitools.tcxaeproject import TcXaeProject

RESOURCE_PATH = Path(".") / "tests" / "resources"


def test_get_plc_projects() -> None:
    path = RESOURCE_PATH / "MultiplePlcs" / "MultiplePlcs"
    solution = TcXaeProject(path / "MultiplePlcs.tsproj")
    expected = {
        TcPlcProject(path / "PLC1" / "PLC1.plcproj"),
        TcPlcProject(path / "PLC2" / "PLC2.plcproj"),
    }
    assert expected == set(solution.plc_projects)


def test_get_independent_plc_project() -> None:
    path = RESOURCE_PATH / "IndependentProjectFile" / "IndependentProjectFile"
    solution = TcXaeProject(path / "IndependentProjectFile.tsproj")
    expected = {
        TcPlcProject(path / "PLC1" / "PLC1.plcproj"),
        TcPlcProject(path / "PLC2" / "PLC2.plcproj"),
    }
    assert expected == set(solution.plc_projects)
