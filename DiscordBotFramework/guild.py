from os import listdir
from os.path import exists
from shutil import rmtree
import json

from .util import isDiscordID


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

    def jsonify(self):
        dictionary = self.__dict__.copy()
        for attribute in self.unsaved_attributes:
            dictionary.pop(attribute)
        return dictionary


class GuildManager(object):
    def __init__(self, client):
        self.client = client
        self.guildIndex = dict()
        self.template = self.client.GuildData(None, self.client.DEFAULT_PREFIX)

    def addGuildData(self, guild):
        self.guildIndex.update({str(guild.id): self.client.GuildData(guild, self.client.DEFAULT_PREFIX)})
        with open(f"{self.client.GUILD_PATH}\\{guild.id}.json", 'w', encoding="utf-8") as file:
            file.write(json.dumps(self.template.jsonify(), indent=2))

    def removeGuildData(self, guild):
        self.guildIndex.pop(str(guild.id))
        self.client.FileManager.deleteGuildFile()
        rmtree(f"{self.client.GUILD_PATH}\\{guild.id}.json")

    def loadGuildData(self, guild):
        with open(f"{self.client.GUILD_PATH}\\{guild.id}.json", "r", encoding="utf-8") as file:
            guild_dictionary = json.load(file)
        self.guildIndex.update({str(guild.id): self.client.GuildData(guild, self.client.DEFAULT_PREFIX)})
        self.guildIndex[str(guild.id)].__dict__.update(guild_dictionary)

    def saveGuildData(self, guild_data):
        # Saves guildIndex data
        with open(f"{self.client.GUILD_PATH}\\{guild_data.guild.id}.json", 'w', encoding="utf-8") as file:
            file.write(json.dumps(guild_data.jsonify()))

    def updateGuildData(self, guild):
        with open(f"{self.client.GUILD_PATH}\\{guild.id}.json", 'r+', encoding="utf-8") as file:
            guild_dict = json.load(file)
            for key in guild_dict.copy().keys():  # Deletes unused attributes
                if key not in self.client.GuildManager.template.jsonify():
                    guild_dict.pop(key)
            for key, arg in self.client.GuildManager.template.jsonify().items():  # Adds new attributes
                if key not in guild_dict:
                    guild_dict.setdefault(key, arg)
            file.truncate(0), file.seek(0), file.write(json.dumps(guild_dict, indent=2, ensure_ascii=True))

    def checkGuildDirectory(self):
        # Delete the data of the guilds where the bot is no longer present
        guild_id_index = list(str(guild.id) for guild in self.client.guilds)
        for file_name in listdir(self.client.GUILD_PATH):
            file_path = f"{self.client.GUILD_PATH}\\{file_name}"
            if file_name.endswith(".json") and isDiscordID(file_name[:-5]):
                if file_name[:-5] not in guild_id_index:
                    rmtree(file_path)
            else:
                self.client.Logger.WARNING(f"An unexpected file is present in the Guild directory: {file_path}")

        # Checks the files of the guildIndex
        for guild in self.client.guilds:
            if not exists(f"{self.client.GUILD_PATH}\\{guild.id}.json"):
                self.addGuildData(guild)
            else:
                self.updateGuildData(guild)
        self.client.Logger.INFO("Files have been successfully checked.")

    def loadGuildDirectory(self):
        # Load guildIndex data
        for guild in self.client.guilds:
            self.loadGuildData(guild)
        self.client.Logger.INFO("Files have been successfully loaded.")

    def saveGuildDirectory(self):
        for guild in self.guildIndex.values():
            self.saveGuildData(guild)
