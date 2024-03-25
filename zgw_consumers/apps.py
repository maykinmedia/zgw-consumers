import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ZgwConsumersConfig(AppConfig):
    name = "zgw_consumers"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        from .cache import install_schema_fetcher_cache
        from .models import lookups  # noqa

        install_schema_fetcher_cache()
        register_serializer_field()


def register_serializer_field() -> None:
    try:
        from rest_framework import serializers
    except ImportError:
        logger.debug(
            "Could not import DRF, skipping serializer field registration. HINT: "
            "to have DRF support, install with the extra: pip install "
            "zgw-consumers[drf]"
        )
        return

    from .drf import fields as drf_fields
    from .models import fields as model_fields

    mapping = serializers.ModelSerializer.serializer_field_mapping
    mapping[model_fields.ServiceUrlField] = drf_fields.ServiceUrlApiField
