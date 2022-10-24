"""Tests for the tcclitools TcSolution class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

from tcclitools.tcplcproject import TcPlcProject
from tcclitools.tcsolution import TcSolution
from tcclitools.tcxaeproject import TcXaeProject

RESOURCE_PATH = Path(".") / "tests" / "resources"


def test_get_xae_projects() -> None:
    path = RESOURCE_PATH / "Solution"
    solution = TcSolution(path / "Solution.sln")
    expected = {
        TcXaeProject(path / "TwinCAT Project1" / "TwinCAT Project1.tsproj"),
        TcXaeProject(path / "TwinCAT Project2" / "TwinCAT Project2.tsproj"),
    }
    assert expected == set(solution.xae_projects)


def test_get_plc_projects() -> None:
    path = RESOURCE_PATH / "MultiplePlcs"
    solution = TcSolution(path / "MultiplePlcs.sln")
    expected = {
        TcPlcProject(path / "MultiplePlcs" / "PLC1" / "PLC1.plcproj"),
        TcPlcProject(path / "MultiplePlcs" / "PLC2" / "PLC2.plcproj"),
    }
    assert expected == set(solution.plc_projects)
