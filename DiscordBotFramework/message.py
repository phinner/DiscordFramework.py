from inspect import stack


class Reader(object):
    def __init__(self, name, keywords=None, quotes=None, function=None, detector=None):
        """
        :param name: String containing the name of the reader
        :param keywords: List with the keywords to detect, can be None if you want to always trigger the reader
        :param quotes: List with the quotes
        :param function: Function, can be None. Can be used if you wanna reply with complex stuff
        :param detector: Function that will be used to detect the keywords, make sure it accepts a message and keywords argument to be able to read the message content. The default function is a simple any.
        """
        self.name = name
        self.quotes = quotes
        self.keywords = keywords
        self.function = function
        self.enabled = True
        self.detector = detector

        if detector is None:
            self.detector = lambda msg, kwords: any(keyword in msg.content for keyword in kwords)


class MessageHandler(object):
    MessageReaders = dict()

    def __init__(self, client):
        self.client = client

    def hasPrefix(self, msg):
        """
        This function looks for the prefix, at the beginning of the message
        :return: Bool
        """
        return msg.content.startswith(self.client.GuildManager.guildIndex[str(msg.guild.id)].prefix)

    def getCommand(self, msg):
        """
        This function split the message and extracts the command which follow the prefix
        :return: String
        """
        return msg.content[len(self.client.GuildManager.guildIndex[str(msg.guild.id)].prefix):].split(" ", 1)[0]

    def getArgs(self, msg):
        """
        This function returns the args after the command, returns None if there is no args
        :return: String
        """
        data = msg.content[len(self.client.GuildManager.guildIndex[str(msg.guild.id)].prefix):].split(" ", 1)
        if len(data) == 1:
            data.append(None)
        return data[1]

    @classmethod
    def registerReader(cls, **kwargs):
        """
        This function registers a reader function, it can be used as a decorator or a regular function call.
        If you don't register a reader but call the this function anyway, the function of the reader will be None.
        """
        def wrapper(function):
            reader = Reader(**kwargs, function=function)

            # Makes sure there are no duplicates
            if reader.name in cls.MessageReaders:
                raise IndexError(f"{reader.name} already exists in the command index.")

            # Updates the reaction index
            cls.MessageReaders.update({reader.name: reader})

        # Checks if the function is called as a decorator
        if any(line.startswith('@') for line in stack(context=2)[1].code_context):
            return wrapper
        else: wrapper(None)

    @classmethod
    def unregisterReader(cls, name):
        if name in cls.MessageReaders:
            cls.MessageReaders.pop(name)
        else: raise IndexError(f"{name} not found.")
