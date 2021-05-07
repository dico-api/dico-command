import dico
from .command import Command


class Bot(dico.Client):
    def __init__(self,
                 token: str, *,
                 prefix: str = None,
                 intents: dico.Intents = dico.Intents.no_privileged(),
                 default_allowed_mentions: dico.AllowedMentions = None,
                 loop=None,
                 cache: bool = True):
        super().__init__(token, intents=intents, default_allowed_mentions=default_allowed_mentions, loop=loop, cache=cache)
        self.prefix = prefix

    async def execute_handler(self, message: dico.Message):
        if message.content.startswith(self.prefix):
            pass

    def command(self, name: str = None):
        def wrap(func):
            return Command(func, name or func.__name__)
        return wrap
