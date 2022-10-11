"""Tests for the tcclitools TcLibraryReference class"""
# pylint: disable=missing-function-docstring

import pytest
from packaging import version as version_module

from tcclitools.tclibrary import TcLibraryException, TcLibraryReference

TITLE = "foo"
COMPANY = "bar"
VERSION_STR = "1"
VERSION = version_module.Version(VERSION_STR)


def test_compare_eq() -> None:
    lib_a1 = TcLibraryReference(TITLE, "*", COMPANY)
    lib_a2 = TcLibraryReference(TITLE, "*", COMPANY)
    lib_any = TcLibraryReference(TITLE, "*", COMPANY)
    assert lib_a1 == lib_a2
    assert lib_a1 == lib_any


def test_compare_gt() -> None:
    lib_a1 = TcLibraryReference(TITLE, "1", COMPANY)
    lib_a2 = TcLibraryReference(TITLE, "2", COMPANY)
    lib_any = TcLibraryReference(TITLE, "*", COMPANY)
    assert lib_a2 > lib_a1
    assert lib_any > lib_a1
    with pytest.raises(NotImplementedError):
        assert lib_a1 > lib_any


def test_compare_ge() -> None:
    lib_a1 = TcLibraryReference(TITLE, "1", COMPANY)
    lib_a2 = TcLibraryReference(TITLE, "2", COMPANY)
    lib_a3 = TcLibraryReference(TITLE, "2", COMPANY)
    lib_any = TcLibraryReference(TITLE, "*", COMPANY)
    assert lib_a2 >= lib_a1
    assert lib_a3 >= lib_a2
    assert lib_any >= lib_a1


def test_parse_string() -> None:
    (title, version, company) = TcLibraryReference.parse_string(
        f"{TITLE}, {VERSION_STR} ({COMPANY})"
    )
    assert title == TITLE
    assert version == VERSION
    assert company == COMPANY


def test_from_string() -> None:
    lib = TcLibraryReference.from_string(f"{TITLE}, {VERSION_STR} ({COMPANY})")
    assert lib.title == TITLE
    assert lib.version == VERSION
    assert lib.company == COMPANY


def test_parse_invalid_library_string() -> None:
    with pytest.raises(TcLibraryException):
        TcLibraryReference.parse_string("foobar")


def test_select_latest() -> None:
    lib_v1 = TcLibraryReference(TITLE, "1", COMPANY)
    lib_v2 = TcLibraryReference(TITLE, "2", COMPANY)
    latest = TcLibraryReference.select_latest([lib_v1, lib_v2])
    assert latest == lib_v2


def test_select_invalid_latest() -> None:
    lib_a = TcLibraryReference("foo", "1", "bar")
    lib_b = TcLibraryReference("bar", "2", "foo")
    with pytest.raises(TcLibraryException):
        TcLibraryReference.select_latest([lib_a, lib_b])
