from django.core.exceptions import ValidationError
from django.db import IntegrityError

import pytest
import requests_mock

from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory


def test_model_validation_with_oas_fields_enabled_none_provided(settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = False
    service = Service(
        label="test",
        api_type=APITypes.orc,
        api_root="https://example.com/api/",
        auth_type=AuthTypes.no_auth,
        oas="",
        oas_file="",
    )

    with pytest.raises(ValidationError) as exc_context:
        service.clean()

    error_dict = exc_context.value.error_dict
    assert "oas" in error_dict
    assert "oas_file" in error_dict


def test_model_validation_with_oas_fields_enabled_both_provided(settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = False
    service = Service(
        label="test",
        api_type=APITypes.orc,
        api_root="https://example.com/api/",
        auth_type=AuthTypes.no_auth,
        oas="https://example.com/api/schema.json",
        oas_file="schema.json",
    )

    with pytest.raises(ValidationError) as exc_context:
        service.clean()

    error_dict = exc_context.value.error_dict
    assert "oas" in error_dict
    assert "oas_file" in error_dict


def test_model_validation_with_oas_fields_disabled_none_provided(settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True
    service = Service(
        label="test",
        api_type=APITypes.orc,
        api_root="https://example.com/api/",
        auth_type=AuthTypes.no_auth,
        oas="",
        oas_file="",
    )

    try:
        service.clean()
    except ValidationError:
        pytest.fail("OAS fields should be ignored")


def test_model_validation_with_oas_fields_disabled_both_provided(settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True
    service = Service(
        label="test",
        api_type=APITypes.orc,
        api_root="https://example.com/api/",
        auth_type=AuthTypes.no_auth,
        oas="https://example.com/api/schema.json",
        oas_file="schema.json",
    )

    try:
        service.clean()
    except ValidationError:
        pytest.fail("OAS fields should be ignored")


@pytest.mark.django_db
def test_connection_check_service_model_badly_configured(settings):
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True
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
    settings.ZGW_CONSUMERS_IGNORE_OAS_FIELDS = True
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
