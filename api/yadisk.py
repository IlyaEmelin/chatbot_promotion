import asyncio
import os
import urllib

import requests
from dotenv import load_dotenv
import aiohttp


YA_API_HOST = 'https://cloud-api.yandex.net/'

load_dotenv()
DISK_TOKEN = os.environ.get('DISK_TOKEN')
AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}
API_VERSION = 'v1'
UPLOAD_PATH = 'app:/{}'
REQUEST_UPLOAD_URL = (f'{YA_API_HOST}'
                      f'{API_VERSION}/disk/resources/upload')
REQUEST_DOWNLOAD_URL = (f'{YA_API_HOST}'
                        f'{API_VERSION}/disk/resources/download')


def upload_files_to_yadisk(files):
    """Функция постановки задач на загрузку файлов."""
    [upload_file_and_get_url(file) for file in files]


def upload_file_and_get_url(file):
    """Функция загрузки файлов и получения URL для скачивания."""
    upload_url = requests.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={
            'path': UPLOAD_PATH.format(file.filename),
            'overwrite': 'True'
        },
    ).json()['href']
    location = urllib.parse.unquote(
        requests.put(
            data=file.read(),
            url=upload_url,
        ).headers['Location']
    ).replace('/disk', '')
    download_url = requests.get(
        REQUEST_DOWNLOAD_URL,
        headers=AUTH_HEADERS,
        params={'path': location, },
    ).json()['href']
    return dict(filename=file.filename, url=download_url)
