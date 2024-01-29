import pytest

from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service
from zgw_consumers.service import pagination_helper

pytestmark = pytest.mark.django_db

BOOK_API_ROOT = "https://book.example.org/api/v1/"


def test_paginated_results(settings, requests_mock):
    """
    check that function works and doesn't fall into infinite loop
    """
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
    )
    client = build_client(service)

    response = client.get("books")
    response.raise_for_status()
    data = response.json()

    all_data = pagination_helper(client, data)

    assert list(all_data) == [{"name": "A"}, {"name": "B"}]


def test_paginated_results_without_next(settings, requests_mock):
    """
    check that function doesn't crash if next-link is missing
    """
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
    )
    client = build_client(service)

    response = client.get("books")
    response.raise_for_status()
    data = response.json()

    all_data = pagination_helper(client, data)

    assert list(all_data) == [{"name": "A"}]


def test_paginated_results_max_requests(settings, requests_mock):
    """
    check that function works and doesn't fall into infinite loop
    """
    requests_mock.get(
        f"{BOOK_API_ROOT}books",
        complete_qs=True,
        json={
            "count": 3,
            "next": f"{BOOK_API_ROOT}books?page=2",
            "previous": None,
            "results": [{"name": "A"}],
        },
    )
    requests_mock.get(
        f"{BOOK_API_ROOT}books?page=2",
        complete_qs=True,
        json={
            "count": 3,
            "next": f"{BOOK_API_ROOT}books?page=3",
            "previous": f"{BOOK_API_ROOT}books?page=1",
            "results": [{"name": "B"}],
        },
    )
    requests_mock.get(
        f"{BOOK_API_ROOT}books?page=3",
        complete_qs=True,
        json={
            "count": 3,
            "next": None,
            "previous": f"{BOOK_API_ROOT}books?page=2",
            "results": [{"name": "C"}],
        },
    )

    service = Service.objects.create(
        api_type=APITypes.orc,
        api_root=BOOK_API_ROOT,
    )
    client = build_client(service)

    response = client.get("books")
    response.raise_for_status()
    data = response.json()

    all_data = pagination_helper(client, data, max_requests=1)

    assert list(all_data) == [{"name": "A"}, {"name": "B"}]
