import pytest
from django_setup_configuration.test_utils import load_step_config_from_source

from zgw_consumers.contrib.setup_configuration.steps import ServiceConfigurationStep
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory

CONFIG_FILE_PATH = "tests/files/setup_config_services.yaml"


@pytest.fixture()
def step_config_model():
    return load_step_config_from_source(ServiceConfigurationStep, CONFIG_FILE_PATH)


@pytest.mark.django_db
def test_execute_configuration_step_success(step_config_model):
    step = ServiceConfigurationStep()

    assert not step.is_configured(step_config_model)

    step.execute(step_config_model)

    assert Service.objects.count() == 2

    objects_service, zaken_service = Service.objects.all()

    assert objects_service.slug == "objecten-test"
    assert objects_service.label == "Objecten API test"
    assert objects_service.api_root == "http://objecten.local/api/v1/"
    assert objects_service.api_type == "orc"
    assert objects_service.auth_type == "api_key"
    assert objects_service.header_key == "Authorization"
    assert objects_service.header_value == "Token foo"
    assert objects_service.timeout == 10

    assert zaken_service.slug == "zaken-test"
    assert zaken_service.label == "Zaken API test"
    assert zaken_service.api_root == "http://zaken.local/api/v1/"
    assert zaken_service.api_type == "zrc"
    assert zaken_service.auth_type == "zgw"
    assert zaken_service.client_id == "client"
    assert zaken_service.secret == "super-secret"
    assert zaken_service.timeout == 10


@pytest.mark.django_db
def test_execute_configuration_step_update_existing(step_config_model):
    ServiceFactory.create(
        slug="zaken-test",
        label="Objecttypen",
        api_root="http://some.existing.service.local/api/v1/",
    )

    step = ServiceConfigurationStep()

    assert not step.is_configured(step_config_model)

    step.execute(step_config_model)

    assert Service.objects.count() == 2

    objects_service, zaken_service = Service.objects.all()

    assert objects_service.slug == "objecten-test"
    assert objects_service.label == "Objecten API test"
    assert objects_service.api_root == "http://objecten.local/api/v1/"

    assert zaken_service.slug == "zaken-test"
    assert zaken_service.label == "Zaken API test"
    assert zaken_service.api_root == "http://zaken.local/api/v1/"
