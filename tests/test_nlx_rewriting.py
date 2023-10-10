import pytest

from zgw_consumers.client import build_client
from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory

pytestmark = [pytest.mark.django_db]


def test_request_url_and_response_data_rewritten(requests_mock):
    nlx_service = ServiceFactory.create(
        label="Service with NLX",
        api_root="https://example.com/",
        auth_type=AuthTypes.no_auth,
        nlx="http://localhost:8081/:serial-number/:service/",
    )
    client = build_client(nlx_service)

    requests_mock.get(
        "http://localhost:8081/:serial-number/:service/some-resource",
        json=lambda req, _: {"url": req.url},
    )

    with client:
        response_data = client.get("some-resource").json()

    assert requests_mock.last_request.method == "GET"
    assert (
        requests_mock.last_request.url
        == "http://localhost:8081/:serial-number/:service/some-resource"
    )
    assert response_data == {"url": "https://example.com/some-resource"}


def test_non_json_response_data(requests_mock):
    nlx_service = ServiceFactory.create(
        label="Service with NLX",
        api_root="https://example.com/",
        auth_type=AuthTypes.no_auth,
        nlx="http://localhost:8081/:serial-number/:service/",
    )
    client = build_client(nlx_service)

    requests_mock.get(
        "http://localhost:8081/:serial-number/:service/some-resource",
        content=b"AAAAA",
    )

    with client:
        response_data = client.get("some-resource").content

    assert requests_mock.last_request.method == "GET"
    assert (
        requests_mock.last_request.url
        == "http://localhost:8081/:serial-number/:service/some-resource"
    )
    assert response_data == b"AAAAA"


def test_service_without_nlx(requests_mock):
    ServiceFactory.create(
        label="Service with NLX",
        api_root="https://example.com/",
        auth_type=AuthTypes.no_auth,
        nlx="http://localhost:8081/:serial-number/:service/",
    )
    normal_service = ServiceFactory.create(
        label="Service without NLX",
        api_root="https://second.example.com/",
        auth_type=AuthTypes.no_auth,
    )

    client = build_client(normal_service)
    requests_mock.get(
        "https://second.example.com/some-resource",
        json={"url": "https://example.com"},
    )

    with client:
        response_data = client.get("some-resource").json()

    assert requests_mock.last_request.method == "GET"
    assert requests_mock.last_request.url, "https://second.example.com/some-resource"
    # no rewriting of any sorts
    assert response_data, {"url": "https://example.com"}
