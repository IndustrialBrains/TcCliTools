"""TcCliTools exceptions"""


class TcCliToolsException(Exception):
    """TcCliToolsException exception base class"""


class MissingLibrariesError(TcCliToolsException):
    """Missing libraries exception"""


class InvalidFileError(TcCliToolsException):
    """Inavlid file exception"""
