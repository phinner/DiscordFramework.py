from traceback import format_exc
from os import makedirs
from os.path import exists
from discord import Client

from .logger import CustomLogger
from .message import MessageHandler
from .command import CommandManager
from .guild import GuildManager, GuildData

# ------------------------------------------------------------------------------- #

class CustomClient(Client):
    def __init__(self, root, prefix, handlers=None, storage=None, **options):
        """
        The CustomClient is a class that can manage files and use customized managers,
        it only needs a root directory to work.

        You can add more functionalities to your bot by extending the base Manager and Storage classes,
        just update the handlers and/or storage parameters.
        """
        super().__init__(**options)

        # Set up the default settings
        self.DEFAULT_PREFIX = prefix

        # Set up the directories
        self.ROOT = root
        self.DATA_PATH = f"{self.ROOT}\\Data"
        self.CLIENT_PATH = f"{self.DATA_PATH}\\Client"
        self.GUILD_PATH = f"{self.DATA_PATH}\\Guilds"
        self.LOG_PATH = f"{self.DATA_PATH}\\Logs"
        self.API_PATH = f"{self.DATA_PATH}\\API"

        # Checks if they exists
        for directory in [self.ROOT, self.DATA_PATH, self.CLIENT_PATH, self.GUILD_PATH, self.LOG_PATH, self.API_PATH]:
            if not exists(directory):
                makedirs(directory)

        # Set up the handlers
        default_handlers = {
            "logger": CustomLogger,
            "msg": MessageHandler,
            "command": CommandManager,
            "guild": GuildManager
        }

        # Set up the storage classes
        default_storage = {
            "guild": GuildData
        }

        # Add the custom handlers and storage classes
        if handlers is not None: default_handlers.update(handlers)
        if storage is not None: default_storage.update(storage)

        # Initializes the handlers and storage classes
        self.GuildData = default_storage["guild"]
        self.Logger = default_handlers["logger"](self)
        self.GuildManager = default_handlers["guild"](self)
        self.MessageHandler = default_handlers["msg"](self)
        self.CommandManager = default_handlers["command"](self)

    async def on_error(self, event, *args, **kwargs):
        self.Logger.ERROR(f"{event.upper()}: {args}" + (kwargs if kwargs else "") + f"\n{format_exc()}")
