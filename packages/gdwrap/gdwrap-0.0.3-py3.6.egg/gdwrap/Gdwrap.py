#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Google Drive REST API wrapper class.

Have a nice day:D
"""

import os
import io
import httplib2

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload


class Gdwrap:
    SCOPES = 'https://www.googleapis.com/auth/drive'
    DRIVE_API_VER = 'v3'
    APPLICATION_NAME = "gdwrap"

    _credentials = None

    def __init__(self, key_file: str, credential_file: str) -> None:
        # create credentials obj
        store = Storage(credential_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(key_file, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            credentials = tools.run_flow(flow, store)

        self._credentials = credentials

    def file_list(self, page_size: int, fields: str, order_by: str, query: str) -> dict:
        """
        Get file list from Google Drive
        :param page_size:
        :param fields:
        :param order_by:
        :param query:
        :return:
        """
        service = self.__get_service()
        results = service.files().list(
            pageSize=page_size,
            fields=fields,
            orderBy=order_by,
            q=query
        ).execute()
        return results.get('files', [])

    def create_folder(self, dir_name: str, parent_dir_id: str) -> str:
        """
        Create folder into Google Drive
        :param dir_name:
        :param parent_dir_name:
        :return:
        """
        service = self.__get_service()
        file_metadata = {
            'name': dir_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_dir_id],
        }
        folder = service.files() \
            .create(body=file_metadata, fields='id') \
            .execute()
        return folder.get('id')

    def file_download(self, item_id: str, item_name: str, dir_name: str) -> bool:
        """
        Download file from Google Drive
        :param item_id:
        :param dir_name:
        :return:
        """
        service = self.__get_service()
        request = service.files().get_media(fileId=item_id)
        self.__create_download_dir(dir_name)
        fh = io.FileIO(os.path.join(dir_name, item_name), mode='wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        return done

    def file_upload(self, folder_id: str, file_name: str, mine_type: str) -> bool:
        """
        Upload file into Google Drive
        :param folder_id:
        :param file_name:
        :param mine_type:
        :return:
        """
        service = self.__get_service()
        media_body = MediaFileUpload(file_name, mimetype=mine_type, resumable=True)
        body = {
            'name': os.path.split(file_name)[-1],
            'mimeType': "text/csv",
            'parents': [folder_id],
        }
        return service.files().create(body=body, media_body=media_body).execute()

    def __get_service(self) -> object:
        credentials = self._credentials
        http = credentials.authorize(httplib2.Http())
        return discovery.build('drive', self.DRIVE_API_VER, http=http)

    @staticmethod
    def __create_download_dir(dir_name) -> None:
        return os.makedirs(dir_name, 0o777, True)
