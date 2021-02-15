class GuildData(object):
    def __init__(self, guild, prefix):
        self.guild = guild
        self.prefix = prefix
        self.guild_permanent_link = None

    def toDict(self):
        dictionary = self.__dict__.copy()
        dictionary.pop("guild")
        return dictionary


class GuildManager(object):
    def __init__(self, client):
        self.client = client
        self.guilds = dict()
        self.template = GuildData(None, self.client.DEFAULT_PREFIX)

    def addGuildData(self, guild):
        self.guilds.update({str(guild.id): GuildData(guild, self.client.DEFAULT_PREFIX)})
        self.client.FileManager.addGuildFile(f"{self.client.GUILD_PATH}\\{guild.id}.json")

    def removeGuildData(self, guild):
        self.guilds.pop(str(guild.id))
        self.client.FileManager.deleteGuildFile(f"{self.client.GUILD_PATH}\\{guild.id}.json")

    def loadGuildData(self, guild):
        guild_path = f"{self.client.GUILD_PATH}\\{guild.id}.json"
        self.guilds.update({str(guild.id): GuildData(guild, self.client.DEFAULT_PREFIX)})
        self.guilds[str(guild.id)].__dict__.update(self.client.FileManager.loadGuildFile(guild_path))
