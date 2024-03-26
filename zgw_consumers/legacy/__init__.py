"""This module contains stuff from the legacy client.
For newer versions, please make use of the ape-pie client instead.
"""

try:
    import zds_client  # noqa
except ImportError:
    print(
        "The legacy package requires the zds_client package to be installed. "
        "Use `pip install zgw-consumers[zds-client]`."
    )
    raise
