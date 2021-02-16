from random import choice
from inspect import stack

from .util import isDiscordID


class AutoReader(object):
    def __init__(self, name, keywords, quotes, function=None):
        self.name = name
        self.quotes = quotes
        self.keywords = keywords
        self.function = function

        if type(self.keywords) is None:
            self.keywords = str()
        if type(self.quotes) is None:
            self.quotes = str()

        if type(self.keywords) is str:
            self.keywords = [self.keywords]
        if type(self.quotes) is str:
            self.quotes = [self.quotes]

        self.enabled = True

    async def __call__(self, client, message):
        if self.function is None:
            await client.MessageHandler.sendMessage(message.channel, choice(self.quotes))
        else: await self.function(client, message)


class MessageHandler(object):
    MessageReactions = dict()

    def __init__(self, client, error_message_timer=None):
        self.client = client
        self.systemMessageTimer = error_message_timer

    async def __call__(self, message):
        # Respond to the user when the bot finds the corresponding keywords
        for auto in self.MessageReactions.values():
            print(auto, auto.name, auto.function)
            if not auto.enabled:
                continue
            if auto.function is not None:
                return await auto(self.client, message)
            elif all(keyword in message.content for keyword in auto.keywords):
                return await auto(self.client, message)

    async def sendMessage(self, channel, msg, **kwargs):
        if isDiscordID(channel):
            channel = self.client.get_channel(int(channel))
        await channel.send(content=msg, **kwargs)

    async def sendErrMessage(self, channel, msg, **kwargs):
        await self.sendMessage(channel, msg, delete_after=self.systemMessageTimer, **kwargs)

    def havePrefix(self, msg):
        return msg.content.startswith(self.client.GuildManager.guilds[str(msg.guild.id)].prefix)

    def getCommand(self, msg):
        return msg.content[len(self.client.GuildManager.guilds[str(msg.guild.id)].prefix):].split(" ", 1)[0]

    def getArgs(self, msg):
        data = msg.content[len(self.client.GuildManager.guilds[str(msg.guild.id)].prefix):].split(" ", 1)
        if len(data) == 1: data.append(None)
        return data[1]

    @classmethod
    def registerAutoReader(cls, **kwargs):
        def wrapper(function):
            print(kwargs, function)
            react = AutoReader(**kwargs, function=function)

            # Makes sure there are no duplicates
            if react.name in cls.MessageReactions:
                raise IndexError(f"{react.name} already exists in the command index.")

            # Updates the reaction index
            cls.MessageReactions.update({react.name: react})

        # Checks if the function is called as a decorator
        if any(line.startswith('@') for line in stack(context=2)[1].code_context):
            return wrapper
        else: wrapper(None)

    @classmethod
    def unregisterAutoReader(cls, name):
        if name in cls.MessageReactions:
            cls.MessageReactions.pop(name)
        else: raise IndexError(f"{name} not found.")
