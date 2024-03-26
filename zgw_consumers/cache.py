"""
Replace the OAS schema cache with django's cache mechanism.
"""

from django.core.cache import caches

from typing_extensions import deprecated

from .settings import get_setting


class OASCache:
    KEY_PREFIX = "oas"
    DURATION = 60 * 60 * 24  # 24 hours

    @deprecated(
        "zds_client support is deprecated and scheduled for removal in 1.0. OpenAPI "
        "specification integration will be dropped as we don't require it anymore.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    def __init__(self):
        self.alias = get_setting("ZGW_CONSUMERS_OAS_CACHE")
        self._local_cache = {}  # in memory

    def __contains__(self, key: str):
        key = f"{self.KEY_PREFIX}:{key}"
        if key in self._local_cache:
            return True
        else:
            schema = caches[self.alias].get(key)
            if schema is None:
                return False

            self._local_cache[key] = schema
            return True

    def __getitem__(self, key: str):
        key = f"{self.KEY_PREFIX}:{key}"
        if key in self._local_cache:
            return self._local_cache[key]

    def __setitem__(self, key: str, value: dict):
        key = f"{self.KEY_PREFIX}:{key}"
        caches[self.alias].set(key, value, self.DURATION)
        self._local_cache[key] = value

    def clear(self):
        self._local_cache = {}  # reset in-memory cache
        caches[self.alias].clear()


def install_schema_fetcher_cache():
    try:
        from zds_client.oas import schema_fetcher
    except ImportError:
        return

    schema_fetcher.cache = OASCache()
