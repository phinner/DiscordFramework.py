from discord import Client
from traceback import print_exc
from asyncio import sleep
from discord.ext import tasks
from datetime import datetime, timedelta
from os import makedirs
from os.path import exists


from .logger import CustomLogger
from .message import MessageHandler
from .command import CommandHandler, Command
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
            "command": CommandHandler,
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
        self.CommandHandler = default_handlers["command"](self)

    async def on_error(self, event, *args, **kwargs):
        self.Logger.ERROR("{}: {}, {}\n".format(event.upper(), args, kwargs))
        print_exc()

    def scheduledFunction(self, timer, start=None):
        """
        This function is for scheduling functions to start at a certain hour or date
        check https://docs.python.org/3/library/datetime.html to know how to format the inputted dictionary
        :param timer: Dictionary containing the time between the function calls
        :param start: Dictionary containing the start date
        """
        def wrapper(func):
            default_kwargs = {
                'seconds': 0,
                'minutes': 0,
                'hours': 0,
                'count': None,
                'reconnect': True,
                'loop': None
            }

            default_kwargs.update(timer)
            func = tasks.Loop(func, **default_kwargs)

            async def sub_wrapper(*func_args, **func_kwargs):
                return func(*func_args, **func_kwargs)

            @func.before_loop
            async def before_func():
                await self.wait_until_ready()
                if start is None:
                    sleep_time = 0
                else:
                    now = datetime.now()
                    future_kwargs = {
                        "year": now.year,
                        "month": now.month,
                        "day": now.day,
                        "hour": now.hour,
                        "minute": now.minute
                    }

                    future_kwargs.update(start)
                    future = datetime(**future_kwargs)
                    if now >= future:
                        future += timedelta(days=1)
                    sleep_time = (future - now).seconds
                await sleep(sleep_time)

            func.start()
            return sub_wrapper
        return wrapper
