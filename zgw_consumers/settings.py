from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

from .constants import NLXDirectories

NLX_DIRECTORY_URLS = {
    NLXDirectories.demo: "https://demo-directory-api.commonground.acc.utrecht.nl/",
    NLXDirectories.prod: "https://directory-api.commonground.utrecht.nl/",
}

NLX_OUTWAY_TIMEOUT = 2  # 2 seconds


def get_setting(name: str):
    default = globals()[name]
    return getattr(settings, name, default)
