import copy

import pytest
from rest_framework.test import APIClient


@pytest.fixture()
def api_client(request) -> APIClient:
    client = APIClient()
    return client


@pytest.fixture(autouse=True)
def temp_private_root(tmp_path, settings):
    """
    Set up a custom private root location that gets cleared up after tests.

    Instead of using the in-memory approach of the unittest
    privates.test.temp_private_root helper, we can rely on pytest cleaning up the
    temporary directories here, so we use a real filesystem storage.
    """
    tmpdir = tmp_path / "private-media"
    tmpdir.mkdir()
    location = str(tmpdir)

    _original = copy.deepcopy(settings.STORAGES)
    new_storages = {
        **_original,
        "privates": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {
                **_original["privates"].get("OPTIONS", {}),
                "location": location,
            },
        },
    }
    settings.STORAGES = new_storages
    settings.SENDFILE_ROOT = location
    return settings
