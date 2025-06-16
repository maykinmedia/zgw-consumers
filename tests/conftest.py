import pytest
from rest_framework.test import APIClient


@pytest.fixture()
def api_client(request) -> APIClient:
    client = APIClient()
    return client


@pytest.fixture()
def temp_private_root(tmp_path, settings):
    tmpdir = tmp_path / "private-media"
    tmpdir.mkdir()
    location = str(tmpdir)
    settings.PRIVATE_MEDIA_ROOT = location
    settings.SENDFILE_ROOT = location
    return settings
