from django_setup_configuration.configuration import BaseConfigurationStep

from zgw_consumers.models import Service

from .models import ServicesConfigurationModel


class ServiceConfigurationStep(BaseConfigurationStep[ServicesConfigurationModel]):
    """
    Configure one or more ``Service`` instances with their connection parameters and
    authentication credentials, which will allow this application to integrate
    with third-party systems in a consistent manner.
    """

    verbose_name = "Configuration to connect with external services"
    config_model = ServicesConfigurationModel
    namespace = "zgw_consumers"
    enable_setting = "zgw_consumers_config_enable"

    def execute(self, model: ServicesConfigurationModel):
        for config in model.services:
            Service.objects.update_or_create(
                slug=config.identifier,
                defaults={
                    "label": config.label,  # type: ignore setup_configuration pydantic meta programming
                    "api_type": config.api_type,  # type: ignore setup_configuration pydantic meta programming
                    "api_root": config.api_root,  # type: ignore setup_configuration pydantic meta programming
                    "api_connection_check_path": config.api_connection_check_path,  # type: ignore setup_configuration pydantic meta programming
                    "auth_type": config.auth_type,  # type: ignore setup_configuration pydantic meta programming
                    "client_id": config.client_id,  # type: ignore setup_configuration pydantic meta programming
                    "secret": config.secret,  # type: ignore setup_configuration pydantic meta programming
                    "header_key": config.header_key,  # type: ignore setup_configuration pydantic meta programming
                    "header_value": config.header_value,  # type: ignore setup_configuration pydantic meta programming
                    "nlx": config.nlx,  # type: ignore setup_configuration pydantic meta programming
                    "user_id": config.user_id,  # type: ignore setup_configuration pydantic meta programming
                    "user_representation": config.user_representation,  # type: ignore setup_configuration pydantic meta programming
                    "timeout": config.timeout,  # type: ignore setup_configuration pydantic meta programming
                    "jwt_valid_for": config.jwt_valid_for,  # type: ignore setup_configuration pydantic meta programming
                    "oauth2_token_url": config.oauth2_token_url,  # type: ignore setup_configuration pydantic meta programming
                    "oauth2_scope": config.oauth2_scope,  # type: ignore setup_configuration pydantic meta programming
                },
            )
