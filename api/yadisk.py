import io, base64
from PIL import Image
import os
import urllib

import requests
from django.core.files.base import ContentFile
from dotenv import load_dotenv


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


def upload_files_to_yadisk(files, filename_prefix):
    """Функция преобразования и запуска загрузки файлов."""
    urls = []
    for i,file in enumerate(files):
        if isinstance(file, str) and file.startswith('data:image'):
            format, imgstr = file.split(';base64,')
            ext = format.split('/')[-1]
            file = ContentFile(base64.b64decode(imgstr), name=f'{filename_prefix}_{i:02}.' + ext)
        urls.append(upload_file_and_get_url(file))
    return urls


def upload_file_and_get_url(file):
    """Функция загрузки файлов и получения URL для скачивания."""
    upload_url = requests.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={
            # 'path': UPLOAD_PATH.format(file.filename),
            'path': UPLOAD_PATH.format(file.name),
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
    return download_url
    # return dict(filename=file.name, url=download_url)
