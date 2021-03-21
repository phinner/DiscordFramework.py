# ------------------------------------------------------------------------------- #

class Command(object):
    def __init__(self, name, function=None, alias=None, usage=None, category="Unclassified", description=None):
        """
        Command is a class for storing informations about a command. It can be enabled/disabled
        """
        self.name = name
        self.alias = alias
        self.category = category

        self.usage = usage
        self.description = description
        self.enabled = True

        self.function = function

        if self.function is None:
            self.function = lambda *x, **y: None

        assert category is not None

# ------------------------------------------------------------------------------- #

class CommandManager(object):
    Index = dict()
    Categories = dict()

    def __init__(self, client):
        self.client = client

    # --------------------------------------------------------------------------- #

    @classmethod
    def registerCommand(cls, **kwargs):
        """
        This function registers a command function, it can be used as a decorator or a regular function call.
        """
        def wrapper(function=None):
            cmd = Command(function=function, **kwargs)

            # Make sure the command is callable
            if not callable(cmd.function):
                raise TypeError("The function is not callable.")

            # Make sure there are no duplicates
            if (cmd.name or cmd.alias) in cls.Index:
                raise IndexError(f"{cmd.name} or {cmd.alias} already exists in the command index.")

            # Update the commands indexe
            cls.Index.update({cmd.name: cmd})
            if cmd.alias is not None:
                cls.Index.update({cmd.alias: cmd})

            # Add the command to the specified category by storing it in a list
            if cmd.category not in cls.Categories:
                cls.Categories.update({cmd.category: [cmd]})
            else:
                cls.Categories[cmd.category].append(cmd)

        return wrapper

    @classmethod
    def unregisterCommand(cls, index):
        """
        Unregister a command by it's name or alias.
        """
        if index in cls.Index:
            # Delete the category occurences
            if cls.Index[index].category is not None:
                cls.Categories[cls.Index[index].category].remove(cls.Index[index])

            # Make sure the alias is deleted first
            if cls.Index[index].name == index and cls.Index[index].alias is not None:
                cls.Index.pop(cls.Index[index].alias)

            # Delete the command in the Index
            cls.Index.pop(cls.Index[index].name)
        else:
            raise IndexError(f"{index} not found.")
