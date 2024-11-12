from django_setup_configuration.configuration import BaseConfigurationStep
from django_setup_configuration.exceptions import SelfTestFailed

from zgw_consumers.models import Service

from .models import ServicesConfigurationModel


class ServiceConfigurationStep(BaseConfigurationStep[ServicesConfigurationModel]):
    """
    Configure Services to connect with external APIs
    """

    verbose_name = "Configuration to connect with external services"
    config_model = ServicesConfigurationModel
    namespace = "ZGW_CONSUMERS"
    enable_setting = "ZGW_CONSUMERS_CONFIG_ENABLE"

    def is_configured(self, model: ServicesConfigurationModel) -> bool:
        slugs = [config.slug for config in model.services]
        return Service.objects.filter(slug__in=slugs).count() == len(slugs)

    def execute(self, model: ServicesConfigurationModel):
        ignore_fields = ["slug", "connection_check_expected_status"]
        for config in model.services:
            Service.objects.update_or_create(
                slug=config.slug,
                defaults={
                    k: v
                    for k, v in config.model_dump().items()
                    if k not in ignore_fields
                },
            )

    def validate_result(self, model: ServicesConfigurationModel) -> None:
        slugs = [config.slug for config in model.services]
        failed_checks = []
        ordered_models = sorted(model.services, key=lambda x: x.slug)
        for service, model in zip(
            Service.objects.filter(slug__in=slugs).order_by("slug"), ordered_models
        ):
            if service.connection_check != model.connection_check_expected_status:
                failed_checks.append(service.slug)

        if failed_checks:
            raise SelfTestFailed(
                f"non-success response from the following service(s): {failed_checks}"
            )
