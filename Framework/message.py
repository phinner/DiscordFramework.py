# ------------------------------------------------------------------------------- #

class Reader(object):
    def __init__(self, name, keywords=None, quotes=None, function=None, detector=None, category="Reaction"):
        """
        :param name: String containing the name of the reader.
        :param keywords: keywords to detect, can be None if you want to always trigger the reader.
        :param quotes: quotes for the bot to respond.
        :param function: Function, can be None. Can be used if you wanna reply with complex stuff.
        :param detector: Function that will be used to detect the keywords, make sure it accepts a message and keywords argument to be able to read the message content. The default function is a simple any.
        """
        self.name = name
        self.category = category
        self.keywords = keywords
        self.quotes = quotes

        self.enabled = True
        self.function = function
        self.detector = detector

        # make sure the keywords are iterable
        if not None and not hasattr(self.keywords, "__iter__"):
            self.keywords = [self.keywords]

        # make sure the quotes are iterable
        if not None and not hasattr(self.quotes, "__iter__"):
            self.quotes = [self.quotes]

        if detector is None:
            self.detector = lambda msg, kwords: any(keyword in msg.content for keyword in kwords)

# ------------------------------------------------------------------------------- #

class MessageHandler(object):
    Index = dict()
    Categories = dict()

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------------------------------- #

    def hasPrefix(self, msg):
        """
        This function looks for the prefix, at the beginning of the message.
        :return: Bool
        """
        return msg.content.startswith(self.client.GuildManager.Index[str(msg.guild.id)].prefix)

    def getCommand(self, msg):
        """
        This function split the message and extracts the command which follow the prefix.
        :return: String
        """
        return msg.content[len(self.client.GuildManager.Index[str(msg.guild.id)].prefix):].split(" ", 1)[0]

    def getArgs(self, msg):
        """
        This function returns the args after the command, returns None if there is no args.
        :return: String
        """
        data = msg.content[len(self.client.GuildManager.Index[str(msg.guild.id)].prefix):].split(" ", 1)

        if len(data) == 1:
            data.append(None)

        return data[1]

    # --------------------------------------------------------------------------- #

    @classmethod
    def registerReader(cls, **kwargs):
        """
        This function registers a reader function, it can be used as a decorator or a regular function call.
        If you don't register a reader but call the this function anyway, the function of the reader will be None.
        """
        def wrapper(function=None):
            reader = Reader(function=function, **kwargs)

            # Makes sure there are no duplicates
            if reader.name in cls.Index:
                raise IndexError(f"{reader.name} already exists in the command index.")

            # Updates the reaction index
            cls.Index.update({reader.name: reader})

            # Add the reader to the specified category by storing it in a list
            if reader.category not in cls.Categories:
                cls.Categories.update({reader.category: [reader]})
            else:
                cls.Categories[reader.category].append(reader)

        return wrapper

    @classmethod
    def unregisterReader(cls, name):
        """
        Unregister a reader by it's name.
        """
        if name in cls.Index:
            cls.Index.pop(name)
        else:
            raise IndexError(f"{name} not found.")
