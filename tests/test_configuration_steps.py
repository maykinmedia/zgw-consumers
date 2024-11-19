import pytest
from django_setup_configuration.test_utils import execute_single_step

from zgw_consumers.constants import APITypes, AuthTypes
from zgw_consumers.contrib.setup_configuration.steps import ServiceConfigurationStep
from zgw_consumers.models import Service
from zgw_consumers.test.factories import ServiceFactory

CONFIG_FILE_PATH = "tests/files/setup_config_services.yaml"
CONFIG_FILE_PATH_REQUIRED_FIELDS = (
    "tests/files/setup_config_services_required_fields.yaml"
)
CONFIG_FILE_PATH_ALL_FIELDS = "tests/files/setup_config_services_all_fields.yaml"


@pytest.mark.django_db
def test_execute_configuration_step_success():
    execute_single_step(ServiceConfigurationStep, yaml_source=CONFIG_FILE_PATH)

    assert Service.objects.count() == 2

    objects_service, zaken_service = Service.objects.all()

    assert objects_service.slug == "objecten-test"
    assert objects_service.label == "Objecten API test"
    assert objects_service.api_root == "http://objecten.local/api/v1/"
    assert objects_service.api_type == APITypes.orc
    assert objects_service.auth_type == AuthTypes.api_key
    assert objects_service.header_key == "Authorization"
    assert objects_service.header_value == "Token foo"
    assert objects_service.timeout == 10

    assert zaken_service.slug == "zaken-test"
    assert zaken_service.label == "Zaken API test"
    assert zaken_service.api_root == "http://zaken.local/api/v1/"
    assert zaken_service.api_type == APITypes.zrc
    assert zaken_service.auth_type == AuthTypes.zgw
    assert zaken_service.client_id == "client"
    assert zaken_service.secret == "super-secret"
    assert zaken_service.timeout == 10


@pytest.mark.django_db
def test_execute_configuration_step_update_existing():
    ServiceFactory.create(
        slug="zaken-test",
        label="Objecttypen",
        api_root="http://some.existing.service.local/api/v1/",
    )

    execute_single_step(ServiceConfigurationStep, yaml_source=CONFIG_FILE_PATH)

    assert Service.objects.count() == 2

    objects_service, zaken_service = Service.objects.all()

    assert objects_service.slug == "objecten-test"
    assert objects_service.label == "Objecten API test"
    assert objects_service.api_root == "http://objecten.local/api/v1/"

    assert zaken_service.slug == "zaken-test"
    assert zaken_service.label == "Zaken API test"
    assert zaken_service.api_root == "http://zaken.local/api/v1/"


@pytest.mark.django_db
def test_execute_configuration_step_with_required_fields():
    execute_single_step(
        ServiceConfigurationStep, yaml_source=CONFIG_FILE_PATH_REQUIRED_FIELDS
    )

    assert Service.objects.count() == 1

    objects_service = Service.objects.get()

    assert objects_service.slug == "objecten-test"
    assert objects_service.label == "Objecten API test"
    assert objects_service.api_root == "http://objecten.local/api/v1/"
    assert objects_service.api_type == APITypes.orc
    assert objects_service.auth_type == AuthTypes.zgw
    assert objects_service.timeout == 10

    # Not required fields
    assert objects_service.api_connection_check_path == ""
    assert objects_service.header_key == ""
    assert objects_service.header_value == ""
    assert objects_service.client_id == ""
    assert objects_service.secret == ""
    assert objects_service.nlx == ""
    assert objects_service.user_id == ""
    assert objects_service.user_representation == ""


@pytest.mark.django_db
def test_execute_configuration_step_with_all_fields():
    execute_single_step(
        ServiceConfigurationStep, yaml_source=CONFIG_FILE_PATH_ALL_FIELDS
    )

    assert Service.objects.count() == 1

    objects_service = Service.objects.get()

    assert objects_service.slug == "objecten-test"
    assert objects_service.label == "Objecten API test"
    assert objects_service.api_root == "http://objecten.local/api/v1/"
    assert objects_service.api_type == APITypes.orc
    assert objects_service.auth_type == AuthTypes.api_key
    assert objects_service.api_connection_check_path == "objects"
    assert objects_service.header_key == "Authorization"
    assert objects_service.header_value == "Token foo"
    assert objects_service.client_id == "client"
    assert objects_service.secret == "super-secret"
    assert objects_service.nlx == "http://some-outway-adress.local:8080/"
    assert objects_service.user_id == "open-formulieren"
    assert objects_service.user_representation == "Open Formulieren"
    assert objects_service.timeout == 5


@pytest.mark.django_db
def test_execute_configuration_step_idempotent():
    def make_assertions():
        assert Service.objects.count() == 1

        objects_service = Service.objects.get()

        assert objects_service.slug == "objecten-test"
        assert objects_service.label == "Objecten API test"
        assert objects_service.api_root == "http://objecten.local/api/v1/"
        assert objects_service.api_type == APITypes.orc
        assert objects_service.auth_type == AuthTypes.api_key
        assert objects_service.api_connection_check_path == "objects"
        assert objects_service.header_key == "Authorization"
        assert objects_service.header_value == "Token foo"
        assert objects_service.client_id == "client"
        assert objects_service.secret == "super-secret"
        assert objects_service.nlx == "http://some-outway-adress.local:8080/"
        assert objects_service.user_id == "open-formulieren"
        assert objects_service.user_representation == "Open Formulieren"
        assert objects_service.timeout == 5

    execute_single_step(
        ServiceConfigurationStep, yaml_source=CONFIG_FILE_PATH_ALL_FIELDS
    )

    make_assertions()

    execute_single_step(
        ServiceConfigurationStep, yaml_source=CONFIG_FILE_PATH_ALL_FIELDS
    )

    make_assertions()
