"""A dependency tree of a TwinCAT solution"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from anytree import LevelOrderGroupIter, NodeMixin, RenderTree

from .exceptions import MissingLibrariesError
from .tclibraryreference import TcLibraryReference
from .tcplcproject import TcPlcProject
from .tcrepolibrary import TcRepoLibrary
from .tcsolution import TcSolution
from .tcxaeproject import TcXaeProject


class TcNode(NodeMixin):  # type:ignore
    """An AnyTree node with custom property for the TwinCAT object it references"""

    def __init__(
        self,
        origin: TcSolution
        | TcXaeProject
        | TcPlcProject
        | TcLibraryReference
        | TcRepoLibrary,
        parent: TcNode | None = None,
        children: list[TcNode] | None = None,
    ) -> None:
        """An AnyTree node with a reference to the TwinCAT object it originated from"""
        self.origin = origin
        self.parent = parent
        if children:
            self.children = children


class DependencyTree:
    """A dependency tree of a TwinCAT solution"""

    def __init__(
        self,
        solution: TcSolution,
        libraries: Iterable[TcSolution | TcRepoLibrary | TcLibraryReference]
        | None = None,
    ) -> None:
        """Build a dependency tree for `root_solution`.
        The required libraries will be retrieved from `libraries`"""

        # Extract library references from the 'libraries' argument
        library_references = []
        library_plc_projects: dict[TcLibraryReference, TcPlcProject] = {}
        if libraries:
            for item in libraries:
                if isinstance(item, TcSolution):
                    # Get all library projects in the solution
                    projects: set[TcPlcProject] = {
                        proj
                        for proj in item.plc_projects
                        if proj.as_reference() is not None
                    }
                    for project in projects:
                        library_references.append(project.as_reference())
                        library_plc_projects[
                            project.as_reference()  # type:ignore
                        ] = project
                elif isinstance(item, TcRepoLibrary):
                    library_references.append(item.as_reference())
                elif isinstance(item, TcLibraryReference):
                    library_references.append(item)
                else:
                    raise NotImplementedError(
                        f"Cannot extract library references of {type(item)} objects"
                    )
        # make unique
        library_references: set[TcLibraryReference] = set(  # type:ignore
            library_references
        )

        missing_libraries: list[TcLibraryReference] = []

        def traverse(node: TcNode) -> None:
            """Recursively create child nodes for all library references in the parent node"""
            origin = node.origin
            if isinstance(origin, TcSolution):
                for plcproject in origin.xae_projects:
                    traverse(TcNode(plcproject, parent=node))
            elif isinstance(origin, TcXaeProject):
                for xaeproject in origin.plc_projects:
                    traverse(
                        TcNode(
                            xaeproject,
                            parent=node,
                        )
                    )
            elif isinstance(origin, TcPlcProject):
                for reference in origin.library_references:
                    traverse(
                        TcNode(
                            reference,
                            parent=node,
                        )
                    )
            elif isinstance(origin, TcLibraryReference):
                # Get available libraries, sort them so that the newest version is the
                # first item in the list
                matching_libraries = sorted(
                    [lib for lib in library_references if lib == origin],
                    key=lambda lib: lib.version,
                    reverse=True,
                )
                if matching_libraries:
                    # It is, now check if the library reference is based on a PLC project.
                    # If so, traverse the dependencies of that solution
                    matching_library = matching_libraries[0]
                    if matching_library in library_plc_projects:
                        traverse(
                            TcNode(
                                library_plc_projects[matching_library],
                                parent=node,
                            )
                        )
                else:
                    # Library is missing
                    missing_libraries.append(origin)
            elif isinstance(node.origin, TcRepoLibrary):
                # No further dependencies (end of this branch)
                return
            else:
                raise NotImplementedError(
                    f"Cannot create dependency tree for {type(node.origin)} objects"
                )

        self.trunk = TcNode(solution)
        traverse(self.trunk)

        self.missing_libraries = set(missing_libraries)

    def __str__(self) -> str:
        """Return the dependency tree as a printable tree structure"""
        return render_tree(self.trunk)

    def get_build_order(self) -> list[TcSolution | TcPlcProject]:
        """Return the build order of all solutions in the dependency tree"""

        if self.missing_libraries:
            raise MissingLibrariesError(
                f"Unable to generate build order, missing libraries: {self.missing_libraries}"
            )

        # Group PLC projects in the tree by tree depth.
        # Result is reversed to get deepest level first).
        # https://anytree.readthedocs.io/en/latest/api/anytree.iterators.html#anytree.iterators.levelordergroupiter.LevelOrderGroupIter
        levels = [
            [node.origin for node in children if isinstance(node.origin, TcPlcProject)]
            for children in LevelOrderGroupIter(self.trunk)
        ][::-1]

        # Generate build order, filter builds that have already been done
        # and PLC projects that are part of the trunk (will always be built)
        build_order = []
        for plc_projects in levels:
            for plc_project in plc_projects:
                if (
                    plc_project not in build_order
                    and plc_project.parent.parent != self.trunk.origin  # type:ignore
                ):
                    build_order.append(plc_project)

        # add the last build: the solution itself
        build_order.extend([self.trunk.origin])  # type:ignore

        return build_order


def get_all_solutions(path: Path) -> Iterable[TcSolution]:
    """Return all solutions in a folder (including subfolders)"""
    for solution_path in path.glob("**/*.sln"):
        yield TcSolution(path=solution_path)


def render_tree(trunk: TcNode) -> str:
    """Render a tree of TcNodes to a human readable string"""
    tree_str = ""
    for pre, _, node in RenderTree(trunk):
        tree_str += f"{pre}{node.origin}\n"
    return tree_str
