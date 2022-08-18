import pytest
from rest_framework.test import APIClient
from zds_client.oas import schema_fetcher

SCHEMA = """
openapi: 3.0.0
some: yaml
"""


class _oas:
    def __init__(self, url, mocker):
        self.url = url
        self.mocker = mocker

    def fetch(self):
        return schema_fetcher.fetch(self.url)


@pytest.fixture()
def oas(requests_mock):
    schema_fetcher.cache.clear()

    url = "https://example.com/schema.yaml"
    requests_mock.get(url, text=SCHEMA)
    yield _oas(url, mocker=requests_mock)

    # cleanup
    schema_fetcher.cache.clear()


@pytest.fixture()
def api_client(request) -> APIClient:
    client = APIClient()
    return client
