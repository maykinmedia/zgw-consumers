from uuid import uuid4

from django.test import Client
from django.urls import reverse

import pytest
import requests
import requests_mock
from pytest_django.asserts import assertContains

from zgw_consumers.constants import AuthTypes
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory


def test_get_connection_check_correct_status_code(admin_client: Client, settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_connection_check_path="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret-that-is-sufficiently-long-enough",
    )
    with requests_mock.Mocker() as m:
        m.get("https://example.com/foo", status_code=401)
        url = reverse(
            "admin:zgw_consumers_service_change", kwargs={"object_id": service.id}
        )
        response = admin_client.get(url)

        connection_check_inner_html = (
            "<label>Connection check status code:</label>"
            '<div class="readonly">401</div>'
        )
        assertContains(response, connection_check_inner_html, html=True)


def test_get_connection_check_encountering_error(admin_client: Client, settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_connection_check_path="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret-that-is-sufficiently-long-enough",
    )
    with requests_mock.Mocker() as m:
        m.get("https://example.com/foo", exc=requests.RequestException)
        url = reverse(
            "admin:zgw_consumers_service_change", kwargs={"object_id": service.id}
        )
        response = admin_client.get(url)

        connection_check_inner_html = (
            "<label>Connection check status code:</label>"
            '<div class="readonly">None</div>'
        )
        assertContains(response, connection_check_inner_html, html=True)


def test_get_connection_check_not_configured(admin_client: Client, settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret-that-is-sufficiently-long-enough",
    )
    with requests_mock.Mocker() as m:
        m.get("https://example.com/", status_code=200)
        url = reverse(
            "admin:zgw_consumers_service_change", kwargs={"object_id": service.id}
        )
        response = admin_client.get(url)

        connection_check_inner_html = (
            "<label>Connection check status code:</label>"
            '<div class="readonly">200</div>'
        )
        assertContains(response, connection_check_inner_html, html=True)


def test_get_connection_opening_add_page(admin_client: Client, settings):
    url = reverse("admin:zgw_consumers_service_add")
    response = admin_client.get(url)

    connection_check_inner_html = (
        '<label>Connection check status code:</label><div class="readonly">n/a</div>'
    )
    assertContains(response, connection_check_inner_html, html=True)


def test_custom_exception_in_connection_check_is_handled(admin_client: Client):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_connection_check_path="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret-that-is-sufficiently-long-enough",
    )

    with requests_mock.Mocker() as m:
        m.get("https://example.com/foo", exc=Exception)

        url = reverse(
            "admin:zgw_consumers_service_change", kwargs={"object_id": service.id}
        )
        response = admin_client.get(url)

        connection_check_inner_html = (
            "<label>Connection check status code:</label>"
            '<div class="readonly">None</div>'
        )
        assertContains(response, connection_check_inner_html, html=True)


@pytest.mark.parametrize(
    "secret,errors",
    [
        ("", {"secret": ["The field 'secret' is required for ZGW authorization"]}),
        ("my-secret", {}),
    ],
)
def test_zgw_auth_requires_secret(admin_client: Client, secret, errors):
    url = reverse("admin:zgw_consumers_service_add")
    data = {
        "label": "Zaken API",
        "slug": "zaken-api",
        "uuid": str(uuid4()),
        "api_type": "zrc",
        "api_root": "https://example.com/api/v1/",
        "auth_type": AuthTypes.zgw,
        "client_id": "my-client-id",
        "secret": secret,
        "timeout": 10,
        "jwt_valid_for": 43200,
    }

    response = admin_client.post(url, data)

    if errors:
        assert response.status_code == 200
        assert response.context["adminform"].form.errors == errors
        assert not Service.objects.exists()
    else:
        assert response.status_code == 302
        assert Service.objects.get().secret == secret
