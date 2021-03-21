import dropbox

from ..utils import readJSON


class DropboxAPI(object):
	def __init__(self, client, secret_file_path):
		"""
		This utility class is mainly used for retrieving images from dropbox.
		"""
		self.client = client
		self.credentials = readJSON(secret_file_path)
		self.dbx = dropbox.Dropbox(self.credentials["access_token"])

	def listFiles(self, path="", **params):
		"""
		List all the files with the given path,
		default is the whole application directory.
		"""
		return self.dbx.files_list_folder(path, **params).entries

	def listSharedFiles(self, path=None, **params):
		"""
		List all the shared files with the given path,
		default is the whole application directory.
		"""
		return self.dbx.sharing_list_shared_links(path, **params).links

	# --------------------------------------------------------------------------- #

	def checkFileSharing(self, path="", **params):
		"""
		This function make all the files with the given path shareable,
		in other words, it creates a new share link for every file.
		This operation is very slow.
		"""
		for file in self.listFiles(path, **params):
			try:
				self.dbx.sharing_create_shared_link_with_settings(file.path_display)
			except dropbox.exceptions.ApiError:
				pass

	def makeLinkDict(self, path=None, **params):
		"""
		This function returns a dict containing the directory structure.
		The keys are the name of a file and the value is a link to the file.
		"""

		# Recursion is quite useful lol
		def addFile(dictionary, file, path):
			path.pop(0)  # -> pop the root folder

			# Checks if the path list only contains the name of the file, else it calls addFile again to go deeper
			if len(path) == 1:
				dictionary.update({file.name: file.url})

			else:
				# Makes sure it doesn't overwrite an existing dict
				if path[0] in dictionary:
					addFile(dictionary[path[0]], file, path)

				else:
					folder = dict()
					dictionary.update({path[0]: folder})
					addFile(folder, file, path)

		link_dict = dict()

		for file in self.listSharedFiles(path, **params):
			# Checks if the file is not a folder
			if isinstance(file, dropbox.sharing.FolderLinkMetadata):
				continue

			# Splits the path
			file_path = file.path_lower.split("/")

			addFile(link_dict, file, file_path)

		return link_dict
