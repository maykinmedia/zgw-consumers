from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytest

from zgw_consumers.api_models.base import Model, factory
from zgw_consumers.api_models.catalogi import ZaakType
from zgw_consumers.api_models.zaken import Zaak


def test_absent_keys_for_optional_fields() -> None:
    @dataclass
    class TestModel(Model):
        required_field: str
        optional_field: Optional[datetime] = None

    data = {"requiredField": "a value"}

    instance = factory(TestModel, data)

    assert instance.required_field == "a value"
    assert instance.optional_field is None


def test_absent_keys_for_zaaktype() -> None:
    data = {
        "aanleiding": "Voorbeeld",
        "doel": "Voorbeeld",
        "handelingBehandelaar": None,
        "handelingInitiator": "Melden",
        "identificatie": "6",
        "indicatieInternOfExtern": "intern",
        "omschrijving": "Aangeven",
        "onderwerp": "Aangeven",
        "url": "https://uniek-url",
        "vertrouwelijkheidaanduiding": "openbaar",
    }

    # multiple keys are missing that are required in the API spec
    with pytest.raises(TypeError):
        factory(ZaakType, data)


def test_absent_keys_for_zaak() -> None:
    data = {
        "bronorganisatie": "CHANGEME",
        "einddatumGepland": "2022-08-22",
        "identificatie": "0014XXXX55222022",
        "omschrijving": "Test 1. XXXXX",
        "registratiedatum": "2022-07-28",
        "startdatum": "2022-07-28",
        "url": "https://uniek-url",
        "uuid": "53d12522-6cb5-583e-b6f6-7c17a2fcd440",
        "verantwoordelijkeOrganisatie": "CHANGEME",
        "zaaktype": "https://uniek-url",
    }

    # 'vertrouwelijkheidaanduiding' is missing
    with pytest.raises(TypeError):
        factory(Zaak, data)
