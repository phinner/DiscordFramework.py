from __future__ import print_function
import httplib2
import os
import io

from apiclient import discovery
from apiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload

try:
	import argparse
	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
	flags = None


class DriveAPI(object):
	def __init__(self, SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME):
		"""
		Most of the code come from https://github.com/samlopezf/google-drive-api-tutorial and the Google Drive API.
		I just turned it into a class and optimised it a little bit and added some handy functions.

		Gets valid user credentials from storage.

		If nothing has been stored, or if the stored credentials are invalid,
		the OAuth2 flow is completed to obtain the new credentials.

		Returns:
			Credentials, the obtained credential.
		"""
		self.SCOPES = SCOPES
		self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
		self.APPLICATION_NAME = APPLICATION_NAME

		cwd_dir = os.getcwd()
		credential_dir = os.path.join(cwd_dir, '.credentials')
		if not os.path.exists(credential_dir):
			os.makedirs(credential_dir)
		credential_path = os.path.join(credential_dir, 'google-drive-credentials.json')

		store = Storage(credential_path)
		credentials = store.get()
		if not credentials or credentials.invalid:
			flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
			flow.user_agent = self.APPLICATION_NAME
			if flags:
				credentials = tools.run_flow(flow, store, flags)
			else:  # Needed only for compatibility with Python 2.6
				credentials = tools.run(flow, store)
			print('Storing credentials to ' + credential_path)

		self.service = discovery.build('drive', 'v3', http=credentials.authorize(httplib2.Http()))

	def listFiles(self, size, requested_info=None):
		"""
		Returns a list of every file in the Drive, even the ones in the trash bin
		"""
		if requested_info is None:
			requested_info = "id, name"

		results = self.service.files().list(pageSize=size, fields=f"nextPageToken, files({requested_info})").execute()

		return results.get('files', [])

	def uploadFile(self, filename, file_path, mimetype):
		"""
		upload a file to the drive,
		check https://developers.google.com/drive/api/v3/manage-uploads to know how to use the arguments
		"""
		media = MediaFileUpload(file_path, mimetype=mimetype)
		file = self.service.files().create(
			body={'name': filename}, media_body=media, fields='id').execute()

		return file.get("id")  # I added that line because... Why not ? It can be handy later...

	def downloadFile(self, file_id, file_path):
		"""
		Download a file with it's ID and writes it at the given path
		check https://developers.google.com/drive/api/v3/manage-downloads
		"""
		request = self.service.files().get_media(fileId=file_id)
		fh = io.BytesIO()
		downloader = MediaIoBaseDownload(fh, request)

		done = False
		while done is False:
			status, done = downloader.next_chunk()

		# That part is needed to actually save the file at the given path
		with io.open(file_path, 'wb') as local_file:
			fh.seek(0)
			local_file.write(fh.read())

	def createFolder(self, name):
		"""
		Creates a file with a given name
		"""
		file_metadata = {
			'name': name,
			'mimeType': 'application/vnd.google-apps.folder'
		}

		folder = self.service.files().create(body=file_metadata, fields='id').execute()

		return folder.get("id")

	def searchFile(self, size, query, requested_info=None):
		"""
		research files in the drive and returns a list containing the requested infos,
		check https://developers.google.com/drive/api/v3/search-shareddrives to know how to use the arguments
		"""
		if requested_info is None:
			requested_info = "id, name, kind, mimeType, parents"

		results = self.service.files().list(
			pageSize=size, fields=f"nextPageToken, files({requested_info})", q=query).execute()

		return results.get('files', [])

	def extractFiles(self, folder_id, requested_info=None):
		"""
		searchFile returns a list of the files present in a folder, but that function will look for every file in the
		given folder and it's sub-folders, and so on...
		"""
		output_files = list()

		if requested_info is None:
			requested_info = "id, name, kind, mimeType, parents"
		else:
			if not "id" and "mimeType" in requested_info:
				raise ValueError("extractFiles need at least 'id' and 'mimeType' to work.")

		for file in self.searchFile(10, f"'{folder_id}' in parents", requested_info):
			if file["mimeType"] != "application/vnd.google-apps.folder":
				output_files.append(file)
			else:
				output_files = output_files + self.extractFiles(file["id"], requested_info)

		return output_files
