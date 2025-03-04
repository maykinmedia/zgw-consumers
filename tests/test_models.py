from django.db import IntegrityError

import pytest
import requests_mock

from zgw_consumers.constants import AuthTypes
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory


@pytest.mark.django_db
def test_connection_check_service_model_badly_configured(settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_connection_check_path="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )

    with requests_mock.Mocker() as m:
        m.get(
            "https://example.com/foo",
            status_code=404,
        )
        service.refresh_from_db()
        assert service.connection_check == 404


@pytest.mark.django_db
def test_connection_check_service_model_correctly_configured(settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_connection_check_path="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )

    with requests_mock.Mocker() as m:
        m.get(
            "https://example.com/foo",
            status_code=200,
        )
        service.refresh_from_db()
        assert service.connection_check == 200


@pytest.mark.django_db
def test_can_get_service_by_natural_key():
    service = ServiceFactory.create()

    assert Service.objects.get_by_natural_key(*service.natural_key()) == service


@pytest.mark.django_db
def test_fields_making_up_natural_key_field_are_unique():
    ServiceFactory.create(slug="i-should-be-unique")

    with pytest.raises(IntegrityError):
        ServiceFactory.create(slug="i-should-be-unique")
