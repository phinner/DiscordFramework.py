from os import getcwd
from datetime import datetime
import atexit

from DiscordBotFramework.client import CustomClient
from DiscordBotFramework.util import scheduledFunction

# Don't forget to import the commands and readers you created
from .commands import *
from .readers import *

# Let's have fun with the Google drive API
from .API.google_drive import DriveAPI


def get_token(file):
    with open(file, 'r') as f:
        return f.readline()


class ParkingBotClient(CustomClient):
    def __init__(self, root_directory, handlers=None, storage=None, **options):
        super().__init__(root_directory, handlers=handlers, storage=storage, **options)

        # I'll use this boolean to make sure the bot don't overwrites the data if he disconnects
        self.started = False

        # Pre-made kwarg for error messages
        self.error_kwargs = {"delete_after": 5}

        # atexit registers functions to be called when the program exits
        atexit.register(self.Logger.INFO, "The bot has exit.")

        # Let's add some APIs to make some special commands
        self.API = dict()

        # If modifying these scopes, delete your previously saved credentials
        # at ~/.credentials/drive-python-quickstart.json
        SCOPES = 'https://www.googleapis.com/auth/drive'
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Drive API Python Quickstart'
        self.API["drive"] = DriveAPI(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)

        # This dict is for the meme folders located in my google drive
        self.meme_dict = dict()
        self.update_meme_dict()

    def update_meme_dict(self):
        self.meme_dict = self.API["drive"].searchFile(
            100, "'178LIjcRlbHQQy4r4_SHU-qcepTWuZRgm' in parents", "id, name, mimeType"
        )

        # The following code pack the folders name and id to make a dict {name: id}
        self.meme_dict = dict(
            zip([file["name"].casefold() for file in self.meme_dict
                if file["mimeType"] == "application/vnd.google-apps.folder"],

                [file["id"] for file in self.meme_dict
                if file["mimeType"] == "application/vnd.google-apps.folder"])
        )

        # Don't forget the root directory
        self.meme_dict.update({"all": "178LIjcRlbHQQy4r4_SHU-qcepTWuZRgm"})

    async def on_ready(self):
        if not self.started:
            self.GuildManager.checkGuildDirectory()
            self.GuildManager.loadGuildDirectory()
            self.started = True
        self.Logger.INFO(f'The bot have logged in as {self.user}')

    async def handle_commands(self, command_name, msg):
        # Handle the commands by iterating through the indexes, names and then aliases
        for index in [self.CommandManager.commandNames, self.CommandManager.commandAliases]:
            if command_name in index:
                if not index[command_name].enabled:
                    return await msg.channel.send(f"`{command_name}` is currently disabled.", **self.error_kwargs)
                return await index[command_name].function(self, msg, self.MessageHandler.getArgs(msg))
        await msg.channel.send(f"`{command_name}` is an invalid command.", **self.error_kwargs)

    async def handle_readers(self, msg):
        # Respond to the user when the bot finds the corresponding keywords
        for reader in self.MessageHandler.MessageReaders.values():
            if not reader.enabled:
                continue
            if reader.keywords is None or reader.detector(msg, reader.keywords):
                if reader.function is not None:
                    return await reader.function(self, msg)
                else:
                    return await msg.channel.send(choice(reader.quotes) if type(reader.quotes) == list else None)

    async def on_message(self, msg):
        # This if statement prevent the bot to read it's own messages
        if msg.author.id == self.user.id:
            return

        if msg.channel.id == 807365066361405470:  # This ID is our test channel
            if self.MessageHandler.hasPrefix(msg):
                await self.handle_commands(self.MessageHandler.getCommand(msg), msg)
            elif msg.content == f"<@!{self.user.id}>":
                # If the bot is pinged, it sends it's prefix
                await msg.channel.send(f"Mon préfixe est `{self.GuildManager.guildIndex[str(msg.guild.id)].prefix}`")
            else:
                await self.handle_readers(msg)

    @atexit.register
    @scheduledFunction(timer={"minutes": 30}, start={"minute": datetime.now().minute + 11})
    async def backup_data(self):
        await self.wait_until_ready()
        self.GuildManager.saveGuildDirectory()
        self.Logger.INFO("Data have been successfully saved.")

    @atexit.register
    @scheduledFunction(timer={"minutes": 15}, start={"minute": datetime.now().minute + 10})
    async def update_data(self):
        await self.wait_until_ready()
        self.update_meme_dict()
        self.Logger.INFO("Data have been updated.")


client = ParkingBotClient(getcwd())
client.run(get_token("Example\\discord_token.txt"))
