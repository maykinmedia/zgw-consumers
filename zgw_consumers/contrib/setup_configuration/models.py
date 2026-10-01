from collections.abc import Collection, Mapping
from typing import ClassVar, Self

from django.db.models import Model

from django_setup_configuration import ConfigurationModel, DjangoModelRef
from pydantic import model_validator

from zgw_consumers.constants import AuthTypes
from zgw_consumers.models import Service


class SingleServiceConfigurationModel(ConfigurationModel):
    # TODO these should probably be defined in simple_certmanager and referred to?
    # client_certificate: FilePath = DjangoModelRef(Service, "client_certificate")
    # server_certificate: FilePath = DjangoModelRef(Service, "server_certificate")
    # Identifier is mapped to slug, because slug isn't a very descriptive name for
    # devops
    identifier: str = DjangoModelRef(Service, "slug", examples=["service-identifier"])

    class Meta:
        django_model_refs: ClassVar[dict[type[Model], Collection[str]]] = {
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
                "jwt_valid_for",
                "oauth2_token_url",
                "oauth2_scope",
            ]
        }
        extra_kwargs: ClassVar[Mapping[str, Mapping[str, object]]] = {
            "label": {
                "examples": ["Short and human-friendly description of this service"]
            },
            "api_root": {"examples": ["https://example.com/api/v1/"]},
            "api_connection_check_path": {"examples": ["/some/relative/path"]},
            "client_id": {"examples": ["modify-this"]},
            "secret": {"examples": ["modify-this"]},
            "header_key": {"examples": ["Authorization"]},
            "header_value": {"examples": ["Token <modify-this>"]},
            "nlx": {"examples": ["http://some-outway-adress.local:8080/"]},
            "user_id": {"examples": ["client-id"]},
            "user_representation": {"examples": ["Name of the user"]},
        }

    @model_validator(mode="after")
    def check_zgw_secret(self) -> Self:
        # an empty secret can't be used as HMAC key to sign the JWT
        if self.auth_type == AuthTypes.zgw and not self.secret:  # type: ignore setup_configuration pydantic meta programming
            raise ValueError("'secret' is required when 'auth_type' is 'zgw'")
        return self


class ServicesConfigurationModel(ConfigurationModel):
    services: list[SingleServiceConfigurationModel]
