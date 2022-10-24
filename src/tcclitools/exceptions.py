"""TcCliTools exceptions"""


class TcCliToolsException(Exception):
    """TcCliToolsException exception base class"""


class MissingLibrariesError(TcCliToolsException):
    """Missing libraries exception"""


class InvalidLibraryError(TcCliToolsException):
    """Invalid library exception"""


class TcBuildInvokeError(TcCliToolsException):
    """Error when invoking TcBuild"""
