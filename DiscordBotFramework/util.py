from datetime import timedelta, datetime
from asyncio import sleep
from discord.ext import tasks


"""
Old logger

def initLogger(path):
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s[%(levelname)s]> %(msg)s", datefmt="[%Y-%m-%d][%H:%M:%S]")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger
"""


def isDiscordID(name):
    # Discord IDs are the same for servers, users, channels, ...
    if (len(name := str(name)) == 17 or 18) and name.isdigit():
        return True
    return False


def scheduledFunction(timer, start=None):
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
                while now >= future:
                    future += timedelta(start)
                sleep_time = (future - now).seconds
            await sleep(sleep_time)

        func.start()
        return sub_wrapper
    return wrapper
