import json
from pathlib import Path

from django.core.files.base import ContentFile, File
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import pytest
from pyquery import PyQuery as pq

from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

API_ROOT = "https://example.com/api/v1/"
OAS_PATH = Path(__file__).parent / "schemas" / "ztc.yaml"
TESTS_DIR = Path(__file__).parent


@pytest.mark.django_db
def test_listzaaktypen_mixin_client_error(settings, admin_client, requests_mock):
    """
    Assert that an error message is displayed in the admin if ClientError 4xx is raised
    """
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]

    requests_mock.get(
        f"{API_ROOT}zaaktypen",
        status_code=403,
        json={
            "title": "Je hebt geen toestemming om deze actie uit te voeren.",
            "status": 403,
            "detail": "Client identifier bestaat niet",
        },
    )

    # set up service
    with open(OAS_PATH, "r") as oas_file:
        service = Service.objects.create(
            label="Test",
            api_type=APITypes.ztc,
            api_root=API_ROOT,
            oas_file=File(oas_file, name="schema.yaml"),
        )
        service.full_clean()

    # assert that admin page works despite ClientError
    url = reverse("admin:testapp_zgwconfig_change")
    response = admin_client.get(url)
    assert response.status_code == 200

    html = response.content.decode("utf-8")
    doc = pq(html)

    # assert that appropriate error message is displayed
    error = doc(".error")[0]
    assert error.text == _(
        "Failed to retrieve available zaaktypen (got {http_status} - {detail}). "
        "The cause of this exception was: {cause}"
    ).format(
        http_status=403,
        detail="Client identifier bestaat niet",
        cause=f"403 Client Error: None for url: {API_ROOT}zaaktypen",
    )

    # assert that Zaaktype field is present in admin page despite ClientError
    zaaktypen_label = doc.find("label")
    assert zaaktypen_label.text() == "Zaaktype:"


@pytest.mark.django_db
def test_listzaaktypen_mixin_server_error(settings, admin_client, requests_mock):
    """
    Assert that an error message is displayed in the admin if HTTPError 500 is raised
    """
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]

    requests_mock.get(
        f"{API_ROOT}zaaktypen",
        status_code=500,
    )

    # set up service
    with open(OAS_PATH, "r") as oas_file:
        service = Service.objects.create(
            label="Test",
            api_type=APITypes.ztc,
            api_root=API_ROOT,
            oas_file=File(oas_file, name="schema.yaml"),
        )
        service.full_clean()

    # assert that admin page works despite HTTPError
    url = reverse("admin:testapp_zgwconfig_change")
    response = admin_client.get(url)
    assert response.status_code == 200

    html = response.content.decode("utf-8")
    doc = pq(html)

    # assert that appropriate error message is displayed
    error = doc(".error")[0]
    assert error.text == _("500 Server Error: None for url: {url}").format(
        url=f"{API_ROOT}zaaktypen"
    )

    # assert that Zaaktype field is present in admin page despite HTTPError
    zaaktypen_label = doc.find("label")
    assert zaaktypen_label.text() == "Zaaktype:"


@pytest.mark.django_db
def test_listzaaktypen_unexpected_operation_id(settings, admin_client, requests_mock):
    requests_mock.get(
        f"{API_ROOT}zaaktypen",
        status_code=200,
        json={"results": [], "count": 0, "next": None},
    )

    service = Service.objects.create(
        label="Test",
        api_type=APITypes.ztc,
        api_root=API_ROOT,
        oas_file=ContentFile(
            json.dumps(
                {
                    "openapi": "3.0.1",
                    "info": {"title": "Catalogi API 1.0", "version": "1.0"},
                    "paths": {
                        "/api/v1/zaaktypen": {
                            "get": {
                                "tags": ["ZaakType"],
                                "summary": "Alle ZAAKTYPEn opvragen.\r\nDeze lijst kan gefilterd wordt met query-string parameters.",
                                "description": "",
                                "operationId": "ZaakTypeGetAll",  # Operation ID different from zaaktype_list
                                "responses": {
                                    "200": {"description": "OK"},
                                    "401": {"description": "Unauthorized"},
                                },
                            }
                        }
                    },
                }
            ),
            name="schema.yaml",
        ),
    )
    service.full_clean()

    # assert that admin page works despite an operation ID different from zaaktype_list
    url = reverse("admin:testapp_zgwconfig_change")
    response = admin_client.get(url)

    assert response.status_code == 200
