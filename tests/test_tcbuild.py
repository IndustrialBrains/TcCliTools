"""Tests for the tcclitools TcSolution class"""
# pylint: disable=missing-function-docstring

from pathlib import Path

import pytest

from tcclitools.tcbuild import build, install, is_available

tcbuild_available, reason = is_available()

RESOURCE_PATH = Path(".") / "tests" / "resources"


@pytest.mark.skipif(not tcbuild_available, reason=reason)
def test_build_missing_file() -> None:
    (success, _) = build(Path(""))
    assert not success


@pytest.mark.skipif(not tcbuild_available, reason=reason)
def test_build_solution() -> None:
    (success, _) = build(RESOURCE_PATH / "EmptySolution" / "EmptySolution.sln")
    assert success


@pytest.mark.skipif(not tcbuild_available, reason=reason)
def test_install_library() -> None:
    (success, _) = install(RESOURCE_PATH / "LibA" / "LibA.sln", "LibA", "Untitled1")
    assert success
