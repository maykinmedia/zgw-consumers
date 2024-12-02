from django_setup_configuration.configuration import BaseConfigurationStep

from zgw_consumers.models import Service

from .models import ServicesConfigurationModel


class ServiceConfigurationStep(BaseConfigurationStep[ServicesConfigurationModel]):
    """
    Configure Services to connect with external APIs
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
                    "label": config.label,
                    "api_type": config.api_type,
                    "api_root": config.api_root,
                    "api_connection_check_path": config.api_connection_check_path,
                    "auth_type": config.auth_type,
                    "client_id": config.client_id,
                    "secret": config.secret,
                    "header_key": config.header_key,
                    "header_value": config.header_value,
                    "nlx": config.nlx,
                    "user_id": config.user_id,
                    "user_representation": config.user_representation,
                    "timeout": config.timeout,
                },
            )
