from dico.exception import DicoException


class CommandException(DicoException):
    """Base exception for dico-command."""
    def __init__(self, *args, **fmt):
        super().__init__(*args or [self.__doc__.format(**fmt)])


class CommandAlreadyExists(CommandException):
    """Command {name} already exists."""


class CommandNotExists(CommandException):
    """Command {name} doesn't exist."""


class InvalidArgument(CommandException):
    """Parsing argument has failed."""


class CheckFailed(CommandException):
    """Command check has failed."""


class InvalidModule(CommandException):
    """Unable to find module {path}. Check if path is correct."""


class ModuleAlreadyLoaded(CommandException):
    """Module {path} is already loaded."""


class ModuleNotLoaded(CommandException):
    """Module {path} is never loaded."""


class MissingLoadFunction(CommandException):
    """Module {path} is missing "load" function."""


class MissingUnloadFunction(CommandException):
    """Module {path} is missing "unload" function."""


class AddonAlreadyLoaded(CommandException):
    """Addon {name} is already loaded."""
