from sys import path
from os import getcwd

# Don't forget to import the commands you created in the other script
import tools

path.append('D:\\HDD_Coding\\Gitgud\\DiscordBot-Framework\\DiscordBot_Framework')
from DiscordBotFramework.client import CustomClient


def get_token(file):
    with open(file, 'r') as f:
        return f.readline()


class ParkingBotClient(CustomClient):
    async def on_message(self, msg):
        if msg.author.id == self.user.id:
            return

        if msg.channel.id == 807365066361405470:
            if self.MessageHandler.havePrefix(msg):
                await self.CommandHandler(self.MessageHandler.getCommand(msg), self, msg)
            if msg.content == f"<@!{self.user.id}>":
                await msg.channel.send(f"Mon préfixe est `{self.GuildManager.guilds[str(msg.guild.id)].prefix}`")
            await self.MessageHandler(msg)


client = ParkingBotClient(getcwd())
client.run(get_token("Token.txt"))
