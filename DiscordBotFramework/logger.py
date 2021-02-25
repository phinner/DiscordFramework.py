from os import path
from time import gmtime, strftime


class CustomLogger(object):
    def __init__(self, client, daily_log=True, console_print=True, time_format=None):
        """
        Logs information about the bot activity
        """
        self.levels = {
            "TRACE": True,
            "DEBUG": True,
            "INFO": True,
            "WARNING": True,
            "ERROR": True,
            "EXCEPTION": True,
            "CRITICAL": True
        }

        self.client = client
        self.message = "{time}[{level}]> {msg}"
        self._daily_log = daily_log
        self._time_format = None
        self._console_print = console_print

        if time_format is None:
            self._time_format = "[%Y-%m-%d][%H:%M:%S]"

    @property
    def daily_log(self):
        """
        daily_log is a boolean, if it's True the bot will split his logs by changing the log file every 24 hours.
        """
        return self._daily_log

    @daily_log.setter
    def daily_log(self, value):
        if type(value) is bool:
            self._daily_log = value
        else: TypeError(f"{value} is not a boolean.")

    @property
    def console_print(self):
        """
        console_print is a boolean, if it's True the logger will print the log in the console
        """
        return self._daily_log

    @console_print.setter
    def console_print(self, value):
        if type(value) is bool:
            self._console_print = value
        else: TypeError(f"{value} is not a boolean.")

    @property
    def time_formatter(self):
        """
        time_format is the way time is displayed when the bot logs,
        check https://docs.python.org/3/library/time.html#time.strftime to see how to modify it.
        """
        return self._time_format

    @time_formatter.setter
    def time_formatter(self, value):
        if type(value) is str:
            self._daily_log = value
        else: TypeError(f"{value} is not a string.")

    def getLogFile(self):
        file_name = f"{self.client.LOG_PATH}\\{strftime('%d-%m-%Y', gmtime()) if self._daily_log else 'Log'}.log"
        if not path.isfile(file_name): open(file_name, "w").close()
        return file_name

    def log(self, level, message):
        if not self.levels[level]:
            return

        with open(self.getLogFile(), "a") as file:
            log_message = self.message.format(level=level, msg=message, time=strftime(self._time_format, gmtime()))
            file.write(log_message + "\n")

        if self.console_print: print(log_message)

    def TRACE(self, message):
        self.log("TRACE", message)

    def DEBUG(self, message):
        self.log("DEBUG", message)

    def INFO(self, message):
        self.log("INFO", message)

    def WARNING(self, message):
        self.log("WARNING", message)

    def ERROR(self, message):
        self.log("ERROR", message)

    def EXCEPTION(self, message):
        self.log("EXCEPTION", message)

    def CRITICAL(self, message):
        self.log("CRITICAL", message)
