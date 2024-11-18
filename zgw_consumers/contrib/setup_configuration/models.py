from django_setup_configuration.models import ConfigurationModel, DjangoModelRef
from pydantic import Field

from zgw_consumers.models import Service


class SingleServiceConfigurationModel(ConfigurationModel):
    # TODO these should probably be defined in simple_certmanager and referred to?
    # client_certificate: FilePath = DjangoModelRef(Service, "client_certificate")
    # server_certificate: FilePath = DjangoModelRef(Service, "server_certificate")
    # Identifier is mapped to slug, because slug isn't a very descriptive name for devops
    identifier: str = DjangoModelRef(Service, "slug")

    class Meta:
        django_model_refs = {
            Service: [
                "label",
                "api_type",
                "api_root",
                "api_connection_check_path",
                "auth_type",
                "client_id",
                "secret",
                "header_key",
                "header_value",
                "nlx",
                "user_id",
                "user_representation",
                "timeout",
            ]
        }


class ServicesConfigurationModel(ConfigurationModel):
    services: list[SingleServiceConfigurationModel] = Field(default_factory=list)
