import re

from abc import ABC, abstractmethod
from contextlib import suppress
from typing import TypeVar, Sequence, Generic, Type, Optional, TYPE_CHECKING, List

import dico
from dico.exception import HTTPError

from .utils import search, maybe_fmt

if TYPE_CHECKING:
    from .bot import Bot
    from .context import Context


T = TypeVar("T")


class ConverterBase(ABC, Generic[T]):
    CONVERT_TYPE: Type[T]

    def __init__(self, bot: "Bot"):
        if not hasattr(self, "CONVERT_TYPE"):
            raise TypeError("Converter must have CONVERT_TYPE attribute")
        self.bot: "Bot" = bot
        self.cache_type = self.CONVERT_TYPE._cache_type if hasattr(self.CONVERT_TYPE, "_cache_type") else None

    def dump_from_cache(self, guild_id: Optional[dico.Snowflake] = None) -> List[T]:
        if not self.cache_type:
            raise TypeError("dump_from_cache can only be used with DiscordObjectBase")
        if self.bot.has_cache:
            cache = self.bot.cache if not guild_id else self.bot.cache.get_guild_container(guild_id)
            objects = cache.get_storage(self.cache_type) if cache else []
            return [x["value"] for x in objects] if objects else []
        return []

    def __call__(self, *args, **kwargs):
        return self.convert(*args, **kwargs)

    @abstractmethod
    async def convert(self, ctx: "Context", value: str) -> Optional[T]:
        pass


class UserConverter(ConverterBase):
    CONVERT_TYPE = dico.User

    async def convert(self, ctx: "Context", value: str) -> Optional[T]:
        cached = self.dump_from_cache()
        cached.extend([x.user if isinstance(x, dico.GuildMember) else x for x in ctx.mentions])
        maybe_mention = maybe_fmt(value)
        maybe_id = value if re.match(r"^\d+$", value) else maybe_mention
        with suppress(HTTPError):
            if maybe_id:
                return search(cached, id=maybe_id) or await self.bot.http.request_user(maybe_id)
        from_username = search(cached, username=value)
        if from_username:
            return from_username
        from_fullname = search(cached, __str__=value)
        if from_fullname:
            return from_fullname


class GuildMemberConverter(ConverterBase):
    CONVERT_TYPE =dico. GuildMember

    def __init__(self, bot: "Bot"):
        super().__init__(bot)
        self.cache_type = "member"

    async def convert(self, ctx: "Context", value: str) -> Optional[T]:
        cached = self.dump_from_cache(ctx.guild_id)
        cached.extend([x for x in ctx.mentions if isinstance(x, dico.GuildMember)])
        maybe_mention = maybe_fmt(value)
        maybe_id = value if re.match(r"^\d+$", value) else maybe_mention
        with suppress(HTTPError):
            if maybe_id:
                return search(cached, id=maybe_id) or await self.bot.http.request_user(maybe_id)
        from_name = search(cached, __str__=value)
        if from_name:
            return from_name


class ChannelConverter(ConverterBase):
    CONVERT_TYPE = dico.Channel

    async def convert(self, ctx: "Context", value: str) -> Optional[T]:
        cached = self.dump_from_cache()
        cached.append(ctx.channel)
        maybe_mention = maybe_fmt(value)
        maybe_id = value if re.match(r"^\d+$", value) else maybe_mention
        with suppress(HTTPError):
            if maybe_id:
                return search(cached, id=maybe_id) or await self.bot.http.request_user(maybe_id)
        from_name = search(cached, name=value)
        if from_name:
            return from_name


class RoleConverter(ConverterBase):
    CONVERT_TYPE = dico.Role

    async def convert(self, ctx: "Context", value: str) -> Optional[T]:
        cached = self.dump_from_cache()
        maybe_mention = maybe_fmt(value)
        maybe_id = value if re.match(r"^\d+$", value) else maybe_mention
        with suppress(HTTPError):
            if maybe_id:
                return search(cached, id=maybe_id) or await self.bot.http.request_user(maybe_id)
        from_name = search(cached, name=value)
        if from_name:
            return from_name


AVAILABLE_CONVERTERS = {
    dico.User: UserConverter,
    dico.GuildMember: GuildMemberConverter,
    dico.Channel: ChannelConverter,
    dico.Role: RoleConverter
}
