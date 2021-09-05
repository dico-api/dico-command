import typing
from .command import Command

if typing.TYPE_CHECKING:
    from .bot import Bot


class Listener:
    def __init__(self, func, event: str):
        self.__func = func
        self.event = event
        self.addon = None

    def register_addon(self, addon):
        self.addon = addon

    async def func(self, *args, **kwargs):
        args = (self.addon, *args)
        return await self.__func(*args, **kwargs)


def on(event: str = None):
    def wrap(func):
        listener = Listener(func, event or func.__name__)
        return listener
    return wrap


class Addon:
    name: str

    def __init_subclass__(cls, **kwargs):
        cls.name = kwargs.get("name", cls.__name__)

    def __init__(self, bot: "Bot"):
        self.bot = bot
        resp = [getattr(self, x) for x in dir(self)]
        self.commands: typing.List[Command] = [x for x in resp if isinstance(x, Command)]
        self.listeners: typing.List[Listener] = [x for x in resp if isinstance(x, Listener)]

    def __str__(self):
        return self.name
