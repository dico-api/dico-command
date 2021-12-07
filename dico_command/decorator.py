import typing
from .command import Command
from .context import Context


def checks(*funcs: typing.Callable[[Context], typing.Union[bool, typing.Awaitable[bool]]]):
    def wrap(maybe_cmd):
        if isinstance(maybe_cmd, Command):
            maybe_cmd.checks.extend(funcs)
        else:
            if hasattr(maybe_cmd, "_checks"):
                maybe_cmd._checks.extend(funcs)
            else:
                maybe_cmd._checks = [*funcs]
        return maybe_cmd
    return wrap


async def __is_owner(ctx: Context):
    return await ctx.bot.is_owner(ctx)


def is_owner():
    return checks(__is_owner)

