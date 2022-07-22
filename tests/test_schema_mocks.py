from pathlib import Path

import pytest
import requests

from zgw_consumers.test import mock_service_oas_get, read_schema
from zgw_consumers.test.schema_mock import _clear_cache

TESTS_DIR = Path(__file__).parent


@pytest.mark.parametrize("schema", ["dummy", "schema"])
def test_exception_raised_not_found(settings, schema):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = []

    with pytest.raises(IOError):
        read_schema(schema)


@pytest.mark.parametrize("name", ["dummy", "schema"])
def test_read_schema_from_dirs(settings, name):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [
        TESTS_DIR / "schemas",
        TESTS_DIR / "schemas" / "nested",
    ]

    schema = read_schema(name)
    _clear_cache()

    assert f"name: {name}".encode("utf-8") in schema


def test_mock_schema_get(settings, requests_mock):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, "https://example.com/api/v1/", "dummy")

    response = requests.get("https://example.com/api/v1/schema/openapi.yaml?v=3")

    assert response.content == b"openapi: 3.0.0\nname: dummy\n"
    assert requests_mock.call_count == 1
    assert (
        requests_mock.last_request.url
        == "https://example.com/api/v1/schema/openapi.yaml?v=3"
    )
