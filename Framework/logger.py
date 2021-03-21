from os.path import exists
from time import gmtime, strftime


class CustomLogger(object):
    def __init__(self, client):
        """
        Logs information about the bot activity.
        levels can be enabled/disabled.
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
        self._dailylogger = True
        self._console_printer = True
        self._message = "{time}[{level}]> {msg}"
        self._time_formatter = "[%Y-%m-%d][%H:%M:%S]"

    # --------------------------------------------------------------------------- #

    @property
    def dailylogger(self):
        """
        dailylogger is a boolean.
        If it's True, the bot will split it's logs by changing the log file every day.
        The logs are named in the "mm-dd-yyyy.log" format.
        """
        return self._dailylogger

    @dailylogger.setter
    def dailylogger(self, value):
        if type(value) is bool:
            self._dailylogger = value
        else: TypeError(f"{value} is not a boolean.")

    # --------------------------------------------------------------------------- #

    @property
    def console_printer(self):
        """
        console_printer is a boolean.
        If it's True, the logger will print the log in the console.
        """
        return self._dailylogger

    @console_printer.setter
    def console_printer(self, value):
        if type(value) is bool:
            self._console_printer = value
        else: TypeError(f"{value} is not a boolean.")

    # --------------------------------------------------------------------------- #
    @property
    def message(self):
        """
        This field is for setting the message format of the logger.
        The default formatter accept [time, level, msg].
        """
        return self._message

    @message.setter
    def message(self, value):
        if type(value) is str:
            self._message = value
        else: TypeError(f"{value} is not a string.")

    # --------------------------------------------------------------------------- #

    @property
    def time_formatter(self):
        """
        time_format is the way time is displayed when the bot logs,
        check https://docs.python.org/3/library/time.html#time.strftime to see how to modify it.
        """
        return self._time_formatter

    @time_formatter.setter
    def time_formatter(self, value):
        if type(value) is str:
            self._time_formatter = value
        else: TypeError(f"{value} is not a string.")

    # --------------------------------------------------------------------------- #

    def getLogFile(self):
        """
        This function is called before the bot logs something because it returns the name of the log file.
        """

        # Determines the name of the log
        file_name = self.client.LOG_PATH
        if self._dailylogger:
            file_name += f"\\{strftime('%m-%d-%Y', gmtime())}.log"
        else:
            file_name += "\\Log.log"

        # Checks if the log file already exist. If false, it creates a new one.
        if not exists(file_name):
            open(file_name, "w").close()

        return file_name

    def log(self, level, message):
        if not self.levels[level]:
            return

        with open(self.getLogFile(), "a") as file:
            log_message = self.message.format(level=level, msg=message, time=strftime(self._time_formatter, gmtime()))
            file.write(log_message + "\n")

        if self.console_printer:
            print(log_message)

    # --------------------------------------------------------------------------- #

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
