import typing
from .context import Context
from .exception import CheckFailed, InvalidArgument
from .utils import read_function, is_coro, smart_split


class Command:
    def __init__(self,
                 func,
                 name: str,
                 checks: typing.Optional[typing.List[typing.Callable[[Context], bool]]] = None,
                 aliases: typing.Optional[typing.List[str]] = None):
        self.func = func
        self.name = name
        self.checks = checks or []
        self.aliases = aliases or []
        self.subcommands = {}
        self.error_handler = None

        self.args_data = read_function(self.func)
        if hasattr(func, "_checks"):
            self.checks.extend(func._checks)
        self.addon = None

    def subcommand(self, *args, **kwargs):
        def wrap(coro):
            cmd = command(*args, **kwargs)(coro)
            self.subcommands[cmd.name] = cmd
            return cmd
        return wrap

    def register_addon(self, addon):
        self.addon = addon

    async def execute_error_handler(self, ctx, ex):
        if not self.error_handler:
            return False
        args = (self.addon, ctx, ex) if self.addon else (ctx, ex)
        return await self.error_handler(*args)

    def on_error(self, coro):
        self.error_handler = coro
        return coro

    async def evaluate_checks(self, ctx: Context):
        if self.addon and not await self.addon.addon_check(ctx):
            return False
        resp = [n for n in [(await x(ctx)) if is_coro(x) else x(ctx) for x in self.checks] if not n]
        return not resp

    async def invoke(self, ctx: Context, *args, **kwargs):
        if not await self.evaluate_checks(ctx):
            raise CheckFailed
        tgt = self.func
        args = [*args]
        subcommand_invoking = False
        subcommand_name = None
        subcommand = None
        if self.subcommands:
            if args and args[0] in self.subcommands:
                subcommand = self.subcommands[args[0]]
                tgt = subcommand.invoke
                del args[0]
                subcommand_invoking = True
            elif kwargs and [*kwargs.values()][0] in self.subcommands:
                subcommand = kwargs.pop([*kwargs.keys()][0])
                tgt = subcommand.invoke
                subcommand_invoking = True
            elif kwargs or args:
                raise InvalidArgument("unknown subcommand or invalid argument passed.")
        elif (args or kwargs) and not self.args_data:
            raise InvalidArgument("invalid argument data.")
        if subcommand_invoking:
            ctx.subcommand_name = subcommand_name
            msg = ctx.content
            ipt = msg.split(maxsplit=1)
            ipt = ipt[1].split(maxsplit=1) if len(ipt) > 1 else []
            args, kwargs = smart_split(ipt[1] if len(ipt) > 1 else "", subcommand.args_data, subcommand=bool(subcommand.subcommands))
        init_args = (ctx,) if self.addon is None or subcommand_invoking else (self.addon, ctx)
        return await tgt(*init_args, *args, **kwargs)


def command(name: typing.Optional[str] = None, *, aliases: typing.Optional[typing.List[str]] = None):
    def wrap(func):
        return Command(func, name, aliases=aliases)
    return wrap
