"""A TwinCAT XAE Project"""
from __future__ import annotations

from pathlib import Path

from defusedxml import ElementTree

from .tcplcproject import TcPlcProject
from .uniquepath import UniquePath


class TcXaeProject(UniquePath):  # pylint:disable=too-few-public-methods
    """A TwinCAT XAE Project"""

    def __init__(self, path: Path):
        self._allowed_types = [".tsproj", ".tspproj"]
        super().__init__(path)
        self.xmlroot = ElementTree.parse(path).getroot()
        self._plc_projects: set[TcPlcProject] | None = None

    @property
    def plc_projects(self) -> set[TcPlcProject]:
        """PLC projects in the XAE project"""
        if self._plc_projects is None:
            projects: list[TcPlcProject] = []
            for project in self.xmlroot.findall(".//{*}Plc/Project"):
                if "PrjFilePath" in project.attrib:
                    projects.append(
                        TcPlcProject(self.path.parent / project.attrib["PrjFilePath"])
                    )
                elif "File" in project.attrib:
                    # Independent project file
                    xti_path = self.path.parent / "_Config" / "PLC"
                    xti_file = xti_path / project.attrib["File"]
                    if not xti_file.exists():
                        raise FileNotFoundError(
                            f"Missing independent project file: {xti_file.absolute()}"
                        )
                    xmlroot = ElementTree.parse(xti_file).getroot()
                    prj_path = xmlroot.find(".//{*}Project").attrib["PrjFilePath"]
                    projects.append(TcPlcProject(xti_path / prj_path))

            self._plc_projects = set(projects)

        return self._plc_projects
