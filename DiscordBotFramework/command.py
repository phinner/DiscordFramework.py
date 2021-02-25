from inspect import stack


class Command(object):
    def __init__(self, name, function=None, alias=None, usage=None, category=None, description=None):
        self.name = name
        self.alias = alias
        self.usage = usage
        self.category = category
        self.description = description
        self.function = function
        self.enabled = True

        if self.function is None:
            self.function = lambda *x: None


class CommandHandler(object):
    commandNames = dict()
    commandAliases = dict()
    commandCategories = dict()

    def __init__(self, client):
        self.client = client

    @classmethod
    def registerCommand(cls, **kwargs):
        """
        This function registers a command function, it can be used as a decorator or a regular function call.
        If you don't register a command but call the this function anyway, the function of the command will be None.
        """
        def wrapper(function):
            cmd = Command(function=function, **kwargs)

            # Make sure the command is callable
            if not callable(cmd.function):
                raise TypeError("The function is not callable.")
            # Make sure there are no duplicates
            if (cmd.name or cmd.alias) in (cls.commandNames or cls.commandAliases):
                raise IndexError(f"{cmd.name} or {cmd.alias} already exists in the command index.")

            # Update the commands indexes
            cls.commandNames.update({cmd.name: cmd})
            cls.commandAliases.update({cmd.alias: cmd})

            if cmd.category not in cls.commandCategories:
                cls.commandCategories.update({cmd.category: [cmd]})
            else:
                cls.commandCategories[cmd.category].append(cmd)

        # Check if the function is called as a decorator
        if any(line.startswith('@') for line in stack(context=2)[1].code_context):
            return wrapper
        else: wrapper(None)

    @classmethod
    def unregisterCommand(cls, name):
        """
        Unregister a command by it's name. It deletes it's alias.
        """
        if name in cls.commandNames:
            # Deletes the aliases and the category first before
            if cls.commandNames[name].alias is not None:
                cls.commandAliases.pop(cls.commandNames[name].alias)
            if cls.commandNames[name].category is not None:
                cls.commandCategories[cls.commandNames[name].category].remove(cls.commandNames[name])
            cls.commandNames.pop(name)
        else: raise IndexError(f"{name} not found.")
