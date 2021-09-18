import typing
from dico import Message, Embed, AllowedMentions, MessageReference, Component
from dico.model.extras import FILE_TYPE


class Context(Message):
    def __init__(self, client, resp, prefix, command, name_used, **kwargs):
        super().__init__(client, resp, **kwargs)
        self.prefix = prefix
        self.command = command
        self.name_used = name_used
        self.subcommand_name = None

    @classmethod
    def from_message(cls, message: Message, prefix, command, name_used):
        return cls(message.client, message.raw, prefix, command, name_used)

    @property
    def bot(self):
        return self.client

    def send(self,
             content: str = None,
             *,
             embed: typing.Union[Embed, dict] = None,
             embeds: typing.List[typing.Union[Embed, dict]] = None,
             file: FILE_TYPE = None,
             files: typing.List[FILE_TYPE] = None,
             tts: bool = False,
             allowed_mentions: typing.Union[AllowedMentions, dict] = None,
             message_reference: typing.Union[Message, MessageReference, dict] = None,
             component: typing.Union[dict, Component] = None,
             components: typing.List[typing.Union[dict, Component]] = None):
        return self.client.create_message(self.channel,
                                          content,
                                          embed=embed,
                                          embeds=embeds,
                                          file=file,
                                          files=files,
                                          tts=tts,
                                          allowed_mentions=allowed_mentions,
                                          message_reference=message_reference,
                                          component=component,
                                          components=components)
