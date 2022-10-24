"""Wrapper for the TcBuild tool"""
import subprocess  # nosec
from pathlib import Path

from packaging.version import InvalidVersion, Version

from .exceptions import TcBuildInvokeError

VERSION_MINIMAL = Version("1.0.1.0")


def run(args: list[str]) -> tuple[int, str]:
    """Run TcBuild with the given arguments, and return the exit code and console output"""

    def merge_output(stdout: str, stderr: str) -> str:
        # Prefer contents of stderr stream over stdout
        output = stderr if stderr else stdout
        return output.strip()

    try:
        proc = subprocess.run(  # nosec
            ["tcbuild.exe"] + args,
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        if exc.returncode != 0:
            return (exc.returncode, merge_output(exc.stdout, exc.stderr))
        raise exc

    return (proc.returncode, merge_output(proc.stdout, proc.stderr))


def is_available(raise_if_unavailable: bool = False) -> tuple[bool, str]:
    """Check if TcBuild is available. If not, return `False` and the reason why,\\
    or raise an exception when `raise_if_unavailable` is `True`."""
    version: Version | None = None

    def raise_or_return(msg: str) -> tuple[bool, str]:
        if raise_if_unavailable:
            raise TcBuildInvokeError(msg)
        return (False, msg)

    try:
        (returncode, output) = run(["--version"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return raise_or_return("TcBuild not installed or not available on PATH")

    if returncode != 0:
        return raise_or_return(
            f'TcBuild exited with returncode {returncode}: "{output}"'
        )

    try:
        version = Version(output)
    except InvalidVersion:
        return raise_or_return(
            f'TcBuild returned unexpected version string: "{output}"'
        )

    if version < VERSION_MINIMAL:
        return raise_or_return(
            f"TcBuild version is outdated (got: {version}, expected: {VERSION_MINIMAL})",
        )

    return (True, "")


def build(path: Path) -> tuple[bool, str]:
    """Build the solution. If it fails, return False and the reason why."""
    is_available(raise_if_unavailable=True)
    (returncode, output) = run(["build", str(path.resolve())])
    if returncode == 0:
        return (True, "")
    return (False, f"TcBuild exited with code {returncode}. Details:\n{output}")


def install(
    path: Path, xaeproject: str, plcproject: str, libraryfile: str | None = None
) -> tuple[bool, str]:
    """Install a library. If it fails, return False and the reason why."""
    is_available(raise_if_unavailable=True)
    cmds = [
        "install",
        str(path.resolve()),
        "--xaeproject",
        xaeproject,
        "--plcproject",
        plcproject,
    ]
    if libraryfile:
        cmds.extend(["--libraryfile", libraryfile])
    (returncode, output) = run(cmds)
    if returncode == 0:
        return (True, "")
    return (False, f"TcBuild exited with code {returncode}. Details:\n{output}")
