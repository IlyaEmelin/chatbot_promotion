import urllib
import logging


from django.conf import settings
import environ
import requests

logger = logging.getLogger(__name__)

logging.info("Patch (ya-disk) to .env file : %s", settings.BASE_DIR.parent)
env = environ.Env(
    DISK_TOKEN=(str, "dummy-key-for-dev"),
)
environ.Env.read_env(env_file=settings.BASE_DIR.parent / ".env")
logging.info("End load .env")

YA_API_HOST = "https://cloud-api.yandex.net/"
DISK_TOKEN = env.str("DISK_TOKEN")
AUTH_HEADERS = {"Authorization": f"OAuth {DISK_TOKEN}"}
API_VERSION = "v1"
UPLOAD_PATH = "app:/{}"
REQUEST_UPLOAD_URL = f"{YA_API_HOST}" f"{API_VERSION}/disk/resources/upload"
REQUEST_DOWNLOAD_URL = (
    f"{YA_API_HOST}" f"{API_VERSION}/disk/resources/download"
)


def upload_file_and_get_url(file):
    """Функция загрузки файлов и получения URL для скачивания."""
    upload_url = requests.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params={"path": UPLOAD_PATH.format(file.name), "overwrite": "True"},
    ).json()["href"]
    location = urllib.parse.unquote(
        requests.put(
            data=file.read(),
            url=upload_url,
        ).headers["Location"]
    ).replace("/disk", "")
    download_url = requests.get(
        REQUEST_DOWNLOAD_URL,
        headers=AUTH_HEADERS,
        params={
            "path": location,
        },
    ).json()["href"]
    return download_url
