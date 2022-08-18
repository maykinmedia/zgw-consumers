from django.apps import AppConfig

from rest_framework import serializers


class ZgwConsumersConfig(AppConfig):
    name = "zgw_consumers"

    def ready(self):
        from .cache import install_schema_fetcher_cache
        from .models import lookups

        install_schema_fetcher_cache()
        register_serializer_field()


def register_serializer_field() -> None:
    from .drf import fields as drf_fields
    from .models import fields as model_fields

    mapping = serializers.ModelSerializer.serializer_field_mapping
    mapping[model_fields.ServiceUrlField] = drf_fields.ServiceUrlApiField
