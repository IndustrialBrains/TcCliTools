"""A TcXaeShell solution"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable

from .tclibraryreference import TcLibraryReference
from .tcplcproject import TcPlcProject
from .tctreeitem import TcTreeItem
from .tcxaeproject import TcXaeProject
from .uniquepath import UniquePath


class TcSolution(UniquePath, TcTreeItem):
    """A TcXaeShell solution"""

    _REGEX_PROJECT_FILE = re.compile(r'Project\("\{.*?\}"\).*?,\s"(.+tsp{1,2}roj)"')

    def __init__(self, path: Path, children: Iterable[Any] | None = None):
        self._allowed_types = [".sln"]
        UniquePath.__init__(self, path)
        TcTreeItem.__init__(self, parent=None, children=children)
        self._xae_projects: set[TcXaeProject] | None = None
        self._plc_projects: set[TcPlcProject] | None = None
        self._library_references: set[TcLibraryReference] | None = None

    @property
    def xae_projects(self) -> Iterable[TcXaeProject]:
        """XAE projects in the solution"""
        if self._xae_projects is None:
            projects = []
            with self.filepath.open("r", encoding="utf-8") as file:
                for line in file.readlines():
                    match = self._REGEX_PROJECT_FILE.match(line)
                    if match:
                        projects.append(
                            TcXaeProject(
                                self.filepath.parent / match.group(1), parent=self
                            )
                        )
            self._xae_projects = set(projects)
        return iter(self._xae_projects)

    @property
    def plc_projects(self) -> Iterable[TcPlcProject]:
        """PLC projects in the solution"""
        if self._plc_projects is None:
            self._plc_projects = {
                plc_project
                for xae_project in self.xae_projects
                for plc_project in xae_project.plc_projects
            }
        return iter(self._plc_projects)
