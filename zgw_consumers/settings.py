from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

from .constants import NLXDirectories

NLX_DIRECTORY_URLS = {
    NLXDirectories.demo: "https://directory.demo.nlx.io/",
    NLXDirectories.preprod: "https://directory.preprod.nlx.io/",
    NLXDirectories.prod: "https://directory.prod.nlx.io/",
}

NLX_OUTWAY_TIMEOUT = 2  # 2 seconds

ZGW_CONSUMERS_OAS_CACHE = DEFAULT_CACHE_ALIAS
"""
Deprecated.
"""

ZGW_CONSUMERS_CLIENT_CLASS = "zgw_consumers.legacy.client.ZGWClient"
"""
Deprecated.
"""

ZGW_CONSUMERS_TEST_SCHEMA_DIRS = []
"""
Deprecated.
"""

ZGW_CONSUMERS_IGNORE_OAS_FIELDS = False
"""
When enabled, the OAS URL/file field uploads are excluded from the admin.

The OAS information is only relevant for legacy usage of zds-client, which exposes
operations based on the operations in the API. This didn't work well in practice, so
the requirement of OpenAPI specs was dropped. Enable this if you are not using legacy/
deprecated features.

This is a temporary setting that will be removed in 1.0 when zds-client support will be
dropped entirely.
"""


def get_setting(name: str):
    default = globals()[name]
    return getattr(settings, name, default)
