"""A dependency tree of a TwinCAT solution"""
from pathlib import Path
from typing import Iterable

from anytree import LevelOrderGroupIter, Node, RenderTree

from .tclibrary import TcLibrary, TcLibraryException, TcLibraryReference
from .tcsolution import TcSolution


class DependencyTreeException(Exception):
    """DependencyTree exception base class"""


class DependencyTree:
    """A dependency tree of a TwinCAT solution"""

    def __init__(
        self,
        solution: TcSolution,
        libraries: Iterable[TcSolution | TcLibrary | TcLibraryReference] | None = None,
    ) -> None:
        """Build a dependency tree for `root_solution`.
        The required libraries will be retrieved from `library_solutions`,
        except for library references in `ignored_libraries`."""

        # Build a list of available library references and include the solution if available
        available_libraries: list[tuple[TcSolution | None, TcLibraryReference]] = []
        unique_references: list[
            TcLibraryReference
        ] = []  # helper list, used to filter duplicates

        if libraries:
            for item in libraries:
                lib_solution: TcSolution | None = None
                if isinstance(item, TcSolution):
                    # Get all PLC projects in the solution, and add those
                    # which can be installed as a library to the list
                    for xae_project in item.xae_projects:
                        for plc_project in xae_project.plc_projects:
                            try:
                                library = TcLibrary(plc_project.path)
                            except TcLibraryException:
                                # ignore failed attempt to convert PLC project to library
                                continue
                            lib_reference = library.as_reference()
                            lib_solution = item
                elif isinstance(item, TcLibrary):
                    lib_reference = item.as_reference()
                elif isinstance(item, TcLibraryReference):
                    lib_reference = item

                if lib_reference not in unique_references:  # ignore duplicates
                    unique_references.append(lib_reference)
                    available_libraries.append((lib_solution, lib_reference))

        missing_libraries: list[TcLibraryReference] = []

        def traverse(parent: Node):
            """Recursively create child nodes for all library references in the parent node"""
            for required_library in parent.solution.library_references:
                child = Node(str(required_library), parent=parent)

                # Check if the library is available
                (matching_solution, matching_library) = next(  # type:ignore
                    (
                        (sol, lib)
                        for (sol, lib) in available_libraries
                        if lib == required_library
                    ),
                    (None, None),
                )

                if matching_solution is not None:
                    # Found a solution with a matching library,
                    # traverse dependencies of the solution
                    traverse(
                        Node(
                            str(matching_library),
                            parent=child,
                            solution=matching_solution,
                        )
                    )
                elif matching_library is None:
                    # Library is missing
                    missing_libraries.append(required_library)
                else:
                    # Nothing to do: got a reference to a available library
                    pass

        self.trunk = Node(solution.path, solution=solution)
        traverse(self.trunk)

        self.missing_libraries = set(missing_libraries)

    def __str__(self) -> str:
        """Return the dependency tree as a printable tree structure"""
        tree_str = ""
        for pre, _, node in RenderTree(self.trunk):
            tree_str += f"{pre}{node.name}\n"
        return tree_str

    def get_build_order(self) -> list[TcSolution]:
        """Return the build order of all solutions in the dependency tree"""

        if self.missing_libraries:
            raise DependencyTreeException(
                f"Unable to generate build order, missing libraries: {self.missing_libraries}"
            )

        # Group solutions by tree depth (result is reversed to get deepest level first)
        # https://anytree.readthedocs.io/en/latest/api/anytree.iterators.html#anytree.iterators.levelordergroupiter.LevelOrderGroupIter
        levels = [
            [node.solution for node in children if hasattr(node, "solution")]
            for children in LevelOrderGroupIter(self.trunk)
        ][::-1]
        # Generate build order, filter builds that have already been done
        build_order = []
        for solutions in levels:
            for solution in solutions:
                if solution not in build_order:
                    build_order.append(solution)
        return build_order


def get_all_solutions(path: Path) -> list[TcSolution]:
    """Return a list of all solutions in a folder (including subfolders)"""
    return [TcSolution(path=solution_path) for solution_path in path.glob("**/*.sln")]
