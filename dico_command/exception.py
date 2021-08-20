from dico.exception import DicoException


class CommandException(DicoException):
    """Base exception for dico-command."""
    def __init__(self, *args):
        super().__init__(*args or [self.__doc__])


class InvalidArgument(CommandException):
    """Parsing argument has failed."""


class CheckFailed(CommandException):
    """Command check has failed."""
