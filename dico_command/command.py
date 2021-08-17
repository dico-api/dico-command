import typing
from .context import Context
from .utils import read_function


class Command:
    def __init__(self,
                 func,
                 name: str,
                 checks: typing.List[typing.Callable[[Context], bool]] = None):
        self.func = func
        self.name = name
        self.checks = checks or []

        self.args_data = read_function(self.func)
        if hasattr(func, "_checks"):
            self.checks.extend(func._checks)

    def evaluate_checks(self, ctx: Context):
        resp = [n for n in [x(ctx) for x in self.checks] if not n]
        return not resp

    def invoke(self, ctx: Context, *args, **kwargs):
        if not self.evaluate_checks(ctx):
            raise
        return self.func(ctx, *args, **kwargs)
