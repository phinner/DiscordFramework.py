import json
import pickle

# --------------------------------------------------------------------------- #

"""
Old logger
Use the logging module

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

# --------------------------------------------------------------------------- #

def isDiscordID(name):
    """
    Test if a given integrer or string is a discord ID.
    Discord IDs are the same for servers, users, channels, ...
    """
    name = str(name)

    if (len(name) == 17 or 18) and name.isdigit():
        return True

    return False

# --------------------------------------------------------------------------- #

def readJSON(path):
    """
    Utility function for the API.
    """
    with open(path, "r") as file:
        return json.load(file)

def readPICKLE(path):
    """
    Utility function for the API.
    """
    with open(path, "rb") as file:
        return pickle.load(file)

# --------------------------------------------------------------------------- #

"""
The old function scheduler

def ScheduledFunction(start=None, **task_kwargs):

    This function is for scheduling functions to start at a certain hour or date,
    check https://docs.python.org/3/library/datetime.html to know how to format the inputted dictionary.
    :param timer: Dictionary containing the time between the functiontion calls
    :param start: Dictionary containing the attributes of the start date

    def wrapper(function):
        if not callable(function):
            raise TypeError("The function is not callable.")

        kwargs = {
            "seconds": 0,
            "minutes": 0,
            "hours": 0,
            "count": None,
            "reconnect": True,
            "loop": None
        }

        kwargs.update(task_kwargs)
        function = tasks.Loop(function, **kwargs)

        @function.before_loop
        async def before_function():
            sleep_time = 0

            if start is not None:
                now = datetime.now()
                keys = ["year", "month", "day", "hour", "minute", "second"]

                future = dict(zip(keys, now.timetuple()))
                future.update(start)

                future = datetime(**future)

                while now >= future:
                    future += timedelta(**{
                        "seconds": kwargs["seconds"],
                        "minutes": kwargs["minutes"],
                        "hours": kwargs["hours"]
                    })

                sleep_time = (future - now).seconds

            await sleep(sleep_time)

        function.start()

        return function
    return wrapper
"""