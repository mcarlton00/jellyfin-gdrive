from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import time
import requests
import json


def load_config():
    # Reads local config file
    with open('config.json', 'r', encoding='utf-8') as jsonConfig:
        config = json.load(jsonConfig)

        return config


def update_library(config):
    # Triggers a file rescan in Jellyfin
    url = config.get('jellyfin_server')
    api_key = config.get('api_key')
    retries = config.get('retries')

    headers = {'X-Emby-Token': api_key}

    retry_count = 0

    try:
        print('Triggering file scan in Jellyfin')
        r = requests.post(f'{url}/Library/Refresh', headers=headers)
        r.raise_for_status()
    except Exception as e:
        retry_count += 1
        if(retry_count < retries):
            retry_count += 1
            print(f'Error: {e}')
            print(f'Trying again, attempt # {retry_count}')
            time.sleep(1)
        else:
            print(f'Unable to submit request to Jellyfin after retries')
            return False


def main():

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']

    # load config file
    config = load_config()
    check_interval = config.get('check_interval')

    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Google API uses UTC time
    checkTime = datetime.datetime.utcnow()

    # Connect to Google API
    service = build('drive', 'v3', credentials=creds)

    # Trigger a library refresh on startup to catch updates while the
    # program wasn't running
    update_library(config)

    # Loop forever until program is killed
    while True:
        # Update the time used to check for changes
        checkTime = datetime.datetime.utcnow()
        time.sleep(check_interval * 60)

        # Google wants dates in iso8601 format
        checkTimeIso = checkTime.isoformat()

        # Finds audio and video files updated after the last run
        # Reference: https://developers.google.com/drive/api/v3/reference/files/list?apix_params=%7B%22q%22%3A%22mimeType%20contains%20%27video%2F%27%22%2C%22fields%22%3A%22files(id%2C%20name%2C%20modifiedTime)%22%2C%22prettyPrint%22%3Atrue%7D
        results = service.files().list(
            fields="files(name)",
            q=f"(mimeType contains 'video/' or mimeType contains 'audio/') and"
            f" modifiedTime > '{checkTimeIso}'").execute()
        items = results.get('files', [])
        if not items:
            print('No updates found.')
        else:
            # Updates found, trigger library update
            num_files = len(items)
            print(f'Found {num_files} update(s)')
            update_library(config)


if __name__ == '__main__':
    main()
