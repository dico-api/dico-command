import io
import typing
import pathlib
from dico import Message, Embed, AllowedMentions, MessageReference


class Context(Message):
    def __init__(self, client, resp, prefix, command, **kwargs):
        super().__init__(client, resp, **kwargs)
        self.prefix = prefix
        self.command = command

    @classmethod
    def from_message(cls, message: Message, prefix, command):
        return cls(message.client, message.raw, prefix, command)

    @property
    def bot(self):
        return self.client

    def send(self,
             content: str = None,
             *,
             embed: typing.Union[Embed, dict] = None,
             file: typing.Union[io.FileIO, pathlib.Path, str] = None,
             files: typing.List[typing.Union[io.FileIO, pathlib.Path, str]] = None,
             tts: bool = False,
             allowed_mentions: typing.Union[AllowedMentions, dict] = None,
             message_reference: typing.Union[Message, MessageReference, dict] = None):
        return self.client.create_message(self.channel, content, embed=embed, file=file, files=files, tts=tts, allowed_mentions=allowed_mentions, message_reference=message_reference)
