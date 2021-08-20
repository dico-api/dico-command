import typing
import inspect
import logging
import traceback
import dico
from .command import Command
from .context import Context
from .exception import InvalidArgument
from .utils import smart_split, is_coro


class Bot(dico.Client):
    def __init__(self,
                 token: str,
                 prefix: typing.Union[str, list, typing.Callable[[dico.Message], typing.Union[typing.Awaitable[str], str]]],
                 *,
                 intents: dico.Intents = dico.Intents.no_privileged(),
                 default_allowed_mentions: dico.AllowedMentions = None,
                 loop=None,
                 cache: bool = True):
        super().__init__(token, intents=intents, default_allowed_mentions=default_allowed_mentions, loop=loop, cache=cache)
        self.prefixes = [prefix] if not isinstance(prefix, list) else prefix
        self.commands = {}
        self.logger = logging.Logger("dico_command")
        self.on("MESSAGE_CREATE", self.execute_handler)

    async def verify_prefix(self, message: dico.Message):
        final_prefixes = [(await x(message)) if is_coro(x) else x(message) if inspect.isfunction(x) else x for x in self.prefixes]
        prefix_result = [*map(lambda x: message.content.startswith(x), final_prefixes)]
        if len(set(prefix_result)) != 2 and False in prefix_result:
            return
        for i, r in enumerate(prefix_result):
            if r is True:
                return final_prefixes[i]

    async def execute_handler(self, message: dico.Message):
        cont = message.content
        prefix_result = await self.verify_prefix(message)
        if prefix_result is None:
            return
        raw_ipt = cont[len(prefix_result):]
        ipt = raw_ipt.split(maxsplit=1)
        name = ipt[0]
        cmd = self.commands.get(name)
        if not cmd:
            return
        context = Context.from_message(message, prefix_result, cmd)
        try:
            try:
                args, kwargs = smart_split(ipt[1] if len(ipt) > 1 else "", cmd.args_data)
            except Exception as ex:
                raise InvalidArgument from ex
            self.logger.debug(f"Command {name} executed.")
            await cmd.invoke(context, *args, **kwargs)
        except Exception as ex:
            self.handle_command_error(context, ex)

    def add_command(self, func: typing.Callable, name: str = None):
        name = name or func.__name__
        cmd = Command(func, name)
        self.commands[name] = cmd
        return cmd

    def command(self, name: str = None):
        def wrap(func):
            return self.add_command(func, name)
        return wrap

    def handle_command_error(self, context, ex):
        if not self.events.get("command_error"):
            self.logger.error(f"Error while executing command '{context.command.name}':\n"+''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
        else:
            self.dispatch("command_error", context, ex)
