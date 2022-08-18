from django.urls import reverse

import pytest

from testapp.models import Case
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

pytestmark = pytest.mark.django_db

CASETYPE_API_ROOT = "https://casetype.example.org/api/v1/"
CASETYPE = f"{CASETYPE_API_ROOT}casetype/1"


def test_api_read(api_client):
    Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)
    case = Case.objects.create(casetype=CASETYPE)
    url = reverse("case-detail", kwargs={"pk": case.pk})

    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data == {
        "url": f"http://testserver{url}",
        "casetype": CASETYPE,
    }


def test_api_create(api_client):
    url = reverse("case-list")
    Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)
    data = {"casetype": CASETYPE}

    response = api_client.post(url, data)

    assert response.status_code == 201
    case = Case.objects.get()
    assert case.casetype == CASETYPE


def test_api_create_invalid_url(api_client):
    url = reverse("case-list")
    data = {"casetype": "some-casetype"}

    response = api_client.post(url, data)

    assert response.status_code == 400
    assert response.data["casetype"][0].code == "invalid"


def test_api_create_invalid_service(api_client):
    url = reverse("case-list")
    data = {"casetype": "https://other-casetype.example.org/api/v1/casetype/5"}

    response = api_client.post(url, data)

    assert response.status_code == 400
    assert response.data["casetype"][0].code == "unknown_service"
