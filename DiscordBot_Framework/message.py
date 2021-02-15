from random import choice

from .util import isDiscordID


class AutoRespond(object):
    def __init__(self, quotes, func=None, *keywords):
        self.keywords = keywords
        self.quotes = quotes
        self.func = func

    def register(self):
        MessageHandler.MessageReactions.append(self)

    def unregister(self):
        if self in MessageHandler.MessageReactions:
            MessageHandler.MessageReactions.pop(self)


class MessageHandler(object):
    MessageReactions = list()

    def __init__(self, client):
        self.client = client

    async def sendMessage(self, channel, msg, *args):
        if isDiscordID(channel):
            channel = self.client.get_channel(int(channel))
        await channel.send(content=msg, *args)

    def autoResponse(self, msg):
        # Respond to the user when the bot finds the corresponding keywords
        for auto in self.MessageReactions:
            if auto.func is None:
                if all(keyword in msg.content for keyword in auto.keywords):
                    self.sendMessage(msg.channel, choice(auto.quotes))
                    break
            else:
                auto.func(self.client, msg)

    def havePrefix(self, msg):
        return msg.content.startswith(self.client.GuildManager.guilds[str(msg.guild.id)].prefix)

    def getCommand(self, msg):
        return msg.content[len(self.client.GuildManager.guilds[str(msg.guild.id)].prefix):].split(" ", 1)[0]

    def getArgs(self, msg):
        data = msg.content[len(self.client.GuildManager.guilds[str(msg.guild.id)].prefix):].split(" ", 1)
        if len(data) == 1:
            data.append(None)
        return data[1]
