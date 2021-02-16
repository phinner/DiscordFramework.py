from discord import Client
from traceback import print_exc

from .message import MessageHandler
from .command import CommandHandler
from .guild import GuildManager
from .file import FileManager
from .util import initLogger


class CustomClient(Client):
    def __init__(self, root_directory, **options):
        super().__init__(**options)

        # Set up the vars
        self.started = False

        # Set up the const
        self.DEFAULT_PREFIX = "stp "
        self.DIRECTORY_PATH = root_directory
        self.DATA_PATH = f"{self.DIRECTORY_PATH}\\Data"
        self.CLIENT_PATH = f"{self.DATA_PATH}\\Client"
        self.ACCOUNT_PATH = f"{self.DATA_PATH}\\Accounts"
        self.GUILD_PATH = f"{self.DATA_PATH}\\Guilds"

        # Set up the tools
        self.Logger = initLogger(f"{root_directory}\\Log.log")
        self.FileManager = FileManager(self)
        self.GuildManager = GuildManager(self)
        self.MessageHandler = MessageHandler(self)
        self.CommandHandler = CommandHandler(self)

    async def on_ready(self):
        if not self.started:
            self.FileManager.checkFiles()
            self.FileManager.loadFiles()
            self.started = True
        self.Logger.info(f'The bot have logged in as {self.user}')

    async def on_error(self, event, *args, **kwargs):
        self.Logger.error("{}: {}, {}\n".format(event.upper(), args, kwargs)), print_exc()
