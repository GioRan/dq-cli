import io
import logging
import os
import shutil
from typing import List, Union

import pandas
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from Utilities.Utils import Utils as utils


class Constants:
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
              'https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/spreadsheets.readonly']


class GDrive(Constants):

    def __init__(self):

        self.cwd = os.path.dirname(os.path.realpath(__file__))
        creds: Credentials = self.do_creds()
        self.service = build('drive', 'v3', credentials=creds)

    #######################
    ## GDrive operations ##
    #######################
    def do_creds(self) -> Credentials:
        creds = None
        token_path = os.path.join(self.cwd, 'token.json')
        creds_path = os.path.join(self.cwd, 'credentials.json')

        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return creds

    def search(self, type: str, folder_id: str = None, file_id: str = None, name: str = None) -> List[dict]:

        mimeType = {
            'sheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'folder': 'application/vnd.google-apps.folder'
        }

        try:
            files = []
            page_token = None
            query = None
            query_type = None

            if file_id is not None and type == 'sheet':
                query = f"mimeType='{mimeType[type]}' and fileId='{file_id}' and trashed = false"
                query_type = 'direct_download'
            elif name is None and folder_id is not None:
                query = f"mimeType='{mimeType[type]}' and '{folder_id}' in parents and trashed = false"
                query_type = 'search_all'
            elif name is not None and folder_id is not None and type == 'sheet':
                query = f"mimeType='{mimeType[type]}' and '{folder_id}' in parents and name = '{name}' and trashed = false"
                query_type = 'search_filename'

            while True:
                if query_type == 'direct_download':
                    sheet = self.service.files().get(fileId=file_id).execute()
                    sheet['query_type'] = query_type
                    files.append(sheet)
                    break
                else:
                    response = self.service.files().list(q=query, spaces='drive',
                                                         fields='nextPageToken, files(id, name, mimeType, permissions)',
                                                         pageToken=page_token).execute()

                    for file in response.get('files', []):
                        file['query_type'] = query_type
                        files.append(file)

                    page_token = response.get('nextPageToken', None)

                    if page_token is None:
                        break

        except HttpError as http_error:
            logging.error(f'An error occurred: {http_error}')
            files = None

        return files

    def download(self, file: dict, destination_folder: str = None, in_memory_only: bool = False) -> Union[
        None, pandas.DataFrame]:

        fileIO = io.BytesIO()

        try:
            if file['query_type'] == 'direct_download':
                request = self.service.files().export_media(fileId=file['id'],
                                                            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                file['name'] = f"{file['name']}.xlsx"
            else:
                request = self.service.files().get_media(fileId=file['id'])

            downloader = MediaIoBaseDownload(fileIO, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            if done:
                if in_memory_only:
                    logging.info('Download complete in memory')
                else:
                    logging.info('Download complete as file')

        except HttpError as error:
            logging.error(f'An error occurred: {error}')
            fileIO = None

        fileIO.seek(0)

        if in_memory_only:
            return utils.read_excel(fileIO)

        logging.debug(destination_folder)
        logging.debug(file['name'])
        with open(os.path.join(destination_folder, file['name']), 'wb') as f:
            shutil.copyfileobj(fileIO, f)
            logging.info(f"File downloaded -> {os.path.join(destination_folder, file['name'])}")

    def upload(self, folder_id: str, file_path: str) -> None:

        file_name = os.path.splitext(file_path.split(os.sep)[-1])[0]

        try:
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            media = MediaFileUpload(file_path,
                                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            file = self.service.files().create(body=file_metadata, media_body=media,
                                               fields='id, name').execute()

            logging.info(F'File Uploaded -> {file.get("name")}, {file.get("id")}')

        except HttpError as error:
            logging.error(F'An error occurred: {error}')
            file = None

    def move_to_folder(self, file_id: str, parent_folder_id: str):
        try:
            file = self.service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ','.join(file.get('parents'))
            file = self.service.files().update(fileId=file_id, addParents=parent_folder_id,
                                               removeParents=previous_parents,
                                               fields='id, name, parents').execute()

            logging.info(f"File {file.get('id')} -> {file.get('name')} moved to {file.get('parents')}")

        except HttpError as error:
            logging.error(F'An error occurred: {error}')
            file = None

    def create_folder(self, name: str, parent_folder_id: str) -> str:
        try:
            file_metadata = {
                'name': name,
                'parents': [parent_folder_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }

            file = self.service.files().create(body=file_metadata, fields='id').execute()

            logging.info(F'Folder -> {name} has created.')

        except HttpError as error:
            logging.error(F'An error occurred: {error}')
            file = None

        return file.get('id')
