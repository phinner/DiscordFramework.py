import atexit
from os import makedirs, listdir
from os.path import exists
from shutil import rmtree
import json

from .util import isDiscordID


class FileManager(object):
    def __init__(self, client):
        self.client = client
        atexit.register(self.saveFiles)

    def addGuildFile(self, guild_path):
        with open(guild_path, 'w', encoding="utf-8") as file:
            file.write(json.dumps(self.client.GuildManager.template.toDict(), indent=2))
        self.client.Logger.info(f"{guild_path} has been created.")

    def updateGuildFile(self, guild_path):
        with open(guild_path, 'r+', encoding="utf-8") as file:
            guild_dict = json.load(file)
            for key in guild_dict.copy().keys():  # Deletes unused attributes
                if key not in self.client.GuildManager.template.toDict():
                    guild_dict.pop(key)
                    self.client.Logger.warning(f"The key '{key}' has been deleted in {guild_path}.")
            for key, arg in self.client.GuildManager.template.toDict().items():  # Adds new attributes
                if key not in guild_dict:
                    guild_dict.setdefault(key, arg)
                    self.client.Logger.warning(f"The key '{key}' is missing in {guild_path}.")
            file.truncate(0), file.seek(0), file.write(json.dumps(guild_dict, indent=2, ensure_ascii=True))

    def deleteGuildFile(self, guild_path):
        try:
            rmtree(guild_path), self.client.Logger.info(f"{guild_path} has been deleted.")
        except OSError:
            self.client.Logger.warning(f"A problem has occurred while deleting the data of {guild_path}")

    @staticmethod
    def loadGuildFile(guild_path):
        with open(guild_path, "r", encoding="utf-8") as file:
            dictionary = json.load(file)
        return dictionary

    def checkFiles(self):
        # Checks the root directories
        for directory in [self.client.CLIENT_PATH, self.client.ACCOUNT_PATH, self.client.GUILD_PATH]:
            if not exists(directory):
                makedirs(directory), self.client.Logger.info(f"{directory} has been created.")

        # Delete the data of the guilds where the bot is no longer present
        guild_id_index = list(str(guild.id) for guild in self.client.guilds)
        for file_name in listdir(self.client.GUILD_PATH):
            file_path = f"{self.client.GUILD_PATH}\\{file_name}"
            if file_name.endswith(".json") and isDiscordID(file_name[:-5]):
                if file_name[:-5] not in guild_id_index:
                    self.deleteGuildFile(file_path)
            else:
                self.client.Logger.warning(f"An unexpected file is present in the Guild directory: {file_path}")

        # Checks the files of the guilds
        for guild in self.client.guilds:
            guild_path = f"{self.client.GUILD_PATH}\\{guild.id}.json"
            if not exists(guild_path):
                self.addGuildFile(guild_path)
            else:
                self.updateGuildFile(guild_path)
        self.client.Logger.info("Files have been successfully checked.")

    def loadFiles(self):
        # Load guilds data
        for guild in self.client.guilds:
            self.client.GuildManager.loadGuildData(guild)
        self.client.Logger.info("Files have been successfully loaded.")

    def saveFiles(self):
        # Saves guilds data
        for guild_data in self.client.GuildManager.guilds.values():
            with open(f"{self.client.GUILD_PATH}\\{guild_data.guild.id}.json", 'w', encoding="utf-8") as file:
                file.write(json.dumps(guild_data.toDict()))
        self.client.Logger.info("Files have been successfully saved.")
