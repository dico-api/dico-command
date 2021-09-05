import typing
from .context import Context
from .exception import CheckFailed
from .utils import read_function, is_coro


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
        self.addon = None

    def register_addon(self, addon):
        self.addon = addon

    async def evaluate_checks(self, ctx: Context):
        resp = [n for n in [(await x(ctx)) if is_coro(x) else x(ctx) for x in self.checks] if not n]
        return not resp

    async def invoke(self, ctx: Context, *args, **kwargs):
        if not await self.evaluate_checks(ctx):
            raise CheckFailed
        init_args = (ctx,) if self.addon is None else (self.addon, ctx)
        return await self.func(*init_args, *args, **kwargs)


def command(name: str = None):
    def wrap(func):
        return Command(func, name)
    return wrap
