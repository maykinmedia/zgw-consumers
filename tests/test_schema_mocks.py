import os

import pytest

from zgw_consumers.test import mock_service_oas_get, read_schema
from zgw_consumers.test.schema_mock import _clear_cache

TESTS_DIR = os.path.abspath(os.path.dirname(__file__))


@pytest.mark.parametrize("schema", ["dummy", "schema"])
def test_exception_raised_not_found(settings, schema):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = []

    with pytest.raises(IOError):
        read_schema(schema)


@pytest.mark.parametrize("name", ["dummy", "schema"])
def test_read_schema_from_dirs(settings, name):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [
        os.path.join(TESTS_DIR, "schemas"),
        os.path.join(TESTS_DIR, "schemas", "nested"),
    ]

    schema = read_schema(name)
    _clear_cache()

    assert f"name: {name}".encode("utf-8") in schema
