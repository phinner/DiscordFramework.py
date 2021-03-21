import json
import pickle
import asyncio
import atexit
import sys

from os import getcwd
from datetime import datetime
from random import choice

from Framework.client import CustomClient
from Framework.API.dropboxAPI import DropboxAPI

# The TaskManager is not bound to the client, it will be used for background IO tasks
from Framework.task import TaskManager
Task = TaskManager(max_workers=2)

# Don't forget to import the commands and readers you created
from .commands import *
from .readers import *

# ------------------------------------------------------------------------------- #

def get_token(file):
    with open(file, 'r') as f:
        return f.readline()

# ------------------------------------------------------------------------------- #

class ParkingBotClient(CustomClient):
    def __init__(self, root, prefix, handlers=None, storage=None, **options):
        super().__init__(root, prefix, handlers=handlers, storage=storage, **options)

        # I'll use this boolean to make sure the bot don't overwrites the data if he disconnects
        self.started = False

        # Pre-made kwarg for error messages
        self.error_kwargs = {"delete_after": 5}

        # atexit registers functions to be called when the program exits
        atexit.register(self.Logger.INFO, "The bot has exit.")

        # Let's add an API
        self.API = dict()

        self.API["dbx"] = DropboxAPI(self, "Example\\Data\\API\\dropbox_secret.json")

    # --------------------------------------------------------------------------- #

    def initTasks(self):
        task_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(task_loop)


        @Task.scheduledTask(minutes=30, loop=task_loop, start={"minute": datetime.now().minute + 10})
        async def backup_data():
            await self.wait_until_ready()
            self.GuildManager.saveGuildDirectory()
            self.Logger.INFO("Data have been successfully saved.")


        @Task.scheduledTask(hours=1, loop=task_loop)
        async def updateMemes():
            await self.wait_until_ready()

            self.API["dbx"].checkFileSharing()
            memes = self.API["dbx"].makeLinkDict()

            with open(f"{self.CLIENT_PATH}\\memes.json", "w", encoding="utf-8") as file:
                file.write(json.dumps(memes, indent=2))

            with open(f"{self.CLIENT_PATH}\\memes.pickle", "wb") as file:
                infos = dict()
                infos["categories"] = [key for key, value in memes.items() if type(value) != str]
                file.write(pickle.dumps(infos))

            self.Logger.INFO("Fresh memes for a good year...")


        task_loop.run_forever()

    # --------------------------------------------------------------------------- #

    async def handle_commands(self, command_name, msg):
        # Handle the commands by iterating through the indexes, names and then aliases
        if command_name in self.CommandManager.Index:
            if not self.CommandManager.Index[command_name].enabled:
                return await msg.channel.send(f"`{command_name}` is currently disabled.", **self.error_kwargs)
            return await self.CommandManager.Index[command_name].function(self, msg, self.MessageHandler.getArgs(msg))
        await msg.channel.send(f"`{command_name}` is an invalid command.", **self.error_kwargs)

    async def handle_readers(self, msg):
        # Respond to the user when the bot finds the corresponding keywords
        for reader in self.MessageHandler.Categories["Reaction"]:
            if not reader.enabled:
                continue

            # Triggers the reader if it have no keywords, or the keywords have been detected
            if reader.keywords is None or reader.detector(msg, reader.keywords):
                if reader.function is not None:
                    return await reader.function(self, msg)
                elif reader.quotes is not None:
                    return await msg.channel.send(choice(reader.quotes))

    # --------------------------------------------------------------------------- #

    async def on_message(self, msg):
        # This if statement prevent the bot to read it's own messages
        if msg.author.id == self.user.id:
            return

        if self.MessageHandler.hasPrefix(msg):
            await self.handle_commands(self.MessageHandler.getCommand(msg), msg)
        elif msg.content == f"<@!{self.user.id}>":
            # If the bot is pinged, it sends it's prefix
            await msg.channel.send(f"Mon préfixe est `{self.GuildManager.Index[str(msg.guild.id)].prefix}`")
        else:
            await self.handle_readers(msg)

    async def on_ready(self):
        if not self.started:
            self.GuildManager.checkGuildDirectory()
            self.GuildManager.loadGuildDirectory()

            future = Task.submit(self.initTasks)
            future.add_done_callback(self.traceFuture)

            self.started = True
        self.Logger.INFO(f'The bot have logged in as {self.user}')

    def traceFuture(self, future):
        self.Logger.TRACE(f"{future.__name__!r} > {future.result()}")

    def getDisplayColour(self, msg):
        return msg.guild.get_member(self.user.id).roles[-1].colour

# ------------------------------------------------------------------------------- #

if __name__ == "__main__":

    main_loop = asyncio.get_event_loop()
    asyncio.set_event_loop(main_loop)

    client = ParkingBotClient(f"{getcwd()}\\Example", "stp ", loop=main_loop)

    try:
        main_loop.run_until_complete(
            client.start(get_token("Example\\Data\\Client\\discord_token.txt"), bot=True, reconnect=True)
        )
    except KeyboardInterrupt:
        main_loop.run_until_complete(
            client.close()
        )
    finally:
        main_loop.close()
        Task.shutdown(wait=False)
