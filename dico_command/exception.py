from dico.exception import DicoException


class CommandException(DicoException):
    """Base exception for dico-command."""
    def __init__(self, *args):
        super().__init__(*args or [self.__doc__])


class InvalidArgument(CommandException):
    """Parsing argument has failed."""


class CheckFailed(CommandException):
    """Command check has failed."""


class InvalidModule(CommandException):
    """Unable to find module. Check if path is correct."""


class ModuleNotLoaded(CommandException):
    """This module is never loaded."""


class MissingLoadFunction(CommandException):
    """This module is missing "load" function."""


class MissingUnloadFunction(CommandException):
    """This module is missing "unload" function."""
