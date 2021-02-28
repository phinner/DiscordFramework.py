from discord import Client
from traceback import print_exc
from os import makedirs
from os.path import exists


from .logger import CustomLogger
from .message import MessageHandler
from .command import CommandManager
from .guild import GuildManager, GuildData


class CustomClient(Client):
    def __init__(self, root_directory, handlers=None, storage=None, **options):
        super().__init__(**options)

        # Set up the const
        self.DEFAULT_PREFIX = "stp "
        self.DIRECTORY_PATH = root_directory
        self.DATA_PATH = f"{self.DIRECTORY_PATH}\\Data"
        self.CLIENT_PATH = f"{self.DATA_PATH}\\Client"
        self.ACCOUNT_PATH = f"{self.DATA_PATH}\\Accounts"
        self.GUILD_PATH = f"{self.DATA_PATH}\\Guilds"
        self.LOG_PATH = f"{self.DATA_PATH}\\Logs"

        # Checks the root directories
        for directory in [self.CLIENT_PATH, self.ACCOUNT_PATH, self.GUILD_PATH, self.LOG_PATH]:
            if not exists(directory):
                makedirs(directory)

        # Set up the tools
        default_handlers = {
            "logger": CustomLogger,
            "msg": MessageHandler,
            "command": CommandManager,
            "guild": GuildManager
        }

        default_storage = {
            "guild": GuildData
        }

        if handlers is not None: default_handlers.update(handlers)
        if storage is not None: default_storage.update(storage)

        self.GuildData = default_storage["guild"]

        self.Logger = default_handlers["logger"](self)
        self.GuildManager = default_handlers["guild"](self)
        self.MessageHandler = default_handlers["msg"](self)
        self.CommandManager = default_handlers["command"](self)

    async def on_error(self, event, *args, **kwargs):
        self.Logger.ERROR("{}: {}, {}".format(event.upper(), args, kwargs))
        print_exc()
