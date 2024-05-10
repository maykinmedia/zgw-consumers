from django.core.exceptions import ValidationError

import pytest
import requests_mock
from ape_pie import APIClient

from zgw_consumers.client import ServiceConfigAdapter
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
def test_health_check_indication_service_model_badly_configured(settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_health_check_endpoint="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )
    adapter = ServiceConfigAdapter(service)
    client = APIClient.configure_from(adapter)

    with requests_mock.Mocker() as m, client:
        m.get(
            "https://example.com/foo",
            status_code=404,
        )
        service.refresh_from_db()
        assert service.get_health_check_indication == False


@pytest.mark.django_db
def test_health_check_indication_service_model_correctly_configured(settings):
    service = ServiceFactory.create(
        api_root="https://example.com/",
        api_health_check_endpoint="foo",
        auth_type=AuthTypes.zgw,
        client_id="my-client-id",
        secret="my-secret",
    )
    adapter = ServiceConfigAdapter(service)
    client = APIClient.configure_from(adapter)

    with requests_mock.Mocker() as m, client:
        m.get(
            "https://example.com/foo",
            status_code=200,
        )
        service.refresh_from_db()
        assert service.get_health_check_indication == True
