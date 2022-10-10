"""A TcXaeShell solution"""
from __future__ import annotations

import re
from pathlib import Path

from .tclibrary import TcLibraryReference
from .tcxaeproject import TcXaeProject
from .uniquepath import UniquePath


class TcSolution(UniquePath):
    """A TcXaeShell solution"""

    _REGEX_PROJECT_FILE = re.compile(r'Project\("\{.*?\}"\).*?,\s"(.+tsp{1,2}roj)"')

    def __init__(self, path: Path):
        self._allowed_types = [".sln"]
        super().__init__(path)
        self._library_references: set[TcLibraryReference] | None = None
        self._xae_projects: set[TcXaeProject] | None = None

    @property
    def xae_projects(self) -> set[TcXaeProject]:
        """Get XAE projects referenced by the solution"""
        if self._xae_projects is None:
            projects = []
            with self.path.open("r", encoding="utf-8") as file:
                for line in file.readlines():
                    match = self._REGEX_PROJECT_FILE.match(line)
                    if match:
                        projects.append(TcXaeProject(self.path.parent / match.group(1)))
            self._xae_projects = set(projects)
        return self._xae_projects  # type:ignore

    @property
    def library_references(self) -> set[TcLibraryReference]:
        """Libraries referenced by the solution"""
        if self._library_references is None:
            self._library_references = {
                library
                for xae_project in self.xae_projects
                for plc_project in xae_project.plc_projects
                for library in plc_project.library_references
            }
        return self._library_references  # type:ignore
