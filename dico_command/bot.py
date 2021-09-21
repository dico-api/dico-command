import typing
import inspect
import logging
import traceback
import importlib
import dico
from .command import Command
from .context import Context
from .exception import *
from .utils import smart_split, is_coro

if typing.TYPE_CHECKING:
    from .addon import Addon


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
        self.aliases = {}
        self.logger = logging.Logger("dico_command")
        self.on("MESSAGE_CREATE", self.execute_handler)
        self.addons: typing.List[Addon] = []
        self.addon_names: typing.List[str] = []
        self.modules: typing.List[str] = []

    async def get_owners(self) -> typing.List[dico.Snowflake]:
        if not self.application:
            await self.request_current_bot_application_information()
        return self.application.owner_ids if self.application.owner_ids else [self.application.owner.id]

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
        if not cont:
            return
        prefix_result = await self.verify_prefix(message)
        if prefix_result is None:
            return
        raw_ipt = cont[len(prefix_result):]
        if not raw_ipt:
            return
        ipt = raw_ipt.split(maxsplit=1)
        if not ipt:
            return
        name = ipt[0]
        cmd = self.commands.get(self.aliases.get(name, name))
        if not cmd:
            return
        context = Context.from_message(message, prefix_result, cmd, name)
        try:
            try:
                args, kwargs = smart_split(ipt[1] if len(ipt) > 1 else "", cmd.args_data, subcommand=bool(cmd.subcommands))
            except Exception as ex:
                raise InvalidArgument from ex
            self.logger.debug(f"Command {name} executed.")
            await cmd.invoke(context, *args, **kwargs)
        except Exception as ex:
            await self.handle_command_error(context, ex)

    def add_command(self, command: Command):
        if command.name in self.commands:
            raise CommandAlreadyExists(name=command.name)
        self.commands[command.name] = command
        for x in command.aliases:
            if x in self.aliases:
                raise CommandAlreadyExists(name=x)
            self.aliases[x] = command.name
        return command

    def remove_command(self, name: str):
        if name not in self.commands:
            return
        command = self.commands.pop(name)
        for x in command.aliases:
            if x in self.aliases:
                del self.aliases[x]

    def command(self, name: typing.Optional[str] = None, *, aliases: typing.Optional[typing.List[str]] = None):
        def wrap(func):
            cmd = Command(func, name or func.__name__, aliases=aliases)
            self.add_command(cmd)
            return cmd
        return wrap

    async def handle_command_error(self, context, ex):
        if await context.command.execute_error_handler(context, ex):
            return
        if context.command.addon and await context.command.addon.on_addon_command_error(context, ex):
            return
        if not self.events.get("COMMAND_ERROR"):
            self.logger.error(f"Error while executing command '{context.command.name}':\n"+''.join(traceback.format_exception(type(ex), ex, ex.__traceback__)))
        else:
            self.dispatch("command_error", context, ex)

    def load_addons(self, *addons: typing.Type["Addon"]):
        for x in addons:
            if x.name in self.addon_names:
                raise AddonAlreadyLoaded(name=x.name)
            self.addon_names.append(x.name)
            loaded = x(self)
            self.addons.append(loaded)
            for c in loaded.commands:
                c.register_addon(loaded)
                self.add_command(c)
            for e in loaded.listeners:
                e.register_addon(loaded)
                self.on_(e.event, e.func)
            if hasattr(self, "interaction"):
                for t in loaded.interactions:
                    t.register_self_or_cls(loaded)
                    self.interaction.add_command(t)
                for cc in loaded.callbacks:
                    cc.register_self_or_cls(loaded)
                    self.interaction.add_callback(cc)

    def unload_addons(self, *addons: typing.Union[str, typing.Type["Addon"]]):
        for x in addons:
            tgt = x if isinstance(x, str) else x.name
            for i, n in enumerate(self.addon_names):
                if n == tgt:
                    del self.addon_names[i]
                    addon = self.addons.pop(i)
                    for c in addon.commands:
                        self.remove_command(c.name)
                    for e in addon.listeners:
                        event_name = e.event.upper().lstrip("ON_")
                        if self.events.get(event_name):
                            self.events.remove(event_name, e.func)
                    if hasattr(self, "interaction"):
                        for t in addon.interactions:
                            self.interaction.remove_command(t)
                        for cc in addon.callbacks:
                            self.interaction.remove_callback(cc)
                    addon.on_unload()

    def load_module(self, import_path: str):
        try:
            module = importlib.import_module(import_path)
            importlib.reload(module)
            if module.__name__ in self.modules:
                raise ModuleAlreadyLoaded(path=import_path)
            self.modules.append(module.__name__)
            if hasattr(module, "load"):
                module.load(self)
            else:
                raise MissingLoadFunction(path=import_path)
        except ImportError:
            raise InvalidModule(path=import_path)

    def unload_module(self, import_path: str):
        try:
            module = importlib.import_module(import_path)
            if module.__name__ in self.modules:
                if hasattr(module, "unload"):
                    module.unload(self)
                    self.modules.remove(module.__name__)
                else:
                    raise MissingUnloadFunction(path=import_path)
            else:
                raise ModuleNotLoaded(path=import_path)
        except ImportError:
            raise InvalidModule(path=import_path)

    def reload_module(self, import_path: str):
        self.unload_module(import_path)
        self.load_module(import_path)
