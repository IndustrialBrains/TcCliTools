"""Tests for the tcclitools TcSolution class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

import pytest
from anytree import Node

from tcclitools.dependencytree import (
    DependencyTree,
    DependencyTreeException,
    get_all_solutions,
)
from tcclitools.tclibrary import TcLibraryReference
from tcclitools.tcsolution import TcSolution

RESOURCE_PATH = Path(".") / "tests" / "resources"

LIB_A = TcSolution(RESOURCE_PATH / "LibA" / "LibA.sln")
DEP_ON_LIB_A = TcSolution(
    RESOURCE_PATH / "ProjectDependingOnLibA" / "ProjectDependingOnLibA.sln"
)


def test_build_dependency_tree():
    available_solutions = [LIB_A]
    expected = Node(
        DEP_ON_LIB_A.path,
        solution=DEP_ON_LIB_A,
        children=[Node(available_solutions[0].path, solution=available_solutions[0])],
    )
    tree = DependencyTree(DEP_ON_LIB_A, available_solutions)
    assert str(tree.trunk) == str(expected)


def test_dependency_tree_latest_version():
    available_solutions = [
        LIB_A,
        TcSolution(RESOURCE_PATH / "LibA_Newer" / "LibA.sln"),
    ]

    # The latest version should be selected
    expected = Node(
        DEP_ON_LIB_A.path,
        solution=DEP_ON_LIB_A,
        children=[Node(available_solutions[1].path, solution=available_solutions[1])],
    )

    tree = DependencyTree(DEP_ON_LIB_A, available_solutions)

    assert str(tree.trunk) == str(expected)


def test_dependency_tree_missing_libraries():
    tree = DependencyTree(DEP_ON_LIB_A, {})
    expected = {TcLibraryReference("LibA", "*", "Industrial Brains B.V.")}
    assert tree.missing_libraries == expected


def test_get_all_solutions():
    path = RESOURCE_PATH / "Solution"
    assert get_all_solutions(path) == [TcSolution(path / "Solution.sln")]


def test_get_build_order():
    target_solution = TcSolution(
        RESOURCE_PATH / "MultipleDependencies" / "MultipleDependencies.sln"
    )
    lib_a = LIB_A
    lib_b = TcSolution(RESOURCE_PATH / "LibB" / "LibB.sln")  # depends on A
    available_solutions = [lib_a, lib_b]
    expected = [lib_a, lib_b, target_solution]
    build_order = DependencyTree(target_solution, available_solutions).get_build_order()
    assert build_order == expected


def test_get_build_order_missing_library():
    with pytest.raises(DependencyTreeException):
        DependencyTree(DEP_ON_LIB_A).get_build_order()
