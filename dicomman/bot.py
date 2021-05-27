import typing
import logging
import traceback
import dico
from .command import Command
from .context import Context


class Bot(dico.Client):
    def __init__(self,
                 token: str,
                 prefix: str, *,
                 intents: dico.Intents = dico.Intents.no_privileged(),
                 default_allowed_mentions: dico.AllowedMentions = None,
                 loop=None,
                 cache: bool = True):
        super().__init__(token, intents=intents, default_allowed_mentions=default_allowed_mentions, loop=loop, cache=cache)
        self.prefix = prefix
        self.commands = {}
        self.logger = logging.Logger("dicomman")
        self.on("MESSAGE_CREATE", self.execute_handler)

    async def execute_handler(self, message: dico.Message):
        if not message.content.startswith(self.prefix):
            return
        ipt = message.content.lstrip(self.prefix).split()
        name = ipt.pop(0)
        cmd = self.commands.get(name)
        if not cmd:
            return
        context = Context.from_message(message)
        try:
            await cmd.invoke(context, *ipt)
            self.logger.debug(f"Command {name} executed.")
        except Exception as ex:
            self.dispatch("command_error", context, ex)

    def add_command(self, func: typing.Callable, name: str = None):
        name = name or func.__name__
        cmd = Command(func, name)
        self.commands[name] = cmd
        return cmd

    def command(self, name: str = None):
        def wrap(func):
            return self.add_command(func, name)
        return wrap
