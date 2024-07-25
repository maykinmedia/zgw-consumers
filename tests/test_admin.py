from django.test import Client
from django.urls import reverse

import requests
import requests_mock
from pytest_django.asserts import assertContains

from zgw_consumers.constants import AuthTypes
from zgw_consumers.test.factories import ServiceFactory


def test_oas_fields_enabled(admin_client: Client, settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = False
    url = reverse("admin:zgw_consumers_service_add")

    response = admin_client.get(url)

    form = response.context["adminform"]

    assert "oas" in form.fields
    assert "oas_file" in form.fields


def test_oas_fields_disabled(admin_client: Client, settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True
    url = reverse("admin:zgw_consumers_service_add")

    response = admin_client.get(url)

    form = response.context["adminform"]

    assert "oas" not in form.fields
    assert "oas_file" not in form.fields


def test_get_connection_check_correct_status_code(admin_client: Client, settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_connection_check_path="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )
    with requests_mock.Mocker() as m:
        m.get("https://example.com/foo", status_code=401)
        url = reverse(
            "admin:zgw_consumers_service_change", kwargs={"object_id": service.id}
        )
        response = admin_client.get(url)

        connection_check_inner_html = '<label>Connection check status code:</label><div class="readonly">401</div>'
        assertContains(response, connection_check_inner_html, html=True)


def test_get_connection_check_encountering_error(admin_client: Client, settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_connection_check_path="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )
    with requests_mock.Mocker() as m:
        m.get("https://example.com/foo", exc=requests.RequestException)
        url = reverse(
            "admin:zgw_consumers_service_change", kwargs={"object_id": service.id}
        )
        response = admin_client.get(url)

        connection_check_inner_html = '<label>Connection check status code:</label><div class="readonly">None</div>'
        assertContains(response, connection_check_inner_html, html=True)


def test_get_connection_check_not_configured(admin_client: Client, settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )
    with requests_mock.Mocker() as m:
        m.get("https://example.com/", status_code=200)
        url = reverse(
            "admin:zgw_consumers_service_change", kwargs={"object_id": service.id}
        )
        response = admin_client.get(url)

        connection_check_inner_html = '<label>Connection check status code:</label><div class="readonly">200</div>'
        assertContains(response, connection_check_inner_html, html=True)


def test_get_connection_opening_add_page(admin_client: Client, settings):
    url = reverse("admin:zgw_consumers_service_add")
    response = admin_client.get(url)

    connection_check_inner_html = (
        '<label>Connection check status code:</label><div class="readonly">n/a</div>'
    )
    assertContains(response, connection_check_inner_html, html=True)
