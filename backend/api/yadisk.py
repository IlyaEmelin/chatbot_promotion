import logging
import urllib

import requests
from rest_framework import status

logger = logging.getLogger(__name__)


UPLOAD_URL_ERROR = "Ошибка при получении URL для загрузки файла: {}"
UPLOAD_ERROR = "Ошибка при загрузке файла: {}"
DOWNLOAD_URL_ERROR = "Ошибка при получении URL для скачивания файла: {}"
EXIST_ERROR = "Ошибка при проверке существования файла: {}"


class YandexDiskUploader:
    """Класс для загрузки файлов на Яндекс-диск"""

    def __init__(self, token):
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {token}"}
        self.upload_path = "app:/{}"

    def get_upload_url(self, filename):
        """Метод получения URL для загрузки файла"""
        try:
            response = requests.get(
                f"{self.base_url}/resources/upload",
                headers=self.headers,
                params={
                    "path": self.upload_path.format(filename),
                    "overwrite": "true",
                },
            )
            response.raise_for_status()
            return response.json().get("href")
        except Exception as e:
            logging.error(UPLOAD_URL_ERROR.format(e))
            return None

    def upload_file(self, filename, file_data):
        """Метод загрузки файла на Яндекс-диск"""
        upload_url = self.get_upload_url(filename)
        if not upload_url:
            return False
        try:
            logging.debug("Попытка загрузки файла")
            response = requests.put(upload_url, data=file_data)
            response.raise_for_status()
            return self.get_download_url(
                urllib.parse.unquote(response.headers["Location"]).replace(
                    "/disk", ""
                )
            )
        except Exception as e:
            logging.error(UPLOAD_ERROR.format(e))
            return False

    def get_download_url(self, file_path):
        """Метод получения URL для скачивания файла с Яндекс-диска"""
        try:
            logging.debug("Попытка получить URL для скачивания")
            response = requests.get(
                f"{self.base_url}/resources/download",
                headers=self.headers,
                params={"path": file_path},
            )
            response.raise_for_status()
            return response.json().get("href")
        except requests.RequestException as e:
            logging.error(DOWNLOAD_URL_ERROR.format(e))
            return False

    def check_file_exists(self, file_path):
        """Метод проверки существования файла"""
        try:
            response = requests.get(
                f"{self.base_url}/resources",
                headers=self.headers,
                params={"path": file_path},
            )
            return response.status_code == status.HTTP_200_OK
        except Exception as e:
            logging.error(EXIST_ERROR.format(e))
            return False
