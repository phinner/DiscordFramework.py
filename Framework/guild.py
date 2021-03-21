import pickle

from os import listdir
from os.path import exists
from shutil import rmtree

from .utils import isDiscordID

# --------------------------------------------------------------------------- #

class GuildData(object):
    def __init__(self, guild, prefix):
        """
        A data class to manage and save guild data,
        can be extended.
        """
        self.guild = guild
        self.prefix = prefix
        self.permalink = None

    def refreshGuild(self, client):
        if isDiscordID(self.guild):
            self.guild = client.get_guild(self.guild)

    def __getstate__(self):
        copy = self.__dict__.copy()
        copy["guild"] = self.guild.id
        return copy
 
    def __setstate__(self, state):
        self.__dict__ = state

# --------------------------------------------------------------------------- #

class GuildManager(object):
    def __init__(self, client):
        """
        This special manager take care of the file management of the guilds.
        Extend the base GuildData class to store more data, but make sure it can be pickled.
        """
        self.client = client
        self.Index = dict()
        self.template = self.client.GuildData(None, self.client.DEFAULT_PREFIX)

    def addGuildData(self, guild, makefile=True):
        """
        Add a new GuildData object to the guild Index,
        a file can be created or override an existing one.
        """
        self.Index.update(
            {str(guild.id): self.client.GuildData(guild, self.client.DEFAULT_PREFIX)}
        )

        if makefile:
            with open(f"{self.client.GUILD_PATH}\\{guild.id}.pickle", 'wb') as file:
                file.write(pickle.dumps(self.Index[str(guild.id)]))

    def removeGuildData(self, guild, deletefile=True):
        """
        Remove a GuildData object with a given guild from the guild Index,
        the corresponding file can be deleted if it exists.
        """
        self.Index.pop(str(guild.id))

        if deletefile:
            rmtree(f"{self.client.GUILD_PATH}\\{guild.id}.pickle")

    def loadGuildData(self, guild, checkfile=True):
        """
        Load a GuildData object from a pickle file.
        The file can be checked so if you changed the GuildData class, it will be updated.
        """
        with open(f"{self.client.GUILD_PATH}\\{guild.id}.pickle", "rb+") as file:
            loaded_guild = pickle.load(file)
            loaded_guild.refreshGuild(self.client)

            if checkfile:
                # Deletes the unused attributes if the GuildData class had been changed
                for key in loaded_guild.__dict__.copy().keys():
                    if key not in self.template.__dict__:
                        loaded_guild.__dict__.pop(key)

                # Adds new attributes
                for key, arg in self.template.__dict__.items():
                    if key not in loaded_guild.__dict__:
                        loaded_guild.__dict__.setdefault(key, arg)

                # Applies the changes
                file.truncate(0), file.seek(0)
                file.write(pickle.dumps(loaded_guild))
        
        self.Index.update({str(guild.id): loaded_guild})

    def saveGuildData(self, guild_data):
        """
        Save a GuildData object in a pickle file.
        """
        with open(f"{self.client.GUILD_PATH}\\{guild_data.guild.id}.pickle", "wb") as file:
            file.write(pickle.dumps(self.Index[str(guild_data.guild.id)]))

    def checkGuildDirectory(self, deletefile=True):
        """
        Check the guild directory,
        by default, it deletes the unused guild files.
        """

        # Add the new guilds
        for guild in self.client.guilds:
            file_path = f"{self.client.GUILD_PATH}\\{guild.id}.pickle"
            if not exists(file_path):
                self.addGuildData(guild)

        # Delete the data of the guilds where the bot is no longer present
        if deletefile:
            client_guilds = list(str(guild.id) for guild in self.client.guilds)

            for file_name in listdir(self.client.GUILD_PATH):
                file_id = file_name.split(".")[0]

                if file_name.endswith(".pickle") and isDiscordID(file_id):
                    if file_id not in client_guilds:
                        rmtree(f"{self.client.GUILD_PATH}\\{file_name}")
                else:
                    self.client.Logger.WARNING(f"An unexpected file is present in the Guild directory: {file_name}")

    def loadGuildDirectory(self):
        """
        Load the GuildData files in the guild directory.
        """
        for guild in self.client.guilds:
            self.loadGuildData(guild)
        self.client.Logger.INFO("The GuildData files have been successfully loaded.")

    def saveGuildDirectory(self):
        """
        Save the GuildData in the guild directory.
        """
        for guild_data in self.Index.values():
            self.saveGuildData(guild_data)
        self.client.Logger.INFO("The GuildData files have been saved.")
