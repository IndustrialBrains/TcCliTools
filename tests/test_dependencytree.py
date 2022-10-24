"""Tests for the tcclitools TcSolution class"""
# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long

from pathlib import Path

import pytest
from anytree.search import find

from tcclitools.dependencytree import (
    DependencyTree,
    MissingLibrariesError,
    TcNode,
    get_all_solutions,
    render_tree,
)
from tcclitools.tclibraryreference import TcLibraryReference
from tcclitools.tcplcproject import TcPlcProject
from tcclitools.tcsolution import TcSolution

RESOURCE_PATH = Path(".") / "tests" / "resources"

LIB_A = TcSolution(RESOURCE_PATH / "LibA" / "LibA.sln")
DEP_ON_LIB_A = TcSolution(
    RESOURCE_PATH / "ProjectDependingOnLibA" / "ProjectDependingOnLibA.sln"
)


def test_generate_simple_dependency_tree() -> None:
    solution = TcSolution(RESOURCE_PATH / "EmptySolution" / "EmptySolution.sln")
    expected = TcNode(solution, children=[TcNode(next(solution.xae_projects))])
    tree = DependencyTree(solution, {})
    assert str(tree) == render_tree(expected)


def test_generate_dependency_tree() -> None:
    # Should generate something similar to:
    # TcSolution(".\ProjectDependingOnLibA\ProjectDependingOnLibA.sln")
    # └── TcXaeProject(".\ProjectDependingOnLibA\ProjectDependingOnLibA\ProjectDependingOnLibA.tspproj")
    #     └── TcPlcProject(".\ProjectDependingOnLibA\ProjectDependingOnLibA\Untitled1\Untitled1.plcproj")
    #         └── LibA, * (Industrial Brains B.V.)
    #             └── TcPlcProject(".\LibA\LibA\Untitled1\Untitled1.plcproj")
    solution = DEP_ON_LIB_A
    library = LIB_A
    library_xae_project = list(library.xae_projects)[0]
    library_plc_project = list(library_xae_project.plc_projects)[0]
    solution_xae_project = list(solution.xae_projects)[0]
    solution_plc_project = list(solution_xae_project.plc_projects)[0]
    expected = TcNode(
        solution,
        children=[
            TcNode(
                solution_xae_project,
                children=[
                    TcNode(
                        solution_plc_project,
                        children=[
                            TcNode(
                                list(solution_plc_project.library_references)[0],
                                children=[TcNode(library_plc_project)],
                            )
                        ],
                    )
                ],
            )
        ],
    )
    tree = DependencyTree(solution, {library})
    assert str(tree) == render_tree(expected)


def test_dependency_tree_latest_version() -> None:
    libraries = [LIB_A, TcSolution(RESOURCE_PATH / "LibA_Newer" / "LibA.sln")]

    # The latest version should be selected
    expected = next(next(libraries[1].xae_projects).plc_projects)

    tree = DependencyTree(DEP_ON_LIB_A, libraries)

    # The last node should be the selected library
    libnode: TcNode = find(tree.trunk, lambda node: len(node.children) == 0)
    assert libnode.origin == expected

    # Reversing order of libraries should not matter
    tree = DependencyTree(DEP_ON_LIB_A, libraries[::-1])
    libnode = find(tree.trunk, lambda node: len(node.children) == 0)
    assert libnode.origin == expected


def test_dependency_tree_missing_libraries() -> None:
    tree = DependencyTree(DEP_ON_LIB_A, {})
    expected = {TcLibraryReference("LibA", "*", "Industrial Brains B.V.")}
    assert tree.missing_libraries == expected


def test_get_all_solutions() -> None:
    path = RESOURCE_PATH / "Solution"
    assert list(get_all_solutions(path)) == [TcSolution(path / "Solution.sln")]


def test_get_build_order() -> None:
    target_solution = TcSolution(
        RESOURCE_PATH / "MultipleDependencies" / "MultipleDependencies.sln"
    )
    lib_a = LIB_A
    lib_b = TcSolution(RESOURCE_PATH / "LibB" / "LibB.sln")  # depends on A
    available_solutions = [lib_a, lib_b]
    expected = [next(lib_a.plc_projects), next(lib_b.plc_projects), target_solution]
    build_order = DependencyTree(target_solution, available_solutions).get_build_order()
    assert build_order == expected


def test_get_build_order_missing_library() -> None:
    with pytest.raises(MissingLibrariesError):
        DependencyTree(DEP_ON_LIB_A).get_build_order()


def test_multiple_libraries_in_one_solution() -> None:
    path = RESOURCE_PATH / "MultipleLibraries"
    target_solution = TcSolution(
        path / "ProjectDependingOnLibA" / "ProjectDependingOnLibA.sln"
    )
    library_solution = TcSolution(
        path / "ProjectWithLibAandB" / "ProjectWithLibAandB.sln"
    )
    library = TcPlcProject(
        path / "ProjectWithLibAandB" / "ProjectWithLibAandB" / "LibA" / "LibA.plcproj"
    )
    expected = [library, target_solution]
    build_order = DependencyTree(target_solution, [library_solution]).get_build_order()
    assert build_order == expected
