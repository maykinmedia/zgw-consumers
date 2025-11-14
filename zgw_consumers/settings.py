import os

from django.conf import settings

from .constants import NLXDirectories

NLX_OUTWAY_TIMEOUT = 2  # 2 seconds

NLX_DIRECTORY_URLS = {
    NLXDirectories.demo: os.getenv(
        "NLX_DIRECTORY_URL_DEMO",
        "https://nlx-directory-ui.commonground.acc.utrecht.nl/",
    ),
    NLXDirectories.prod: os.getenv(
        "NLX_DIRECTORY_URL_PROD",
        "https://nlx-directory-ui.commonground.utrecht.nl/",
    ),
}


def get_setting(name: str):
    default = globals()[name]
    return getattr(settings, name, default)
