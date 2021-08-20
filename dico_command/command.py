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

    async def evaluate_checks(self, ctx: Context):
        resp = [n for n in [(await x(ctx)) if is_coro(x) else x(ctx) for x in self.checks] if not n]
        return not resp

    async def invoke(self, ctx: Context, *args, **kwargs):
        if not await self.evaluate_checks(ctx):
            raise CheckFailed
        return await self.func(ctx, *args, **kwargs)
