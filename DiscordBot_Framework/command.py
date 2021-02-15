class Command(object):
    def __init__(self, name, alias, usage, private, category, description, func=None):
        self.name = name
        self.alias = alias
        self.usage = usage
        self.private = private
        self.category = category
        self.description = description
        self.func = func

    def register(self):
        CommandHandler.commands.update({self.name: self})

    def unregister(self):
        if self.name in CommandHandler.commands:
            CommandHandler.commands.pop(self.name)


class CommandHandler(object):
    commands = dict()
    categories = list()

    def __init__(self, client):
        self.client = client

    async def __call__(self, cmd_name, *args):
        if cmd_name in self.commands and self.commands[cmd_name].func is not None:
            await self.commands[cmd_name].func(*args)

    def checkCommandsNames(self):
        # Check if the commands don't share the same names or aliases
        names = [cmd.name for cmd in self.commands.values()] + [cmd.alias for cmd in self.commands.values()]
        if any(True for name in names if names.count(name) > 1):
            self.client.Logger.critical(f"Some commands are sharing names or aliases: {names}")
            raise NameError

    def sortCommandsCategories(self):
        # Sorts the commands into categories
        for cmd in self.commands.values():
            if cmd.category not in self.categories:
                self.categories.append(cmd.category)
