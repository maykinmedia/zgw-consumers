from pathlib import Path

import pytest

from zgw_consumers.constants import APITypes
from zgw_consumers.legacy.service import get_paginated_results
from zgw_consumers.models import Service
from zgw_consumers.test import mock_service_oas_get

pytestmark = pytest.mark.django_db

TESTS_DIR = Path(__file__).parent
BOOK_API_ROOT = "https://book.example.org/api/v1/"


def test_paginated_results(settings, requests_mock):
    """
    check that function works and doesn't fall into infinite loop
    """
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, BOOK_API_ROOT, "books")
    requests_mock.get(
        f"{BOOK_API_ROOT}books",
        complete_qs=True,
        json={
            "count": 2,
            "next": f"{BOOK_API_ROOT}books?page=2",
            "previous": None,
            "results": [{"name": "A"}],
        },
    )
    requests_mock.get(
        f"{BOOK_API_ROOT}books?page=2",
        complete_qs=True,
        json={
            "count": 2,
            "next": None,
            "previous": f"{BOOK_API_ROOT}books?page=1",
            "results": [{"name": "B"}],
        },
    )

    service = Service.objects.create(
        api_type=APITypes.orc,
        api_root=BOOK_API_ROOT,
        oas=f"{BOOK_API_ROOT}schema/openapi.yaml?v=3",
    )
    client = service.build_client()

    result = get_paginated_results(client, "book")

    assert result == [{"name": "A"}, {"name": "B"}]


def test_paginated_results_without_next(settings, requests_mock):
    """
    check that function doesn't crash if next-link is missing
    """
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, BOOK_API_ROOT, "books")
    requests_mock.get(
        f"{BOOK_API_ROOT}books",
        complete_qs=True,
        json={
            "count": 2,
            "results": [{"name": "A"}],
        },
    )
    service = Service.objects.create(
        api_type=APITypes.orc,
        api_root=BOOK_API_ROOT,
        oas=f"{BOOK_API_ROOT}schema/openapi.yaml?v=3",
    )
    client = service.build_client()

    result = get_paginated_results(client, "book")

    assert result == [{"name": "A"}]
