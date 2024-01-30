from datetime import date

import pytest

from zgw_consumers.api_models.catalogi import Catalogus, InformatieObjectType
from zgw_consumers.client import build_client
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service
from zgw_consumers.service import get_catalogi, get_informatieobjecttypen

pytestmark = pytest.mark.django_db


CATALOGI_API_ROOT = "https://catalogi.example.org/api/v1/"
CATALOGI_API_ROOT2 = "https://catalogi2.example.org/api/v1/"


def test_get_catalogi(settings, requests_mock):
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

    service1 = Service.objects.create(
        api_type=APITypes.ztc,
        api_root=CATALOGI_API_ROOT,
    )
    service2 = Service.objects.create(
        api_type=APITypes.ztc,
        api_root=CATALOGI_API_ROOT2,
    )
    client1 = build_client(service1)
    client2 = build_client(service2)

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

    service1 = Service.objects.create(
        api_type=APITypes.ztc,
        api_root=CATALOGI_API_ROOT,
    )
    service2 = Service.objects.create(
        api_type=APITypes.ztc,
        api_root=CATALOGI_API_ROOT2,
    )
    client1 = build_client(service1)
    client2 = build_client(service2)

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
