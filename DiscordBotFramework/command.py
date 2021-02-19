from inspect import stack

class Command(object):
    def __init__(self, name, function=None, alias=None, usage=None, category=None, description=None):
        self.name = name
        self.alias = alias
        self.usage = usage
        self.category = category
        self.description = description
        self.function = function

        if self.function is None:
            self.function = lambda *x: None

        self.enabled = True

    async def __call__(self, *args):
        await self.function(*args)


class CommandHandler(object):
    commandNames = dict()
    commandAliases = dict()
    commandCategories = dict()

    def __init__(self, client):
        self.client = client

    async def __call__(self, command_name, client, message):
        for index in [self.commandNames, self.commandAliases]:
            if command_name in index:
                if not index[command_name].enabled:
                    return await self.client.MessageHandler.sendErrMessage(f"{command_name} is currently disabled.")
                return await index[command_name](client, message, self.client.MessageHandler.getArgs(message))
        message.channel.sendMessage(f"{command_name} is an invalid command.", )

    @classmethod
    def registerCommand(cls, **kwargs):  # Use this as a decorator
        def wrapper(function):
            cmd = Command(function=function, **kwargs)

            # Makes sure the command is callable
            if not callable(cmd.function):
                raise TypeError("The function is not callable.")
            # Makes sure there are no duplicates
            if (cmd.name or cmd.alias) in (cls.commandNames or cls.commandAliases):
                raise IndexError(f"{cmd.name} or {cmd.alias} already exists in the command index.")

            # Updates the commands indexes
            cls.commandNames.update({cmd.name: cmd})
            cls.commandAliases.update({cmd.alias: cmd})

            if cmd.category not in cls.commandCategories:
                cls.commandCategories.update({cmd.category: [cmd]})
            else:
                cls.commandCategories[cmd.category].append(cmd)

        # Checks if the function is called as a decorator
        if any(line.startswith('@') for line in stack(context=2)[1].code_context):
            return wrapper
        else: wrapper(None)

    @classmethod
    def unregisterCommand(cls, name):
        if name in cls.commandNames:
            # Deletes the aliases and the category first before
            if cls.commandNames[name].alias is not None:
                cls.commandAliases.pop(cls.commandNames[name].alias)
            if cls.commandNames[name].category is not None:
                cls.commandCategories[cls.commandNames[name].category].remove(cls.commandNames[name])
            cls.commandNames.pop(name)
        else: raise IndexError(f"{name} not found.")
