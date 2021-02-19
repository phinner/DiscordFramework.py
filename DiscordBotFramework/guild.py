class GuildData(object):
    def __init__(self, guild, prefix):
        self.guild = guild
        self.prefix = prefix
        self.guild_permanent_link = None
        self.roles = dict()
        self.unsaved_attributes = ["guild"]

    def addUnsavedAttributes(self, *args):
        for attribute in args:
            if not hasattr(self, attribute):
                raise AttributeError(f"{self.__name__} don't have the attribute {attribute}.")
            self.unsaved_attributes.append(attribute)

    def deleteUnsavedAttributes(self, *args):
        for attribute in args:
            if not hasattr(self, attribute):
                raise AttributeError(f"{self.__name__} don't have the attribute {attribute}.")
            self.unsaved_attributes.remove(attribute)

    def toDict(self):
        dictionary = self.__dict__.copy()
        for attribute in self.unsaved_attributes:
            dictionary.pop(attribute)
        return dictionary


class GuildManager(object):
    def __init__(self, client, custom_guild_class=None):
        self.client = client
        self.guilds = dict()
        if custom_guild_class is None:
            custom_guild_class = GuildData
        self.GuildDataClass = custom_guild_class
        self.template = self.GuildDataClass(None, self.client.DEFAULT_PREFIX)

    def addGuildData(self, guild):
        self.guilds.update({str(guild.id): self.GuildDataClass(guild, self.client.DEFAULT_PREFIX)})
        self.client.FileManager.addGuildFile(f"{self.client.GUILD_PATH}\\{guild.id}.json")

    def removeGuildData(self, guild):
        self.guilds.pop(str(guild.id))
        self.client.FileManager.deleteGuildFile(f"{self.client.GUILD_PATH}\\{guild.id}.json")

    def loadGuildData(self, guild):
        guild_path = f"{self.client.GUILD_PATH}\\{guild.id}.json"
        self.guilds.update({str(guild.id): self.GuildDataClass(guild, self.client.DEFAULT_PREFIX)})
        self.guilds[str(guild.id)].__dict__.update(self.client.FileManager.loadGuildFile(guild_path))
