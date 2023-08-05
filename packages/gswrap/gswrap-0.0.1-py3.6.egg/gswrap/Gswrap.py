#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Google Drive REST API wrapper class.
Have a nice day:D
"""

import httplib2

from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient import discovery


class Gswrap:
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    DRIVE_API_VER = 'v4'
    APPLICATION_NAME = "gswrap"

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

    def get_value(self, spreadsheet_id: str, range_name: str) -> dict:
        """
        get value by range
        :param spreadsheet_id:
        :param range_name:
        :return:
        """
        service = self.__get_service()
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        return result.get('values', [])

    def __get_service(self) -> object:
        credentials = self._credentials
        http = credentials.authorize(httplib2.Http())
        discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                        'version=v4')
        return discovery.build('sheets', self.DRIVE_API_VER, http=http, discoveryServiceUrl=discovery_url)
