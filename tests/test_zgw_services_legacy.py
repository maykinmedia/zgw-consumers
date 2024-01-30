from datetime import date
from pathlib import Path

from django.core.files.base import File

import pytest

from zgw_consumers.api_models.catalogi import Catalogus, InformatieObjectType
from zgw_consumers.constants import APITypes
from zgw_consumers.legacy.service import get_catalogi, get_informatieobjecttypen
from zgw_consumers.models import Service
from zgw_consumers.test import mock_service_oas_get

pytestmark = pytest.mark.django_db


CATALOGI_API_ROOT = "https://catalogi.example.org/api/v1/"
CATALOGI_API_ROOT2 = "https://catalogi2.example.org/api/v1/"
TESTS_DIR = Path(__file__).parent
OAS_PATH = Path(__file__).parent / "schemas" / "ztc.yaml"


def test_get_catalogi(settings, requests_mock):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, CATALOGI_API_ROOT, "books")
    requests_mock.get(
        f"{CATALOGI_API_ROOT}catalogussen",
        json={
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": f"{CATALOGI_API_ROOT}catalogussen/1",
                    "domein": "ABCDE",
                    "rsin": "000000000",
                    "contactpersoon_beheer_naam": "foo",
                },
                {
                    "url": f"{CATALOGI_API_ROOT}catalogussen/2",
                    "domein": "ABCDE",
                    "rsin": "000000000",
                    "contactpersoon_beheer_naam": "foo",
                },
            ],
        },
    )
    requests_mock.get(
        f"{CATALOGI_API_ROOT2}catalogussen",
        json={
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": f"{CATALOGI_API_ROOT2}catalogussen/1",
                    "domein": "ABCDE",
                    "rsin": "000000000",
                    "contactpersoon_beheer_naam": "foo",
                },
                {
                    "url": f"{CATALOGI_API_ROOT2}catalogussen/2",
                    "domein": "ABCDE",
                    "rsin": "000000000",
                    "contactpersoon_beheer_naam": "foo",
                },
            ],
        },
    )

    with open(OAS_PATH, "r") as oas_file:
        service1 = Service.objects.create(
            api_type=APITypes.ztc,
            api_root=CATALOGI_API_ROOT,
            oas_file=File(oas_file, name="schema.yaml"),
        )
        service2 = Service.objects.create(
            api_type=APITypes.ztc,
            api_root=CATALOGI_API_ROOT2,
            oas_file=File(oas_file, name="schema.yaml"),
        )
    client1 = service1.build_client()
    client2 = service2.build_client()

    catalogi = get_catalogi([client1, client2])

    expected = [
        Catalogus(
            url=f"{CATALOGI_API_ROOT}catalogussen/1",
            domein="ABCDE",
            rsin="000000000",
            contactpersoon_beheer_naam="foo",
            contactpersoon_beheer_emailadres="",
            contactpersoon_beheer_telefoonnummer="",
            besluittypen=[],
            informatieobjecttypen=[],
            zaaktypen=[],
        ),
        Catalogus(
            url=f"{CATALOGI_API_ROOT}catalogussen/2",
            domein="ABCDE",
            rsin="000000000",
            contactpersoon_beheer_naam="foo",
            contactpersoon_beheer_emailadres="",
            contactpersoon_beheer_telefoonnummer="",
            besluittypen=[],
            informatieobjecttypen=[],
            zaaktypen=[],
        ),
        Catalogus(
            url=f"{CATALOGI_API_ROOT2}catalogussen/1",
            domein="ABCDE",
            rsin="000000000",
            contactpersoon_beheer_naam="foo",
            contactpersoon_beheer_emailadres="",
            contactpersoon_beheer_telefoonnummer="",
            besluittypen=[],
            informatieobjecttypen=[],
            zaaktypen=[],
        ),
        Catalogus(
            url=f"{CATALOGI_API_ROOT2}catalogussen/2",
            domein="ABCDE",
            rsin="000000000",
            contactpersoon_beheer_naam="foo",
            contactpersoon_beheer_emailadres="",
            contactpersoon_beheer_telefoonnummer="",
            besluittypen=[],
            informatieobjecttypen=[],
            zaaktypen=[],
        ),
    ]

    assert catalogi == expected


def test_get_informatieobjecttypen(settings, requests_mock):
    settings.ZGW_CONSUMERS_TEST_SCHEMA_DIRS = [TESTS_DIR / "schemas"]
    mock_service_oas_get(requests_mock, CATALOGI_API_ROOT, "books")
    requests_mock.get(
        f"{CATALOGI_API_ROOT}catalogussen",
        json={
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": f"{CATALOGI_API_ROOT}catalogussen/1",
                    "domein": "ABCDE",
                    "rsin": "000000000",
                    "contactpersoon_beheer_naam": "foo",
                },
            ],
        },
    )
    requests_mock.get(
        f"{CATALOGI_API_ROOT2}catalogussen",
        json={
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": f"{CATALOGI_API_ROOT2}catalogussen/1",
                    "domein": "ABCDE",
                    "rsin": "000000000",
                    "contactpersoon_beheer_naam": "foo",
                },
            ],
        },
    )

    requests_mock.get(
        f"{CATALOGI_API_ROOT}informatieobjecttypen",
        json={
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": f"{CATALOGI_API_ROOT}informatieobjecttypen/1",
                    "catalogus": f"{CATALOGI_API_ROOT}catalogussen/1",
                    "omschrijving": "foo",
                    "vertrouwelijkheidaanduiding": "openbaar",
                    "begin_geldigheid": "2020-01-01",
                    "einde_geldigheid": None,
                    "concept": False,
                },
                {
                    "url": f"{CATALOGI_API_ROOT}informatieobjecttypen/2",
                    "catalogus": f"{CATALOGI_API_ROOT}catalogussen/1",
                    "omschrijving": "bar",
                    "vertrouwelijkheidaanduiding": "openbaar",
                    "begin_geldigheid": "2020-01-01",
                    "einde_geldigheid": None,
                    "concept": False,
                },
            ],
        },
    )
    requests_mock.get(
        f"{CATALOGI_API_ROOT2}informatieobjecttypen",
        json={
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "url": f"{CATALOGI_API_ROOT2}informatieobjecttypen/1",
                    "catalogus": f"{CATALOGI_API_ROOT2}catalogussen/1",
                    "omschrijving": "baz",
                    "vertrouwelijkheidaanduiding": "openbaar",
                    "begin_geldigheid": "2020-01-01",
                    "einde_geldigheid": None,
                    "concept": False,
                },
                {
                    "url": f"{CATALOGI_API_ROOT2}informatieobjecttypen/2",
                    "catalogus": f"{CATALOGI_API_ROOT2}catalogussen/1",
                    "omschrijving": "aaa",
                    "vertrouwelijkheidaanduiding": "openbaar",
                    "begin_geldigheid": "2020-01-01",
                    "einde_geldigheid": None,
                    "concept": False,
                },
            ],
        },
    )

    with open(OAS_PATH, "r") as oas_file:
        service1 = Service.objects.create(
            api_type=APITypes.ztc,
            api_root=CATALOGI_API_ROOT,
            oas_file=File(oas_file, name="schema.yaml"),
        )
        service2 = Service.objects.create(
            api_type=APITypes.ztc,
            api_root=CATALOGI_API_ROOT2,
            oas_file=File(oas_file, name="schema.yaml"),
        )
    client1 = service1.build_client()
    client2 = service2.build_client()

    informatieobjecttypen = get_informatieobjecttypen([client1, client2])

    catalogus1 = Catalogus(
        url=f"{CATALOGI_API_ROOT}catalogussen/1",
        domein="ABCDE",
        rsin="000000000",
        contactpersoon_beheer_naam="foo",
        contactpersoon_beheer_emailadres="",
        contactpersoon_beheer_telefoonnummer="",
        besluittypen=[],
        informatieobjecttypen=[],
        zaaktypen=[],
    )
    catalogus2 = Catalogus(
        url=f"{CATALOGI_API_ROOT2}catalogussen/1",
        domein="ABCDE",
        rsin="000000000",
        contactpersoon_beheer_naam="foo",
        contactpersoon_beheer_emailadres="",
        contactpersoon_beheer_telefoonnummer="",
        besluittypen=[],
        informatieobjecttypen=[],
        zaaktypen=[],
    )

    expected = [
        InformatieObjectType(
            url=f"{CATALOGI_API_ROOT}informatieobjecttypen/1",
            catalogus=catalogus1,
            omschrijving="foo",
            vertrouwelijkheidaanduiding="openbaar",
            begin_geldigheid=date(2020, 1, 1),
            einde_geldigheid=None,
            concept=False,
        ),
        InformatieObjectType(
            url=f"{CATALOGI_API_ROOT}informatieobjecttypen/2",
            catalogus=catalogus1,
            omschrijving="bar",
            vertrouwelijkheidaanduiding="openbaar",
            begin_geldigheid=date(2020, 1, 1),
            einde_geldigheid=None,
            concept=False,
        ),
        InformatieObjectType(
            url=f"{CATALOGI_API_ROOT2}informatieobjecttypen/1",
            catalogus=catalogus2,
            omschrijving="baz",
            vertrouwelijkheidaanduiding="openbaar",
            begin_geldigheid=date(2020, 1, 1),
            einde_geldigheid=None,
            concept=False,
        ),
        InformatieObjectType(
            url=f"{CATALOGI_API_ROOT2}informatieobjecttypen/2",
            catalogus=catalogus2,
            omschrijving="aaa",
            vertrouwelijkheidaanduiding="openbaar",
            begin_geldigheid=date(2020, 1, 1),
            einde_geldigheid=None,
            concept=False,
        ),
    ]

    assert informatieobjecttypen == expected
