from urllib.parse import urljoin

from django.db import migrations

from ..constants import AuthTypes


def update_fields(apps, schema_editor):
    Service = apps.get_model("zgw_consumers", "Service")

    for service in Service.objects.filter(auth_type=AuthTypes.no_auth).exclude(
        client_id="", secret=""
    ):
        service.auth_type = AuthTypes.jwt
        service.save()

    for service in Service.objects.filter(oas=""):
        service.oas = urljoin(service.api_root, "schema/openapi.yaml")
        service.save()


class Migration(migrations.Migration):
    dependencies = [
        ("zgw_consumers", "0005_auto_20200326_1040"),
    ]

    operations = [migrations.RunPython(update_fields, migrations.RunPython.noop)]
