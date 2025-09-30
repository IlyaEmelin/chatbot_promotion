import logging
import urllib

import requests
from rest_framework import status

logger = logging.getLogger(__name__)


TOKEN_ERROR = "Ошибка авторизации (возможно, неверный токен)."
UPLOAD_URL_MSG = "Попытка получить URL для загрузки файла"
UPLOAD_URL_ERROR = "Ошибка при получении URL для загрузки файла: {}"
UPLOAD_MSG = "Попытка загрузки файла"
UPLOAD_ERROR = "Ошибка при загрузке файла: {}"
DOWNLOAD_URL_MSG = "Попытка получить URL для скачивания"
DOWNLOAD_URL_ERROR = "Ошибка при получении URL для скачивания файла: {}"
EXIST_MSG = "Попытка проверить существование файла"
EXIST_ERROR = "Ошибка при проверке существования файла: {}"


class YandexDiskUploader:
    """Класс для загрузки файлов на Яндекс-диск"""

    class TokenError(Exception):
        """Класс исключений, возникающих при отсутствии ."""

    class UploadUrlError(Exception):
        """Класс исключений, возникающих при запросе ссылки на загрузку."""

    class UploadError(Exception):
        """Класс исключений, возникающих при загрузке файла."""

    class DownloadUrlError(Exception):
        """Класс исключений, возникающих при запросе ссылки на скачивание."""

    class FileCheckError(Exception):
        """Класс исключений, возникающих при проверке существования файла."""

    def __init__(self, token):
        self.base_url = "https://cloud-api.yandex.net/v1/disk"
        self.headers = {"Authorization": f"OAuth {token}"}
        self.upload_path = "app:/{}"

    def get_upload_url(self, filename):
        """Метод получения URL для загрузки файла"""
        try:
            logging.debug(UPLOAD_URL_MSG)
            response = requests.get(
                f"{self.base_url}/resources/upload",
                headers=self.headers,
                params={
                    "path": self.upload_path.format(filename),
                    "overwrite": "true",
                },
            )
            if response.status_code in (401, 403):
                logging.error(TOKEN_ERROR)
                raise self.TokenError(TOKEN_ERROR)
            response.raise_for_status()
            return response.json().get("href")
        except Exception as e:
            logging.error(UPLOAD_URL_ERROR.format(e))
            raise self.UploadUrlError(UPLOAD_URL_ERROR.format(e))

    def upload_file(self, filename, file_data):
        """Метод загрузки файла на Яндекс-диск"""
        upload_url = self.get_upload_url(filename)
        try:
            logging.debug(UPLOAD_MSG)
            response = requests.put(upload_url, data=file_data)
            response.raise_for_status()
            return self.get_download_url(
                urllib.parse.unquote(response.headers["Location"]).replace(
                    "/disk", ""
                )
            )
        except Exception as e:
            logging.error(UPLOAD_ERROR.format(e))
            raise self.UploadError(UPLOAD_ERROR.format(e))

    def get_download_url(self, file_path):
        """Метод получения URL для скачивания файла с Яндекс-диска"""
        try:
            logging.debug(DOWNLOAD_URL_MSG)
            response = requests.get(
                f"{self.base_url}/resources/download",
                headers=self.headers,
                params={"path": file_path},
            )
            response.raise_for_status()
            return response.json().get("href")
        except requests.RequestException as e:
            logging.error(DOWNLOAD_URL_ERROR.format(e))
            raise self.DownloadUrlError(DOWNLOAD_URL_ERROR.format(e))

    def check_file_exists(self, file_path):
        """Метод проверки существования файла"""
        try:
            logging.debug(EXIST_MSG)
            response = requests.get(
                f"{self.base_url}/resources",
                headers=self.headers,
                params={"path": file_path},
            )
            return response.status_code == status.HTTP_200_OK
        except Exception as e:
            logging.error(EXIST_ERROR.format(e))
            raise self.FileCheckError(EXIST_ERROR.format(e))
